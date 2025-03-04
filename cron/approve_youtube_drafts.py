#!/usr/bin/env python3
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from create_audio.db_utils import PodcastDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def approve_draft_videos() -> None:
    """Approve all videos in draft status for YouTube upload."""
    try:
        logger.info("Looking for draft videos to approve...")
        db = PodcastDB()
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Get count of draft videos
                cur.execute("""
                    SELECT COUNT(*)
                    FROM youtube_video_metadata
                    WHERE publish_status = 'draft'
                """)
                draft_count = cur.fetchone()[0]
                logger.info(f"Found {draft_count} videos in draft status")

                if draft_count > 0:
                    # Update all draft videos to approved status
                    cur.execute("""
                        UPDATE youtube_video_metadata
                        SET publish_status = 'approved'::youtube_publish_status
                        WHERE publish_status = 'draft'::youtube_publish_status
                        RETURNING id, title
                    """)
                    approved_videos = cur.fetchall()
                    conn.commit()
                    
                    # Log the approved videos
                    logger.info(f"Successfully approved {len(approved_videos)} videos:")
                    for video_id, title in approved_videos:
                        logger.info(f"  - Video ID {video_id}: {title}")
                else:
                    logger.info("No draft videos found to approve")

    except Exception as e:
        logger.error(f"Error approving draft videos: {str(e)}")
        raise e

if __name__ == "__main__":
    approve_draft_videos()
