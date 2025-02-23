import os
import logging
import numpy
from typing import List, Dict, Tuple
from PIL import Image
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip, TextClip, 
    CompositeVideoClip, concatenate_videoclips, ColorClip
)
from moviepy.video.fx.resize import resize

logger = logging.getLogger(__name__)

class MainVideoCreator:
    """Creates the main segment of the podcast video"""
    
    def __init__(self):
        self.clips = []
        
    def resize_video(self, clip, width: int, height: int) -> VideoFileClip:
        """Resize a video clip to the specified dimensions"""
        return clip.resize(width=width, height=height)
        
    def add_logo(self, clip: VideoFileClip, logo_path: str, logo_width: int, logo_height: int) -> CompositeVideoClip:
        """Add a logo to the video clip"""
        if not os.path.exists(logo_path):
            logger.warning(f"Logo file not found: {logo_path}")
            return clip
            
        logo = ImageClip(logo_path)
        logo = logo.resize(width=logo_width, height=logo_height)
        logo = logo.set_position((50, 50))  # Top-left corner with padding
        logo = logo.set_duration(clip.duration)
        return CompositeVideoClip([clip, logo])

    def create_main_video(
        self,
        audio_path: str,
        config: Dict,
        resolution: Tuple[int, int]
    ) -> CompositeVideoClip:
        """
        Create the main video segment with audio and visuals
        
        Args:
            audio_path: Path to the main audio file
            config: Configuration dictionary
            resolution: Video resolution (width, height)
            
        Returns:
            CompositeVideoClip: The composed main video segment
        """
        try:
            # Load audio
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # Create background clips
            clips = []
            
            # Add background video/image if available
            if config.get('background_video_path') and os.path.exists(config['background_video_path']):
                bg_clip = VideoFileClip(config['background_video_path'])
                bg_clip = self.resize_video(bg_clip, resolution[0], resolution[1])
                bg_clip = bg_clip.loop(duration=duration)
                clips.append(bg_clip)
            elif config.get('background_image_path') and os.path.exists(config['background_image_path']):
                pil_image = Image.open(config['background_image_path'])
                bg_clip = ImageClip(numpy.array(pil_image))
                bg_clip = bg_clip.resize(width=resolution[0], height=resolution[1])
                bg_clip = bg_clip.set_duration(duration)
                clips.append(bg_clip)
                
            # Add title text if provided
            if config.get('title'):
                title_clip = TextClip(
                    config['title'],
                    fontsize=config['title_font_size'],
                    color=config['title_font_color'],
                    font=config['title_font_name']
                ).set_position(('center', 100)).set_duration(duration)
                clips.append(title_clip)
                
            # Add subtitle text if provided
            if config.get('subtitle'):
                subtitle_clip = TextClip(
                    config['subtitle'],
                    fontsize=config['subtitle_font_size'],
                    color=config['subtitle_font_color'],
                    font=config['subtitle_font_name']
                ).set_position(('center', 200)).set_duration(duration)
                clips.append(subtitle_clip)
                
            # Add logo if available
            if config.get('logo_settings_main_logo_path') and os.path.exists(config['logo_settings_main_logo_path']):
                pil_image = Image.open(config['logo_settings_main_logo_path'])
                logo_clip = ImageClip(numpy.array(pil_image))
                logo_clip = logo_clip.resize(
                    width=config['logo_settings_logo_size'][0],
                    height=config['logo_settings_logo_size'][1]
                )
                logo_clip = logo_clip.set_position((50, 50))
                logo_clip = logo_clip.set_duration(duration)
                clips.append(logo_clip)
                
            # Add footer text if provided
            if config.get('footer_settings_text'):
                footer_height = 80  # Increased height for better padding
                footer_y = resolution[1] - 100  # Position of the footer background
                
                # Add a dark background behind the footer text for better visibility
                footer_bg = (ColorClip((resolution[0], footer_height), color=(0, 0, 0))
                    .set_opacity(0.7)
                    .set_position(('center', footer_y))
                    .set_duration(duration))
                clips.append(footer_bg)
                
                # Position the text in the center of the background with padding
                footer_clip = TextClip(
                    config['footer_settings_text'],
                    fontsize=config['footer_settings_font_size'],
                    color=config['footer_settings_font_color'],
                    font=config['footer_settings_font_name'],
                    size=(resolution[0] - 80, None),  # More padding
                    method='caption',
                    align='center'
                ).set_position(('center', footer_y + (footer_height - config['footer_settings_font_size']) // 2)).set_duration(duration)
                clips.append(footer_clip)
                
            # Create main composite video
            logger.info("Compositing main video segment...")
            main_video = CompositeVideoClip(clips, size=resolution)
            main_video = main_video.set_audio(audio_clip)
            
            #let us save this video in the output directory
            main_video_output_path = os.path.join(config['output_dir'], 'composite_main_video.mp4')
            main_video.write_videofile(main_video_output_path, codec='libx264', audio_codec='aac')
            logger.info("Main video segment created successfully")
            return main_video,main_video_output_path
            
        except Exception as e:
            logger.error(f"Error creating main video segment: {str(e)}")
            raise