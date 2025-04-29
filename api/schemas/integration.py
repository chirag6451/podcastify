"""
Purpose and Objective: 
This module defines Pydantic schemas for integration-related API endpoints including
YouTube channels, playlists, and video paths for external platform publishing.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .base import BaseSchema

# YouTube Channel schemas
class YouTubeChannelBase(BaseSchema):
    """Base schema for YouTube channels"""
    channel_id: str = Field(..., example="UC1234567890abcdef")
    name: str = Field(..., example="Business Insights")

class YouTubeChannelCreate(YouTubeChannelBase):
    """Schema for creating YouTube channel records"""
    pass

class YouTubeChannelResponse(YouTubeChannelBase):
    """Schema for YouTube channel response"""
    id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "channel_id": "UC1234567890abcdef",
                "name": "Business Insights",
                "created_at": "2025-04-24T12:00:00Z",
                "updated_at": "2025-04-24T12:00:00Z"
            }
        }

# YouTube Playlist schemas
class YouTubePlaylistBase(BaseSchema):
    """Base schema for YouTube playlists"""
    channel_id: int = Field(..., example=1)
    playlist_id: str = Field(..., example="PL1234567890abcdef")
    playlist_title: str = Field(..., example="AI in Business")
    playlist_description: Optional[str] = Field(None, example="Discussions about AI applications in business")
    is_default: bool = Field(False, example=True)

class YouTubePlaylistCreate(YouTubePlaylistBase):
    """Schema for creating YouTube playlist records"""
    pass

class YouTubePlaylistResponse(YouTubePlaylistBase):
    """Schema for YouTube playlist response"""
    id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "channel_id": 1,
                "playlist_id": "PL1234567890abcdef",
                "playlist_title": "AI in Business",
                "playlist_description": "Discussions about AI applications in business",
                "is_default": True,
                "created_at": "2025-04-24T12:00:00Z",
                "updated_at": "2025-04-24T12:00:00Z"
            }
        }

# Video Path schemas
class VideoPathBase(BaseSchema):
    """Base schema for video paths"""
    job_id: Optional[int] = Field(None, example=1)
    audio_path: Optional[str] = Field(None, example="/storage/podcasts/audio/123.mp3")
    welcome_audio_path: Optional[str] = Field(None, example="/storage/podcasts/welcome/123.mp3")
    intro_video_path: Optional[str] = Field(None, example="/storage/podcasts/intro/123.mp4")
    bumper_video_path: Optional[str] = Field(None, example="/storage/podcasts/bumper/123.mp4")
    short_video_path: Optional[str] = Field(None, example="/storage/podcasts/short/123.mp4")
    main_video_path: Optional[str] = Field(None, example="/storage/podcasts/main/123.mp4")
    outro_video_path: Optional[str] = Field(None, example="/storage/podcasts/outro/123.mp4")
    welcome_video_avatar_path: Optional[str] = Field(None, example="/storage/podcasts/welcome_avatar/123.mp4")

class VideoPathCreate(VideoPathBase):
    """Schema for creating video path records"""
    pass

class VideoPathUpdate(BaseSchema):
    """Schema for updating video path records"""
    audio_path: Optional[str] = Field(None, example="/storage/podcasts/audio/123.mp3")
    welcome_audio_path: Optional[str] = Field(None, example="/storage/podcasts/welcome/123.mp3")
    intro_video_path: Optional[str] = Field(None, example="/storage/podcasts/intro/123.mp4")
    bumper_video_path: Optional[str] = Field(None, example="/storage/podcasts/bumper/123.mp4")
    short_video_path: Optional[str] = Field(None, example="/storage/podcasts/short/123.mp4")
    main_video_path: Optional[str] = Field(None, example="/storage/podcasts/main/123.mp4")
    outro_video_path: Optional[str] = Field(None, example="/storage/podcasts/outro/123.mp4")
    welcome_video_avatar_path: Optional[str] = Field(None, example="/storage/podcasts/welcome_avatar/123.mp4")

class VideoPathResponse(VideoPathBase):
    """Schema for video path response"""
    id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "job_id": 1,
                "audio_path": "/storage/podcasts/audio/123.mp3",
                "welcome_audio_path": "/storage/podcasts/welcome/123.mp3",
                "intro_video_path": "/storage/podcasts/intro/123.mp4",
                "bumper_video_path": "/storage/podcasts/bumper/123.mp4",
                "short_video_path": "/storage/podcasts/short/123.mp4",
                "main_video_path": "/storage/podcasts/main/123.mp4",
                "outro_video_path": "/storage/podcasts/outro/123.mp4",
                "welcome_video_avatar_path": "/storage/podcasts/welcome_avatar/123.mp4",
                "created_at": "2025-04-24T12:00:00Z",
                "updated_at": "2025-04-24T12:00:00Z"
            }
        }
