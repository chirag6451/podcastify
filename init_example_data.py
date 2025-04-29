"""
Purpose and Objective: 
This script initializes example data for the PodcastAI platform including users, master data,
podcasts, and episodes. It's designed for development and testing purposes to provide
a comprehensive set of sample data that demonstrates the platform's capabilities.
"""

import os
import sys
from pathlib import Path
import logging
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from passlib.context import CryptContext

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path to fix imports
sys.path.insert(0, str(Path(__file__).parent))

# Import database configuration and models
from api.db import engine, Base, get_db
from api.models.user import User, UserSettings, BusinessInformation
from api.models.podcast import Podcast, PodcastGroup, Episode, PodcastPlatformConfig
from api.models.style import ConversationStyle, VideoStyle, ProfileType
from api.models.voice import ElevenlabsVoice
from api.models.speaker import Speaker

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password for storing"""
    return pwd_context.hash(password)

def init_master_data(db: Session):
    """Initialize master data if not already present"""
    # Check if master data exists
    if db.query(ConversationStyle).count() == 0:
        logger.info("Initializing master data...")
        init_conversation_styles(db)
        init_video_styles(db)
        init_profile_types(db)
        init_voices(db)
        logger.info("Master data initialization complete")
    else:
        logger.info("Master data already exists, skipping initialization")

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
        style = ConversationStyle(**style_data)
        db.add(style)
        logger.info(f"Added conversation style: {style_data['name']}")
    
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
        style = VideoStyle(**style_data)
        db.add(style)
        logger.info(f"Added video style: {style_data['name']}")
    
    db.commit()

def init_profile_types(db: Session):
    """Initialize profile types with default values"""
    types = [
        {"name": "Solo Host", "description": "Single host format for monologue-style podcasts"},
        {"name": "Co-hosts", "description": "Two or more regular hosts discussing topics"},
        {"name": "Interview", "description": "Host with rotating guests for interviews"},
        {"name": "Panel", "description": "Multiple speakers discussing topics in a panel format"},
        {"name": "Storytelling", "description": "Narrative-driven format focusing on storytelling"}
    ]
    
    for type_data in types:
        profile_type = ProfileType(**type_data)
        db.add(profile_type)
        logger.info(f"Added profile type: {type_data['name']}")
    
    db.commit()

def init_voices(db: Session):
    """Initialize voice options with default values"""
    voices = [
        {"voice_id": "voice_1", "name": "Alex", "description": "Deep, authoritative male voice", "labels": {"gender": "male", "accent": "American"}},
        {"voice_id": "voice_2", "name": "Sophia", "description": "Clear, professional female voice", "labels": {"gender": "female", "accent": "British"}},
        {"voice_id": "voice_3", "name": "Michael", "description": "Warm, friendly male voice", "labels": {"gender": "male", "accent": "Australian"}},
        {"voice_id": "voice_4", "name": "Emma", "description": "Energetic, youthful female voice", "labels": {"gender": "female", "accent": "American"}},
        {"voice_id": "voice_5", "name": "James", "description": "Sophisticated male voice with British accent", "labels": {"gender": "male", "accent": "British"}},
        {"voice_id": "voice_6", "name": "Olivia", "description": "Relaxed female voice with Australian accent", "labels": {"gender": "female", "accent": "Australian"}}
    ]
    
    for voice_data in voices:
        voice = ElevenlabsVoice(**voice_data)
        db.add(voice)
        logger.info(f"Added voice: {voice_data['name']}")
    
    db.commit()

def init_example_users(db: Session):
    """Initialize example users with settings and business information"""
    # Check if users already exist
    if db.query(User).count() > 0:
        logger.info("Users already exist, skipping user initialization")
        return db.query(User).all()
    
    logger.info("Initializing example users...")
    
    users_data = [
        {
            "email": "john.doe@example.com",
            "password": "password123",
            "name": "John Doe",
            "settings": {
                "theme": "light",
                "notifications_enabled": True,
                "language_preference": "en"
            },
            "business": {
                "company_name": "Doe Enterprises",
                "industry": "Technology",
                "website": "https://doe-enterprises.example.com",
                "address": "123 Tech Lane, San Francisco, CA",
                "phone": "+1-555-123-4567"
            }
        },
        {
            "email": "jane.smith@example.com",
            "password": "securepass456",
            "name": "Jane Smith",
            "settings": {
                "theme": "dark",
                "notifications_enabled": True,
                "language_preference": "en"
            },
            "business": {
                "company_name": "Smith Media",
                "industry": "Media & Entertainment",
                "website": "https://smith-media.example.com",
                "address": "456 Media Blvd, Los Angeles, CA",
                "phone": "+1-555-765-4321"
            }
        },
        {
            "email": "alex.johnson@example.com",
            "password": "alexj789",
            "name": "Alex Johnson",
            "settings": {
                "theme": "system",
                "notifications_enabled": False,
                "language_preference": "en"
            },
            "business": {
                "company_name": "Johnson Podcasts",
                "industry": "Education",
                "website": "https://johnson-podcasts.example.com",
                "address": "789 Education Ave, Boston, MA",
                "phone": "+1-555-987-6543"
            }
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        # Create user
        user = User(
            email=user_data["email"],
            password_hash=hash_password(user_data["password"]),
            name=user_data["name"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(user)
        db.flush()  # Flush to get the user ID
        
        # Create user settings
        settings_data = user_data["settings"]
        settings = UserSettings(
            user_id=user.id,
            theme=settings_data["theme"],
            notifications_enabled=settings_data["notifications_enabled"],
            language_preference=settings_data["language_preference"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(settings)
        
        # Create business information
        business_data = user_data["business"]
        business = BusinessInformation(
            user_id=user.id,
            company_name=business_data["company_name"],
            industry=business_data["industry"],
            website=business_data["website"],
            address=business_data["address"],
            phone=business_data["phone"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(business)
        
        logger.info(f"Added user: {user_data['name']} ({user_data['email']})")
        created_users.append(user)
    
    db.commit()
    return created_users

def init_example_speakers(db: Session, users):
    """Initialize example speakers for each user"""
    if db.query(Speaker).count() > 0:
        logger.info("Speakers already exist, skipping speaker initialization")
        return db.query(Speaker).all()
    
    logger.info("Initializing example speakers...")
    
    # Get available voices
    voices = db.query(ElevenlabsVoice).all()
    if not voices:
        logger.error("No voices found. Please initialize master data first.")
        return []
    
    # Get profile types
    profile_types = db.query(ProfileType).all()
    if not profile_types:
        logger.error("No profile types found. Please initialize master data first.")
        return []
    
    speakers_data = [
        {"name": "David Miller", "bio": "Tech entrepreneur and podcast host", "social_twitter": "@davidmiller", "social_linkedin": "davidmiller", "social_website": "https://davidmiller.example.com"},
        {"name": "Sarah Chen", "bio": "Marketing expert and public speaker", "social_twitter": "@sarahchen", "social_linkedin": "sarahchen", "social_website": "https://sarahchen.example.com"},
        {"name": "Robert Taylor", "bio": "Business consultant with 15 years of experience", "social_twitter": "@roberttaylor", "social_linkedin": "roberttaylor", "social_website": "https://roberttaylor.example.com"},
        {"name": "Emily Wilson", "bio": "Journalist and storyteller", "social_twitter": "@emilywilson", "social_linkedin": "emilywilson", "social_website": "https://emilywilson.example.com"},
        {"name": "Michael Brown", "bio": "Professor of Computer Science", "social_twitter": "@michaelbrown", "social_linkedin": "michaelbrown", "social_website": "https://michaelbrown.example.com"},
        {"name": "Jennifer Lee", "bio": "Author and creative writing instructor", "social_twitter": "@jenniferlee", "social_linkedin": "jenniferlee", "social_website": "https://jenniferlee.example.com"}
    ]
    
    created_speakers = []
    
    for user in users:
        # Create 2 speakers for each user
        for i in range(2):
            speaker_data = speakers_data[len(created_speakers) % len(speakers_data)]
            voice = random.choice(voices)
            profile_type = random.choice(profile_types)
            
            speaker = Speaker(
                user_id=user.id,
                name=speaker_data["name"],
                bio=speaker_data["bio"],
                profile_type_id=profile_type.id,
                voice_id=voice.voice_id,
                social_twitter=speaker_data["social_twitter"],
                social_linkedin=speaker_data["social_linkedin"],
                social_website=speaker_data["social_website"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(speaker)
            created_speakers.append(speaker)
            logger.info(f"Added speaker: {speaker_data['name']} for user {user.name}")
    
    db.commit()
    return created_speakers

def init_example_podcasts(db: Session, users):
    """Initialize example podcasts and podcast groups for each user"""
    if db.query(Podcast).count() > 0:
        logger.info("Podcasts already exist, skipping podcast initialization")
        return db.query(Podcast).all()
    
    logger.info("Initializing example podcasts...")
    
    # Get available styles and profile types
    video_styles = db.query(VideoStyle).all()
    conversation_styles = db.query(ConversationStyle).all()
    profile_types = db.query(ProfileType).all()
    speakers = db.query(Speaker).all()
    
    if not video_styles or not conversation_styles or not profile_types:
        logger.error("Missing master data. Please initialize master data first.")
        return []
    
    podcast_groups_data = [
        {"name": "Technology", "description": "Podcasts about technology and innovation"},
        {"name": "Business", "description": "Podcasts about business strategies and entrepreneurship"},
        {"name": "Education", "description": "Educational podcasts on various topics"},
        {"name": "Entertainment", "description": "Entertainment and lifestyle podcasts"}
    ]
    
    podcasts_data = [
        {
            "title": "Tech Talks",
            "description": "Exploring the latest in technology and digital innovation",
            "language": "en",
            "audience_type": "Tech enthusiasts",
            "categories": ["Technology", "Innovation", "Digital"],
            "keywords": ["tech", "innovation", "digital", "future"]
        },
        {
            "title": "Business Insights",
            "description": "Strategic discussions on business growth and entrepreneurship",
            "language": "en",
            "audience_type": "Entrepreneurs and business professionals",
            "categories": ["Business", "Entrepreneurship", "Strategy"],
            "keywords": ["business", "entrepreneurship", "strategy", "growth"]
        },
        {
            "title": "Learning Lab",
            "description": "Educational podcast covering diverse academic topics",
            "language": "en",
            "audience_type": "Students and lifelong learners",
            "categories": ["Education", "Learning", "Academic"],
            "keywords": ["education", "learning", "academic", "knowledge"]
        },
        {
            "title": "Creative Corner",
            "description": "Exploring creativity in art, design, and media",
            "language": "en",
            "audience_type": "Creative professionals and enthusiasts",
            "categories": ["Creativity", "Art", "Design"],
            "keywords": ["creativity", "art", "design", "media"]
        }
    ]
    
    created_podcasts = []
    
    for user in users:
        # Create 1-2 podcast groups for each user
        user_groups = []
        for i in range(random.randint(1, 2)):
            group_data = podcast_groups_data[i % len(podcast_groups_data)]
            group = PodcastGroup(
                user_id=user.id,
                name=f"{group_data['name']} - {user.name}",
                description=group_data["description"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(group)
            db.flush()
            user_groups.append(group)
            logger.info(f"Added podcast group: {group.name} for user {user.name}")
        
        # Create 1-3 podcasts for each user
        for i in range(random.randint(1, 3)):
            podcast_data = podcasts_data[i % len(podcasts_data)]
            group = random.choice(user_groups) if user_groups else None
            
            # Get random styles and speakers for this user
            video_style = random.choice(video_styles)
            conversation_style = random.choice(conversation_styles)
            profile_type = random.choice(profile_types)
            
            # Find speakers for this user
            user_speakers = [s for s in speakers if s.user_id == user.id]
            speaker1 = user_speakers[0] if len(user_speakers) > 0 else None
            speaker2 = user_speakers[1] if len(user_speakers) > 1 else None
            
            podcast = Podcast(
                user_id=user.id,
                title=f"{podcast_data['title']} with {user.name}",
                description=podcast_data["description"],
                language=podcast_data["language"],
                audience_type=podcast_data["audience_type"],
                categories=podcast_data["categories"],
                keywords=podcast_data["keywords"],
                group_id=group.id if group else None,
                video_style_id=video_style.id,
                conversation_style_id=conversation_style.id,
                profile_type_id=profile_type.id,
                speaker1_id=speaker1.id if speaker1 else None,
                speaker2_id=speaker2.id if speaker2 else None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(podcast)
            db.flush()
            created_podcasts.append(podcast)
            logger.info(f"Added podcast: {podcast.title} for user {user.name}")
    
    db.commit()
    return created_podcasts

def init_example_episodes(db: Session, podcasts):
    """Initialize example episodes for each podcast"""
    if db.query(Episode).count() > 0:
        logger.info("Episodes already exist, skipping episode initialization")
        return
    
    logger.info("Initializing example episodes...")
    
    episodes_data = [
        {
            "title": "Introduction to the Series",
            "description": "Welcome to our first episode where we introduce the podcast and what to expect in future episodes.",
            "keywords": ["introduction", "welcome", "overview"],
            "status": "published"
        },
        {
            "title": "Deep Dive: Key Concepts",
            "description": "In this episode, we explore the fundamental concepts that will form the foundation of our discussions.",
            "keywords": ["concepts", "fundamentals", "deep dive"],
            "status": "published"
        },
        {
            "title": "Expert Interview: Industry Perspectives",
            "description": "We interview a leading expert to get their perspective on current industry trends and future directions.",
            "keywords": ["interview", "expert", "industry", "trends"],
            "status": "draft"
        },
        {
            "title": "Case Study Analysis",
            "description": "An in-depth analysis of a relevant case study, examining key lessons and takeaways.",
            "keywords": ["case study", "analysis", "lessons"],
            "status": "draft"
        },
        {
            "title": "Q&A Session: Audience Questions",
            "description": "We answer questions submitted by our audience, covering a range of topics related to our podcast theme.",
            "keywords": ["questions", "answers", "audience", "Q&A"],
            "status": "scheduled"
        }
    ]
    
    for podcast in podcasts:
        # Create 2-5 episodes for each podcast
        for i in range(random.randint(2, 5)):
            episode_data = episodes_data[i % len(episodes_data)]
            
            # Set publish date based on status
            publish_date = None
            if episode_data["status"] == "published":
                # Published episodes have a past date
                days_ago = random.randint(1, 30)
                publish_date = datetime.utcnow() - timedelta(days=days_ago)
            elif episode_data["status"] == "scheduled":
                # Scheduled episodes have a future date
                days_ahead = random.randint(1, 14)
                publish_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            # Get the same styles and speakers as the podcast
            episode = Episode(
                podcast_id=podcast.id,
                title=f"{episode_data['title']} - Episode {i+1}",
                description=episode_data["description"],
                keywords=episode_data["keywords"],
                language=podcast.language,
                status=episode_data["status"],
                publish_date=publish_date,
                video_style_id=podcast.video_style_id,
                conversation_style_id=podcast.conversation_style_id,
                speaker1_id=podcast.speaker1_id,
                speaker2_id=podcast.speaker2_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(episode)
            logger.info(f"Added episode: {episode.title} for podcast {podcast.title}")
    
    db.commit()

def init_example_platform_configs(db: Session, podcasts):
    """Initialize example platform configurations for each podcast"""
    if db.query(PodcastPlatformConfig).count() > 0:
        logger.info("Platform configs already exist, skipping platform config initialization")
        return
    
    logger.info("Initializing example platform configurations...")
    
    platforms = [
        {"id": 1, "name": "Spotify"},
        {"id": 2, "name": "Apple Podcasts"},
        {"id": 3, "name": "Google Podcasts"},
        {"id": 4, "name": "YouTube"}
    ]
    
    for podcast in podcasts:
        # Create 1-3 platform configs for each podcast
        for i in range(random.randint(1, 3)):
            platform = platforms[i % len(platforms)]
            
            config = PodcastPlatformConfig(
                podcast_id=podcast.id,
                platform_id=platform["id"],
                enabled=True,
                auto_publish=random.choice([True, False]),
                account_id=f"account_{podcast.user_id}_{platform['id']}",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(config)
            logger.info(f"Added platform config: {platform['name']} for podcast {podcast.title}")
    
    db.commit()

def main():
    """Main function to initialize all example data"""
    # Get database session
    db = next(get_db())
    
    try:
        # Initialize master data first
        init_master_data(db)
        
        # Initialize example users
        users = init_example_users(db)
        
        # Initialize example speakers
        speakers = init_example_speakers(db, users)
        
        # Initialize example podcasts and podcast groups
        podcasts = init_example_podcasts(db, users)
        
        # Initialize example episodes
        init_example_episodes(db, podcasts)
        
        # Initialize example platform configurations
        init_example_platform_configs(db, podcasts)
        
        logger.info("Example data initialization complete!")
        
    except Exception as e:
        logger.error(f"Error initializing example data: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
