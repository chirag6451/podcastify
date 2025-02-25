#!/usr/bin/env python3
import time
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from video_creator import HeyGenAPI
from video_creator.db_utils import VideoDB
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('heygen_monitor.log')
    ]
)
logger = logging.getLogger(__name__)

class HeyGenVideoMonitor:
    # Status constants
    FINAL_STATUSES = {'completed', 'error', 'aborted'}
    
    def __init__(self, poll_interval=5):
        load_dotenv()
        self.db = VideoDB()
        self.api = HeyGenAPI()
        self.poll_interval = poll_interval
        
    def get_in_progress_videos(self):
        """Get all videos that haven't reached a final status"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT task_id, heygen_video_id, status, created_at, last_updated_at
                    FROM heygen_videos
                    WHERE status NOT IN ('completed', 'error', 'aborted')
                    ORDER BY created_at DESC
                """)
                return cursor.fetchall()
    
    def update_video_status(self, video_id, current_status):
        """Check and update status for a single video"""
        # Don't check status for final statuses
        if current_status in self.FINAL_STATUSES:
            return current_status
            
        try:
            response = self.api.check_video_status(video_id)
            new_status = response.get("data", {}).get("status", "").lower()
            
            # Only update if status has changed
            if new_status != current_status:
                # For completed videos, get URLs and save files
                if new_status == 'completed':
                    data = response.get("data", {})
                    video_url = data.get("video_url")
                    thumbnail_url = data.get("thumbnail_url")
                    
                    # Generate local file paths
                    video_path = f"videos/heygen_{video_id}.mp4"
                    thumbnail_path = f"thumbnails/heygen_{video_id}.jpg"
                    
                    # Ensure directories exist
                    os.makedirs("videos", exist_ok=True)
                    os.makedirs("thumbnails", exist_ok=True)
                    
                    # Download files
                    try:
                        self.api.download_video(video_url, video_path)
                        self.api.download_video(thumbnail_url, thumbnail_path)
                        logger.info(f"Downloaded video and thumbnail for {video_id}")
                        
                        # Update heygen_videos table with all information
                        success = self.db.update_heygen_video_status(
                            video_id, 
                            new_status,
                            video_url=video_url,
                            thumbnail_url=thumbnail_url,
                            video_path=video_path,
                            thumbnail_path=thumbnail_path
                        )
                        
                        # Update video_paths table with heygen video path
                        with self.db.get_connection() as conn:
                            with conn.cursor() as cursor:
                                cursor.execute("""
                                    UPDATE video_paths 
                                    SET hygen_short_video = %s
                                    WHERE job_id = (
                                        SELECT task_id 
                                        FROM heygen_videos 
                                        WHERE heygen_video_id = %s
                                    )
                                """, (video_path, video_id))
                                conn.commit()
                                logger.info(f"Updated video_paths table with heygen video path for video {video_id}")
                                
                    except Exception as e:
                        logger.error(f"Error downloading files for video {video_id}: {e}")
                        # Still update status but without paths
                        success = self.db.update_heygen_video_status(
                            video_id, 
                            new_status,
                            video_url=video_url,
                            thumbnail_url=thumbnail_url
                        )
                else:
                    # For non-completed status, just update status
                    success = self.db.update_heygen_video_status(video_id, new_status)
                
                if success:
                    logger.info(f"Updated video {video_id} status: {current_status} -> {new_status}")
                else:
                    logger.warning(f"Failed to update video {video_id} status in database")
            else:
                logger.debug(f"Video {video_id} status unchanged: {current_status}")
                
            return new_status
            
        except Exception as e:
            logger.error(f"Error checking status for video {video_id}: {e}")
            # Only mark as error if it's a permanent error
            if "not found" in str(e).lower() or "invalid" in str(e).lower():
                self.db.update_heygen_video_status(video_id, "error")
                return "error"
            return current_status
    
    def run(self):
        """Main monitoring loop"""
        logger.info("Starting HeyGen video monitor...")
        
        while True:
            try:
                # Get all non-final status videos
                in_progress_videos = self.get_in_progress_videos()
                
                if not in_progress_videos:
                    logger.info("No videos in progress. Waiting...")
                else:
                    logger.info(f"Found {len(in_progress_videos)} videos in progress")
                    
                    # Update each video's status
                    for task_id, video_id, current_status, created_at, last_updated_at in in_progress_videos:
                        logger.info(f"Checking video {video_id} (task {task_id}, current: {current_status}, created: {created_at})")
                        new_status = self.update_video_status(video_id, current_status)
                        
                        if new_status in self.FINAL_STATUSES:
                            logger.info(f"Video {video_id} reached final status: {new_status}")
                
                # Wait before next check
                time.sleep(self.poll_interval)
                
            except KeyboardInterrupt:
                logger.info("Stopping monitor...")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.poll_interval)  # Wait before retrying

def main():
    monitor = HeyGenVideoMonitor()
    monitor.run()

if __name__ == "__main__":
    main()
