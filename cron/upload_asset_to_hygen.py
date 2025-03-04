#!/usr/bin/env python3
import logging
import sys
import os
from typing import Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from video_creator.hygen import HeyGenAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def get_hygen_asset_id(file_path: str) -> Optional[str]:
    """
    Upload a file to Hygen and return its asset ID
    
    Args:
        file_path: Path to the file to upload
        
    Returns:
        str: Asset ID if successful, None otherwise
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
            
        # Initialize Hygen client
        client = HeyGenAPI()
        
        # Upload the asset
        logger.info(f"Uploading asset: {file_path}")
        asset_id = client.upload_asset(file_path)
        
        if asset_id:
            logger.info(f"Successfully uploaded asset. Asset ID: {asset_id}")
            return asset_id
        else:
            logger.error("Failed to get asset ID from upload")
            return None
            
    except Exception as e:
        logger.error(f"Error uploading asset to Hygen: {str(e)}")
        return None
        
if __name__ == "__main__":
    asset_id = get_hygen_asset_id("profiles/indapoint/videos/indapoint_hygen_bg_video.mp4")
    print(asset_id)