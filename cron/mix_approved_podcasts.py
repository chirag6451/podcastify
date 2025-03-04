#!/usr/bin/env python3
import os
import sys
from datetime import datetime
import logging
from pydub import AudioSegment
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import colorlog

# Add parent directory to path to import from project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OUTPUTS_DIR

# Configure logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s:%(name)s:%(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))

logger = colorlog.getLogger('mix_podcasts')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def get_db_session():
    """Create database session"""
    POSTGRES_USER = os.getenv("POSTGRES_USER", "chiragahmedabadi")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "indapoint")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "podcraftai")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()

def mix_audio_files(audio_files, output_path, crossfade_duration=1000, outro_duration=10000):
    """Mix audio files with crossfade and background music"""
    try:
        if not audio_files:
            raise ValueError("No audio files provided for mixing")

        # Background music paths with different moods
        bg_music_files = {
            'calm': "defaults/bgmusic/soft_theme_main_track.mp3",
            'upbeat': "defaults/bgmusic/s3.mp3"
        }
        
        # Transition sound effects
        transition_effects = {
            'whoosh': "defaults/sound_effects/Tech/Tech-06.wav",  # You'll need to add these files
            'chime': "defaults/sound_effects/Tech/Tech-02.wav",
            'pop': "defaults/sound_effects/Tech/Tech-03.wav"
        }
        
        # Load background music files
        bg_music = {}
        for mood, file_path in bg_music_files.items():
            if os.path.exists(file_path):
                bg_music[mood] = AudioSegment.from_file(file_path)
            else:
                logger.error(f"Background music file not found: {file_path}")
        
        # Load transition effects
        effects = {}
        for effect_name, file_path in transition_effects.items():
            if os.path.exists(file_path):
                effects[effect_name] = AudioSegment.from_file(file_path)
                # Make effects subtle
                effects[effect_name] = effects[effect_name] - 15  # -15dB
            else:
                logger.warning(f"Effect file not found: {file_path}")

        # Load the first audio file
        mixed = AudioSegment.from_file(audio_files[0])
        logger.info(f"Loaded first audio file: {audio_files[0]}")

        # Add subsequent files with enhanced transitions
        current_bg_index = 0
        for i, audio_file in enumerate(audio_files[1:], 1):
            if not os.path.exists(audio_file):
                logger.error(f"Audio file not found: {audio_file}")
                continue

            # Load next audio segment
            next_audio = AudioSegment.from_file(audio_file)
            logger.info(f"Loaded next audio file: {audio_file}")
            
            # Choose background music based on position
            bg_mood = 'upbeat' if i % 2 == 0 else 'calm'
            if bg_music.get(bg_mood):
                bg_segment = bg_music[bg_mood]
                # Use 5 seconds of background music
                bg_duration = 5000
                bg_segment = bg_segment[:bg_duration]
                
                # Dynamic volume adjustment
                # Analyze speech volume in next segment
                speech_volume = next_audio.dBFS
                # Adjust bg music volume to be 15dB below speech
                target_volume = speech_volume - 15
                volume_change = target_volume - bg_segment.dBFS
                bg_segment = bg_segment + volume_change
                
                # Fade background music in and out
                bg_segment = bg_segment.fade_in(1000).fade_out(1000)
                
                # Add transition effect if available
                if effects:
                    effect = effects['whoosh' if i % 3 == 0 else 'chime' if i % 3 == 1 else 'pop']
                    if effect:
                        # Add effect at start of transition
                        bg_segment = effect.overlay(bg_segment[:1000]) + bg_segment[1000:]
                
                # Add background music
                mixed = mixed.append(bg_segment, crossfade=crossfade_duration)
            
            # Add next audio segment
            mixed = mixed.append(next_audio, crossfade=crossfade_duration)
            logger.info(f"Added background music ({bg_duration/1000}s) and next segment with effects")

        # Enhanced outro
        if bg_music.get('calm'):
            outro_music = bg_music['calm'][:outro_duration]
            # Create layered outro effect
            if effects.get('chime'):
                # Add subtle chimes throughout outro
                chime_positions = [2000, 5000, 8000]  # at 2s, 5s, and 8s
                for pos in chime_positions:
                    if pos < outro_duration:
                        outro_music = outro_music.overlay(effects['chime'], position=pos)
            
            # Fade in/out the outro music
            outro_music = outro_music.fade_in(2000).fade_out(2000)
            # Adjust volume
            outro_music = outro_music - 10
            
            # Get the last segment of the mixed audio
            last_segment = mixed[-outro_duration:]
            # Overlay the enhanced outro
            last_segment = last_segment.overlay(outro_music)
            
            # Replace the last segment
            mixed = mixed[:-outro_duration] + last_segment
            logger.info(f"Added enhanced outro in last {outro_duration/1000} seconds")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Export with higher quality
        mixed.export(output_path, format="mp3", bitrate="192k")
        logger.info(f"Successfully exported mixed audio to: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error mixing audio files: {str(e)}")
        return False

def process_approved_podcasts():
    """Process all podcasts that need final mixing"""
    session = get_db_session()
    try:
        # Get all podcasts that need final mixing
        approved_podcasts = session.execute(
            text("""
                SELECT * FROM podcast_audio_details
                WHERE final_mix_path IS NOT NULL
                AND final_podcast_audio_path IS NULL
                AND default_podcast_intro_audio_path IS NOT NULL
                AND welcome_audio_path IS NOT NULL
            """)
        ).fetchall()

        logger.info(f"Found {len(approved_podcasts)} podcasts to process")

        for podcast in approved_podcasts:
            try:
                # Create output path for final mixed audio
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"final_podcast_{podcast.job_id}_{timestamp}.mp3"
                output_path = os.path.join(OUTPUTS_DIR, str(podcast.job_id), "final", output_filename)

                # List of audio files to mix in order
                default_intro_audio_path = "profiles/indapoint/audios/indapoint_intro.mp3"
                audio_files = [
                    podcast.welcome_audio_path,
                    default_intro_audio_path,
                    podcast.final_mix_path
                ]

                logger.info(f"Starting audio mix for podcast {podcast.job_id}")
                logger.info(f"Audio files to mix: {audio_files}")

                # Mix the audio files
                if mix_audio_files(audio_files, output_path):
                    # Update the database with the final podcast audio path and approval details
                    session.execute(
                        text("""
                            UPDATE podcast_audio_details 
                            SET final_podcast_audio_path = :path,
                                approval_status = 'approved',
                                approved_at = CURRENT_TIMESTAMP,
                                approved_by = 'system',
                                approved_version = COALESCE(approved_version, 0) + 1,
                                approval_comments = 'Final mix completed successfully',
                                updated_at = CURRENT_TIMESTAMP
                            WHERE job_id = :job_id
                        """),
                        {"path": output_path, "job_id": podcast.job_id}
                    )
                    session.commit()
                    logger.info(f"Successfully processed and approved podcast {podcast.job_id}")
                else:
                    logger.error(f"Failed to mix audio for podcast {podcast.job_id}")

            except Exception as e:
                logger.error(f"Error processing podcast {podcast.job_id}: {str(e)}")
                session.rollback()

    except Exception as e:
        logger.error(f"Database error: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    logger.info("Starting podcast mixing process")
    process_approved_podcasts()
    logger.info("Finished podcast mixing process")
