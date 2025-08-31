"""
Module to set up SQLAlchemy
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL")


engine = create_engine(DATABASE_URL) if DATABASE_URL else None
SessionLocal = (
    sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None
)


def get_db():
    """
    create local session for postgres database
    """
    if not SessionLocal:
        raise RuntimeError(
            "Database engine is not initialized. Check if DATABASE_URL is set."
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
