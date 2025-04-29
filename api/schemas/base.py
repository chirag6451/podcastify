"""
Purpose and Objective: 
This module defines base Pydantic schemas that are used across multiple API endpoints.
These schemas provide common response structures and base classes for other schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime

class BaseSchema(BaseModel):
    """
    Base schema with common configuration for all Pydantic models.
    """
    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models
        json_schema_extra = {
            "example": {}  # Will be overridden by child classes
        }

class MessageResponse(BaseModel):
    """
    Standard response schema for operations that return a simple message.
    """
    message: str = Field(..., example="Operation completed successfully")

class ErrorResponse(BaseModel):
    """
    Standard error response schema.
    """
    detail: str = Field(..., example="An error occurred")

class PaginatedResponse(BaseModel):
    """
    Base schema for paginated responses.
    """
    items: List[Any]
    total: int = Field(..., example=100)
    page: int = Field(..., example=1)
    size: int = Field(..., example=10)
    pages: int = Field(..., example=10)

class DateTimeRange(BaseModel):
    """
    Schema for date-time range filters.
    """
    start_date: Optional[datetime] = Field(None, example="2025-01-01T00:00:00Z")
    end_date: Optional[datetime] = Field(None, example="2025-12-31T23:59:59Z")
