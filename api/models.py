from sqlalchemy import Column, Integer, String, DateTime, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

load_dotenv()

# Database configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "chiragahmedabadi")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "indapoint")
POSTGRES_DB = os.getenv("POSTGRES_DB", "podcraftai")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from .db import Base

class PodcastJob(Base):
    __tablename__ = "podcast_jobs"

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

class GoogleAuthRequest(BaseModel):
    code: str

class GoogleAuthResponse(BaseModel):
    success: bool
    user_id: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
