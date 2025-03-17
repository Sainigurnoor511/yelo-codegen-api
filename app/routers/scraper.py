from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Depends
import subprocess
import uuid
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict
import os
import time
from datetime import datetime
from ..services.scraper_service import extract_html_code, get_absolute_path
from ..utils.logger import setup_logger
from ..databases.redis import get_redis

logger = setup_logger()
router = APIRouter(prefix="/api/v1/knowledge-base", tags=["Knowledge Base"])
spider_path = get_absolute_path("app/scrapers", "spider.py")
extracted_link_path = get_absolute_path("app/scrapers", "extracted_links.csv")
tasks: Dict[str, Dict] = {}  # task_id -> {"status": str, "start_time": datetime}

class CrawlRequest(BaseModel):
    url: HttpUrl
    webhook_url: Optional[HttpUrl] = None


async def rate_limiter(request: Request, redis=Depends(get_redis)):
    """Rate limiting: Allow only 1 request per 15 minutes per client IP using Redis."""
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"

    last_request_time = await redis.get(key)

    if last_request_time:
        time_since_last_request = time.time() - float(last_request_time)
        remaining_time = 900 - time_since_last_request  # 900 seconds = 15 minutes
        remaining_minutes, remaining_seconds = divmod(int(remaining_time), 60)
        if remaining_time > 0:
            raise HTTPException(
                status_code=429,
                detail = f"Rate limit exceeded. Try again in {remaining_minutes} min {remaining_seconds} sec."

            )

    # Store the current request timestamp in Redis with a 15-minute expiry
    await redis.setex(key, 900, str(time.time()))


def run_spider_and_extract(task_id: str, url: str, webhook_url: Optional[str] = None):
    """Run the spider and extract HTML content in the background."""
    tasks[task_id]["status"] = "running"
    try:
        result = subprocess.run(
            ["scrapy", "runspider", spider_path, "-a", f"start_url={url}", "-a", f"webhook_url={webhook_url or ''}"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            logger.info(f"Link crawling completed successfully for task: {task_id}")
            
            # Extract HTML from the links
            extract_result = extract_html_code(webhook_url)
            logger.info(f"Scraping knowledge base completed successfully for task: {task_id}.\nScraping Results:{extract_result}")

            tasks[task_id]["status"] = "completed"

        else:
            logger.error(f"Link crawling failed for task: {task_id}, Error: {result.stderr}")
            tasks[task_id]["status"] = "failed"

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        tasks[task_id]["status"] = "failed"

    finally:
        os.remove(extracted_link_path)  # Delete extracted links file after processing
        logger.info(f"File 'extracted_links' removed.")


@router.post("/crawl", dependencies=[Depends(rate_limiter)])
async def crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    """API to start crawling and extracting HTML content in the background, with Redis rate limiting."""
    url = str(request.url)
    webhook_url = str(request.webhook_url) if request.webhook_url else None

    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    task_id = str(uuid.uuid4())  # Generate a unique task ID
    start_time = datetime.utcnow()  # Capture the start time

    tasks[task_id] = {"status": "queued", "start_time": start_time}  # Mark task as queued

    try:
        # Run the spider in the background
        background_tasks.add_task(run_spider_and_extract, task_id, url, webhook_url)

        return {
            "status": "success",
            "task_id": task_id,
            "message": "Crawling process started"
        }

    except Exception as e:
        logger.error(f"Error initiating crawl: {str(e)}")
        tasks[task_id]["status"] = "failed"
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Check the status of a specific task and its runtime."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task ID not found")

    task_info = tasks[task_id]
    elapsed_time = (datetime.utcnow() - task_info["start_time"]).total_seconds()

    return {
        "task_id": task_id,
        "status": task_info["status"],
        "elapsed_time": f"{elapsed_time:.2f} seconds"
    }


@router.get("/tasks")
async def list_all_tasks():
    """List all tasks with their statuses."""
    return {task_id: {"status": task_data["status"]} for task_id, task_data in tasks.items()}
