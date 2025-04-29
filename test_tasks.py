import os
import json
from video_creator import create_podcast_video, PodcastVideoConfig

def generate_audio_task_test(config: dict, business_info: dict, job_id: str):
    """Test version of generate_audio task without database operations"""
    try:
        print(f"Would generate audio for job {job_id} with config:")
        print(json.dumps(config, indent=2))
        
        # For testing, we'll use hardcoded audio paths
        audio_path = "output/20250210_164450_alex_mr_johnson_i_heard_that_j/final_mix.mp3"
        welcome_audio_path = "output/20250210_164450_alex_mr_johnson_i_heard_that_j/Ken_2.mp3"
        
        # Add welcome audio path to config
        config['intro_audio_path'] = welcome_audio_path
        
        return audio_path
        
    except Exception as e:
        print(f"Error in audio generation for job {job_id}: {str(e)}")
        raise

def create_video_task_test(job_id, config):
    """Test version of create video task without database operations"""
    try:
        print(f"Creating video for job {job_id}")
        
        # Create output directory path
        output_dir = os.path.join("output", f"{job_id}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract video settings
        video_settings = config.get("video_settings", {})
        
        # Create video configuration
        video_config = PodcastVideoConfig(
            voiceover_path=os.path.join("output", "20250210_164450_alex_mr_johnson_i_heard_that_j", "final_mix.mp3"),
            speaker1_video_path=os.path.join("video_creator/defaults/speakers/g1.mp4"),
            speaker1_name=config["speaker1_name"],
            speaker2_video_path=os.path.join("video_creator/defaults/speakers/m1.mp4"),
            speaker2_name=config["speaker2_name"],
            title=config["business_info"]["name"],
            subtitle=config["topic"],
            output_filename=f"podcast_{job_id}.mp4",
            output_dir=output_dir,
            
            # Video settings from profile
            resolution=tuple(video_settings.get("resolution", [1920, 1080])),
            bg_music_volume=video_settings.get("bg_music_volume", 0.1),
            videos_library_path=video_settings.get("videos_library_path"),
            background_video_path=video_settings.get("background_video_path"),
            background_image_path=video_settings.get("background_image_path"),
            background_music_path=video_settings.get("background_music_path"),
            
            # Pass the entire video settings for intro/outro configs
            profile_config=config
        )
        
        # Create video
        video_path = create_podcast_video(
            voiceover_path=video_config.voiceover_path,
            speaker1_video_path=video_config.speaker1_video_path,
            speaker1_name=video_config.speaker1_name,
            speaker2_video_path=video_config.speaker2_video_path,
            speaker2_name=video_config.speaker2_name,
            title=video_config.title,
            subtitle=video_config.subtitle,
            output_filename=video_config.output_filename,
            output_dir=video_config.output_dir,
            resolution=video_config.resolution,
            bg_music_volume=video_config.bg_music_volume,
            videos_library_path=video_config.videos_library_path,
            background_image_path=video_config.background_image_path,
            background_music_path=video_config.background_music_path,
            profile_config=video_config.profile_config
        )
        
        return video_path
        
    except Exception as e:
        print(f"Error in video generation for job {job_id}: {str(e)}")
        raise 