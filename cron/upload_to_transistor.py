#!/usr/bin/env python3
import logging
import sys
import os
import json
import re
from typing import Optional
import re
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get show ID from API
from utils.transistor_fm_api import TransistorFMClient
client = TransistorFMClient()
shows = client.get_shows()
if not shows or 'data' not in shows or not shows['data']:
    raise ValueError("No shows found in Transistor account")

# Use first show's ID
SHOW_ID = shows['data'][0]['id']
logger.info(f"Using show ID: {SHOW_ID} ({shows['data'][0]['attributes']['title']})")

from create_audio.db_utils import PodcastDB
from utils.transistor_fm_api import TransistorFMClient

def get_youtube_url(job_id: int, db_cursor) -> Optional[str]:
    """Get YouTube URL for a job if available"""
    db_cursor.execute("""
        SELECT 'https://www.youtube.com/watch?v=' || youtube_video_id as url
        FROM youtube_video_metadata
        WHERE job_id = %s AND youtube_video_id IS NOT NULL
    """, (job_id,))
    result = db_cursor.fetchone()
    return result[0] if result else None

def upload_podcast_to_transistor() -> None:
    """Upload completed podcasts to Transistor.fm"""
    try:
        logger.info("Looking for new podcasts to upload to Transistor.fm...")
        db = PodcastDB()
        client = TransistorFMClient()

        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Get podcasts from podcast_audio_details that haven't been uploaded
                cur.execute("""
                    SELECT 
                        pad.job_id::integer,
                        COALESCE(yvm.seo_title, j.topic) as title,
                        COALESCE(yvm.seo_description, pad.welcome_voiceover_text) as description,
                        pad.final_podcast_audio_path,
                        j.customer_id
                    FROM podcast_audio_details pad
                    JOIN podcast_jobs j ON j.id = pad.job_id::integer
                    LEFT JOIN podcast_uploads pu ON pu.job_id = pad.job_id::integer
                    LEFT JOIN youtube_video_metadata yvm ON yvm.job_id = pad.job_id::integer
                    WHERE pad.final_podcast_audio_path IS NOT NULL
                    AND pu.id IS NULL
                    AND pad.approval_status = 'approved'
                """)
                
                new_podcasts = cur.fetchall()
                logger.info(f"Found {len(new_podcasts)} new podcasts to upload")

                for podcast in new_podcasts:
                    job_id, title, description, audio_path, customer_id = podcast
                    
                    try:
                        # First create entry in podcast_uploads
                        cur.execute("""
                            INSERT INTO podcast_uploads
                            (episode_title, audio_file_path, episode_description, 
                             show_id, customer_id, job_id)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            RETURNING id
                        """, (
                            title,
                            audio_path,
                            description,
                            SHOW_ID,
                            customer_id,
                            job_id
                        ))
                        podcast_upload_id = cur.fetchone()[0]
                        conn.commit()
                        
                        # Create episode summary
                        summary = description
                        
                        # Get video URL if available
                        video_url = get_youtube_url(job_id, cur)
                        
                        # Get thumbnail URL
                        cur.execute("""
                            SELECT selected_thumbnail_path
                            FROM youtube_video_metadata
                            WHERE job_id = %s
                        """, (job_id,))
                        thumbnail_result = cur.fetchone()
                        thumbnail_url = thumbnail_result[0] if thumbnail_result else None

                        # Upload to Transistor
                        episode = client.create_episode(
                            show_id=SHOW_ID,
                            seo_title=title,
                            seo_description=description,
                            video_url=video_url,
                            thumbnail_url_medium=thumbnail_url,
                            season=None,  # Optional: Add if needed
                            number=None   # Optional: Add if needed
                        )
                        
                        if not episode:
                            logger.error(f"Failed to create episode for job {job_id}")
                            continue
                            
                        episode_id = episode['id']
                        
                        # Get upload authorization
                        filename = os.path.basename(audio_path)
                        auth = client.authorize_upload(filename)
                        
                        if not auth:
                            logger.error(f"Failed to get upload authorization for job {job_id}")
                            continue
                            
                        # Upload the audio file
                        if client.upload_audio(auth['upload_url'], audio_path):
                            # Update episode with the audio URL
                            updated = client.update_episode_audio(episode_id, auth['audio_url'])
                            
                            if updated:
                                # Record the upload in transistor_fm_episodes
                                cur.execute("""
                                    INSERT INTO transistor_fm_episodes
                                    (podcast_upload_id, transistor_episode_id, status,
                                     media_url, share_url, embed_html, embed_html_dark,
                                     response_data, job_id, customer_id)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """, (
                                    podcast_upload_id,
                                    episode_id,
                                    updated['attributes'].get('status'),
                                    updated['attributes'].get('media_url'),
                                    updated['attributes'].get('share_url'),
                                    updated['attributes'].get('embed_html'),
                                    updated['attributes'].get('embed_html_dark'),
                                    json.dumps(updated),
                                    job_id,
                                    customer_id
                                ))
                                conn.commit()
                                
                                logger.info(f"Successfully uploaded podcast {job_id} to Transistor.fm")
                                logger.info(f"Episode URL: {updated['attributes'].get('share_url')}")
                        else:
                            logger.error(f"Failed to upload audio for job {job_id}")
                            
                    except Exception as e:
                        logger.error(f"Error processing job {job_id}: {str(e)}")
                        conn.rollback()
                        continue

    except Exception as e:
        logger.error(f"Error uploading podcasts to Transistor.fm: {str(e)}")
        raise e

if __name__ == "__main__":
    upload_podcast_to_transistor()
