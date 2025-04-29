"""
Purpose and Objective: 
This script initializes payment-related data for the podcast creation platform.
It populates the plans table with default subscription plans needed for the platform.
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
from api.payment_models import Plan

def init_plans(db: Session):
    """Initialize subscription plans with default values"""
    plans = [
        {
            "name": "Basic",
            "description": "Basic plan for podcast creation with essential features",
            "price": 9.99,
            "credits": 100,
            "features": ["Up to 5 podcast episodes per month", "Basic voice selection", "Standard video styles", "720p video quality"]
        },
        {
            "name": "Professional",
            "description": "Professional plan for serious podcasters with advanced features",
            "price": 29.99,
            "credits": 300,
            "features": ["Up to 15 podcast episodes per month", "All voice options", "All video styles", "1080p video quality", "Priority processing"]
        },
        {
            "name": "Enterprise",
            "description": "Enterprise plan for businesses and professional content creators",
            "price": 99.99,
            "credits": 1000,
            "features": ["Unlimited podcast episodes", "All voice options", "All video styles", "4K video quality", "Priority processing", "Dedicated support", "Custom branding"]
        }
    ]
    
    for plan_data in plans:
        existing = db.query(Plan).filter(Plan.name == plan_data["name"]).first()
        if not existing:
            plan = Plan(**plan_data)
            db.add(plan)
            logger.info(f"Added plan: {plan_data['name']}")
        else:
            logger.info(f"Plan already exists: {plan_data['name']}")
    
    db.commit()

def init_all_payment_data():
    """Initialize all payment-related data"""
    db = next(get_db())
    try:
        logger.info("Initializing subscription plans...")
        init_plans(db)
        
        logger.info("Payment data initialization completed successfully")
    except Exception as e:
        logger.error(f"Error initializing payment data: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting payment data initialization process")
    init_all_payment_data()
