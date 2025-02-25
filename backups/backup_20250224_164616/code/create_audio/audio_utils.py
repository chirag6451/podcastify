"""Module for audio generation and processing utilities."""
import os
import time
import json
from typing import List, Dict
from pydub import AudioSegment
from pydub.effects import normalize
from create_audio.elevanlab_util import client
from create_audio.conversation import Conversation
from create_audio.logger_utils import PodcastLogger

# Initialize logger
logger = PodcastLogger("AudioGenerator")

def create_natural_overlap(base_audio: AudioSegment, overlay_audio: AudioSegment, position_ms: int) -> AudioSegment:
    """Create a natural-sounding overlap between two audio segments"""
    # Parameters for natural-sounding overlap
    CROSSFADE_DURATION = 200  # 200ms crossfade
    OVERLAY_VOLUME_REDUCTION = 3  # -3dB for overlaying audio
    BASE_VOLUME_REDUCTION = 2  # -2dB for base audio during overlap
    
    # Calculate the end position of the overlay
    overlay_end_position = position_ms + len(overlay_audio)
    
    # Ensure the base audio is long enough
    if overlay_end_position > len(base_audio):
        pad_duration = overlay_end_position - len(base_audio)
        base_audio = base_audio + AudioSegment.silent(duration=pad_duration)
    
    # Extract the segment of base audio that will be overlapped
    overlap_region = base_audio[position_ms:overlay_end_position]
    
    # Reduce volume of both audio segments in the overlap region
    overlap_region = overlap_region - BASE_VOLUME_REDUCTION
    overlay_audio = overlay_audio - OVERLAY_VOLUME_REDUCTION
    
    # Apply crossfade at the start and end of the overlay
    if len(overlay_audio) > CROSSFADE_DURATION * 2:
        overlay_audio = overlay_audio.fade_in(CROSSFADE_DURATION).fade_out(CROSSFADE_DURATION)
    
    # Overlay the audio segments
    overlap_region = overlap_region.overlay(overlay_audio)
    
    # Combine the parts
    return base_audio[:position_ms] + overlap_region + base_audio[overlay_end_position:]

def generate_audio_files(conversation: Conversation, topic_dir: str, speakers: List[Dict],) -> Dict[str, str]:
    """Generate audio files for both main speech and overlaps."""
    logger.info("Generating audio files...")
    audio_files = {}
    
    # Analytics tracking
    total_duration_ms = 0
    turn_durations = []
    
    # Create direct mapping of speaker name to voice_id
    voice_map = {s['name']: s['voice_id'] for s in speakers}
    
    for turn in conversation.turns:
        turn_start_time = time.time()
        
        # Generate main speech audio
        main_audio_path = os.path.join(topic_dir, f"{turn.speaker}_{turn.order}.mp3")
        if not os.path.exists(main_audio_path):
            logger.info(f"Generating main audio for {turn.speaker} turn {turn.order}")
            try:
                response = client.text_to_speech.convert(
                    voice_id=voice_map[turn.speaker],
                    output_format="mp3_44100_128",
                    text=turn.text,
                    model_id="eleven_multilingual_v2"
                )
                audio_data = b"".join(chunk for chunk in response)
                with open(main_audio_path, "wb") as f:
                    f.write(audio_data)
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Error generating audio for {turn.speaker}: {str(e)}")
                raise
        
        # Load the audio to get its duration
        main_audio = AudioSegment.from_mp3(main_audio_path)
        turn_duration_ms = len(main_audio)
        total_duration_ms += turn_duration_ms
        
        audio_files[f"{turn.speaker}_{turn.order}"] = main_audio_path
        
        # Generate overlap audio if present
        overlap_duration_ms = 0
        if turn.overlap_with:
            for overlap_speaker, overlap_text in turn.overlap_with.items():
                overlap_audio_path = os.path.join(topic_dir, f"{overlap_speaker}_overlap_{turn.order}.mp3")
                if not os.path.exists(overlap_audio_path):
                    logger.info(f"Generating overlap audio for {overlap_speaker}")
                    try:
                        response = client.text_to_speech.convert(
                            voice_id=voice_map[overlap_speaker],
                            output_format="mp3_44100_128",
                            text=overlap_text,
                            model_id="eleven_multilingual_v2"
                        )
                        audio_data = b"".join(chunk for chunk in response)
                        with open(overlap_audio_path, "wb") as f:
                            f.write(audio_data)
                        time.sleep(1)  # Rate limiting
                    except Exception as e:
                        logger.error(f"Error generating overlap audio for {overlap_speaker}: {str(e)}")
                        raise
                
                # Load overlap audio to get its duration
                overlap_audio = AudioSegment.from_mp3(overlap_audio_path)
                overlap_duration_ms += len(overlap_audio)
                
                audio_files[f"{overlap_speaker}_overlap_{turn.order}"] = overlap_audio_path
        
        # Calculate total turn duration including overlaps
        total_turn_duration_ms = turn_duration_ms + (overlap_duration_ms if overlap_duration_ms > 0 else 0)
        turn_durations.append({
            "turn": turn.order,
            "speaker": turn.speaker,
            "duration_seconds": total_turn_duration_ms / 1000,
            "has_overlap": bool(turn.overlap_with)
        })
    
    # Print analytics
    logger.info("\n=== Audio Generation Analytics ===")
    logger.info(f"Total number of turns: {len(conversation.turns)}")
    logger.info(f"Total audio duration: {total_duration_ms/1000:.2f} seconds ({total_duration_ms/60000:.2f} minutes)")
    logger.info(f"Average duration per turn: {(total_duration_ms/len(conversation.turns))/1000:.2f} seconds")
    logger.info("\nTurn-by-turn breakdown:")
    for turn_data in turn_durations:
        overlap_info = " (with overlap)" if turn_data["has_overlap"] else ""
        logger.info(f"Turn {turn_data['turn']} - {turn_data['speaker']}: {turn_data['duration_seconds']:.2f} seconds{overlap_info}")
    logger.info("================================\n")
    
    logger.success("Audio generation complete")
    return audio_files

def CreateWelcomeAudio(welcome_text: str, welcome_audio_path: str, voice_id: str) -> str:
    """Generate audio file for welcome text."""
    logger.info("Generating welcome audio...")
    try:
        response = client.text_to_speech.convert(
            voice_id=voice_id,
            output_format="mp3_44100_128",
            text=welcome_text,
            model_id="eleven_multilingual_v2"
        )
        audio_data = b"".join(chunk for chunk in response)
        with open(welcome_audio_path, "wb") as f:
            f.write(audio_data)
        time.sleep(1)  # Rate limiting
    except Exception as e:
        logger.error(f"Error generating welcome audio: {str(e)}")
        raise

    logger.success("Welcome audio generated")
    return welcome_audio_path

def mix_conversation(conversation: Conversation, audio_files: Dict[str, str]) -> str:
    """Mix the conversation audio files with natural overlaps."""
    logger.info("Mixing conversation audio...")
    
    # Initialize the final mix
    final_mix = AudioSegment.empty()
    current_position = 0
    
    for turn in conversation.turns:
        # Load main speech audio
        main_audio_path = audio_files[f"{turn.speaker}_{turn.order}"]
        main_audio = AudioSegment.from_mp3(main_audio_path)
        main_audio = normalize(main_audio)
        
        # Add main speech to mix
        final_mix = final_mix + main_audio
        
        # Process overlaps if present
        if turn.overlap_with:
            for overlap_speaker, _ in turn.overlap_with.items():
                overlap_audio_path = audio_files[f"{overlap_speaker}_overlap_{turn.order}"]
                overlap_audio = AudioSegment.from_mp3(overlap_audio_path)
                overlap_audio = normalize(overlap_audio)
                
                # Calculate overlap position (near the end of main speech)
                overlap_position = len(main_audio) - len(overlap_audio) - 500  # Start 500ms before end
                if overlap_position < 0:
                    overlap_position = 0
                
                # Create natural overlap
                final_mix = create_natural_overlap(
                    final_mix,
                    overlap_audio,
                    current_position + overlap_position
                )
        
        current_position += len(main_audio)
    
    # Export final mix
    output_path = os.path.join(os.path.dirname(audio_files[f"{conversation.turns[0].speaker}_1"]), "final_mix.mp3")
    final_mix.export(output_path, format="mp3")
    logger.success(f"Final mix saved to: {output_path}")
    
    return output_path
