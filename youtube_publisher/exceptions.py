"""
Custom exceptions for YouTube publisher module.
"""

class YouTubeError(Exception):
    """Base exception for YouTube-related errors."""
    pass

class AuthenticationError(YouTubeError):
    """Raised when there's an authentication error with YouTube API."""
    pass

class PublishError(YouTubeError):
    """Raised when there's an error publishing a video."""
    pass

class ApprovalError(YouTubeError):
    """Raised when there's an error with video approval workflow."""
    pass

class ValidationError(YouTubeError):
    """Raised when video metadata validation fails."""
    pass
