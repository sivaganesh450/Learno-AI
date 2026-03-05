from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # MongoDB
    MONGO_URI: str
    DATABASE_NAME: str = "lerno_db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    S3_UPLOADS_BUCKET: str = "lerno-uploads-demo"
    BEDROCK_MODEL_ID: str = "us.meta.llama3-3-70b-instruct-v1:0"

    # Web Search
    TAVILY_API_KEY: Optional[str] = None

    # Code Assistant settings
    CODE_ASSISTANT_MAX_ATTEMPTS: int = 3

    # Deep Search & Report Generator settings
    DEEP_SEARCH_MAX_SECTIONS: int = 5      # max body sections (excl. intro/conclusion)
    DEEP_SEARCH_SEARCH_DEPTH: str = "advanced"  # basic | advanced

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
