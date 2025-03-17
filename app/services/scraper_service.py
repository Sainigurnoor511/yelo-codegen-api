import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import datetime
import time
from typing import Optional, Dict, Any, List
from ..utils.logger import setup_logger

logger = setup_logger()

def get_absolute_path(path: str, filename: str) -> str:
    return os.path.abspath(os.path.join(path, filename)).replace("\\", "/")

# Paths
base_directory = get_absolute_path("app/scrapers", "Website_Code")
extracted_link_path = get_absolute_path("app/scrapers", "extracted_links.csv")

def sanitize_filename(filename: str) -> str:
    """Removes or replaces invalid characters from filenames."""
    invalid_chars = r'[<>:"/\\|?*#]'
    return re.sub(invalid_chars, '_', filename)

def remove_unwanted_elements(html_content: str) -> str:
    """Removes headers, footers, and unnecessary elements from HTML content."""
    soup = BeautifulSoup(html_content, "html.parser")

    for tag in ["header", "footer"]:
        if (element := soup.find(tag)):
            element.decompose()

    for class_name in [
        "csh-article-content-updated csh-text-wrap csh-font-sans-light",
        "csh-markdown csh-markdown-line csh-article-content-separate csh-article-content-separate-bottom"
    ]:
        for element in soup.find_all(class_=class_name):
            element.decompose()

    return soup.prettify()

def extract_html_code(webhook_url: Optional[str] = None) -> Dict[str, Any]:
    """Extracts HTML code from links and saves cleaned HTML content in files."""
    if not os.path.exists(extracted_link_path):
        logger.error("Extracted links file not found!")
        return {"error": "No extracted links found."}

    links = pd.read_csv(extracted_link_path)["Links"].tolist()
    os.makedirs(base_directory, exist_ok=True)  # Ensure "Website Code" folder exists

    success_count = 0
    failed_links: List[Dict[str, str]] = []

    for link in links:
        try:
            raw_filename = f"{link.split('//')[-1].replace('/', '_')}_HTML_CODE.html"
            filename = get_absolute_path(base_directory, sanitize_filename(raw_filename))
            response = requests.get(link, timeout=10)

            if response.status_code == 200:
                cleaned_html = remove_unwanted_elements(response.text)
                
                # with open(filename, "w", encoding="utf-8") as file:
                #     file.write(cleaned_html)
                # logger.info(f"Content saved to {filename}")
                
                # Send successful webhook notification with HTML content
                send_webhook(
                    link=link, 
                    status="success", 
                    webhook_url=webhook_url,
                    html_content=cleaned_html,
                    # filename=filename
                )
                
                success_count += 1
                
            else:
                error_msg = f"Status code {response.status_code}"
                send_webhook(
                    link=link, 
                    status="failed", 
                    webhook_url=webhook_url,
                    error=error_msg
                )
                raise requests.RequestException(error_msg)

        except (requests.RequestException, OSError) as e:
            logger.error(f"Error processing {link}: {e}")
            send_webhook(
                link=link, 
                status="failed", 
                webhook_url=webhook_url,
                error=str(e)
            )
            failed_links.append({"link": link, "error": str(e)})
        
        # Sleep for 2 seconds to limit webhook rate
        time.sleep(2)

    return {
        "status": "completed" if not failed_links else "partially completed",
        "total_links": len(links),
        "successfully_extracted": success_count,
        "failed_extractions": failed_links
    }

def send_webhook(link: str, status: str, webhook_url: Optional[str], html_content: Optional[str] = None, filename: Optional[str] = None, error: Optional[str] = None) -> None:
    """Send webhook notification to another server for each processed link."""
    if not webhook_url:
        logger.info(f"No webhook URL provided, skipping webhook for {link}")
        return
    
    payload = {
        "link": link,
        "status": status,
        "timestamp": str(datetime.datetime.now()),
    }

    if filename:
        payload["filename"] = filename

    if error:
        payload["error"] = str(error)

    try:
        # If there is HTML content, send it as `article` in the request
        if html_content:
            form_data = {
                "article": html_content
            }
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(webhook_url, data=form_data, headers=headers, timeout=10)
        else:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)

        # Logging webhook response
        if response.status_code == 200:
            logger.info(f"Webhook sent successfully for {link}")
        else:
            logger.warning(f"Webhook failed with status code {response.status_code} for {link}")

    except Exception as e:
        logger.error(f"Error sending webhook for {link}: {e}")
