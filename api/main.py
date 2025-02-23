from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from video_creator.db_utils import VideoDB
import os
import json
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path
import traceback

from celery_app.tasks import generate_audio_task, create_video_task
from .logger import api_logger
from .models import PodcastJob
from .db import get_db, engine, Base
from config import get_error_detail, format_error_message, OUTPUTS_DIR
from profile_utils import ProfileUtils

# Get package root directory
PACKAGE_ROOT = str(Path(__file__).parent.parent)

# Create outputs directory
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount outputs directory for serving generated videos
app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")

# Initialize VideoDB instance
video_db = VideoDB()

# Initialize profile utils
profile_utils = ProfileUtils()

# Pydantic models for request validation
class PodcastRequest(BaseModel):
    profile_name: str = "indapoint" 
    conversation_type: str = "podcast"
    customer_id : str = "indapoint"
    topic: Optional[str] = "AI and Business Where do we go from here?"
    title: Optional[str] = "AI and Business"
    sub_title: Optional[str] = "AI and Business Dynamics"
    theme: Optional[str] = "dark"
    video_type: Optional[str] = "podcast"
    main_video_style: Optional[str] = "video"

class PodcastResponse(BaseModel):
    job_id: int
    status: str
    error: Optional[str] = None
    output_path: Optional[str] = None

def load_profile(profile_name: str, theme: str = "dark") -> tuple[dict, dict]:
    """Load profile configuration and business info using ProfileUtils"""
    try:
        # Get complete profile config
        config = profile_utils.get_profile_config(profile_name, theme)
        business_info = profile_utils.get_business_info(profile_name)
  
        return config, business_info
    except Exception as e:
        error_detail = get_error_detail(e, context="loading profile")
        error_msg = format_error_message(error_detail)
        raise HTTPException(status_code=400, detail=error_detail)

# Add custom exception handler for all exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    error_detail = get_error_detail(exc)
    error_msg = format_error_message(error_detail)
    api_logger.error(error_msg)
    return JSONResponse(
        status_code=500,
        content=error_detail
    )

@app.post("/api/podcasts", response_model=PodcastResponse)
async def create_podcast(request: PodcastRequest, db: Session = Depends(get_db)):
    """Start podcast generation process"""
    try:
        api_logger.info(f"Received podcast creation request: {request.dict()}")
        
        # Create new job record
        job = PodcastJob(
            profile_name=request.profile_name,
            conversation_type=request.conversation_type,
            topic=request.topic,
            customer_id=request.customer_id,
            status="processing"
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Initialize video_paths record for this job
        video_paths_id = video_db.add_video_paths(
            job_id=job.id,
            paths={},  # Empty paths to start
            video_config={},  # Initial config
            theme=request.theme,
            profile=request.profile_name
        )
        api_logger.info(f"Created video_paths record with ID: {video_paths_id}")
        
        # Load profile configuration
        config, _ = load_profile(request.profile_name, request.theme)
        
        #let us create dict of all request vars and use that 
        request_dict = request.dict()
        
        try:
            # Update video paths configuration using VideoDB
            video_db.update_video_config(job_id=job.id, config=config)
            api_logger.info(f"Updated video config for job {job.id}")

            video_db.update_video_theme(job_id=job.id, theme=request.theme)
            api_logger.info(f"Updated video theme for job {job.id}")

            video_db.update_video_profile(job_id=job.id, profile=request.profile_name)
            api_logger.info(f"Updated video profile for job {job.id}")

        except Exception as e:
            api_logger.error(f"Error updating video configuration: {str(e)}")
            # Continue even if video config update fails
            pass

        if os.getenv('CELERY_PROCESS') == 'true':
            audio_task = generate_audio_task.delay(
                config=config,
                business_info={},
                job_id=str(job.id),
                request_dict=request_dict
            )
            # Update job with task ID only in Celery mode
            job.audio_task_id = audio_task.id
        else:
            # In non-Celery mode, just get the audio path
            audio_path = generate_audio_task(
                config=config,
                business_info={},
                job_id=str(job.id),
                request_dict=request_dict
            )
            # Store the audio path
            job.audio_path = audio_path
        
        db.commit()
        
        return PodcastResponse(
            job_id=job.id,
            status=job.status,
            error=job.error_message,
            output_path=job.output_path
        )
            
    except Exception as e:
        error_detail = get_error_detail(e, context="creating podcast")
        error_msg = format_error_message(error_detail)
        api_logger.error(error_msg)
        job.status = "failed"
        job.error_message = error_msg
        db.commit()
        raise HTTPException(status_code=500, detail=error_detail)
            
@app.get("/api/podcasts/{job_id}", response_model=PodcastResponse)
async def get_podcast_status(job_id: int, db: Session = Depends(get_db)):
    """Get status of a podcast generation job"""
    job = db.query(PodcastJob).filter(PodcastJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return PodcastResponse(
        job_id=job.id,
        status=job.status,
        error=job.error_message if job.status == "failed" else None,
        output_path=job.output_path if job.status == "completed" else None
    )

@app.get("/api/podcasts")
async def list_podcasts(db: Session = Depends(get_db)):
    """List all podcast jobs"""
    jobs = db.query(PodcastJob).order_by(PodcastJob.created_at.desc()).all()
    return [job.to_dict() for job in jobs]
