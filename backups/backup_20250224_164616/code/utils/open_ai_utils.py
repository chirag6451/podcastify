import os
import logging
from pydantic import BaseModel
from openai import OpenAI
import json
import requests
import random
from dotenv import load_dotenv
from typing import Optional, List, Dict
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



# #let us test the function
# if __name__ == "__main__":
#     context = "The video is about the benefits of eating healthy food"
#     topic = "Healthy food"
#     segment_description = "The video is about the benefits of eating healthy food"
#     print(create_image_prompt(context, topic, segment_description))

print(transcribe_audio("defaults/voiceover/final_mix.mp3")) 