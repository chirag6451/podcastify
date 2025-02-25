import os
from google_auth import get_credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import io
from typing import Optional, List, Dict
import logging

class DriveUtils:
    def __init__(self, credentials_path: str = 'credentials.json'):
        """Initialize Drive Utils with credentials"""
        self.credentials_path = credentials_path
        self.service = self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Drive service"""
        try:
            creds = get_credentials()
            return build('drive', 'v3', credentials=creds)
        except Exception as e:
            raise Exception(f"Failed to initialize Drive service: {str(e)}")
    
    @staticmethod
    def get_folder_id_from_url(url: str) -> str:
        """Extract folder ID from Google Drive URL"""
        if not url:
            raise ValueError("URL cannot be empty")
            
        # Clean up the URL
        url = url.strip()
        
        # Handle folder URLs
        if "/folders/" in url:
            folder_id = url.split("/folders/")[-1].split("/")[0].split("?")[0]
            return folder_id
            
        # Handle file URLs
        elif "/file/d/" in url:
            file_id = url.split("/file/d/")[-1].split("/")[0].split("?")[0]
            return file_id
            
        # Handle direct file IDs
        elif url.startswith("http") and "id=" in url:
            file_id = url.split("id=")[-1].split("&")[0]
            return file_id
            
        # Handle view URLs
        elif "view" in url:
            # Try to extract ID between /d/ and /view
            try:
                file_id = url.split("/d/")[-1].split("/view")[0]
                return file_id
            except:
                # Try to extract ID after /d/ and before any query params
                try:
                    file_id = url.split("/d/")[-1].split("?")[0]
                    return file_id
                except:
                    raise ValueError(f"Could not extract ID from view URL: {url}")
            
        # Handle direct IDs (not URLs)
        elif not url.startswith("http"):
            return url
            
        raise ValueError(f"Could not extract ID from URL: {url}")

    def find_audio_files(self, folder_id: str, recursive: bool = True) -> List[Dict]:
        """
        Find audio files in a Google Drive folder
        
        Args:
            folder_id: ID of the Google Drive folder
            recursive: Whether to search in subfolders
            
        Returns:
            List of dictionaries containing file information
        """
        audio_files = []
        try:
            # Query for audio files
            query = f"'{folder_id}' in parents and (mimeType contains 'audio/mpeg' or mimeType contains 'audio/wav' or fileExtension='mp3' or fileExtension='wav')"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType)"
            ).execute()
            audio_files.extend(results.get('files', []))
            
            if recursive:
                # Query for subfolders
                folder_results = self.service.files().list(
                    q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder'",
                    fields="files(id, name)"
                ).execute()
                subfolders = folder_results.get('files', [])
                
                # Recursively search subfolders
                for folder in subfolders:
                    audio_files.extend(self.find_audio_files(folder['id'], recursive))
            
            return audio_files
            
        except Exception as e:
            raise Exception(f"Error finding audio files: {str(e)}")
    
    def download_file(self, file_id: str, output_path: str) -> bool:
        """
        Download a file from Google Drive
        
        Args:
            file_id: ID of the file to download
            output_path: Path where to save the file
            
        Returns:
            bool: True if download was successful
        """
        try:
            # First try to get the file metadata
            file_metadata = self.service.files().get(fileId=file_id, fields='id, name, mimeType').execute()
            print(f"File metadata: {file_metadata}")
            
            # Try different download methods
            try:
                # Method 1: Direct download
                request = self.service.files().get_media(fileId=file_id)
            except Exception as e1:
                print(f"Direct download failed, trying export: {str(e1)}")
                try:
                    # Method 2: Export for Google Docs types
                    request = self.service.files().export_media(fileId=file_id, mimeType='application/pdf')
                except Exception as e2:
                    print(f"Export failed, trying alt=media: {str(e2)}")
                    # Method 3: Using alt=media parameter
                    request = self.service.files().get(fileId=file_id, alt='media')
            
            file_handle = io.BytesIO()
            downloader = MediaIoBaseDownload(file_handle, request)
            done = False
            
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    print(f"Download progress: {int(status.progress() * 100)}%")
            
            # Save the file
            with open(output_path, "wb") as f:
                f.write(file_handle.getvalue())
            
            # Verify file was created and has content
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"File downloaded successfully: {output_path} ({os.path.getsize(output_path)} bytes)")
                return True
            else:
                print(f"File download appears to have failed: {output_path}")
                return False
            
        except Exception as e:
            print(f"Error downloading file: {str(e)}")
            return False

    def upload_file(self, file_path: str, folder_id: str, new_filename: Optional[str] = None) -> Optional[str]:
        """
        Upload a file to Google Drive
        
        Args:
            file_path: Path to the file to upload
            folder_id: ID of the destination folder
            new_filename: Optional new name for the file
            
        Returns:
            str: ID of the uploaded file if successful, None otherwise
        """
        try:
            # First verify the folder exists and we have access
            try:
                folder = self.service.files().get(fileId=folder_id, fields='id, name').execute()
                logging.info(f"Found destination folder: {folder.get('name', 'Unknown')} ({folder['id']})")
            except Exception as e:
                logging.error(f"Could not access folder {folder_id}: {str(e)}")
                # Try to extract folder ID again in case it's a URL
                if folder_id.startswith('https://'):
                    try:
                        folder_id = self.get_folder_id_from_url(folder_id)
                        folder = self.service.files().get(fileId=folder_id, fields='id, name').execute()
                        logging.info(f"Found destination folder using extracted ID: {folder.get('name', 'Unknown')} ({folder['id']})")
                    except Exception as e2:
                        logging.error(f"Could not access folder even after ID extraction: {str(e2)}")
                        return None
                else:
                    return None

            file_name = new_filename or os.path.basename(file_path)
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(
                file_path,
                resumable=True
            )
            
            logging.info(f"Starting file upload to folder {folder_id}...")
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            if file_id:
                logging.info(f"Successfully uploaded file. ID: {file_id}")
                return file_id
            else:
                logging.error("File upload succeeded but no file ID returned")
                return None
            
        except Exception as e:
            logging.error(f"Error uploading file: {str(e)}", exc_info=True)
            return None
