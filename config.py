"""Global configuration settings for the podcast generation system"""
from asyncore import ExitNow
import os
from pathlib import Path
import traceback
from dotenv import load_dotenv

load_dotenv()
# Get package root directory
PACKAGE_ROOT = str(Path(__file__).parent)

# Directory paths
OUTPUTS_DIR = os.path.join(PACKAGE_ROOT, "outputs")
PROFILES_DIR = os.path.join(PACKAGE_ROOT, "profiles")
LOGS_DIR = os.path.join(PACKAGE_ROOT, "logs")
TEMP_DIR = os.path.join(PACKAGE_ROOT, "temp")

# Default paths
DEFAULT_ASSETS_FOLDER = os.path.join(PACKAGE_ROOT, "defaults")
DEFAULT_BGMUSIC_PATH = os.path.join(DEFAULT_ASSETS_FOLDER, "bgmusic")
DEFAULT_IMAGES_PATH = os.path.join(DEFAULT_ASSETS_FOLDER, "images")
DEFAULT_BG_IMAGES_PATH = os.path.join(DEFAULT_ASSETS_FOLDER, "bgimages")
DEFAULT_VIDEOS_PATH = os.path.join(DEFAULT_ASSETS_FOLDER, "videos")
DEFAULT_FONTS_PATH = os.path.join(DEFAULT_ASSETS_FOLDER, "fonts")
DEFAULT_VOICEOVER_PATH = os.path.join(DEFAULT_ASSETS_FOLDER, "voiceover")
DEFAULT_AUDIO_PATH = os.path.join(DEFAULT_ASSETS_FOLDER, "audio")
DEFAULT_SPEAKERS_PATH = os.path.join(DEFAULT_ASSETS_FOLDER, "speakers")

# Static audio paths
STATIC_AUDIO_PATH = os.path.join(DEFAULT_VOICEOVER_PATH, "final_mix.mp3")
STATIC_WELCOME_PATH = os.path.join(DEFAULT_VOICEOVER_PATH, "welcome.mp3")
STATIC_SCHEMA_PATH = os.path.join(DEFAULT_AUDIO_PATH, "conversation.json")
DEFAULT_INTRO_PATH = os.path.join(DEFAULT_ASSETS_FOLDER, "intro.mp4")
DEFAULT_OUTRO_PATH = os.path.join(DEFAULT_ASSETS_FOLDER, "outro.mp4")
# Default media files
DEFAULT_BG_MUSIC = os.path.join(DEFAULT_BGMUSIC_PATH, "s3.mp3")
DEFAULT_LOGO = os.path.join(DEFAULT_IMAGES_PATH, "logo.png")
DEFAULT_WATERMARK = os.path.join(DEFAULT_IMAGES_PATH, "watermark.png")
DEFAULT_BACKGROUND_VIDEO = os.path.join(DEFAULT_VIDEOS_PATH, "1_optimized.mp4")
DEFAULT_BACKGROUND_IMAGE = os.path.join(DEFAULT_BG_IMAGES_PATH, "bg1.jpeg")
DEFAULT_SPEAKER1_VIDEO = os.path.join(DEFAULT_SPEAKERS_PATH, "g1.mp4")
DEFAULT_SPEAKER2_VIDEO = os.path.join(DEFAULT_SPEAKERS_PATH, "m1.mp4")

# Video settings
VIDEO_SETTINGS = {
    "resolution": (1920, 1080),
    "fps": 30,
    "video_codec": "libx264",
    "audio_codec": "aac",
    "video_bitrate": "8000k",
    "audio_bitrate": "192k",
    "threads": 4,
    "preset": "medium"
}

# Font settings
FONT_SETTINGS = {
    "title": {
        "size": 60,
        "color": "#EBE0E2",
        "name": "Helvetica-Bold"
    },
    "subtitle": {
        "size": 40,
        "color": "#eab676",
        "name": "Helvetica"
    },
    "footer": {
        "size": 30,
        "color": "#eeeee4",
        "name": "Helvetica"
    }
}

# Audio settings
AUDIO_SETTINGS = {
    "sample_rate": 44100,
    "channels": 2,
    "normalize": True,
    "bg_music_volume": 0.1
}

# Error handling settings
def get_debug_mode():
    """Get debug mode from environment, with proper type conversion"""
    debug_env = os.getenv('DEBUG_MODE', 'false')
    return debug_env.lower() in ('true', '1', 'yes', 'on')

DEBUG_MODE = get_debug_mode()


def get_error_detail(error: Exception, include_traceback: bool = None, context: str = None) -> dict:
    """Get error details based on debug mode
    Args:
        error: The exception that occurred
        include_traceback: Override DEBUG_MODE setting. If None, uses DEBUG_MODE
        context: Optional context string (e.g. "creating podcast", "job 123")
    """
    if include_traceback is None:
        include_traceback = DEBUG_MODE
        
    # Basic error info for non-debug mode
    if not include_traceback:
        return {"error": str(error)}
    
    # Detailed error info for debug mode
    try:
        tb_list = traceback.extract_tb(error.__traceback__)
        error_frames = []
        
        for frame in tb_list:
            frame_info = {
                "file": os.path.basename(str(frame[0])),
                "line": str(frame[1]),
                "function": str(frame[2]),
                "code": str(frame[3])
            }
            error_frames.append(frame_info)
        
        error_info = {
            "error": str(error),
            "traceback": error_frames,
            "current_frame": error_frames[-1] if error_frames else {},
            "full_traceback": traceback.format_exc()
        }
        
        if context:
            error_info["context"] = context
            
        return error_info
    except Exception as e:
        # Fallback if we can't get traceback info
        return {
            "error": str(error),
            "meta_error": f"Error getting traceback: {str(e)}",
            "full_traceback": traceback.format_exc()
        }

def format_error_message(error_detail: dict) -> str:
    """Format error message for logging"""
    # Handle case where error_detail is a tuple
    if isinstance(error_detail, tuple):
        return f"Error - {str(error_detail[0])}"
        
    if not isinstance(error_detail, dict):
        return f"Error - {str(error_detail)}"
    
    if len(error_detail) == 1:  # Non-debug mode
        return f"Error - {error_detail.get('error', 'Unknown error')}"
        
    # Format detailed error message
    current_frame = error_detail.get('current_frame', {})
    error_location = f"{current_frame.get('file', 'unknown')}:{current_frame.get('line', '?')}"
    
    if error_detail.get('context'):
        error_location = f"{error_location} ({error_detail['context']})"
    
    error_msg = f"Error in {error_location} - {error_detail.get('error', 'Unknown error')}"
    
    if error_detail.get('traceback'):
        error_msg += "\nTraceback:"
        for frame in error_detail['traceback']:
            error_msg += f"\n  File {frame['file']}, line {frame['line']}, in {frame['function']}"
            error_msg += f"\n    {frame['code']}"
    
    return error_msg

# Create required directories
for directory in [OUTPUTS_DIR, LOGS_DIR, TEMP_DIR, DEFAULT_ASSETS_FOLDER, DEFAULT_BGMUSIC_PATH, DEFAULT_IMAGES_PATH, DEFAULT_VIDEOS_PATH, DEFAULT_FONTS_PATH, DEFAULT_VOICEOVER_PATH, DEFAULT_AUDIO_PATH, DEFAULT_SPEAKERS_PATH]:
    os.makedirs(directory, exist_ok=True)

# Environment settings
ENV_SETTINGS = {
    "dev_mode": os.getenv("DEV_MODE", "false").lower() == "true",
    "static_audio": os.getenv("STATIC_AUDIO", "false").lower() == "true",
    "celery_process": os.getenv("CELERY_PROCESS", "false").lower() == "true",
    "openai_model": os.getenv("OPENAI_MODEL", "gpt-4-0125-preview")
}

# Default profile settings
DEFAULT_PROFILE = {
    "voice_settings": {
        "language": "English",
        "voice_accent": "Indian",
        "welcome_voice_id": "cgSgspJ2msm6clMCkdW9",
        "voice_id1": "cgSgspJ2msm6clMCkdW9",
        "voice_id2": "iP95p4xoKVk53GoZ742B",
        "speaker1_name": "Jessica",
        "speaker2_name": "Ken"
    },
    "default_settings": {
        "num_turns": 5,
        "conversation_mood": "explaining in simple terms"
    }
} 