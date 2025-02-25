import sys
import logging
import numpy as np
import os
import random
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    concatenate_audioclips,
    TextClip,
    ImageClip
)
from moviepy.audio.fx.all import volumex, audio_loop
from moviepy.audio.AudioClip import CompositeAudioClip
from typing import List
import glob

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('video_creation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def scroll_text(t, clip, screen_width):
    """Move text from right to left"""
    speed = 150
    x = screen_width - (speed * t)
    return (x, 1000)

class PodcastVideoCreator:
    def __init__(
        self,
        source_videos_path: str,
        background_music_path: str,
        voiceover_path: str,
        logo_path: str,
        logo_width: int = "",
        logo_height: int = "",
        bg_music_volume: float = 0.1,
        heading_text: str = "AppliView Podcast",
        subheading_text: str = "Tech Insights & Innovation",
        footer_text: str = "Follow us on social media • Subscribe to our channel • Visit our website",
        output_path: str = "final_video.mp4"
    ):
        self.source_videos_path = source_videos_path
        self.background_music_path = background_music_path
        self.voiceover_path = voiceover_path
        self.logo_path = logo_path
        self.logo_width = logo_width
        self.logo_height = logo_height
        self.bg_music_volume = bg_music_volume
        self.heading_text = heading_text
        self.subheading_text = subheading_text
        self.footer_text = footer_text
        self.output_path = output_path
        self.width = 1920
        self.height = 1080
        
        self._validate_inputs()

    def _validate_inputs(self):
        """Validate all input paths and parameters."""
        if not os.path.isdir(self.source_videos_path):
            raise ValueError(f"Source videos directory not found: {self.source_videos_path}")
        
        if not os.path.isfile(self.background_music_path):
            raise ValueError(f"Background music file not found: {self.background_music_path}")
            
        if not os.path.isfile(self.voiceover_path):
            raise ValueError(f"Voice-over audio file not found: {self.voiceover_path}")
            
        if not os.path.isfile(self.logo_path):
            raise ValueError(f"Logo file not found: {self.logo_path}")
            
        if not 0 <= self.bg_music_volume <= 1:
            raise ValueError(f"Background music volume must be between 0 and 1")
            
        video_files = self._get_video_files()
        if not video_files:
            raise ValueError(f"No video files found in {self.source_videos_path}")

    def _get_video_files(self) -> List[str]:
        """Get all video files from the source directory."""
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        video_files = []
        
        for ext in video_extensions:
            video_files.extend(glob.glob(os.path.join(self.source_videos_path, f"*{ext}")))
            
        return video_files

    def _get_clip_segments(self, total_duration: float) -> List[VideoFileClip]:
        """Select and prepare random video clips to match the required duration."""
        video_files = self._get_video_files()
        segments = []
        current_duration = 0
        
        while current_duration < total_duration:
            video_path = random.choice(video_files)
            print(f"Processing video: {video_path}")
            
            try:
                clip = VideoFileClip(video_path)
                remaining_duration = total_duration - current_duration
                
                if clip.duration > remaining_duration:
                    if clip.duration > remaining_duration + 1:
                        start_time = random.uniform(0, clip.duration - remaining_duration)
                        clip = clip.subclip(start_time, start_time + remaining_duration)
                    else:
                        clip = clip.subclip(0, remaining_duration)
                
                clip = clip.resize(newsize=(self.width, self.height))
                segments.append(clip)
                current_duration += clip.duration
                
            except Exception as e:
                print(f"Error processing video {video_path}: {str(e)}")
                continue
                
        return segments

    def _prepare_background_music(self, target_duration: float) -> AudioFileClip:
        """Prepare background music to match target duration."""
        bg_music = AudioFileClip(self.background_music_path)
        bg_music = bg_music.fx(volumex, self.bg_music_volume)
        
        if bg_music.duration < target_duration:
            bg_music = bg_music.fx(audio_loop, duration=target_duration)
        else:
            bg_music = bg_music.subclip(0, target_duration)
        
        return bg_music

    def _create_logo_clip(self, duration):
        """Create a logo clip with specified dimensions"""
        try:
            logo_clip = (ImageClip(self.logo_path)
                        .resize(newsize=(self.logo_width, self.logo_height))
                        .set_duration(duration)
                        .set_position((50, 50)))  # Position in top left with 50px padding
            return logo_clip
        except Exception as e:
            print(f"Error creating logo clip: {str(e)}")
            raise

    def _create_scrolling_footer(self, duration):
        """Create a scrolling footer TextClip"""
        try:
            footer_clip = TextClip(
                self.footer_text,
                fontsize=40,
                color='white',
                font='Arial-Bold',
                method='label',
                size=(None, None)
            )
            
            footer_clip = footer_clip.set_duration(duration)
            footer_clip = footer_clip.set_position(
                lambda t: scroll_text(t, footer_clip, self.width)
            )
            
            return footer_clip
        except Exception as e:
            print(f"Error creating footer: {str(e)}")
            raise

    def _create_heading_clip(self, duration):
        """Create a heading TextClip with text wrapping for longer titles"""
        try:
            # Calculate max width for text (70% of video width)
            max_width = int(self.width * 0.7)
            
            heading_clip = TextClip(
                self.heading_text,
                fontsize=60,
                color='white',
                font='Arial-Bold',
                method='caption',
                size=(max_width, None),
                align='center'
            )
            
            # Get the actual height of the text clip for positioning
            self.heading_height = heading_clip.h
            
            # Position the clip in the top center, starting at y=60
            heading_pos = ('center', 60)
            heading_clip = heading_clip.set_duration(duration)
            heading_clip = heading_clip.set_position(heading_pos)
            
            return heading_clip
        except Exception as e:
            print(f"Error creating heading: {str(e)}")
            raise

    def _create_subheading_clip(self, duration):
        """Create a subheading TextClip with text wrapping for longer subtitles"""
        try:
            # Calculate max width for text (80% of video width)
            max_width = int(self.width * 0.8)
            
            subheading_clip = TextClip(
                self.subheading_text,
                fontsize=45,
                color='#CCCCCC',
                font='Arial',
                method='caption',
                size=(max_width, None),
                align='center'
            )
            
            # Calculate position based on heading height plus padding
            # Add 40px padding between heading and subheading
            subheading_y = 60 + getattr(self, 'heading_height', 0) + 40
            subheading_pos = ('center', subheading_y)
            
            subheading_clip = subheading_clip.set_duration(duration)
            subheading_clip = subheading_clip.set_position(subheading_pos)
            
            return subheading_clip
        except Exception as e:
            print(f"Error creating subheading: {str(e)}")
            raise

    def create_video(self):
        """Create the final video with logo, voice-over, background music, and scrolling footer."""
        video_segments = []
        voice_over = None
        bg_music = None
        final_video = None
        footer_clip = None
        logo_clip = None
        heading_clip = None
        subheading_clip = None

        try:
            print("Starting video creation process...")
            
            voice_over = AudioFileClip(self.voiceover_path)
            total_duration = voice_over.duration
            print(f"Voice-over duration: {total_duration} seconds")
            
            video_segments = self._get_clip_segments(total_duration)
            final_video = concatenate_videoclips(video_segments)
            
            print("Creating logo clip...")
            logo_clip = self._create_logo_clip(total_duration)
            
            print("Creating scrolling footer...")
            footer_clip = self._create_scrolling_footer(total_duration)
            
            print("Creating heading clip...")
            heading_clip = self._create_heading_clip(total_duration)
            
            print("Creating subheading clip...")
            subheading_clip = self._create_subheading_clip(total_duration)
            
            print("Processing background music...")
            bg_music = self._prepare_background_music(total_duration)
            
            print("Mixing audio tracks...")
            final_audio = CompositeAudioClip([bg_music, voice_over])
            
            print("Compositing video with logo, heading, subheading, and footer...")
            final_video = CompositeVideoClip([
                final_video,
                logo_clip,
                heading_clip,
                subheading_clip,
                footer_clip
            ])
            
            final_video = final_video.set_audio(final_audio)
            
            print(f"Writing final video to {self.output_path}...")
            final_video.write_videofile(
                self.output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                threads=4,
                preset='medium'
            )
            
            print("Video creation completed successfully!")
            
        except Exception as e:
            print(f"Error creating video: {str(e)}")
            raise
            
        finally:
            print("Cleaning up resources...")
            try:
                if voice_over: voice_over.close()
                if bg_music: bg_music.close()
                if final_video: final_video.close()
                if footer_clip: footer_clip.close()
                if logo_clip: logo_clip.close()
                if heading_clip: heading_clip.close()
                if subheading_clip: subheading_clip.close()
                for segment in video_segments:
                    if segment: segment.close()
                print("Cleanup completed.")
            except Exception as e:
                print(f"Error during cleanup: {str(e)}")

def main():
    try:
        creator = PodcastVideoCreator(
            source_videos_path="videos",
            background_music_path="bgmusic/s3.mp3",
            voiceover_path="voiceover/1_trimmed.wav.mp3",
            logo_path="images/logo.png",
            logo_width=DEFAULT_LOGO_WIDTH,
            logo_height=DEFAULT_LOGO_HEIGHT,
            bg_music_volume=0.1,
            heading_text="AppliView Podcast",
            subheading_text="Tech Insights & Innovation",
            footer_text="Follow us on social media • Subscribe to our channel • Visit our website: example.com • Contact us at info@example.com",
            output_path="2final_video.mp4"
        )
        creator.create_video()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()