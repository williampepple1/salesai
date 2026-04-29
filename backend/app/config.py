import json
from functools import lru_cache
from typing import Any, Optional

import boto3
from pydantic import model_validator
from pydantic_settings import BaseSettings
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: Optional[str] = None
    TEST_DATABASE_URL: Optional[str] = None
    DATABASE_SECRET_ARN: Optional[str] = None
    
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
    ENABLE_LOCAL_UPLOADS: bool = False
    
    # CORS
    CORS_ORIGINS: list[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.is_production and "*" in self.CORS_ORIGINS:
            raise ValueError("Production CORS_ORIGINS cannot include '*'.")
        return self

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "prod"

    def get_database_url(self) -> str:
        """Resolve the application database URL from env or Secrets Manager."""
        database_url = self.DATABASE_URL

        if self.DATABASE_SECRET_ARN:
            database_url = _load_database_url_from_secret(
                self.DATABASE_SECRET_ARN,
                self.AWS_REGION,
            )

        if not database_url:
            raise RuntimeError(
                "Database configuration is missing. Set DATABASE_URL for local use "
                "or DATABASE_SECRET_ARN for production."
            )

        if database_url.startswith("sqlite"):
            raise RuntimeError("SQLite is not supported for this production app.")

        if not database_url.startswith(
            ("postgresql://", "postgresql+psycopg://", "postgresql+psycopg2://")
        ):
            raise RuntimeError("DATABASE_URL must use PostgreSQL.")

        return _normalize_postgres_driver(database_url)


settings = Settings()


@lru_cache(maxsize=8)
def _load_database_url_from_secret(secret_arn: str, region_name: str) -> str:
    client = boto3.client("secretsmanager", region_name=region_name)
    response = client.get_secret_value(SecretId=secret_arn)
    payload = json.loads(response["SecretString"])

    if payload.get("url"):
        return _require_postgres_url(payload["url"])

    required_keys = {"username", "password", "host", "port", "dbname"}
    missing_keys = required_keys - set(payload)
    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise RuntimeError(f"Database secret is missing required keys: {missing}")

    url = URL.create(
        "postgresql+psycopg",
        username=payload["username"],
        password=payload["password"],
        host=payload["host"],
        port=int(payload["port"]),
        database=payload["dbname"],
    )
    return url.render_as_string(hide_password=False)


def _require_postgres_url(database_url: Any) -> str:
    if not isinstance(database_url, str) or not database_url.startswith(
        ("postgresql://", "postgresql+psycopg://", "postgresql+psycopg2://")
    ):
        raise RuntimeError("Database secret must contain a PostgreSQL URL.")
    return _normalize_postgres_driver(database_url)


def _normalize_postgres_driver(database_url: str) -> str:
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url
