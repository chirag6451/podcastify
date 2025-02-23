import os
import logging
import subprocess
from moviepy.editor import VideoFileClip, concatenate_videoclips

def setup_simple_logger():
    """Set up basic logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

logger = setup_simple_logger()

def preprocess_video_for_compatibility(
    source_video: str, 
    target_duration: float = None, 
    output_path: str = None,
    video_codec: str = "libx264",
    audio_codec: str = "aac",
    fps: int = 30,
    threads: int = 4,
    preset: str = "medium",
    video_bitrate: str = "1000k",
    width: int = 1920,
    height: int = 1080
) -> str:
    """
    Pre-process a video to make it compatible with MoviePy and ensure it meets the target duration.
    
    Args:
        source_video (str): Path to the source video file
        target_duration (float, optional): Desired duration in seconds. If None, keeps original duration
        output_path (str, optional): Path for the output video. If None, creates one based on source
        video_codec (str): Video codec to use (default: libx264)
        audio_codec (str): Audio codec to use (default: aac)
        fps (int): Frames per second (default: 30)
        threads (int): Number of threads to use (default: 4)
        preset (str): FFmpeg preset (default: medium)
        video_bitrate (str): Video bitrate (default: 1000k)
        width (int): Output video width (default: 1920)
        height (int): Output video height (default: 1080)
        
    Returns:
        str: Path to the processed video file
    """
    try:
        if not output_path:
            dirname = os.path.dirname(source_video)
            basename = os.path.basename(source_video)
            name, ext = os.path.splitext(basename)
            output_path = os.path.join(dirname, f"{name}_processed{ext}")
            
        logger.info(f"Processing video: {source_video}")
        logger.info(f"Target duration: {target_duration if target_duration else 'original'}")
        
        # Basic ffmpeg command with specified parameters
        ffmpeg_cmd = [
            'ffmpeg', '-y',  # Overwrite output files
            '-i', source_video,
            '-c:v', video_codec,
            '-c:a', audio_codec,
            '-r', str(fps),
            '-threads', str(threads),
            '-preset', preset,
            '-b:v', video_bitrate,
            '-vf', f'scale={width}:{height}',
            '-pix_fmt', 'yuv420p',  # Widely compatible pixel format
            '-movflags', '+faststart',  # Enable fast start for web playback
            '-strict', 'experimental'
        ]
        
        # Add duration parameter if specified
        if target_duration:
            ffmpeg_cmd.extend(['-t', str(target_duration)])
            
        ffmpeg_cmd.append(output_path)
        
        # Execute the command
        process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg error: {stderr.decode()}")
            
        # Verify the output
        if not os.path.exists(output_path):
            raise Exception("Failed to create output video")
            
        # Test the output with MoviePy
        with VideoFileClip(output_path) as clip:
            actual_duration = clip.duration
            logger.info(f"Successfully processed video. Duration: {actual_duration:.2f}s")
            
        return output_path
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        raise

def combine_videos_with_transitions(
    videos: list,
    output_path: str,
    transition_duration: float = 1.0,
    fade_in_duration: float = 1.0,
    fade_out_duration: float = 1.0,
    video_codec: str = "libx264",
    audio_codec: str = "aac",
    fps: int = 30,
    threads: int = 4,
    preset: str = "medium",
    video_bitrate: str = "1000k"
) -> str:
    """
    Combine multiple videos with crossfade transitions and fade effects.
    
    Args:
        videos (list): List of either video file paths (str) or VideoFileClip objects
        output_path (str): Path for the output combined video
        transition_duration (float): Duration of crossfade between clips in seconds
        fade_in_duration (float): Duration of fade in effect at start in seconds
        fade_out_duration (float): Duration of fade out effect at end in seconds
        video_codec (str): Video codec to use (default: libx264)
        audio_codec (str): Audio codec to use (default: aac)
        fps (int): Frames per second (default: 30)
        threads (int): Number of threads to use (default: 4)
        preset (str): FFmpeg preset (default: medium)
        video_bitrate (str): Video bitrate (default: 1000k)
        
    Returns:
        str: Path to the combined video file
    """
    clips_to_close = []  # Track clips we need to close
    
    try:
        logger.info(f"Attempting to combine {len(videos)} videos...")
        
        # Load all videos
        clips = []
        for video in videos:
            try:
                if isinstance(video, str):
                    if os.path.exists(video):
                        clip = VideoFileClip(video)
                        clips_to_close.append(clip)  # Track for cleanup
                        clips.append(clip)
                        logger.info(f"Successfully loaded file: {video}")
                    else:
                        logger.error(f"Video file not found: {video}")
                        raise FileNotFoundError(f"Video file not found: {video}")
                elif hasattr(video, 'duration'):  # Likely a VideoFileClip
                    clips.append(video)
                    logger.info("Successfully added video clip")
                else:
                    raise ValueError(f"Invalid video type: {type(video)}. Must be string path or VideoFileClip")
            except Exception as e:
                logger.error(f"Error loading video: {str(e)}")
                raise
        
        if not clips:
            raise Exception("No valid clips to combine")
            
        # Add transitions between clips
        clips_with_transitions = []
        for i, clip in enumerate(clips):
            if i > 0:  # Not the first clip
                # Add fadeout to previous clip
                clips_with_transitions[-1] = clips_with_transitions[-1].fadeout(transition_duration)
                # Add fadein to current clip
                clip = clip.fadein(transition_duration)
            clips_with_transitions.append(clip)
        
        # Concatenate with crossfading
        final = concatenate_videoclips(
            clips_with_transitions,
            method="compose",
            padding=-transition_duration  # Negative padding creates overlap for crossfade
        )
        
        # Add fade effects to final video
        final = final.fadein(fade_in_duration).fadeout(fade_out_duration)
        
        # Write the combined video
        final.write_videofile(
            output_path,
            codec=video_codec,
            audio_codec=audio_codec,
            fps=fps,
            threads=threads,
            preset=preset,
            bitrate=video_bitrate
        )
        
        logger.info(f"Successfully created combined video: {output_path}")
        
        # Clean up only the clips we created
        final.close()
        for clip in clips_to_close:
            clip.close()
            
        return output_path
        
    except Exception as e:
        logger.error(f"Error combining videos: {str(e)}")
        # Clean up only the clips we created
        try:
            for clip in clips_to_close:
                clip.close()
        except:
            pass
        raise

def create_looped_video_from_section(
    source_video: str,
    output_path: str = None,
    width: int = 1920,
    height: int = 1080,
    target_duration: float = 5.0,
    extract_seconds: float = 2.0,
    video_codec: str = "libx264",
    audio_codec: str = "aac",
    fps: int = 30,
    threads: int = 4,
    preset: str = "medium",
    video_bitrate: str = "1000k"
) -> str:
    """
    Extract first N seconds from video and loop it to reach target duration.
    Both video and audio will be looped to match the target duration.
    
    Args:
        source_video (str): Path to source video file
        output_path (str): Path for output video. If None, creates one based on source
        width (int): Target width for output video
        height (int): Target height for output video
        target_duration (float): Desired duration in seconds for final video
        extract_seconds (float): Number of seconds to extract from start of video
        video_codec (str): Video codec to use (default: libx264)
        audio_codec (str): Audio codec to use (default: aac)
        fps (int): Frames per second (default: 30)
        threads (int): Number of threads to use (default: 4)
        preset (str): FFmpeg preset (default: medium)
        video_bitrate (str): Video bitrate (default: 1000k)
        
    Returns:
        str: Path to the processed video file
    """
    try:
        if not output_path:
            dirname = os.path.dirname(source_video)
            basename = os.path.basename(source_video)
            name, ext = os.path.splitext(basename)
            output_path = os.path.join(dirname, f"{name}_looped{ext}")

        logger.info(f"Processing video: {source_video}")
        
        # Load source video to get duration
        with VideoFileClip(source_video) as source_clip:
            actual_duration = source_clip.duration
            extract_seconds = min(extract_seconds, actual_duration)
            
        logger.info(f"Source duration: {actual_duration}s, extracting {extract_seconds}s and looping to {target_duration}s")
        
        # Calculate number of loops needed
        loop_count = int(target_duration / extract_seconds) + 1
            
        # Create FFmpeg command - note stream_loop before input file
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-stream_loop', str(loop_count),  # Number of times to loop - MUST be before input
            '-i', source_video,
            '-t', str(target_duration),  # Total output duration
            '-filter_complex', f'[0:v]scale={width}:{height}[v];[0:a]volume=1[a]',
            '-map', '[v]',
            '-map', '[a]',
            '-c:v', video_codec,
            '-c:a', audio_codec,
            '-r', str(fps),
            '-threads', str(threads),
            '-preset', preset,
            '-b:v', video_bitrate,
            '-pix_fmt', 'yuv420p',
            output_path
        ]
        
        # Execute ffmpeg command
        process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg error: {stderr.decode()}")
        
        # Verify the output
        if not os.path.exists(output_path):
            raise Exception("Failed to create output video")
            
        logger.info(f"Successfully created looped video: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating looped video: {str(e)}")
        raise

if __name__ == "__main__":
    # Test all functions
    source_video = "profiles/indapoint/videos/intro7.mp4"
    try:
        # Test video processing
        processed_video = preprocess_video_for_compatibility(
            source_video=source_video,
            target_duration=5.0,
            video_codec="libx264",
            audio_codec="aac",
            fps=30,
            threads=4,
            preset="medium",
            video_bitrate="1000k",
            width=1920,
            height=1080
        )
        logger.info(f"Video processed successfully: {processed_video}")
        
        # Test video looping
        looped_video = create_looped_video_from_section(
            source_video=source_video,
            width=780,
            height=480,
            target_duration=10.0,  # Create a 10 second video
            extract_seconds=2.0    # Using first 2 seconds
        )
        logger.info(f"Created looped video: {looped_video}")
        
        # Test video combining
        videos = [
            processed_video,
            looped_video,
            "outputs/indapoint/short_video.mp4"
        ]
        
        combined_video = combine_videos_with_transitions(
            videos=videos,
            output_path="outputs/indapoint/combined_test.mp4",
            transition_duration=1.0,
            fade_in_duration=1.0,
            fade_out_duration=1.0
        )
        logger.info(f"Videos combined successfully: {combined_video}")
        
    except Exception as e:
        logger.error(f"Failed to process/combine videos: {str(e)}")
