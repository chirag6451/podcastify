#!/usr/bin/env python3
"""
Cron script to upload pending videos to YouTube.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.youtube_uploader import YouTubeUploader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to upload pending videos to YouTube."""
    try:
        # Get credentials path from environment or use default
        credentials_path = os.getenv('YOUTUBE_CREDENTIALS_PATH', 
                                   os.path.join(project_root, 'config', 'client_secrets.json'))
        token_path = os.getenv('YOUTUBE_TOKEN_PATH',
                              os.path.join(project_root, 'config', 'youtube_token.json'))
        playlist_id = os.getenv('YOUTUBE_PLAYLIST_ID')
        
        # Initialize uploader
        uploader = YouTubeUploader(credentials_path, token_path)
        
        # Upload pending videos
        logger.info("Starting YouTube upload process")
        uploader.upload_pending_videos(playlist_id)
        logger.info("Finished YouTube upload process")
        
    except Exception as e:
        logger.error(f"Failed to process YouTube uploads: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
