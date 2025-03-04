import os
import tempfile
import random
import base64
import requests
import sys
import traceback
import numpy as np
from dotenv import load_dotenv
from utils.file_writer import get_output_path
from utils.open_ai_utils import create_image_prompt, transcribe_audio
load_dotenv()

import moviepy.editor as mp
from moviepy.audio.fx.all import audio_loop
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.video.fx.resize import resize

from PIL import Image, ImageDraw, ImageFont, ImageColor
import speech_recognition as sr
import cv2  # For OpenCV-based resizing

import logging
import colorlog
import json

# Setup colored logger
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)-8s%(reset)s %(message)s',
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    }
))
logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

########################################################################
# IMAGE & AUDIO SPLIT FUNCTIONS
########################################################################
def generate_getimage_and_save_image(prompt, output_path):
    url = "https://api.getimg.ai/v1/stable-diffusion-xl/text-to-image"
    
    # Request payload

    prompt = "Generate a professional, high-quality image that represents: " + prompt
    api_key = os.environ.get("GETIMAGE_API_KEY")
    payload = {
        "prompt": prompt,
        "width": 1280,
        "height": 720
    }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    
    try:
        logger.info("Requesting image generation for prompt: %s", prompt)
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        image_data = response_data.get("image")
        if image_data:
            image_binary = base64.b64decode(image_data)
            with open(output_path, 'wb') as image_file:
                image_file.write(image_binary)
            logger.info("Image generated successfully for prompt.")
            return output_path
        else:
            logger.warning("Image data not found in the response.")
            return None
    except requests.exceptions.RequestException as e:
        logger.error("Error occurred during API request: %s", e)
        traceback.print_exc()
        return None
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        traceback.print_exc()
        return None

def generate_image_from_text(context, topic, segment_description, resolution, UseOpenAI=True):
    """
    Generate a simple image with the given text centered on it.
    """
    temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
 
    if UseOpenAI:
        text = create_image_prompt(context, topic, segment_description)      
    else:
        text = segment_description
    result = generate_getimage_and_save_image(text, temp_file.name)
    if result is None:
        width, height = resolution
        img = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        text_width, text_height = draw.textsize(text, font=font)
        position = ((width - text_width) // 2, (height - text_height) // 2)
        draw.text(position, text, fill="black", font=font)
        img.save(temp_file.name)
        logger.info("Using fallback text image generation.")
    return temp_file.name

def transcribe_audio_segment(audio_clip, UseOpenAI=True):
    """
    Write the audio_clip to a temporary WAV file and transcribe it using Google Speech Recognition.
    """
    if UseOpenAI:
        response = transcribe_audio(audio_clip)
        # Handle both string and object responses
        if hasattr(response, 'text'):
            return response.text
        return response
    else:
        recognizer = sr.Recognizer()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_audio_path = temp_audio.name
        audio_clip.write_audiofile(temp_audio_path, logger=None)
        
        with sr.AudioFile(temp_audio_path) as source:
            audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            logger.info("Transcription successful: %s", text)
        except sr.UnknownValueError:
            text = ""
            logger.warning("Google Speech Recognition could not understand audio.")
        except sr.RequestError as e:
            text = ""
            logger.error("Request error from Google Speech Recognition: %s", e)
        os.unlink(temp_audio_path)
        return text

########################################################################
# VIDEO TRANSITION & OVERLAY FUNCTIONS (unchanged)
########################################################################
def add_logo_and_footer(clip, logo_path=None, logo_size=(100, 100), logo_position='top-right', footer_text=None):
    """
    Add logo and footer text to a video clip.
    """
    final_clip = clip
    
    if logo_path and os.path.exists(logo_path):
        logo = mp.ImageClip(logo_path).resize(logo_size)
        video_width, video_height = clip.size
        logo_width, logo_height = logo_size
        margin = 20
        
        if logo_position == 'top-left':
            pos = (margin, margin)
        elif logo_position == 'top-right':
            pos = (video_width - logo_width - margin, margin)
        elif logo_position == 'bottom-left':
            pos = (margin, video_height - logo_height - margin)
        else:  # bottom-right
            pos = (video_width - logo_width - margin, video_height - logo_height - margin)
        
        logo = logo.set_duration(clip.duration)
        final_clip = mp.CompositeVideoClip([final_clip, logo.set_position(pos)])
    
    if footer_text:
        txt_clip = mp.TextClip(
            footer_text,
            fontsize=30,
            color='white',
            font='Arial',
            size=(clip.size[0], None),
            method='caption'
        ).set_duration(clip.duration)
        
        txt_pos = ('center', clip.size[1] - txt_clip.size[1] - 20)
        txt_bg = mp.ColorClip(
            size=(clip.size[0], txt_clip.size[1] + 40),
            color=(0, 0, 0)
        ).set_opacity(0.6).set_duration(clip.duration)
        txt_bg = txt_bg.set_position(('center', clip.size[1] - txt_bg.size[1]))
        final_clip = mp.CompositeVideoClip([final_clip, txt_bg, txt_clip.set_position(txt_pos)])
    
    return final_clip

def apply_random_transition(clip, duration, direction=None, transition_type=None):
    """
    Apply either a fade or zoom-in transition effect to a video clip.
    """
    if transition_type is None:
        transition_type = random.choice(['fade', 'zoom-in'])
    
    if transition_type == 'fade':
        return fadein(clip, duration)
    else:  # zoom-in only
        w, h = clip.size

        def make_frame(t):
            # Always zoom in from 1.5x to 1x
            zoom_factor = max(1.0, 1.5 - 0.5 * t)  # Ensure zoom factor never goes below 1.0
            frame = clip.get_frame(t)
            zoomed_w = max(w, int(w * zoom_factor))  # Ensure width never goes below original
            zoomed_h = max(h, int(h * zoom_factor))  # Ensure height never goes below original
            
            # Resize the frame
            resized = cv2.resize(frame, (zoomed_w, zoomed_h))
            
            # Calculate center crop coordinates
            x_start = (zoomed_w - w) // 2
            y_start = (zoomed_h - h) // 2
            
            # Return the center portion
            return resized[y_start:y_start+h, x_start:x_start+w]

        zoomed_clip = clip.fl(lambda gf, t: make_frame(t))
        zoomed_clip.size = clip.size
        return zoomed_clip

def create_transition_sequence(clips, transition_type=None, transition_duration=1.0):
    """
    Create a sequence of clips with transitions.
    """
    if not clips:
        logger.warning("No clips provided for transition sequence")
        return []
        
    final_transition_type = transition_type or random.choice(['fade', 'zoom-in'])
    logger.info("Using %s transitions", final_transition_type)
    
    final_clips = []
    for i, clip in enumerate(clips):
        current_clip = clip
        if i > 0:  # Apply transition to all clips except the first one
            current_clip = apply_random_transition(
                current_clip,
                transition_duration,
                transition_type=final_transition_type
            )
        final_clips.append(current_clip)
    
    return final_clips

########################################################################
# MAIN FUNCTION: create_video_with_images
########################################################################
def create_video_with_images(audio_path, config, resolution, job_id, request_dict, show_speakers=False):
    """
    Create a video with transitions between images generated from audio segments.
    
    This function:
      1. Loads the voice-over audio and splits it into segments (using config['voice_split_duration']).
      2. For each segment, it transcribes the audio and generates an image from the text.
      3. Creates image clips for each segment (placed at the appropriate start time).
      4. Applies transitions between the image clips.
      5. Composites the clips, overlays logo/footer, adds background music, and (optionally) speaker overlays.
    
    Parameters:
      - audio_path: Path to the voice-over audio.
      - config: A dictionary containing configuration keys (e.g. background_music_path, voice_split_duration,
                speaker paths/names, logo settings, etc.)
      - resolution: Tuple (width, height) for the video.
      - request_dict: Additional request parameters.
      - show_speakers (bool): Flag indicating whether to add speaker overlays. Defaults to False.
    
    Returns:
      The path to the final video file.
    """
    try:
        # Create temporary output file path
        # let us get the output path from the file writer
        output_path, output_dir = get_output_path(
            filename=config.get('main_video_filename', 'video.mp4'),
            profile_name=request_dict['profile_name'],
            customer_id=request_dict['customer_id'],
            job_id=str(job_id)
        )
        image_clips = []

        # Load voice-over audio
        voiceover_audio = mp.AudioFileClip(audio_path)
        total_duration = voiceover_audio.duration
        voice_split_duration = config.get('voice_split_duration', 30)
        num_splits = int(total_duration // voice_split_duration)
        if total_duration % voice_split_duration > 0:
            num_splits += 1
        logger.info("Total voice-over duration: %.2fs in %d segments", total_duration, num_splits)
        
        # Generate an image for each audio segment
        for i in range(num_splits):
            start_time = i * voice_split_duration
            end_time = min((i + 1) * voice_split_duration, total_duration)
            segment_duration = end_time - start_time
            logger.info("Processing segment %d: %.2fs to %.2fs", i+1, start_time, end_time)
            segment_audio = voiceover_audio.subclip(start_time, end_time)
            text = transcribe_audio_segment(segment_audio)
            if not text:
                text = f"Segment {i+1}"
            logger.info("Transcribed text: %s", text)
            context = config.get('context')
            context_data = ""
            if context and os.path.exists(context):
                with open(context, 'r') as f:
                    context_data = f.read()[:2000]
            topic = config.get('topic')
            image_path = generate_image_from_text(context_data, topic, text, resolution)
            img_clip = mp.ImageClip(image_path, duration=segment_duration).set_start(start_time)
            image_clips.append(img_clip)
        
        logger.info("Applying transitions...")
        final_clips = create_transition_sequence(image_clips, transition_type=config.get('transition_type'), transition_duration=config.get('transition_duration', 1.0))
        
        logger.info("Compositing video clips...")
        base_video = mp.CompositeVideoClip(final_clips, size=resolution).set_duration(total_duration)
        logo_path = config.get('logo_settings_main_logo_path') or config.get('logo_path')
        logo_position = config.get('logo_settings_logo_position') or config.get('logo_position', 'top-right')
        base_video = add_logo_and_footer(
            base_video, 
            logo_path=logo_path,
            logo_size=config.get('logo_size', (100, 100)),
            logo_position=logo_position,
            footer_text=config.get('footer_text')
        )
        
        logger.info("Processing background music...")
        bg_music_clip = mp.AudioFileClip(config['background_music_path']).volumex(config.get('bg_music_volume', 0.1))
        if bg_music_clip.duration < total_duration:
            bg_music_clip = audio_loop(bg_music_clip, duration=total_duration)
        else:
            bg_music_clip = bg_music_clip.subclip(0, total_duration)
        logger.info("Combining audio tracks...")
        final_audio = mp.CompositeAudioClip([bg_music_clip, voiceover_audio])
        base_video = base_video.set_audio(final_audio)
        
        # --- Add speaker overlays if requested and provided ---
        if show_speakers and (config.get('speaker1_video_path') or config.get('speaker2_video_path')):
            if config.get('speaker_size') is None:
                config['speaker_size'] = min(resolution[0] // 4, resolution[1] // 3)
            
            def create_circular_mask(size):
                import numpy as np
                mask = np.zeros((size, size, 1), dtype="uint8")
                center = (size // 2, size // 2)
                radius = min(center)
                cv2.circle(mask, center, radius, (255,), -1)
                return mp.ImageClip(mask, ismask=True)
            
            circle_mask = create_circular_mask(config['speaker_size'])
            
            def load_speaker_clip(path, duration, position, size, mask):
                base, ext = os.path.splitext(path.lower())
                valid_image_exts = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}
                valid_video_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".mpeg", ".mpg"}
                if ext in valid_image_exts:
                    clip = mp.ImageClip(path).set_duration(duration)
                elif ext in valid_video_exts:
                    clip = mp.VideoFileClip(path)
                    if clip.duration < duration:
                        clip = clip.loop(duration=duration)
                    else:
                        clip = clip.subclip(0, duration)
                else:
                    raise ValueError(f"Speaker clip '{path}' has invalid extension '{ext}'.")
                return clip.resize((size, size)).set_mask(mask).set_position(position).set_duration(duration)
            
            speaker_overlays = []
            margin = 20
            if config.get('speaker1_video_path') and config.get('speaker2_video_path'):
                speaker_y_position = int(resolution[1] * 0.4)
                spacing = int(config['speaker_size'] * 1.5)
                center_x = resolution[0] // 2
                speaker1_x = int(center_x - spacing)
                speaker2_x = int(center_x + spacing - config['speaker_size'])
                speaker1_clip = load_speaker_clip(config['speaker1_video_path'], total_duration, (speaker1_x, speaker_y_position), config['speaker_size'], circle_mask)
                speaker2_clip = load_speaker_clip(config['speaker2_video_path'], total_duration, (speaker2_x, speaker_y_position), config['speaker_size'], circle_mask)
                speaker_overlays.extend([speaker1_clip, speaker2_clip])
                name_y_position = speaker_y_position + config['speaker_size'] + 5
                text_bg_width = config['speaker_size']
                text_bg_height = int(config['speaker_font_size'] * 1.5)
                speaker_box_rgb = ImageColor.getrgb(config['speaker_box_color'])
                text_bg = mp.ColorClip((text_bg_width, text_bg_height), color=speaker_box_rgb)\
                            .set_opacity(config['speaker_box_opacity']).set_duration(total_duration)
                text_bg1 = text_bg.set_position((speaker1_x, name_y_position))
                text_bg2 = text_bg.set_position((speaker2_x, name_y_position))
                speaker_overlays.extend([text_bg1, text_bg2])
                if config.get('voice_settings_speaker1_name'):
                    speaker1_name_clip = mp.TextClip(
                        config['voice_settings_speaker1_name'],
                        fontsize=config['speaker_font_size'],
                        color=config['speaker_font_color'],
                        font=config['speaker_font'],
                        stroke_color='black',
                        stroke_width=1,
                        size=(text_bg_width, None),
                        method='caption',
                        align='center'
                    ).set_position((speaker1_x, name_y_position)).set_duration(total_duration)
                    speaker_overlays.append(speaker1_name_clip)
                if config.get('voice_settings_speaker2_name'):
                    speaker2_name_clip = mp.TextClip(
                        config['voice_settings_speaker2_name'],
                        fontsize=config['speaker_font_size'],
                        color=config['speaker_font_color'],
                        font=config['speaker_font'],
                        stroke_color='black',
                        stroke_width=1,
                        size=(text_bg_width, None),
                        method='caption',
                        align='center'
                    ).set_position((speaker2_x, name_y_position)).set_duration(total_duration)
                    speaker_overlays.append(speaker2_name_clip)
            else:
                if config.get('single_speaker_position') in ["bottom-left", "bottom-right"]:
                    speaker_x = margin if config['single_speaker_position'] == "bottom-left" else resolution[0] - config['speaker_size'] - margin
                    speaker_y = resolution[1] - config['speaker_size'] - margin
                else:
                    if config.get('logo_settings_main_logo_path') and os.path.exists(config['logo_settings_main_logo_path']):
                        if config.get('logo_settings_logo_position') in ["top-left", "bottom-left"]:
                            speaker_x = resolution[0] - config['speaker_size'] - margin
                        elif config.get('logo_settings_logo_position') in ["top-right", "bottom-right"]:
                            speaker_x = margin
                        else:
                            speaker_x = resolution[0] - config['speaker_size'] - margin
                        speaker_y = margin if config['logo_settings_logo_position'].startswith("top") else resolution[1] - config['speaker_size'] - margin
                    else:
                        speaker_x = resolution[0] - config['speaker_size'] - margin
                        speaker_y = resolution[1] - config['speaker_size'] - margin
                chosen_speaker_path = config.get('speaker1_video_path') if config.get('speaker1_video_path') else config.get('speaker2_video_path')
                speaker_clip = load_speaker_clip(chosen_speaker_path, total_duration, (speaker_x, speaker_y), config['speaker_size'], circle_mask)
                speaker_overlays.append(speaker_clip)
                name_y = speaker_y + config['speaker_size'] + 5
                text_bg_width = config['speaker_size']
                text_bg_height = int(config['speaker_font_size'] * 1.5)
                speaker_box_rgb = ImageColor.getrgb(config['speaker_box_color'])
                text_bg = mp.ColorClip((text_bg_width, text_bg_height), color=speaker_box_rgb)\
                            .set_opacity(config['speaker_box_opacity']).set_duration(total_duration)
                text_bg = text_bg.set_position((speaker_x, name_y))
                speaker_overlays.append(text_bg)
                chosen_name = config.get('voice_settings_speaker1_name') if config.get('voice_settings_speaker1_name') else config.get('voice_settings_speaker2_name')
                if chosen_name:
                    name_clip = mp.TextClip(
                        chosen_name,
                        fontsize=config['speaker_font_size'],
                        color=config['speaker_font_color'],
                        font=config['speaker_font'],
                        stroke_color='black',
                        stroke_width=1,
                        size=(text_bg_width, None),
                        method='caption',
                        align='center'
                    ).set_position((speaker_x, name_y)).set_duration(total_duration)
                    speaker_overlays.append(name_clip)
            base_video = mp.CompositeVideoClip([base_video] + speaker_overlays, size=resolution)
        
        logger.info("Writing final video to %s", output_path)
        base_video.write_videofile(output_path, codec=config.get('codec'), audio_codec=config.get('audio_codec'), fps=config.get('fps'))
        logger.info("Video creation complete.")
        
        # (Optional) Clean up temporary image files if needed...
        return output_path
    except Exception as e:
        logger.error("Error creating video: %s", e)
        traceback.print_exc()
        return None
