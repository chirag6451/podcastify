from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from create_audio.db_utils import PodcastDB
import json
import logging
import os
from typing import Optional, Dict
from datetime import datetime

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

    def create_folder(self, folder_name: str, parent_folder_id: Optional[str] = None) -> Dict:
        """
        Create a new folder in Google Drive
        
        Args:
            folder_name (str): Name of the folder to create
            parent_folder_id (str): ID of the parent folder. If None, creates in root.
            
        Returns:
            dict: Created folder metadata including id and webViewLink
        """
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id, name, webViewLink'
            ).execute()
            
            # Make the folder publicly accessible
            permission = {
                'role': 'reader',
                'type': 'anyone'
            }
            self.service.permissions().create(
                fileId=folder['id'],
                body=permission
            ).execute()
            
            # Get the shareable link
            shared_folder = self.service.files().get(
                fileId=folder['id'],
                fields='webViewLink'
            ).execute()
            
            folder['shareUrl'] = shared_folder['webViewLink']
            return folder
            
        except Exception as e:
            logger.error(f"Error creating folder: {e}")
            raise

    def upload_file(self, file_path: str, folder_id: Optional[str] = None, 
                    title: Optional[str] = None, description: Optional[str] = None) -> Dict:
        """
        Upload a file to Google Drive and make it shareable
        
        Args:
            file_path (str): Path to the file
            folder_id (str): ID of the folder to upload to. If None, uploads to root.
            title (str): Title for the file. If None, uses filename.
            description (str): Description for the file
            
        Returns:
            dict: Uploaded file metadata including webViewLink and shareUrl
        """
        upload_id = None
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
                
            original_file_name = os.path.basename(file_path)
            file_name = title or original_file_name
            mime_type = self._get_mime_type(file_path)
            
            # Get user_id first
            db = PodcastDB()
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT user_id FROM google_auth WHERE email = %s
                    """, (self.user_email,))
                    user_id = cur.fetchone()[0]
                    
                    # Create initial upload record with pending status
                    cur.execute("""
                        INSERT INTO user_drive_uploads 
                        (user_id, folder_id, file_name, original_file_name, upload_status)
                        VALUES (%s, %s, %s, %s, 'pending')
                        RETURNING id
                    """, (user_id, folder_id, file_name, original_file_name))
                    upload_id = cur.fetchone()[0]
                    conn.commit()
            
            # Create a folder for this upload
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            upload_folder_name = f"{file_name.rsplit('.', 1)[0]}_{timestamp}"
            upload_folder = self.create_folder(upload_folder_name, folder_id)
            
            file_metadata = {
                'name': file_name,
                'description': description,
                'parents': [upload_folder['id']]  # Upload to the new folder
            }
            
            # Create MediaFileUpload object with resumable upload
            media = MediaFileUpload(
                file_path,
                mimetype=mime_type,
                resumable=True
            )
            
            # Upload the file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, size, mimeType'
            ).execute()
            
            # Make the file publicly accessible and get share URL
            permission = {
                'role': 'reader',
                'type': 'anyone'
            }
            self.service.permissions().create(
                fileId=file['id'],
                body=permission
            ).execute()
            
            # Get the shareable link
            shared_file = self.service.files().get(
                fileId=file['id'],
                fields='webViewLink'
            ).execute()
            share_url = shared_file['webViewLink']
            
            # Update upload record with success status and file details
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE user_drive_uploads 
                        SET upload_status = 'completed',
                            file_id = %s,
                            file_size = %s,
                            mime_type = %s,
                            web_view_link = %s,
                            share_url = %s,
                            upload_folder_id = %s,
                            upload_folder_name = %s,
                            upload_folder_share_url = %s
                        WHERE id = %s
                    """, (
                        file['id'],
                        file.get('size'),
                        file.get('mimeType'),
                        file.get('webViewLink'),
                        share_url,
                        upload_folder['id'],
                        upload_folder_name,
                        upload_folder['shareUrl'],
                        upload_id
                    ))
                    conn.commit()
            
            logger.info(f"Uploaded and shared file: {file_name} with ID: {file['id']} in folder: {upload_folder_name}")
            return {
                **file, 
                'shareUrl': share_url,
                'uploadFolder': {
                    'id': upload_folder['id'],
                    'name': upload_folder_name,
                    'shareUrl': upload_folder['shareUrl']
                }
            }
            
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            # Update upload record with error status
            if upload_id:
                db = PodcastDB()
                with db.get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE user_drive_uploads 
                            SET upload_status = 'failed',
                                error_message = %s
                            WHERE id = %s
                        """, (str(e), upload_id))
                        conn.commit()
            raise

    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type based on file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.mp4': 'video/mp4',
            '.txt': 'text/plain',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png'
        }
        return mime_types.get(ext, 'application/octet-stream')

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

            query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_id != 'root':
                query += f" and '{parent_id}' in parents"

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='nextPageToken, files(id, name)',
                pageSize=page_size,
                pageToken=page_token,
                orderBy='name'  # Sort by name
            ).execute()
            
            logger.info(f"Found {len(results.get('files', []))} folders with page size {page_size}")
            return {
                'folders': results.get('files', []),
                'nextPageToken': results.get('nextPageToken')
            }
            
        except Exception as e:
            logger.error(f"Error listing folders: {e}")
            raise

    def search_folders(self, query_text, page_size=50, page_token=None):
        """
        Search for folders in Google Drive by name
        
        Args:
            query_text (str): Text to search for in folder names
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

            # Create search query
            query = f"mimeType='application/vnd.google-apps.folder' and name contains '{query_text}' and trashed=false"

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='nextPageToken, files(id, name)',
                pageSize=page_size,
                pageToken=page_token,
                orderBy='name'  # Sort by name
            ).execute()
            
            logger.info(f"Found {len(results.get('files', []))} folders matching '{query_text}'")
            return {
                'folders': results.get('files', []),
                'nextPageToken': results.get('nextPageToken')
            }
            
        except Exception as e:
            logger.error(f"Error searching folders: {e}")
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
