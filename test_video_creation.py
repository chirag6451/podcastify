#!/usr/bin/env python3

import os
import json
from test_tasks import generate_audio_task_test, create_video_task_test

def load_profile(profile_name="indapoint"):
    """Load profile configuration"""
    profile_path = os.path.join("profiles", f"{profile_name}.json")
    with open(profile_path) as f:
        return json.load(f)

def test_video_creation(
    topic="The Impact of AI on Healthcare",
    num_turns=2,
    conversation_type="explaining in simple terms"
):
    """Test video creation with hardcoded parameters"""
    
    # Load profile
    profile = load_profile()
    
    #let us add topic, num_turns, conversation_type to profile
    profile["topic"] = topic
    profile["num_turns"] = num_turns
    profile["conversation_type"] = conversation_type

    
    # Create a test job ID
    job_id = "test_job_001"
    
    
    try:
        print("Starting audio generation...")
        # Generate audio
        audio_path = generate_audio_task_test(
            config=profile,
            job_id=job_id
        )
        print(f"Audio generated at: {audio_path}")
        
        print("\nStarting video generation...")
        # Create video
        video_path = create_video_task_test(
            job_id=job_id,
            config=profile
        )
        print(f"Video created at: {video_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    print("Testing video creation pipeline...")
    test_video_creation() 