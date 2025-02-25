#!/usr/bin/env python3
import os
import logging
import colorlog
from podcast_video_creator import PodcastVideoCreator

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

def ensure_directories():
    """Ensure required directories exist"""
    dirs = ['output', 'output/intro', 'output/outro']
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def create_sample_video():
    """Create a simple sample video"""
    logger.info("\n" + "="*50)
    logger.info("Creating Sample Video")
    logger.info("="*50 + "\n")

    try:
        # Ensure directories exist
        ensure_directories()
        
        # Test files
        bg_video = "video_creator/defaults/videos/1_optimized.mp4"
        bg_music = "video_creator/defaults/bgmusic/s3.mp3"
        logo = "video_creator/defaults/images/logo.png"
        voiceover = "video_creator/defaults/voiceover/intro_script.mp3"
        
        # Debug logging for file paths
        logger.debug("File paths being used:")
        logger.debug(f"Background video: {bg_video}")
        logger.debug(f"Background music: {bg_music}")
        logger.debug(f"Logo: {logo}")
        logger.debug(f"Voiceover: {voiceover}")
        
        # Validate required files
        required_files = [
            (bg_video, "background video"),
            (bg_music, "background music"),
            (logo, "logo"),
            (voiceover, "voiceover")
        ]
        
        for file_path, file_type in required_files:
            if not os.path.exists(file_path):
                logger.error(f"{file_type.title()} file not found: {file_path}")
                return
        
        # Create video creator instance
        video_creator = PodcastVideoCreator()
        
        # Create intro config
        intro_config = {
            'params': {
                'background_video_path': bg_video,
                'heading': "Welcome to Our Channel",
                'subheading': "Tech Insights & Innovation",
                'footer': "Subscribe • Like • Share",
                'background_music_path': bg_music,
                'output_path': "output/generated_intro7.mp4",
                'segment_type': "intro",
                'duration': 5,
                'bg_music_volume': 0.1,
                'logo_path': logo,
                'logo_width': 150,
                'logo_height': 150,
                'resolution': (3840, 2160)
            }
        }
        
        # Create outro config
        outro_config = {
            'params': {
                'background_video_path': bg_video,
                'heading': "Thanks for Watching",
                'subheading': "See You Next Time",
                'footer': "Follow us on social media",
                'background_music_path': bg_music,
                'output_path': "output/generated_outro.mp4",
                'segment_type': "outro",
                'duration': 3,
                'bg_music_volume': 0.1,
                'logo_path': logo,
                'logo_width': 150,
                'logo_height': 150,
                'resolution': (3840, 2160)
            }
        }
        
        speaker1_video = "video_creator/defaults/speakers/g1.mp4"
        speaker2_video = "video_creator/defaults/speakers/m1.mp4"
        bg_image = "video_creator/defaults/bgimages/gray-abstract-wireframe-technology-background_53876-101941.jpeg.jpeg"
        
        # Debug logging for speaker and background paths
        logger.debug(f"Speaker 1 video: {speaker1_video}")
        logger.debug(f"Speaker 2 video: {speaker2_video}")
        logger.debug(f"Background image: {bg_image}")
        
        # Validate background image exists
        if not os.path.exists(bg_image):
            logger.error(f"Background image not found at: {bg_image}")
            raise FileNotFoundError(f"Background image not found at: {bg_image}")
        
        # Set up output paths
        video_output = f"output/podcast_videos/episode_{2:03d}_intro7.mp4"
        thumbnails_dir = f"output/thumbnails/episode_{2:03d}"
        
        logger.debug(f"Video output path: {video_output}")
        logger.debug(f"Thumbnails directory: {thumbnails_dir}")
        intro_audio_path="video_creator/defaults/voiceover/intro.mp3",
        # Create video with all components
        output_path = video_creator.create_video(
            audio_path=voiceover,
            intro_audio_path=intro_audio_path,
            background_video_path=bg_video,
            background_music_path=bg_music,
            videos_library_path="video_creator/defaults/videos",
            logo_path=logo,
            resolution=(1080, 720),
            output_filename="new_final_video.mp4",
            title="Tech Insights",
            subtitle="Exploring the Future of Technology",
            speaker1_video_path=speaker1_video,
            speaker1_name="John Smith",
            speaker2_video_path=speaker2_video,
            speaker2_name="Jane Doe",
            background_image_path=bg_image,
            thumbnails_output_dir=thumbnails_dir,
            create_thumbnails_flag=True,
            intro_config=intro_config,
            outro_config=outro_config,
            bg_music_volume=0.1
        )
        
        logger.info(f"Video created successfully: {output_path}")
        
    except Exception as e:
        logger.error(f"Error creating video: {str(e)}")
        raise

if __name__ == "__main__":
    create_sample_video()
