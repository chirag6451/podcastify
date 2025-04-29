"""
Purpose and Objective: 
This module defines Pydantic schemas for voice-related API endpoints including
voice retrieval and filtering for the Elevenlabs integration.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .base import BaseSchema

class VoiceBase(BaseSchema):
    """Base schema for voice data"""
    voice_id: str = Field(..., example="21m00Tcm4TlvDq8ikWAM")
    name: str = Field(..., example="Rachel")
    category: Optional[str] = Field(None, example="premade")
    description: Optional[str] = Field(None, example="A warm and friendly female voice")
    gender: Optional[str] = Field(None, example="female")
    accent: Optional[str] = Field(None, example="american")
    age: Optional[str] = Field(None, example="young")
    language: Optional[str] = Field(None, example="en")
    use_case: Optional[str] = Field(None, example="podcast")
    preview_url: Optional[str] = Field(None, example="https://api.elevenlabs.io/v1/voices/21m00Tcm4TlvDq8ikWAM/preview")

class VoiceResponse(VoiceBase):
    """Schema for voice response"""
    labels: Optional[Dict[str, Any]] = Field(None)
    settings: Optional[Dict[str, Any]] = Field(None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "voice_id": "21m00Tcm4TlvDq8ikWAM",
                "name": "Rachel",
                "category": "premade",
                "description": "A warm and friendly female voice",
                "labels": {
                    "accent": "american",
                    "age": "young",
                    "gender": "female"
                },
                "gender": "female",
                "accent": "american",
                "age": "young",
                "language": "en",
                "use_case": "podcast",
                "preview_url": "https://api.elevenlabs.io/v1/voices/21m00Tcm4TlvDq8ikWAM/preview",
                "settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
        }

class VoiceFilter(BaseSchema):
    """Schema for filtering voices"""
    gender: Optional[str] = Field(None, example="female")
    accent: Optional[str] = Field(None, example="american")
    age: Optional[str] = Field(None, example="young")
    language: Optional[str] = Field(None, example="en")
    use_case: Optional[str] = Field(None, example="podcast")
    category: Optional[str] = Field(None, example="premade")
