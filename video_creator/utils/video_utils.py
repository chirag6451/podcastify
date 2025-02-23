import os
import logging
import colorlog
import random
import glob
import time
from typing import Dict, Optional, List

from moviepy.editor import (
    VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips
)
from moviepy.video.fx.all import fadein, fadeout
from moviepy.audio.fx.all import audio_fadein, audio_fadeout

from video_creator import podcast_video

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
        clip = clip.fadein(0.5)
    if fade_out:
        clip = clip.fadeout(0.5)
        
    # Add audio fades if clip has audio
    if clip.audio is not None:
        if fade_in:
            clip.audio = clip.audio.audio_fadein(0.5)
        if fade_out:
            clip.audio = clip.audio.audio_fadeout(0.5)
    
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
            "bg_music": "default_bg_music.mp3",
            "logo": "default_logo.png",
            "intro_video": "intro_extro/intro7.mp4",
            "outro_video": "intro_extro/outro7.mp4",
            "output_dir": "output",
            "videos_dir": 'videos'
        }
        
        self.text_settings = {
            "fonts": {},
            "sizes": {},
            "content": {},
            "positions": {}
        }
        
        self.duration_settings = {
            "intro": 5,
            "short": 60,
            "brief": 90,
            "outro": 5,
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
            "width": 200,
            "height": 200
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
                "heading": content.get("heading", "AppliView Podcast"),
                "subheading": content.get("subheading", "Tech Insights & Innovation"),
                "footer": content.get("footer", "Follow us on social media • Subscribe to our channel")
            }
            
            # Update positions
            self.text_settings["positions"] = text_settings.get("positions", {})

        # Update duration settings
        if 'durations' in settings:
            durations = settings['durations']
            self.duration_settings.update({
                "intro": durations.get('intro', 5),
                "short": durations.get('short', 60),
                "brief": durations.get('brief', 90),
                "outro": durations.get('outro', 5),
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
            "Background Music": ("bg_music", "default_bg_music.mp3"),
            "Logo": ("logo", "default_logo.png"),
            "Intro Video": ("intro_video", "intro_extro/intro7.mp4"),
            "Outro Video": ("outro_video", "intro_extro/outro7.mp4"),
            "Output Directory": ("output_dir", "output"),
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
            "Intro Duration": ("intro", 5),
            "Short Duration": ("short", 60),
            "Brief Duration": ("brief", 90),
            "Outro Duration": ("outro", 5)
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
            intro_clip = None
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
                clip_duration=self.duration_settings.get("short", 60),
                logo_width=self.logo_settings.get("width", 200),
                logo_height=self.logo_settings.get("height", 200),
                bg_music_volume=0.07,  
                footer_text=self.text_settings.get("content", {}).get("footer", "Follow us on social media • Subscribe to our channel"),
                output_path=short_path
            )
            short_creator.create_short()
            short_clip = VideoFileClip(short_path)
            short_clip = add_fade_effects(short_clip)
            logger.info(f"✅ Short clip created: {short_clip.duration:.2f}s")
            
            # # 3. Create brief video (with duration limit)
            # brief_path = os.path.join(self.default_paths["output_dir"], "brief_video.mp4")
            # logger.info("\n3️⃣  Creating brief video...")
            # try:
            #     # Select random video for brief
            #     brief_source = random.choice(glob.glob(os.path.join(self.default_paths["videos_dir"], "**/*.mp4"), recursive=True))
            #     logger.info(f"Selected random video: {brief_source}")

            #     # Load main audio and take first few seconds
            #     main_audio = AudioFileClip(audio_path)
            #     brief_audio_duration = min(15.0, main_audio.duration)  # Take up to 15 seconds
            #     brief_audio = main_audio.subclip(0, brief_audio_duration)
            #     brief_audio = brief_audio.fx(audio_fadeout, 2)  # Add 2-second fadeout
            #     main_audio.close()

            #     brief_video = create_brief_video(
            #         source_video_path=brief_source,
            #         logo_path=self.default_paths["logo"],
            #         background_music_path=self.default_paths["bg_music"],
            #         output_video_path=brief_path,
            #         voiceover_path=audio_path,  # Pass the main audio path
            #         video_duration=brief_audio_duration,  # Match video duration to audio
            #         logo_width=200,
            #         logo_height=200,
            #         footer_text=self.text_settings.get("content", {}).get("footer", "Follow us on social media • Subscribe to our channel")
            #     )
            #     logger.info(f"✅ Brief video created: {brief_video.duration:.2f}s")
            # except Exception as e:
            #     logger.error(f"❌ Error creating brief video: {str(e)}")
            #     logger.exception(e)

            # Create intro video
            intro_path = os.path.join(self.default_paths["output_dir"], "intro_video.mp4")
            logger.info("\n4️⃣  Creating intro video...")
            try:
                intro_clip = create_brief_video(
                    source_video_path=self.default_paths.get("intro_video", "intro_extro/intro7.mp4"),
                    logo_path=self.default_paths["logo"],
                    background_music_path=self.default_paths["bg_music"],
                    output_video_path=intro_path,
                    video_duration=5.0,  # Short 5-second intro
                    logo_width=200,
                    logo_height=200,
                    footer_text="Welcome to our Podcast"
                )
                logger.info(f"✅ Intro video created: {intro_clip.duration:.2f}s")
            except Exception as e:
                logger.error(f"❌ Error creating intro video: {str(e)}")
                logger.exception(e)

            # 5. Create main podcast video (using full audio length)
            podcast_path = os.path.join(self.default_paths["output_dir"], "podcast_video.mp4")
            logger.info("\n5️⃣  Creating main podcast video...")
            logger.info(f"   Full audio duration: {audio_duration:.2f}s")
            podcast_creator = podcast_video.PodcastVideoCreator(
                source_videos_path=self.default_paths["videos_dir"],
                background_music_path=self.default_paths["bg_music"],
                voiceover_path=audio_path,
                logo_path=self.default_paths["logo"],
                logo_width=self.logo_settings.get("width", 200),
                logo_height=self.logo_settings.get("height", 200),
                bg_music_volume=0.07,  
                heading_text=self.text_settings.get("content", {}).get("heading", "AppliView Podcast"),
                subheading_text=self.text_settings.get("content", {}).get("subheading", "Tech Insights & Innovation"),
                footer_text=self.text_settings.get("content", {}).get("footer", "Follow us on social media • Subscribe to our channel"),
                output_path=podcast_path
            )
            podcast_creator.create_video()
            podcast_video_clip = VideoFileClip(podcast_path)
            logger.info(f"✅ Main podcast video created: {podcast_video_clip.duration:.2f}s")
            
            # 6. Get outro video
            outro_path = self.default_paths["outro_video"]
            logger.info("\n6️⃣  Using outro video...")
            logger.info(f"   Path: {outro_path}")
            if not os.path.exists(outro_path):
                logger.error(f"❌ Outro video not found at: {outro_path}")
                return None
            outro_video_clip = VideoFileClip(outro_path)
            outro_video_clip = add_fade_effects(outro_video_clip)
            logger.info(f"✅ Outro video loaded: {outro_video_clip.duration:.2f}s")

            # 7. Combine all videos
            logger.info("\n7️⃣  Combining all videos...")
            
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
            
            if intro_clip:
                video_segments.append(intro_clip)
                total_duration += intro_clip.duration
                logger.info(f"Added intro: {intro_clip.duration:.2f}s")
            
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
                intro_clip.close()
                podcast_video_clip.close()
                outro_video_clip.close()

                # Delete temporary files if cleanup is enabled
                # if constants.CLEANUP_LOCAL_VIDEOS:
                #     logger.info("Deleting temporary video files...")
                #     os.remove(short_path)
                #     if os.path.exists(brief_path):
                #         os.remove(brief_path)
                #     os.remove(podcast_path)
                # else:
                #     logger.info("Keeping local video files (CLEANUP_LOCAL_VIDEOS is False)")

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

import os
import logging
from moviepy.editor import VideoFileClip, concatenate_videoclips
import datetime
import json
logger = logging.getLogger(__name__)

def create_final_video_from_paths(video_paths: dict, config: dict, job_id: int) -> str:
    """
    Create final video by concatenating video clips with transitions.
    
    Args:
        video_paths: Dictionary of video paths in order (intro, short, bumper, main, outro)
        config: Configuration dictionary containing video settings
        job_id: Job ID to include in the output filename
        
    Returns:
        Path to the final video file
    """
   
    try:
        logger.info("Creating final video from paths...")
        
        # Get video resolution from config
        resolution = config.get('resolution', (780, 480))
         
        # Load clips in order
        clips = []
        path_order = ['intro_video_path', 'short_video_path', 'bumper_video_path', 'main_video_path', 'outro_video_path']
        
        for path_key in path_order:
            if path_key in video_paths and os.path.exists(video_paths[path_key]):
                logger.info(f"Loading {path_key}...")
                clip = VideoFileClip(video_paths[path_key])
                # Resize clip to match target resolution
                if clip.size != resolution:
                    clip = clip.resize(width=resolution[0], height=resolution[1])
                clips.append(clip)
        
        if not clips:
            raise ValueError("No valid video clips found")
            
        # Add crossfade transitions between clips
        transition_duration = 1.0  # 1 second transition
        for i in range(len(clips)-1):
            clips[i] = clips[i].crossfadeout(transition_duration)
            clips[i+1] = clips[i+1].crossfadein(transition_duration)
        
        # Concatenate all clips with transitions
        logger.info("Concatenating clips with transitions...")
        final_video = concatenate_videoclips(
            clips,
            method="compose"
        )
        
        # Create output path
        output_dir = config['output_dir']
        output_filename = config.get('final_video_output_filename', 'final_video_{job_id}.mp4')
        output_filename = output_filename.replace('{job_id}', str(job_id))
        output_path = os.path.join(output_dir, output_filename)
        
        # Write final video
        logger.info(f"Writing final video to {output_path}...")
        final_video.write_videofile(
            output_path,
            fps=config.get('fps', 30),
            codec=config.get('video_codec', 'libx264'),
            bitrate=config.get('video_bitrate', '8000k'),
            audio_codec=config.get('audio_codec', 'aac'),
            audio_bitrate=config.get('audio_bitrate', '128k')
        )
        
        # Close clips to free up memory
        for clip in clips:
            clip.close()
            
        logger.info("Final video created successfully!")
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating final video: {str(e)}")
        raise
