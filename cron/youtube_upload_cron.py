#!/usr/bin/env python3
import logging
import os
import sys
from typing import List, Optional, Tuple

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

def process_pending_youtube_uploads() -> None:
    """Process all pending YouTube uploads that have been approved"""
    try:
        logger.info("Starting YouTube upload process...")
        db = PodcastDB()
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Get all users with Google credentials
                cur.execute("""
                    SELECT DISTINCT email 
                    FROM google_auth 
                    WHERE refresh_token IS NOT NULL
                """)
                users = cur.fetchall()
                logger.info(f"Found {len(users)} users with Google credentials")

                # Process each user's uploads
                for user in users:
                    user_email = user[0]
                    logger.info(f"Processing videos for user: {user_email}")

                    try:
                        # Get all approved videos for this user that haven't been uploaded
                        cur.execute("""
                            SELECT 
                                m.id,
                                m.customer_id,
                                CASE 
                                    WHEN j.youtube_channel_id IS NOT NULL AND j.youtube_channel_id != '' THEN j.youtube_channel_id
                                    ELSE (SELECT channel_id FROM customer_youtube_channels WHERE id = m.channel_id)
                                END as channel_id,
                                COALESCE(m.seo_title, m.title) as title,
                                COALESCE(m.seo_description, m.description) as description,
                                m.privacy_status,
                                m.video_file_path,
                                m.selected_thumbnail_path,
                                j.youtube_playlist_id,
                                j.id as job_id
                            FROM youtube_video_metadata m
                            LEFT JOIN podcast_jobs j ON m.job_id = j.id
                            LEFT JOIN customer_youtube_channels c ON m.channel_id = c.id
                            WHERE m.publish_status = 'approved'
                            AND m.youtube_video_id IS NULL
                            AND m.customer_id = %s
                        """, (user_email,))
                        uploads = cur.fetchall()
                        logger.info(f"Found {len(uploads)} pending uploads for user {user_email}")

                        # Process each video for this user
                        youtube = YouTubeManager(user_email)  # Create YouTubeManager once per user
                        for upload in uploads:
                            try:
                                logger.info(f"Processing upload with ID {upload[0]}")
                                logger.info(f"Title: '{upload[3]}'")  # Log the title
                                logger.info(f"Description length: {len(upload[4]) if upload[4] else 0}")
                                logger.info(f"Using channel ID: {upload[2]}")  # Log channel ID
                                
                                # Clean and validate title
                                title = upload[3].strip() if upload[3] else ""
                                if not title:
                                    # If title is empty, try to get it from database
                                    db = PodcastDB()
                                    with db.get_connection() as conn:
                                        with conn.cursor() as cur:
                                            cur.execute("""
                                                SELECT title 
                                                FROM youtube_video_metadata 
                                                WHERE id = %s
                                            """, (upload[0],))
                                            result = cur.fetchone()
                                            if result and result[0]:
                                                title = result[0].strip()
                                
                                if not title:
                                    raise ValueError(f"No valid title found for video {upload[0]}")
                                
                                logger.info(f"Using title: '{title}'")
                                
                                # Ensure playlist_id is None if empty or whitespace
                                playlist_id = upload[8] if upload[8] and upload[8].strip() else None
                                if playlist_id:
                                    logger.info(f"Will add to playlist: {playlist_id}")
                                else:
                                    logger.info("No playlist specified, skipping playlist addition")
                                
                                result = youtube.upload_video(
                                    video_path=upload[6],  # video_file_path
                                    channel_id=str(upload[2]),  # channel_id from podcast_jobs or metadata
                                    playlist_id=playlist_id,  # playlist_id from podcast_jobs
                                    title=title,  # cleaned title
                                    description=upload[4],  # description from metadata
                                    privacy_status='public',  # Set to public by default
                                    upload_id=upload[0]  # metadata id
                                )
                                if isinstance(result, dict):
                                    logger.info(f"Successfully uploaded video {upload[0]} to YouTube with ID {result.get('youtube_id')}")
                                    logger.info(f"Video {upload[0]} details:")
                                    logger.info(f"  YouTube ID: {result.get('youtube_id')}")
                                    logger.info(f"  URL: {result.get('url')}")
                                    
                                    # Update database with thumbnail URLs
                                    video_info = youtube.service.videos().list(
                                        part="snippet",
                                        id=result.get('youtube_id')
                                    ).execute()
                                    
                                    if video_info.get('items'):
                                        thumbnails = video_info['items'][0]['snippet'].get('thumbnails', {})
                                        cur.execute("""
                                            UPDATE youtube_video_metadata
                                            SET thumbnail_url_default = %s,
                                                thumbnail_url_medium = %s,
                                                thumbnail_url_high = %s
                                            WHERE id = %s
                                        """, (
                                            thumbnails.get('default', {}).get('url'),
                                            thumbnails.get('medium', {}).get('url'),
                                            thumbnails.get('high', {}).get('url'),
                                            upload[0]
                                        ))
                                        conn.commit()
                                        logger.info(f"  Thumbnails:")
                                        logger.info(f"    Default: {thumbnails.get('default', {}).get('url')}")
                                        logger.info(f"    Medium: {thumbnails.get('medium', {}).get('url')}")
                                        logger.info(f"    High: {thumbnails.get('high', {}).get('url')}")
                                        logger.info(f"Updated metadata for video {upload[0]} with URLs and thumbnails")

                            except Exception as e:
                                logger.error(f"Error uploading video {upload[0]}: {e}")

                    except Exception as e:
                        logger.error(f"Error processing videos for user {user_email}: {e}")

    except Exception as e:
        logger.error(f"Error in process_pending_youtube_uploads: {e}")

if __name__ == "__main__":
    process_pending_youtube_uploads()
