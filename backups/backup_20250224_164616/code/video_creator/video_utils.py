import os
import logging
import colorlog
import random
import glob
import time
from typing import Dict, Optional, List

from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip,
    TextClip, CompositeVideoClip, ColorClip,
    CompositeAudioClip, vfx, concatenate_videoclips
)
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.audio.fx.audio_loop import audio_loop

import constants
from podcast_video import PodcastVideoCreator
from intro import create_brief_video
from random_clip import PodcastShortsCreator

def setup_logger():
    """Set up colored logging configuration"""
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s %(levelname)-8s%(reset)s %(blue)s%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        }
    ))

    logger = colorlog.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)  # Set to INFO to avoid debug messages
    
    # Remove any existing handlers to avoid duplicate logs
    for old_handler in logger.handlers[:-1]:
        logger.removeHandler(old_handler)
    
    return logger

# Initialize logger
logger = setup_logger()

def add_fade_effects(clip, fade_in=True, fade_out=True):
    """Add fade in and fade out effects to video clip"""
    duration = clip.duration
    
    if fade_in:
        clip = clip.fadein(constants.FADE_IN_DURATION)
    if fade_out:
        clip = clip.fadeout(constants.FADE_OUT_DURATION)
        
    # Add audio fades if clip has audio
    if clip.audio is not None:
        if fade_in:
            clip.audio = clip.audio.audio_fadein(constants.FADE_IN_DURATION)
        if fade_out:
            clip.audio = clip.audio.audio_fadeout(constants.FADE_OUT_DURATION)
    
    return clip

def get_random_video(videos_path: str) -> str:
    """Get a random video from the specified directory"""
    try:
        if not os.path.isdir(videos_path):
            raise ValueError(f"Videos directory not found: {videos_path}")
            
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        video_files = []
        
        for ext in video_extensions:
            video_files.extend(glob.glob(os.path.join(videos_path, f"*{ext}")))
        
        if not video_files:
            raise ValueError(f"No video files found in {videos_path}")
        
        selected_video = random.choice(video_files)
        logger.info(f"Selected random video: {selected_video}")
        return selected_video
        
    except Exception as e:
        logger.error(f"Error selecting random video: {str(e)}")
        raise

class VideoCreator:
    def __init__(self):
        """Initialize VideoCreator with default paths and settings"""
        self.api_settings = {}  # Initialize empty api_settings
        
        self.default_paths = {
            "bg_music": constants.DEFAULT_BG_MUSIC,
            "logo": constants.DEFAULT_LOGO_PATH,
            "intro_video": constants.DEFAULT_INTRO_VIDEO,
            "outro_video": constants.DEFAULT_OUTRO_VIDEO,
            "output_dir": constants.OUTPUT_DIR,
            "videos_dir": 'videos'
        }
        
        self.text_settings = {
            "fonts": {},
            "sizes": {},
            "content": {},
            "positions": {}
        }
        
        self.duration_settings = {
            "intro": constants.DEFAULT_INTRO_DURATION,
            "short": constants.DEFAULT_SHORT_DURATION,
            "brief": constants.DEFAULT_BRIEF_DURATION,
            "outro": constants.DEFAULT_OUTRO_DURATION,
            "fade_in": 0.5,
            "fade_out": 0.5
        }
        
        self.video_settings = {
            "fps": 30,
            "codec": "libx264",
            "bitrate": "2000k"
        }
        
        self.audio_settings = {
            "codec": "aac",
            "bitrate": "192k",
            "channels": 2,
            "sample_rate": 44100
        }
        
        self.color_settings = {
            "overlay": [0, 0, 0, 0.7],
            "background": [0, 0, 0],
            "text_primary": "white",
            "text_secondary": "#CCCCCC"
        }
        
        self.dimension_settings = {
            "width": 1920,
            "height": 1080
        }
        
        self.logo_settings = {
            "width": constants.DEFAULT_LOGO_WIDTH,
            "height": constants.DEFAULT_LOGO_HEIGHT
        }

        # Create output directory if it doesn't exist
        os.makedirs(self.default_paths["output_dir"], exist_ok=True)

    def validate_path(self, path: str, default_path: str) -> str:
        """Validate if a path exists, return default if not"""
        print(f"Validating path: {path}, default: {default_path}")
        if not path:
            logger.warning(f"⚠️  No path provided in API settings, using default: {default_path}")
            if not os.path.exists(default_path):
                logger.error(f"❌ Default path {default_path} not found!")
                raise ValueError(f"Default path does not exist: {default_path}")
            return default_path

        # Remove leading slash if present
        if path.startswith('/'):
            path = path[1:]

        # List of possible base paths to try
        base_paths = [
            os.path.dirname(os.path.dirname(__file__)),  # podcast root directory
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'videos'),
            self.api_settings.get('videoSettings', {}).get('paths', {}).get('videos_dir', '')
        ]

        # Try all possible path combinations
        possible_paths = []
        for base in base_paths:
            if base:
                possible_paths.extend([
                    path,  # Try as is
                    os.path.join(base, path),  # Try with base path
                    os.path.normpath(os.path.join(base, path))  # Try normalized path
                ])

        # Remove duplicates while preserving order
        possible_paths = list(dict.fromkeys(possible_paths))

        logger.debug(f"🔍 Trying paths for {path}:")
        for try_path in possible_paths:
            logger.debug(f"   Checking: {try_path}")
            if os.path.exists(try_path):
                logger.info(f"✅ Found valid path: {try_path}")
                return try_path

        # If we get here, no valid path was found
        logger.warning(f"⚠️  No valid path found for {path}, using default: {default_path}")
        if not os.path.exists(default_path):
            logger.error(f"❌ Default path {default_path} not found!")
            raise ValueError(f"Neither provided path nor default path exists: {path} / {default_path}")
        return default_path

    def update_settings(self, settings: dict):
        """Update video settings from API response"""
        if not settings:
            return

        # Store original API settings for reference
        self.api_settings = settings

        # Update paths
        paths = settings.get("paths", {})
        for key, value in paths.items():
            if key in self.default_paths:
                self.default_paths[key] = self.validate_path(value, self.default_paths[key])

        # Update text settings
        text_settings = settings.get("text", {})
        if text_settings:
            # Update fonts
            self.text_settings["fonts"] = text_settings.get("fonts", {})
            
            # Update sizes
            self.text_settings["sizes"] = text_settings.get("sizes", {})
            
            # Update content (heading, subheading, footer)
            content = text_settings.get("content", {})
            self.text_settings["content"] = {
                "heading": content.get("heading", constants.DEFAULT_HEADING),
                "subheading": content.get("subheading", constants.DEFAULT_SUBHEADING),
                "footer": content.get("footer", constants.DEFAULT_FOOTER)
            }
            
            # Update positions
            self.text_settings["positions"] = text_settings.get("positions", {})

        # Update duration settings
        if 'durations' in settings:
            durations = settings['durations']
            self.duration_settings.update({
                "intro": durations.get('intro', constants.DEFAULT_INTRO_DURATION),
                "short": durations.get('short', constants.DEFAULT_SHORT_DURATION),
                "brief": durations.get('brief', constants.DEFAULT_BRIEF_DURATION),
                "outro": durations.get('outro', constants.DEFAULT_OUTRO_DURATION),
                "fade_in": durations.get('fade_in', 0.5),
                "fade_out": durations.get('fade_out', 0.5)
            })
            logger.info("✅ Updated duration settings from API")

        # Update video encoding settings
        if 'video' in settings:
            video = settings['video']
            self.video_settings.update({
                "fps": video.get('fps', 30),
                "codec": video.get('codec', 'libx264'),
                "bitrate": video.get('bitrate', '2000k')
            })
            logger.info("✅ Updated video encoding settings from API")

        # Update audio settings
        if 'audio' in settings:
            audio = settings['audio']
            self.audio_settings.update({
                "codec": audio.get('codec', 'aac'),
                "bitrate": audio.get('bitrate', '192k'),
                "channels": audio.get('channels', 2),
                "sample_rate": audio.get('sample_rate', 44100)
            })
            logger.info("✅ Updated audio settings from API")

        # Update color settings
        if 'colors' in settings:
            self.color_settings = settings['colors']
            logger.info("✅ Updated color settings from API")

        # Update dimension settings
        if 'dimensions' in settings:
            self.dimension_settings = settings['dimensions']
            logger.info("✅ Updated dimension settings from API")

        # Update logo settings
        if 'logo' in settings:
            self.logo_settings = settings['logo']
            logger.info("✅ Updated logo settings from API")

        # Log final settings
        self.print_settings_summary()

    def print_settings_summary(self):
        """Print a comprehensive summary of all settings and their sources"""
        logger.info("\n📊 SETTINGS VALIDATION SUMMARY")
        logger.info("=" * 60)

        # Path Settings Summary
        logger.info("\n🗂️  PATH SETTINGS VALIDATION")
        logger.info("-" * 60)
        path_settings = {
            "Background Music": ("bg_music", constants.DEFAULT_BG_MUSIC),
            "Logo": ("logo", constants.DEFAULT_LOGO_PATH),
            "Intro Video": ("intro_video", constants.DEFAULT_INTRO_VIDEO),
            "Outro Video": ("outro_video", constants.DEFAULT_OUTRO_VIDEO),
            "Output Directory": ("output_dir", constants.OUTPUT_DIR),
            "Videos Directory": ("videos_dir", 'videos')
        }

        for display_name, (key, default) in path_settings.items():
            current = self.default_paths.get(key)
            api_value = self.api_settings.get('paths', {}).get(key)
            
            logger.info(f"\n📁 {display_name}:")
            logger.info(f"  API Setting: {api_value if api_value else 'Not provided'}")
            logger.info(f"  Default: {default}")
            logger.info(f"  Final Used: {current}")
            logger.info(f"  Source: {'API' if current == api_value else 'Default'}")
            logger.info(f"  Status: {'✅ File exists' if os.path.exists(current) else '❌ File not found'}")

        # Text Settings Summary
        logger.info("\n📝 TEXT SETTINGS VALIDATION")
        logger.info("-" * 60)
        text_settings = {
            "Fonts": ("fonts", {}),
            "Sizes": ("sizes", {}),
            "Content": ("content", {}),
            "Positions": ("positions", {})
        }

        for display_name, (key, default) in text_settings.items():
            current = self.text_settings.get(key)
            api_value = self.api_settings.get('text', {}).get(key)
            
            logger.info(f"\n✍️ {display_name}:")
            logger.info(f"  API Setting: {api_value if api_value else 'Not provided'}")
            logger.info(f"  Default: {default}")
            logger.info(f"  Final Used: {current}")
            logger.info(f"  Source: {'API' if current == api_value else 'Default'}")

        # Duration Settings Summary
        logger.info("\n⏱️  DURATION SETTINGS VALIDATION")
        logger.info("-" * 60)
        duration_settings = {
            "Intro Duration": ("intro", constants.DEFAULT_INTRO_DURATION),
            "Short Duration": ("short", constants.DEFAULT_SHORT_DURATION),
            "Brief Duration": ("brief", constants.DEFAULT_BRIEF_DURATION),
            "Outro Duration": ("outro", constants.DEFAULT_OUTRO_DURATION)
        }

        for display_name, (key, default) in duration_settings.items():
            current = self.duration_settings.get(key)
            api_value = self.api_settings.get('durations', {}).get(key)
            
            logger.info(f"\n⌛ {display_name}:")
            logger.info(f"  API Setting: {api_value if api_value else 'Not provided'}")
            logger.info(f"  Default: {default}")
            logger.info(f"  Final Used: {current}")
            logger.info(f"  Source: {'API' if current == api_value else 'Default'}")

        # Video Source Settings
        logger.info("\n🎬 VIDEO SOURCE SETTINGS")
        logger.info("-" * 60)
        logger.info(f"Source Videos Path: {self.default_paths.get('videos_dir', 'videos/')}")
        if hasattr(self, 'source_videos_path'):
            videos = glob.glob(os.path.join(self.source_videos_path, "*.mp4"))
            logger.info(f"Number of source videos found: {len(videos)}")
            logger.info("Video files:")
            for video in videos[:5]:  # Show first 5 videos
                logger.info(f"  - {os.path.basename(video)}")
            if len(videos) > 5:
                logger.info(f"  ... and {len(videos) - 5} more videos")

        # Summary of Potential Issues
        logger.info("\n⚠️  POTENTIAL ISSUES")
        logger.info("-" * 60)
        issues = []
        
        # Check path existence
        for name, (key, _) in path_settings.items():
            path = self.default_paths.get(key)
            if not os.path.exists(path):
                issues.append(f"❌ {name} file not found at: {path}")

        # Check duration values
        for name, (key, default) in duration_settings.items():
            duration = self.duration_settings.get(key)
            if duration <= 0:
                issues.append(f"❌ Invalid {name}: {duration}s")

        # Check text settings
        for name, (key, default) in text_settings.items():
            text = self.text_settings.get(key)
            if not text:
                issues.append(f"⚠️ Empty {name}")

        if issues:
            for issue in issues:
                logger.warning(issue)
        else:
            logger.info("✅ No potential issues found")

        logger.info("\n" + "=" * 60)

    def create_video(self, audio_path: str) -> Optional[str]:
        """Create video from audio file"""
        try:
            # Validate audio path
            if not os.path.exists(audio_path):
                logger.error("❌ Audio file not found!")
                return None
                
            # Print settings summary before starting video creation
            logger.info("\n🎥 STARTING VIDEO CREATION")
            logger.info("=" * 60)
            logger.info(f"Audio File: {audio_path}")
            logger.info(f"File exists: {'✅' if os.path.exists(audio_path) else '❌'}")
            logger.info(f"File size: {os.path.getsize(audio_path) / (1024*1024):.2f} MB")
            
            # Load audio file and get its duration
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            logger.info(f"🎵 Audio Duration: {audio_duration:.2f} seconds")
            
            # Initialize all clips as None for proper cleanup
            intro_video_clip = None
            short_clip = None
            brief_video = None
            podcast_video_clip = None
            outro_video_clip = None
            final_video = None
            
            # 1. Get intro video
            intro_path = self.default_paths["intro_video"]
            logger.info("\n1️⃣  Using intro video...")
            logger.info(f"   Path: {intro_path}")
            if not os.path.exists(intro_path):
                logger.error(f"❌ Intro video not found at: {intro_path}")
                return None
            intro_video_clip = VideoFileClip(intro_path)
            intro_video_clip = add_fade_effects(intro_video_clip)
            logger.info(f"✅ Intro video loaded: {intro_video_clip.duration:.2f}s")

            # 2. Create short video clip (with duration limit)
            short_path = os.path.join(self.default_paths["output_dir"], "short_video.mp4")
            logger.info("\n2️⃣  Creating short video clip...")
            short_creator = PodcastShortsCreator(
                source_videos_path=self.default_paths["videos_dir"],
                background_music_path=self.default_paths["bg_music"],
                voiceover_path=audio_path,  
                logo_path=self.default_paths["logo"],
                clip_duration=self.duration_settings.get("short", constants.DEFAULT_SHORT_DURATION),
                logo_width=self.logo_settings.get("width", 150),
                logo_height=self.logo_settings.get("height", 150),
                bg_music_volume=7.0,
                footer_text=self.text_settings.get("content", {}).get("footer", "Follow us on social media • Subscribe to our channel"),
                output_path=short_path
            )
            short_creator.create_short()
            short_clip = VideoFileClip(short_path)
            short_clip = add_fade_effects(short_clip)
            logger.info(f"✅ Short clip created: {short_clip.duration:.2f}s")
            
            # 3. Create brief video (with duration limit)
            brief_path = os.path.join(self.default_paths["output_dir"], "brief_video.mp4")
            logger.info("\n3️⃣  Creating brief video...")
            try:
                random_source = get_random_video(self.default_paths["videos_dir"])
                logger.info(f"Using random video for brief: {random_source}")
                brief_video = create_brief_video(
                    source_video_path=random_source,
                    logo_path=self.default_paths["logo"],
                    background_music_path=self.default_paths["bg_music"],
                    output_video_path=brief_path,
                    video_duration=self.duration_settings.get("brief", constants.DEFAULT_BRIEF_DURATION),
                    footer_text=self.text_settings.get("content", {}).get("footer", constants.DEFAULT_FOOTER)
                )
                if brief_video is not None:
                    brief_video = add_fade_effects(brief_video)
                    logger.info(f"✅ Brief video created: {brief_video.duration:.2f}s")
            except Exception as e:
                logger.error(f"❌ Error creating brief video: {str(e)}")
                brief_video = None
            
            # 4. Create main podcast video (using full audio length)
            podcast_path = os.path.join(self.default_paths["output_dir"], "podcast_video.mp4")
            logger.info("\n4️⃣  Creating main podcast video...")
            logger.info(f"   Full audio duration: {audio_duration:.2f}s")
            podcast_creator = PodcastVideoCreator(
                source_videos_path=self.default_paths["videos_dir"],
                background_music_path=self.default_paths["bg_music"],
                voiceover_path=audio_path,
                logo_path=self.default_paths["logo"],
                logo_width=self.logo_settings.get("width", 150),
                logo_height=self.logo_settings.get("height", 150),
                bg_music_volume=7.0,
                heading_text=self.text_settings.get("content", {}).get("heading", constants.DEFAULT_HEADING),
                subheading_text=self.text_settings.get("content", {}).get("subheading", constants.DEFAULT_SUBHEADING),
                footer_text=self.text_settings.get("content", {}).get("footer", constants.DEFAULT_FOOTER),
                output_path=podcast_path
            )
            podcast_creator.create_video()
            podcast_video_clip = VideoFileClip(podcast_path)
            logger.info(f"✅ Main podcast video created: {podcast_video_clip.duration:.2f}s")
            
            # 5. Get outro video
            outro_path = self.default_paths["outro_video"]
            logger.info("\n5️⃣  Using outro video...")
            logger.info(f"   Path: {outro_path}")
            if not os.path.exists(outro_path):
                logger.error(f"❌ Outro video not found at: {outro_path}")
                return None
            outro_video_clip = VideoFileClip(outro_path)
            outro_video_clip = add_fade_effects(outro_video_clip)
            logger.info(f"✅ Outro video loaded: {outro_video_clip.duration:.2f}s")

            # 6. Combine all videos
            logger.info("\n6️⃣  Combining all videos...")
            
            # Add all clips in sequence
            video_segments = []
            total_duration = 0
            
            if intro_video_clip:
                video_segments.append(intro_video_clip)
                total_duration += intro_video_clip.duration
                logger.info(f"Added intro: {intro_video_clip.duration:.2f}s")
            
            if short_clip:
                video_segments.append(short_clip)
                total_duration += short_clip.duration
                logger.info(f"Added short clip: {short_clip.duration:.2f}s")
            
            if brief_video:
                video_segments.append(brief_video)
                total_duration += brief_video.duration
                logger.info(f"Added brief video: {brief_video.duration:.2f}s")
            
            if podcast_video_clip:
                video_segments.append(podcast_video_clip)
                total_duration += podcast_video_clip.duration
                logger.info(f"Added main podcast: {podcast_video_clip.duration:.2f}s")
            
            if outro_video_clip:
                video_segments.append(outro_video_clip)
                total_duration += outro_video_clip.duration
                logger.info(f"Added outro: {outro_video_clip.duration:.2f}s")
            
            if not video_segments:
                logger.error("❌ No video segments to combine!")
                return None
                
            logger.info(f"\n📊 Final Video Summary:")
            logger.info(f"   Total Duration: {total_duration:.2f}s")
            logger.info(f"   Audio Duration: {audio_duration:.2f}s")
            logger.info(f"   Number of Segments: {len(video_segments)}")
            
            # Concatenate all clips
            final_video = concatenate_videoclips(video_segments)
            
            # Write final video
            output_path = os.path.join(self.default_paths["output_dir"], f"final_video_{int(time.time())}.mp4")
            logger.info(f"\n💾 Writing final video to: {output_path}")
            final_video.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                bitrate="2000k",
                threads=4,
                logger=None
            )
            
            logger.info("✅ Video creation completed successfully!")
            
            # Clean up resources
            logger.info("\nCleaning up resources...")
            try:
                # Close video clips
                intro_video_clip.close()
                short_clip.close()
                if brief_video is not None:
                    brief_video.close()
                podcast_video_clip.close()
                outro_video_clip.close()

                # Delete temporary files if cleanup is enabled
                if constants.CLEANUP_LOCAL_VIDEOS:
                    logger.info("Deleting temporary video files...")
                    os.remove(short_path)
                    if os.path.exists(brief_path):
                        os.remove(brief_path)
                    os.remove(podcast_path)
                else:
                    logger.info("Keeping local video files (CLEANUP_LOCAL_VIDEOS is False)")

                logger.info("Cleanup completed")
            except Exception as e:
                logger.error(f"Error during cleanup: {str(e)}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error creating video: {str(e)}", exc_info=True)
            return None
            
def create_video_from_audio(audio_path: str, settings: Dict = None) -> Optional[str]:
    """
    Convenience function to create a video from an audio file
    
    Args:
        audio_path: Path to the input audio file
        settings: Dictionary containing video settings
        
    Returns:
        Optional[str]: Path to the created video file, or None if creation failed
    """
    try:
        creator = VideoCreator()
        
        # Update settings if provided

        if settings:
            creator.update_settings(settings)
        
        return creator.create_video(audio_path)
    except Exception as e:
        logger.error(f"Error creating video: {str(e)}")
        return None
