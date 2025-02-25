"""
Data models for YouTube publisher module.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class YouTubeChannel:
    """YouTube channel information."""
    id: int
    customer_id: str
    channel_id: str
    channel_title: str
    channel_description: Optional[str] = None
    channel_thumbnail_url: Optional[str] = None
    credentials_path: str = None
    is_active: bool = True

@dataclass
class YouTubePlaylist:
    """YouTube playlist information."""
    id: int
    channel_id: int
    playlist_id: str
    playlist_title: str
    playlist_description: Optional[str] = None
    is_default: bool = False

@dataclass
class VideoTemplate:
    """Template for video metadata."""
    id: int
    customer_id: str
    template_name: str
    title_template: str
    description_template: Optional[str] = None
    tags: List[str] = None
    privacy_status: str = 'private'
    language: str = 'en'

@dataclass
class YouTubeVideo:
    """YouTube video metadata and status."""
    id: int
    job_id: int
    customer_id: str
    channel_id: int
    title: str
    description: Optional[str] = None
    tags: List[str] = None
    thumbnail_path: Optional[str] = None
    language: str = 'en'
    privacy_status: str = 'private'
    approval_status: str = 'pending'
    approval_notes: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    publish_status: str = 'draft'
    scheduled_publish_time: Optional[datetime] = None
    youtube_video_id: Optional[str] = None
    publish_error: Optional[str] = None
    published_at: Optional[datetime] = None
    playlist_id: Optional[int] = None
    template_id: Optional[int] = None
    video_path_id: Optional[int] = None
