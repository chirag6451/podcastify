"""
Purpose and Objective: 
This module organizes and exports all API route modules for the podcast platform.
It provides a clean way to include all routers in the main FastAPI application.
"""

from .user import router as user_router
from .voice import router as voice_router
from .style import router as style_router
from .podcast import router as podcast_router
# Import other routers as they are created
# from .speaker import router as speaker_router

__all__ = [
    "user_router",
    "voice_router",
    "style_router",
    "podcast_router"
]
