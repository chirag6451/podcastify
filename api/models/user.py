"""
Purpose and Objective: 
This module defines SQLAlchemy models for user-related entities including
User, UserSettings, and BusinessInformation. These models represent the core
user data structures for the podcast creation platform.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db import Base

class User(Base):
    """
    SQLAlchemy model for user accounts.
    Represents registered users of the platform with their authentication and profile information.
    """
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    name = Column(String)
    profile_picture = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    podcasts = relationship("Podcast", back_populates="user")
    podcast_groups = relationship("PodcastGroup", back_populates="user")
    speakers = relationship("Speaker", back_populates="user")
    credits = relationship("Credit", back_populates="user")
    credit_usage = relationship("CreditUsage", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    payment_methods = relationship("PaymentMethod", back_populates="user")
    password_resets = relationship("PasswordReset", back_populates="user")
    business_information = relationship("BusinessInformation", back_populates="user", uselist=False)

class UserSettings(Base):
    """
    SQLAlchemy model for user settings.
    Stores user preferences for podcast creation including default voices, styles, and automation settings.
    """
    __tablename__ = "user_settings"
    __table_args__ = {'extend_existing': True}

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    autopilot_mode = Column(Boolean, default=False)
    default_voice1_id = Column(String, ForeignKey("elevenlabs_voices.voice_id"), nullable=True)
    default_voice2_id = Column(String, ForeignKey("elevenlabs_voices.voice_id"), nullable=True)
    default_language = Column(String, nullable=True)
    default_video_style_id = Column(Integer, ForeignKey("video_styles.id"), nullable=True)
    default_conversation_style_id = Column(Integer, ForeignKey("conversation_styles.id"), nullable=True)
    default_duration = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="settings")
    default_voice1 = relationship("ElevenlabsVoice", foreign_keys=[default_voice1_id])
    default_voice2 = relationship("ElevenlabsVoice", foreign_keys=[default_voice2_id])
    default_video_style = relationship("VideoStyle")
    default_conversation_style = relationship("ConversationStyle")

class BusinessInformation(Base):
    """
    SQLAlchemy model for business information.
    Stores business details for users, including contact information and social media profiles.
    """
    __tablename__ = "business_information"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    business_name = Column(String(255), nullable=False)
    business_email = Column(String(255), nullable=False)
    business_type = Column(String(100), nullable=False)
    business_website = Column(String(255), nullable=True)
    instagram_handle = Column(String(100), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    facebook_url = Column(String(255), nullable=True)
    business_description = Column(Text, nullable=True)
    target_audience = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="business_information")

class PasswordReset(Base):
    """
    SQLAlchemy model for password reset tokens.
    Manages password reset requests and their expiration.
    """
    __tablename__ = "password_resets"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True, index=True)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="password_resets")
