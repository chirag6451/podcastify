import os
from video_processor import preprocess_video_for_compatibility, create_looped_video_from_section, setup_simple_logger

# Setup logging
logger = setup_simple_logger()

def test_video_processing():
    # Source video path
    source_video = "profiles/indapoint/videos/intro7.mp4"
    
    try:
        # Test video looping
        logger.info("Testing video looping...")
        looped_video = create_looped_video_from_section(
            source_video=source_video,
            width=780,
            height=480,
            target_duration=10.0,  # Create a 10 second video
            extract_seconds=2.0     # Using first 2 seconds
        )
        logger.info(f"Successfully created looped video: {looped_video}")
        logger.info(f"Original video: {source_video}")
        
    except Exception as e:
        logger.error(f"Error during video processing: {str(e)}")

if __name__ == "__main__":
    test_video_processing()
