import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi import HTTPException, Request, status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/salesai_test"))
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("S3_BUCKET_IMAGES", "test-images")
os.environ.setdefault("CLERK_DOMAIN", "test.clerk.accounts.dev")
os.environ.setdefault("CLERK_SECRET_KEY", "sk_test")
os.environ.setdefault("CLERK_PUBLISHABLE_KEY", "pk_test")
os.environ.setdefault("OPENAI_API_KEY", "sk-test")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-token")

from app.main import app
from app.database import Base, get_db
from app.models import User
from app.clerk_auth import get_current_active_user

SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"]
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    pytest.exit("SQLite is not supported. Set TEST_DATABASE_URL to a PostgreSQL database.")

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def pytest_sessionstart(session):
    """Run production migrations against the PostgreSQL test database."""
    backend_dir = Path(__file__).resolve().parents[1]
    alembic_cfg = Config(str(backend_dir / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(backend_dir / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="function")
def db():
    """Create a fresh PostgreSQL data set for each test."""
    table_names = ", ".join(f'"{table.name}"' for table in reversed(Base.metadata.sorted_tables))
    if table_names:
        with engine.begin() as connection:
            connection.execute(text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"))

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        if table_names:
            with engine.begin() as connection:
                connection.execute(text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"))


@pytest.fixture(scope="function")
def client(db, test_user):
    """Create a test client"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    async def override_current_user(request: Request):
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_current_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Create a test user"""
    user = User(
        clerk_user_id="user_test",
        email="test@example.com",
        username="testuser",
        business_name="Test Business",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Return a bearer header accepted by the Clerk override."""
    return {"Authorization": "Bearer test-token"}
