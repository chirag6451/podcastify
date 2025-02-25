from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from create_audio.db_utils import PodcastDB
import json
import logging
import os
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Full access scopes for Google Drive
SCOPES = [
    'https://www.googleapis.com/auth/drive',  # Full Drive access
    'https://www.googleapis.com/auth/drive.file',  # Access to files created by the app
    'https://www.googleapis.com/auth/drive.appdata',  # Access to app-specific data
    'https://www.googleapis.com/auth/drive.metadata'  # Read/write file metadata
]

class GoogleDriveManager:
    def __init__(self, user_email):
        self.user_email = user_email
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialize Google Drive service with stored credentials"""
        try:
            # Get stored token from database
            db = PodcastDB()
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            access_token,
                            refresh_token,
                            token_uri,
                            client_id,
                            client_secret
                        FROM google_auth
                        WHERE email = %s
                    """, (self.user_email,))
                    result = cur.fetchone()
                    
                    if not result:
                        raise Exception(f"No stored credentials found for {self.user_email}")
                    
                    access_token, refresh_token, token_uri, client_id, client_secret = result

            # Create credentials object
            creds = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri=token_uri,
                client_id=client_id,
                client_secret=client_secret,
                scopes=SCOPES
            )

            # Refresh token if expired
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    # Update the access token in database
                    with db.get_connection() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                UPDATE google_auth 
                                SET access_token = %s,
                                    refresh_token = %s,
                                    updated_at = CURRENT_TIMESTAMP
                                WHERE email = %s
                            """, (creds.token, creds.refresh_token, self.user_email))
                            conn.commit()
                            logger.info("Updated access token in database")
                else:
                    raise Exception("Token expired and no refresh token available")

            # Build the Drive service with cache disabled
            self.service = build('drive', 'v3', credentials=creds, cache_discovery=False)
            logger.info(f"Successfully initialized Drive service for {self.user_email}")
            
        except Exception as e:
            logger.error(f"Error initializing Drive service: {e}")
            raise

    def upload_video(self, video_path: str, folder_id: Optional[str] = None, 
                    title: Optional[str] = None, description: Optional[str] = None) -> Dict:
        """
        Upload a video file to Google Drive
        
        Args:
            video_path (str): Path to the video file
            folder_id (str): ID of the folder to upload to. If None, uploads to root.
            title (str): Title for the video. If None, uses filename.
            description (str): Description for the video
            
        Returns:
            dict: Uploaded file metadata including webViewLink
        """
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
                
            file_name = title or os.path.basename(video_path)
            mime_type = 'video/mp4'  # Assuming MP4 format
            
            file_metadata = {
                'name': file_name,
                'description': description
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Create MediaFileUpload object with resumable upload
            media = MediaFileUpload(
                video_path,
                mimetype=mime_type,
                resumable=True
            )
            
            # Upload the file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, size, mimeType'
            ).execute()
            
            logger.info(f"Uploaded video: {file_name} with ID: {file['id']}")
            return file
            
        except Exception as e:
            logger.error(f"Error uploading video: {e}")
            raise

    def set_file_permissions(self, file_id: str, role: str = 'reader', 
                           type: str = 'anyone') -> Dict:
        """
        Set sharing permissions for a file
        
        Args:
            file_id (str): ID of the file to share
            role (str): Permission role ('reader', 'writer', 'commenter')
            type (str): Type of permission ('user', 'group', 'domain', 'anyone')
            
        Returns:
            dict: Updated permission details
        """
        try:
            permission = {
                'role': role,
                'type': type
            }
            
            result = self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
            logger.info(f"Set {role} permission for {type} on file: {file_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error setting permissions: {e}")
            raise

    def list_folders(self, parent_id='root', page_size=50, page_token=None):
        """
        List folders in Google Drive with pagination
        
        Args:
            parent_id (str): ID of the parent folder (default: 'root')
            page_size (int): Number of folders to return per page (default: 50, max: 100)
            page_token (str): Token for the next page (default: None)
            
        Returns:
            dict: {
                'folders': list of folder objects,
                'nextPageToken': token for the next page if more results exist
            }
        """
        try:
            if not self.service:
                self._initialize_service()

            # Ensure page_size is within limits
            page_size = min(max(1, page_size), 100)

            query = f"mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='nextPageToken, files(id, name)',
                pageSize=page_size,
                pageToken=page_token,
                orderBy='name'  # Sort by name
            ).execute()
            
            return {
                'folders': results.get('files', []),
                'nextPageToken': results.get('nextPageToken')
            }
            
        except Exception as e:
            logger.error(f"Error listing folders: {e}")
            raise

    def _get_folder_path(self, folder_id):
        """Get the full path of a folder"""
        try:
            path_parts = []
            current_id = folder_id
            
            while current_id != 'root':
                file = self.service.files().get(
                    fileId=current_id,
                    fields='name, parents'
                ).execute()
                
                path_parts.insert(0, file['name'])
                current_id = file.get('parents', ['root'])[0]
            
            return '/' + '/'.join(path_parts)
            
        except Exception as e:
            logger.error(f"Error getting folder path: {e}")
            return "Unknown path"
