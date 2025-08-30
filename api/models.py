"""
Module to create type classes for API
"""

from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from pydantic import BaseModel


from database import Base


class Note(Base):
    """
    Note class for database representation
    """

    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    creator = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())


class NoteType(BaseModel):
    """
    Note class for typing
    """

    title: str
    content: str
    creator: Optional[str] = None
