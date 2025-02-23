import os
import sys
import logging
import importlib
from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.video.fx.all import fadein, fadeout
from moviepy.audio.fx.all import audio_fadein, audio_fadeout
from datetime import datetime
import time
import json
from pathlib import Path
from typing import Optional
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from intro import create_brief_video
from random_clip import PodcastShortsCreator
from podcast_video import PodcastVideoCreator
from utils import get_random_file, DriveUtils
from utils.api_client import APIClient

# Default company name
DEFAULT_COMPANY = "appliview"

# Default fallback files
DEFAULT_FILES = {
    "bg_music": "bgmusic/s3.mp3",
    "voiceover": "voiceover/120_trimmed.wav",
    "logo": "images/logo.png",
    "intro_video": "intro_extro/intro7.mp4",  # Default intro
    "outro_video": "intro_extro/extro.mp4"   # Default outro
}

# Default fallback output folder URL
DEFAULT_OUTPUT_FOLDER_URL = "https://drive.google.com/drive/folders/169-AXbZVYNzsf_rPIG5m7ICh3Ou3P7cg"

# Set up logging
def setup_logging():
    """Set up logging configuration"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"podcast_processing_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logging.info(f"Starting podcast processing, log file: {log_file}")

def validate_paths(config):
    """Validate paths and use fallbacks if needed"""
    paths = config["company"]["paths"]
    modified = False
    
    for key, path in paths.items():
        if not os.path.exists(path):
            fallback = DEFAULT_FILES.get(key)
            if fallback and os.path.exists(fallback):
                logging.warning(f"{path} not found, using fallback: {fallback}")
                paths[key] = fallback
                modified = True
            else:
                logging.warning(f"{path} not found and no valid fallback available")
    
    return config

def load_company_config(company_name=DEFAULT_COMPANY):
    """Dynamically load company configuration"""
    try:
        config_module = importlib.import_module(f"config.{company_name.lower()}_config")
        config = config_module.get_config()
        return validate_paths(config)
    except ImportError as e:
        if company_name != DEFAULT_COMPANY:
            logging.warning(f"Configuration for company '{company_name}' not found, falling back to {DEFAULT_COMPANY}")
            return load_company_config()  # Retry with default company
        raise ValueError(f"Default company configuration not found: {str(e)}")

def add_transition(clip, transition_duration=1.0):
    """Add fade-in and fade-out transitions to both video and audio."""
    if clip is None:
        return None
        
    # Add video transitions
    clip = clip.fx(fadein, transition_duration).fx(fadeout, transition_duration)
    
    # Add audio transitions if the clip has audio
    if clip.audio is not None:
        clip = clip.set_audio(
            clip.audio.fx(audio_fadein, transition_duration)
                        .fx(audio_fadeout, transition_duration)
        )
    
    return clip

def create_final_video(company_name=DEFAULT_COMPANY, input_audio_path=None, output_path=None):
    """Combine all video segments into one final video with transitions."""
    try:
        # Load company-specific configuration
        config = load_company_config(company_name)
        company_config = config["company"]
        paths = company_config["paths"]
        content = company_config["content"]
        style = company_config["style"]
        gdrive_folders = company_config.get("gdrive", {})
        
        # Initialize Google Drive manager with new DriveUtils
        drive = DriveUtils()
        
        # Create all necessary directories
        logging.info("\nCreating output directories...")
        # First create base directories from dir_structure
        for dir_name, dir_path in config["dir_structure"].items():
            logging.info(f"Creating {dir_name} directory: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
        
        # Then create output directories for all video paths
        output_paths = {
            "short_clip": paths.get("short_clip"),
            "intro_video": paths.get("intro_video"),
            "podcast_video": paths.get("podcast_video"),
            "final_video": paths.get("final_video")
        }
        
        for path_name, path in output_paths.items():
            if path:
                dir_path = os.path.dirname(path)
                if dir_path:
                    logging.info(f"Creating output directory for {path_name}: {dir_path}")
                    os.makedirs(dir_path, exist_ok=True)
        
        # Also create company output directory if specified
        if company_config.get("output_dir"):
            logging.info(f"Creating company output directory: {company_config['output_dir']}")
            os.makedirs(company_config["output_dir"], exist_ok=True)
        
        logging.info("\nChecking for voiceover file in Google Drive...")
        input_folder_id = gdrive_folders.get("input")
        if not input_folder_id:
            logging.error("No input folder ID specified in configuration")
            return False
            
        # Find audio files in the input folder
        audio_files = drive.find_audio_files(input_folder_id, recursive=False)
        
        if not audio_files:
            logging.error("No voiceover file found in Google Drive input folder")
            logging.info("Please upload a voiceover file before creating the video")
            return False
            
        # Get the first audio file (you might want to add more specific selection criteria)
        voiceover_file = audio_files[0]
        logging.info(f"Found voiceover file: {voiceover_file['name']}")
        
        voiceover_path = os.path.join(
            config["dir_structure"]["voiceover"],
            voiceover_file["name"]
        )
        
        # Download voiceover file
        logging.info(f"Downloading voiceover file to {voiceover_path}...")
        if not drive.download_file(voiceover_file["id"], voiceover_path):
            logging.error("Failed to download voiceover file")
            return False
            
        paths["voiceover"] = voiceover_path
        logging.info("Voiceover file downloaded successfully!")
        
        # Get random background music
        try:
            bg_music = get_random_file(config["dir_structure"]["bgmusic"], ['.mp3', '.wav', '.m4a'])
            logging.info(f"Selected random background music: {bg_music}")
        except ValueError as e:
            logging.warning(f"{str(e)}")
            bg_music = paths["bg_music"]  # Fallback to default
            logging.info(f"Using default background music: {bg_music}")
        
        # Get random source video
        try:
            source_video = get_random_file(config["dir_structure"]["videos"], ['.mp4', '.mov', '.avi'])
            logging.info(f"Selected random source video: {source_video}")
        except ValueError as e:
            logging.warning(f"{str(e)}")
            source_video = f"{config['dir_structure']['videos']}/intro1.mp4"  # Fallback to default
            logging.info(f"Using default source video: {source_video}")

        # 1. Load intro video from intro_extro folder
        logging.info("\n1. Loading intro video...")
        intro_path = paths["intro_video"]
        if not os.path.exists(intro_path):
            logging.warning(f"Company intro video not found: {intro_path}")
            intro_path = DEFAULT_FILES["intro_video"]
            logging.info(f"Using default intro video: {intro_path}")
        logging.info(f"Loading intro video from: {intro_path}")
        intro_video_clip = VideoFileClip(intro_path)
        # Resize intro video to match configured dimensions
        intro_video_clip = intro_video_clip.resize(width=config["video"]["width"], height=config["video"]["height"])
        logging.info(f"Intro video duration: {intro_video_clip.duration}s")
        intro_video_clip = add_transition(intro_video_clip)
        logging.info("Intro video loaded successfully!")

        # 2. Create short video clip
        logging.info("\n2. Creating short video clip...")
        short_creator = PodcastShortsCreator(
            source_videos_path=config["dir_structure"]["videos"],
            background_music_path=bg_music,  # Use random background music
            voiceover_path=paths["voiceover"],
            logo_path=paths["logo"],
            clip_duration=config["duration"]["short_clip_duration"],
            logo_width=style["logo"]["width"],
            logo_height=style["logo"]["height"],
            bg_music_volume=config["audio"]["bg_music_volume"],
            footer_text=content["footer"],
            output_path=config["paths"]["short_clip"]
        )
        short_creator.create_short()
        logging.info(f"Loading short clip from: {config['paths']['short_clip']}")
        short_clip = VideoFileClip(config["paths"]["short_clip"])
        logging.info(f"Short clip duration: {short_clip.duration}s")
        short_clip = add_transition(short_clip)
        logging.info("Short clip loaded successfully!")

        # 3. Create brief video
        logging.info("\n3. Creating Brief video...")
        logging.info(f"Source video path: {source_video}")  # Use random source video
        logging.info(f"Logo path: {paths['logo']}")
        logging.info(f"Background music: {bg_music}")  # Use random background music
        brief_video = create_brief_video(
            source_video_path=source_video,
            logo_path=paths["logo"],
            background_music_path=bg_music,
            output_video_path=config["paths"]["intro_video"],
            video_duration=config["duration"]["intro_duration"],
            logo_width=style["logo"]["width"],
            logo_height=style["logo"]["height"],
            heading_text=content["heading"],
            subheading_text=content["subheading"],
            footer_text=content["footer"],
            heading_fontsize=config["text_style"]["heading"]["size"],
            subheading_fontsize=config["text_style"]["subheading"]["size"],
            footer_fontsize=config["text_style"]["footer"]["size"],
            heading_color=style["colors"]["primary"],
            subheading_color=style["colors"]["secondary"],
            footer_color=style["colors"]["primary"]
        )
        if brief_video is None:
            logging.warning("Brief video creation returned None!")
        else:
            logging.info(f"Brief video duration: {brief_video.duration}s")
            brief_video = add_transition(brief_video)
            logging.info("Brief video created successfully!")

        # 4. Create main podcast video
        logging.info("\n4. Creating podcast video...")
        podcast_creator = PodcastVideoCreator(
            source_videos_path=config["dir_structure"]["videos"],
            background_music_path=bg_music,  # Use random background music
            voiceover_path=paths["voiceover"],
            logo_path=paths["logo"],
            logo_width=style["logo"]["width"],
            logo_height=style["logo"]["height"],
            bg_music_volume=config["audio"]["bg_music_volume"],
            footer_text=content["footer"],
            output_path=config["paths"]["podcast_video"]
        )
        podcast_creator.create_video()
        logging.info(f"Loading podcast video from: {config['paths']['podcast_video']}")
        podcast_video_clip = VideoFileClip(config["paths"]["podcast_video"])
        logging.info(f"Podcast video duration: {podcast_video_clip.duration}s")
        podcast_video_clip = add_transition(podcast_video_clip)
        logging.info("Podcast video loaded successfully!")

        # 5. Load outro video
        logging.info("\n5. Loading outro video...")
        outro_path = paths["outro_video"]
        if not os.path.exists(outro_path):
            logging.warning(f"Company outro video not found: {outro_path}")
            outro_path = DEFAULT_FILES["outro_video"]
            logging.info(f"Using default outro video: {outro_path}")
        logging.info(f"Loading outro video from: {outro_path}")
        outro_video_clip = VideoFileClip(outro_path)
        # Resize outro video to match configured dimensions
        outro_video_clip = outro_video_clip.resize(width=config["video"]["width"], height=config["video"]["height"])
        logging.info(f"Outro video duration: {outro_video_clip.duration}s")
        outro_video_clip = add_transition(outro_video_clip)
        logging.info("Outro video loaded successfully!")

        # Combine all clips in the specified order
        logging.info("\nCombining all video segments...")
        final_clips = [
            intro_video_clip,     # 1. Intro from intro_extro folder
            short_clip,           # 2. PodcastShortsCreator output
            brief_video,          # 3. Brief video
            podcast_video_clip,   # 4. Main podcast video
            outro_video_clip      # 5. Outro from intro_extro folder
        ]
        
        # Verify all clips are valid
        logging.info("\nVerifying clip durations:")
        for i, clip in enumerate(final_clips):
            if clip is None:
                logging.warning(f"Clip {i+1} is None!")
            else:
                logging.info(f"Clip {i+1} duration: {clip.duration}s")

        final_video = concatenate_videoclips(final_clips, method="compose")
        logging.info(f"Final video duration: {final_video.duration}s")

        # Save final video
        if output_path:
            final_video_path = output_path
        else:
            final_video_path = os.path.join(
                company_config["output_dir"],
                f"{company_name.lower()}_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            )
        logging.info(f"\nWriting final video to {final_video_path}...")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(final_video_path)
        os.makedirs(output_dir, exist_ok=True)
        
        final_video.write_videofile(
            final_video_path,
            fps=config["video"]["fps"],
            codec=config["video"]["video_codec"],
            audio_codec=config["video"]["audio_codec"],
            bitrate=config["video"]["video_bitrate"],
            audio_bitrate=config["video"]["audio_bitrate"],
            threads=config["video"]["threads"],
            preset=config["video"]["preset"]
        )

        # Upload final video to Google Drive
        logging.info("\nUploading final video to Google Drive...")
        if not os.path.exists(final_video_path) or os.path.getsize(final_video_path) == 0:
            logging.error(f"Final video not found at {final_video_path}")
            return False
            
        # Create a descriptive filename with timestamp
        output_filename = os.path.basename(final_video_path)
        logging.info(f"Uploading {output_filename} to Google Drive...")
        
        try:
            # First try to use configured output folder
            output_folder = gdrive_folders.get("output")
            if output_folder:
                logging.info(f"Using configured output folder: {output_folder}")
                file_id, shareable_link = drive.upload_file(
                    final_video_path,
                    output_folder,
                    output_filename
                )
                
                if file_id and shareable_link:
                    logging.info("Upload successful using configured folder")
                else:
                    output_folder = None  # Reset to try folder creation
            
            # If configured folder doesn't work, create a new one
            if not output_folder:
                logging.info("Configured folder not accessible, creating new folder...")
                folder_name = f"{company_name.lower()}_videos"
                output_folder = drive.find_or_create_folder(folder_name)
                if not output_folder:
                    logging.error("Could not create output folder")
                    return False
                    
                logging.info(f"Created new folder: {folder_name}")
                file_id, shareable_link = drive.upload_file(
                    final_video_path,
                    output_folder,
                    output_filename
                )
            
            if file_id and shareable_link:
                logging.info("\nVideo uploaded successfully!")
                logging.info(f"File ID: {file_id}")
                logging.info(f"Shareable link: {shareable_link}")
                
                # Save the link to a file for reference
                links_file = os.path.join(company_config["output_dir"], "video_links.txt")
                os.makedirs(os.path.dirname(links_file), exist_ok=True)
                with open(links_file, "a") as f:
                    f.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    f.write(f"\nVideo: {output_filename}")
                    f.write(f"\nLocal path: {final_video_path}")
                    f.write(f"\nGoogle Drive folder: {output_folder}")
                    f.write(f"\nGoogle Drive link: {shareable_link}\n")
                logging.info(f"\nLink saved to: {links_file}")
                
                return True
            else:
                logging.error("Failed to upload final video to Google Drive")
                return False
                
        except Exception as e:
            logging.error(f"Error during upload: {str(e)}")
            return False
            
    except Exception as e:
        logging.error(f"Error creating final video: {str(e)}")
        return False
    finally:
        # Clean up all video clips
        try:
            if 'intro_video_clip' in locals(): intro_video_clip.close()
            if 'short_clip' in locals(): short_clip.close()
            if 'brief_video' in locals(): brief_video.close()
            if 'podcast_video_clip' in locals(): podcast_video_clip.close()
            if 'outro_video_clip' in locals(): outro_video_clip.close()
            if 'final_video' in locals(): final_video.close()
        except Exception as e:
            logging.warning(f"Error during cleanup: {str(e)}")
            logging.error(f"Error during cleanup: {str(e)}", exc_info=True)

def process_single_podcast(podcast_data: dict, company_name: str = DEFAULT_COMPANY) -> Optional[str]:
    """
    Process a single podcast and create its video
    
    Returns:
        str: File ID of the uploaded video if successful, None otherwise
    """
    podcast_id = podcast_data['podcastId']
    
    try:
        drive = DriveUtils()
        
        try:
            # Get output folder URL
            output_folder_url = podcast_data.get('project', {}).get('outputFolderUrl')
            if not output_folder_url:
                logging.error(f"No output folder URL found for podcast {podcast_id}")
                return None
                
            # Extract folder ID
            output_folder_id = drive.get_folder_id_from_url(output_folder_url)
            print(output_folder_id)
            logging.info(f"Using output folder ID: {output_folder_id}")
            
            # Verify folder access
            try:
                folder = drive.service.files().get(fileId=output_folder_id, fields='id, name').execute()
                logging.info(f"Verified output folder: {folder.get('name', 'Unknown')} ({folder['id']})")
            except Exception as e:
                logging.error(f"Could not access output folder: {str(e)}")
                return None
            
            # Get audio URL
            audio_url = podcast_data.get('audioUrl')
            if not audio_url:
                logging.error(f"No audio URL found for podcast {podcast_id}")
                return None

            # Create temporary directories
            temp_dir = "temp_processing"
            os.makedirs(temp_dir, exist_ok=True)

            # Set audio filename and path
            audio_path = os.path.join(temp_dir, f"podcast_{podcast_id}.mp3")
            
            logging.info(f"Downloading audio file for podcast {podcast_id} from {audio_url}...")
            
            try:
                # Extract file ID from Google Drive URL
                audio_file_id = drive.get_folder_id_from_url(audio_url)
                if not audio_file_id:
                    logging.error(f"Could not extract file ID from audio URL for podcast {podcast_id}")
                    return None

                # Download using Drive API
                if not drive.download_file(audio_file_id, audio_path):
                    logging.error(f"Failed to download audio file for podcast {podcast_id}")
                    return None

                if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
                    logging.error(f"Downloaded audio file is missing or empty for podcast {podcast_id}")
                    return None

                logging.info(f"Successfully downloaded audio file: {audio_path} ({os.path.getsize(audio_path)} bytes)")

            except Exception as e:
                logging.error(f"Error downloading audio file for podcast {podcast_id}: {str(e)}")
                return None

            # Create video with downloaded audio
            output_video_path = os.path.join(temp_dir, f"video_{podcast_id}.mp4")
            logging.info(f"Creating video for podcast {podcast_id}...")
            
            success = create_final_video(
                company_name,
                input_audio_path=audio_path,
                output_path=output_video_path
            )
            
            if not success:
                logging.error(f"Failed to create video for podcast {podcast_id}")
                return None
                
            if not os.path.exists(output_video_path) or os.path.getsize(output_video_path) == 0:
                logging.error(f"Created video file is missing or empty for podcast {podcast_id}")
                return None
                
            logging.info(f"Successfully created video: {output_video_path} ({os.path.getsize(output_video_path)} bytes)")
            
            # Upload video to output folder
            logging.info(f"Uploading video for podcast {podcast_id} to Google Drive...")
            
            if not os.path.exists(output_video_path) or os.path.getsize(output_video_path) == 0:
                logging.error(f"Video file is missing or empty: {output_video_path}")
                return None
                
            try:
                file_metadata = {
                    'name': os.path.basename(output_video_path),
                    'parents': [output_folder_id]
                }
                
                media = MediaFileUpload(
                    output_video_path,
                    mimetype='video/mp4',
                    resumable=True
                )
                
                file = drive.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                
                video_file_id = file.get('id')
                if not video_file_id:
                    logging.error(f"Failed to get file ID for uploaded video for podcast {podcast_id}")
                    return None
                    
                logging.info(f"Successfully uploaded video for podcast {podcast_id}, file ID: {video_file_id}")
                
            except Exception as e:
                logging.error(f"Error uploading video for podcast {podcast_id}: {str(e)}")
                return None
            
            # Clean up temporary files
            try:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                if os.path.exists(output_video_path):
                    os.remove(output_video_path)
                logging.info(f"Cleaned up temporary files for podcast {podcast_id}")
            except Exception as e:
                logging.warning(f"Error cleaning up temporary files for podcast {podcast_id}: {str(e)}")
            
            return video_file_id
            
        except ValueError as e:
            logging.error(f"Error extracting IDs from URLs for podcast {podcast_id}: {str(e)}")
            return None
        
    except Exception as e:
        logging.error(f"Error processing podcast {podcast_id}: {str(e)}", exc_info=True)
        return None

def is_valid_drive_url(url: str) -> bool:
    """Check if URL is a valid Google Drive URL"""
    if not url:
        return False
    return url.startswith('https://drive.google.com/')

def main_processing_loop():
    """Main loop to continuously process pending videos"""
    setup_logging()
    api_client = APIClient()
    
    while True:
        try:
            logging.info("\nChecking for pending videos...")
            pending_videos = api_client.get_pending_videos()
            if not pending_videos:
                logging.info("No pending videos found")
                time.sleep(60)  # Wait before checking again
                continue
            
            for podcast in pending_videos:
                podcast_id = podcast['podcastId']
                try:
                    # Log podcast details
                    logging.info(f"\nProcessing podcast: {podcast['title']} (ID: {podcast_id})")
                    logging.info(f"Audio URL: {podcast.get('audioUrl')}")
                    logging.info(f"Input Folder URL: {podcast.get('project', {}).get('inputFolderUrl')}")
                    logging.info(f"Output Folder URL: {podcast.get('project', {}).get('outputFolderUrl')}")
                    print(podcast)
                    print("--------------------------------")
                    print(podcast.get('project', {}).get('outputFolderUrl'))
                    print(podcast.get('audioUrl'))
            
                    
                    # Skip if audio URL is invalid
                    if not is_valid_drive_url(podcast.get('audioUrl')):
                        logging.error(f"Invalid or missing audio URL for podcast {podcast_id}, skipping...")
                        continue
                    
                    # Skip if output folder URL is invalid
                    output_folder_url = podcast.get('project', {}).get('outputFolderUrl')
                    if not is_valid_drive_url(output_folder_url):
                        logging.error(f"Invalid or missing output folder URL for podcast {podcast_id}, skipping...")
                        continue
                    
                    # Process the podcast
                    print(podcast)
                    #print audio url
                    print(podcast.get('audioUrl'))
                    #print output folder url
                    print(podcast.get('project', {}).get('outputFolderUrl'))
                    success = process_single_podcast(podcast)
                
                    
                    if success:
                        # Create shareable link for the uploaded video
                        video_url = f"https://drive.google.com/file/d/{success}/view"
                        
                        # Update the video URL in the API
                        if api_client.update_video_url(podcast_id, video_url):
                            logging.info(f"Successfully processed and updated podcast {podcast_id}")
                        else:
                            logging.error(f"Failed to update video URL for podcast {podcast_id}")
                    else:
                        logging.error(f"Failed to process podcast {podcast_id}")
                    
                except Exception as e:
                    logging.error(f"Error processing podcast {podcast_id}: {str(e)}", exc_info=True)
                    continue  # Move to next podcast
            
            time.sleep(60)  # Wait before checking for new podcasts
            
        except Exception as e:
            logging.error(f"Error in processing loop: {str(e)}", exc_info=True)
            time.sleep(60)  # Wait longer if there's an error

if __name__ == "__main__":
    main_processing_loop()
