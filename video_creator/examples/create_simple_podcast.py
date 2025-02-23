#!/usr/bin/env python3

import os
import sys

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from video_creator import create_podcast_video, PodcastVideoConfig, PodcastVideoMaker

# Get the package root directory
PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def example_simple():
    """Example using the simple function interface"""
    video_path = create_podcast_video(
        voiceover_path=os.path.join(PACKAGE_ROOT, "defaults/voiceover/s3.mp3"),
        speaker1_video_path=os.path.join(PACKAGE_ROOT, "defaults/speakers/g1.mp4"),
        speaker1_name="John Smith",
        speaker2_video_path=os.path.join(PACKAGE_ROOT, "defaults/speakers/m1.mp4"),
        speaker2_name="Jane Doe",
        title="AI in Modern World",
        subtitle="Impact and Future Prospects",
        output_filename="simple_podcast.mp4",
        videos_library_path=os.path.join(PACKAGE_ROOT, "defaults/videos"),
        background_image_path=os.path.join(PACKAGE_ROOT, "defaults/bgimages/bg1.jpeg"),
        background_music_path=os.path.join(PACKAGE_ROOT, "defaults/bgmusic/s3.mp3"),
        bg_music_volume=0.8,  # Set background music volume to 80% for testing
        # Custom font styles
        title_font_size=50,
        title_font_color='#FFFFFF',
        title_font_name='Arial-Bold',
        subtitle_font_size=32,
        subtitle_font_color='#CCCCCC',
        subtitle_font_name='Arial',
        footer_font_size=28,
        footer_font_color='#FFFFFF',
        footer_font_name='Arial'
    )
    print(f"Video created at: {video_path}")

def example_with_config():
    """Example using the configuration object for more control"""
    # Create configuration with custom settings
    config = PodcastVideoConfig(
        voiceover_path=os.path.join(PACKAGE_ROOT, "defaults/voiceover/intro_script.mp3"),
        # Use default speaker videos
        intro_audio_path=os.path.join(PACKAGE_ROOT, "defaults/voiceover/intro_script.mp3"),
        speaker1_video_path=os.path.join(PACKAGE_ROOT, "defaults/speakers/g1.mp4"),
        speaker1_name="Rajni Shah",
        speaker2_video_path=os.path.join(PACKAGE_ROOT, "defaults/speakers/m1.mp4"),
        speaker2_name="Chirag Shah",
        title="Hindi Podcast",
        subtitle="Hindi Podcast Test",
        # Override some defaults
        resolution=(780, 480),  # 4K resolution
        bg_music_volume=0.7,     # Set background music volume to 70% for testing
        output_filename="hindi_custom_podcast.mp4",
        footer_text="Follow us on Twitter • Subscribe • Share • Like",
        videos_library_path=os.path.join(PACKAGE_ROOT, "defaults/videos"),
        background_image_path=os.path.join(PACKAGE_ROOT, "defaults/bgimages/bg1.jpeg"),
        background_music_path=os.path.join(PACKAGE_ROOT, "defaults/bgmusic/soft_theme_main_track.mp3"),
        # Custom font styles
        title_font_size=100,       # Larger title for 4K
        title_font_color='#1B0B13FF',
        title_font_name='Helvetica-Bold',
        subtitle_font_size=60,    # Larger subtitle for 4K
        subtitle_font_color='#E1385AFF',
        subtitle_font_name='Helvetica',
        footer_font_size=80,      # Larger footer for 4K
        footer_font_color='#3B13D8FF',
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