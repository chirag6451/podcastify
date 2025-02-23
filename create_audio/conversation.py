"""Module for conversation generation and processing."""
import time
from create_audio.elevanlab_util import client
import os
import json
from dotenv import load_dotenv
from create_audio.openai_utils import generate_conversation_about
from create_audio.combine_audio import combine_audio_files
from datetime import datetime
import uuid
from typing import Optional, List, Dict

load_dotenv()

class ConversationTurn:
    def __init__(self, order: int, speaker: str, text: str, overlap_with: Optional[Dict[str, str]] = None):
        self.order = order
        self.speaker = speaker
        self.text = text
        self.overlap_with = overlap_with
    
    def to_dict(self) -> Dict:
        """Convert turn to dictionary format"""
        return {
            "order": self.order,
            "speaker": self.speaker,
            "text": self.text,
            "overlap_with": self.overlap_with
        }

class Conversation:
    """Class representing a conversation between multiple speakers."""
    
    def __init__(self, turns: List[ConversationTurn], topic: str, speakers: List[str], 
                 intro: Optional[Dict] = None, outro: Optional[Dict] = None):
        """
        Initialize a conversation.
        
        Args:
            turns: List of conversation turns
            topic: Topic of conversation
            speakers: List of speaker names
            intro: Optional intro section with text and speaker
            outro: Optional outro section with text and speaker
        """
        self.turns = turns
        self.topic = topic
        self.speakers = speakers
        self.intro = intro or {}
        self.outro = outro or {}
    
    def to_dict(self) -> Dict:
        """Convert conversation to dictionary format"""
        return {
            "topic": self.topic,
            "intro": self.intro,
            "conversation": [turn.to_dict() for turn in self.turns],
            "outro": self.outro,
            "speakers": self.speakers
        }

def ensure_directory(directory):
    """Ensure the directory exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_unique_conversation_id():
    """Generate a unique identifier for the conversation"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]  # Use first 8 characters of UUID
    return f"{timestamp}_{unique_id}"

def generate_audio(text: str, voice_id: str, output_path: str):
    """Generate audio for a piece of text"""
    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        output_format="mp3_44100_128",
        text=text,
        model_id="eleven_multilingual_v2"
    )
    
    # Consume the generator to get the audio bytes
    audio_data = b"".join(chunk for chunk in audio)
    with open(output_path, "wb") as f:
        f.write(audio_data)

def save_conversation_schema(conversation, topic_dir: str, conversation_id: str):
    """Save the conversation schema as JSON for future reference"""
    schema_file = os.path.join(topic_dir, "conversation_schema.json")
    
    schema_data = {
        "id": conversation_id,
        "timestamp": datetime.now().isoformat(),
        "conversation": conversation.to_dict(),
        "metadata": {
            "topic": conversation.topic,
            "num_turns": len(conversation.turns),
            "speakers": conversation.speakers,
            "has_overlaps": any(turn.overlap_with for turn in conversation.turns)
        }
    }
    
    with open(schema_file, "w", encoding="utf-8") as f:
        json.dump(schema_data, f, indent=2, ensure_ascii=False)
    
    return schema_file

def get_voice_id(speaker: str) -> str:
    """Get the voice ID for a speaker"""
    voice_id_map = {
        "Emma": "21m00Tcm4TlvDq8ikWAM",
        "Other": "2EiwWnXFnvU5JabPnv8n"
    }
    return voice_id_map.get(speaker, "2EiwWnXFnvU5JabPnv8n")

def conversation_sequence(topic: str = "The future of artificial intelligence", num_turns: int = 6):
    """Generate and process a conversation about the given topic"""
    # Generate a unique identifier for this conversation
    conversation_id = get_unique_conversation_id()
    
    # Create topic-specific directory for individual audio files
    topic_dir = os.path.join("output", f"{topic.replace(' ', '_')}_{conversation_id}")
    ensure_directory(topic_dir)
    
    # Generate conversation using OpenAI
    print(f"\nGenerating conversation about: {topic}")
    print(f"Conversation ID: {conversation_id}")
    conversation_data = generate_conversation_about(topic, num_turns)
    
    # Convert conversation data to Conversation object
    conversation_turns = []
    speakers = set()
    for turn in conversation_data:
        conversation_turn = ConversationTurn(turn["order"], turn["speaker"], turn["text"], turn.get("overlap_with"))
        conversation_turns.append(conversation_turn)
        speakers.add(turn["speaker"])
    conversation = Conversation(conversation_turns, topic, list(speakers))
    
    # Save the conversation schema
    schema_file = save_conversation_schema(conversation, topic_dir, conversation_id)
    print(f"Saved conversation schema to: {schema_file}")
    
    # Dictionary to store overlap information
    overlap_info = {}
    
    # Process each turn and generate audio
    print("\nGenerating audio for each turn...")
    for turn in conversation.turns:
        # Generate audio using ElevenLabs
        print(f"\nProcessing {turn.speaker}'s turn ({turn.order})...")
        
        # Select voice based on speaker
        voice_id = get_voice_id(turn.speaker)
        
        # Generate main audio
        audio_save_path = os.path.join(topic_dir, f"{turn.speaker}_{turn.order}.mp3")
        generate_audio(turn.text, voice_id, audio_save_path)
        
        # Handle overlapping speech if present
        if turn.overlap_with:
            for overlap_speaker, overlap_text in turn.overlap_with.items():
                # Remove [overlap] tag for audio generation
                clean_text = overlap_text.replace("[overlap]", "").strip()
                
                # Generate overlap audio with slightly faster speed for natural interruption
                overlap_voice_id = get_voice_id(overlap_speaker)
                overlap_path = os.path.join(topic_dir, f"overlap_{turn.order}.mp3")
                
                # Add some emphasis to the overlapping speech
                emphasized_text = f'<emphasis level="strong">{clean_text}</emphasis>'
                generate_audio(emphasized_text, overlap_voice_id, overlap_path)
                
                # Store overlap information (position will be calculated during combination)
                overlap_info[turn.order] = {
                    "speaker": overlap_speaker,
                    "text": clean_text
                }
        
        print(f"{turn.order}. {turn.speaker}: {turn.text}")
        if turn.overlap_with:
            for speaker, text in turn.overlap_with.items():
                print(f"   [Overlap] {speaker}: {text}")
        time.sleep(1)
    
    # Combine all audio files
    print("\nCombining audio files...")
    output_file = os.path.join("output", f"conversation_{topic.replace(' ', '_')}_{conversation_id}.mp3")
    combine_audio_files(input_dir=topic_dir, output_file=output_file, overlap_info=overlap_info)
    print(f"\nFinal conversation audio saved to: {output_file}")
    
    # Save conversation text for reference
    text_output = os.path.join(topic_dir, "conversation.txt")
    with open(text_output, "w", encoding="utf-8") as f:
        f.write(f"Topic: {topic}\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for turn in conversation.turns:
            f.write(f"{turn.order}. {turn.speaker}: {turn.text}\n")
            if turn.overlap_with:
                for speaker, text in turn.overlap_with.items():
                    f.write(f"   [Overlap] {speaker}: {text}\n")
    
    return output_file, topic_dir, schema_file

if __name__ == "__main__":
    # Example usage with default topic
    output_file, topic_dir, schema_file = conversation_sequence("God Ganesha")
    print(f"\nGenerated files:")
    print(f"1. Audio: {output_file}")
    print(f"2. Schema: {schema_file}")
    print(f"3. Directory: {topic_dir}")
    
    # Or specify your own topic and number of turns
    # conversation_sequence("Space exploration in 2024", num_turns=8)
