"""Module for generating natural conversations with overlapping speech."""
import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from openai import OpenAI

from create_audio.audio_utils import generate_audio_files, mix_conversation, CreateWelcomeAudio
from create_audio.conversation import Conversation, ConversationTurn, ensure_directory
from create_audio.conversation_prompts import get_conversation_prompts
from create_audio.db_utils import PodcastDB
from create_audio.logger_utils import PodcastLogger
import config as config_settings
import random
from utils.file_writer import get_output_path
# Initialize logger
logger = PodcastLogger("ConversationGenerator", "conversation.log")

def optimise_overlapping(data, key_to_update, num_random_records):
    """
    This function processes the input JSON and keeps only a specified number of random keys in the given field.

    Parameters:
    - data (dict): The input JSON containing a `conversation` list.
    - key_to_update (str): The key within each conversation entry to process.
    - num_random_records (int): The number of random keys to retain in the specified field.

    Returns:
    - dict: The updated JSON with the specified number of random keys retained in the given field.
    """
    for entry in data['conversation']:
        if key_to_update in entry:
            overlap_keys = list(entry[key_to_update].keys())
            if len(overlap_keys) > num_random_records:
                selected_keys = random.sample(overlap_keys, num_random_records)  # Select specified number of random keys
                entry[key_to_update] = {key: entry[key_to_update][key] for key in selected_keys}
    return data

def clean_filename(text: str) -> str:
    """Clean text to create a valid and clean filename.
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text suitable for filenames
    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and special chars with underscore
    text = re.sub(r'[^a-z0-9]+', '_', text)
    # Remove multiple underscores
    text = re.sub(r'_+', '_', text)
    # Remove leading/trailing underscores
    text = text.strip('_')
    # Truncate to reasonable length
    return text[:30]

def generate_conversation(
    config: Dict,
    job_id: str,
    request_dict: Dict
) -> Tuple[str, str]:
    """
    Generate a conversation about a topic.
    
    Args:
        config: The conversation config
        job_id: The job ID
        request_dict: The request dictionary
        voice_id1: Optional voice ID for first speaker
        voice_id2: Optional voice ID for second speaker
        speaker1_name: Optional name for first speaker (default: "Speaker1")
        speaker2_name: Optional name for second speaker (default: "Speaker2")
        output_dir: Optional output directory
    
    Returns:
        Tuple of (audio_path, schema_path)
    """
    
    #IF WE HAVE SET STATIC_AUDIO IN .ENV we just return the static audio files 
    if os.getenv('STATIC_AUDIO') == 'true':
        audio_path=config_settings.STATIC_AUDIO_PATH
        schema_path = config_settings.STATIC_SCHEMA_PATH
        welcome_audio_path = config_settings.STATIC_WELCOME_PATH
        return audio_path, schema_path, welcome_audio_path
    
    client = OpenAI()
    
   
    #print(json.dumps(config, indent=4))
    
    # Create output directory if not provided
    
    
    try:
        # Use provided voice IDs or select speakers from database
        if config.get("voice_settings_voice_id1") and config.get("voice_settings_voice_id2"):
            logger.info("Using provided voice IDs...")
            speakers = [
                {
                    "name": config.get("voice_settings_speaker1_name") or "Speaker1",
                    "voice_id": config.get("voice_settings_voice_id1"),
                    "language": config.get("voice_settings_language"),
                    "accent": config.get("voice_settings_voice_accent"),
                    "personality": "friendly",
                    "speaking_style": config.get("voice_settings_conversation_mood")
                },
                {
                    "name": config.get("voice_settings_speaker2_name") or "Speaker2",
                    "voice_id": config.get("voice_settings_voice_id2"),
                    "language": config.get("voice_settings_language"),
                    "accent": config.get("voice_settings_voice_accent"),
                    "personality": "analytical",
                    "speaking_style": config.get("voice_settings_conversation_mood")
                }
            ]
        else:
            # Select speakers from database
            logger.section(f"Generating {config.get('voice_settings_language')} conversation about {request_dict.get('topic')}")
            db = PodcastDB()
            speakers = db.select_speakers_from_db(request_dict.get("topic"), config.get("voice_settings_conversation_mood"), config.get("voice_settings_language"), config.get("voice_settings_voice_accent"))
  
    
    #let us create a dict of business_info json from the config
        business_info = {
            "type": config.get("business_info_type", ""),
            "name": config.get("business_info_name", ""),
            "website": config.get("business_info_website", ""),
            "email": config.get("business_info_email", ""),
            "social_media": {
                "linkedin": config.get("business_info_social_media_linkedin", ""),
                "twitter": config.get("business_info_social_media_twitter", "")
            }
        }
    
        system_prompt, user_prompt = get_conversation_prompts(
            topic=request_dict.get("topic"),
            num_turns=config.get("voice_settings_num_turns"),
            speakers=speakers,
            conversation_mood=config.get("voice_settings_conversation_mood"),
            language=config.get("voice_settings_language"),
            voice_accent=config.get("voice_settings_voice_accent"),
            business_info=business_info
        )
      
        
        logger.info(f"Generating conversation using OpenAI in {config.get('voice_settings_language')}...")
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini-2024-07-18	"),
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Parse the response
        conversation_data = json.loads(response.choices[0].message.content)
        #let us print in nice format
    
        
        # Convert to our conversation class
        turns = []
        
        # Map 'Host' to first speaker for intro/outro
        host_speaker = speakers[0]["name"]
        
        # Add intro if present
        if "intro" in conversation_data and conversation_data["intro"]:
            intro_turn = ConversationTurn(
                order=0,
                speaker=host_speaker,  # Always use first speaker as host
                text=conversation_data["intro"]["text"],
                overlap_with={}
            )
            turns.append(intro_turn)
        
        # Add main conversation turns
        for turn in conversation_data["conversation"]:
            speaker_name = turn["speaker"]
            # Map 'Host' to first speaker if needed
            if speaker_name.lower() == "host":
                speaker_name = host_speaker
                
            turns.append(
                ConversationTurn(
                    order=turn["order"],
                    speaker=speaker_name,
                    text=turn["text"],
                    overlap_with=turn.get("overlap_with", {})
                )
            )
        
        # Add outro if present
        if "outro" in conversation_data and conversation_data["outro"]:
            outro_turn = ConversationTurn(
                order=len(turns) + 1,
                speaker=host_speaker,  # Always use first speaker as host
                text=conversation_data["outro"]["text"],
                overlap_with={}
            )
            turns.append(outro_turn)
        
        #find out topic summry from the conversation data
        welcome_voiceover = conversation_data.get("welcome_voiceover", "")
        # Create a conversation
        conversation = Conversation(
            turns=turns,
            topic=request_dict.get("topic"),
            speakers=[s["name"] for s in speakers],
            intro=conversation_data.get("intro", {}),
            outro=conversation_data.get("outro", {})
        )
        
        # Print conversation summary
     
        # Save the conversation schema
        schema_path, schema_output_dir = get_output_path(
            filename="conversation.json",
            profile_name=request_dict.get("profile_name"),
            customer_id=request_dict.get("customer_id"),
            job_id=job_id,
            theme=request_dict.get("theme", "default"),
            timestamp_format="%Y%m%d_%H%M%S",
            create_dir=True
        )
        
        with open(schema_path, "w") as f:
            json.dump(conversation.to_dict(), f, indent=2)
        
        logger.info(f"Saved conversation schema to {schema_path}")
        
        # Generate audio files
        logger.info("Generating audio files...")
        _, output_dir = get_output_path(
            filename="dummy.txt",  # We only need the directory
            profile_name=request_dict.get("profile_name"),
            customer_id=request_dict.get("customer_id"),
            job_id=job_id,
            theme=request_dict.get("theme", "default"),
            timestamp_format="%Y%m%d_%H%M%S",
            create_dir=True
        )
        
        # Generate audio files
        logger.info("Generating audio files...")
        audio_files = generate_audio_files(conversation, output_dir, speakers)
        
        #let us generate welcome voiceover
        logger.info("Generating welcome voiceover...")
        welcome_audio_path = os.path.join(output_dir, "welcome.mp3")
        welcome_audio = CreateWelcomeAudio(welcome_voiceover, welcome_audio_path, speakers[0]["voice_id"])
        # Mix the conversation
        logger.info("Mixing conversation...")
        output_path = mix_conversation(conversation, audio_files)
        
        logger.success(f"Generated conversation at {output_path}")
       
        return output_path, schema_path, welcome_audio,welcome_voiceover
    
    except Exception as e:
        logger.error(f"Error generating conversation: {str(e)}")
        raise

def print_conversation_summary(schema_path: str):
    """Print a summary of the conversation flow."""
    with open(schema_path, "r") as f:
        data = json.load(f)
    
    logger.info("\nConversation Summary:")
    for turn in data["conversation"]:
        overlap_info = f" (overlaps with {turn['overlap_with']})" if turn.get("overlap_with") else ""
        logger.info(f"{turn['speaker']}: {turn['text'][:50]}...{overlap_info}")
