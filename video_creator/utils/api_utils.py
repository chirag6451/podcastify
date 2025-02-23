import os
import requests
import logging
from typing import Optional, Dict, Tuple, Any
from .drive_utils import DriveUtils
import constants

# API Configuration
BASE_URL = "http://localhost:3000"
HEADERS = {
    "x-api-key": "indapoint-secure-key-2024",
    "Content-Type": "application/json"
}

class PodcastAPIManager:
    def __init__(self, base_url: str = BASE_URL, api_key: str = HEADERS["x-api-key"]):
        """Initialize PodcastAPIManager with API configuration"""
        self.base_url = base_url
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
        self.drive_utils = DriveUtils()
        self.temp_dir = "temp_audio"
        os.makedirs(self.temp_dir, exist_ok=True)

    def validate_path(self, path: str, default_path: str) -> str:
        """
        Validate if a path exists, return default if not
        
        Args:
            path: Path to validate
            default_path: Default path from constants.py
            
        Returns:
            str: Valid path or default path
        """
        if not path:
            logging.warning(f"Path not provided, using default: {default_path}")
            return default_path
            
        if not os.path.exists(path):
            logging.error(f"Path {path} does not exist, using default: {default_path}")
            return default_path
            
        return path

    def get_video_settings(self, project_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and validate video settings from project settings
        
        Args:
            project_settings: Settings from API response
            
        Returns:
            Dict[str, Any]: Validated video settings
        """
        try:
            settings = project_settings.get('videoSettings', {})
            
            # Validate paths
            paths = settings.get('paths', {})
            validated_paths = {
                'output_dir': self.validate_path(paths.get('output_dir'), constants.OUTPUT_DIR),
                'intro_video': self.validate_path(project_settings.get('introVideo'), constants.DEFAULT_INTRO_VIDEO),
                'outro_video': self.validate_path(project_settings.get('outroVideo'), constants.DEFAULT_OUTRO_VIDEO),
                'bg_music': self.validate_path(project_settings.get('bgMusic'), constants.DEFAULT_BG_MUSIC),
                'logo': self.validate_path(project_settings.get('logoPath'), constants.DEFAULT_LOGO_PATH),
                'brief_video': os.path.join(constants.OUTPUT_DIR, 'brief_video.mp4'),
                'short_video': os.path.join(constants.OUTPUT_DIR, 'short_video.mp4'),
                'podcast_video': os.path.join(constants.OUTPUT_DIR, 'podcast_video.mp4')
            }
            
            # Get text settings or use defaults
            text_settings = settings.get('text', {})
            text_content = text_settings.get('content', {})
            text = {
                'heading': text_content.get('heading', constants.DEFAULT_HEADING),
                'subheading': text_content.get('subheading', constants.DEFAULT_SUBHEADING),
                'footer': text_content.get('footer', constants.DEFAULT_FOOTER)
            }
            
            # Combine all settings
            return {
                'paths': validated_paths,
                'text': text,
                'dimensions': settings.get('dimensions', {
                    'width': constants.VIDEO_WIDTH,
                    'height': constants.VIDEO_HEIGHT
                }),
                'durations': settings.get('durations', {
                    'brief': constants.DEFAULT_BRIEF_DURATION,
                    'intro': constants.DEFAULT_INTRO_DURATION,
                    'outro': constants.DEFAULT_OUTRO_DURATION,
                    'short': constants.DEFAULT_SHORT_DURATION,
                    'fade_in': constants.FADE_IN_DURATION,
                    'fade_out': constants.FADE_OUT_DURATION
                }),
                'video': settings.get('video', {
                    'fps': constants.FPS,
                    'codec': constants.VIDEO_CODEC,
                    'bitrate': constants.VIDEO_BITRATE
                }),
                'audio': settings.get('audio', {
                    'codec': constants.AUDIO_CODEC,
                    'bitrate': constants.AUDIO_BITRATE,
                    'channels': constants.AUDIO_CHANNELS,
                    'sample_rate': constants.AUDIO_SAMPLE_RATE
                })
            }
        except Exception as e:
            logging.error(f"Error processing video settings: {str(e)}")
            return None

    def get_podcast_data(self, podcast_id: int) -> Optional[Dict]:
        """
        Get podcast data from API
        
        Args:
            podcast_id: ID of the podcast
            
        Returns:
            Optional[Dict]: Podcast data with validated settings if successful, None if failed
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/podcasts/{podcast_id}",
                headers=self.headers
            )
            response.raise_for_status()
            
            data = response.json()
            if not data:
                logging.error("No data received from API")
                return None
                
            podcast_data = data[0] if isinstance(data, list) else data
            
            # Extract podcast and project data
            podcast = podcast_data.get('podcast', {})
            project = podcast_data.get('project', {})
            project_settings = project.get('settings', {})
            
            # Get validated video settings
            video_settings = self.get_video_settings(project_settings)
            if not video_settings:
                return None
                
            return {
                'podcast': podcast,
                'project': {
                    'id': project.get('id'),
                    'name': project.get('name'),
                    'description': project.get('description'),
                    'settings': video_settings
                }
            }
            
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Error processing podcast data: {str(e)}")
            return None

    def download_podcast_audio(self, podcast_data: Dict) -> Optional[Tuple[str, int]]:
        """
        Download podcast audio from Google Drive
        
        Args:
            podcast_data: Dictionary containing podcast information from API
            
        Returns:
            Optional[Tuple[str, int]]: Tuple of (local audio path, podcast ID) if successful, None if failed
        """
        try:
            podcast_id = podcast_data['podcast']['id']
            title = podcast_data['podcast']['title']
            audio_url = podcast_data['podcast']['audioUrl']

            logging.info(f"\nDownloading audio for podcast: {title} (ID: {podcast_id})")
            
            # Extract file ID from Google Drive URL
            audio_file_id = self.drive_utils.get_folder_id_from_url(audio_url)
            download_path = os.path.join(self.temp_dir, f"audio_{podcast_id}.mp3")
            
            logging.info(f"Downloading audio from {audio_url}...")
            if not self.drive_utils.download_file(audio_file_id, download_path):
                logging.error("Failed to download audio file")
                return None
            
            logging.info(f"Successfully downloaded audio to {download_path}")
            logging.info(f"Audio file size: {os.path.getsize(download_path)} bytes")
            
            return download_path, podcast_id

        except Exception as e:
            logging.error(f"Error downloading podcast audio: {str(e)}")
            return None

    def get_notification_emails(self, podcast_data: Dict) -> str:
        """
        Get notification emails from both project and project settings
        
        Args:
            podcast_data: Dictionary containing podcast information
            
        Returns:
            str: Comma-separated list of unique email addresses
        """
        email_set = set()
        
        # Get emails from project root level
        project = podcast_data.get('project', {})
        project_emails = project.get('notification_emails', '')
        if project_emails:
            emails = project_emails.split(',')
            email_set.update(email.strip() for email in emails if email.strip())
            
        # Get emails from project settings
        settings = project.get('settings', {})
        settings_emails = settings.get('notification_emails', '')
        if settings_emails:
            emails = settings_emails.split(',')
            email_set.update(email.strip() for email in emails if email.strip())
            
        if email_set:
            logging.info(f"Found notification emails: {', '.join(email_set)}")
        else:
            logging.warning("No notification emails found in project or settings")
            
        return ','.join(email_set)

    def send_video_upload_notification(self, video_title: str, video_url: str, recipient_email: str) -> bool:
        """
        Send email notification about video upload
        
        Args:
            video_title: Title of the uploaded video
            video_url: URL of the uploaded video
            recipient_email: Email address to send notification to
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            from .email_utils import EmailSender
            email_sender = EmailSender()
            success = email_sender.send_video_upload_notification(
                video_title=video_title,
                video_url=video_url,
                recipient_email=recipient_email.strip()
            )
            if success:
                logging.info(f"Successfully sent notification email to: {recipient_email}")
            else:
                logging.error(f"Failed to send notification email to: {recipient_email}")
            return success
        except Exception as e:
            logging.error(f"Error sending notification to {recipient_email}: {str(e)}")
            return False

    def upload_podcast_video(self, podcast_data: Dict, video_path: str) -> Optional[Dict]:
        """
        Upload podcast video to Google Drive and update API
        
        Args:
            podcast_data: Dictionary containing podcast information
            video_path: Path to the video file
            
        Returns:
            Optional[Dict]: Response from API if successful, None if failed
        """
        try:
            podcast_id = podcast_data['podcast']['id']
            project_settings = podcast_data['project'].get('settings', {})
            output_folder_url = project_settings.get('outputFolderUrl')
            
            if not output_folder_url:
                logging.error("Output folder URL not found in project settings")
                return None

            if not os.path.exists(video_path):
                logging.error(f"Video file not found: {video_path}")
                return None

            # Upload to Google Drive
            output_folder_id = self.drive_utils.get_folder_id_from_url(output_folder_url)
            logging.info(f"Uploading video to {output_folder_url}...")
            
            new_file_id = self.drive_utils.upload_file(
                file_path=video_path,
                folder_id=output_folder_id,
                new_filename=f"podcast_{podcast_id}_final.mp4"
            )
            
            if not new_file_id:
                logging.error("Failed to upload video")
                return None
            
            logging.info(f"Successfully uploaded video. File ID: {new_file_id}")
            
            # Create video URL
            video_url = f"https://drive.google.com/file/d/{new_file_id}/view"
            
            # Update video URL in database
            response = requests.post(
                f"{self.base_url}/api/background/update-video",
                headers=self.headers,
                json={
                    "podcastId": podcast_id,
                    "driveVideoUrl": video_url
                }
            )
            response.raise_for_status()
            api_response = response.json()
            logging.info(f"Video URL update response: {api_response}")
            
            # Get notification emails and send notifications
            notification_emails = self.get_notification_emails(podcast_data)
            if notification_emails:
                video_title = podcast_data['podcast'].get('title', 'Podcast Video')
                for email in notification_emails.split(','):
                    if email.strip():
                        self.send_video_upload_notification(video_title, video_url, email)
            
            return {
                "message": "Video URL updated successfully",
                "driveVideoUrl": video_url
            }
            
        except Exception as e:
            logging.error(f"Failed to upload podcast video: {str(e)}")
            return None

    def get_pending_podcasts(self) -> Optional[list]:
        """Get list of pending podcasts from API"""
        try:
            response = requests.get(
                f"{self.base_url}/api/background/pending-videos",
                headers=self.headers
            )
            response.raise_for_status()
            
            data = response.json()
            if not data:
                logging.error("No pending podcasts found")
                return None
                
            # Process each podcast to ensure it has required fields
            processed_podcasts = []
            for item in data:
                podcast = item.get('podcast', {})
                project = item.get('project', {})
                
                if not podcast or not project:
                    logging.error("Invalid podcast data structure")
                    continue
                    
                processed_podcast = {
                    'podcast': {
                        'id': podcast.get('id'),
                        'title': podcast.get('title', ''),
                        'subtitle': podcast.get('subtitle', ''),
                        'description': podcast.get('description', ''),
                        'audioUrl': podcast.get('audioUrl', ''),
                        'duration': podcast.get('duration'),
                        'youtubeUrl': podcast.get('youtubeUrl'),
                        'spotifyUrl': podcast.get('spotifyUrl'),
                        'linkedinUrl': podcast.get('linkedinUrl'),
                        'createdAt': podcast.get('createdAt')
                    },
                    'project': {
                        'id': project.get('id'),
                        'name': project.get('name', ''),
                        'description': project.get('description', ''),
                        'settings': project.get('settings', {})
                    }
                }
                processed_podcasts.append(processed_podcast)
                
            return processed_podcasts
            
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Error processing pending podcasts: {str(e)}")
            return None

    def update_podcast_status(self, podcast_id: int, video_url: str, notification_emails: str = None) -> bool:
        """
        Update podcast status with video URL and send notifications
        
        Args:
            podcast_id: ID of the podcast
            video_url: URL of the uploaded video
            notification_emails: Comma-separated list of email addresses
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Update podcast status with video URL
            response = requests.post(
                f"{self.base_url}/api/background/update-video",
                headers=self.headers,
                json={
                    "podcastId": podcast_id,
                    "driveVideoUrl": video_url
                }
            )
            response.raise_for_status()
            api_response = response.json()
            logging.info(f"Video URL update response: {api_response}")
            
            # Send email notifications if emails are provided
            if notification_emails:
                from .email_utils import EmailSender
                email_sender = EmailSender()
                podcast_data = self.get_podcast_data(podcast_id)
                
                if podcast_data:
                    video_title = podcast_data['podcast']['title']
                    for email in notification_emails.split(','):
                        email = email.strip()
                        if email:
                            try:
                                success = email_sender.send_video_upload_notification(
                                    video_title=video_title,
                                    video_url=video_url,
                                    recipient_email=email
                                )
                                if success:
                                    logging.info(f"Successfully sent notification email to: {email}")
                                else:
                                    logging.error(f"Failed to send notification email to: {email}")
                            except Exception as e:
                                logging.error(f"Error sending notification to {email}: {str(e)}")
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to update podcast status: {str(e)}")
            return False
