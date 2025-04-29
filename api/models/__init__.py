"""
Purpose and Objective: 
This module re-exports all models from domain-specific model files to provide 
a clean import interface. This allows importing models directly from api.models
while maintaining a modular, domain-based file organization.
"""

# Re-export models from domain-specific files
# These will be added as we create each model file

# Base imports
from ..db import Base, engine, SessionLocal, get_db

# User models
from .user import User, UserSettings, BusinessInformation, PasswordReset

# Style models
from .style import ConversationStyle, VideoStyle, ProfileType, Platform

# Voice models
from .voice import ElevenlabsVoice

# Speaker models
from .speaker import Speaker

# Podcast models
from .podcast import Podcast, PodcastGroup, Episode, PodcastPlatformConfig

# Payment models
from .payment import Plan, Subscription, Transaction, PaymentMethod

# Credit models
from .credit import Credit, CreditUsage

# Integration models
from .integration import CustomerYoutubeChannel, CustomerYoutubePlaylist, VideoPath

# Job models
from .podcast_job import PodcastJob

# Auth models
from .auth import GoogleAuthRequest, GoogleAuthResponse

# Create all tables
# This should be done in a separate script for production
# Base.metadata.create_all(bind=engine)
