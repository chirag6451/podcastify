from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from .google_drive import GoogleDriveManager
from .youtube_manager import YouTubeManager
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import tempfile
import os
import logging
import shutil
from create_audio.db_utils import PodcastDB

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/publish")

class DriveFolder(BaseModel):
    id: str
    name: str
    path: str

class UploadFolderResponse(BaseModel):
    id: str
    name: str
    shareUrl: str

class VideoUploadResponse(BaseModel):
    success: bool
    file: Dict[str, Any]

class YouTubeChannel(BaseModel):
    id: str
    title: str
    description: Optional[str]
    
class YouTubePlaylist(BaseModel):
    id: str
    title: str
    description: Optional[str]
    
class YouTubeUploadResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    url: str

@router.get("/drive/folders")
async def list_drive_folders(
    user_email: str = Query(..., description="User's email address"),
    parent_id: str = Query('root', description="Parent folder ID"),
    page_size: int = Query(50, ge=1, le=100, description="Number of folders per page"),
    page_token: str = Query(None, description="Token for the next page")
):
    """
    List folders in Google Drive with pagination
    
    - page_size: Number of folders to return (1-100, default: 50)
    - page_token: Token for the next page (optional)
    """
    try:
        drive_manager = GoogleDriveManager(user_email)
        result = drive_manager.list_folders(parent_id, page_size, page_token)
        return {
            "success": True,
            "folders": result['folders'],
            "nextPageToken": result.get('nextPageToken')
        }
    except Exception as e:
        logger.error(f"Error listing folders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/drive/search-folders")
async def search_drive_folders(
    user_email: str = Query(..., description="User's email address"),
    query: str = Query(..., description="Search query"),
    page_size: int = Query(50, ge=1, le=100, description="Number of folders per page"),
    page_token: Optional[str] = Query(None, description="Token for the next page")
):
    """
    Search for folders in Google Drive by name
    """
    try:
        drive_manager = GoogleDriveManager(user_email)
        result = drive_manager.search_folders(
            query_text=query,
            page_size=page_size,
            page_token=page_token
        )
        return {"success": True, "folders": result["folders"], "nextPageToken": result["nextPageToken"]}
    except Exception as e:
        logger.error(f"Error searching Drive folders: {e}")
        return {"success": False, "error": str(e)}

@router.post("/drive/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    user_email: str = Form(...),
    folder_id: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """
    Upload a file to Google Drive
    """
    try:
        # Save uploaded file temporarily
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            # Upload to Google Drive
            drive_manager = GoogleDriveManager(user_email)
            result = drive_manager.upload_file(
                file_path=temp_file_path,
                folder_id=folder_id,
                title=title,
                description=description
            )
            return {"success": True, "file": result}
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/youtube/channels")
async def list_youtube_channels(user_email: str):
    """List YouTube channels for the user"""
    try:
        youtube = YouTubeManager(user_email)
        channels = youtube.list_channels()
        return channels
    except Exception as e:
        logger.error(f"Error listing channels: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/youtube/playlists/{channel_id}")
async def list_youtube_playlists(channel_id: str, user_email: str):
    """List playlists for a YouTube channel"""
    try:
        youtube = YouTubeManager(user_email)
        playlists = youtube.list_playlists(channel_id)
        return playlists
    except Exception as e:
        logger.error(f"Error listing playlists: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/youtube/channels/{channel_id}/save")
async def save_youtube_channel(
    channel_id: str,
    user_email: str = Query(..., description="User's email address")
):
    """Save a YouTube channel for later use"""
    try:
        youtube = YouTubeManager(user_email)
        saved_channel = youtube.save_channel(channel_id)
        return saved_channel
    except Exception as e:
        logger.error(f"Error saving channel: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/youtube/playlists/{playlist_id}/save")
async def save_youtube_playlist(
    playlist_id: str,
    channel_id: str = Query(..., description="YouTube channel ID"),
    user_email: str = Query(..., description="User's email address")
):
    """Save a YouTube playlist for later use"""
    try:
        # First get the channel from our database
        db = PodcastDB()
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Get channel ID from our database
                cur.execute("""
                    SELECT id 
                    FROM customer_youtube_channels 
                    WHERE customer_id = %s AND channel_id = %s
                """, (user_email, channel_id))
                channel_result = cur.fetchone()
                if not channel_result:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Channel {channel_id} not found. Please save it first using /youtube/channels/{channel_id}/save"
                    )
                db_channel_id = channel_result[0]
                
                # Get playlist details from YouTube
                youtube = YouTubeManager(user_email)
                playlists = youtube.list_playlists(channel_id)
                playlist = next((p for p in playlists if p['id'] == playlist_id), None)
                if not playlist:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Playlist {playlist_id} not found"
                    )
                
                # Save playlist to database
                cur.execute("""
                    INSERT INTO customer_youtube_playlists
                    (channel_id, playlist_id, playlist_title, playlist_description)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (channel_id, playlist_id) 
                    DO UPDATE SET 
                        playlist_title = EXCLUDED.playlist_title,
                        playlist_description = EXCLUDED.playlist_description
                    RETURNING id, playlist_id, playlist_title
                """, (db_channel_id, playlist['id'], playlist['title'], playlist.get('description', '')))
                saved_playlist = cur.fetchone()
                conn.commit()
                
                return {
                    "id": saved_playlist[0],
                    "playlist_id": saved_playlist[1],
                    "title": saved_playlist[2]
                }
                
    except Exception as e:
        logger.error(f"Error saving playlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/youtube/upload")
async def upload_youtube_video(
    file: UploadFile = File(...),
    user_email: str = Form(...),
    channel_id: str = Form(...),
    playlist_id: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    privacy_status: str = Form("private")
):
    """Create a pending YouTube video upload"""
    try:
        # Save video file
        temp_file = f"/tmp/{file.filename}"
        try:
            with open(temp_file, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # First get the channel ID from our database
            db = PodcastDB()
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id 
                        FROM customer_youtube_channels 
                        WHERE customer_id = %s AND channel_id = %s
                    """, (user_email, channel_id))
                    channel_result = cur.fetchone()
                    if not channel_result:
                        raise HTTPException(
                            status_code=404, 
                            detail=f"Channel {channel_id} not found. Please save it first using /youtube/channels/{channel_id}/save"
                        )
                    
                    # For direct video uploads, store the file path directly in metadata
                    cur.execute("""
                        INSERT INTO youtube_video_metadata
                        (customer_id, channel_id, title, description, 
                         privacy_status, publish_status, video_file_path)
                        VALUES (%s, %s, %s, %s, %s::youtube_privacy_status, 
                                'draft'::youtube_publish_status, %s)
                        RETURNING id, title, description, publish_status
                    """, (
                        user_email,
                        channel_result[0],
                        title or file.filename,
                        description,
                        privacy_status,
                        temp_file
                    ))
                    result = cur.fetchone()
                    conn.commit()
            
            return {
                'id': result[0],
                'title': result[1],
                'description': result[2],
                'status': result[3],
                'message': 'Video upload created and pending approval'
            }
            
        finally:
            # Don't delete temp file as we need it for upload
            pass
                
    except Exception as e:
        logger.error(f"Error creating video upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/youtube/videos/{video_id}/status")
async def get_youtube_video_status(
    video_id: str,
    user_email: str = Query(..., description="User's email address")
):
    """Get the current status of a YouTube video"""
    try:
        youtube = YouTubeManager(user_email)
        return youtube.get_video_status(video_id)
    except Exception as e:
        logger.error(f"Error getting video status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/youtube/videos/{video_id}")
async def delete_youtube_video(
    video_id: str,
    user_email: str = Query(..., description="User's email address")
):
    """Delete a YouTube video"""
    try:
        db = PodcastDB()
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Get YouTube video ID from our database
                cur.execute("""
                    SELECT youtube_video_id 
                    FROM youtube_video_metadata 
                    WHERE id = %s AND customer_id = %s
                """, (video_id, user_email))
                result = cur.fetchone()
                if not result or not result[0]:
                    raise HTTPException(
                        status_code=404,
                        detail=f"No YouTube video found for ID {video_id}"
                    )
                youtube_video_id = result[0]
                
                # Delete from YouTube
                youtube = YouTubeManager(user_email)
                youtube.delete_video(youtube_video_id)
                
                # Update our database
                cur.execute("""
                    UPDATE youtube_video_metadata
                    SET youtube_video_id = NULL,
                        publish_status = 'draft'::youtube_publish_status,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s AND customer_id = %s
                    RETURNING id
                """, (video_id, user_email))
                conn.commit()
                
                return {"message": "Video deleted successfully"}
                
    except Exception as e:
        logger.error(f"Error deleting video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/youtube/videos/{video_id}/approve")
async def approve_youtube_video(
    video_id: int,
    user_email: str = Query(..., description="User's email address")
):
    """Approve a YouTube video for upload"""
    try:
        db = PodcastDB()
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE youtube_video_metadata
                    SET approval_status = 'approved'::youtube_approval_status,
                        approved_at = CURRENT_TIMESTAMP,
                        approved_by = %s
                    WHERE id = %s AND customer_id = %s
                    RETURNING id, title, description, approval_status
                """, (user_email, video_id, user_email))
                result = cur.fetchone()
                if not result:
                    raise HTTPException(status_code=404, detail="Video not found")
                conn.commit()
        
        return {
            'id': result[0],
            'title': result[1],
            'description': result[2],
            'status': result[3],
            'message': 'Video approved for upload'
        }
        
    except Exception as e:
        logger.error(f"Error approving video: {e}")
        raise HTTPException(status_code=500, detail=str(e))
