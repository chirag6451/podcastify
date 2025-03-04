#!/usr/bin/env python3
import os
import sys
import logging
import psycopg2
from collections import namedtuple
from datetime import datetime
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image_utils import create_youtube_thumbnail
from utils.open_ai_utils import create_youtube_seo_title_and_description
from config import get_business_details
from create_audio.db_utils import PodcastDB
from video_creator.db_utils import VideoDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Define a named tuple for video metadata
VideoMetadata = namedtuple('VideoMetadata', [
    'job_id',
    'final_video_path',
    'topic',
    'customer_id',
    'email',
    'channel_id',
    'thumbnail_dir',
    'welcome_voiceover_text',
    'conversation_json'
])

def add_new_videos_to_metadata():
    """Add new videos to YouTube metadata"""
    try:
        logger.info("Looking for new videos to add to YouTube metadata...")
        db = PodcastDB()

        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Get jobs that have a final video path but no metadata
                cur.execute("""
                    SELECT 
                        j.id as job_id,
                        j.topic,
                        j.customer_id,
                        cyc.id as channel_id,
                        vp.welcome_voiceover_text,
                        vp.conversation_json as conversation_data,
                        vp.final_video_path
                    FROM podcast_jobs j
                    JOIN video_paths vp ON vp.job_id = j.id
                    JOIN google_auth ga ON ga.email = j.customer_id
                    JOIN customer_youtube_channels cyc ON cyc.customer_id = j.customer_id
                    LEFT JOIN youtube_video_metadata yvm ON yvm.job_id = j.id
                    WHERE vp.final_video_path IS NOT NULL
                    AND yvm.id IS NULL
                """)
                
                new_videos = cur.fetchall()
                logger.info(f"Found {len(new_videos)} new videos to process")

                for video in new_videos:
                    job_id, topic, customer_id, channel_id, welcome_text, conversation_data, final_video_path = video
                    
                    try:
                        # Generate SEO title and description
                        seo_result = create_youtube_seo_title_and_description(
                            topic=topic,
                            context=welcome_text,
                            business_details={"welcome_text": welcome_text, "conversation": conversation_data}
                        )
                        
                        if seo_result is None:
                            logger.error(f"Failed to generate SEO metadata for job {job_id}")
                            title = topic
                            description = welcome_text
                            subtitle = welcome_text
                            thumbnail_title = title
                            thumbnail_subtitle = title
                            thumbnail_footer = title
                            
                        title, description, subtitle, thumbnail_title, thumbnail_subtitle, thumbnail_footer = seo_result
                        
                        # Add logging to check values
                        logger.info(f"Generated SEO metadata for job {job_id}:")
                        logger.info(f"Title: {title}")
                        logger.info(f"Description length: {len(description) if description else 0}")
                        logger.info(f"Subtitle: {subtitle}")
                        logger.info(f"Thumbnail title: {thumbnail_title}")
                        
                        # Create thumbnail
                        thumbnail_path = process_youtube_thumbnails(
                            job_id=job_id,
                            thumbnail_title=thumbnail_title,
                            thumbnail_subtitle=thumbnail_subtitle,
                            thumbnail_footer=thumbnail_footer
                        )
                        video_db = VideoDB()
                        selected_thumbnail_path = video_db.select_random_thumbnail(job_id=job_id)
                        if selected_thumbnail_path:
                            logger.info(f"Selected thumbnail: {selected_thumbnail_path}")
                        else:
                            logger.info("No valid thumbnails found")
                        
                        # Insert into youtube_video_metadata
                        cur.execute("""
                            INSERT INTO youtube_video_metadata 
                            (job_id, customer_id, channel_id, title, description, seo_title, seo_description,
                            video_file_path, thumbnail_path, privacy_status, publish_status, 
                            thumbnail_title, thumbnail_subtitle, selected_thumbnail_path)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'private', 'draft', %s, %s, %s)
                        """, (
                            job_id,
                            customer_id,
                            channel_id,
                            title,
                            description,
                            title,  # Use the SEO title as seo_title
                            description,  # Use the SEO description as seo_description
                            final_video_path,
                            thumbnail_path,
                            thumbnail_title,
                            thumbnail_subtitle,
                            selected_thumbnail_path
                        ))
                        conn.commit()
                        
                        logger.info(f"Added metadata for job {job_id}")
                        
                    except Exception as e:
                        logger.error(f"Error processing job {job_id}: {str(e)}")
                        conn.rollback()
                        continue

    except Exception as e:
        logger.error(f"Error adding videos to metadata: {str(e)}")
        raise e

def process_youtube_thumbnails(job_id: int,
         thumbnail_title:str,
         thumbnail_subtitle:str,
         thumbnail_footer:str
         )           :
    """Process YouTube thumbnails for a job"""
    video_db = VideoDB()
    
    try:
        # Get existing thumbnail paths
        existing_thumbnails = video_db.get_thumbnail_paths(job_id)
        
        # Create new YouTube thumbnail
     
        thumbnail_path = create_youtube_thumbnail(
            title=thumbnail_title,
            subtitle=thumbnail_subtitle,
            footer_text=thumbnail_footer
        )
        
        if thumbnail_path:
            # Combine existing thumbnails with new one
            all_thumbnails = existing_thumbnails + [thumbnail_path]
            
            # Update database with all thumbnail paths
            video_db.update_thumbnail_paths(job_id, all_thumbnails)
            
            logger.info(f"Added YouTube thumbnail to existing thumbnails for job {job_id}")
            return all_thumbnails
            
    except Exception as e:
        logger.error(f"Error processing YouTube thumbnails for job {job_id}: {str(e)}")
        return existing_thumbnails  # Return existing thumbnails if there's an error

if __name__ == "__main__":
    add_new_videos_to_metadata()
