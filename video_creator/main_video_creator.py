import os
import logging
import numpy
import random
import glob
from typing import List, Dict, Tuple
from PIL import Image
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip, TextClip, 
    CompositeVideoClip, concatenate_videoclips, ColorClip
)
from moviepy.video.fx.resize import resize
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from utils.file_writer import get_output_path

logger = logging.getLogger(__name__)

class MainVideoCreator:
    """Creates the main segment of the podcast video"""
    
    def __init__(self):
        self.clips = []
        self.bg_color = '#1a1a1a'
        
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

    def create_background_sequence(self, duration: float, videos_path: str, resolution: tuple) -> VideoFileClip:
        """Create a sequence of different background videos for the entire duration"""
        logger.info("Creating background video sequence from multiple videos...")
        
        # Get all video files from the directory
        video_files = []
        for ext in ['.mp4', '.avi', '.mov', '.mkv']:
            video_files.extend([os.path.join(videos_path, f) for f in os.listdir(videos_path) if f.endswith(ext)])
        
        if not video_files:
            raise ValueError(f"No video files found in {videos_path}")
            
        random.shuffle(video_files)  # Randomize video order
        
        video_segments = []
        remaining_duration = duration
        video_clips = []  # Keep track for cleanup
        
        try:
            while remaining_duration > 0 and video_files:
                # Get next video
                video_path = video_files.pop(0)
                if not video_files:  # If we've used all videos, refill and reshuffle
                    video_files = [os.path.join(videos_path, f) for f in os.listdir(videos_path) 
                                 if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
                    random.shuffle(video_files)
                
                try:
                    logger.info(f"Loading video: {os.path.basename(video_path)}")
                    video = VideoFileClip(video_path)
                    video_clips.append(video)  # Add to cleanup list
                    
                    # Resize video to match target resolution
                    video = self.resize_video(video, resolution[0], resolution[1])
                    
                    # Calculate segment duration
                    # Use a random duration between 5 and 10 seconds, or remaining duration if less
                    segment_duration = min(random.uniform(5, 10), remaining_duration)
                    
                    # If video is shorter than segment_duration, loop it
                    if video.duration < segment_duration:
                        video = video.loop(duration=segment_duration)
                    else:
                        # Take a random segment from the video
                        max_start = max(0, video.duration - segment_duration)
                        start_time = random.uniform(0, max_start)
                        video = video.subclip(start_time, start_time + segment_duration)
                    
                    # Add fade transitions
                    if video_segments:  # Not the first clip
                        video = video.fadein(0.5)
                    if remaining_duration - segment_duration <= 0:  # Last clip
                        video = video.fadeout(0.5)
                    
                    video_segments.append(video)
                    remaining_duration -= segment_duration
                    
                    logger.info(f"Added video segment from {os.path.basename(video_path)} "
                              f"(duration: {segment_duration:.2f}s, remaining: {remaining_duration:.2f}s)")
                    
                except Exception as e:
                    logger.error(f"Error processing video {video_path}: {str(e)}")
                    continue
            
            if not video_segments:
                raise ValueError("No valid video segments created")
                
            # Concatenate all video segments
            logger.info(f"Concatenating {len(video_segments)} video segments...")
            final_background = concatenate_videoclips(video_segments, method="compose")
            logger.info(f"Created background sequence with total duration: {final_background.duration:.2f}s")
            
            return final_background
            
        except Exception as e:
            logger.error(f"Error creating background sequence: {str(e)}")
            # Clean up on error
            for clip in video_clips:
                try:
                    clip.close()
                except:
                    pass
            # Create a plain black background as fallback
            return ColorClip(
                size=resolution,
                color=self.bg_color.lstrip('#')  # Remove # from hex color
            ).set_duration(duration)

    def _get_video_files(self, directory: str) -> List[str]:
        """Get all video files from the source directory."""
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        video_files = []
        
        for ext in video_extensions:
            video_files.extend(glob.glob(os.path.join(directory, f"*{ext}")))
            
        return video_files

    def _get_clip_segments(self, directory: str, total_duration: float, resolution: Tuple[int, int]) -> List[VideoFileClip]:
        """Select and prepare random video clips to match the required duration."""
        video_files = self._get_video_files(directory)
        if not video_files:
            raise ValueError(f"No video files found in {directory}")
            
        segments = []
        current_duration = 0
        
        while current_duration < total_duration:
            video_path = random.choice(video_files)
            logger.info(f"Processing video: {os.path.basename(video_path)}")
            
            try:
                clip = VideoFileClip(video_path)
                remaining_duration = total_duration - current_duration
                
                if clip.duration > remaining_duration:
                    if clip.duration > remaining_duration + 1:
                        start_time = random.uniform(0, clip.duration - remaining_duration)
                        clip = clip.subclip(start_time, start_time + remaining_duration)
                    else:
                        clip = clip.subclip(0, remaining_duration)
                
                clip = self.resize_video(clip, resolution[0], resolution[1])
                segments.append(clip)
                current_duration += clip.duration
                
            except Exception as e:
                logger.error(f"Error processing video {video_path}: {str(e)}")
                continue
                
        return segments

    def create_main_video(
        self,
        audio_path: str,
        config: Dict,
        resolution: Tuple[int, int],
        job_id: str,
        request_dict: dict
    ) -> CompositeVideoClip:
        """
        Create the main video segment with audio and visuals
        
        Args:
            audio_path: Path to the main audio file
            config: Configuration dictionary containing videos_library_path for random background videos
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
            
            # First check videos_library_path for random video sequence
            if config.get('videos_library_path') and os.path.exists(config['videos_library_path']):
                logger.info(f"Creating random video sequence from library: {config['videos_library_path']}")
                bg_clip = self.create_background_sequence(duration, config['videos_library_path'], resolution)
                clips.append(bg_clip)
            # Fallback to background_video_path for single video
            elif config.get('background_video_path') and os.path.exists(config['background_video_path']):
                logger.info(f"Using single background video: {config['background_video_path']}")
                bg_clip = VideoFileClip(config['background_video_path'])
                bg_clip = self.resize_video(bg_clip, resolution[0], resolution[1])
                bg_clip = bg_clip.loop(duration=duration)
                clips.append(bg_clip)
            # Fallback to background image
            elif config.get('background_image_path') and os.path.exists(config['background_image_path']):
                logger.info(f"Using background image: {config['background_image_path']}")
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
            main_video_filename = config['main_video_filename']
            main_video_output_path, _ = get_output_path(
                filename=main_video_filename,
                profile_name=request_dict['profile_name'],
                customer_id=request_dict['customer_id'],
                job_id=job_id,
                theme=request_dict.get('theme', 'default')
            )
            main_video.write_videofile(main_video_output_path, codec='libx264', audio_codec='aac')
            logger.info("Main video segment created successfully")
            return main_video, main_video_output_path
            
        except Exception as e:
            logger.error(f"Error creating main video segment: {str(e)}")
            raise