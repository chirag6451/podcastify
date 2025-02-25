#!/usr/bin/env python3
import os
import sys
import uuid
from datetime import datetime
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import json
from db_utils import PodcastDB
from logger_utils import PodcastLogger

# Initialize logger
logger = PodcastLogger("VoiceUpdater", "voice_updates.log")

def update_elevenlabs_voices():
    """Fetch latest voices from ElevenLabs and update the database."""
    try:
        logger.section("ElevenLabs Voice Update")
        start_time = datetime.now()
        
        load_dotenv()
        client = ElevenLabs(
            api_key=os.getenv("ELEVANLAB_API_KEY"),
        )

        # Get all voices from ElevenLabs
        logger.info("Fetching voices from ElevenLabs API...")
        response = client.voices.get_all()
        voices_data = [voice.model_dump() for voice in response.voices]
        logger.success(f"Retrieved {len(voices_data)} voices from ElevenLabs")
        logger.separator()
        
        # Initialize database
        db = PodcastDB()
        
        # Store each voice in the database
        logger.info("Updating database with voice information...")
        for i, voice in enumerate(voices_data, 1):
            db.upsert_elevenlabs_voice(voice)
            if i % 5 == 0 or i == len(voices_data):  # Show progress every 5 items or at the end
                logger.progress(i, len(voices_data), "Voice Database Update")
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.separator()
        logger.process_end("ElevenLabs Voice Update", True, duration)
        return True
    except Exception as e:
        logger.error(f"Failed to update ElevenLabs voices: {str(e)}")
        logger.process_end("ElevenLabs Voice Update", False)
        return False

def update_speaker_profiles():
    """Update speaker profiles from the local configuration."""
    try:
        logger.section("Speaker Profile Update")
        start_time = datetime.now()
        
        # Read speaker profiles from speakers.json
        logger.info("Reading speaker profiles from configuration...")
        with open('speakers.json', 'r') as f:
            data = json.load(f)
            speakers_data = data['speakers']
        
        db = PodcastDB()
        
        # Store each speaker profile
        logger.info("Updating database with speaker profiles...")
        for i, speaker_info in enumerate(speakers_data, 1):
            speaker = {
                'speaker_id': speaker_info.get('speaker_id', str(uuid.uuid4())),
                'name': speaker_info['name'],
                'voice_id': speaker_info['voice_id'],
                'gender': speaker_info['gender'],
                'personality': speaker_info['personality'],
                'ideal_for': speaker_info['ideal_for'],
                'accent': speaker_info['accent'],
                'best_languages': speaker_info['best_languages']
            }
            db.upsert_speaker_profile(speaker)
            if i % 3 == 0 or i == len(speakers_data):  # Show progress every 3 items or at the end
                logger.progress(i, len(speakers_data), "Speaker Profile Update")
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.separator()
        logger.process_end("Speaker Profile Update", True, duration)
        return True
    except Exception as e:
        logger.error(f"Failed to update speaker profiles: {str(e)}")
        logger.process_end("Speaker Profile Update", False)
        return False

def main():
    """Main function to update both voices and speaker profiles."""
    start_time = datetime.now()
    logger.section("Database Update Process")
    
    # Update ElevenLabs voices
    voices_success = update_elevenlabs_voices()
    
    # Update speaker profiles
    speakers_success = update_speaker_profiles()
    
    # Log completion status
    duration = (datetime.now() - start_time).total_seconds()
    logger.section("Update Summary")
    if voices_success and speakers_success:
        logger.success(f"Complete database update finished successfully in {duration:.2f} seconds")
    else:
        logger.error(f"Database update completed with some errors in {duration:.2f} seconds")
    logger.separator("=")

if __name__ == "__main__":
    main()
