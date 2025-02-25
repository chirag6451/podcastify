#!/usr/bin/env python3
import logging
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from create_audio.db_utils import PodcastDB
from publish.youtube_manager import YouTubeManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def process_pending_youtube_uploads():
    """Process all pending YouTube uploads that have been approved"""
    try:
        logger.info("Starting to process pending YouTube uploads...")
        db = PodcastDB()
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Get all approved videos pending upload
                cur.execute("""
                    SELECT 
                        m.id,
                        m.customer_id,
                        c.channel_id as youtube_channel_id,
                        m.title,
                        m.description,
                        m.privacy_status,
                        COALESCE(m.video_file_path, v.main_video_path) as video_path,
                        m.playlist_id
                    FROM youtube_video_metadata m
                    LEFT JOIN video_paths v ON v.id = m.video_path_id
                    JOIN customer_youtube_channels c ON c.id = m.channel_id
                    WHERE m.approval_status = 'approved'
                    AND m.publish_status IN ('draft', 'failed')
                    LIMIT 10  -- Process in batches
                """)
                pending_uploads = cur.fetchall()
                logger.info(f"Found {len(pending_uploads)} pending uploads to process")
                
                for upload in pending_uploads:
                    try:
                        logger.info(f"Processing upload ID {upload[0]} for customer {upload[1]}")
                        # Initialize YouTube manager for this user
                        youtube = YouTubeManager(upload[1])  # customer_id
                        
                        # Upload video
                        result = youtube.upload_video(
                            video_path=upload[6],  # video_path
                            channel_id=upload[2],  # youtube_channel_id
                            playlist_id=upload[7],  # playlist_id
                            title=upload[3],  # title
                            description=upload[4],  # description
                            privacy_status=upload[5],  # privacy_status
                            upload_id=upload[0]  # metadata id for updating status
                        )
                        # Update successful upload in database
                        video_id = result.get('youtube_id')
                        if not video_id:
                            raise Exception("No video ID returned from YouTube")
                            
                        video_url = result.get('url')
                        if not video_url:
                            video_url = f"https://youtube.com/watch?v={video_id}"
                        
                        # Extract thumbnail URLs if available
                        thumbnail_default = None
                        thumbnail_medium = None
                        thumbnail_high = None
                        
                        # Get video details from YouTube
                        youtube_response = youtube.service.videos().list(
                            part="snippet",
                            id=video_id
                        ).execute()
                        
                        if 'items' in youtube_response and youtube_response['items']:
                            video_details = youtube_response['items'][0]
                            if 'snippet' in video_details and 'thumbnails' in video_details['snippet']:
                                thumbnails = video_details['snippet']['thumbnails']
                                if 'default' in thumbnails:
                                    thumbnail_default = thumbnails['default']['url']
                                if 'medium' in thumbnails:
                                    thumbnail_medium = thumbnails['medium']['url']
                                if 'high' in thumbnails:
                                    thumbnail_high = thumbnails['high']['url']
                        
                        cur.execute("""
                            UPDATE youtube_video_metadata
                            SET youtube_video_id = %s,
                                publish_status = 'published'::youtube_publish_status,
                                published_at = CURRENT_TIMESTAMP,
                                updated_at = CURRENT_TIMESTAMP,
                                video_url = %s,
                                thumbnail_url_default = %s,
                                thumbnail_url_medium = %s,
                                thumbnail_url_high = %s,
                                error_message = NULL
                            WHERE id = %s
                        """, (
                            video_id,
                            video_url,
                            thumbnail_default,
                            thumbnail_medium,
                            thumbnail_high,
                            upload[0]
                        ))
                        conn.commit()
                        logger.info(f"Successfully uploaded video ID {video_id} for customer {upload[1]}")
                        logger.info(f"Video URL: {video_url}")
                        if thumbnail_high:
                            logger.info(f"Thumbnail URLs:")
                            logger.info(f"  Default: {thumbnail_default}")
                            logger.info(f"  Medium:  {thumbnail_medium}")
                            logger.info(f"  High:    {thumbnail_high}")
                    except Exception as e:
                        logger.error(f"Error uploading video {upload[0]}: {str(e)}")
                        # Update error status in database
                        cur.execute("""
                            UPDATE youtube_video_metadata
                            SET publish_status = 'failed'::youtube_publish_status,
                                error_message = %s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = %s
                        """, (str(e), upload[0]))
                        conn.commit()
                        
    except Exception as e:
        logger.error(f"Error processing YouTube uploads: {e}")
        raise

if __name__ == "__main__":
    process_pending_youtube_uploads()
