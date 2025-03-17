# import logging
# import sys
# import os
# from pythonjsonlogger import jsonlogger
# from fastapi import Request

# def setup_logger():
#     formatter = jsonlogger.JsonFormatter(
#         reserved_attrs=["created", "levelno", "msecs", "msg", "args",
#                         "relativeCreated", "exc_info", "exc_text", "stack_info"],
#         fmt="%(asctime)s %(levelname)s %(message)s",
#         datefmt="%Y-%m-%d %H:%M:%S",
#         rename_fields={"asctime": "time", "levelname": "level"}
#     )
#     json_handler = logging.StreamHandler(sys.stdout)
#     json_handler.setFormatter(formatter)

#     logger = logging.getLogger(__name__)  # Dynamic module-based logger name
#     if logger.handlers:
#         logger.handlers.clear()

#     logger.addHandler(json_handler)
#     logger.propagate = False
#     logger.setLevel(logging.DEBUG)  # Adjust as needed (DEBUG, INFO, etc.)
#     return logger

# logger = setup_logger()

# async def log_request_data(request: Request):
#     """
#     Logs the request headers, method, URL, and body.
#     """
#     body = await request.body()
#     logger.info({
#         "method": request.method,
#         "url": str(request.url),
#         "headers": dict(request.headers),
#         "body": body.decode("utf-8") if body else None
#     })


import logging
import sys
import os
from pythonjsonlogger import jsonlogger
from fastapi import Request
import colorlog

def setup_logger():
    """
    Sets up a logger with both colored console output and structured JSON logging.
    """
    # Color Formatter for Console Output
    color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    
    # JSON Formatter for structured logs
    json_formatter = jsonlogger.JsonFormatter(
        reserved_attrs=[
            "created", "levelno", "msecs", "msg", "args",
            "relativeCreated", "exc_info", "exc_text", "stack_info"
        ],
        fmt="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        rename_fields={"asctime": "time", "levelname": "level"},
    )

    # Console Handler (Colored)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(color_formatter)

    # JSON Log Handler (for external processing)
    json_handler = logging.StreamHandler(sys.stdout)
    json_handler.setFormatter(json_formatter)

    logger = logging.getLogger("app_logger")  # Generic application logger
    if logger.handlers:
        logger.handlers.clear()  # Avoid duplicate handlers

    logger.addHandler(console_handler)  # For human-readable logs
    logger.addHandler(json_handler)  # For structured logs
    logger.setLevel(logging.DEBUG)  # Set desired log level

    return logger

logger = setup_logger()

async def log_request_data(request: Request):
    """
    Logs HTTP request details including headers, method, URL, and body.
    """
    body = await request.body()
    log_data = {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "body": body.decode("utf-8") if body else None
    }
    
    logger.info("Received HTTP Request", extra={"structured_log": log_data})
