#!/usr/bin/env python3
from video_creator import HeyGenAPI
from video_creator.db_utils import VideoDB
import json

# Constants
TASK_ID = 10  # Using an existing task ID
INPUT_TEXT = "Artificial Intelligence is transforming our world... It automates complex tasks, streamlines decision-making, and unlocks endless creative potential! In healthcare, finance, education, and beyond, AI reduces errors and saves valuable time — empowering us to focus on what truly matters... Embrace the future where technology inspires innovation and enriches every aspect of our lives!"

def handle_video_generation():
    try:
        api = HeyGenAPI()
        db = VideoDB()
        
        # First generate the video
        heygen_video_id = api.create_video_add_to_queue(
            # Character and voice parameters
            character_type="avatar",
            avatar_id="Judith_expressive_2024120201",
            avatar_style="normal",
            voice_type="text",
            input_text=INPUT_TEXT,
            voice_id="c4be407b9d94405a9eb403190d77c851",
            speed=1.1,
            # Video dimensions
            width=1280,
            height=720,
            # Background parameters (defaults to video background)
            background_type="video",
            background_asset_id="f978e4db1f2743d3a4001c0b3e6b6bb7",
            play_style="loop",
            fit="cover",
            # Output and polling parameters
            video_output_file="output_video.mp4",
            thumbnail_output_file="thumbnail.jpg",
            poll_interval=5,
            timeout=300,
            # Pass task ID for database tracking
            task_id=TASK_ID
        )
        print(f"\nVideo generation started!")
        print(f"Task ID: {TASK_ID}")
        print(f"HeyGen Video ID: {heygen_video_id}")
        
        # Add video information to database
        db_id = db.add_heygen_video(TASK_ID, heygen_video_id)
        print(f"Database record created with ID: {db_id}")
        
        print("\nUse monitor_heygen_videos.py to track the status of this video.")
            
    except Exception as e:
        print("Error generating video:", e)

if __name__ == "__main__":
    handle_video_generation()
