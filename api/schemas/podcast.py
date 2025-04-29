"""
Purpose and Objective: 
This module defines Pydantic schemas for podcast-related API endpoints including
podcast creation, episode management, and podcast group organization.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .base import BaseSchema

# Podcast Group schemas
class PodcastGroupBase(BaseSchema):
    """Base schema for podcast groups"""
    name: str = Field(..., example="Business Podcasts")
    description: Optional[str] = Field(None, example="Collection of business-focused podcasts")

class PodcastGroupCreate(PodcastGroupBase):
    """Schema for creating podcast groups"""
    pass

class PodcastGroupResponse(PodcastGroupBase):
    """Schema for podcast group response"""
    id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-04-24T12:00:00Z")

# Podcast schemas
class PodcastBase(BaseSchema):
    """Base schema for podcasts"""
    title: str = Field(..., example="The Business Innovation Podcast")
    description: str = Field(..., example="Exploring innovative business strategies and technologies")
    language: Optional[str] = Field("en", example="en")
    audience_type: Optional[str] = Field(None, example="Business professionals")
    categories: Optional[List[str]] = Field(None, example=["Business", "Technology", "Innovation"])
    keywords: Optional[List[str]] = Field(None, example=["innovation", "business", "technology"])
    website: Optional[str] = Field(None, example="https://example.com/podcast")
    email: Optional[str] = Field(None, example="podcast@example.com")
    contact_number: Optional[str] = Field(None, example="+1234567890")
    group_id: Optional[int] = Field(None, example=1)
    video_style_id: Optional[int] = Field(None, example=1)
    conversation_style_id: Optional[int] = Field(None, example=1)
    profile_type_id: Optional[int] = Field(None, example=1)
    speaker1_id: Optional[int] = Field(None, example=1)
    speaker2_id: Optional[int] = Field(None, example=2)

class PodcastCreate(PodcastBase):
    """Schema for creating podcasts"""
    pass

class PodcastUpdate(BaseSchema):
    """Schema for updating podcasts"""
    title: Optional[str] = Field(None, example="The Business Innovation Podcast")
    description: Optional[str] = Field(None, example="Exploring innovative business strategies and technologies")
    cover_image: Optional[str] = Field(None, example="https://example.com/cover.jpg")
    language: Optional[str] = Field(None, example="en")
    audience_type: Optional[str] = Field(None, example="Business professionals")
    categories: Optional[List[str]] = Field(None, example=["Business", "Technology", "Innovation"])
    keywords: Optional[List[str]] = Field(None, example=["innovation", "business", "technology"])
    website: Optional[str] = Field(None, example="https://example.com/podcast")
    email: Optional[str] = Field(None, example="podcast@example.com")
    contact_number: Optional[str] = Field(None, example="+1234567890")
    group_id: Optional[int] = Field(None, example=1)
    video_style_id: Optional[int] = Field(None, example=1)
    conversation_style_id: Optional[int] = Field(None, example=1)
    profile_type_id: Optional[int] = Field(None, example=1)
    speaker1_id: Optional[int] = Field(None, example=1)
    speaker2_id: Optional[int] = Field(None, example=2)

class PodcastResponse(PodcastBase):
    """Schema for podcast response"""
    id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)
    cover_image: Optional[str] = Field(None, example="https://example.com/cover.jpg")
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    
    # Optional related data
    group: Optional[PodcastGroupResponse] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "title": "The Business Innovation Podcast",
                "description": "Exploring innovative business strategies and technologies",
                "cover_image": "https://example.com/cover.jpg",
                "language": "en",
                "audience_type": "Business professionals",
                "categories": ["Business", "Technology", "Innovation"],
                "keywords": ["innovation", "business", "technology"],
                "website": "https://example.com/podcast",
                "email": "podcast@example.com",
                "contact_number": "+1234567890",
                "group_id": 1,
                "video_style_id": 1,
                "conversation_style_id": 1,
                "profile_type_id": 1,
                "speaker1_id": 1,
                "speaker2_id": 2,
                "created_at": "2025-04-24T12:00:00Z",
                "updated_at": "2025-04-24T12:00:00Z"
            }
        }

# Episode schemas
class EpisodeBase(BaseSchema):
    """Base schema for episodes"""
    podcast_id: int = Field(..., example=1)
    title: str = Field(..., example="Episode 1: Innovation in the Digital Age")
    description: str = Field(..., example="Discussing the latest innovations in digital technology")
    keywords: Optional[List[str]] = Field(None, example=["digital", "innovation", "technology"])
    language: Optional[str] = Field("en", example="en")
    video_style_id: Optional[int] = Field(None, example=1)
    conversation_style_id: Optional[int] = Field(None, example=1)
    speaker1_id: Optional[int] = Field(None, example=1)
    speaker2_id: Optional[int] = Field(None, example=2)

class EpisodeCreate(EpisodeBase):
    """Schema for creating episodes"""
    pass

class EpisodeUpdate(BaseSchema):
    """Schema for updating episodes"""
    title: Optional[str] = Field(None, example="Episode 1: Innovation in the Digital Age")
    description: Optional[str] = Field(None, example="Discussing the latest innovations in digital technology")
    keywords: Optional[List[str]] = Field(None, example=["digital", "innovation", "technology"])
    language: Optional[str] = Field(None, example="en")
    status: Optional[str] = Field(None, example="published")
    publish_date: Optional[datetime] = Field(None, example="2025-04-30T12:00:00Z")
    cover_image: Optional[str] = Field(None, example="https://example.com/episode-cover.jpg")
    video_style_id: Optional[int] = Field(None, example=1)
    conversation_style_id: Optional[int] = Field(None, example=1)
    speaker1_id: Optional[int] = Field(None, example=1)
    speaker2_id: Optional[int] = Field(None, example=2)

class EpisodeResponse(EpisodeBase):
    """Schema for episode response"""
    id: int = Field(..., example=1)
    duration: Optional[str] = Field(None, example="30:45")
    status: str = Field(..., example="published")
    publish_date: Optional[datetime] = Field(None, example="2025-04-30T12:00:00Z")
    cover_image: Optional[str] = Field(None, example="https://example.com/episode-cover.jpg")
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "podcast_id": 1,
                "title": "Episode 1: Innovation in the Digital Age",
                "description": "Discussing the latest innovations in digital technology",
                "duration": "30:45",
                "keywords": ["digital", "innovation", "technology"],
                "language": "en",
                "video_style_id": 1,
                "conversation_style_id": 1,
                "status": "published",
                "publish_date": "2025-04-30T12:00:00Z",
                "cover_image": "https://example.com/episode-cover.jpg",
                "speaker1_id": 1,
                "speaker2_id": 2,
                "created_at": "2025-04-24T12:00:00Z",
                "updated_at": "2025-04-24T12:00:00Z"
            }
        }

# Platform config schemas
class PlatformConfigBase(BaseSchema):
    """Base schema for platform configurations"""
    podcast_id: int = Field(..., example=1)
    platform_id: int = Field(..., example=1)
    enabled: bool = Field(True, example=True)
    auto_publish: bool = Field(False, example=False)
    account_id: Optional[str] = Field(None, example="account123")

class PlatformConfigCreate(PlatformConfigBase):
    """Schema for creating platform configurations"""
    pass

class PlatformConfigResponse(PlatformConfigBase):
    """Schema for platform configuration response"""
    id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
