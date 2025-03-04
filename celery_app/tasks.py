from typing import Dict, Any, Tuple, List
import os
from pathlib import Path
from celery import Celery
from sqlalchemy.orm import Session
import json
from api.db import get_db, engine
from api.models import PodcastJob
from api.logger import PodcastLogger
from create_audio.conversation_generator import generate_conversation
from utils.file_writer import get_output_path
from video_creator import create_podcast_video
from utils.logger_utils import PodcastLogger
from config import get_error_detail, format_error_message
import config as config_settings
from .celery_logging import setup_celery_logging, TaskLogger

# Initialize Celery
celery = Celery('tasks')
celery.conf.broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
celery.conf.result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
from video_creator.db_utils import VideoDB  # Import VideoDB directly from db_utils
video_db = VideoDB()

# Setup celery logging
logger = setup_celery_logging()

def get_error_detail(error: Exception, job_id: str, task_type: str, include_traceback: bool = False, context: str = "") -> tuple[str, dict]:
    """Get error details based on debug mode"""
    error_info = {"error": str(error)}
    error_msg = f"Error in {task_type} for job {job_id}: {str(error)}"
    
    if include_traceback:
        tb = traceback.extract_tb(error.__traceback__)[-1]  # Get the last frame
        error_info.update({
            "file": os.path.basename(tb.filename),
            "line": tb.lineno,
            "function": tb.name,
            "code": tb.line
        })
        error_msg = f"Error in {error_info['file']}:{error_info['line']} - {error_msg}"
    
    if context:
        error_msg = f"{context}: {error_msg}"
    
    return error_msg, error_info

@celery.task(bind=True)
def generate_audio_task(self,request_dict: dict, config: dict, business_info: dict, job_id: str):
    """Generate audio for podcast"""
    debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    task_logger = TaskLogger(job_id)
    try:
        # Get database session
        db = Session(engine)
        
        # Get job from database
        job = db.query(PodcastJob).filter(PodcastJob.id == int(job_id)).first()
        if not job:
            raise Exception(f"Job {job_id} not found")
        
        task_logger.info(f"Starting audio generation for job {job_id}")
        
        audio_path, schema_path, welcome_audio_path,welcome_voiceover = generate_conversation(
            job_id=job_id,
            config=config,
            request_dict=request_dict
        )
       
        # audio_path=config_settings.STATIC_AUDIO_PATH
        # schema_path = config_settings.STATIC_SCHEMA_PATH
        # welcome_audio_path = config_settings.STATIC_WELCOME_PATH
        # welcome_voiceover="Welcome to the IndaPoint Podcast"
        
        #let us insert the audio path and welcome audio path to the job
        video_db.add_specific_path(job_id=int(job_id), path_type='welcome_audio_path', path_value=welcome_audio_path)
        video_db.add_specific_path(job_id=int(job_id), path_type='audio_path', path_value=audio_path)
     
        config['welcome_voiceover'] = welcome_voiceover
        config['context'] = schema_path
        config['topic'] = request_dict.get('topic')
        # Update job with video task info
        job.status = "processing_video"
        db.commit()
        
        # Start video generation
        config['intro_audio_path'] = welcome_audio_path  # Add welcome_audio_path to config
        if os.getenv('CELERY_PROCESS') == 'true':
            video_task = create_video_task.delay(
                audio_path=audio_path,
                config=config,
                job_id=job_id,
                request_dict=request_dict,
                welcome_audio_path=welcome_audio_path
            )
        else:
            video_task = create_video_task(
                audio_path=audio_path,
                config=config,
                job_id=job_id,
                request_dict=request_dict,
                welcome_audio_path=welcome_audio_path
            )
        
        # Update job with video task ID
        job.video_task_id = video_task.id
        db.commit()
        
        return audio_path
        
    except Exception as e:
        error_detail = get_error_detail(e, job_id=job_id, task_type="audio generation", context=f"audio generation for job {job_id}")
        task_logger.error(f"Error in audio generation: {error_detail}")
        # Update job status
        job.status = "failed"
        job.error_message = str(e)
        db.commit()
        raise Exception(error_detail)
    finally:
        db.close()

@celery.task(bind=True)
def create_video_task(self, audio_path: str, config: dict, job_id: str, request_dict: dict, welcome_audio_path: str):
    """Create video for podcast"""
    debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    task_logger = TaskLogger(job_id)
    try:
        # Get database session
        db = Session(engine)
        
        # Get job from database
        job = db.query(PodcastJob).filter(PodcastJob.id == int(job_id)).first()
        if not job:
            raise Exception(f"Job {job_id} not found")
        
        task_logger.info("Starting video generation")
        # Update task state to show it's started
        self.update_state(state='PROGRESS', meta={'current': 0, 'total': 100, 'status': 'Starting video generation'})
        
        # Create output filename
        output_filename = f"podcast_{job_id}.mp4"
        task_logger.info(f"Creating output path for {output_filename}")
        
        #let us call get output path
        output_path, _ = get_output_path(
            filename=output_filename,
            profile_name=request_dict.get('profile_name'),
            customer_id=request_dict.get('customer_id'),
            job_id=job_id,
            theme=request_dict.get('theme', 'default')
        )
        
        # Update progress before video creation
        self.update_state(state='PROGRESS', meta={'current': 10, 'total': 100, 'status': 'Starting video creation'})
        task_logger.info("Starting video creation process")
        
        # Create video with the provided configuration
        video_path, thumbnail_paths = create_podcast_video(
            audio_path=audio_path,
            welcome_audio_path=welcome_audio_path,
            config=config,
            job_id=job_id,
            request_dict=request_dict,
        )
        
        # Update progress after video creation
        self.update_state(state='PROGRESS', meta={'current': 90, 'total': 100, 'status': 'Video created, saving results'})
        task_logger.info(f"Video created at {video_path}")
        
        thumbnail_db = VideoDB()
        thumbnail_db.add_thumbnail_path_1(job_id=job_id, thumbnail_path=thumbnail_paths)
        task_logger.info(f"Added {len(thumbnail_paths) if thumbnail_paths else 0} thumbnails to database")
        
        # Update job status and output path
        job.status = "completed"
        job.output_path = video_path
        db.commit()
        task_logger.info("Job status updated to completed")
        
        # Final progress update
        self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Video generation completed'})
        task_logger.info("Video generation task completed successfully")
        
        return output_path
        
    except Exception as e:
        error_detail = get_error_detail(e, job_id=job_id, task_type="video generation", context=f"video generation for job {job_id}")
        task_logger.error(f"Error in video generation: {error_detail}")
        # Update job status
        job.status = "failed"
        job.error_message = str(e)
        db.commit()
        raise Exception(error_detail)
    finally:
        db.close()
