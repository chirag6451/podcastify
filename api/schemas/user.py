"""
Purpose and Objective: 
This module defines Pydantic schemas for user-related API endpoints including
user registration, authentication, profile management, and business information.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from .base import BaseSchema

# User schemas
class UserBase(BaseSchema):
    """Base schema for user data"""
    email: EmailStr = Field(..., example="user@example.com")
    name: str = Field(..., example="John Doe")

class UserCreate(BaseSchema):
    """Schema for user registration"""
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="securepassword123")
    name: str = Field(..., example="John Doe")

class UserLogin(BaseSchema):
    """Schema for user login"""
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="securepassword123")

class UserResponse(UserBase):
    """Schema for user response data"""
    id: int = Field(..., example=1)
    profile_picture: Optional[str] = Field(None, example="https://example.com/profile.jpg")
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-04-24T12:00:00Z")

class UserProfileUpdate(BaseSchema):
    """Schema for updating user profile"""
    name: Optional[str] = Field(None, example="John Doe")
    profile_picture: Optional[str] = Field(None, example="https://example.com/profile.jpg")

class ChangePassword(BaseSchema):
    """Schema for changing password"""
    current_password: str = Field(..., example="oldpassword123")
    new_password: str = Field(..., example="newpassword456")

class PasswordResetRequest(BaseSchema):
    """Schema for requesting password reset"""
    email: EmailStr = Field(..., example="user@example.com")

class PasswordReset(BaseSchema):
    """Schema for resetting password"""
    token: str = Field(..., example="reset-token-123")
    new_password: str = Field(..., example="newpassword456")

# Business Information schemas
class BusinessInformationBase(BaseSchema):
    """Base schema for business information"""
    business_name: str = Field(..., example="Acme Corporation")
    business_email: EmailStr = Field(..., example="contact@acme.com")
    business_type: str = Field(..., example="Technology")
    business_website: Optional[str] = Field(None, example="https://acme.com")
    instagram_handle: Optional[str] = Field(None, example="acmecorp")
    linkedin_url: Optional[str] = Field(None, example="https://linkedin.com/company/acmecorp")
    facebook_url: Optional[str] = Field(None, example="https://facebook.com/acmecorp")
    business_description: Optional[str] = Field(None, example="Leading provider of innovative solutions")
    target_audience: Optional[str] = Field(None, example="Small to medium-sized businesses")

class BusinessInformationCreate(BusinessInformationBase):
    """Schema for creating business information"""
    pass

class BusinessInformationResponse(BusinessInformationBase):
    """Schema for business information response"""
    id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-04-24T12:00:00Z")

# User Settings schemas
class UserSettingsBase(BaseSchema):
    """Base schema for user settings"""
    autopilot_mode: Optional[bool] = Field(False, example=False)
    default_voice1_id: Optional[str] = Field(None, example="21m00Tcm4TlvDq8ikWAM")
    default_voice2_id: Optional[str] = Field(None, example="AZnzlk1XvdvUeBnXmlld")
    default_language: Optional[str] = Field(None, example="en")
    default_video_style_id: Optional[int] = Field(None, example=1)
    default_conversation_style_id: Optional[int] = Field(None, example=1)
    default_duration: Optional[str] = Field(None, example="30:00")

class UserSettingsUpdate(UserSettingsBase):
    """Schema for updating user settings"""
    pass

class UserSettingsResponse(UserSettingsBase):
    """Schema for user settings response"""
    user_id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-04-24T12:00:00Z")

# Credit schemas
class CreditBalance(BaseSchema):
    """Schema for credit balance response"""
    user_id: int = Field(..., example=1)
    total_credits: int = Field(..., example=100)
    used_credits: int = Field(..., example=25)
    remaining_credits: int = Field(..., example=75)

# Token schemas
class Token(BaseSchema):
    """Schema for authentication token"""
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(..., example="bearer")

class TokenData(BaseSchema):
    """Schema for token data"""
    email: Optional[str] = None
