from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from .google_drive import GoogleDriveManager
from typing import List, Optional
from pydantic import BaseModel
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/publish")

class DriveFolder(BaseModel):
    id: str
    name: str
    path: str

class VideoUploadResponse(BaseModel):
    id: str
    name: str
    webViewLink: str
    size: Optional[str]
    mimeType: str

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

@router.post("/drive/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    user_email: str = Form(...),
    folder_id: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """
    Upload a video file to Google Drive
    """
    try:
        # Create a temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            # Write the uploaded file to the temporary file
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            try:
                # Upload to Google Drive
                drive_manager = GoogleDriveManager(user_email)
                result = drive_manager.upload_video(
                    video_path=temp_file.name,
                    folder_id=folder_id,
                    title=title or file.filename,
                    description=description
                )
                
                # Make the file publicly readable
                drive_manager.set_file_permissions(result['id'])
                
                return {
                    "success": True,
                    "file": result
                }
            finally:
                # Clean up the temporary file
                os.unlink(temp_file.name)
                
    except Exception as e:
        logger.error(f"Error uploading video: {e}")
        raise HTTPException(status_code=500, detail=str(e))
