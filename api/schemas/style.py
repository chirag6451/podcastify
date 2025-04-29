"""
Purpose and Objective: 
This module defines Pydantic schemas for style-related API endpoints including
conversation styles, video styles, profile types, and platforms.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .base import BaseSchema

# Conversation Style schemas
class ConversationStyleBase(BaseSchema):
    """Base schema for conversation styles"""
    name: str = Field(..., example="Casual Interview")
    description: Optional[str] = Field(None, example="A relaxed, informal conversation between hosts")

class ConversationStyleCreate(ConversationStyleBase):
    """Schema for creating conversation styles"""
    pass

class ConversationStyleResponse(ConversationStyleBase):
    """Schema for conversation style response"""
    id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Casual Interview",
                "description": "A relaxed, informal conversation between hosts",
                "created_at": "2025-04-24T12:00:00Z",
                "updated_at": "2025-04-24T12:00:00Z"
            }
        }

# Video Style schemas
class VideoStyleBase(BaseSchema):
    """Base schema for video styles"""
    name: str = Field(..., example="Split Screen")
    description: Optional[str] = Field(None, example="Two hosts shown side by side")

class VideoStyleCreate(VideoStyleBase):
    """Schema for creating video styles"""
    pass

class VideoStyleResponse(VideoStyleBase):
    """Schema for video style response"""
    id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Split Screen",
                "description": "Two hosts shown side by side",
                "created_at": "2025-04-24T12:00:00Z",
                "updated_at": "2025-04-24T12:00:00Z"
            }
        }

# Profile Type schemas
class ProfileTypeBase(BaseSchema):
    """Base schema for profile types"""
    name: str = Field(..., example="AI Avatar")
    description: Optional[str] = Field(None, example="Computer-generated avatar representation")

class ProfileTypeCreate(ProfileTypeBase):
    """Schema for creating profile types"""
    pass

class ProfileTypeResponse(ProfileTypeBase):
    """Schema for profile type response"""
    id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "AI Avatar",
                "description": "Computer-generated avatar representation",
                "created_at": "2025-04-24T12:00:00Z",
                "updated_at": "2025-04-24T12:00:00Z"
            }
        }

# Platform schemas
class PlatformBase(BaseSchema):
    """Base schema for platforms"""
    name: str = Field(..., example="YouTube")
    description: Optional[str] = Field(None, example="Video sharing platform")
    icon_url: Optional[str] = Field(None, example="https://example.com/youtube-icon.png")

class PlatformCreate(PlatformBase):
    """Schema for creating platforms"""
    pass

class PlatformResponse(PlatformBase):
    """Schema for platform response"""
    id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "YouTube",
                "description": "Video sharing platform",
                "icon_url": "https://example.com/youtube-icon.png",
                "created_at": "2025-04-24T12:00:00Z",
                "updated_at": "2025-04-24T12:00:00Z"
            }
        }
