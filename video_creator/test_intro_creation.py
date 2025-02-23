#!/usr/bin/env python3
import os
import logging
import colorlog
from utils.podcast_intro_creator import create_podcast_intro

def setup_logger():
    """Set up colored logging configuration"""
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s %(levelname)s: %(blue)s%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        }
    ))

    logger = colorlog.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

logger = setup_logger()

def test_intro_creation():
    """Test creating a podcast intro"""
    try:
        # Test files
        speaker1_video = "video_creator/defaults/speakers/g1.mp4"
        speaker2_video = "video_creator/defaults/speakers/m1.mp4"
        bg_image = "video_creator/defaults/images/podcast_bg.jpg"  # Fixed path for background image
        bg_music = "video_creator/defaults/bgmusic/s3.mp3"
        voiceover = "video_creator/defaults/voiceover/intro_script.mp3"
        
        # Validate required files
        required_files = [
            (speaker1_video, "speaker 1 video"),
            (speaker2_video, "speaker 2 video"),
            (bg_image, "background image"),
            (bg_music, "background music"),
            (voiceover, "voiceover")
        ]
        
        for file_path, file_type in required_files:
            if not os.path.exists(file_path):
                logger.error(f"{file_type.title()} file not found: {file_path}")
                return
        
        # Create podcast intro
        output_path = create_podcast_intro(
            speaker1_video_path=speaker1_video,
            speaker1_name="John Smith",
            speaker2_video_path=speaker2_video,
            speaker2_name="Jane Doe",
            title="Tech Talk Podcast",
            subtitle="Exploring the Future of Technology",
            footer="Subscribe • Like • Share",
            background_image_path=bg_image,
            duration=10,
            background_music_path=bg_music,
            voiceover_path=voiceover,
            resolution=(1920, 1080)
        )
        
        logger.info(f"Podcast intro created successfully: {output_path}")
        
    except Exception as e:
        logger.error(f"Error creating podcast intro: {str(e)}")
        raise

if __name__ == "__main__":
    test_intro_creation()
