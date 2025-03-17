from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from ..config.settings import settings

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate the Authorization token in the headers.
    """

    async def dispatch(self, request: Request, call_next):
        # for localhost
        if request.method == "OPTIONS":
            return await call_next(request) 
        # Extract the Authorization header
        auth_header = request.headers.get("Authorization")

        # Token expected in the header
        expected_token = settings.SECRET_TOKEN

        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"message": "Authorization header missing"},
            )

        # Check if the provided token matches the expected token
        if auth_header != expected_token:
            return JSONResponse(
                status_code=401,
                content={"message": "Invalid Authorization token"},
            )

        # Proceed to the next middleware or endpoint
        response = await call_next(request)
        return response
