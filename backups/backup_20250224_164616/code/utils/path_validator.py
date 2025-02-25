import os
import logging
from typing import Dict, Any
from config import (
    DEFAULT_BG_MUSIC,
    DEFAULT_LOGO,
    DEFAULT_WATERMARK,
    DEFAULT_BACKGROUND_VIDEO,
    DEFAULT_SPEAKER1_VIDEO,
    DEFAULT_SPEAKER2_VIDEO,
    DEFAULT_BACKGROUND_IMAGE,
    STATIC_AUDIO_PATH,
    STATIC_WELCOME_PATH,
    STATIC_SCHEMA_PATH
)

logger = logging.getLogger(__name__)

# Mapping of config keys to their default values
DEFAULT_PATHS = {
    'background_music_path': DEFAULT_BG_MUSIC,
    'logo_settings_main_logo_path': DEFAULT_LOGO,
    'logo_settings_watermark_logo_path': DEFAULT_WATERMARK,
    'background_video_path': DEFAULT_BACKGROUND_VIDEO,
    'speaker1_video_path': DEFAULT_SPEAKER1_VIDEO,
    'speaker2_video_path': DEFAULT_SPEAKER2_VIDEO,
    'background_image_path': DEFAULT_BACKGROUND_IMAGE,
    'static_audio_path': STATIC_AUDIO_PATH,
    'static_welcome_path': STATIC_WELCOME_PATH,
    'static_schema_path': STATIC_SCHEMA_PATH
}

def validate_and_fix_paths(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates all file paths in the config and replaces invalid paths with defaults.
    
    Args:
        config: Dictionary containing configuration with file paths
        
    Returns:
        Updated config with validated paths
    """
    for key, default_path in DEFAULT_PATHS.items():
        if key in config:
            path = config[key]
            if not path or not os.path.exists(path):
                logger.warning(f"Invalid or missing path for {key}: {path}. Using default: {default_path}")
                config[key] = default_path
            else:
                logger.debug(f"Valid path found for {key}: {path}")
    
    return config
