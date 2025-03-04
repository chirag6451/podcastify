from typing import Optional, List
import os
from googleapiclient.http import MediaFileUpload
from video_creator.db_utils import VideoDB

class YouTubePublisher:
    def __init__(self, credentials):
        self.youtube = build('youtube', 'v3', credentials=credentials)
        self.video_db = VideoDB()

    def upload_video_with_thumbnails(
        self, 
        video_path: str,
        title: str,
        description: str,
        job_id: int,
        privacy_status: str = "private"
    ) -> Optional[str]:
        """Upload video and custom thumbnail to YouTube"""
        try:
            # First upload the video
            video_id = self.upload_video(
                video_path=video_path,
                title=title,
                description=description,
                privacy_status=privacy_status
            )
            
            if not video_id:
                raise Exception("Failed to upload video")

            # Get thumbnail paths from database
            thumbnail_paths = self.video_db.get_thumbnail_paths(job_id)
            
            if thumbnail_paths:
                # Upload the first thumbnail
                self.set_custom_thumbnail(video_id, thumbnail_paths[0])
                logger.info(f"Set custom thumbnail for video {video_id}")
            
            return video_id

        except Exception as e:
            logger.error(f"Error uploading video with thumbnail: {str(e)}")
            raise

    def set_custom_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Set custom thumbnail for a YouTube video"""
        try:
            if not os.path.exists(thumbnail_path):
                raise FileNotFoundError(f"Thumbnail file not found: {thumbnail_path}")

            media = MediaFileUpload(
                thumbnail_path,
                mimetype='image/jpeg',
                resumable=True
            )

            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=media
            ).execute()

            return True

        except Exception as e:
            logger.error(f"Error setting custom thumbnail: {str(e)}")
            return False 