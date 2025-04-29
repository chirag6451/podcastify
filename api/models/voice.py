"""
Purpose and Objective: 
This module defines the ElevenlabsVoice SQLAlchemy model for voice data from the Elevenlabs API.
This model stores voice metadata and is used for speaker voice selection.
"""

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..db import Base

class ElevenlabsVoice(Base):
    """
    SQLAlchemy model for Elevenlabs voices.
    Stores voice metadata from the Elevenlabs API including gender, accent, and preview URLs.
    """
    __tablename__ = "elevenlabs_voices"
    __table_args__ = {'extend_existing': True}

    voice_id = Column(String, primary_key=True)
    name = Column(String)
    category = Column(String)
    description = Column(String)
    labels = Column(JSONB)
    gender = Column(String)
    accent = Column(String)
    age = Column(String)
    language = Column(String)
    use_case = Column(String)
    preview_url = Column(String)
    settings = Column(JSONB)
    
    # Relationships
    speakers = relationship("Speaker", back_populates="voice")
    user_settings_voice1 = relationship("UserSettings", foreign_keys="UserSettings.default_voice1_id", back_populates="default_voice1")
    user_settings_voice2 = relationship("UserSettings", foreign_keys="UserSettings.default_voice2_id", back_populates="default_voice2")
