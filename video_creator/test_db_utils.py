from .db_utils import VideoDB
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_video_paths():
    db = VideoDB()
    
    # Test data
    job_id = 639  # Using an existing completed job
    test_paths = {
        'audio_path': '/tmp/podcast_639/audio.mp3',
        'welcome_audio_path': '/tmp/podcast_639/welcome.mp3',
        'intro_video_path': '/tmp/podcast_639/intro_video_1234.mp4',
        'bumper_video_path': '/tmp/podcast_639/bumper_video_1234.mp4',
        'short_video_path': '/tmp/podcast_639/short_video_1234.mp4',
        'main_video_path': '/tmp/podcast_639/main_video_1234.mp4',
        'outro_video_path': '/tmp/podcast_639/outro_video_1234.mp4',
        'welcome_video_avatar_path': '/tmp/podcast_639/welcome_avatar_1234.mp4'
    }

    try:
        # 1. Test adding video paths
        logger.info("Testing add_video_paths...")
        video_paths_id = db.add_video_paths(job_id, test_paths)
        logger.info(f"Added video paths with ID: {video_paths_id}")

        # 2. Test getting video paths
        logger.info("\nTesting get_video_paths...")
        paths = db.get_video_paths(job_id)
        logger.info(f"Retrieved paths: {paths}")

        # 3. Test updating video paths
        logger.info("\nTesting update_video_paths...")
        update_data = {
            'main_video_path': '/tmp/podcast_639/updated_main_1234.mp4',
            'short_video_path': '/tmp/podcast_639/updated_short_1234.mp4'
        }
        updated = db.update_video_paths(job_id, update_data)
        logger.info(f"Update successful: {updated}")

        # Verify the update
        paths = db.get_video_paths(job_id)
        logger.info(f"Updated paths: {paths}")

        # 4. Test getting all video paths
        logger.info("\nTesting get_all_video_paths...")
        all_paths = db.get_all_video_paths()
        logger.info(f"Total records: {len(all_paths)}")
        logger.info(f"First record: {all_paths[0] if all_paths else None}")

        # 5. Test deleting video paths
        logger.info("\nTesting delete_video_paths...")
        deleted = db.delete_video_paths(job_id)
        logger.info(f"Deletion successful: {deleted}")

        # Verify deletion
        paths = db.get_video_paths(job_id)
        logger.info(f"After deletion: {paths}")

    except Exception as e:
        logger.error(f"Error during testing: {e}")

def test_specific_paths():
    db = VideoDB()
    job_id = 639

    try:
        # 1. Test adding specific paths
        logger.info("\nTesting add_specific_path...")
        
        # Add intro video path
        success = db.add_specific_path(
            job_id=job_id,
            path_type='intro_video_path',
            path_value='/tmp/podcast_639/specific_intro_1234.mp4'
        )
        logger.info(f"Added intro path: {success}")
        
        # Add outro video path
        success = db.add_specific_path(
            job_id=job_id,
            path_type='outro_video_path',
            path_value='/tmp/podcast_639/specific_outro_1234.mp4'
        )
        logger.info(f"Added outro path: {success}")

        # 2. Test getting specific paths
        logger.info("\nTesting get_specific_path...")
        
        # Get intro path
        intro_path = db.get_specific_path(job_id, 'intro_video_path')
        logger.info(f"Retrieved intro path: {intro_path}")
        
        # Get outro path
        outro_path = db.get_specific_path(job_id, 'outro_video_path')
        logger.info(f"Retrieved outro path: {outro_path}")
        
        # Try getting non-existent path
        main_path = db.get_specific_path(job_id, 'main_video_path')
        logger.info(f"Retrieved non-existent main path: {main_path}")

        # 3. Test deleting specific path
        logger.info("\nTesting delete_specific_path...")
        
        # Delete intro path
        success = db.delete_specific_path(job_id, 'intro_video_path')
        logger.info(f"Deleted intro path: {success}")
        
        # Verify intro path is gone but outro remains
        intro_path = db.get_specific_path(job_id, 'intro_video_path')
        outro_path = db.get_specific_path(job_id, 'outro_video_path')
        logger.info(f"After deletion - intro path: {intro_path}, outro path: {outro_path}")

        # 4. Test invalid path type
        logger.info("\nTesting invalid path type...")
        result = db.get_specific_path(job_id, 'invalid_path_type')
        logger.info(f"Result with invalid path type: {result}")

        # Clean up
        db.delete_video_paths(job_id)

    except Exception as e:
        logger.error(f"Error during testing: {e}")

if __name__ == "__main__":
    test_video_paths()
    test_specific_paths()
