"""
Purpose and Objective: 
This module defines Pydantic schemas for podcast job-related API endpoints including
job creation, status updates, and result retrieval for podcast generation processes.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .base import BaseSchema

class PodcastJobBase(BaseSchema):
    """Base schema for podcast jobs"""
    podcast_id: Optional[int] = Field(None, example=1)
    episode_id: Optional[int] = Field(None, example=1)
    title: str = Field(..., example="AI in Business")
    description: str = Field(..., example="Discussion about AI applications in modern business")
    duration: Optional[str] = Field(None, example="30:00")
    status: str = Field("pending", example="pending")
    speaker1_id: Optional[int] = Field(None, example=1)
    speaker2_id: Optional[int] = Field(None, example=2)
    conversation_style_id: Optional[int] = Field(None, example=1)
    video_style_id: Optional[int] = Field(None, example=1)

class PodcastJobCreate(PodcastJobBase):
    """Schema for creating podcast jobs"""
    pass

class PodcastJobUpdate(BaseSchema):
    """Schema for updating podcast jobs"""
    status: Optional[str] = Field(None, example="processing")
    progress: Optional[int] = Field(None, example=50)
    error_message: Optional[str] = Field(None, example="Error processing audio")
    result_data: Optional[Dict[str, Any]] = Field(None)

class PodcastJobResponse(PodcastJobBase):
    """Schema for podcast job response"""
    id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)
    progress: Optional[int] = Field(None, example=75)
    error_message: Optional[str] = Field(None, example=None)
    result_data: Optional[Dict[str, Any]] = Field(None)
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "podcast_id": 1,
                "episode_id": 1,
                "title": "AI in Business",
                "description": "Discussion about AI applications in modern business",
                "duration": "30:00",
                "status": "completed",
                "progress": 100,
                "speaker1_id": 1,
                "speaker2_id": 2,
                "conversation_style_id": 1,
                "video_style_id": 1,
                "error_message": None,
                "result_data": {
                    "audio_url": "https://storage.example.com/podcasts/audio/123.mp3",
                    "video_url": "https://storage.example.com/podcasts/video/123.mp4",
                    "transcript": "https://storage.example.com/podcasts/transcript/123.txt"
                },
                "created_at": "2025-04-24T12:00:00Z",
                "updated_at": "2025-04-24T12:00:00Z"
            }
        }
