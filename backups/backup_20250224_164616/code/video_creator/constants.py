# Video dimensions
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

# Video processing settings
TEMP_AUDIO_BITRATE = "320k"  # Higher bitrate for temp processing
VIDEO_PRESET = "medium"  # Encoding preset (ultrafast to veryslow)
VIDEO_THREADS = 4  # Number of threads for video processing

# Audio settings
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHANNELS = 2
AUDIO_NORMALIZE = True  # Whether to normalize audio levels
BG_MUSIC_VOLUME = 0.1  # Background music volume (0.0 to 1.0)

# Default durations (in seconds)
DEFAULT_INTRO_DURATION = 3      # Shorter intro to grab attention
DEFAULT_SHORT_DURATION = 15     # Short clip for social media
DEFAULT_BRIEF_DURATION = 5      # Brief overview video
DEFAULT_OUTRO_DURATION = 3      # Shorter outro to maintain engagement

# Fade effects duration (in seconds)
FADE_IN_DURATION = 0.5         # Duration of fade in effect
FADE_OUT_DURATION = 1.0        # Duration of fade out effect
AUDIO_FADE_DURATION = 2.0      # Duration of audio fade effects

# Video quality settings
VIDEO_BITRATE = "8000k"
VIDEO_CODEC = "libx264"
AUDIO_BITRATE = "192k"
AUDIO_CODEC = "aac"

# Frame rate
FPS = 30

# Color settings
BACKGROUND_COLOR = (0, 0, 0)  # Black
TEXT_PRIMARY_COLOR = "white"
TEXT_SECONDARY_COLOR = "#CCCCCC"
OVERLAY_COLOR = (0, 0, 0, 0.7)  # Semi-transparent black

# Text settings
HEADING_FONT = "Arial-Bold"
SUBHEADING_FONT = "Arial"
FOOTER_FONT = "Arial"

HEADING_SIZE = 80
SUBHEADING_SIZE = 60
FOOTER_SIZE = 40

HEADING_COLOR = TEXT_PRIMARY_COLOR
SUBHEADING_COLOR = TEXT_SECONDARY_COLOR
FOOTER_COLOR = TEXT_PRIMARY_COLOR

# Podcast content settings
PODCAST_TITLE = "TechTalk Insights"
PODCAST_SUBTITLE = "Exploring the Future of Technology"
SHORT_VIDEO_TITLE = "Quick Highlight"
SHORT_VIDEO_SUBTITLE = "Stay tuned for the full episode!"
PODCAST_FOOTER = "Subscribe • Like • Share"

# Logo settings
DEFAULT_LOGO_WIDTH = 150  # Increased for better visibility
DEFAULT_LOGO_HEIGHT = 150
LOGO_POSITION = ("center", 50)  # (x, y) position for logo

# Default paths and sources
DEFAULT_VIDEOS_DIR = "videos"  # Directory containing background videos
DEFAULT_INTRO_VIDEO = "intro_extro/intro7.mp4"
DEFAULT_OUTRO_VIDEO = "intro_extro/extro.mp4"
DEFAULT_LOGO_PATH = "images/logo.png"
DEFAULT_BG_MUSIC = "bgmusic/s3.mp3"

# Output paths
OUTPUT_DIR = "output"
FINAL_VIDEO_PATH = f"{OUTPUT_DIR}/final_video.mp4"
INTRO_VIDEO_PATH = f"{OUTPUT_DIR}/intro_video.mp4"
OUTRO_VIDEO_PATH = f"{OUTPUT_DIR}/outro_video.mp4"
BRIEF_VIDEO_PATH = f"{OUTPUT_DIR}/brief_video.mp4"
SHORT_VIDEO_PATH = f"{OUTPUT_DIR}/short_video.mp4"
PODCAST_VIDEO_PATH = f"{OUTPUT_DIR}/podcast_video.mp4"

# Text positions (y-coordinates)
HEADING_Y_POS = 200
SUBHEADING_Y_POS = 300
FOOTER_Y_POS = 900  # Added footer position

# Video margins and padding
VIDEO_MARGIN = 50  # Margin from edges
TEXT_PADDING = 20  # Padding between text elements

# Cleanup Settings
CLEANUP_LOCAL_VIDEOS = False

# Ensure output directory exists
import os
os.makedirs(OUTPUT_DIR, exist_ok=True)
