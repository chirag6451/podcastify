"""
Purpose and Objective: 
This module defines SQLAlchemy models for external platform integrations including
YouTube channels, playlists, and video paths. These models support publishing
podcasts to external platforms.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db import Base

class CustomerYoutubeChannel(Base):
    """
    SQLAlchemy model for YouTube channels.
    Stores YouTube channel information for users.
    """
    __tablename__ = "customer_youtube_channels"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(String(50), nullable=False)
    name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    playlists = relationship("CustomerYoutubePlaylist", back_populates="channel")

class CustomerYoutubePlaylist(Base):
    """
    SQLAlchemy model for YouTube playlists.
    Stores YouTube playlist information for organizing videos.
    """
    __tablename__ = "customer_youtube_playlists"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey("customer_youtube_channels.id"))
    playlist_id = Column(String(50), nullable=False)
    playlist_title = Column(String(255))
    playlist_description = Column(Text)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    channel = relationship("CustomerYoutubeChannel", back_populates="playlists")

class VideoPath(Base):
    """
    SQLAlchemy model for video file paths.
    Tracks paths to generated video files for podcasts.
    """
    __tablename__ = "video_paths"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("podcast_jobs.id"), nullable=True)
    audio_path = Column(String, nullable=True)
    welcome_audio_path = Column(String, nullable=True)
    intro_video_path = Column(String, nullable=True)
    bumper_video_path = Column(String, nullable=True)
    short_video_path = Column(String, nullable=True)
    main_video_path = Column(String, nullable=True)
    outro_video_path = Column(String, nullable=True)
    welcome_video_avatar_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    podcast_job = relationship("PodcastJob")
