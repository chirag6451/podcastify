#!/usr/bin/env python3
import os
import numpy as np
from typing import Tuple, Optional, List, Callable
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip, TextClip, 
    CompositeVideoClip, ColorClip, CompositeAudioClip
)
from moviepy.video.fx.resize import resize
from moviepy.video.fx.speedx import speedx
from moviepy.audio.fx.audio_loop import audio_loop
import logging
from PIL import Image

def create_circular_mask(size: Tuple[int, int]) -> ImageClip:
    """Create a circular mask for video clips"""
    center = (size[0] // 2, size[1] // 2)
    radius = min(center[0], center[1])
    Y, X = np.ogrid[:size[1], :size[0]]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y - center[1])**2)
    mask = dist_from_center <= radius
    mask_array = np.zeros((size[1], size[0], 4), dtype=np.uint8)
    mask_array[mask] = [255, 255, 255, 255]
    return ImageClip(mask_array, ismask=True, duration=None)

def create_thumbnails(
    video_path: str, 
    num_thumbnails: int = 3,
    thumbnail_size: Tuple[int, int] = (1280, 720),  # YouTube recommended size
    thumbnails_dir: Optional[str] = None
) -> List[str]:
    """
    Create thumbnails from the generated video.
    
    Args:
        video_path (str): Path to the video file
        num_thumbnails (int): Number of thumbnails to generate
        thumbnail_size (Tuple[int, int]): Size of thumbnails in pixels (width, height)
        thumbnails_dir (Optional[str]): Directory to save thumbnails. If None, uses 'thumbnails' in video directory
        
    Returns:
        List[str]: List of paths to the generated thumbnail files
    """
    try:
        # Load the video
        video = VideoFileClip(video_path)
        duration = video.duration
        
        # Calculate timestamps for thumbnails
        timestamps = [duration * (i + 1) / (num_thumbnails + 1) for i in range(num_thumbnails)]
        
        # Create output directory
        if thumbnails_dir is None:
            thumbnails_dir = os.path.join(os.path.dirname(video_path), "thumbnails")
        os.makedirs(thumbnails_dir, exist_ok=True)
        
        thumbnail_paths = []
        # Generate thumbnails
        for i, timestamp in enumerate(timestamps):
            # Get the frame at the timestamp
            frame = video.get_frame(timestamp)
            
            # Create an ImageClip from the frame and resize to YouTube dimensions
            thumbnail = (ImageClip(frame)
                       .resize(thumbnail_size))
            
            # Generate output path
            output_filename = f"thumbnail_{i+1}.jpg"
            output_path = os.path.join(thumbnails_dir, output_filename)
            
            # Save the frame first
            temp_path = os.path.join(thumbnails_dir, f"temp_{output_filename}")
            thumbnail.save_frame(temp_path)
            
            # Use PIL to load and save with quality
            with Image.open(temp_path) as img:
                img.save(output_path, 'JPEG', quality=95)
            
            # Remove temporary file
            os.remove(temp_path)
            
            thumbnail_paths.append(output_path)
            
            # Clean up
            thumbnail.close()
        
        return thumbnail_paths
        
    except Exception as e:
        logging.error(f"Error creating thumbnails: {str(e)}")
        raise
    finally:
        try:
            video.close()
        except:
            pass

def create_podcast_intro(
    speaker1_video_path: str,
    speaker1_name: str,
    speaker2_video_path: str,
    speaker2_name: str,
    title: str,
    subtitle: str,
    footer: str,
    background_image_path: str,
    duration: int,
    background_music_path: str,
    video_output_path: str = "output/podcast_intro7.mp4",
    thumbnails_output_dir: str = "output/thumbnails",
    voiceover_path: Optional[str] = None,
    resolution: Tuple[int, int] = (1920, 1080),
    bg_music_volume: float = 0.1,
    voiceover_volume: float = 1.0,
    create_thumbnails_flag: bool = False
) -> Tuple[str, Optional[List[str]]]:
    """
    Create a podcast intro video featuring two speakers.
    
    Args:
        speaker1_video_path (str): Path to the first speaker's video
        speaker1_name (str): Name of the first speaker
        speaker2_video_path (str): Path to the second speaker's video
        speaker2_name (str): Name of the second speaker
        title (str): Title of the podcast
        subtitle (str): Subtitle or episode description
        footer (str): Footer text
        background_image_path (str): Path to the background image
        duration (int): Duration of the intro in seconds
        background_music_path (str): Path to background music file
        video_output_path (str): Path where the output video will be saved
        thumbnails_output_dir (str): Directory where thumbnails will be saved
        voiceover_path (Optional[str]): Path to voiceover audio file
        resolution (Tuple[int, int]): Output video resolution (width, height)
        bg_music_volume (float): Volume of background music (0.0 to 1.0)
        voiceover_volume (float): Volume of voiceover (0.0 to 1.0)
        create_thumbnails_flag (bool): Whether to create thumbnails from the video
        
    Returns:
        Tuple[str, Optional[List[str]]]: Tuple containing:
            - Path to the generated video file
            - List of paths to generated thumbnails (if create_thumbnails_flag is True)
    """
    try:
        # Validate input files
        for file_path in [speaker1_video_path, speaker2_video_path, background_image_path, background_music_path]:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
        
        if voiceover_path and not os.path.exists(voiceover_path):
            raise FileNotFoundError(f"Voiceover file not found: {voiceover_path}")
        
        # Ensure output directories exist
        os.makedirs(os.path.dirname(video_output_path), exist_ok=True)
        if create_thumbnails_flag:
            os.makedirs(thumbnails_output_dir, exist_ok=True)
        
        # Load and prepare background
        background = ImageClip(background_image_path).resize(resolution)
        background = background.set_duration(duration)
        
        # Create semi-transparent overlay
        overlay = ColorClip(resolution, color=(0, 0, 0))
        overlay = overlay.set_opacity(0.5).set_duration(duration)
        
        # Calculate dimensions for circular speaker videos
        speaker_size = min(resolution[0] // 4, resolution[1] // 3)  # Size of the circular frame
        speaker_y_position = resolution[1] * 0.4  # Vertical position for both speakers
        
        # Calculate x positions for left and right speakers
        spacing = speaker_size * 1.5  # Space between speakers
        center_x = resolution[0] // 2
        speaker1_x = center_x - spacing
        speaker2_x = center_x + spacing - speaker_size
        
        # Create circular mask
        circle_mask = create_circular_mask((speaker_size, speaker_size))
        
        # Create circular background for speakers (optional, for better visual effect)
        circle_bg = ColorClip((speaker_size, speaker_size), color=(128, 128, 128))
        circle_bg = circle_bg.set_mask(circle_mask)
        
        # Load and prepare speaker videos
        speaker1_clip = (VideoFileClip(speaker1_video_path)
            .resize((speaker_size, speaker_size))
            .set_mask(circle_mask)
            .set_position((speaker1_x, speaker_y_position))
            .loop()
            .set_duration(duration))
        
        speaker2_clip = (VideoFileClip(speaker2_video_path)
            .resize((speaker_size, speaker_size))
            .set_mask(circle_mask)
            .set_position((speaker2_x, speaker_y_position))
            .loop()
            .set_duration(duration))
        
        # Create text clips
        title_clip = (TextClip(title, fontsize=70, color='white', font='Arial-Bold')
            .set_position(('center', resolution[1] * 0.15))
            .set_duration(duration))
        
        subtitle_clip = (TextClip(subtitle, fontsize=40, color='white', font='Arial')
            .set_position(('center', resolution[1] * 0.25))
            .set_duration(duration))
        
        footer_clip = (TextClip(footer, fontsize=30, color='white', font='Arial')
            .set_position(('center', resolution[1] * 0.85))
            .set_duration(duration))
        
        # Position speaker names directly below their respective circles
        name_y_position = speaker_y_position + speaker_size + 5  # Reduced gap to 5 pixels
        name_fontsize = 36  # Slightly smaller font size
        
        # Create text background clips (black rectangles behind text)
        text_bg_height = 50
        text_bg_width = speaker_size
        text_bg = ColorClip((text_bg_width, text_bg_height), color=(0, 0, 0))
        text_bg = text_bg.set_opacity(0.7)  # Semi-transparent background
        
        # Create speaker name clips with enhanced visibility
        speaker1_name_clip = (TextClip(
            speaker1_name, 
            fontsize=name_fontsize, 
            color='white', 
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=1,
            size=(text_bg_width, None),  # Fixed width, auto height
            method='caption',  # Use caption method for better text wrapping
            align='center'  # Center align text
        ).set_position((speaker1_x, name_y_position))
         .set_duration(duration))
        
        speaker2_name_clip = (TextClip(
            speaker2_name, 
            fontsize=name_fontsize, 
            color='white', 
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=1,
            size=(text_bg_width, None),  # Fixed width, auto height
            method='caption',  # Use caption method for better text wrapping
            align='center'  # Center align text
        ).set_position((speaker2_x, name_y_position))
         .set_duration(duration))
        
        # Add text backgrounds to clips list
        text_bg1 = text_bg.set_position((speaker1_x, name_y_position)).set_duration(duration)
        text_bg2 = text_bg.set_position((speaker2_x, name_y_position)).set_duration(duration)

        # Load and prepare audio
        background_music = AudioFileClip(background_music_path)
        # Loop the background music to match the duration
        background_music = audio_loop(background_music, duration=duration)
        background_music = background_music.volumex(bg_music_volume)
        
        # Create final composition with explicit order
        clips = [
            background, 
            overlay,
            # Add circular backgrounds
            circle_bg.set_position((speaker1_x, speaker_y_position)).set_duration(duration),
            circle_bg.set_position((speaker2_x, speaker_y_position)).set_duration(duration),
            # Add speaker videos
            speaker1_clip,
            speaker2_clip,
            # Add text backgrounds
            text_bg1,
            text_bg2,
            # Add text elements in specific order
            title_clip, 
            subtitle_clip, 
            speaker1_name_clip,
            speaker2_name_clip,
            footer_clip
        ]
        
        # Add voiceover if provided
        if voiceover_path:
            voiceover = (AudioFileClip(voiceover_path)
                .volumex(voiceover_volume)
                .set_duration(duration))
            final_audio = CompositeAudioClip([background_music.set_duration(duration), voiceover])
        else:
            final_audio = background_music.set_duration(duration)
        
        # Create final video
        final_video = CompositeVideoClip(clips, size=resolution)
        final_video = final_video.set_audio(final_audio)
        
        # Write output file
        final_video.write_videofile(
            video_output_path,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            threads=4,
            preset='medium'
        )
        
        # Create thumbnails if requested
        thumbnail_paths = None
        if create_thumbnails_flag:
            thumbnail_paths = create_thumbnails(
                video_output_path,
                thumbnails_dir=thumbnails_output_dir
            )
        
        return video_output_path, thumbnail_paths
        
    except Exception as e:
        logging.error(f"Error creating podcast intro: {str(e)}")
        raise
    finally:
        # Clean up
        try:
            final_video.close()
            background_music.close()
            if voiceover_path:
                voiceover.close()
            speaker1_clip.close()
            speaker2_clip.close()
        except:
            pass 