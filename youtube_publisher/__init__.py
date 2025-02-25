"""
YouTube Publisher Module

This module handles all YouTube-related functionality including:
- Channel management
- Authentication
- Video metadata management
- Publishing workflow
"""

from .youtube_manager import YouTubeManager
from .models import YouTubeVideo, YouTubeChannel, YouTubePlaylist, VideoTemplate
from .exceptions import YouTubeError, AuthenticationError, PublishError

__all__ = [
    'YouTubeManager',
    'YouTubeVideo',
    'YouTubeChannel',
    'YouTubePlaylist',
    'VideoTemplate',
    'YouTubeError',
    'AuthenticationError',
    'PublishError'
]
