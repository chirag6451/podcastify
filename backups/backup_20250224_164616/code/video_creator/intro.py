#file intro.py
import sys
import logging
from constants import (
    VIDEO_WIDTH, VIDEO_HEIGHT, FPS,
    VIDEO_CODEC, AUDIO_CODEC,
    VIDEO_BITRATE, AUDIO_BITRATE,
    DEFAULT_INTRO_DURATION,
    HEADING_FONT, SUBHEADING_FONT, FOOTER_FONT,
    HEADING_SIZE, SUBHEADING_SIZE, FOOTER_SIZE,
    HEADING_COLOR, SUBHEADING_COLOR, FOOTER_COLOR,
    DEFAULT_HEADING, DEFAULT_SUBHEADING, DEFAULT_FOOTER,
    DEFAULT_LOGO_WIDTH, DEFAULT_LOGO_HEIGHT,
    HEADING_Y_POS, SUBHEADING_Y_POS
)

# 1. Monkey patch PIL.Image.ANTIALIAS at the very top
from PIL import Image
import numpy as np
import os
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    ColorClip,
    CompositeAudioClip,
    vfx,
    concatenate_videoclips
)
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
import logging
import colorlog

logger = logging.getLogger(__name__)

# Handle Pillow version compatibility
try:
    # Try the new way first (Pillow >= 10.0.0)
    ANTIALIAS = Image.Resampling.LANCZOS
except:
    try:
        # Try the old way (Pillow < 10.0.0)
        ANTIALIAS = Image.ANTIALIAS
    except:
        # Fallback to LANCZOS
        ANTIALIAS = Image.LANCZOS

print("Starting video creation script...")

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('video_creation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def scroll_text(t, width):
    """Move text from right to left"""
    speed = 150  # Pixels per second
    x = int(width - (speed * t))  # Convert to int to avoid string concatenation error
    return (x, 980)  # Fixed Y position near bottom of screen


def create_text_clip(text, fontsize, color, position, duration, font='Arial-Bold', is_footer=False):
    """Create a text clip with specified parameters"""
    try:
        # Calculate max width for text wrapping (70% for heading, 80% for subheading)
        max_width = int(VIDEO_WIDTH * (0.8 if is_footer else 0.7))
        
        # Create the text clip
        text_clip = TextClip(
            text,
            fontsize=fontsize,
            color=color,
            font=font,
            method='caption',
            size=(max_width, None),
            align='center'
        )
        
        # For footer, use the scroll_text function
        if is_footer:
            text_clip = text_clip.set_position(lambda t: scroll_text(t, VIDEO_WIDTH))
        else:
            # For static text, calculate y position if it's a tuple with 'auto'
            if isinstance(position, tuple) and len(position) == 3 and position[1] == 'auto':
                # Get the height of the clip
                clip_height = text_clip.h
                # Use the provided base_y and add the height
                base_y = position[0]
                prev_height = position[2]
                if isinstance(prev_height, (int, float)):
                    y_pos = int(prev_height) + 40  # 40px padding
                    position = (base_y, y_pos)
            text_clip = text_clip.set_position(position)
        
        # Set the duration
        text_clip = text_clip.set_duration(duration)
        return text_clip, text_clip.h  # Return both the clip and its height
        
    except Exception as e:
        print(f"Error creating text clip: {str(e)}")
        raise

def create_brief_video(
    source_video_path,
    logo_path,
    background_music_path,
    output_video_path,
    voiceover_path=None,
    video_duration=DEFAULT_INTRO_DURATION,
    logo_width=DEFAULT_LOGO_WIDTH,
    logo_height=DEFAULT_LOGO_HEIGHT,
    footer_text=DEFAULT_FOOTER
):
    """Create a simple brief video with minimal overlays and audio fade effect"""
    background_video = None
    logo = None
    background_music = None
    voiceover = None
    final_video = None

    try:
        # 1. Create background video - simple resize and crop
        background_video = VideoFileClip(source_video_path)
        background_video = background_video.without_audio()
        
        # Resize maintaining aspect ratio
        aspect_ratio = background_video.w / background_video.h
        target_aspect = VIDEO_WIDTH / VIDEO_HEIGHT
        
        if aspect_ratio > target_aspect:
            # Video is wider than target
            new_height = VIDEO_HEIGHT
            new_width = int(VIDEO_HEIGHT * aspect_ratio)
        else:
            # Video is taller than target
            new_width = VIDEO_WIDTH
            new_height = int(VIDEO_WIDTH / aspect_ratio)
            
        background_video = background_video.resize((new_width, new_height))
        
        # Center crop
        x1 = max(0, (background_video.w - VIDEO_WIDTH) // 2)
        y1 = max(0, (background_video.h - VIDEO_HEIGHT) // 2)
        background_video = background_video.crop(
            x1=x1, 
            y1=y1, 
            x2=x1 + VIDEO_WIDTH, 
            y2=y1 + VIDEO_HEIGHT
        )
        
        # Set duration with loop if needed
        if background_video.duration < video_duration:
            background_video = background_video.loop(duration=video_duration)
        else:
            background_video = background_video.subclip(0, video_duration)

        # 2. Create simple logo overlay - fixed size and position
        if os.path.exists(logo_path):
            logo = ImageClip(logo_path)
            # Use smaller logo size for better performance
            logo = logo.resize(width=logo_width)  # Fixed width, maintain aspect ratio
            logo = logo.set_position((50, 50))  # Fixed position in top-left
            logo = logo.set_duration(video_duration)

        # 3. Composite video - simple overlay
        clips = [background_video]
        if logo is not None:
            clips.append(logo)
        
        final_video = CompositeVideoClip(clips, size=(VIDEO_WIDTH, VIDEO_HEIGHT))

        # 4. Add audio tracks
        audio_clips = []
        
        # Add voiceover with fade out if provided
        if voiceover_path and os.path.exists(voiceover_path):
            voiceover = AudioFileClip(voiceover_path)
            # Take first few seconds of voiceover
            voiceover_duration = min(video_duration - 1, voiceover.duration)  # Leave 1s for fade
            voiceover = voiceover.subclip(0, voiceover_duration)
            # Add fade out effect
            voiceover = voiceover.audio_fadeout(2)
            # Set voiceover volume higher than background music
            voiceover = voiceover.volumex(1.0)
            audio_clips.append(voiceover)

        # Add background music if available
        if os.path.exists(background_music_path):
            background_music = AudioFileClip(background_music_path)
            if background_music.duration < video_duration:
                background_music = background_music.loop(duration=video_duration)
            else:
                background_music = background_music.subclip(0, video_duration)
            # Lower volume for background music
            background_music = background_music.volumex(0.05)  # Even lower volume (5%)
            audio_clips.append(background_music)

        # Combine audio tracks if any
        if audio_clips:
            final_audio = CompositeAudioClip(audio_clips)
            final_video = final_video.set_audio(final_audio)

        # 5. Write final video with optimized settings
        final_video.write_videofile(
            output_video_path,
            fps=FPS,
            codec=VIDEO_CODEC,
            audio_codec=AUDIO_CODEC,
            preset='ultrafast',  # Faster encoding
            threads=4,
            remove_temp=True
        )

        return final_video

    except Exception as e:
        print(f"Error in create_brief_video: {str(e)}")
        raise
    finally:
        # Clean up resources
        try:
            if background_video is not None:
                background_video.close()
            if logo is not None:
                logo.close()
            if background_music is not None:
                background_music.close()
            if voiceover is not None:
                voiceover.close()
            if final_video is not None:
                final_video.close()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

if __name__ == "__main__":
    try:
        print("Starting main execution...")
        create_brief_video(
            source_video_path='videos/intro1.mp4',
            logo_path='images/logo.png',
            background_music_path='audio/appliview_podcast.m4a',
            output_video_path='debug_output_video.mp4',
            video_duration=3,
            logo_width=100,
            logo_height=100,
            footer_text="Follow us on social media • Subscribe to our channel • Visit our website: example.com"
        )
        print("Main execution completed successfully!")
    except Exception as e:
        print(f"Main execution error: {str(e)}")
        logging.error(f"Main execution error: {str(e)}")
        sys.exit(1)
