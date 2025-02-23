"""Example script demonstrating how to generate natural conversations."""
from conversation_generator import generate_conversation, print_conversation_summary
from logger_utils import PodcastLogger
from openai_utils import GetBestVoiceID
from db_utils import PodcastDB
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
            "name": "Tech Talks Today",
            "website": "www.techtalkspodcast.com",
            "email": "host@techtalkspodcast.com",
            "social_media": {
                "twitter": "@techtalkspod",
                "instagram": "@techtalkstoday"
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
        logger.section("\nExample 2: Technical Programming Discussion")
        audio_path, schema_path = generate_conversation(
            topic=text,
            num_turns=1,
            conversation_mood="explaining in simple terms",
            language="English",
            voice_accent="Indian",
            business_info=business_info,
            voice_id1="H6QPv2pQZDcGqLwDTIJQ",
            voice_id2="u7bRcYbD7visSINTyAT8",
            speaker1_name="Priya",
            speaker2_name="Rahul"
        )
       
        # # Example 3: Philosophical Debate in Spanish
        # logger.section("\nExample 3: Philosophical Debate (Spanish)")
        # audio_path, schema_path = generate_conversation(
        #     topic="The nature of consciousness and human experience",
        #     num_turns=10,
        #     conversation_mood="philosophical",
        #     language="spanish"
        # )
        
        # # Example 4: Storytelling in Japanese
        # logger.section("\nExample 4: Storytelling (Japanese)")
        # audio_path, schema_path = generate_conversation(
        #     topic="Traditional Japanese folklore",
        #     num_turns=6,
        #     conversation_mood="storytelling",
        #     language="japanese"
        # )
        # print_conversation_summary(schema_path)
        
        # # Example 5: Using specific voice IDs
        # logger.section("\nExample 5: Direct Voice IDs")
        # audio_path, schema_path = generate_conversation(
        #     topic="The future of AI",
        #     num_turns=4,
        #     conversation_mood="professional",
        #     language="english",
        #     voice_id1="21m00Tcm4TlvDq8ikWAM",  # Example voice ID
        #     voice_id2="AZnzlk1XvdvUeBnXmlld"   # Example voice ID
        # )
        # print_conversation_summary(schema_path)
        
    except Exception as e:
        logger.error(f"Error in example: {str(e)}")
        raise

if __name__ == "__main__":
    main()
