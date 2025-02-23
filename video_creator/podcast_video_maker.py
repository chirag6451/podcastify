from typing import Optional, Tuple, List
import os
from .podcast_video_creator import PodcastVideoCreator

# Get the package root directory
PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))

class PodcastVideoMaker:
    """Simple interface to create podcast videos"""
    
    def __init__(self):
        self._creator = PodcastVideoCreator()
    
    def create_video(self, config, audio_path: str, welcome_audio_path: str, job_id: str,request_dict: dict) -> Tuple[str, Optional[List[str]]]:
        """
        Create a podcast video with the given configuration.
        
        Args:
            config: Configuration dictionary containing video settings
            audio_path: Path to the audio file
            job_id: Job ID for tracking
            
        Returns:
            Tuple containing:
                - Path to the output video file
                - List of paths to thumbnail images (if any)
        """
        # Ensure output directory exists
        os.makedirs(config['output_dir'], exist_ok=True)
       
        
        # Create the video using PodcastVideoCreator
        
        output_path = self._creator.create_video(
            audio_path=audio_path,
            welcome_audio_path=welcome_audio_path,
            config=config,
            job_id=job_id,
            request_dict=request_dict
        )
        
        # Get thumbnail paths from the output directory
        thumbnail_dir = os.path.join(config['output_dir'], "thumbnails")
        thumbnail_paths = None
        if config['create_thumbnails'] and os.path.exists(thumbnail_dir):
            thumbnail_paths = [os.path.join(thumbnail_dir, f) for f in os.listdir(thumbnail_dir) if f.endswith('.jpg')]
        
        return output_path, thumbnail_paths

def create_podcast_video(
    audio_path: str,
    welcome_audio_path: str,
    config: dict,
    job_id: str,
    request_dict: dict = None
) -> Tuple[str, Optional[List[str]]]:
    """
    Create a podcast video with the given configuration.
    
    Args:
        audio_path: Path to the audio file
        welcome_audio_path: Path to the welcome audio file
        config: Configuration dictionary containing video settings
        job_id: Job ID for tracking
        request_dict: Optional dictionary containing request parameters
        
    Returns:
        Tuple containing:
            - Path to the output video file
            - List of paths to thumbnail images (if any)
    """
    maker = PodcastVideoMaker()
    return maker.create_video(
        config=config,
        audio_path=audio_path,
        welcome_audio_path=welcome_audio_path,
        job_id=job_id,
        request_dict=request_dict or {}
    )