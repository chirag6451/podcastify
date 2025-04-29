"""
Purpose and Objective: 
This module defines Pydantic schemas for speaker-related API endpoints including
speaker creation, updating, and retrieval.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .base import BaseSchema

class SpeakerBase(BaseSchema):
    """Base schema for speakers"""
    name: str = Field(..., example="Jane Smith")
    profile_type_id: int = Field(..., example=1)
    bio: Optional[str] = Field(None, example="Jane is a technology expert with 15 years of experience")
    voice_id: Optional[str] = Field(None, example="21m00Tcm4TlvDq8ikWAM")
    social_twitter: Optional[str] = Field(None, example="@janesmith")
    social_linkedin: Optional[str] = Field(None, example="https://linkedin.com/in/janesmith")
    social_website: Optional[str] = Field(None, example="https://janesmith.com")

class SpeakerCreate(SpeakerBase):
    """Schema for creating speakers"""
    pass

class SpeakerUpdate(BaseSchema):
    """Schema for updating speakers"""
    name: Optional[str] = Field(None, example="Jane Smith")
    profile_type_id: Optional[int] = Field(None, example=1)
    profile_url: Optional[str] = Field(None, example="https://example.com/profile.jpg")
    bio: Optional[str] = Field(None, example="Jane is a technology expert with 15 years of experience")
    voice_id: Optional[str] = Field(None, example="21m00Tcm4TlvDq8ikWAM")
    social_twitter: Optional[str] = Field(None, example="@janesmith")
    social_linkedin: Optional[str] = Field(None, example="https://linkedin.com/in/janesmith")
    social_website: Optional[str] = Field(None, example="https://janesmith.com")

class SpeakerResponse(SpeakerBase):
    """Schema for speaker response"""
    id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)
    profile_url: Optional[str] = Field(None, example="https://example.com/profile.jpg")
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "name": "Jane Smith",
                "profile_type_id": 1,
                "profile_url": "https://example.com/profile.jpg",
                "bio": "Jane is a technology expert with 15 years of experience",
                "voice_id": "21m00Tcm4TlvDq8ikWAM",
                "social_twitter": "@janesmith",
                "social_linkedin": "https://linkedin.com/in/janesmith",
                "social_website": "https://janesmith.com",
                "created_at": "2025-04-24T12:00:00Z",
                "updated_at": "2025-04-24T12:00:00Z"
            }
        }
