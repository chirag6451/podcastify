#!/usr/bin/env python3
import os
import numpy as np
from typing import Tuple, Optional, List, Callable
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip, TextClip, 
    CompositeVideoClip, ColorClip, CompositeAudioClip, concatenate_videoclips
)
from moviepy.video.fx.resize import resize
from moviepy.video.fx.speedx import speedx
from moviepy.audio.fx.audio_loop import audio_loop
import logging
import colorlog
from PIL import Image
import json

def setup_logger():
    """Set up colored logging configuration"""
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s %(levelname)s: %(blue)s%(message)s',
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

    logger = colorlog.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

logger = setup_logger()

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
        
    return []


def create_podcast_short_video(
    audio_path: str,
    welcome_audio_path: str,
    config: dict,
    request_dict: dict,
) -> Tuple[str, Optional[List[str]]]:
    """
    Creates a podcast intro video that displays:
      - Two circular speaker "videos" (which can each be images or videos) side by side
      - A background (which can be an image or a video)
      - Background music
      - Optional voiceover
      - Title, subtitle, and footer text

    Ensures the final video duration matches the *full length* of
    the chosen audio source (voiceover if provided, otherwise `audio_path`).
    A fade-out is applied in the last few seconds **without cutting** the audio short.
    """
    import moviepy.video.fx.all as vfx  # For fadeout, etc.
    
    fade_duration = 1.5  # Duration of the fade-out at the end of the video
    
    try:
        output_dir = config['output_dir']
        output_filename = config['short_video_output_filename']
        
        logger.debug("\nStarting create_podcast_short_video with parameters:")
        logger.debug(f"Background path: {config['background_image_path']}")
        logger.debug(f"Resolution: {config['resolution']}")
        
        # --- Basic validations ---
        background_path = config['short_video_background_path']
        if not background_path:
            raise ValueError("Background path is None.")
        if not os.path.exists(background_path):
            raise FileNotFoundError(f"Background not found: {background_path}")
        if not os.path.isfile(background_path):
            raise ValueError(f"Background path is not a file: {background_path}")
        
        # Validate other required files
        required_files = [
            (config['speaker1_video_path'], "speaker1 video/image"),
            (config['speaker2_video_path'], "speaker2 video/image"),
            (config['background_music_path'], "background music")
        ]
        
        for file_path, file_type in required_files:
            logger.debug(f"Checking {file_type} path: {file_path}")
            if not file_path:
                raise ValueError(f"{file_type.title()} path is None")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"{file_type.title()} file not found: {file_path}")
            if not os.path.isfile(file_path):
                raise ValueError(f"{file_type.title()} path is not a file: {file_path}")
            logger.debug(f"{file_type.title()} file OK: {file_path}")
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Create output dirs
        os.makedirs(os.path.dirname(config['output_filename']), exist_ok=True)
        if config.get('create_thumbnails'):
            os.makedirs(config['thumbnails_output_dir'], exist_ok=True)
        
        # --- Decide which audio is the "primary" (voiceover vs. welcome audio) ---
        chosen_audio_path = audio_path
        if welcome_audio_path and os.path.exists(welcome_audio_path):
            if config.get('use_welcome_audio'):
                chosen_audio_path = welcome_audio_path
        
        # Load the chosen main audio
        voiceover_clip = AudioFileClip(chosen_audio_path)
        audio_duration = voiceover_clip.duration

        # If you need to allow a forced "minimum" or "override" duration from config:
        # final_video_duration = max(audio_duration, config.get("duration", 0))
        # But typically we just match the audio exactly:
        final_video_duration = audio_duration
        
        logger.info(f"Final video duration set to {final_video_duration:.2f}s (audio length).")
        
        # --- Extension sets we consider for images vs. video ---
        valid_image_exts = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}
        valid_video_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".mpeg", ".mpg"}
        
        # ---- 1) Create the background clip (image or video), loop/cut to final duration ----
        def load_background_clip(path, duration):
            _, ext = os.path.splitext(path.lower())
            if ext in valid_image_exts:
                try:
                    with Image.open(path) as img:
                        logger.debug(
                            f"Using background image: {path} | size: {img.size} | mode: {img.mode}"
                        )
                except Exception as e:
                    raise RuntimeError(f"Cannot open background image '{path}': {e}")
                
                # ImageClip lasts the entire duration
                clip = ImageClip(path).resize(config['resolution'])
                return clip.set_duration(duration)
            
            elif ext in valid_video_exts:
                # Load and prepare background video
                background = VideoFileClip(path)
                
                # Set position to center and resize to fill screen while maintaining aspect ratio
                background_w, background_h = background.size
                target_w, target_h = config['resolution']
                scale = max(target_w/background_w, target_h/background_h)
                new_size = (int(background_w*scale), int(background_h*scale))
                
                # If background video is shorter than needed duration, loop it
                if background.duration < duration:
                    n_loops = int(np.ceil(duration / background.duration))
                    clips = [background] * n_loops
                    background = concatenate_videoclips(clips)
                
                background = (background
                    .resize(new_size)
                    .set_position(("center", "center"))
                    .set_duration(duration))  # Set exact duration
                
                return background.without_audio()  # Remove audio from background
            
            else:
                raise ValueError(
                    f"Background file '{path}' has unrecognized extension '{ext}'. "
                    "Expected an image (jpg/png/etc.) or a video (mp4/mov/etc.)"
                )
        
        background = load_background_clip(background_path, final_video_duration)
        logger.info(f"Background clip duration: {background.duration}, Target duration: {final_video_duration}")
        
        # Optional overlay
        overlay = ColorClip(config['resolution'], color=(0, 0, 0)).set_opacity(0.5)
        overlay = overlay.set_duration(final_video_duration)
        
        # --- Helper for circular mask ---
        def create_circular_mask(size):
            import numpy as np
            import cv2
            
            w, h = size
            mask = np.zeros((h, w, 1), dtype="uint8")
            center = (w // 2, h // 2)
            radius = min(center)
            cv2.circle(mask, center, radius, (255,), -1)
            return ImageClip(mask, ismask=True)
        
        # If 'speaker_size' is in config, use it; otherwise compute a default
        if 'speaker_size' in config and config['speaker_size']:
            speaker_size = config['speaker_size']
        else:
            speaker_size = min(config['resolution'][0] // 4, config['resolution'][1] // 3)
        
        circle_mask = create_circular_mask((speaker_size, speaker_size))
        
        # --- Function to load speaker clip (either an image or video), loop/cut, etc. ---
        def load_speaker_clip(path, duration, position, size, mask):
            base, ext = os.path.splitext(path.lower())
            if ext in valid_image_exts:
                clip = ImageClip(path).set_duration(duration)
            elif ext in valid_video_exts:
                clip = VideoFileClip(path)
                logger.info(f"Loading speaker clip: {path}, Original duration: {clip.duration}")
                
                # If video is shorter than needed duration, calculate number of loops needed
                if clip.duration < duration:
                    n_loops = int(np.ceil(duration / clip.duration))
                    logger.info(f"Video needs {n_loops} loops to reach {duration}s")
                    clips = [clip] * n_loops
                    clip = concatenate_videoclips(clips)
                    logger.info(f"After concatenating {n_loops} clips, duration: {clip.duration}")
                
                # Set exact duration after looping
                clip = clip.set_duration(duration)
                logger.info(f"Final clip duration after set_duration: {clip.duration}")
            else:
                raise ValueError(f"Speaker clip '{path}' has invalid extension '{ext}'.")
            
            # Resize + mask + position
            clip = (
                clip
                .resize((size, size))
                .set_mask(mask)
                .set_position(position)
                .set_duration(duration)  # Ensure final duration is exact
            )
            return clip
        
        # Speaker positions
        speaker_y_position = int(config['resolution'][1] * 0.4)
        spacing = speaker_size * 1.5
        center_x = config['resolution'][0] // 2
        speaker1_x = int(center_x - spacing)
        speaker2_x = int(center_x + spacing - speaker_size)
        
        # Load speaker1
        speaker1_clip = load_speaker_clip(
            config['speaker1_video_path'],
            final_video_duration,
            (speaker1_x, speaker_y_position),
            speaker_size,
            circle_mask
        )
        logger.info(f"Speaker1 clip duration: {speaker1_clip.duration}, Target duration: {final_video_duration}")
        
        # Load speaker2
        speaker2_clip = load_speaker_clip(
            config['speaker2_video_path'],
            final_video_duration,
            (speaker2_x, speaker_y_position),
            speaker_size,
            circle_mask
        )
        logger.info(f"Speaker2 clip duration: {speaker2_clip.duration}, Target duration: {final_video_duration}")

        # Ensure clips are looped to exact duration
        background = background.loop(duration=final_video_duration)
        speaker1_clip = speaker1_clip.loop(duration=final_video_duration)
        speaker2_clip = speaker2_clip.loop(duration=final_video_duration)
        
        logger.info(f"After looping - Background: {background.duration}, Speaker1: {speaker1_clip.duration}, Speaker2: {speaker2_clip.duration}")
        
        # Circular background behind speakers
        circle_bg = ColorClip((speaker_size, speaker_size), color=(128, 128, 128)).set_mask(circle_mask)
        circle_bg1 = circle_bg.set_position((speaker1_x, speaker_y_position)).set_duration(final_video_duration)
        circle_bg2 = circle_bg.set_position((speaker2_x, speaker_y_position)).set_duration(final_video_duration)
        
        # --- Text clips: title, subtitle, footer ---
        title_clip = (
            TextClip(
                request_dict['title'],
                fontsize=config['title_font_size'],
                color=config['title_font_color'],
                font=config['title_font_name']
            )
            .set_position(('center', config['resolution'][1] * 0.15))
            .set_duration(final_video_duration)
        )
        
        subtitle_clip = (
            TextClip(
                request_dict['sub_title'],
                fontsize=config['subtitle_font_size'],
                color=config['subtitle_font_color'],
                font=config['subtitle_font_name']
            )
            .set_position(('center', config['resolution'][1] * 0.25))
            .set_duration(final_video_duration)
        )
        
        # Add a dark background behind the footer text for better visibility
        footer_height = 60
        footer_y = config['resolution'][1] * 0.85
        
        footer_bg = (
            ColorClip((config['resolution'][0], footer_height), color=(0, 0, 0))
            .set_opacity(0.7)
            .set_position(('center', footer_y))
            .set_duration(final_video_duration)
        )

        # Calculate vertical center of footer background
        footer_text_y = footer_y + (footer_height - config['footer_settings_font_size']) / 2

        footer_clip = (
            TextClip(
                config['footer_settings_text'],
                fontsize=config['footer_settings_font_size'],
                color=config['footer_settings_font_color'],
                font=config['footer_settings_font_name'],
                size=(config['resolution'][0] - 40, None),  # Add some padding
                method='caption',
                align='center'
            )
            .set_position(('center', footer_text_y))
            .set_duration(final_video_duration)
        )
        
        # Speaker names
        name_y_position = speaker_y_position + speaker_size + 5
        name_fontsize = config.get('speaker_font_size', 30)
        text_bg_height = config.get('speaker_box_height', 50)
        text_bg_width = config.get('speaker_box_width', speaker_size)
        
        # Calculate vertical center position for text within background box
        text_y_position = name_y_position + (text_bg_height - name_fontsize) / 2

        text_bg = ColorClip((text_bg_width, text_bg_height), color=(0, 0, 0)).set_opacity(0.7)
        text_bg1 = text_bg.set_position((speaker1_x, name_y_position)).set_duration(final_video_duration)
        text_bg2 = text_bg.set_position((speaker2_x, name_y_position)).set_duration(final_video_duration)

        speaker1_name_clip = (
            TextClip(
                config['voice_settings_speaker1_name'],
                fontsize=name_fontsize,
                color=config.get('speaker_font_color', 'white'),
                font=config.get('speaker_font', 'Arial-Bold'),
                stroke_color=config.get('speaker_stoke_color', 'black'),
                stroke_width=1,
                size=(text_bg_width, None),
                method='caption',
                align='center'
            )
            .set_position((speaker1_x, text_y_position))
            .set_duration(final_video_duration)
        )
        
        speaker2_name_clip = (
            TextClip(
                config['voice_settings_speaker2_name'],
                fontsize=name_fontsize,
                color=config.get('speaker_font_color', 'white'),
                font=config.get('speaker_font', 'Arial-Bold'),
                stroke_color=config.get('speaker_stoke_color', 'black'),
                stroke_width=1,
                size=(text_bg_width, None),
                method='caption',
                align='center'
            )
            .set_position((speaker2_x, text_y_position))
            .set_duration(final_video_duration)
        )
        
        # --- Background music ---
        background_music_clip = AudioFileClip(config['background_music_path'])
        
        # Helper to loop or cut audio
        def audio_loop(audioclip, duration):
            from moviepy.audio.fx.all import audio_loop
            return audio_loop(audioclip, duration=duration)
        
        bg_music = audio_loop(background_music_clip, final_video_duration).volumex(config['bg_music_volume'])
        
        # Build final audio track
        final_audio = CompositeAudioClip([
            bg_music.set_duration(final_video_duration),
            voiceover_clip.volumex(config['voiceover_volume']).set_duration(final_video_duration)
        ])
        
        # Combine all visual clips
        clips = [
            background,
            overlay,
            circle_bg1,
            circle_bg2,
            speaker1_clip,
            speaker2_clip,
            text_bg1,
            text_bg2,
            title_clip,
            subtitle_clip,
            speaker1_name_clip,
            speaker2_name_clip,
            footer_bg,  # Add the dark background first
            footer_clip,  # Then add the footer text on top
        ]
        
        final_video = CompositeVideoClip(clips, size=config['resolution']).set_audio(final_audio)
        logger.info(f"Final composite video duration: {final_video.duration}, Target duration: {final_video_duration}")
        
        # Ensure final video is exactly as long as the audio
        final_video = final_video.set_duration(final_video_duration)
        logger.info(f"Final video duration after set_duration: {final_video.duration}")
        
        # Fade out in the last fade_duration seconds
        # (This does not cut the audio; it just fades volume and video.)
        final_video = final_video.fx(vfx.fadeout, fade_duration)
        
        full_output_path = os.path.join(output_dir, output_filename)
        
        final_video.write_videofile(
            full_output_path,
            fps=config['fps'],
            codec=config['codec'],
            audio_codec=config['audio_codec'],
            threads=config['threads'],
            preset=config['preset']
        )
        
        # Optionally create thumbnails
        thumbnail_paths = None
        if config.get('create_thumbnails'):
            thumbnail_paths = create_thumbnails(
                full_output_path,
                thumbnails_dir=config['thumbnails_output_dir']
            )
        
        logger.info(f"Podcast short video saved to: {full_output_path}")
        return full_output_path, thumbnail_paths
    
    except Exception as e:
        logger.exception(f"Error in create_podcast_short_video: {str(e)}")
        raise



def create_bumper_hygen_short_video(
    audio_path: Optional[str],
    welcome_audio_path: Optional[str],
    config: dict,
    request_dict: dict,
    duration: int = 5
) -> Tuple[str, Optional[List[str]]]:
    """
    Creates a podcast intro video that displays:
      - Two circular speaker "videos" (which can each be images or videos) side by side
      - A background (which can be an image or a video)
      - Background music
      - Optional voiceover
      - Title, subtitle, and footer text

    Ensures the final video duration matches the chosen audio source:
    - If welcome_audio_path is specified and `config['use_welcome_audio']` is True,
      use that audio as the primary voiceover
    - Otherwise, if `audio_path` is provided, use that
    - If neither is provided (or found), use only background music
    A fade-out is applied in the last few seconds **without cutting** the audio short.
    """
    import moviepy.video.fx.all as vfx  # For fadeout, etc.

    fade_duration = 1.5  # Duration of the fade-out at the end of the video

  
    try:
   

        logger.debug("\nStarting create_podcast_short_video with parameters:")
        logger.debug(f"Background path: {config['background_image_path']}")
        logger.debug(f"Resolution: {config['resolution']}")

        # --- Basic validations ---
        background_path = config['hygen_bumper_background_path']
        if not background_path:
            raise ValueError("Background path is None.")
        if not os.path.exists(background_path):
            raise FileNotFoundError(f"Background not found: {background_path}")
        if not os.path.isfile(background_path):
            raise ValueError(f"Background path is not a file: {background_path}")

        # Validate other required files
        required_files = [
            (config['hygen_bumper_background_path'], "background video"),
            (config['hygen_bumper_background_music_path'], "background music")
        ]
        for file_path, file_type in required_files:
            logger.debug(f"Checking {file_type} path: {file_path}")
            if not file_path:
                raise ValueError(f"{file_type.title()} path is None")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"{file_type.title()} file not found: {file_path}")
            if not os.path.isfile(file_path):
                raise ValueError(f"{file_type.title()} path is not a file: {file_path}")
            logger.debug(f"{file_type.title()} file OK: {file_path}")


        # --- Determine which audio will be used as "primary" voiceover, if any ---
        chosen_audio_path = None
        # if welcome_audio_path and os.path.exists(welcome_audio_path) and config.get('use_welcome_audio'):
        #     chosen_audio_path = welcome_audio_path
        # elif audio_path and os.path.exists(audio_path):
        #     chosen_audio_path = audio_path

        logger.debug(f"Chosen audio path: {chosen_audio_path}")

        # If we found a valid voiceover path, load it; otherwise, set voiceover to None
        voiceover_clip = None
        audio_duration = 2
        duration = 5
        background_music_clip = AudioFileClip(config['background_music_path'])

        # Decide how long the final video should be:
        # - If we have voiceover, match that duration
        # - If no voiceover, match the background music's duration
        final_video_duration =5
        

        # --- Extension sets we consider for images vs. video ---
        valid_image_exts = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}
        valid_video_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".mpeg", ".mpg"}

        # ---- 1) Create the background clip (image or video), loop/cut to final duration ----
        def load_background_clip(path, duration):
            _, ext = os.path.splitext(path.lower())
            if ext in valid_image_exts:
                try:
                    with Image.open(path) as img:
                        logger.debug(
                            f"Using background image: {path} | size: {img.size} | mode: {img.mode}"
                        )
                except Exception as e:
                    raise RuntimeError(f"Cannot open background image '{path}': {e}")

                # ImageClip for the entire duration
                clip = ImageClip(path).resize(config['resolution'])
                return clip.set_duration(duration)

            elif ext in valid_video_exts:
                # Load and prepare background video
                background = VideoFileClip(path)
                
                # Set position to center and resize to fill screen while maintaining aspect ratio
                background_w, background_h = background.size
                target_w, target_h = config['resolution']
                scale = max(target_w/background_w, target_h/background_h)
                new_size = (int(background_w*scale), int(background_h*scale))
                
                # If background video is shorter than needed duration, loop it
                if background.duration < duration:
                    n_loops = int(np.ceil(duration / background.duration))
                    clips = [background] * n_loops
                    background = concatenate_videoclips(clips)
                
                background = (background
                    .resize(new_size)
                    .set_position(("center", "center"))
                    .set_duration(duration))  # Set exact duration
                
                return background.without_audio()  # Remove audio from background
            else:
                raise ValueError(
                    f"Background file '{path}' has unrecognized extension '{ext}'. "
                    "Expected an image or a video."
                )

        background = load_background_clip(background_path, final_video_duration)

        # Optional overlay (semi-transparent black)
        overlay = ColorClip(config['resolution'], color=(0, 0, 0)).set_opacity(0.5)
        overlay = overlay.set_duration(final_video_duration)

        # --- Helper for circular mask ---
        def create_circular_mask(size):
            import numpy as np
            import cv2

            w, h = size
            mask = np.zeros((h, w, 1), dtype="uint8")
            center = (w // 2, h // 2)
            radius = min(center)
            cv2.circle(mask, center, radius, (255,), -1)
            return ImageClip(mask, ismask=True)

        # If 'speaker_size' is in config, use it; otherwise compute a default
        if 'speaker_size' in config and config['speaker_size']:
            speaker_size = config['speaker_size']
        else:
            speaker_size = min(config['resolution'][0] // 4, config['resolution'][1] // 3)

        circle_mask = create_circular_mask((speaker_size, speaker_size))

        # --- Function to load speaker clip (either an image or video) ---
        def load_speaker_clip(path, duration, position, size, mask):
            base, ext = os.path.splitext(path.lower())
            if ext in valid_image_exts:
                clip = ImageClip(path).set_duration(duration)
            elif ext in valid_video_exts:
                clip = VideoFileClip(path)
                logger.info(f"Loading speaker clip: {path}, Original duration: {clip.duration}")
                
                # If video is shorter than needed duration, calculate number of loops needed
                if clip.duration < duration:
                    n_loops = int(np.ceil(duration / clip.duration))
                    logger.info(f"Video needs {n_loops} loops to reach {duration}s")
                    clips = [clip] * n_loops
                    clip = concatenate_videoclips(clips)
                    logger.info(f"After concatenating {n_loops} clips, duration: {clip.duration}")
                
                # Set exact duration after looping
                clip = clip.set_duration(duration)
                logger.info(f"Final clip duration after set_duration: {clip.duration}")
            else:
                raise ValueError(f"Speaker clip '{path}' has invalid extension '{ext}'.")

            clip = (
                clip
                .resize((size, size))
                .set_mask(mask)
                .set_position(position)
                .set_duration(duration)  # Ensure final duration is exact
            )
            return clip

        # Speaker positions
        speaker_y_position = int(config['resolution'][1] * 0.4)
        spacing = speaker_size * 1.5
        center_x = config['resolution'][0] // 2
        speaker1_x = int(center_x - spacing)
        speaker2_x = int(center_x + spacing - speaker_size)

        # Load speaker1
        speaker1_clip = load_speaker_clip(
            config['speaker1_video_path'],
            final_video_duration,
            (speaker1_x, speaker_y_position),
            speaker_size,
            circle_mask
        )

        # Load speaker2
        speaker2_clip = load_speaker_clip(
            config['speaker2_video_path'],
            final_video_duration,
            (speaker2_x, speaker_y_position),
            speaker_size,
            circle_mask
        )

        # Circular background behind speakers
        circle_bg = ColorClip((speaker_size, speaker_size), color=(128, 128, 128)).set_mask(circle_mask)
        circle_bg1 = circle_bg.set_position((speaker1_x, speaker_y_position)).set_duration(final_video_duration)
        circle_bg2 = circle_bg.set_position((speaker2_x, speaker_y_position)).set_duration(final_video_duration)

        # --- Text clips: title, subtitle, footer ---
        title_clip = (
            TextClip(
                request_dict['title'],
                fontsize=config['title_font_size'],
                color=config['title_font_color'],
                font=config['title_font_name']
            )
            .set_position(('center', config['resolution'][1] * 0.15))
            .set_duration(final_video_duration)
        )

        subtitle_clip = (
            TextClip(
                request_dict['sub_title'],
                fontsize=config['subtitle_font_size'],
                color=config['subtitle_font_color'],
                font=config['subtitle_font_name']
            )
            .set_position(('center', config['resolution'][1] * 0.25))
            .set_duration(final_video_duration)
        )

        # Dark overlay behind footer
        footer_height = 60
        footer_y = config['resolution'][1] * 0.85
        
        footer_bg = (
            ColorClip((config['resolution'][0], footer_height), color=(0, 0, 0))
            .set_opacity(0.7)
            .set_position(('center', footer_y))
            .set_duration(final_video_duration)
        )

        # Calculate vertical center of footer background
        footer_text_y = footer_y + (footer_height - config['footer_settings_font_size']) / 2

        footer_clip = (
            TextClip(
                config['footer_settings_text'],
                fontsize=config['footer_settings_font_size'],
                color=config['footer_settings_font_color'],
                font=config['footer_settings_font_name'],
                size=(config['resolution'][0] - 40, None),
                method='caption',
                align='center'
            )
            .set_position(('center', footer_text_y))
            .set_duration(final_video_duration)
        )

        # Speaker names
        name_y_position = speaker_y_position + speaker_size + 5
        name_fontsize = config.get('speaker_font_size', 18)
        text_bg_height = config.get('speaker_box_height', 40)
        text_bg_width = config.get('speaker_box_width', speaker_size)

        # Calculate vertical center position for text within background box
        text_y_position = name_y_position + (text_bg_height - name_fontsize) / 2

        text_bg = ColorClip((text_bg_width, text_bg_height), color=(0, 0, 0)).set_opacity(0.7)
        text_bg1 = text_bg.set_position((speaker1_x, name_y_position)).set_duration(final_video_duration)
        text_bg2 = text_bg.set_position((speaker2_x, name_y_position)).set_duration(final_video_duration)

        speaker1_name_clip = (
            TextClip(
                config['voice_settings_speaker1_name'],
                fontsize=name_fontsize,
                color=config.get('speaker_font_color', 'white'),
                font=config.get('speaker_font', 'Arial-Bold'),
                stroke_color=config.get('speaker_stoke_color', 'black'),
                stroke_width=1,
                size=(text_bg_width, None),
                method='caption',
                align='center'
            )
            .set_position((speaker1_x, text_y_position))
            .set_duration(final_video_duration)
        )

        speaker2_name_clip = (
            TextClip(
                config['voice_settings_speaker2_name'],
                fontsize=name_fontsize,
                color=config.get('speaker_font_color', 'white'),
                font=config.get('speaker_font', 'Arial-Bold'),
                stroke_color=config.get('speaker_stoke_color', 'black'),
                stroke_width=1,
                size=(text_bg_width, None),
                method='caption',
                align='center'
            )
            .set_position((speaker2_x, text_y_position))
            .set_duration(final_video_duration)
        )

        # Helper to loop or cut audio
        def audio_loop(audioclip, duration):
            from moviepy.audio.fx.all import audio_loop
            return audio_loop(audioclip, duration=duration)

        # Prepare/loop background music to match final video duration
        bg_music = audio_loop(background_music_clip, final_video_duration).volumex(config['bg_music_volume'])

        # Build the final audio track
        if voiceover_clip:
            final_audio = CompositeAudioClip([
                bg_music.set_duration(final_video_duration),
                voiceover_clip.volumex(config['voiceover_volume']).set_duration(final_video_duration)
            ])
        else:
            # No voiceover, just background music
            final_audio = bg_music.set_duration(final_video_duration)

        # Combine all visual clips
        clips = [
            background,
            overlay,
            circle_bg1,
            circle_bg2,
            speaker1_clip,
            speaker2_clip,
            text_bg1,
            text_bg2,
            title_clip,
            subtitle_clip,
            speaker1_name_clip,
            speaker2_name_clip,
            footer_bg,
            footer_clip,
        ]

        final_video = CompositeVideoClip(clips, size=config['resolution']).set_audio(final_audio)
        logger.info(f"Final composite video duration: {final_video.duration}, Target duration: {final_video_duration}")

        # Ensure final video is exactly as long as the audio
        final_video = final_video.set_duration(final_video_duration)
        logger.info(f"Final video duration after set_duration: {final_video.duration}")

        # Fade out in the last fade_duration seconds (video+audio)
        final_video = final_video.fx(vfx.fadeout, fade_duration)
        output_dir = config['output_dir']
        output_filename = config['hygen_bumper_output_filename']
        #let us add the current date and time to the output filename
        from datetime import datetime
        output_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{output_filename}"
        full_output_path = os.path.join(output_dir, output_filename)
        final_video.write_videofile(
            full_output_path,
            fps=config['fps'],
            codec=config['codec'],
            audio_codec=config['audio_codec'],
            threads=config['threads'],
            preset=config['preset']
        )

        # Optionally create thumbnails
        #let us trim video as per the duration
        final_duration = (config['hygen_bumper_duration'] if config['hygen_bumper_duration'] else 5)    
        final_video = final_video.subclip(0, final_duration)
    
  
        
        logger.info(f"Podcast short video saved to: {full_output_path}")
     
        return full_output_path

    except Exception as e:
        logger.exception(f"Error in create_podcast_short_video: {str(e)}")
        raise
