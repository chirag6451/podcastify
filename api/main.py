from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from video_creator.db_utils import VideoDB
import os
import json
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path
import traceback
from create_audio.db_utils import PodcastDB

from celery_app.tasks import generate_audio_task, create_video_task
from .logger import api_logger
from .models.podcast_job import PodcastJob
from .db import get_db, engine, Base
from config import get_error_detail, format_error_message, OUTPUTS_DIR
from profile_utils import ProfileUtils
from .google_auth import router as google_auth_router
from publish.routes import router as publish_router
from .routers import user_router, voice_router, style_router, podcast_router
from .security import verify_api_key

# Get package root directory
PACKAGE_ROOT = str(Path(__file__).parent.parent)

# Create outputs directory
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="PodcastAI API",
    description="API for PodcastAI",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
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
    customer_id : str = "ahmedabadi@gmail.com"
    youtube_channel_id:str="UCjsp-HaZASVdOq48PwMDTxg"
    youtube_playlist_id: str="PLv8bszWmOt2PqiWc7y5kcpyUR84Wyy7YU"
    
    topic: Optional[str] = "AI and Business Where do we go from here?"
    title: Optional[str] = "AI and Business"
    sub_title: Optional[str] = "AI and Business Dynamics"
    theme: Optional[str] = "dark"
    voice_settings_num_turns: Optional[int] = 10
    voice_settings_conversation_mood: Optional[str] = "neutral"
    voice_settings_language: Optional[str] = "en"
    voice_settings_voice_accent: Optional[str] = "neutral"
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

app.include_router(google_auth_router, tags=["auth"])
app.include_router(publish_router, tags=["publish"])
app.include_router(user_router, prefix="/api/users", tags=["users"])
app.include_router(voice_router, prefix="/api/voices", tags=["voices"])
app.include_router(style_router, prefix="/api/styles", tags=["styles"])
app.include_router(podcast_router, prefix="/api/podcasts", tags=["podcasts"])

@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation"""
    return RedirectResponse(url="/api/docs")

@app.get("/docs", include_in_schema=False)
async def docs_redirect():
    """Redirect to API documentation"""
    return RedirectResponse(url="/api/docs")

@app.post("/api/podcasts/", response_model=PodcastResponse, tags=["podcasts"])
async def create_podcast(request: PodcastRequest, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """Start podcast generation process"""
    try:
        api_logger.info(f"Received podcast creation request: {request.dict()}")
        
        # Create new job record
        job = PodcastJob(
            profile_name=request.profile_name,
            conversation_type=request.conversation_type,
            topic=request.topic,
            customer_id=request.customer_id,
            youtube_channel_id=request.youtube_channel_id,
            youtube_playlist_id=request.youtube_playlist_id,
            
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
            customer_id=request.customer_id,
            profile=request.profile_name
        )
        api_logger.info(f"Created video_paths record with ID: {video_paths_id}")
        
        # Load profile configuration
        config, _ = load_profile(request.profile_name, request.theme)

        config['voice_settings_num_turns'] = request.voice_settings_num_turns
        config['voice_settings_conversation_mood'] = request.voice_settings_conversation_mood
        config['voice_settings_language'] = request.voice_settings_language
        config['voice_settings_voice_accent'] = request.voice_settings_voice_accent 
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
            
@app.get("/api/podcasts/{job_id}", response_model=PodcastResponse, tags=["podcasts"])
async def get_podcast_status(job_id: int, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
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

@app.get("/api/podcasts/", tags=["podcasts"])
async def list_podcasts(db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """List all podcast jobs"""
    jobs = db.query(PodcastJob).order_by(PodcastJob.created_at.desc()).all()
    return [job.to_dict() for job in jobs]

@app.get("/api/google/auth/list")
def list_google_auth():
    """List all Google authenticated accounts with their status"""
    try:
        db = PodcastDB()
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        email,
                        CASE 
                            WHEN access_token IS NULL OR access_token = '' THEN false
                            WHEN refresh_token IS NULL OR refresh_token = '' THEN false
                            ELSE true
                        END as is_valid,
                        CASE 
                            WHEN access_token IS NULL OR access_token = '' THEN 'No access token'
                            WHEN refresh_token IS NULL OR refresh_token = '' THEN 'No refresh token'
                            WHEN token_expiry IS NULL THEN 'Token expiry not set'
                            WHEN token_expiry < NOW() THEN 'Token expired'
                            ELSE 'Valid'
                        END as status,
                        token_expiry
                    FROM google_auth
                    ORDER BY email
                """)
                accounts = []
                for row in cur.fetchall():
                    email, is_valid, status, token_expiry = row
                    accounts.append({
                        "email": email,
                        "is_valid": bool(is_valid),
                        "status": status,
                        "token_expiry": token_expiry.isoformat() if token_expiry else None
                    })
                return accounts
    except Exception as e:
        api_logger.error(f"Error listing Google auth accounts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to list authenticated accounts"
        )
