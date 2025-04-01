from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Form, Depends
from typing import Dict
from ..utils.logger import logger, log_request_data
from ..services.code_gen_services import update_website_styles
# from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/yelo-code-gen", tags=["Yelo Code Generator"])

class CodeGenForm:
    """
    Form class to handle HTML, CSS, and user prompt as form data.
    """
    def __init__(self, html: str = Form(...), css: str = Form(...), user_prompt: str = Form(...)):
        self.html = html
        self.css = css
        self.user_prompt = user_prompt


@router.post("/test-log")
async def test_log(request: Request):
    """
    Test endpoint to log request details.
    """
    await log_request_data(request)
    logger.debug("Debugging info inside /test-log endpoint.")
    logger.info("Information log from /test-log endpoint.")
    logger.warning("Warning message from /test-log endpoint.")
    logger.error("Error message from /test-log endpoint.")
    return {"message": "Logs have been recorded! Check your console."}


@router.post("/generate-code", response_model=Dict[str, str])
async def generate_code(form: CodeGenForm = Depends()):
    """
    Generate code for the given HTML, CSS, and user prompt received as form data.
    """
    logger.info("Generating code...")

    # Access form data through the class
    html = form.html
    css = form.css
    user_prompt = form.user_prompt

    # Log the received form data
    logger.info(f"HTML: {html}")
    logger.info(f"CSS: {css}")
    logger.info(f"Prompt: {user_prompt}")

    # Use the code generation service
    updated_html, updated_css = update_website_styles(html, css, user_prompt)

    logger.info("Code generated successfully!")

    return {
        "updated_html": updated_html,
        "updated_css": updated_css
    }
