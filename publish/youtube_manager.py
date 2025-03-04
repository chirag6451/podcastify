import os
import logging
import re
from typing import Dict, List, Optional, Any
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, HttpError
from google.oauth2.credentials import Credentials
from create_audio.db_utils import PodcastDB

logger = logging.getLogger(__name__)

def clean_text_for_youtube(text: str, is_title: bool = False) -> str:
    """Clean text by removing HTML tags and markdown formatting
    
    Args:
        text (str): Text to clean
        is_title (bool): If True, applies title-specific rules (like length limit)
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Convert markdown links to plain text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # Remove special characters that might cause issues
    text = text.replace('\n\n', '\n')  # Replace double newlines
    text = text.replace('\\n', '\n')   # Replace escaped newlines
    text = text.replace('|', '-')      # Replace pipe with dash
    text = text.strip()
    
    # Only apply length limit for titles (YouTube has a 100 character limit for titles)
    if is_title and len(text) > 100:
        text = text[:97] + "..."
    
    return text

class YouTubeManager:
    """Manages YouTube API operations"""
    
    def __init__(self, user_email: str):
        """Initialize with user email"""
        self.user_email = user_email
        self.service = self._get_youtube_service()
        
    def _get_youtube_service(self) -> Any:
        """Get authenticated YouTube service"""
        db = PodcastDB()
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Get OAuth credentials
                cur.execute("""
                    SELECT 
                        access_token,
                        refresh_token,
                        token_uri,
                        client_id,
                        client_secret,
                        token_expiry
                    FROM google_auth 
                    WHERE email = %s
                """, (self.user_email,))
                result = cur.fetchone()
                if not result:
                    raise Exception(f"No Google credentials found for {self.user_email}")
                
                access_token, refresh_token, token_uri, client_id, client_secret, token_expiry = result
                
                # Create credentials
                creds = Credentials(
                    token=access_token,
                    refresh_token=refresh_token,
                    token_uri=token_uri,
                    client_id=client_id,
                    client_secret=client_secret,
                    scopes=["https://www.googleapis.com/auth/youtube.upload",
                           "https://www.googleapis.com/auth/youtube"]
                )
                
                # Check if token needs refresh
                if not creds.valid:
                    logger.info(f"Refreshing expired token for user {self.user_email}")
                    try:
                        # Refresh the token
                        creds.refresh(None)
                        
                        # Update the database with new token
                        cur.execute("""
                            UPDATE google_auth 
                            SET access_token = %s,
                                token_expiry = CURRENT_TIMESTAMP + INTERVAL '1 hour'
                            WHERE email = %s
                        """, (creds.token, self.user_email))
                        conn.commit()
                        logger.info(f"Successfully refreshed token for user {self.user_email}")
                    except Exception as e:
                        logger.error(f"Failed to refresh token for user {self.user_email}: {e}")
                        # Mark credentials as invalid
                        cur.execute("""
                            UPDATE google_auth 
                            SET access_token = NULL,
                                token_expiry = NULL
                            WHERE email = %s
                        """, (self.user_email,))
                        conn.commit()
                        raise Exception(f"Token refresh failed for {self.user_email}. Please re-authenticate.")
                
                # Build service
                return build("youtube", "v3", credentials=creds)
    
    def list_channels(self) -> List[Dict]:
        """List YouTube channels for the user"""
        try:
            # Get channels from YouTube API
            channels = self.service.channels().list(
                part="snippet,contentDetails",
                mine=True
            ).execute()
            
            return [{
                'id': channel['id'],
                'title': channel['snippet']['title'],
                'description': channel['snippet'].get('description', ''),
                'thumbnail': channel['snippet'].get('thumbnails', {}).get('default', {}).get('url', '')
            } for channel in channels.get('items', [])]
            
        except Exception as e:
            logger.error(f"Error listing channels: {e}")
            raise
            
    def list_playlists(self, channel_id: str) -> List[Dict]:
        """List playlists for a channel"""
        try:
            # Get playlists from YouTube API
            playlists = self.service.playlists().list(
                part="snippet,contentDetails",
                channelId=channel_id,
                maxResults=50
            ).execute()
            
            return [{
                'id': playlist['id'],
                'title': playlist['snippet']['title'],
                'description': playlist['snippet'].get('description', ''),
                'itemCount': playlist['contentDetails'].get('itemCount', 0),
                'thumbnail': playlist['snippet'].get('thumbnails', {}).get('default', {}).get('url', '')
            } for playlist in playlists.get('items', [])]
            
        except Exception as e:
            logger.error(f"Error listing playlists: {e}")
            raise
            
    def save_channel(self, channel_id: str) -> Dict:
        """Save a specific YouTube channel for later use"""
        try:
            # Get channel details from YouTube API
            channel = self.service.channels().list(
                part="snippet,contentDetails",
                id=channel_id
            ).execute()
            
            if not channel.get('items'):
                raise Exception(f"Channel {channel_id} not found")
                
            channel_data = channel['items'][0]
            
            # Get OAuth credentials
            db = PodcastDB()
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get credentials from google_auth
                    cur.execute("""
                        SELECT access_token, refresh_token, token_uri, client_id, client_secret
                        FROM google_auth 
                        WHERE email = %s
                    """, (self.user_email,))
                    creds = cur.fetchone()
                    
                    # Store channel in database
                    cur.execute("""
                        INSERT INTO customer_youtube_channels 
                        (customer_id, channel_id, channel_title, channel_description, 
                         channel_thumbnail_url, credentials_path, refresh_token, 
                         access_token, token_expiry)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP + INTERVAL '1 hour')
                        ON CONFLICT (customer_id, channel_id) 
                        DO UPDATE SET 
                            channel_title = EXCLUDED.channel_title,
                            channel_description = EXCLUDED.channel_description,
                            channel_thumbnail_url = EXCLUDED.channel_thumbnail_url,
                            access_token = EXCLUDED.access_token,
                            refresh_token = EXCLUDED.refresh_token,
                            token_expiry = EXCLUDED.token_expiry
                        RETURNING id, channel_id, channel_title, channel_description, channel_thumbnail_url
                    """, (
                        self.user_email,
                        channel_data["id"],
                        channel_data["snippet"]["title"],
                        channel_data["snippet"].get("description", ""),
                        channel_data["snippet"].get("thumbnails", {}).get("default", {}).get("url", ""),
                        f"/credentials/{self.user_email}_{channel_id}.json",  # Credentials path
                        creds[1],  # refresh_token
                        creds[0],  # access_token
                    ))
                    saved_channel = cur.fetchone()
                    conn.commit()
            
            return {
                'id': saved_channel[0],
                'channel_id': saved_channel[1],
                'title': saved_channel[2],
                'description': saved_channel[3],
                'thumbnail_url': saved_channel[4]
            }
            
        except Exception as e:
            logger.error(f"Error saving channel: {e}")
            raise
            
    def _get_channel_credentials(self, channel_id: str) -> Optional[Credentials]:
        """Get OAuth2 credentials for a specific channel"""
        try:
            db = PodcastDB()
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get channel credentials from google_auth table
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
                        return None
                        
                    # Create credentials
                    return Credentials(
                        token=result[0],
                        refresh_token=result[1],
                        token_uri=result[2] or 'https://oauth2.googleapis.com/token',
                        client_id=result[3],
                        client_secret=result[4],
                        scopes=["https://www.googleapis.com/auth/youtube.upload",
                               "https://www.googleapis.com/auth/youtube"]
                    )
                    
        except Exception as e:
            logger.error(f"Error getting channel credentials: {e}")
            return None
            
    def upload_video(self, video_path: str, channel_id: str, playlist_id: Optional[str] = None,
                    title: Optional[str] = None, description: Optional[str] = None,
                    privacy_status: str = "public", upload_id: Optional[int] = None) -> Optional[Dict]:
        """Upload a video to YouTube
        
        Args:
            video_path: Path to the video file
            channel_id: YouTube channel ID to upload to
            playlist_id: Optional playlist ID to add the video to
            title: Video title
            description: Video description
            privacy_status: Video privacy status ('public', 'private', or 'unlisted'), defaults to 'public'
            upload_id: Optional ID for tracking the upload
            
        Returns:
            Dict containing video information if successful, None if failed
        """
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")

            # Clean title and description
            clean_title = clean_text_for_youtube(title, is_title=True) if title else "Untitled Video"
            clean_description = clean_text_for_youtube(description, is_title=False) if description else ""

            body = {
                "snippet": {
                    "title": clean_title,
                    "description": clean_description,
                    "categoryId": "22"  # People & Blogs category
                },
                "status": {
                    "privacyStatus": privacy_status,
                    "selfDeclaredMadeForKids": False
                }
            }
            
            # Get channel credentials
            channel_creds = self._get_channel_credentials(channel_id)
            if not channel_creds:
                raise Exception(f"No credentials found for channel {channel_id}")

            # Initialize service with channel credentials
            self.service = build('youtube', 'v3', credentials=channel_creds)

            # Prepare the video upload
            insert_request = self.service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
            )

            response = None
            while response is None:
                try:
                    _, response = insert_request.next_chunk()
                    if response:
                        logger.info(f"Video upload complete: {response}")
                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]:
                        # Retry on server errors
                        continue
                    else:
                        raise

            # Get video details
            video_info = self.service.videos().list(
                part="status,snippet,contentDetails,statistics",
                id=response["id"]
            ).execute()['items'][0]

            # Upload thumbnail if available
            db = PodcastDB()
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT selected_thumbnail_path 
                        FROM youtube_video_metadata 
                        WHERE id = %s
                    """, (upload_id,))
                    result = cur.fetchone()
                    if result and result[0] and os.path.exists(result[0]):
                        try:
                            self.service.thumbnails().set(
                                videoId=response["id"],
                                media_body=MediaFileUpload(result[0], mimetype='image/jpeg', resumable=True)
                            ).execute()
                            logger.info(f"Successfully uploaded thumbnail for video {response['id']}")
                        except Exception as e:
                            logger.error(f"Error uploading thumbnail: {e}")

            # Add to playlist if specified
            if playlist_id and playlist_id != "string":
                try:
                    self.service.playlistItems().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "playlistId": playlist_id,
                                "resourceId": {
                                    "kind": "youtube#video",
                                    "videoId": response["id"]
                                }
                            }
                        }
                    ).execute()
                except Exception as e:
                    logger.error(f"Error adding video to playlist: {e}")
                    # Don't fail the upload if playlist add fails

            # Update database with success
            db = PodcastDB()
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE youtube_video_metadata
                        SET publish_status = 'published'::youtube_publish_status,
                            youtube_video_id = %s,
                            published_at = CURRENT_TIMESTAMP
                        WHERE id = %s AND customer_id = %s
                        RETURNING id, youtube_video_id, title, description, publish_status
                    """, (response["id"], upload_id, self.user_email))
                    result = cur.fetchone()
                    conn.commit()

            return {
                'id': result[0],
                'youtube_id': result[1],
                'title': result[2],
                'description': result[3],
                'status': result[4],
                'url': f"https://www.youtube.com/watch?v={result[1]}"
            }

        except Exception as e:
            if upload_id:
                # Update database with error
                db = PodcastDB()
                with db.get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE youtube_video_metadata
                            SET publish_status = 'failed'::youtube_publish_status,
                                publish_error = %s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = %s
                        """, (str(e), upload_id))
                        conn.commit()
            raise

    def get_video_status(self, video_id: str) -> Dict:
        """Get the current status of a YouTube video"""
        try:
            # Get video details from YouTube API
            video_details = self.service.videos().list(
                part="status,snippet,contentDetails",
                id=video_id
            ).execute()
            
            if not video_details.get('items'):
                raise Exception(f"Video {video_id} not found")
                
            video_info = video_details['items'][0]
            
            # Update database with latest status
            db = PodcastDB()
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE youtube_video_metadata
                        SET publish_status = %s::youtube_publish_status,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE youtube_video_id = %s
                        RETURNING id, title, description, privacy_status, 
                                 publish_status, youtube_video_id,
                                 published_at
                    """, (
                        'processing' if video_info['status'].get('processingStatus') == 'processing' 
                        else 'published',
                        video_id
                    ))
                    result = cur.fetchone()
                    conn.commit()
            
            # Get the YouTube processing status
            processing_status = video_info['status'].get('processingStatus', 'processing')
            
            return {
                'id': result[0],
                'title': result[1],
                'description': result[2],
                'privacy_status': result[3],
                'publish_status': result[4],
                'youtube_id': result[5],
                'published_at': result[6],
                'processing_status': processing_status,  # From YouTube API
                'url': f"https://www.youtube.com/watch?v={result[5]}"
            }
            
        except Exception as e:
            logger.error(f"Error getting video status: {e}")
            raise

    def delete_video(self, video_id: str) -> Dict:
        """Delete a YouTube video"""
        try:
            # Get video details first to confirm ownership
            video_details = self.service.videos().list(
                part="status,snippet",
                id=video_id
            ).execute()
            
            if not video_details.get('items'):
                raise Exception(f"Video {video_id} not found")
            
            # Delete from YouTube
            self.service.videos().delete(
                id=video_id
            ).execute()
            
            # Update database
            db = PodcastDB()
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE youtube_video_metadata
                        SET publish_status = 'failed'::youtube_publish_status,
                            deleted_at = CURRENT_TIMESTAMP,
                            publish_error = 'Video deleted from YouTube'
                        WHERE youtube_video_id = %s AND customer_id = %s
                        RETURNING id, youtube_video_id, title
                    """, (video_id, self.user_email))
                    result = cur.fetchone()
                    if not result:
                        raise Exception(f"Video {video_id} not found in database")
                    conn.commit()
            
            return {
                'id': result[0],
                'youtube_id': result[1],
                'title': result[2],
                'status': 'deleted'
            }
            
        except Exception as e:
            logger.error(f"Error deleting video: {e}")
            raise
