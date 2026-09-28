"""
Database configuration and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import os

# Database URL from environment or default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://motor_user:motor_password@localhost:5432/motor_biomecanico"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    # NullPool for development; use QueuePool in production
    poolclass=NullPool,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",  # Debug SQL queries
    connect_args={
        "connect_timeout": 10,
        "application_name": "motor_biomecanico"
    }
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for getting database session in FastAPI endpoints.

    Usage:
        @app.get("/cases/")
        def list_cases(db: Session = Depends(get_db)):
            return db.query(Case).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_db_async():
    """Async version of get_db for async endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all tables in the database (use with caution!)."""
    Base.metadata.drop_all(bind=engine)
