#!/usr/bin/env python3

from utils.profile_manager import ProfileManager
from utils.logger_utils import PodcastLogger
import json
import argparse

logger = PodcastLogger("profile_manager")

def list_profiles():
    """List all available profiles"""
    pm = ProfileManager()
    profiles = pm.list_profiles()
    logger.info("Available profiles:")
    for profile in profiles:
        logger.info(f"- {profile}")

def view_profile(profile_name: str):
    """View details of a specific profile"""
    pm = ProfileManager()
    profile = pm.get_profile(profile_name)
    if profile:
        logger.info(f"\nProfile: {profile.profile_name}")
        logger.info("\nVoice Settings:")
        for k, v in profile.voice_settings.items():
            logger.info(f"  {k}: {v}")
        logger.info("\nVideo Settings:")
        for k, v in profile.video_settings.items():
            logger.info(f"  {k}: {v}")
        logger.info("\nBusiness Info:")
        for k, v in profile.business_info.items():
            logger.info(f"  {k}: {v}")
        logger.info("\nDefault Settings:")
        for k, v in profile.default_settings.items():
            logger.info(f"  {k}: {v}")
    else:
        logger.error(f"Profile {profile_name} not found")

def create_new_profile(profile_name: str, input_file: str):
    """Create a new profile from JSON file"""
    try:
        with open(input_file, 'r') as f:
            profile_data = json.load(f)
        
        pm = ProfileManager()
        pm.create_profile(profile_name, profile_data)
        logger.success(f"Created profile: {profile_name}")
    except Exception as e:
        logger.error(f"Error creating profile: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Manage podcast profiles')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # List profiles command
    subparsers.add_parser('list', help='List all profiles')
    
    # View profile command
    view_parser = subparsers.add_parser('view', help='View profile details')
    view_parser.add_argument('profile_name', help='Name of the profile to view')
    
    # Create profile command
    create_parser = subparsers.add_parser('create', help='Create a new profile')
    create_parser.add_argument('profile_name', help='Name for the new profile')
    create_parser.add_argument('input_file', help='JSON file containing profile data')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_profiles()
    elif args.command == 'view':
        view_profile(args.profile_name)
    elif args.command == 'create':
        create_new_profile(args.profile_name, args.input_file)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
