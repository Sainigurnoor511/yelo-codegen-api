# from fastapi import FastAPI
# import uvicorn
# from fastapi.middleware.cors import CORSMiddleware
# from app.middlewares.auth_middleware import AuthMiddleware
# from app.middlewares.logger_middleware import LoggingMiddleware
# from app.config.settings import settings
# import os
# from fastapi.responses import JSONResponse
# from fastapi.exceptions import RequestValidationError
# from app.utils.logger import setup_logger
# from app.routers import scraper
# from contextlib import asynccontextmanager

# logger = setup_logger()

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup logic
#     logger.info("Starting up the application...")
    
#     # Create necessary directories
#     # os.makedirs("app/scrapers/Website_Code", exist_ok=True)
#     # os.makedirs("logs", exist_ok=True)
    
#     yield
    
#     # Shutdown logic
#     logger.info("Shutting down the application...")


# app = FastAPI(title=settings.PROJECT_NAME,version=settings.VERSION,lifespan=lifespan)
# origins = ["*"]

# app.add_middleware(AuthMiddleware)
# app.add_middleware(LoggingMiddleware)

# nw = os.getenv("ICP_NUM_WORKERS")
# NUM_WORKERS = (2 if nw is None else int(nw))

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(scraper.router)

# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request, exc):
#     return JSONResponse(
#         status_code=422,
#         content={"status": "error", "message": exc.errors()}
#     )

# @app.get("/", tags=["Health"])
# async def root():
#     return {"status": "healthy", "message": "Knowledge Base Scraper API is running"}

# if __name__ == "__main__":
#     logger.info("Starting FastAPI application...")
#     uvicorn.run(app, host="0.0.0.0", port=8000, workers=NUM_WORKERS)


from fastapi import FastAPI, Request
import uvicorn
from app.utils.logger import setup_logger, log_request_data
from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from app.middlewares.auth_middleware import AuthMiddleware
from app.middlewares.logger_middleware import LoggingMiddleware
from app.config.settings import settings
import os
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager


app = FastAPI()

logger = setup_logger()

@app.get("/")
async def root():
    """
    Root endpoint to check if API is running.
    """
    logger.info("Root endpoint hit!")
    return {"message": "FastAPI is running!"}

@app.post("/test-log")
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=9000, reload=True)
