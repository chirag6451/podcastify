#!/usr/bin/env python3

from create_podcast_with_video import PodcastCreationConfig, create_podcast_with_video
from utils.profile_manager import ProfileManager
from utils.logger_utils import PodcastLogger
import time
import os
import json
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime

from celery_app.tasks import generate_audio_task, create_video_task
from create_podcast_with_video import PodcastCreationConfig
from api.logger import PodcastLogger

# Get package root directory
PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))

# Initialize logger
logger = PodcastLogger("podcast_tester", "test.log")

def check_task_progress(audio_task_id: str, video_task_id: str) -> None:
    """Monitor task progress"""
    
    while True:
        audio_task = generate_audio_task.AsyncResult(audio_task_id)
        video_task = create_video_task.AsyncResult(video_task_id)
        
        logger.info(f"Audio Task Status: {audio_task.status}")
        if audio_task.ready():
            if audio_task.successful():
                logger.success("Audio generation completed successfully")
            else:
                logger.error(f"Audio generation failed: {audio_task.result}")
        
        logger.info(f"Video Task Status: {video_task.status}")
        if video_task.ready():
            if video_task.successful():
                logger.success(f"Video generation completed: {video_task.result}")
                break
            else:
                logger.error(f"Video generation failed: {video_task.result}")
                break
        
        time.sleep(5)  # Check every 5 seconds

def print_profile_config(config: PodcastCreationConfig) -> None:
    """Print the configuration details for verification"""
    logger.info("\n🎯 Configuration Details:")
    logger.info("=" * 50)
    
    # Voice Settings
    logger.info("\n🎤 Voice Settings:")
    logger.info(f"Speaker 1: {config.speaker1_name} (Voice ID: {config.voice_id1})")
    logger.info(f"Speaker 2: {config.speaker2_name} (Voice ID: {config.voice_id2})")
    logger.info(f"Language: {config.language}, Accent: {config.voice_accent}")
    
    # Video Settings
    logger.info("\n🎥 Video Settings:")
    logger.info(f"Resolution: {config.resolution}")
    logger.info(f"Background Music Volume: {config.bg_music_volume}")
    
    # Logo Settings
    logger.info("\n🎨 Logo Settings:")
    logger.info(f"Main Logo: {os.path.basename(config.main_logo_path) if config.main_logo_path else 'None'}")
    logger.info(f"Watermark: {os.path.basename(config.watermark_logo_path) if config.watermark_logo_path else 'None'}")
    logger.info(f"Logo Position: {config.logo_position}")
    logger.info(f"Logo Size: {config.logo_size}")
    logger.info(f"Watermark Opacity: {config.watermark_opacity}")
    
    # Footer Settings
    logger.info("\n📝 Footer Settings:")
    logger.info(f"Text: {config.footer_text}")
    logger.info(f"Position: {config.footer_position}")
    logger.info(f"Font: {config.footer_font_name} ({config.footer_font_size}pt)")
    logger.info(f"Color: {config.footer_font_color}")
    if config.additional_footer_text:
        logger.info(f"Additional Text: {config.additional_footer_text}")
    
    # Business Info
    logger.info("\n💼 Business Info:")
    for key, value in config.business_info.items():
        if isinstance(value, dict):
            logger.info(f"{key}:")
            for k, v in value.items():
                logger.info(f"  - {k}: {v}")
        else:
            logger.info(f"{key}: {value}")
    
    logger.info("=" * 50)

def generate_fun_topic(topic_type: str = "tech") -> str:
    """Generate a fun topic based on type"""
    topics = {
        "tech": """
        🚀 The EPIC Battle: Tabs vs Spaces in Coding!
        
        Key Points:
        1. 🤔 The age-old developer debate
        2. 💻 Impact on code readability
        3. 🛠 IDE and editor preferences
        4. 🤝 Team collaboration challenges
        5. 🎮 Famous coding style wars
        
        A light-hearted look at developer preferences!
        """,
        "ai": """
        🤖 When AI Meets Dad Jokes: The Future of Humor
        
        Key Points:
        1. 😄 Can AI understand puns?
        2. 🎭 The art of timing in comedy
        3. 🧠 Neural networks and humor
        4. 🎪 AI as a comedy writer
        5. 🎯 The ultimate dad joke generator
        
        A humorous exploration of AI capabilities!
        """,
        "business": """
        💼 If Office Coffee Machines Were AI-Powered
        
        Key Points:
        1. ☕ Smart coffee preferences
        2. 📊 Analytics-driven brewing
        3. 🤖 Predictive maintenance
        4. 🎯 Productivity correlation
        5. 🌟 The future of office beverages
        
        A caffeinated look at workplace innovation!
        """
    }
    return topics.get(topic_type, topics["tech"])

def create_fun_podcast(profile_name: str, topic_type: str, topic: str = None, return_task_ids: bool = False) -> Tuple[str, str]:
    """
    Create a fun podcast using the specified profile and topic
    """
    try:
        logger.info(f"Creating podcast with profile: {profile_name}, topic_type: {topic_type}")
        
        # Load profile data
        profile_path = os.path.join(PACKAGE_ROOT, f"profiles/{profile_name}.json")
        with open(profile_path, 'r') as f:
            profile_data = json.load(f)
        
        # Create config from profile
        try:
            config = PodcastCreationConfig.from_dict(profile_data)
            config.topic_type = topic_type
            config.topic = topic
        except Exception as e:
            logger.error(f"Error loading profile configuration: {str(e)}")
            raise
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join(PACKAGE_ROOT, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Set output path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"{profile_name}_{topic_type}_{timestamp}.mp4")
        
        # Generate audio using Celery task
        audio_task = generate_audio_task.delay(
            topic=topic if topic else f"Latest trends in {topic_type}",
            num_turns=2,
            conversation_mood="explaining in simple terms",
            language=config.language,
            voice_accent=config.voice_accent,
            business_info=profile_data.get('business_info', {}),
            welcome_voice_id=config.welcome_voice_id,
            voice_id1=config.voice_id1,
            voice_id2=config.voice_id2,
            speaker1_name=config.speaker1_name,
            speaker2_name=config.speaker2_name
        )
        
        # Wait for audio task to complete
        audio_result = audio_task.get()
        audio_path, schema_path, welcome_audio_path = audio_result
        
        # Generate video using Celery task
        video_task = create_video_task.delay(
            audio_path=audio_path,
            intro_audio_path=welcome_audio_path,
            config={
                'speaker1_name': config.speaker1_name,
                'speaker2_name': config.speaker2_name,
                'title': profile_data.get('business_info', {}).get('name', 'AI Tech Talk'),
                'subtitle': f"Discussion about {topic_type}",
                'resolution': config.resolution,
                'bg_music_volume': config.bg_music_volume,
                'videos_library_path': config.videos_library_path,
                'background_image_path': config.background_image_path,
                'background_music_path': config.background_music_path,
                'title_font_size': config.title_font_size,
                'title_font_color': config.title_font_color,
                'title_font_name': config.title_font_name,
                'subtitle_font_size': config.subtitle_font_size,
                'subtitle_font_color': config.subtitle_font_color,
                'subtitle_font_name': config.subtitle_font_name,
                'footer_font_size': config.footer_font_size,
                'footer_font_color': config.footer_font_color,
                'footer_font_name': config.footer_font_name
            },
            output_filename=output_path
        )
        
        if return_task_ids:
            return audio_task.id, video_task.id
        
        # Wait for video task to complete
        video_path = video_task.get()
        return video_path

    except Exception as e:
        logger.error(f"Error in create_fun_podcast: {str(e)}")
        raise

def main():
    # Example usage
    audio_task_id, video_task_id = create_fun_podcast(
        profile_name="indapoint",
        topic_type="ai",
        return_task_ids=True
    )
    check_task_progress(audio_task_id, video_task_id)
    
    # create_fun_podcast(
    #     profile_name="techpro",
    #     topic_type="business",
    #     output_dir="fun_outputs"
    # )

if __name__ == "__main__":
    main()
