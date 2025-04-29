"""
Purpose and Objective: 
This module defines SQLAlchemy models for podcast-related entities including
Podcast, PodcastGroup, Episode, and PodcastPlatformConfig. These models represent
the core podcast content and organization structure.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, ARRAY, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db import Base

class PodcastGroup(Base):
    """
    SQLAlchemy model for podcast groups.
    Allows users to organize podcasts into logical collections.
    """
    __tablename__ = "podcast_groups"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="podcast_groups")
    podcasts = relationship("Podcast", back_populates="group")

class Podcast(Base):
    """
    SQLAlchemy model for podcasts.
    Represents a podcast series with its metadata and configuration.
    """
    __tablename__ = "podcasts"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(Text)
    cover_image = Column(String, nullable=True)
    language = Column(String, nullable=True)
    audience_type = Column(String, nullable=True)
    categories = Column(ARRAY(String), nullable=True)
    keywords = Column(ARRAY(String), nullable=True)
    website = Column(String, nullable=True)
    email = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    group_id = Column(Integer, ForeignKey("podcast_groups.id"), nullable=True)
    video_style_id = Column(Integer, ForeignKey("video_styles.id"), nullable=True)
    conversation_style_id = Column(Integer, ForeignKey("conversation_styles.id"), nullable=True)
    profile_type_id = Column(Integer, ForeignKey("profile_types.id"), nullable=True)
    speaker1_id = Column(Integer, ForeignKey("speakers.id"), nullable=True)
    speaker2_id = Column(Integer, ForeignKey("speakers.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="podcasts")
    group = relationship("PodcastGroup", back_populates="podcasts")
    speaker1 = relationship("Speaker", foreign_keys=[speaker1_id], back_populates="podcasts_as_speaker1")
    speaker2 = relationship("Speaker", foreign_keys=[speaker2_id], back_populates="podcasts_as_speaker2")
    episodes = relationship("Episode", back_populates="podcast")
    platform_configs = relationship("PodcastPlatformConfig", back_populates="podcast")
    video_style = relationship("VideoStyle", back_populates="podcasts")
    conversation_style = relationship("ConversationStyle", back_populates="podcasts")
    profile_type = relationship("ProfileType", back_populates="podcasts")

class Episode(Base):
    """
    SQLAlchemy model for podcast episodes.
    Represents individual episodes within a podcast series.
    """
    __tablename__ = "episodes"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    podcast_id = Column(Integer, ForeignKey("podcasts.id"))
    title = Column(String)
    description = Column(Text)
    duration = Column(String, nullable=True)
    keywords = Column(ARRAY(String), nullable=True)
    language = Column(String, nullable=True)
    video_style_id = Column(Integer, ForeignKey("video_styles.id"), nullable=True)
    conversation_style_id = Column(Integer, ForeignKey("conversation_styles.id"), nullable=True)
    status = Column(String, default="draft")
    publish_date = Column(DateTime, nullable=True)
    cover_image = Column(String, nullable=True)
    speaker1_id = Column(Integer, ForeignKey("speakers.id"), nullable=True)
    speaker2_id = Column(Integer, ForeignKey("speakers.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    podcast = relationship("Podcast", back_populates="episodes")
    speaker1 = relationship("Speaker", foreign_keys=[speaker1_id], back_populates="episodes_as_speaker1")
    speaker2 = relationship("Speaker", foreign_keys=[speaker2_id], back_populates="episodes_as_speaker2")
    video_style = relationship("VideoStyle", back_populates="episodes")
    conversation_style = relationship("ConversationStyle", back_populates="episodes")
    credit_usage = relationship("CreditUsage", back_populates="episode")

class PodcastPlatformConfig(Base):
    """
    SQLAlchemy model for podcast platform configurations.
    Manages distribution settings for podcasts across different platforms.
    """
    __tablename__ = "podcast_platform_configs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    podcast_id = Column(Integer, ForeignKey("podcasts.id"))
    platform_id = Column(Integer, ForeignKey("platforms.id"))
    enabled = Column(Boolean, default=True)
    auto_publish = Column(Boolean, default=False)
    account_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    podcast = relationship("Podcast", back_populates="platform_configs")
    platform = relationship("Platform", back_populates="platform_configs")
