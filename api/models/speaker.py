"""
Purpose and Objective: 
This module defines the Speaker SQLAlchemy model for podcast participants.
Speakers are associated with users and can be assigned to podcasts and episodes.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db import Base

class Speaker(Base):
    """
    SQLAlchemy model for podcast speakers.
    Represents individuals who participate in podcasts, with their voice settings and profile information.
    """
    __tablename__ = "speakers"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    profile_type_id = Column(Integer, ForeignKey("profile_types.id"))
    profile_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    voice_id = Column(String, ForeignKey("elevenlabs_voices.voice_id"))
    social_twitter = Column(String, nullable=True)
    social_linkedin = Column(String, nullable=True)
    social_website = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="speakers")
    profile_type = relationship("ProfileType", back_populates="speakers")
    voice = relationship("ElevenlabsVoice", back_populates="speakers")
    
    # Podcast relationships
    podcasts_as_speaker1 = relationship("Podcast", foreign_keys="Podcast.speaker1_id", back_populates="speaker1")
    podcasts_as_speaker2 = relationship("Podcast", foreign_keys="Podcast.speaker2_id", back_populates="speaker2")
    
    # Episode relationships
    episodes_as_speaker1 = relationship("Episode", foreign_keys="Episode.speaker1_id", back_populates="speaker1")
    episodes_as_speaker2 = relationship("Episode", foreign_keys="Episode.speaker2_id", back_populates="speaker2")
