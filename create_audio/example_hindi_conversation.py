"""Example script demonstrating Hindi conversation generation."""
from conversation_generator import generate_conversation, print_conversation_summary
from logger_utils import PodcastLogger

# Initialize logger
logger = PodcastLogger("HindiConversationExample")

def main():
    """Generate example Hindi conversations with different topics and moods."""
    try:
        # Example 1: Casual conversation about family traditions
        # logger.section("Example 1: Family Traditions Discussion (Hindi)")
        # audio_path, schema_path = generate_conversation(
        #     topic="भारतीय परिवार की परंपराएं और आधुनिक समय",  # Indian family traditions in modern times
        #     num_turns=6,
        #     conversation_mood="casual",
        #     language="hindi"
        # )
        # print_conversation_summary(schema_path)
        
        # Example 2: Storytelling about Indian mythology
        logger.section("\nExample 2: Mythological Storytelling (Hindi)")
        audio_path, schema_path = generate_conversation(
            topic="Bhagwat Geeta and Gandhi",  # Stories from Mahabharata and their relevance
            num_turns=8,
            conversation_mood="storytelling",
            language="hindi"
        )
        print_conversation_summary(schema_path)
        exit()
        
        # # Example 3: Discussion about Indian cuisine
        # logger.section("\nExample 3: Cooking Discussion (Hindi)")
        # audio_path, schema_path = generate_conversation(
        #     topic="भारतीय व्यंजनों की विविधता और पाक कला",  # Diversity of Indian cuisine and cooking
        #     num_turns=6,
        #     conversation_mood="enthusiastic",
        #     language="hindi"
        # )
        # print_conversation_summary(schema_path)
        
    except Exception as e:
        logger.error(f"Error in example: {str(e)}")
        raise

if __name__ == "__main__":
    main()
