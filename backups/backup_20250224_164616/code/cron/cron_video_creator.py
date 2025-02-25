#!/usr/bin/env python3
import os
import sys
import logging
import datetime
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.absolute())
sys.path.append(project_root)

from video_creator.utils.video_utils import create_final_video_from_paths
from video_creator.db_utils import VideoDB
from video_creator.podcast_video_creator import PodcastVideoCreator
from utils.file_writer import get_output_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('video_creator.log')
    ]
)
logger = logging.getLogger(__name__)

def process_pending_videos():
    """
    Process all pending videos that meet the criteria:
    - Status is pending OR
    - Final video path is blank
    - Status is not error
    - Retry count is less than 5
    """
    video_db = VideoDB()
    creator = PodcastVideoCreator()
    
    try:
        # Get all pending videos
        pending_videos = video_db.get_pending_videos(max_retries=5)
        logger.info(f"Found {len(pending_videos)} pending videos to process")
        
        for video in pending_videos:
            job_id = video['job_id']
            logger.info(f"Processing video for job {job_id}")
            
            try:
                # Update status to processing
                video_db.update_video_status(job_id=job_id, status="processing")
                
                # Get video paths and config from the database
                video_paths = video_db.get_video_paths(job_id)
                
                # Check if this is a HeyGen video
                if video.get('is_heygen_video'):
                    logger.info(f"Job {job_id} is a HeyGen video")
                    # If HeyGen video path is empty, check HeyGen status
                    if video.get('hygen_short_video'):
                        heygen_status = video_db.get_heygen_video_status_and_paths(job_id)
                      
                        if heygen_status:
                            if heygen_status['status'] == 'error':
                                # If HeyGen video failed, mark video as failed
                                error_msg = f"HeyGen video generation failed for job {job_id}"
                                logger.error(error_msg)
                                video_db.update_video_status(
                                    job_id=job_id,
                                    status="failed",
                                    error_details=error_msg
                                )
                                continue
                            elif heygen_status['video_path']:
                                # If HeyGen video exists, use it as short video path
                                video_paths['short_video_path'] = heygen_status['video_path']
                                logger.info(f"Using HeyGen video path: {heygen_status['video_path']}")
                    else:
                        # If HeyGen video does not exist, mark video as failed
                        #we wait for hygen video not completed we skip this record , we do not need to take any acditon here or update any record
                        logger.error(f"HeyGen video is not completed for job {job_id}")
                        continue
                
                # Check if we have any valid paths
                valid_paths = [path for path in video_paths.values() if path and os.path.exists(path)]
                if not valid_paths:
                    raise ValueError(f"No valid video paths found for job {job_id}")
                
                # Get video config from the video_paths record
                video_config = video.get('video_config', {})
                if not video_config:
                    video_config = {}
                
                # Set final video filename
                final_video_output_filename = f'final_video_{job_id}.mp4'
                video_config['final_video_output_filename'] = final_video_output_filename
                
                #let us get output file path from get_output_path
                final_video_path, _ = get_output_path(
                    filename=final_video_output_filename,
                    profile_name=video.get('profile'),
                    customer_id=video.get('customer_id'),
                    job_id=job_id,
                    theme=video.get('theme', 'default')
                )
                # Create final video using create_final_video_from_paths directly
                final_video_path = create_final_video_from_paths(
                    video_paths=video_paths,
                    config=video_config,
                    job_id=job_id,
                    customer_id=video.get('customer_id'),
                    theme=video.get('theme', 'default'),
                    profile=video.get('profile')
                )
                
                # Update status to completed with final path
                video_db.update_video_status(
                    job_id=job_id,
                    status="completed",
                    final_video_path=final_video_path
                )
                logger.info(f"Successfully created video for job {job_id}")
                
            except Exception as e:
                error_msg = f"Failed to create video: {str(e)}"
                logger.error(error_msg)
                
                # Update status to failed with error details
                video_db.update_video_status(
                    job_id=job_id,
                    status="failed",
                    error_details=error_msg
                )
                
    except Exception as e:
        logger.error(f"Error in video processing cron: {str(e)}")

def main():
    """Main entry point for the video creator cron job"""
    logger.info("Starting video creator cron job")
    process_pending_videos()
    logger.info("Finished video creator cron job")

if __name__ == "__main__":
    main()
