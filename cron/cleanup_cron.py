#!/usr/bin/env python3
import logging
import os
import sys
from typing import List, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from create_audio.db_utils import PodcastDB
from publish.youtube_manager import YouTubeManager
from publish.google_drive import GoogleDriveManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def get_users_to_cleanup(db_conn, specific_email: Optional[str] = None) -> List[str]:
    """Get list of users to cleanup"""
    with db_conn.cursor() as cur:
        if specific_email:
            cur.execute("SELECT email FROM google_auth WHERE email = %s", (specific_email,))
        else:
            cur.execute("SELECT email FROM google_auth")
        return [row[0] for row in cur.fetchall()]

def cleanup_youtube_data(user_email: str, db_conn) -> None:
    """Delete all YouTube videos and data for a user"""
    try:
        youtube = YouTubeManager(user_email)
        
        # Get all YouTube videos for user
        with db_conn.cursor() as cur:
            cur.execute("""
                SELECT youtube_video_id 
                FROM youtube_video_metadata 
                WHERE customer_id = %s 
                AND youtube_video_id IS NOT NULL
            """, (user_email,))
            videos = cur.fetchall()
            
            # Delete each video from YouTube
            for video in videos:
                try:
                    youtube_id = video[0]
                    youtube.service.videos().delete(id=youtube_id).execute()
                    logger.info(f"Deleted YouTube video {youtube_id} for user {user_email}")
                except Exception as e:
                    logger.error(f"Error deleting YouTube video {youtube_id}: {e}")
            
            # Delete all YouTube records from database
            cur.execute("""
                DELETE FROM youtube_video_metadata WHERE customer_id = %s;
                DELETE FROM customer_youtube_channels WHERE customer_id = %s;
            """, (user_email, user_email))
            db_conn.commit()
            logger.info(f"Deleted all YouTube records for user {user_email}")
            
    except Exception as e:
        logger.error(f"Error cleaning up YouTube data for user {user_email}: {e}")

def cleanup_drive_data(user_email: str, db_conn) -> None:
    """Delete all Google Drive files and data for a user"""
    try:
        drive = GoogleDriveManager(user_email)
        
        # Get all Drive files for user
        with db_conn.cursor() as cur:
            cur.execute("""
                SELECT file_id 
                FROM google_drive_files 
                WHERE customer_id = %s
            """, (user_email,))
            files = cur.fetchall()
            
            # Delete each file from Drive
            for file in files:
                try:
                    file_id = file[0]
                    drive.service.files().delete(fileId=file_id).execute()
                    logger.info(f"Deleted Drive file {file_id} for user {user_email}")
                except Exception as e:
                    logger.error(f"Error deleting Drive file {file_id}: {e}")
            
            # Delete all Drive records from database
            cur.execute("""
                DELETE FROM google_drive_files WHERE customer_id = %s;
                DELETE FROM customer_drive_folders WHERE customer_id = %s;
            """, (user_email, user_email))
            db_conn.commit()
            logger.info(f"Deleted all Drive records for user {user_email}")
            
    except Exception as e:
        logger.error(f"Error cleaning up Drive data for user {user_email}: {e}")

def cleanup_local_files(user_email: str) -> None:
    """Delete all local files for a user"""
    try:
        # Delete temp video files
        temp_dir = "/tmp"
        for filename in os.listdir(temp_dir):
            if filename.startswith(f"{user_email}_"):
                file_path = os.path.join(temp_dir, filename)
                try:
                    os.remove(file_path)
                    logger.info(f"Deleted local file {file_path}")
                except Exception as e:
                    logger.error(f"Error deleting local file {file_path}: {e}")
    except Exception as e:
        logger.error(f"Error cleaning up local files for user {user_email}: {e}")

def process_cleanup(user_email: Optional[str] = None) -> None:
    """Process cleanup for all users or a specific user"""
    try:
        logger.info("Starting cleanup process...")
        if user_email:
            logger.info(f"Cleaning up data for user: {user_email}")
        else:
            logger.info("Cleaning up data for all users")
            
        db = PodcastDB()
        with db.get_connection() as conn:
            # Get users to cleanup
            users = get_users_to_cleanup(conn, user_email)
            if not users:
                logger.info("No users found to cleanup")
                return
                
            for email in users:
                logger.info(f"Processing cleanup for user {email}")
                
                # Cleanup YouTube data
                cleanup_youtube_data(email, conn)
                
                # Cleanup Drive data
                cleanup_drive_data(email, conn)
                
                # Cleanup local files
                cleanup_local_files(email)
                
                logger.info(f"Completed cleanup for user {email}")
            
            logger.info("Cleanup process completed")
            
    except Exception as e:
        logger.error(f"Error during cleanup process: {e}")

if __name__ == "__main__":
    # This will run cleanup for all users when run directly
    process_cleanup()
