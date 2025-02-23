#!/usr/bin/env python3

from utils.logger_utils import PodcastLogger
from utils.profile_manager import ProfileManager
import os
import sys
import json
from typing import Optional, Dict, Tuple, Any
from dataclasses import dataclass, field

# Initialize logger
logger = PodcastLogger("podcast_creator")

# Get the package root directory
PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))

@dataclass
class PodcastCreationConfig:
    # Required parameters
    topic: str
    
    # Optional parameters with defaults from profile
    num_turns: int = 5
    conversation_mood: str = "explaining in simple terms"
    language: str = "English"
    voice_accent: str = "Indian"
    welcome_voice_id: Optional[str] = None
    voice_id1: Optional[str] = None
    voice_id2: Optional[str] = None
    speaker1_name: Optional[str] = None
    speaker2_name: Optional[str] = None
    title: str = "AI Tech Talk"
    subtitle: str = "Impact and Future Prospects"
    resolution: Tuple[int, int] = (1920, 1080)
    bg_music_volume: float = 0.1
    videos_library_path: str = field(default_factory=lambda: os.path.join(PACKAGE_ROOT, "video_creator/defaults/videos"))
    background_image_path: str = field(default_factory=lambda: os.path.join(PACKAGE_ROOT, "video_creator/defaults/bgimages/bg1.jpeg"))
    background_music_path: str = field(default_factory=lambda: os.path.join(PACKAGE_ROOT, "video_creator/defaults/bgmusic/s3.mp3"))
    
    # Font Settings
    title_font_size: int = 60
    title_font_color: str = '#EBE0E2'
    title_font_name: str = 'Helvetica-Bold'
    subtitle_font_size: int = 40
    subtitle_font_color: str = '#eab676'
    subtitle_font_name: str = 'Helvetica'
    
    # Footer Settings
    footer_text: str = ""
    footer_font_size: int = 30
    footer_font_color: str = '#eeeee4'
    footer_font_name: str = 'Helvetica'
    footer_position: str = 'bottom-center'
    footer_padding: int = 20
    show_social_links: bool = True
    show_website: bool = True
    additional_footer_text: str = ""
    
    # Logo Settings
    main_logo_path: Optional[str] = None
    watermark_logo_path: Optional[str] = None
    logo_size: Tuple[int, int] = (200, 100)
    logo_position: str = 'top-right'
    watermark_opacity: float = 0.3
    show_watermark: bool = True
    
    # Business Information
    business_info: Dict = field(default_factory=dict)
    
    @classmethod
    def from_profile(cls, topic: str, profile_name: str) -> 'PodcastCreationConfig':
        """Create a PodcastCreationConfig instance from a profile"""
        profile_manager = ProfileManager()
        profile = profile_manager.get_profile(profile_name)
        
        if profile is None:
            raise ValueError(f"Profile {profile_name} not found")
        
        # Create config with topic
        config = cls(topic=topic)
        
        # Update voice settings
        for key, value in profile.voice_settings.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        # Update video settings
        for key, value in profile.video_settings.items():
            if key == 'footer_settings':
                for footer_key, footer_value in value.items():
                    attr_name = f"footer_{footer_key}" if footer_key != "text" else "footer_text"
                    if hasattr(config, attr_name):
                        setattr(config, attr_name, footer_value)
            elif key == 'logo_settings':
                for logo_key, logo_value in value.items():
                    if hasattr(config, logo_key):
                        if logo_key in ['main_logo_path', 'watermark_logo_path']:
                            logo_value = os.path.join(PACKAGE_ROOT, logo_value)
                        setattr(config, logo_key, logo_value)
            elif hasattr(config, key):
                if key in ['videos_library_path', 'background_image_path', 'background_music_path']:
                    value = os.path.join(PACKAGE_ROOT, value)
                setattr(config, key, value)
        
        # Update business info
        config.business_info = profile.business_info
        
        # Update default settings
        for key, value in profile.default_settings.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PodcastCreationConfig':
        voice_settings = data.get('voice_settings', {})
        video_settings = data.get('video_settings', {})
        font_settings = data.get('font_settings', {})
        
        return cls(
            topic=data.get('topic'),
            num_turns=data.get('num_turns', 5),
            conversation_mood=data.get('conversation_mood', "explaining in simple terms"),
            language=data.get('language', "English"),
            voice_accent=data.get('voice_accent', "Indian"),
            welcome_voice_id=voice_settings.get('welcome_voice_id'),
            voice_id1=voice_settings.get('voice_id1'),
            voice_id2=voice_settings.get('voice_id2'),
            speaker1_name=voice_settings.get('speaker1_name'),
            speaker2_name=voice_settings.get('speaker2_name'),
            title=data.get('title', "AI Tech Talk"),
            subtitle=data.get('subtitle', "Impact and Future Prospects"),
            resolution=tuple(video_settings.get('resolution', [1920, 1080])),
            bg_music_volume=video_settings.get('bg_music_volume', 0.1),
            videos_library_path=video_settings.get('videos_library_path', os.path.join(PACKAGE_ROOT, "video_creator/defaults/videos")),
            background_image_path=video_settings.get('background_image_path', os.path.join(PACKAGE_ROOT, "video_creator/defaults/bgimages/bg1.jpeg")),
            background_music_path=video_settings.get('background_music_path', os.path.join(PACKAGE_ROOT, "video_creator/defaults/bgmusic/s3.mp3")),
            title_font_size=font_settings.get('title_font_size', 60),
            title_font_color=font_settings.get('title_font_color', '#EBE0E2'),
            title_font_name=font_settings.get('title_font_name', 'Helvetica-Bold'),
            subtitle_font_size=font_settings.get('subtitle_font_size', 40),
            subtitle_font_color=font_settings.get('subtitle_font_color', '#eab676'),
            subtitle_font_name=font_settings.get('subtitle_font_name', 'Helvetica'),
            footer_text=data.get('footer_text', ""),
            footer_font_size=font_settings.get('footer_font_size', 30),
            footer_font_color=font_settings.get('footer_font_color', '#eeeee4'),
            footer_font_name=font_settings.get('footer_font_name', 'Helvetica'),
            footer_position=data.get('footer_position', 'bottom-center'),
            footer_padding=data.get('footer_padding', 20),
            show_social_links=data.get('show_social_links', True),
            show_website=data.get('show_website', True),
            additional_footer_text=data.get('additional_footer_text', ""),
            main_logo_path=data.get('main_logo_path'),
            watermark_logo_path=data.get('watermark_logo_path'),
            logo_size=tuple(data.get('logo_size', [200, 100])),
            logo_position=data.get('logo_position', 'top-right'),
            watermark_opacity=data.get('watermark_opacity', 0.3),
            show_watermark=data.get('show_watermark', True),
            business_info=data.get('business_info', {})
        )
    
    def to_dict(self) -> Dict:
        """Convert config to dictionary for video task"""
        return {
            'speaker1_name': self.speaker1_name,
            'speaker2_name': self.speaker2_name,
            'title': self.title,
            'subtitle': self.subtitle,
            'resolution': self.resolution,
            'bg_music_volume': self.bg_music_volume,
            'videos_library_path': self.videos_library_path,
            'background_image_path': self.background_image_path,
            'background_music_path': self.background_music_path,
            'title_font_size': self.title_font_size,
            'title_font_color': self.title_font_color,
            'title_font_name': self.title_font_name,
            'subtitle_font_size': self.subtitle_font_size,
            'subtitle_font_color': self.subtitle_font_color,
            'subtitle_font_name': self.subtitle_font_name,
            'footer_text': self.footer_text,
            'footer_font_size': self.footer_font_size,
            'footer_font_color': self.footer_font_color,
            'footer_font_name': self.footer_font_name,
            'footer_position': self.footer_position,
            'footer_padding': self.footer_padding,
            'show_social_links': self.show_social_links,
            'show_website': self.show_website,
            'additional_footer_text': self.additional_footer_text,
            'main_logo_path': self.main_logo_path,
            'watermark_logo_path': self.watermark_logo_path,
            'logo_size': self.logo_size,
            'logo_position': self.logo_position,
            'watermark_opacity': self.watermark_opacity,
            'show_watermark': self.show_watermark
        }

def create_podcast_with_video(
    config: PodcastCreationConfig,
    topic: str,
    output_path: str,
    return_task_ids: bool = False
) -> tuple[str, str]:
    """
    Create a podcast with video using the provided configuration.
    
    Args:
        config: The podcast creation configuration
        topic: Topic for the podcast
        output_path: Path where the final video will be saved
        return_task_ids: If True, return the task IDs without waiting for completion
    
    Returns:
        Tuple of (audio_task_id, video_task_id)
    """
    # Generate audio using Celery task
    audio_task = generate_audio_task.delay(
        topic=topic,
        speaker1_name=config.speaker1_name,
        speaker2_name=config.speaker2_name,
        voice_id1=config.voice_id1,
        voice_id2=config.voice_id2,
        language=config.language,
        voice_accent=config.voice_accent
    )

    # Generate video using Celery task
    video_task = create_video_task.delay(
        audio_task_id=audio_task.id,
        output_path=output_path,
        resolution=config.resolution,
        bg_music_volume=config.bg_music_volume,
        main_logo_path=config.main_logo_path,
        watermark_logo_path=config.watermark_logo_path,
        logo_position=config.logo_position,
        logo_size=config.logo_size,
        watermark_opacity=config.watermark_opacity,
        footer_text=config.footer_text,
        footer_position=config.footer_position,
        footer_font_name=config.footer_font_name,
        footer_font_size=config.footer_font_size,
        footer_font_color=config.footer_font_color,
        additional_footer_text=config.additional_footer_text
    )

    return audio_task.id, video_task.id

def check_task_status(audio_task_id: str, video_task_id: str) -> Dict[str, str]:
    """
    Check the status of audio and video generation tasks
    
    Args:
        audio_task_id: ID of the audio generation task
        video_task_id: ID of the video generation task
        
    Returns:
        Dict containing status of both tasks
    """
    from celery_app.tasks import generate_audio_task, create_video_task
    
    audio_task = generate_audio_task.AsyncResult(audio_task_id)
    video_task = create_video_task.AsyncResult(video_task_id)
    
    return {
        'audio_task': {
            'status': audio_task.status,
            'result': audio_task.result if audio_task.ready() else None
        },
        'video_task': {
            'status': video_task.status,
            'result': video_task.result if video_task.ready() else None
        }
    }

def example_usage():
    """Example usage of the combined podcast creator with Celery tasks"""
    # Read topic from a file
    with open("sample_blog.txt", "r") as f:
        topic_text = f.read()
    
    config = PodcastCreationConfig.from_profile(topic_text, "default_profile")
    
    # Start the tasks
    audio_task_id, video_task_id = create_podcast_with_video(config, topic_text, "combined_podcast.mp4")
    logger.info(f"Started tasks - Audio: {audio_task_id}, Video: {video_task_id}")
    
    # You can check status using check_task_status(audio_task_id, video_task_id)

if __name__ == "__main__":
    example_usage()
