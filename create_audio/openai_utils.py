from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from openai import OpenAI
from dataclasses import dataclass
import json
import re
import logging

load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class ConversationTurn:
    order: int
    speaker: str
    text: str
    overlap_with: Optional[Dict[str, str]] = None  # {"speaker": "text"} for overlapping speech

    def to_dict(self) -> Dict:
        return {
            "order": self.order,
            "speaker": self.speaker,
            "text": self.text,
            "overlap_with": self.overlap_with
        }

@dataclass
class Conversation:
    turns: List[ConversationTurn]
    topic: str
    speakers: List[str] = ("Emma", "Jake")
    
    def to_dict(self) -> Dict:
        return {
            "topic": self.topic,
            "speakers": self.speakers,
            "turns": [turn.to_dict() for turn in self.turns]
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

class OpenAIConversationGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
    
    def extract_json_from_response(self, content: str) -> Dict:
        """Extract and validate JSON from OpenAI response"""
        # Try to find JSON content between curly braces
        json_match = re.search(r'\{[^{]*"turns":[^}]*\}', content)
        if not json_match:
            raise ValueError("No valid JSON structure found in response")
        
        try:
            # Parse the JSON content
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            # Validate required fields
            if "turns" not in data:
                raise ValueError("Missing 'turns' field in response")
            
            for turn in data["turns"]:
                required_fields = ["order", "speaker", "text"]
                missing_fields = [field for field in required_fields if field not in turn]
                if missing_fields:
                    raise ValueError(f"Missing required fields in turn: {missing_fields}")
            
            return data
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON. Response content: {content}")
            raise ValueError(f"Invalid JSON format: {str(e)}")
    
    def generate_conversation(self, topic: str, num_turns: int = 6, speakers: Optional[List[str]] = None) -> Conversation:
        """Generate a natural conversation about a given topic with emotional expression and overlapping speech."""
        if speakers is None:
            speakers = ["Emma", "Jake"]
        
        system_prompt = """
        Create a natural, emotionally expressive conversation between two people about the given topic.
        Follow these rules for emotional expression and overlapping speech:

        1. Emotional Context:
           - Set proper context for emotions (e.g., excitement, curiosity, concern)
           - Maintain emotional continuity across multiple sentences
           - Use appropriate punctuation to convey emotion (!, ?, ...)

        2. Emphasis and Expression:
           - Use CAPITAL LETTERS for emphasized or important words
           - Use 'single quotes' around words with special emotional weight
           - Include natural reactions and interjections

        3. Speech Patterns:
           - Vary sentence length for natural rhythm
           - Include conversational fillers ("um", "well", "you know")
           - Use ellipsis (...) for thoughtful pauses
           - Break up long sentences for natural speech flow

        4. Overlapping Speech Rules:
           - ONLY the non-speaking person can make overlapping comments
           - Overlaps should occur at the END of the main speaker's turn
           - Keep overlapping text short (brief reactions, agreements, or interjections)
           - Example: If Emma is speaking, only Jake can make overlapping comments, and vice versa
           - Overlaps should feel like natural reactions to what was just said

        You must respond with ONLY valid JSON in this exact format:
        {
          "turns": [
            {
              "order": 1,
              "speaker": "Emma",
              "text": "You know, I find it fascinating how...",
              "overlap_with": null
            },
            {
              "order": 2,
              "speaker": "Jake",
              "text": "That's such an interesting perspective on...",
              "overlap_with": {"Emma": "[overlap]Oh, that's exactly what I was thinking!"}
            }
          ]
        }

        IMPORTANT OVERLAP RULES:
        1. overlap_with must ONLY contain the OTHER speaker, never the current speaker
        2. Overlaps must feel like natural reactions to the END of the speech
        3. Not every turn needs an overlap - use them naturally (15-20% of turns)
        """
        
        user_prompt = f"""
        Topic: {topic}
        Number of turns: {num_turns}
        Speakers: {', '.join(speakers)}
        
        Create an emotionally engaging conversation about this topic between the speakers.
        Remember:
        1. Show clear emotional progression
        2. Use emphasis (CAPITALS) for important points
        3. Include emotional expressions in 'single quotes'
        4. Maintain distinct speaker personalities
        5. ONLY allow overlaps from the non-speaking person at the END of turns
        
        Example of good overlap:
        Speaker 1: "...and that's why I believe AI will transform healthcare completely!"
        Speaker 2: [overlap]"Yes, especially in diagnostics!"

        Example of bad overlap (DO NOT DO):
        Speaker 1: "I think AI will... [overlap with self] transform healthcare"
        
        IMPORTANT: Respond with ONLY the JSON output, no additional text or explanations.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # Get the response content
            content = response.choices[0].message.content
            
            # Try to parse JSON, if it fails, try to extract JSON part
            try:
                conversation_data = json.loads(content)
            except json.JSONDecodeError:
                # Find JSON between curly braces
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if not json_match:
                    raise ValueError(f"No JSON found in response: {content}")
                conversation_data = json.loads(json_match.group(0))
            
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
            
            return Conversation(
                turns=turns,
                topic=topic,
                speakers=speakers
            )
            
        except Exception as e:
            print(f"Error generating conversation: {str(e)}")
            print(f"Response content: {content if 'content' in locals() else 'No response received'}")
            raise

def generate_conversation_about(topic: str, num_turns: int = 6) -> Conversation:
    """Convenience function to generate a conversation about a topic."""
    generator = OpenAIConversationGenerator()
    return generator.generate_conversation(topic, num_turns)

def GetBestVoiceID(voice_accent: str, language: str, topic: str, gender: str, mood: str, all_voices_records: List[dict]) -> Dict:
    """
    Get the best voice ID for a given condition.
    
    Args:
        voice_accent: The desired voice accent
        language: The language of the voice
        topic: The conversation topic
        gender: The conversation gender
        mood: The conversation mood
        all_voices_records: A list of all voice records
    
    Returns:
        A dictionary with the best voice ID and name
    """
    if not all_voices_records:
        raise ValueError("No voice records provided")

    system_prompt = """You are a voice selection expert. Your task is to compare the required voice profile against available voices and select the best match.

    RULES:
    1. You MUST ONLY select a voice from the provided available voices list
    2. You MUST return the exact voice_id and name as shown in the available voices
    3. Compare the required profile (accent, language, topic, mood, gender) with each voice's characteristics
    4. Consider labels, category, and description when matching
    5. DO NOT invent or suggest voices not in the list
    
    Return ONLY a JSON response in this format:
    {
        "voice_id": "exact_id_from_list",
        "name": "exact_name_from_list",
        "reason": "brief explanation of why this voice matches the required profile"
    }
    """
    
    # Create a clear profile of what we're looking for
    required_profile = {
        "accent": voice_accent,
        "language": language,
        "topic": topic,
        "mood": mood,
        "gender": gender
    }
    
    # Format available voices as a clear list
    available_voices = []
    for voice in all_voices_records:
        available_voices.append({
            "voice_id": voice["voice_id"],
            "accent": voice["accent"],
            "gender": voice["gender"],
            "name": voice["name"],
            "personality": voice["personality"],
            "ideal_for": voice["ideal_for"],
            "best_languages": voice["best_languages"]
        })
    
    user_prompt = f"""REQUIRED VOICE PROFILE:
{json.dumps(required_profile, indent=2)}

AVAILABLE VOICES:
{json.dumps(available_voices, indent=2)}

Compare the required profile against each available voice and select the best match.
You must return one of the exact voice_id and name combinations from the available voices list."""
    
    # Get OpenAI's recommendation
    client = OpenAI()
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    try:
        result = json.loads(response.choices[0].message.content)
        # Validate the response has required fields
        if not all(key in result for key in ["voice_id", "name", "reason"]):
            raise ValueError("Invalid response format from OpenAI")
            
        # Verify that the selected voice exists in our database
        selected_voice = next(
            (voice for voice in all_voices_records 
             if voice['voice_id'] == result['voice_id'] and voice['name'] == result['name']),
            None
        )
        
        if not selected_voice:
            raise ValueError(f"Selected voice {result['voice_id']} not found in database")
            
        return result
        
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Error processing OpenAI response: {str(e)}")
        # Return the first voice as fallback
        return {
            "voice_id": all_voices_records[0]["voice_id"],
            "name": all_voices_records[0]["name"],
            "reason": "Fallback selection due to processing error"
        }

# if __name__ == "__main__":
#     from db_utils import PodcastDB
    
#     # Get actual voices from database
#     db = PodcastDB()
#     voice_records = db.get_voice_records(limit=30)
    
#     # Test voice selection
#     result = GetBestVoiceID(
#         voice_accent="American",
#         language="english",
#         topic="The future of space travel",
#         mood="casual",
#         all_voices_records=voice_records
#     )
#     print(result)