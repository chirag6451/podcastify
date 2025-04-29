"""
Purpose and Objective: 
This module defines Pydantic models for authentication-related requests and responses,
particularly for Google OAuth authentication.
"""

from pydantic import BaseModel
from typing import Optional

class GoogleAuthRequest(BaseModel):
    """
    Pydantic model for Google authentication requests.
    Contains the authorization code from Google OAuth.
    """
    code: str

class GoogleAuthResponse(BaseModel):
    """
    Pydantic model for Google authentication responses.
    Contains user information and authentication status.
    """
    success: bool
    user_id: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
