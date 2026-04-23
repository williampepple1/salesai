from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str
    
    # AWS
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_IMAGES: str
    
    # Clerk Authentication
    CLERK_DOMAIN: str  # e.g., "your-app.clerk.accounts.dev"
    CLERK_SECRET_KEY: str
    CLERK_PUBLISHABLE_KEY: str
    CLERK_AUDIENCE: Optional[str] = None  # Optional: for custom JWT claims
    
    # OpenAI
    OPENAI_API_KEY: str
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: list[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
