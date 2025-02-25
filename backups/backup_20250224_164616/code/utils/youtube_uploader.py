"""
YouTube Uploader Utility

This module handles uploading generated videos to YouTube playlists.
Requires Google OAuth2 credentials and YouTube Data API v3.
"""

import os
import logging
from typing import Optional, Dict, List
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from video_creator.db_utils import VideoDB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# YouTube API scopes required
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtubepartner'
]

class YouTubeUploader:
    def __init__(self):
        """Initialize YouTube uploader."""
        self.credentials = None
        self.youtube = None
        self.db = VideoDB()
    
    def authenticate(self, credentials_path: str, token_path: str) -> None:
        """
        Authenticate with YouTube using OAuth2.
        
        Args:
            credentials_path: Path to client_secrets.json file
            token_path: Path to store/retrieve OAuth2 token
        """
        if os.path.exists(token_path):
            self.credentials = Credentials.from_authorized_user_file(token_path, SCOPES)

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                self.credentials = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open(token_path, 'w') as token:
                token.write(self.credentials.to_json())
        
        self.youtube = build('youtube', 'v3', credentials=self.credentials)
    
    def upload_video(self, video_path: str, title: str, description: str, 
                    privacy_status: str = 'private', tags: Optional[list] = None) -> Dict:
        """
        Upload a video to YouTube.
        
        Args:
            video_path: Path to the video file
            title: Video title
            description: Video description
            privacy_status: Video privacy status (private/public/unlisted)
            tags: Optional list of video tags
            
        Returns:
            Dictionary containing video ID and other metadata
        """
        if not self.youtube:
            raise ValueError("Not authenticated. Call authenticate() first.")
            
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'categoryId': '22'  # People & Blogs category
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        media = MediaFileUpload(video_path, 
                              mimetype='video/*',
                              resumable=True)
        
        try:
            logger.info(f"Starting upload for video: {title}")
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Uploaded {int(status.progress() * 100)}%")
            
            logger.info(f"Upload Complete! Video ID: {response['id']}")
            return response
            
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            raise
    
    def add_to_playlist(self, video_id: str, playlist_id: str) -> Dict:
        """
        Add a video to a specified playlist.
        
        Args:
            video_id: YouTube video ID
            playlist_id: YouTube playlist ID
            
        Returns:
            Dictionary containing playlist item details
        """
        if not self.youtube:
            raise ValueError("Not authenticated. Call authenticate() first.")
            
        body = {
            'snippet': {
                'playlistId': playlist_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        }
        
        try:
            logger.info(f"Adding video {video_id} to playlist {playlist_id}")
            response = self.youtube.playlistItems().insert(
                part='snippet',
                body=body
            ).execute()
            
            logger.info("Successfully added to playlist!")
            return response
            
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            raise
    
    def upload_pending_videos(self) -> None:
        """Upload all pending videos to YouTube."""
        # Get pending videos from database
        pending_videos = self.db.get_pending_youtube_uploads()
        
        for video in pending_videos:
            try:
                # Authenticate with channel credentials
                self.authenticate(
                    credentials_path=video['credentials_path'],
                    token_path=video['token_path']
                )
                
                # Get video metadata
                title = video.get('title') or video.get('job_title', f"Video {video['job_id']}")
                description = video.get('description') or video.get('job_description', '')
                tags = video.get('tags', [])
                video_path = video.get('final_video_path')
                
                if not video_path or not os.path.exists(video_path):
                    logger.error(f"Video file not found: {video_path}")
                    self.db.update_youtube_video_status(
                        video_id=video['id'],
                        status='error',
                        error_message=f"Video file not found: {video_path}"
                    )
                    continue
                
                # Upload video
                response = self.upload_video(
                    video_path=video_path,
                    title=title,
                    description=description,
                    privacy_status=video.get('privacy_status', 'private'),
                    tags=tags
                )
                
                # Add to playlist if specified
                if video.get('playlist_id') and response:
                    self.add_to_playlist(response['id'], video['playlist_id'])
                
                # Update database with YouTube video ID
                self.db.update_youtube_video_status(
                    video_id=video['id'],
                    status='uploaded',
                    youtube_video_id=response['id']
                )
                
                logger.info(f"Successfully processed video {video['job_id']}")
                
            except Exception as e:
                logger.error(f"Failed to process video {video['job_id']}: {str(e)}")
                # Update database with error status
                self.db.update_youtube_video_status(
                    video_id=video['id'],
                    status='error',
                    error_message=str(e)
                )
