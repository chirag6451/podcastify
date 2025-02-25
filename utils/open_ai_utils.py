import os
import logging
from pydantic import BaseModel
from openai import OpenAI
import json
import requests
import random
from dotenv import load_dotenv
from typing import Optional, List, Dict
from pydantic import BaseModel
load_dotenv()

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

class CreateImagePrompt(BaseModel):
    prompt: str
    



def create_image_prompt(context: str, topic: str,segment_description: str,language="english"):
    try:
       
        completion = client.beta.chat.completions.parse(
            model=os.environ.get("OPENAI_MODEL"),
            messages=[
                {"role": "system", "content": "We are creating video with images on given topic. We have divided entire video voice over into segments. Based on the given context of video on given topic, we are creating images for each segment of the video. Based on description of given segment, you need to generate image prompt that aligns with the context of the video and signifies the content of the segment. The prompt to generate image shold only for the gien topic and not for any person or animal or any other object. it should clear, insturctive with exact description of the image and in {language} language."},
                {"role": "user", "content": f"The topic is {topic} and the context is {context} and the current segment description is {segment_description} return the response in {language} language."},
            ],
            response_format=CreateImagePrompt,
        )
        message = completion.choices[0].message
        logging.info(f"Message from openai: {message}")
        if message.content:
            image_prompt = json.loads(message.content)
            prompt=image_prompt["prompt"]
    
            return prompt
        else:
            print("Failed to retrieve image prompt")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    
def transcribe_audio(audio_file_path: str) -> str:
    """
    Transcribe audio file using OpenAI Whisper API
    
    Args:
        audio_file_path (str): Path to the audio file to transcribe
        
    Returns:
        str: Transcribed text from the audio file
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcription = client.audio.translations.create(
                file=audio_file,
                model="whisper-1",
                 response_format="text"
            )
         
            return transcription.text
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return None





 # Build base prompts
system_prompt_podcast_intro  = f"""You are an expert podcast script writer.
Create a natural, emotionally expressive conversation podcast intro for the given topic and context.

Follow these rules:

1. Introduction and Structure:
    - Create a professional intro identifying the subject and setting context,base on given topic and context, for exmmple if context is about a blog post, then the intro should be about blog post, if it is about given topic, then the intro should be about the given topic, if it is about a podcast, then the intro should be about the podcast. Let us detail topic being discussed in the intro and present in question format to create curiosity and interest
    - introduce yourself as host of the podcast as per the given host name
    - do not assume or predict host name, it should be as per the given host name, if not provided, then do not assume or predict
    - the speakers in the conversation, they are not the hosts
    - Let us detail topic being discussed in the intro and present in question format to create curiosity and interest
    
    - proivde only voice over text for the intro, no effectts or music dtils 
    - Outline what listeners will learn
    - Keep intro concise (5 to 10 sentences)

    
2. Language and Cultural Context:
    - Consider cultural norms and communication styles as per the topic and context

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
    - Use ellipsis (...) for thoughtful pauses
    - Break up long sentences for natural speech flow
    - Ensure speech patterns reflect the speaker's personality and accent
"""

#create class to indetinfy if text has food items or not
class PodcatTranscript(BaseModel):
 podcast_intro: str


def get_podcast_intro(topic: str, context: str, host_name: str):
    try:
        completion = client.beta.chat.completions.parse(
            model=os.environ.get("OPENAI_MODEL"),
            messages=[
                {"role": "system", "content": system_prompt_podcast_intro},
                {"role": "user", "content": f"The topic is {topic} and the context is {context} and the host name is {host_name}"},
            ],
            response_format=PodcatTranscript,
        )
        message = completion.choices[0].message
        logging.info(f"Message from openai about podcast intro: {message}")
        if message.content:
            logging.info("Successfully retrieved details")
            return message.content
        else:
            logging.error("Failed to retrieve details")
            return None
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return None