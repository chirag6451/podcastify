import os
from pydub import AudioSegment
from pydub.effects import normalize, speedup
import re
from typing import Dict, Optional

def extract_sequence_number(filename):
    # Extract the number from filenames like "Emma_1.mp3" or "Jake_2.mp3"
    match = re.search(r'_(\d+)\.mp3$', filename)
    return int(match.group(1)) if match else 0

def extract_speaker(filename):
    # Extract speaker name from filename
    match = re.search(r'^([^_]+)_', filename)
    return match.group(1).strip() if match else ""

def get_natural_gap_duration(current_speaker, next_speaker):
    # Add longer pauses between different speakers, shorter within same speaker
    if current_speaker == next_speaker:
        return 300  # 300ms for same speaker
    return 800  # 800ms between different speakers

def apply_natural_transition(audio1, audio2, gap_duration):
    # Create a gap with the specified duration
    gap = AudioSegment.silent(duration=gap_duration)
    
    # Apply fade out to the end of first clip
    fade_duration = min(200, len(audio1))  # 200ms fade or shorter if clip is shorter
    audio1 = audio1.fade_out(fade_duration)
    
    # Apply fade in to the start of second clip
    fade_duration = min(200, len(audio2))  # 200ms fade or shorter if clip is shorter
    audio2 = audio2.fade_in(fade_duration)
    
    # Combine with gap
    return audio1 + gap + audio2

def create_natural_overlap(base_audio: AudioSegment, overlay_audio: AudioSegment, position_ms: int) -> AudioSegment:
    """Create a natural-sounding overlap between two audio segments"""
    # Parameters for natural-sounding overlap
    CROSSFADE_DURATION = 300  # 300ms crossfade
    OVERLAY_VOLUME_REDUCTION = 4  # -4dB for overlaying audio
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

def combine_audio_files(input_dir="output", output_file="combined_conversation.mp3", overlap_info: Optional[Dict] = None):
    """
    Combine audio files with support for overlapping speech.
    overlap_info should be a dictionary mapping turn numbers to overlap details:
    {
        2: {"speaker": "Emma", "text": "Oh, exactly!", "position": 1000}  # Position in ms
    }
    """
    # Ensure output directory exists
    if not os.path.exists(input_dir):
        print(f"Input directory {input_dir} does not exist!")
        return
    
    # Get all MP3 files and sort them by sequence number
    audio_files = [f for f in os.listdir(input_dir) if f.endswith('.mp3') and not f.startswith('overlap_')]
    audio_files.sort(key=extract_sequence_number)
    
    if not audio_files:
        print("No MP3 files found in the output directory!")
        return
    
    # Load and normalize the first audio file
    print(f"\nProcessing: {audio_files[0]}")
    combined = AudioSegment.from_mp3(os.path.join(input_dir, audio_files[0]))
    combined = normalize(combined)
    current_speaker = extract_speaker(audio_files[0])
    current_position = len(combined)  # Keep track of current position in ms
    
    # Append the rest of the audio files with natural transitions
    for i in range(1, len(audio_files)):
        print(f"Processing: {audio_files[i]}")
        audio_path = os.path.join(input_dir, audio_files[i])
        next_audio = AudioSegment.from_mp3(audio_path)
        next_audio = normalize(next_audio)
        
        next_speaker = extract_speaker(audio_files[i])
        gap_duration = get_natural_gap_duration(current_speaker, next_speaker)
        
        # Check for overlaps at this turn
        turn_number = extract_sequence_number(audio_files[i])
        if overlap_info and turn_number in overlap_info:
            overlap = overlap_info[turn_number]
            # Calculate overlap position - start overlay when main speaker is 1/3 through their line
            main_audio_duration = len(next_audio)
            overlap_position = current_position + (main_audio_duration // 3)
            
            # Load and apply the overlap audio
            overlap_path = os.path.join(input_dir, f"overlap_{turn_number}.mp3")
            if os.path.exists(overlap_path):
                overlap_audio = AudioSegment.from_mp3(overlap_path)
                overlap_audio = normalize(overlap_audio)
                combined = create_natural_overlap(combined, overlap_audio, overlap_position)
        
        # Apply natural transition and update position
        combined = apply_natural_transition(combined, next_audio, gap_duration)
        current_position = len(combined)
        current_speaker = next_speaker
    
    # Final normalization and dynamic compression
    combined = normalize(combined)
    
    # Export the combined audio with higher quality settings
    print("\nExporting final audio...")
    combined.export(
        output_file,
        format="mp3",
        bitrate="192k",
        parameters=["-q:a", "0"]  # Use highest quality VBR setting
    )
    print(f"Successfully created combined audio file: {output_file}")

if __name__ == "__main__":
    combine_audio_files()
