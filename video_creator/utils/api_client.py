import requests
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class APIClient:
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.api_key = os.getenv("API_KEY", "indapoint-secure-key-2024")
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def get_pending_videos(self) -> List[Dict]:
        """
        Get list of pending videos to process
        
        Returns:
            List of pending video objects with their details
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/background/pending-videos",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching pending videos: {str(e)}")
            return []
    
    def update_video_url(self, podcast_id: int, drive_video_url: str) -> bool:
        """
        Update the video URL for a processed podcast
        
        Args:
            podcast_id: ID of the podcast
            drive_video_url: Google Drive URL of the processed video
            
        Returns:
            bool: True if update was successful
        """
        try:
            data = {
                "podcastId": podcast_id,
                "driveVideoUrl": drive_video_url
            }
            response = requests.post(
                f"{self.base_url}/api/background/update-video",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error updating video URL: {str(e)}")
            return False
