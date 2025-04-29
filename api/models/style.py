"""
Purpose and Objective: 
This module defines SQLAlchemy models for style-related entities including
ConversationStyle, VideoStyle, ProfileType, and Platform. These models represent
the configuration options for podcast creation and distribution.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db import Base

class ConversationStyle(Base):
    """
    SQLAlchemy model for conversation styles.
    Defines different conversation patterns and tones for podcast generation.
    """
    __tablename__ = "conversation_styles"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    podcasts = relationship("Podcast", back_populates="conversation_style")
    episodes = relationship("Episode", back_populates="conversation_style")
    user_settings = relationship("UserSettings", back_populates="default_conversation_style")

class VideoStyle(Base):
    """
    SQLAlchemy model for video styles.
    Defines different visual styles and formats for podcast video generation.
    """
    __tablename__ = "video_styles"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    podcasts = relationship("Podcast", back_populates="video_style")
    episodes = relationship("Episode", back_populates="video_style")
    user_settings = relationship("UserSettings", back_populates="default_video_style")

class ProfileType(Base):
    """
    SQLAlchemy model for profile types.
    Defines different speaker profile categories for podcast participants.
    """
    __tablename__ = "profile_types"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    podcasts = relationship("Podcast", back_populates="profile_type")
    speakers = relationship("Speaker", back_populates="profile_type")

class Platform(Base):
    """
    SQLAlchemy model for distribution platforms.
    Defines different platforms where podcasts can be published.
    """
    __tablename__ = "platforms"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    type = Column(String)  # podcast, video, social
    logo_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    platform_configs = relationship("PodcastPlatformConfig", back_populates="platform")
