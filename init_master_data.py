"""
Purpose and Objective: 
This script initializes master data for the podcast creation platform.
It populates the conversation styles, video styles, profile types, and platforms tables
with default values needed for the platform to function properly.
"""

import os
import sys
from pathlib import Path
import logging
from sqlalchemy.orm import Session

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path to fix imports
sys.path.insert(0, str(Path(__file__).parent))

# Import database configuration
from api.db import engine, Base, get_db
from api.podcast_models import ConversationStyle, VideoStyle, ProfileType, Platform

def init_conversation_styles(db: Session):
    """Initialize conversation styles with default values"""
    styles = [
        {"name": "Casual", "description": "Relaxed, informal conversation style suitable for everyday topics"},
        {"name": "Professional", "description": "Formal, business-oriented conversation style for professional topics"},
        {"name": "Educational", "description": "Informative, teaching-oriented style for educational content"},
        {"name": "Debate", "description": "Argumentative style with opposing viewpoints"},
        {"name": "Interview", "description": "Question-answer format with a host and guest"},
        {"name": "Storytelling", "description": "Narrative-focused style for sharing stories and experiences"}
    ]
    
    for style_data in styles:
        existing = db.query(ConversationStyle).filter(ConversationStyle.name == style_data["name"]).first()
        if not existing:
            style = ConversationStyle(**style_data)
            db.add(style)
            logger.info(f"Added conversation style: {style_data['name']}")
        else:
            logger.info(f"Conversation style already exists: {style_data['name']}")
    
    db.commit()

def init_video_styles(db: Session):
    """Initialize video styles with default values"""
    styles = [
        {"name": "Standard", "description": "Classic podcast video style with speakers side by side"},
        {"name": "Cinematic", "description": "Film-like quality with dramatic lighting and camera angles"},
        {"name": "Minimalist", "description": "Clean, simple design with minimal distractions"},
        {"name": "Dynamic", "description": "Energetic style with motion graphics and transitions"},
        {"name": "News", "description": "Professional news-like presentation with lower thirds"},
        {"name": "Animated", "description": "Cartoon-style animation representing speakers"}
    ]
    
    for style_data in styles:
        existing = db.query(VideoStyle).filter(VideoStyle.name == style_data["name"]).first()
        if not existing:
            style = VideoStyle(**style_data)
            db.add(style)
            logger.info(f"Added video style: {style_data['name']}")
        else:
            logger.info(f"Video style already exists: {style_data['name']}")
    
    db.commit()

def init_profile_types(db: Session):
    """Initialize profile types with default values"""
    types = [
        {"name": "Host", "description": "Main presenter or host of the podcast"},
        {"name": "Guest", "description": "Invited speaker or interviewee"},
        {"name": "Expert", "description": "Subject matter expert providing insights"},
        {"name": "Celebrity", "description": "Well-known personality"},
        {"name": "Character", "description": "Fictional or role-playing character"}
    ]
    
    for type_data in types:
        existing = db.query(ProfileType).filter(ProfileType.name == type_data["name"]).first()
        if not existing:
            profile_type = ProfileType(**type_data)
            db.add(profile_type)
            logger.info(f"Added profile type: {type_data['name']}")
        else:
            logger.info(f"Profile type already exists: {type_data['name']}")
    
    db.commit()

def init_platforms(db: Session):
    """Initialize platforms with default values"""
    platforms = [
        {"name": "Spotify", "type": "podcast", "logo_url": "https://storage.googleapis.com/pr-newsroom-wp/1/2018/11/Spotify_Logo_RGB_Green.png"},
        {"name": "Apple Podcasts", "type": "podcast", "logo_url": "https://www.apple.com/v/apple-podcasts/b/images/overview/hero_icon__c135x5gz14mu_large.png"},
        {"name": "Google Podcasts", "type": "podcast", "logo_url": "https://www.gstatic.com/podcasts/google_podcasts_logo_icon_248x248.png"},
        {"name": "YouTube", "type": "video", "logo_url": "https://www.youtube.com/img/desktop/yt_1200.png"},
        {"name": "SoundCloud", "type": "podcast", "logo_url": "https://developers.soundcloud.com/assets/logo_big_white-65c2b096da68dd533f68367687808425bfb608f349b193d5d2738f0d4cb09658.png"},
        {"name": "Stitcher", "type": "podcast", "logo_url": "https://www.stitcher.com/s3/press/stitcher-logo.png"}
    ]
    
    for platform_data in platforms:
        existing = db.query(Platform).filter(Platform.name == platform_data["name"]).first()
        if not existing:
            platform = Platform(**platform_data)
            db.add(platform)
            logger.info(f"Added platform: {platform_data['name']}")
        else:
            logger.info(f"Platform already exists: {platform_data['name']}")
    
    db.commit()

def init_all_master_data():
    """Initialize all master data"""
    db = next(get_db())
    try:
        logger.info("Initializing conversation styles...")
        init_conversation_styles(db)
        
        logger.info("Initializing video styles...")
        init_video_styles(db)
        
        logger.info("Initializing profile types...")
        init_profile_types(db)
        
        logger.info("Initializing platforms...")
        init_platforms(db)
        
        logger.info("Master data initialization completed successfully")
    except Exception as e:
        logger.error(f"Error initializing master data: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting master data initialization process")
    init_all_master_data()
