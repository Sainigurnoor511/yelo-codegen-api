from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import setup_logger, log_request_data

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        await log_request_data(request)
        
        response = await call_next(request)
        
        logger.info({
            "status_code": response.status_code,
            "headers": dict(response.headers)
        })
        return response
