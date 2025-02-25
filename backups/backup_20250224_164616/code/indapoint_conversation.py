"""Example script demonstrating how to generate natural conversations."""
from create_audio.conversation_generator import generate_conversation, print_conversation_summary
from create_audio.logger_utils import PodcastLogger
from create_audio.openai_utils import GetBestVoiceID
from create_audio.db_utils import PodcastDB
import json

# Initialize logger
logger = PodcastLogger("ConversationExample")

def main():
    """Generate example conversations with different topics and moods."""
    try:
        # Example 1: Casual AI Discussion in English
        logger.section("Example 1: Casual AI Discussion (English)")
        
        # Example business info
        business_info = {
            "type": "podcast",
            "name": "IndaPoint Technologies AI Talks",
            "website": "www.indapoint.com",
            "email": "info@indapoint.com",
            "social_media": {
                "twitter": "@indapoint",
                "instagram": "@indapoint"
            }
        }
        
        #let us fetch topic data from sample_blog.txt file
        #with open("sample_blog.txt", "r") as f:
        #    text = f.read()
            
        # audio_path, schema_path = generate_conversation(
        #     topic="Coldplay band",
        #     num_turns=5,
        #     conversation_mood="upseting",
        #     language="english",
        #     voice_accent="American",
        #     business_info=business_info,
        #     text=text
        # )
        # print_conversation_summary(schema_path)
        
        # Example 2: Technical Programming Discussion in Hindi
         #let us fetch topic data from sample_blog.txt file
        #with open("sample_blog.txt", "r") as f:
        #    text = f.read()
        #let us fetch topic data from sample_blog.txt file
        with open("sample_blog.txt", "r") as f:
           text = f.read()
        logger.section("\nIndaPoint Technologies AI Talks")
        audio_path, schema_path = generate_conversation(
            topic=text,
            num_turns=2,
            conversation_mood="explaining in simple terms",
            language="English",
            voice_accent="Indian",
            business_info=business_info,
            voice_id1="cgSgspJ2msm6clMCkdW9",
            voice_id2="iP95p4xoKVk53GoZ742B",
            speaker1_name="Jessica",
            speaker2_name="Ken"
        )
       
        
    except Exception as e:
        logger.error(f"Error in example: {str(e)}")
        raise

if __name__ == "__main__":
    main()
