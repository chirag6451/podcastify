from indapoint_podcast import generate_conversation

def main():
    # Example business info
    business_info = {
        "name": "TechCorp",
        "industry": "Technology",
        "description": "A leading technology company"
    }

    # Generate a conversation
    audio_path, schema_path = generate_conversation(
        topic="The future of artificial intelligence",
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
    
    print(f"Generated audio file: {audio_path}")
    print(f"Generated schema file: {schema_path}")

if __name__ == "__main__":
    main()
