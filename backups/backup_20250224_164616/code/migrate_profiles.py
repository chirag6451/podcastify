"""Script to migrate existing profile JSON to new modular structure."""
import json
import os
from pathlib import Path
from profile_manager import ProfileManager

def migrate_profile(profile_path: str, profile_name: str):
    """Migrate a single profile JSON to the new structure.
    
    Args:
        profile_path: Path to the existing profile JSON
        profile_name: Name of the profile (e.g., 'indapoint')
    """
    # Read existing profile
    with open(profile_path, 'r') as f:
        existing_config = json.load(f)
    
    # Initialize new structure
    sections = {
        'global': {
            'profile_name': existing_config.get('profile_name', ''),
            'business_info': existing_config.get('business_info', {}),
            'default_settings': existing_config.get('default_settings', {})
        },
        'audio': {
            'voice_settings': existing_config.get('voice_settings', {})
        },
        'video': {
            'video_settings': {
                **existing_config.get('video_settings', {}),
                'speaker1_video_path': os.path.join('video_creator/defaults/speakers', 'g1.mp4'),
                'speaker2_video_path': os.path.join('video_creator/defaults/speakers', 'm1.mp4')
            }
        },
        'intro': {},
        'short_video': {},
        'main_video': {},
        'outro': {}
    }
    
    # Initialize profile manager
    profile_manager = ProfileManager()
    
    # Create profile directory
    profile_dir = os.path.join('profiles', profile_name)
    os.makedirs(profile_dir, exist_ok=True)
    
    # Save each section
    for section_name, config in sections.items():
        if config:  # Only save non-empty sections
            profile_manager.save_section(profile_name, section_name, config)
    
    # Create backup of original file
    backup_path = profile_path + '.backup'
    with open(backup_path, 'w') as f:
        json.dump(existing_config, f, indent=4)
    
    print(f"Migration completed for profile: {profile_name}")
    print(f"Original profile backed up to: {backup_path}")
    print(f"New profile sections created in: {profile_dir}/")

def main():
    """Main migration function."""
    profiles_dir = 'profiles'
    
    # Find all JSON files in profiles directory
    for file in os.listdir(profiles_dir):
        if file.endswith('.json'):
            profile_path = os.path.join(profiles_dir, file)
            profile_name = file.replace('.json', '')
            
            print(f"\nMigrating profile: {profile_name}")
            migrate_profile(profile_path, profile_name)

if __name__ == '__main__':
    main()
