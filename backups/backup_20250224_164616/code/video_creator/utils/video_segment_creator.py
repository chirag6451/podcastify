#!/usr/bin/env python3
import os
import logging
from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, 
    concatenate_videoclips, ColorClip, ImageClip, CompositeAudioClip
)
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.audio.fx.audio_loop import audio_loop
import colorlog
from typing import Dict, Any, Optional, Tuple, List

from utils.file_writer import get_output_path

def setup_logger():
    # This function is not provided in the original file or the code block
    # It's assumed to exist as it's called in the create_video_segment function
    pass

def create_video_segment(
    config: dict,
    job_id: str,
    segment_type: str = "generic",
    request_dict: dict = None,
    audio_path: str = None
) -> str:
    """
    Create a video segment (intro/outro) with background video, text overlays, and background music.
    No voiceover is used for these segments.
    """
    try:
        print(f"Creating {segment_type} video segment...")
    
        
      
        
        # Check if input files exist
        background_video_path = config['background_video_path']
        background_music_path = config['background_music_path']
        logo_path = config['logo_settings_main_logo_path']
        resolution = config['resolution']
        duration = config['duration']
        bg_music_volume = config['bg_music_volume']
        heading_font_size = config['title_font_size']
        heading_font_color = config['title_font_color']
        heading_font = config['title_font_name']
        subheading_font_size = config['subtitle_font_size']
        subheading_font_color = config['subtitle_font_color']
        subheading_font = config['subtitle_font_name']
     
        footer = config['footer_text']
        
      
        #if heading is not avaiable in config we use the title and subtitle from request_dict
  
        try :
            heading = config['title']
            subheading = config['sub_title']
        except:
            heading = request_dict['title']
            subheading = request_dict['sub_title']

        if not os.path.exists(background_video_path):
            raise FileNotFoundError(f"Background video file not found: {background_video_path}")
        if not os.path.exists(background_music_path):
            raise FileNotFoundError(f"Background music file not found: {background_music_path}")
        if logo_path and not os.path.exists(logo_path):
            raise FileNotFoundError(f"Logo file not found: {logo_path}")

        # Load the background video
        video = VideoFileClip(background_video_path)
        
        # Resize video to target resolution
        video = video.resize(resolution)
        
        # Get a segment from the middle of the video or loop if it's too short
        if video.duration > duration:
            start = (video.duration - duration) / 2
            video = video.subclip(start, start + duration)
        else:
            print(f"Background video is shorter than {duration}s, looping to match duration.")
            video = video.loop(duration=duration)
        
        # Create text clips
        heading_clip = TextClip(
            heading,
            fontsize=config['title_font_size'],
            color=config['title_font_color'],
            font=config['title_font_name'],
            size=(int(resolution[0] * 0.8), None),
            method='caption'
        ).set_duration(duration)
        
        subheading_clip = TextClip(
            subheading,
            fontsize=config['subtitle_font_size'],
            color=config['subtitle_font_color'],
            font=config['subtitle_font_name'],
            size=(int(resolution[0] * 0.8), None),
            method='caption'
        ).set_duration(duration)
        
        footer_clip = TextClip(
            footer,
            fontsize=config['footer_settings_font_size'],
            color=config['footer_settings_font_color'],
            font=config['footer_settings_font_name'],
            size=(int(resolution[0] * 0.8), None),
            method='caption'
        ).set_duration(duration)
        
        # Position text clips
        # Calculate the total height of both clips plus spacing
        total_height = heading_clip.size[1] + subheading_clip.size[1] + 20  # 20px spacing between texts
        
        # Calculate center positions
        center_y = (resolution[1] - total_height) // 2
        heading_y = center_y
        subheading_y = heading_y + heading_clip.size[1] + 20
        
        heading_clip = heading_clip.set_position(('center', heading_y))
        subheading_clip = subheading_clip.set_position(('center', subheading_y))
        footer_clip = footer_clip.set_position(('center', resolution[1] - 100))  # 100px from bottom
        
        # Add logo if provided
        clips = [video, heading_clip, subheading_clip, footer_clip]
        if logo_path:
            # Add padding for logo position
            padding = 20
            logo_width = config['logo_settings_logo_size'][0]
            logo_height = config['logo_settings_logo_size'][1]
            logo_clip = (ImageClip(logo_path)
                        .resize((logo_width, logo_height))
                        .set_duration(duration)
                        .set_position((resolution[0] - logo_width - padding, padding)))  # Top-right with padding
            clips.append(logo_clip)
        
        # Composite the final video with all elements
        final_video = CompositeVideoClip(clips, size=resolution)
        
        # Add background music
        print(f"Adding background music from {background_music_path}")
        bg_music = AudioFileClip(background_music_path)
        
        # Ensure background music matches video duration
        if bg_music.duration < duration:
            print(f"Background music is shorter than {duration}s, looping to match duration.")
            bg_music = bg_music.loop(duration=duration)
        else:
            print(f"Trimming background music to match {duration}s.")
            bg_music = bg_music.subclip(0, duration)
        
        # Set volume for background music
        bg_music = bg_music.volumex(bg_music_volume)
        print(f"Background music volume set to {bg_music_volume}")
        
        # Attach audio to video
        final_video = final_video.set_audio(bg_music)
        
        # Create output directory if it doesn't exist
        # output_dir = config['output_dir']
        # output_path = os.path.join(output_dir, config['output_filename'])
     
        # output_dir = os.path.dirname(output_path)
        # os.makedirs(output_dir, exist_ok=True)
        
        #let us get the output path from the file writer
        output_path = get_output_path(
            job_id=job_id,
            customer_id=request_dict['customer_id'],
            profile_name=request_dict['profile_name'],
            output_filename=config['intro_filename'],
            output_dir=config['output_dir']
        )
        
        # Write the final video to file
        print(f"Writing final video to {output_path}...")
        final_video.write_videofile(
            output_path, 
            codec=config['codec'],
            audio_codec=config['audio_codec'], 
            fps=config['fps']
        )
        print(f"{segment_type.capitalize()} video segment created successfully!")
        return output_path
        
    except Exception as e:
        logging.error(f"Error creating {segment_type} segment: {str(e)}")
        raise



def process_individual_video(config: Dict) -> Dict:
    """
    Process an individual video segment (e.g., intro or outro) based on the provided configuration.
    
    Args:
        config (Dict): Configuration dictionary for the video segment.
        
    Returns:
        Dict: Metadata about the generated video, including its name, type, and path.
    """
    name = config.get('name', 'Unnamed Video')
    params = config.get('params', {})
    segment_type = params.get('segment_type', 'generic')  # intro, outro, etc.
    
    try:
        print(f"Processing {name} ({segment_type})...")
        video_path = create_video_segment(**params)
        result = {
            'name': name,
            'type': segment_type,
            'path': video_path
        }
        print(f"{name} created successfully: {video_path}")
        return result
    except Exception as e:
        print(f"Failed to create {name}: {str(e)}")
        return {
            'name': name,
            'type': segment_type,
            'error': str(e)
        }


