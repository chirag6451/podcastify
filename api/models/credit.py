"""
Purpose and Objective: 
This module defines SQLAlchemy models for credit-related entities including
Credit and CreditUsage. These models represent the credit system for tracking
podcast generation usage and purchases.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db import Base

class Credit(Base):
    """
    SQLAlchemy model for user credits.
    Tracks credit purchases and allocations for users.
    """
    __tablename__ = "credits"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer)
    price = Column(Float)
    transaction_id = Column(String, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="credits")

class CreditUsage(Base):
    """
    SQLAlchemy model for credit usage tracking.
    Records how credits are consumed for podcast episodes.
    """
    __tablename__ = "credit_usage"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    episode_id = Column(Integer, ForeignKey("episodes.id"))
    credits_used = Column(Integer)
    minutes_used = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="credit_usage")
    episode = relationship("Episode", back_populates="credit_usage")
