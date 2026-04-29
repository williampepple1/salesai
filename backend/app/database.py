from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

def create_database_engine(database_url: str | None = None):
    """Create a PostgreSQL engine with conservative pooling for Lambda."""
    resolved_url = database_url or settings.get_database_url()
    return create_engine(
        resolved_url,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=2,
        max_overflow=3,
        pool_timeout=10,
        connect_args={"connect_timeout": 5},
    )


engine = create_database_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
