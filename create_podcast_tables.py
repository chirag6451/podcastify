"""
Purpose and Objective: 
This script creates all the new tables needed for the podcast creation platform.
It only creates tables that don't already exist in the database.
"""

import os
import sys
from pathlib import Path
from sqlalchemy import inspect
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path to fix imports
sys.path.insert(0, str(Path(__file__).parent))

# Import database configuration
from api.db import engine, Base

# Import all models from podcast_models
from api.podcast_models import (
    ConversationStyle, VideoStyle, ProfileType, Platform,
    User, UserSettings, PodcastGroup, Speaker, Podcast, Episode,
    PodcastPlatformConfig, Credit, CreditUsage
)

# Import payment models
from api.payment_models import (
    Plan, Subscription, Transaction, PaymentMethod, PasswordReset, BusinessInformation
)

def create_tables():
    """Create all tables defined in podcast_models.py and payment_models.py"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    # Get all table classes from podcast_models and payment_models
    table_models = [
        # Podcast models
        ConversationStyle, VideoStyle, ProfileType, Platform,
        User, UserSettings, PodcastGroup, Speaker, Podcast, Episode,
        PodcastPlatformConfig, Credit, CreditUsage,
        
        # Payment models
        Plan, Subscription, Transaction, PaymentMethod, PasswordReset, BusinessInformation
    ]
    
    # Create tables that don't exist yet
    tables_to_create = []
    for model in table_models:
        table_name = model.__tablename__
        if table_name not in existing_tables:
            tables_to_create.append(model.__table__)
            logger.info(f"Table '{table_name}' will be created")
        else:
            logger.info(f"Table '{table_name}' already exists, skipping")
    
    if tables_to_create:
        Base.metadata.create_all(engine, tables=tables_to_create)
        logger.info(f"Created {len(tables_to_create)} new tables")
    else:
        logger.info("No new tables to create")

if __name__ == "__main__":
    logger.info("Starting table creation process")
    create_tables()
    logger.info("Table creation process completed")
