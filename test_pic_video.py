import os
import tempfile
import random
import base64
import requests
import sys
import traceback
from dotenv import load_dotenv
load_dotenv()

import moviepy.editor as mp
from moviepy.audio.fx.all import audio_loop
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.video.fx.resize import resize

from PIL import Image, ImageDraw, ImageFont, ImageColor
import speech_recognition as sr
import cv2  # For OpenCV-based resizing

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
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        image_data = response_data.get("image")
        if image_data:
            image_binary = base64.b64decode(image_data)
            with open(output_path, 'wb') as image_file:
                image_file.write(image_binary)
            print(f"Image generated successfully for prompt: {prompt}")
            return output_path
        else:
            print("Image data not found in the response.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error occurred during API request: {e}")
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()
        return None

def generate_image_from_text(text, resolution):
    """
    Generate a simple image with the given text centered on it.
    """
    temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
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
        print("Using fallback text image generation")
    return temp_file.name

def transcribe_audio_segment(audio_clip):
    """
    Write the audio_clip to a temporary WAV file and transcribe it using Google Speech Recognition.
    """
    recognizer = sr.Recognizer()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        temp_audio_path = temp_audio.name
    audio_clip.write_audiofile(temp_audio_path, logger=None)
    
    with sr.AudioFile(temp_audio_path) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        text = ""
    except sr.RequestError:
        text = ""
    
    os.unlink(temp_audio_path)
    return text

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
    Apply a random transition effect to a video clip.
    """
    if transition_type is None:
        transition_type = random.choice(['fade', 'zoom'])
    
    if transition_type == 'fade':
        return fadein(clip, duration)
    else:  # zoom transition
        zoom_type = random.choice(['in', 'out']) if direction is None else direction
        w, h = clip.size

        def make_frame(t):
            if zoom_type == 'in':
                zoom_factor = 1.5 - 0.5 * t  # from 1.5x to 1x
            else:
                zoom_factor = 1 + 0.5 * t  # from 1x to 1.5x

            frame = clip.get_frame(t)
            # Ensure dimensions are at least 1 pixel
            zoomed_w = max(1, int(w * zoom_factor))
            zoomed_h = max(1, int(h * zoom_factor))
            x_offset = (zoomed_w - w) // 2
            y_offset = (zoomed_h - h) // 2
            resized = cv2.resize(frame, (zoomed_w, zoomed_h))
            if x_offset > 0 and y_offset > 0:
                return resized[y_offset:y_offset+h, x_offset:x_offset+w]
            else:
                return resized

        zoomed_clip = clip.fl(lambda gf, t: make_frame(t))
        zoomed_clip.size = clip.size  # ensure the size remains correct
        return zoomed_clip

def create_transition_sequence(clips, transition_type=None, transition_duration=1.0):
    """
    Create a sequence of clips with transitions.
    """
    if not clips:
        return []
        
    final_transition_type = transition_type or random.choice(['fade', 'zoom'])
    direction = random.choice(['in', 'out']) if final_transition_type == 'zoom' else None
        
    print(f"Using {final_transition_type} transitions" + (f" with direction: {direction}" if direction else ""))
    
    final_clips = []
    for i, clip in enumerate(clips):
        current_clip = clip.copy()
        if transition_duration > 0:
            if i > 0:
                current_clip = apply_random_transition(
                    current_clip,
                    transition_duration,
                    direction=direction,
                    transition_type=final_transition_type
                )
            if i < len(clips) - 1:
                current_clip = fadeout(current_clip, transition_duration)
        final_clips.append(current_clip)
    
    return final_clips

def create_video(voice_over, bg_music, output_file, resolution, bg_volume=0.3, 
                 voice_split_duration=5, logo_path=None, logo_size=(100, 100), 
                 logo_position='top-right', footer_text=None, transition_duration=1.0,
                 transition_type=None,
                 # --- New speaker parameters ---
                 speaker1_path=None,
                 speaker2_path=None,
                 speaker1_name=None,
                 speaker2_name=None,
                 speaker_size=None,
                 # --- New speaker style parameters ---
                 speaker_font="Arial-Bold",
                 speaker_font_size=36,
                 speaker_font_color="white",
                 speaker_box_color="black",
                 speaker_box_opacity=0.7,
                 # --- New single speaker position parameter ---
                 single_speaker_position=None):
    """
    Create a video with transitions between images and optional speaker overlays.
    
    - Speaker images/videos are optional.
    - If only one speaker is provided, it will be placed on the side opposite to the logo (if a logo is provided)
      or default to the bottom-right corner, unless an explicit single_speaker_position is set (e.g. "bottom-left" or "bottom-right").
    - Footer text is optional.
    
    Speaker style parameters:
      - speaker_font, speaker_font_size, speaker_font_color: controls the speaker name text.
      - speaker_box_color, speaker_box_opacity: controls the background box behind the speaker name.
    """
    try:
        # Load voice-over audio
        voiceover_audio = mp.AudioFileClip(voice_over)
        total_duration = voiceover_audio.duration

        num_splits = int(total_duration // voice_split_duration)
        if total_duration % voice_split_duration > 0:
            num_splits += 1

        image_clips = []
        print(f"Total voice-over duration: {total_duration:.2f}s in {num_splits} segments")

        for i in range(num_splits):
            start_time = i * voice_split_duration
            end_time = min((i + 1) * voice_split_duration, total_duration)
            segment_duration = end_time - start_time

            print(f"Processing segment {i + 1}: {start_time:.2f}s to {end_time:.2f}s")
            segment_audio = voiceover_audio.subclip(start_time, end_time)
            text = transcribe_audio_segment(segment_audio)
            if not text:
                text = f"Segment {i + 1}"
            print(f"Transcribed text: {text}")

            image_path = generate_image_from_text(text, resolution)
            img_clip = mp.ImageClip(image_path, duration=segment_duration).set_start(start_time)
            image_clips.append(img_clip)

        print("Applying transitions...")
        final_clips = create_transition_sequence(
            image_clips,
            transition_type=transition_type,
            transition_duration=transition_duration
        )

        print("Compositing video clips...")
        final_video = mp.CompositeVideoClip(final_clips, size=resolution).set_duration(total_duration)
        final_video = add_logo_and_footer(
            final_video,
            logo_path=logo_path,
            logo_size=logo_size,
            logo_position=logo_position,
            footer_text=footer_text
        )

        print("Processing background music...")
        bg_music_clip = mp.AudioFileClip(bg_music).volumex(bg_volume)
        if bg_music_clip.duration < total_duration:
            bg_music_clip = audio_loop(bg_music_clip, duration=total_duration)
        else:
            bg_music_clip = bg_music_clip.subclip(0, total_duration)

        print("Combining audio tracks...")
        final_audio = mp.CompositeAudioClip([bg_music_clip, voiceover_audio])
        final_video = final_video.set_audio(final_audio)

        # --- Add speaker clips if provided ---
        if (speaker1_path or speaker2_path):
            if speaker_size is None:
                speaker_size = min(resolution[0] // 4, resolution[1] // 3)
            
            def create_circular_mask(size):
                import numpy as np
                w = h = size
                mask = np.zeros((h, w, 1), dtype="uint8")
                center = (w // 2, h // 2)
                radius = min(center)
                cv2.circle(mask, center, radius, (255,), -1)
                return mp.ImageClip(mask, ismask=True)
            
            circle_mask = create_circular_mask(speaker_size)
            
            # Helper to load a speaker clip (image or video)
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
            
            # If both speakers are provided, use dual layout
            if speaker1_path and speaker2_path:
                speaker_y_position = int(resolution[1] * 0.4)
                spacing = int(speaker_size * 1.5)
                center_x = resolution[0] // 2
                speaker1_x = int(center_x - spacing)
                speaker2_x = int(center_x + spacing - speaker_size)
                
                speaker1_clip = load_speaker_clip(speaker1_path, total_duration, (speaker1_x, speaker_y_position), speaker_size, circle_mask)
                speaker2_clip = load_speaker_clip(speaker2_path, total_duration, (speaker2_x, speaker_y_position), speaker_size, circle_mask)
                
                speaker_overlays.extend([speaker1_clip, speaker2_clip])
                
                # Create background box for speaker names
                name_y_position = speaker_y_position + speaker_size + 5
                text_bg_width = speaker_size
                text_bg_height = int(speaker_font_size * 1.5)
                speaker_box_rgb = ImageColor.getrgb(speaker_box_color)
                text_bg = mp.ColorClip((text_bg_width, text_bg_height), color=speaker_box_rgb)\
                            .set_opacity(speaker_box_opacity).set_duration(total_duration)
                text_bg1 = text_bg.set_position((speaker1_x, name_y_position))
                text_bg2 = text_bg.set_position((speaker2_x, name_y_position))
                speaker_overlays.extend([text_bg1, text_bg2])
                
                if speaker1_name:
                    speaker1_name_clip = mp.TextClip(
                        speaker1_name,
                        fontsize=speaker_font_size,
                        color=speaker_font_color,
                        font=speaker_font,
                        stroke_color='black',
                        stroke_width=1,
                        size=(text_bg_width, None),
                        method='caption',
                        align='center'
                    ).set_position((speaker1_x, name_y_position)).set_duration(total_duration)
                    speaker_overlays.append(speaker1_name_clip)
                if speaker2_name:
                    speaker2_name_clip = mp.TextClip(
                        speaker2_name,
                        fontsize=speaker_font_size,
                        color=speaker_font_color,
                        font=speaker_font,
                        stroke_color='black',
                        stroke_width=1,
                        size=(text_bg_width, None),
                        method='caption',
                        align='center'
                    ).set_position((speaker2_x, name_y_position)).set_duration(total_duration)
                    speaker_overlays.append(speaker2_name_clip)
            else:
                # Only one speaker provided.
                if single_speaker_position in ["bottom-left", "bottom-right"]:
                    if single_speaker_position == "bottom-left":
                        speaker_x = margin
                    else:  # bottom-right
                        speaker_x = resolution[0] - speaker_size - margin
                    speaker_y = resolution[1] - speaker_size - margin
                else:
                    # Fallback logic: if logo exists, place speaker opposite the logo
                    if logo_path and os.path.exists(logo_path):
                        if logo_position in ["top-left", "bottom-left"]:
                            speaker_x = resolution[0] - speaker_size - margin
                        elif logo_position in ["top-right", "bottom-right"]:
                            speaker_x = margin
                        else:
                            speaker_x = resolution[0] - speaker_size - margin
                        if logo_position.startswith("top"):
                            speaker_y = margin
                        elif logo_position.startswith("bottom"):
                            speaker_y = resolution[1] - speaker_size - margin
                        else:
                            speaker_y = resolution[1] - speaker_size - margin
                    else:
                        speaker_x = resolution[0] - speaker_size - margin
                        speaker_y = resolution[1] - speaker_size - margin
                
                chosen_speaker_path = speaker1_path if speaker1_path else speaker2_path
                speaker_clip = load_speaker_clip(chosen_speaker_path, total_duration, (speaker_x, speaker_y), speaker_size, circle_mask)
                speaker_overlays.append(speaker_clip)
                
                # Also add a background box and speaker name if provided.
                name_y = speaker_y + speaker_size + 5
                text_bg_width = speaker_size
                text_bg_height = int(speaker_font_size * 1.5)
                speaker_box_rgb = ImageColor.getrgb(speaker_box_color)
                text_bg = mp.ColorClip((text_bg_width, text_bg_height), color=speaker_box_rgb)\
                            .set_opacity(speaker_box_opacity).set_duration(total_duration)
                text_bg = text_bg.set_position((speaker_x, name_y))
                speaker_overlays.append(text_bg)
                chosen_name = speaker1_name if speaker1_name else speaker2_name
                if chosen_name:
                    name_clip = mp.TextClip(
                        chosen_name,
                        fontsize=speaker_font_size,
                        color=speaker_font_color,
                        font=speaker_font,
                        stroke_color='black',
                        stroke_width=1,
                        size=(text_bg_width, None),
                        method='caption',
                        align='center'
                    ).set_position((speaker_x, name_y)).set_duration(total_duration)
                    speaker_overlays.append(name_clip)
            
            final_video = mp.CompositeVideoClip([final_video] + speaker_overlays, size=resolution)
        
        print("Writing final video...")
        final_video.write_videofile(output_file, fps=24, audio_codec='aac')
        print("Video creation complete.")

        # Clean up temporary image files
        for clip in image_clips:
            if hasattr(clip, 'filename'):
                try:
                    os.unlink(clip.filename)
                except Exception:
                    pass
    except Exception as e:
        print(f"Error creating video: {str(e)}")
        traceback.print_exc()

# Example usage:
if __name__ == "__main__":
    try:
        voice_over_path = "defaults/audio/welcome.mp3"
        bg_music_path = "defaults/bgmusic/soft_theme_main_track.mp3"
        output_video = "final_video.mp4"
        video_resolution = (1280, 720)
        background_volume = 0.3
        split_duration = 5
        transition_duration = 1.0
        
        logo_path = "defaults/images/logo.png"
        logo_size = (120, 80)
        logo_position = 'top-left'  # change as needed
        footer_text = "2025 PodcraftAI - AI Generated Content"  # optional
        
        transition_type = None

        # For testing, try with both speakers, one speaker, or none.
        speaker1_path = "defaults/speakers/speaker_mal2e.jpg"  # image or video file
        speaker2_path = None  # Only one speaker provided.
        speaker1_name = "Brad"
        speaker2_name = None
        speaker_size = 150

        # Speaker style parameters (optional)
        speaker_font = "Arial-Bold"
        speaker_font_size = 36
        speaker_font_color = "white"
        speaker_box_color = "black"
        speaker_box_opacity = 0.7

        # New parameter to explicitly set single speaker position.
        single_speaker_position = "bottom-left"  # options: "bottom-left" or "bottom-right"

        create_video(
            voice_over=voice_over_path,
            bg_music=bg_music_path,
            output_file=output_video,
            resolution=video_resolution,
            bg_volume=background_volume,
            voice_split_duration=split_duration,
            logo_path=logo_path,
            logo_size=logo_size,
            logo_position=logo_position,
            footer_text=footer_text,
            transition_duration=transition_duration,
            transition_type=transition_type,
            speaker1_path=speaker1_path,
            speaker2_path=speaker2_path,
            speaker1_name=speaker1_name,
            speaker2_name=speaker2_name,
            speaker_size=speaker_size,
            speaker_font=speaker_font,
            speaker_font_size=speaker_font_size,
            speaker_font_color=speaker_font_color,
            speaker_box_color=speaker_box_color,
            speaker_box_opacity=speaker_box_opacity,
            single_speaker_position=single_speaker_position
        )
    except Exception as e:
        print(f"Error in main: {str(e)}")
        traceback.print_exc()
