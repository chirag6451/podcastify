"""
Purpose and Objective: 
This module defines the PodcastJob SQLAlchemy model for tracking podcast generation jobs.
The PodcastJob model represents background processing tasks for podcast creation.
"""

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from ..db import Base

class PodcastJob(Base):
    """
    SQLAlchemy model for podcast generation jobs.
    Tracks the status and details of podcast creation processes.
    """
    __tablename__ = "podcast_jobs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    profile_name = Column(String)
    customer_id = Column(String, nullable=True)
    conversation_type = Column(String)
    topic = Column(String, nullable=True)
    status = Column(String, default="pending")
    error_message = Column(String, nullable=True)
    audio_task_id = Column(String, nullable=True)
    video_task_id = Column(String, nullable=True)
    output_path = Column(String, nullable=True)
    youtube_channel_id = Column(String(255), nullable=True)
    youtube_playlist_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """
        Convert the model instance to a dictionary for JSON serialization.
        
        Returns:
            dict: A dictionary representation of the podcast job
        """
        return {
            "id": self.id,
            "profile_name": self.profile_name,
            "customer_id": self.customer_id,
            "conversation_type": self.conversation_type,
            "topic": self.topic,
            "status": self.status,
            "error": self.error_message,
            "audio_task_id": self.audio_task_id,
            "video_task_id": self.video_task_id,
            "output_path": self.output_path,
            "youtube_channel_id": self.youtube_channel_id,
            "youtube_playlist_id": self.youtube_playlist_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
