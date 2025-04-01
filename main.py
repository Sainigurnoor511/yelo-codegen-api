from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from app.middlewares.auth_middleware import AuthMiddleware
from app.middlewares.logger_middleware import LoggingMiddleware
from app.config.settings import settings
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.utils.logger import setup_logger
from app.routes import code_gen_routes
from contextlib import asynccontextmanager
from fastapi import status
from datetime import datetime

logger = setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Starting up the application...")
    
    yield
    
    # Shutdown logic
    logger.info("Shutting down the application...")


app = FastAPI(title=settings.PROJECT_NAME,version=settings.VERSION,lifespan=lifespan)
origins = ["*"]

app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(code_gen_routes.router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"status": "error", "message": exc.errors()}
    )

@app.get("/")
async def root():
    """
    Root endpoint to check if API is running.
    """
    logger.info("Root endpoint hit!")

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response = {
        "status": "success",
        "code": status.HTTP_200_OK,
        "message": "Yelo Code Gen API is running!",
        "version": settings.VERSION,
        "time": current_time,
    }

    return response

if __name__ == "__main__":
    logger.info("Starting FastAPI application...")
    uvicorn.run(app, host="0.0.0.0", port=5000)
