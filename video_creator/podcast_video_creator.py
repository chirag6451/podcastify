import os
import sys
import logging
import tempfile
import random
from video_creator.hygen import HeyGenAPI
from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, 
    concatenate_videoclips, ColorClip, ImageClip, CompositeAudioClip
)
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.video.fx.resize import resize
from moviepy.video.fx.speedx import speedx
from moviepy.audio.fx.audio_loop import audio_loop
import colorlog
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
import json
from profile_utils import ProfileUtils
from video_creator.utils.podcast_short_video_creator import create_bumper_hygen_short_video, create_podcast_short_video
from video_creator.utils.video_segment_creator import create_video_segment
import datetime
from config import DEFAULT_INTRO_PATH, DEFAULT_OUTRO_PATH
from video_creator.utils.video_utils import create_final_video_from_paths
from .db_utils import VideoDB  # Import VideoDB directly from db_utils

# Initialize profile utils
profile_utils = ProfileUtils()

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

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

    logger = colorlog.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

logger = setup_logger()

class PodcastVideoCreator:
    def __init__(self):
        """Initialize video creator"""
        # Set default background color
        self.bg_color = '#1a1a1a'
        
        # Set up logging
        logger = setup_logger()
        logger.info("Initialized video creator")
        
        # Initialize database connection
        self.db = VideoDB()

    def create_text_clip(self, text, font_size, color, y_position, duration):
        """Create a text clip with the given parameters"""
        return (TextClip(text, fontsize=font_size, color=color, font=self.config['HEADING_FONT'])
                .set_position(('center', y_position))
                .set_duration(duration))

    def get_available_videos(self) -> list:
        """Get list of all available background videos"""
        videos_dir = os.path.join(self.profile_path, self.config['DEFAULT_VIDEOS_DIR'])
        video_files = []
        for ext in ['.mp4', '.avi', '.mov', '.mkv']:
            video_files.extend(glob.glob(os.path.join(videos_dir, f"*{ext}")))
        
        if not video_files:
            logger.error(f"No video files found in {videos_dir}")
            raise ValueError("No background videos available")
            
        return video_files

    def create_background_sequence(self, duration: float, videos_path: str, resolution: tuple) -> VideoFileClip:
        """Create a sequence of different background videos for the entire duration"""
        logger.info("Creating background video sequence from multiple videos...")
        
        # Get all video files from the directory
        video_files = []
        for ext in ['.mp4', '.avi', '.mov', '.mkv']:
            video_files.extend([os.path.join(videos_path, f) for f in os.listdir(videos_path) if f.endswith(ext)])
        
        if not video_files:
            raise ValueError(f"No video files found in {videos_path}")
            
        import random
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
            raise e

    def create_background(self, duration: float, background_video_path: str, resolution: tuple) -> VideoFileClip:
        """Create a background video of the specified duration"""
        try:
            # Load and process the background video
            video = VideoFileClip(background_video_path)
            video = self.resize_video(video, resolution[0], resolution[1])
            
            # If video is shorter than needed duration, loop it
            if video.duration < duration:
                video = video.loop(duration=duration)
            else:
                # Take a segment from the start
                video = video.subclip(0, duration)
                
            return video
            
        except Exception as e:
            logger.error(f"Error creating background: {str(e)}")
            # Create a plain black background as fallback
            return ColorClip(
                size=resolution,
                color=self.bg_color.lstrip('#')  # Remove # from hex color
            ).set_duration(duration)

    def resize_video(self, clip, target_width, target_height):
        """Resize video clip to match target dimensions while maintaining aspect ratio"""
        # Calculate new dimensions maintaining aspect ratio
        aspect_ratio = clip.w / clip.h
        target_aspect = target_width / target_height
        
        if aspect_ratio > target_aspect:
            # Video is wider than target
            new_height = target_height
            new_width = int(target_height * aspect_ratio)
        else:
            # Video is taller than target
            new_width = target_width
            new_height = int(target_width / aspect_ratio)
            
        # Resize the clip
        resized = clip.resize((new_width, new_height))
        
        # Center crop to target dimensions
        x1 = max(0, (resized.w - target_width) // 2)
        y1 = max(0, (resized.h - target_height) // 2)
        
        return resized.crop(x1=x1, y1=y1, 
                          x2=x1 + target_width, 
                          y2=y1 + target_height)

    def create_logo_overlay(self, duration):
        """Create a logo overlay"""
        if os.path.exists(self.logo_path):
            logo = ImageClip(self.logo_path)
            
            # Get logo dimensions from config
            width = self.config.get('DEFAULT_LOGO_WIDTH', 120)
            height = self.config.get('DEFAULT_LOGO_HEIGHT')
            
            # Calculate height to maintain aspect ratio if not specified
            if height is None:
                aspect_ratio = logo.h / logo.w
                height = int(width * aspect_ratio)
            
            # Resize logo
            logo = logo.resize(width=width, height=height)
            
            # Position logo at top-right with padding
            padding = 20
            position = (self.width - width - padding, padding)  # Top-right position
            logo = logo.set_position(position).set_duration(duration)
            
            return logo
        return None

    def create_hygen_bumper_video(self, config, request_dict):
        """
        Create a short bumper video using only background music 
        (no voiceover or welcome audio).
        """
        try:
            # Fixed duration for bumper
            preview_duration = 10  # or fetch from config, e.g. config.get("preview_duration", 10)

            # Prepare the background music
            background_music_path = config['background_music_path']
            logger.info("Preparing background music...")
            bg_music = AudioFileClip(background_music_path)

            # If background music is shorter than the required duration, loop it
            # Otherwise, trim it.
            if bg_music.duration < preview_duration:
                logger.debug("Looping background music to match desired preview duration...")
                bg_music = audio_loop(bg_music, duration=preview_duration)
            else:
                logger.debug("Trimming background music to preview duration...")
                bg_music = bg_music.subclip(0, preview_duration)

            # Optionally lower the volume
            bg_music = bg_music.volumex(0.1)

            # This is our final audio (since there's no voiceover)
            final_audio = bg_music

            # Create the short video (no audio paths since no voiceover)
            logger.info("Creating short bumper video...")
          
           
            short_video_path, thumbnail_paths = create_bumper_hygen_short_video(
                # No audio inputs for voiceover or welcome audio
                audio_path=None,        
                welcome_audio_path=None,
                config=config,
                request_dict=request_dict,
            )

            # Load the created video
            # logger.debug(f"Loading short video from path: {short_video_path}")
            # short_video_clip = VideoFileClip(short_video_path)

            # # Set the final audio for the short video
            # short_video_clip = short_video_clip.set_audio(final_audio)

            # # Write the final short video
            # final_short_video_path = os.path.join(
            #     config['output_dir'],
            #     config['short_video_output_filename']
            # )
            # short_video_clip.write_videofile(
            #     final_short_video_path,
            #     codec=config['codec'],
            #     audio_codec=config['audio_codec'],
            #     fps=config['fps'],
            #     threads=config['threads'],
            #     preset=config['preset']
            # )

            logger.info(f"Final short bumper video created at: {short_video_path}")
            return thumbnail_paths, short_video_path

        except Exception as e:
            logger.error(f"Error creating short bumper video: {str(e)}")
            raise
        finally:
            # Clean up resources
            try:
                bg_music.close()
                final_audio.close()
                short_video_clip.close()
            except:
                pass
    
    
    def create_short_video(self, 
                           main_audio, 
                           welcome_audio_path,
                           config,
                           request_dict
                         ):
        """Create a short video segment using a portion of the main audio"""
        
        
        
        try:
          
            
            #if intro_audio_path is given then we use it and do not create preview , we use diredly as intro
            if welcome_audio_path:
                logger.info(f"Creating preview audio from intro audio...")
                preview_audio = AudioFileClip(welcome_audio_path)
                # preview_audio = intro_audio.subclip(0, min(intro_audio.duration, preview_duration))
            else:
                preview_duration=10
                logger.info(f"Creating preview audio from voiceover...")
                main_voiceover = AudioFileClip(main_audio)  # Use main_audio instead
                # Take the first preview_duration seconds of the voiceover
                preview_audio = main_voiceover.subclip(0, preview_duration)

            # Get current duration
            current_duration = preview_audio.duration
                
            # Write preview audio to temp file and play it
            logger.info("Playing preview audio...")
            temp_audio_path = os.path.join(tempfile.gettempdir(), "preview_audio.mp3")
            preview_audio.write_audiofile(temp_audio_path)
        
            
            # Play using pydub
            #audio = AudioSegment.from_file(temp_audio_path)
        
            
            # Clean up temp file
            os.remove(temp_audio_path)
            background_music_path = config['background_music_path']
            # Load and prepare background music
            logger.info("Preparing background music...")
            bg_music = AudioFileClip(background_music_path)
            
            # Loop background music if needed
            if bg_music.duration < current_duration:
                logger.debug("Looping background music to match preview duration...")
                bg_music = audio_loop(bg_music, duration=current_duration)
            else:
                logger.debug("Trimming background music to preview duration...")
                bg_music = bg_music.subclip(0, current_duration)
            
            bg_music = bg_music.volumex(0.1)
            
            # Combine voiceover and background music
            logger.info("Combining audio tracks...")
            final_audio = CompositeAudioClip([preview_audio, bg_music])
            
            # Test audio clips if needed
            logger.info("Testing audio clips...")
       
            # Create short video using create_podcast_short_video
            logger.info("Creating short video...")
            short_video_path, thumbnail_paths = create_podcast_short_video(
                audio_path=welcome_audio_path, #for short video we use welcome audio path
                welcome_audio_path=welcome_audio_path,
                config=config,
                request_dict=request_dict,
               
            )
            
            # Load the created video as a VideoFileClip
            logger.debug(f"Loading short video from path: {short_video_path}")
            short_video_clip = VideoFileClip(short_video_path)
            
            print("--------------------------------\n")
            print(f"short_video_clip: {short_video_path}")  
            print("--------------------------------\n")
            # Set the final audio for the short video
            short_video_clip = short_video_clip.set_audio(final_audio)
            
          
            # Write the final short video with the new audio
            #let us add timestamp to the output filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = config['short_video_output_filename']
            final_short_video_path = os.path.join(config['output_dir'], output_filename + "_" + timestamp + ".mp4")
            # final_short_video_path = config['output_dir'] + "/" + config['short_video_output_filename']
            short_video_clip.write_videofile(
                final_short_video_path,
                codec=config['codec'],
                audio_codec=config['audio_codec'],
                fps=config['fps'],
                threads=config['threads'],
                preset=config['preset']
            )
         
            # Load and return the final video clip
   
            return thumbnail_paths,final_short_video_path
            
        except Exception as e:
            logger.error(f"Error creating short video: {str(e)}")
            raise
        finally:
            # Clean up audio clips
            try:
                main_voiceover.close()
                preview_audio.close()
                bg_music.close()
                final_audio.close()
                short_video_clip.close()
            except:
                pass
    
                
    def test_audio(self, audio_clip: AudioFileClip, duration: float = None) -> None:
        """
        Test play an audio clip using pydub
        
        Args:
            audio_clip: MoviePy AudioFileClip to test
            duration: Optional duration in seconds to test (default: full clip)
        """
        try:
            # Get the audio file path from MoviePy clip
            audio_path = audio_clip.filename
            
            # Load audio with pydub
            audio = AudioSegment.from_file(audio_path)
            
            # If duration specified, only play that duration
            if duration:
                audio = audio[:int(duration * 1000)]  # pydub works in milliseconds
                
            logger.info(f"Playing audio clip: {audio_path}")
            play(audio)
            
        except Exception as e:
            logger.error(f"Error playing audio: {str(e)}")

    def create_video(self, 
                     audio_path,
                     welcome_audio_path,
                     config,
                     job_id,  # Add job_id as a separate parameter
                     request_dict
                  ):
        
        """Create a video with the specified parameters"""
        
        intro_clip = None
        outro = None
        main_video = None
        short_video = None
        final_video = None
        
    # #
        try:
            import json
            # Set paths
            print("on top of the world")
            print(json.dumps(config, indent=4))
            background_video_path = config['background_video_path']
        
            #self.background_video_path = os.path.dirname(config['background_video_path'])
            self.background_video_path = config['background_video_path']
            self.background_music_path = config['background_music_path']
            self.logo_path = config['logo_settings_main_logo_path']
            
            # Create output directory and set full output path
            os.makedirs(config['output_dir'], exist_ok=True)
            #self.output_path = os.path.join(config['output_dir'], config['output_filename'] )
            
            final_clips = []  # List to store all video segments in sequence
            
          # Get merged config with intro section overrides
       
    
            # Create intro and outro segments if configs are provided
         
            if config['intro_video']:
                intro_config = profile_utils.get_merged_config('indapoint', 'intro')
            
                resolution = config['resolution']   
                #if fixed_video_path is set in config, we use that as intro and do not create intro video
                if intro_config['fixed_video_path']:
                    #let us validate the video path
                
                    if not os.path.exists(intro_config['fixed_video_path']):
                        logger.error(f"Fixed video path does not exist: {intro_config['fixed_video_path']}")
                        raise ValueError(f"Fixed video path does not exist: {intro_config['fixed_video_path']}")
                        intro_clip=DEFAULT_INTRO_PATH
                    intro_video_path=intro_config['fixed_video_path']
              
            
                
                #let us create a video based on inro clip to
                else:
                    intro_config = profile_utils.get_merged_config('indapoint', 'intro')

                    if intro_config:
                        intro_video_path = create_video_segment(audio_path=audio_path, config=intro_config, segment_type="intro",request_dict=request_dict)
                        logger.info("Loading intro video...")
                  
                        #let us store this in database
                # Store intro path in database
                self.db.add_specific_path(job_id=int(job_id), path_type='intro_video_path', path_value=intro_video_path)
                
            
                # Create and add short video
                logger.info("Creating short video segment...")
            
            # # Set output filename in config
            config['output_filename'] = os.path.join(config['output_dir'], 'podcast_short_video.mp4')
            
            #if hygen video is set than we use that as short video and we do not create short video
            if config['heygen_short_video']:
                logger.info("Creating heygen video...")
                api = HeyGenAPI(db=self.db)
                
                # First generate the video
                INPUT_TEXT = config['welcome_voiceover']
        
                heygen_video_id = api.create_video_add_to_queue(
                    # Character and voice parameters
                    character_type="avatar",
                    avatar_id="Judith_expressive_2024120201",
                    avatar_style="normal",
                    voice_type="text",
                    input_text=INPUT_TEXT,
                    voice_id="c4be407b9d94405a9eb403190d77c851",
                    speed=1.1,
                    # Video dimensions
                    width=1280,
                    height=720,
                    # Background parameters (defaults to video background)
                    background_type="video",
                    background_asset_id="f978e4db1f2743d3a4001c0b3e6b6bb7",
                    play_style="loop",
                    fit="cover",
                    # Output and polling parameters
                    video_output_file="output_video.mp4",
                    thumbnail_output_file="thumbnail.jpg",
                    poll_interval=5,
                    timeout=300,
                    # Pass task ID for database tracking
                    task_id=int(job_id)
                )
                #also update is_heygen_video to true in database
                self.db.update_heygen_video_flag(job_id=int(job_id), is_heygen_video=True)
                logger.info(f"Heygen video ID: {heygen_video_id}")
            elif config['short_video']:
                thumbnail_paths,short_video_path = self.create_short_video(
                    main_audio=audio_path,
                    welcome_audio_path=welcome_audio_path,
                    config=config,
                    request_dict=request_dict
                )

                logger.info(f"Short video created at: {short_video_path}")
                #final_clips.append(short_video)
            #let us store this in database
                self.db.add_specific_path(job_id=int(job_id), path_type='short_video_path', path_value=short_video_path)
            
            
            if config['hygen_bumper']:
                logger.info("Creating heygen bumper video...")
                bumper_video_path = create_bumper_hygen_short_video(
                    audio_path=None,
                    welcome_audio_path=None,
                    config=config, 
                    request_dict=request_dict
                    )
            else:
                if config['bumper_video']:
                    #let us create bumper video by using bumper config
                    bumper_config = profile_utils.get_merged_config('indapoint', 'bumper')
                if bumper_config['fixed_video_path']:
            
                    bumper_video_path=bumper_config['fixed_video_path']
                else:
                    bumper_video_path = create_video_segment(audio_path=audio_path, config=bumper_config, segment_type="bumper",request_dict=request_dict)
                    # bumper_video_clip = VideoFileClip(bumper_video)
                    # bumper_video_clip = self.resize_video(bumper_video_clip, resolution[0], resolution[1])
            
            logger.info(f"Bumper video created at: {bumper_video_path}")
            self.db.add_specific_path(job_id=int(job_id), path_type='bumper_video_path', path_value=bumper_video_path)
          
           #let us chcek request_dict for main_video_style
            if config['main_video']:
                if request_dict['main_video_style'] == 'video':
                    logger.info("Creating main video...")
                    from video_creator.main_video_creator import MainVideoCreator
                    main_video_creator = MainVideoCreator()
                    main_video_clip,main_video_path = main_video_creator.create_main_video(audio_path=audio_path, config=config,resolution=resolution)
                elif request_dict['main_video_style'] == 'images':
                    logger.info("Creating main video...")
                    from video_creator.video_with_images import create_video_with_images
                    # Create a temporary output path for the images video
                    temp_output = os.path.join(config['output_dir'], f"main_video_with_images_{random.randint(1000, 9999)}.mp4")
                    config['output_file'] = temp_output
                    main_video_path = create_video_with_images(audio_path=audio_path, config=config, resolution=resolution, request_dict=request_dict)
                    if main_video_path is None:
                        raise ValueError("Failed to create video with images")
         
      
            
                self.db.add_specific_path(job_id=int(job_id), path_type='main_video_path', path_value=main_video_path)
            
            if config['outro_video']:
                outro_config = profile_utils.get_merged_config('indapoint', 'outro')
                if outro_config:
                    logger.info("Creating outro video segment...")
                    
                if outro_config['fixed_video_path']:
                    outro_video_path=outro_config['fixed_video_path']
                else:
                    outro_video_path = create_video_segment(**outro_config['params'])

                
                self.db.add_specific_path(job_id=int(job_id), path_type='outro_video_path', path_value=outro_video_path)
                logger.info("Outro video added successfully")
            
         
            # Get all video paths from database
            video_paths = self.db.get_video_paths_in_order(int(job_id))
        
            
            # Create final video using paths
          
        
            # output_path = create_final_video_from_paths(video_paths, config, job_id)
        
            logger.info("Video creation completed successfully and recorded in database!")
            return job_id

        except Exception as e:
            logger.error(f"Error creating video: {str(e)}")
            raise e

        finally:
            # Clean up resources
            for clip in [intro_clip, outro, main_video, short_video, final_video]:
                if clip:
                    try:
                        clip.close()
                    except:
                        pass

    def add_logo(self, clip, logo_path, logo_width, logo_height):
        """Add a logo to the clip"""
        logo = ImageClip(logo_path)
        logo = logo.resize(width=logo_width, height=logo_height)
        logo = logo.set_position((50, 50))  # Top-left corner with padding
        logo = logo.set_duration(clip.duration)
        return CompositeVideoClip([clip, logo])

def create_video(audio_path: str, title: str = None, subtitle: str = None, profile: str = "default", output_filename: str = None) -> str:
    """
    Create a video from an audio file with the given parameters
    
    Args:
        audio_path (str): Path to the input audio file
        title (str, optional): Title to display in the video. Defaults to None.
        subtitle (str, optional): Subtitle to display in the video. Defaults to None.
        profile (str, optional): Profile to use for video creation. Defaults to "default".
        output_filename (str, optional): Name for the output video file. Defaults to None.
        
    Returns:
        str: Path to the created video file
    """
    try:
        # Initialize video creator with profile
        creator = PodcastVideoCreator(
            profile=profile,
            podcast_title=title,
            podcast_subtitle=subtitle   
        )
        
        # Update config with title and subtitle if provided
        if title:
            creator.config['PODCAST_TITLE'] = title
        if subtitle:
            creator.config['PODCAST_SUBTITLE'] = subtitle
            
        # Create the video
        return creator.create_video(audio_path, creator.intro_video_path, creator.bg_music_path, creator.logo_path, output_filename)
        
    except Exception as e:
        logger.error(f"Error creating video: {str(e)}")
        raise

# if __name__ == "__main__":
#     # Example usage
#     try:
#         video_path = create_video(
#             audio_path="profiles/default/voiceover/AI_in_Recruitment.wav",
#             title="AI in Recruitment",
#             subtitle="Best Practices and Ethical Considerations",
#             output_filename="ai_recruitment.mp4"
#         )
#         logger.info(f"Video created successfully: {video_path}")
        
#     except Exception as e:
#         logger.error(f"Failed to create video: {str(e)}")
