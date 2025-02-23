#!/usr/bin/env python3
import os
import logging
import colorlog
from utils.video_segment_creator import create_video_segment

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

def ensure_directories():
    """Ensure required directories exist"""
    dirs = ['output']
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def validate_file(file_path, file_type):
    """Validate if a file exists and is of correct type"""
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    if not os.path.isfile(file_path):
        return False, f"Not a valid file: {file_path}"
    return True, None

def test_video_segments():
    """Test creating different types of video segments"""
    logger = setup_logger()
    ensure_directories()
    
    # Test files
    bg_video = "video_creator/defaults/videos/1_optimized.mp4"  # Using a known video file
    bg_music = "video_creator/defaults/bgmusic/s3.mp3"
    logo = "video_creator/defaults/images/logo.png"
    
    # Validate required files
    required_files = [
        (bg_video, "background video"),
        (bg_music, "background music"),
        (logo, "logo")
    ]
    
    for file_path, file_type in required_files:
        is_valid, error = validate_file(file_path, file_type)
        if not is_valid:
            logger.error(error)
            return
    
    # Test configurations
    configs = [
        {
            'name': 'Intro Video',
            'params': {
                'background_video_path': bg_video,
                'heading': "Welcome to Our Channel",
                'subheading': "Tech Insights & Innovation",
                'footer': "Subscribe • Like • Share",
                'background_music_path': bg_music,
                'output_path': "output/test_intro7.mp4",
                'segment_type': "intro",
                'duration': 5,
                'bg_music_volume': 0.2,  # Testing lower volume
                'logo_path': logo,
                'logo_width': 150,
                'logo_height': 150,
                'resolution': (3840, 2160)
            }
        },
        {
            'name': 'Outro Video',
            'params': {
                'background_video_path': bg_video,
                'heading': "Thanks for Watching",
                'subheading': "See You in the Next Video",
                'footer': "Don't Forget to Subscribe!",
                'background_music_path': bg_music,
                'output_path': "output/test_outro.mp4",
                'segment_type': "outro",
                'duration': 3,
                'bg_music_volume': 0.4,  # Testing higher volume
                'logo_path': logo,
                'logo_width': 150,
                'logo_height': 150,
                'resolution': (3840, 2160)
            }
        }
    ]
    
    # Test each configuration
    for config in configs:
        try:
            logger.info("\n" + "="*50)
            logger.info(f"Creating {config['name']}")
            logger.info(f"Using background music volume: {config['params']['bg_music_volume']}")
            logger.info("="*50 + "\n")
            
            output_path = create_video_segment(**config['params'])
            logger.info(f"Successfully created {config['name']}")
            logger.info(f"Output: {output_path}")
            
        except Exception as e:
            logger.error(f"Error creating {config['name']}: {str(e)}")

if __name__ == "__main__":
    test_video_segments()
