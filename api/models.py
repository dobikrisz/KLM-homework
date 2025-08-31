"""
Module to create type classes for API
"""

from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel

Base = declarative_base()


# pylint: disable=too-few-public-methods
class Note(Base):
    """
    Note class for database representation
    """

    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    creator = Column(String)
    # pylint: disable=not-callable
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    # pylint: disable=not-callable
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())


class NoteType(BaseModel):
    """
    Note class for typing
    """

    title: str
    content: str
    creator: Optional[str] = None
