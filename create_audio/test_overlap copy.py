import json
from pydub import AudioSegment
from pydub.effects import normalize
import os
from openai import OpenAI
from typing import Optional, List, Dict
from datetime import datetime
import time
import os
from dotenv import load_dotenv

import re

load_dotenv()

class ConversationTurn:
    def __init__(self, order: int, speaker: str, text: str, overlap_with: Optional[Dict[str, str]] = None):
        self.order = order
        self.speaker = speaker
        self.text = text
        self.overlap_with = overlap_with

class Conversation:
    def __init__(self, turns: List[ConversationTurn], topic: str, speakers: List[str]):
        self.turns = turns
        self.topic = topic
        self.speakers = speakers

class Speaker:
    def __init__(self, name: str, voice_id: str, personality: str):
        self.name = name
        self.voice_id = voice_id
        self.personality = personality

def get_voice_id(speaker_name: str, speakers: List[Speaker]) -> str:
    """Get the correct voice ID for a speaker"""
    for speaker in speakers:
        if speaker.name == speaker_name:
            return speaker.voice_id
    raise ValueError(f"No voice ID found for speaker {speaker_name}")

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

def generate_test_conversation(
    topic: str = "God Ganesha's wisdom",
    num_turns: int = 6,
    speakers: Optional[List[Speaker]] = None,
    conversation_mood: str = "casual"
) -> Conversation:
    """Generate a test conversation with proper overlapping speech."""
    client = OpenAI()
    
    if speakers is None:
        speakers = [
            Speaker("Emma", "21m00Tcm4TlvDq8ikWAM", "friendly and enthusiastic"),
            Speaker("Jake", "2EiwWnXFnvU5JabPnv8n", "thoughtful and analytical")
        ]
    
    # Build speaker personalities section
    speaker_personalities = "\n".join(f"- {s.name}: {s.personality}" for s in speakers)
    
    # Build examples section
    speaker1, speaker2 = speakers[0], speakers[1]
    example_overlap = speaker1.name + ": \"...and that's why I believe this is so important!\"\n" + speaker2.name + ": [overlap]\"Oh, that's fascinating!\""
    example_bad = speaker1.name + ": \"I think... [overlap with self] this is important\""
    
    # Build base prompts
    base_system = """
    Create a natural, emotionally expressive conversation between speakers about the given topic.
    
    Follow these rules for emotional expression and overlapping speech:

    1. Emotional Context:
       - Set proper context for emotions matching the conversation mood
       - Maintain emotional continuity across multiple sentences
       - Use appropriate punctuation to convey emotion (!, ?, ...)
       - Ensure each speaker's personality is reflected in their speech

    2. Emphasis and Expression:
       - Use CAPITAL LETTERS for emphasized or important points
       - Use 'single quotes' around words with special emotional weight
       - Include natural reactions and interjections that match each speaker's personality
       - Adapt language and expressions to match the mood

    3. Speech Patterns:
       - Vary sentence length for natural rhythm
       - Include conversational fillers ("um", "well", "you know") appropriate to each personality
       - Use ellipsis (...) for thoughtful pauses
       - Break up long sentences for natural speech flow
       - Ensure speech patterns reflect both the speaker's personality and conversation mood

    4. Overlapping Speech Rules:
       - ONLY the non-speaking person can make overlapping comments
       - Overlaps MUST occur at the END of the main speaker's turn
       - Keep overlapping text short (brief reactions, agreements, or interjections)
       - Overlaps should match both the speaker's personality and the conversation mood

    You must respond with ONLY valid JSON in this exact format:
    {
      "turns": [
        {
          "order": 1,
          "speaker": "SpeakerName",
          "text": "Speech text...",
          "overlap_with": null
        },
        {
          "order": 2,
          "speaker": "OtherSpeaker",
          "text": "Response text...",
          "overlap_with": {"SpeakerName": "[overlap]Reaction text!"}
        }
      ]
    }

    IMPORTANT OVERLAP RULES:
    1. overlap_with must ONLY contain the OTHER speaker, never the current speaker
    2. Overlaps must feel like natural reactions to the END of the speech
    3. Not every turn needs an overlap - use them naturally (15-20% of turns)
    4. Ensure overlaps match both the speaker's personality and conversation mood
    """
    
    # Combine prompts with dynamic content
    system_prompt = "Conversation Mood: " + conversation_mood + "\n" + \
                    "The overall tone should match this mood throughout the conversation.\n" + \
                    "\nSpeaker Personalities:\n" + speaker_personalities + "\n" + \
                    base_system
    
    user_prompt = "Topic: " + topic + "\n" + \
                  "Number of turns: " + str(num_turns) + "\n" + \
                  "Conversation Mood: " + conversation_mood + "\n" + \
                  "\nCreate an emotionally engaging " + conversation_mood + " conversation about this topic between the speakers.\n" + \
                  "Remember:\n" + \
                  "1. Show clear emotional progression matching the " + conversation_mood + " mood\n" + \
                  "2. Use emphasis (CAPITALS) for important points\n" + \
                  "3. Include emotional expressions in 'single quotes'\n" + \
                  "4. Maintain each speaker's unique personality:\n" + speaker_personalities + "\n" + \
                  "5. ONLY allow overlaps from the non-speaking person at the END of turns\n" + \
                  "\nExample of good overlap (matching personality and mood):\n" + example_overlap + "\n" + \
                  "\nExample of bad overlap (DO NOT DO):\n" + example_bad + "\n" + \
                  "\nIMPORTANT: Respond with ONLY the JSON output, no additional text or explanations."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        conversation_data = json.loads(content)
        
        # Convert to our conversation class
        turns = [
            ConversationTurn(
                order=turn["order"],
                speaker=turn["speaker"],
                text=turn["text"],
                overlap_with=turn.get("overlap_with")
            )
            for turn in conversation_data["turns"]
        ]
        
        conversation = Conversation(
            turns=turns,
            topic=topic,
            speakers=[s.name for s in speakers]
        )
        
        # Save conversation to a unique directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        topic_dir = os.path.join("output", f"{topic.replace(' ', '_')}_{timestamp}")
        os.makedirs(topic_dir, exist_ok=True)
        
        schema_path = os.path.join(topic_dir, "conversation_schema.json")
        with open(schema_path, 'w') as f:
            json.dump({
                "conversation": {
                    "topic": topic,
                    "mood": conversation_mood,
                    "speakers": [
                        {
                            "name": s.name,
                            "personality": s.personality
                        }
                        for s in speakers
                    ],
                    "turns": [
                        {
                            "order": turn.order,
                            "speaker": turn.speaker,
                            "text": turn.text,
                            "overlap_with": turn.overlap_with
                        }
                        for turn in turns
                    ]
                }
            }, f, indent=2)
        
        print(f"Generated {conversation_mood} conversation schema saved to: {schema_path}")
        return conversation, schema_path, speakers
    
    except Exception as e:
        print(f"Error generating conversation: {str(e)}")
        raise

def generate_audio_files(conversation: Conversation, topic_dir: str, speakers: List[Speaker]):
    """Generate audio files for both main speech and overlaps."""
    from elevanlab_util import client
    
    print("\nGenerating audio files...")
    for turn in conversation.turns:
        # Generate main speech audio
        main_audio_path = os.path.join(topic_dir, f"{turn.speaker}_{turn.order}.mp3")
        if not os.path.exists(main_audio_path):
            print(f"Generating main audio for {turn.speaker} turn {turn.order}")
            audio_bytes = client.text_to_speech.convert(
                voice_id=get_voice_id(turn.speaker, speakers),
                output_format="mp3_44100_128",
                text=turn.text,
                model_id="eleven_multilingual_v2"
            )
            with open(main_audio_path, "wb") as f:
                f.write(b"".join(chunk for chunk in audio_bytes))
            time.sleep(1)  # Rate limiting
        
        # Generate overlap audio if present
        if turn.overlap_with:
            for speaker, text in turn.overlap_with.items():
                if speaker == turn.speaker:
                    print(f"Warning: Skipping overlap where {speaker} overlaps with themselves")
                    continue
                
                overlap_path = os.path.join(topic_dir, f"overlap_{turn.order}.mp3")
                if not os.path.exists(overlap_path):
                    print(f"Generating overlap audio for {speaker} in turn {turn.order}")
                    overlap_text = text.replace("[overlap]", "").strip()
                    audio_bytes = client.text_to_speech.convert(
                        voice_id=get_voice_id(speaker, speakers),
                        output_format="mp3_44100_128",
                        text=overlap_text,
                        model_id="eleven_multilingual_v2"
                    )
                    with open(overlap_path, "wb") as f:
                        f.write(b"".join(chunk for chunk in audio_bytes))
                    time.sleep(1)  # Rate limiting

def test_natural_conversation(schema_path: str = None):
    # Load the conversation schema
    if schema_path is None:
        schema_path = "/Users/chiragahmedabadi/dev/mypodcast/output/God_Ganesha_20250126_105233_39782639/conversation_schema.json"
    topic_dir = os.path.dirname(schema_path)
    
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    
    print("\nAnalyzing conversation structure:")
    print(f"Topic: {schema['conversation']['topic']}")
    print(f"Total turns: {len(schema['conversation']['turns'])}")
    
    # Load all audio files in sequence
    combined = None
    current_position = 0
    last_speaker = None
    
    for turn in schema['conversation']['turns']:
        print(f"\nProcessing turn {turn['order']}:")
        print(f"Speaker: {turn['speaker']}")
        print(f"Text: {turn['text']}")
        
        # Load main audio
        main_audio_path = os.path.join(topic_dir, f"{turn['speaker']}_{turn['order']}.mp3")
        if not os.path.exists(main_audio_path):
            print(f"Warning: Missing audio file {main_audio_path}")
            continue
        
        main_audio = AudioSegment.from_mp3(main_audio_path)
        main_audio = normalize(main_audio)
        
        # First turn initializes the combined audio
        if combined is None:
            combined = main_audio
            current_position = len(combined)
            last_speaker = turn['speaker']
            continue
        
        # Add a small gap between turns
        gap_duration = 500  # 500ms gap
        combined = combined + AudioSegment.silent(duration=gap_duration)
        current_position = len(combined)
        
        # Add the main audio
        combined = combined + main_audio
        main_end_position = len(combined)
        
        # Handle overlaps if present
        if turn.get('overlap_with'):
            for speaker, text in turn['overlap_with'].items():
                # Ensure overlapping speaker is different from main speaker
                if speaker == turn['speaker']:
                    print(f"Warning: Skipping overlap where speaker {speaker} overlaps with themselves")
                    continue
                
                print(f"  Overlap by {speaker}: {text}")
                
                # Load overlap audio
                overlap_path = os.path.join(topic_dir, f"overlap_{turn['order']}.mp3")
                if not os.path.exists(overlap_path):
                    print(f"Warning: Missing overlap audio file {overlap_path}")
                    continue
                
                overlap_audio = AudioSegment.from_mp3(overlap_path)
                overlap_audio = normalize(overlap_audio)
                
                # Calculate overlap position to start in last 2 seconds of main audio
                OVERLAP_DURATION = 2000  # 2 seconds in milliseconds
                main_duration = len(main_audio)
                overlap_duration = len(overlap_audio)
                
                # If main audio is shorter than 2 seconds, start overlap at midpoint
                if main_duration <= OVERLAP_DURATION:
                    overlap_position = current_position + (main_duration // 2)
                else:
                    # Start overlap in last 2 seconds
                    overlap_position = main_end_position - min(OVERLAP_DURATION, overlap_duration)
                
                combined = create_natural_overlap(combined, overlap_audio, overlap_position)
        
        last_speaker = turn['speaker']
    
    if combined:
        # Create test output directory
        test_output_dir = os.path.join(topic_dir, "natural_mix")
        os.makedirs(test_output_dir, exist_ok=True)
        
        # Export final mix
        output_file = os.path.join(test_output_dir, "natural_conversation.mp3")
        combined.export(output_file, format="mp3", bitrate="192k")
        print(f"\nCreated natural conversation mix: {output_file}")
        
        # Print conversation flow
        print("\nFinal conversation flow:")
        for turn in schema['conversation']['turns']:
            print(f"\n{turn['order']}. {turn['speaker']}: {turn['text']}")
            if turn.get('overlap_with'):
                for speaker, text in turn['overlap_with'].items():
                    if speaker != turn['speaker']:  # Only show valid overlaps
                        print(f"   → {speaker} overlaps at end: {text}")

if __name__ == "__main__":
    # Example usage with custom speakers and mood
    custom_speakers = [
        Speaker("David", "2EiwWnXFnvU5JabPnv8n", "intellectual and curious"),
        Speaker("Sarah", "21m00Tcm4TlvDq8ikWAM", "empathetic and insightful")
    ]
    
    print("Generating and testing natural conversation...")
    conversation, schema_path, speakers = generate_test_conversation(
        topic="The philosophy of mindfulness",
        num_turns=6,
        speakers=custom_speakers,
        conversation_mood="philosophical"
    )
    
    # Generate audio files
    topic_dir = os.path.dirname(schema_path)
    generate_audio_files(conversation, topic_dir, speakers)
    
    # Mix the conversation with overlaps
    test_natural_conversation(schema_path)
    print("\nDone! Check the natural_mix directory for the final audio file.")
