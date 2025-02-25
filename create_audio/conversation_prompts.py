"""Module for managing conversation generation prompts."""
from typing import List, Tuple, Dict, Optional
import json
import logging

logger = logging.getLogger(__name__)

def get_personality_description(speaker: Dict) -> str:
    """Get a description of the speaker's personality."""
    try:
        if 'personality' not in speaker:
            return "friendly and professional"
            
        personality = speaker['personality']
        if isinstance(personality, str):
            try:
                personality = json.loads(personality)
            except json.JSONDecodeError:
                # If not valid JSON, use the string as is
                return personality
                
        if isinstance(personality, dict):
            return ", ".join(f"{k}: {v}" for k, v in personality.items())
        
        return str(personality)
    except Exception as e:
        logger.warning(f"Error getting personality description: {e}")
        return "friendly and professional"

def get_language_description(speaker: Dict) -> str:
    """Get a description of the speaker's language capabilities."""
    try:
        language = speaker.get('language', 'english')
        accent = speaker.get('accent', 'neutral')
        return f"Speaks {language} with a {accent} accent"
    except Exception as e:
        logger.warning(f"Error getting language description: {e}")
        return "Speaks English with a neutral accent"

def get_conversation_prompts(
    topic: str,
    num_turns: int,
    speakers: List[dict],
    conversation_mood: str,
    language: str = "english",
    voice_accent: str = "American",
    business_info: Optional[Dict] = None
) -> Tuple[str, str]:
    """
    Get system and user prompts for conversation generation.
    
    Args:
        topic: The conversation topic
        num_turns: Number of conversation turns
        speakers: List of speaker information
        conversation_mood: Mood/style of the conversation
        language: Conversation language
        voice_accent: Preferred accent
        business_info: Optional dictionary containing:
            - type: "business", "personal", or "podcast"
            - name: Business/Personal/Podcast name
            - website: Website URL
            - email: Contact email
            - phone: Contact phone
            - social_media: Dict of social media handles
    """
    if len(speakers) < 2:
        raise ValueError("Need at least 2 speakers for conversation")
    
    # Build speaker descriptions section
    speaker_descriptions = []
    for s in speakers:
        description = f"- {s['name']}: {get_personality_description(s)}\n"
        description += f"  {get_language_description(s)}"
        speaker_descriptions.append(description)
    speaker_section = "\n".join(speaker_descriptions)
    
    # Build examples section
    speaker1, speaker2 = speakers[0], speakers[1]
    example_overlap = f"{speaker1['name']}: \"...and that's why I believe this is so important!\"\n{speaker2['name']}: [overlap]\"Oh!\""
    example_bad = f"{speaker1['name']}: \"I think... [overlap with self] this is important\""
    
    # Build base prompts
    system_prompt = f"""You are an expert podcast script writer.
    Create a natural, emotionally expressive conversation in {language.upper()} between speakers about the given topic.

    Follow these rules:

    1. Introduction and Structure:
       - Create a professional intro identifying the subject and setting context, for exmmple if context is about a blog post, then the intro should be about blog post, if it is about given topic, then the intro should be about the given topic, if it is about a podcast, then the intro should be about the podcast. Let us detail topic being discussed in the intro and present in question format to create curiosity and interest
       - Mention host/business credentials if provided
       - Outline what listeners will learn
       - Keep intro concise (5 to 10 sentences)
       
    2. Language and Cultural Context:
       - Generate the conversation entirely in {language.upper()}
       - Use appropriate cultural references and idioms for {language.upper()} speakers
       - Maintain natural speech patterns common in {language.upper()}
       - Consider cultural norms and communication styles

    3. Emotional Context:
       - Set proper context for emotions matching the conversation mood
       - Maintain emotional continuity across multiple sentences
       - Use appropriate punctuation to convey emotion (!, ?, ...)
       - Ensure each speaker's personality and accent are reflected in their speech

    4. Emphasis and Expression:
       - Use CAPITAL LETTERS for emphasized or important points
       - Use 'single quotes' around words with special emotional weight
       - Include natural reactions and interjections that match each speaker's personality
       - Adapt language and expressions to match the mood and speaker's accent

    5. Speech Patterns:
       - Vary sentence length for natural rhythm
       - Include conversational fillers appropriate for {language.upper()}
       - Use ellipsis (...) for thoughtful pauses
       - Break up long sentences for natural speech flow
       - Ensure speech patterns reflect the speaker's personality and accent

    6. Overlapping Speech Rules:
       - ONLY one or two overlaps in entire conversation
       - Use overlapping speech to convey shared thoughts or ideas
       - Only short words for overlapping speech
       - Avoid repeating the same words
       - Use different words to convey different meanings

    7. Outro and Call-to-Action:
       - Summarize key discussion points
       - Include a compelling call-to-action
       - Naturally integrate contact information if provided
       - Thank listeners
       - Keep outro concise (2-3 sentences)

    8. Welcome voice-over:
       - Welcome and greet audience with context of business details provided and to podcast and provide reason for discussing it
       - Introduce the topic first and provide reason for discussing it
       - Provide a brief overview of the topic
       - Keep the summary concise (5 sentences)
       - Use appropriate language and expressions

    Required JSON Output Format:
    {{
    
    "Podcast_topic_intro": "Intro to podcast topic",
      "intro": {{
        "text": "Professional introduction text",
        "speaker": "Host name"
      }},
      "conversation": [
        {{
          "order": 1,
          "speaker": "Speaker1",
          "text": "Main speech text...",
          "overlap_with": {{
            "Speaker2": "Brief overlapping reaction"
          }}
        }}
      ],
      "outro": {{
        "text": "Professional outro with CTA",
        "speaker": "Host name"
      }}
      "welcome_voiceover": "Voiceover to welcome audience to podcast with brief introduction to topic"  
    }},
      "welcome_voiceover": ""
    }}

    Available Speakers:
    {speaker_section}

    Example of good overlap:
    {example_overlap}

    Example of BAD overlap (don't do this):
    {example_bad}
    """
    
    # Create business/personal info string
    contact_info = ""
    if business_info:
        type_str = business_info.get('type', 'podcast')
        if type_str == "business":
            contact_info = f"Business: {business_info.get('name', '')}"
        elif type_str == "personal":
            contact_info = f"Host: {business_info.get('name', '')}"
        else:
            contact_info = f"Podcast: {business_info.get('name', '')}"
            
        if business_info.get('website'):
            contact_info += f"\nWebsite: {business_info['website']}"
        if business_info.get('email'):
            contact_info += f"\nEmail: {business_info['email']}"
        if business_info.get('phone'):
            contact_info += f"\nPhone: {business_info['phone']}"
        if business_info.get('social_media'):
            socials = business_info['social_media']
            contact_info += "\nSocial Media: " + ", ".join(f"{k}: {v}" for k, v in socials.items())
    
    user_prompt = f"""Generate a natural {conversation_mood} conversation in {language.upper()} between {speaker1['name']} and {speaker2['name']} about {topic}.

    The conversation should:
    1. Start with a professional introduction that identifies the subject
    2. Be {num_turns} turns long
    3. Match each speaker's personality and accent
    4. Maintain the {conversation_mood} mood throughout
    5. Have emotional depth and natural flow
    6. Use appropriate {language.upper()} expressions and cultural context
    7. End with a compelling outro and call-to-action
    
    {contact_info if contact_info else ""}
    """
    
    return system_prompt, user_prompt
