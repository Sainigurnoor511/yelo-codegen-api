from dotenv import load_dotenv
import os

load_dotenv()
class Settings:
    PROJECT_NAME: str = "YELO Code Generator"
    VERSION: str = "1.0.0"    
    SECRET_TOKEN = os.getenv("SECRET_TOKEN", "default_token")
    
settings = Settings()
