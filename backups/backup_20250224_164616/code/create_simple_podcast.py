#!/usr/bin/env python3

from utils.logger_utils import PodcastLogger

# Initialize logger
logger = PodcastLogger("podcast_creator")

import os
import sys

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)


import json

from video_creator import create_podcast_video, PodcastVideoConfig, PodcastVideoMaker


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Get the package root directory
PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))


business_info = {
    "type": "podcast",
    "name": "IndaPoint AI Tech Talks",
    "website": "www dot indapoint.com",
    "email": "  info at indapoint.com",
    "social_media": {
        "twitter": "@indapoint",
        "instagram": "@indapoint"
    }
}




def example_simple():
    """Example using the simple function interface"""
    video_path = create_podcast_video(
        voiceover_path=os.path.join(PACKAGE_ROOT, "video_creator/defaults/voiceover/s3.mp3"),
        speaker1_video_path=os.path.join(PACKAGE_ROOT, "video_creator/defaults/speakers/g1.mp4"),
        speaker1_name="Ken",
        speaker2_video_path=os.path.join(PACKAGE_ROOT, "video_creator/defaults/speakers/m1.mp4"),
        speaker2_name="Jesssica",
        title="AI in Modern World",
        subtitle="Impact and Future Prospects",
        output_filename="simple_podcast.mp4",
        videos_library_path=os.path.join(PACKAGE_ROOT, "video_creator/defaults/videos"),
        background_image_path=os.path.join(PACKAGE_ROOT, "video_creator/defaults/bgimages/bg1.jpeg"),
        background_music_path=os.path.join(PACKAGE_ROOT, "video_creator/defaults/bgmusic/s3.mp3"),
        bg_music_volume=0.2,  # Set background music volume to 80% for testing
        # Custom font styles
        title_font_size=20,
        title_font_color='#05000070',
        title_font_name='Arial-Bold',
        subtitle_font_size=18,
        subtitle_font_color='#CCCCCC',
        subtitle_font_name='Arial',
        footer_font_size=15,
        footer_font_color='#FFFFFF',
        footer_font_name='Arial'
    )
    print(f"Video created at: {video_path}")

def example_with_config():
    """Example using the configuration object for more control"""
    # Create configuration with custom settings
    config = PodcastVideoConfig(
        voiceover_path=os.path.join(PACKAGE_ROOT, "video_creator/defaults/voiceover/intro_script.mp3"),
        speaker1_video_path=os.path.join(PACKAGE_ROOT, "video_creator/defaults/speakers/g1.mp4"),
        speaker1_name="Jessica  ",
        speaker2_video_path=os.path.join(PACKAGE_ROOT, "video_creator/defaults/speakers/m1.mp4"),
        speaker2_name="Ken",
        title="Deeep Seek",
        subtitle="Impact and Future Prospects",
        # Override some defaults
        resolution=(1020, 780),  # 4K resolution
        bg_music_volume=0.1,     # Reduce background music volume to 10%
        output_filename="1_deep_seek_podcast.mp4",
        footer_text="Visit our website • www.indapoint.com • | Subscribe",
        videos_library_path=os.path.join(PACKAGE_ROOT, "video_creator/defaults/videos"),
        background_image_path=os.path.join(PACKAGE_ROOT, "video_creator/defaults/bgimages/bg1.jpeg"),
        background_music_path=os.path.join(PACKAGE_ROOT, "video_creator/defaults/bgmusic/s3.mp3"),
        # Custom font styles
        title_font_size=60,       # Larger title for 4K
        title_font_color='#EBE0E2',  # Removed FF suffix
        title_font_name='Helvetica-Bold',
        subtitle_font_size=40,    # Larger subtitle for 4K
        subtitle_font_color='#eab676',  # Fixed double ## and removed FF suffix
        subtitle_font_name='Helvetica',
        footer_font_size=30,      # Larger footer for 4K
        footer_font_color='#eeeee4',  # Removed FF suffix
        footer_font_name='Helvetica'
    )
    
    # Create video using the config
    maker = PodcastVideoMaker()
    video_path = maker.create_video(config)
    print(f"Video created at: {video_path}")

if __name__ == "__main__":
    # print("Creating simple podcast video...")
    # example_simple()
    

    print("\nCreating podcast video with custom configuration...")
    example_with_config() 