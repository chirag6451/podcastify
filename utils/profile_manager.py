"""Profile manager for podcast configurations"""

import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from utils.logger_utils import PodcastLogger

logger = PodcastLogger("profile_manager")

@dataclass
class Profile:
    """Profile configuration for podcast generation"""
    profile_name: str
    voice_settings: Dict[str, Any]
    video_settings: Dict[str, Any]
    business_info: Dict[str, Any]
    default_settings: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Profile':
        """Create a Profile instance from a dictionary"""
        return cls(
            profile_name=data['profile_name'],
            voice_settings=data['voice_settings'],
            video_settings=data['video_settings'],
            business_info=data['business_info'],
            default_settings=data['default_settings']
        )

class ProfileManager:
    """Manages podcast configuration profiles"""
    
    def __init__(self, profiles_dir: str = "profiles"):
        self.profiles_dir = profiles_dir
        self._profiles: Dict[str, Profile] = {}
        self._load_profiles()
    
    def _load_profiles(self) -> None:
        """Load all profile configurations from the profiles directory"""
        if not os.path.exists(self.profiles_dir):
            logger.warning(f"Profiles directory {self.profiles_dir} does not exist")
            return
            
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith('.json'):
                profile_path = os.path.join(self.profiles_dir, filename)
                try:
                    with open(profile_path, 'r') as f:
                        profile_data = json.load(f)
                        profile_name = os.path.splitext(filename)[0]
                        self._profiles[profile_name] = Profile.from_dict(profile_data)
                        logger.info(f"Loaded profile: {profile_name}")
                except Exception as e:
                    logger.error(f"Error loading profile {filename}: {str(e)}")
    
    def get_profile(self, profile_name: str) -> Optional[Profile]:
        """Get a profile by name"""
        return self._profiles.get(profile_name)
    
    def list_profiles(self) -> List[str]:
        """List all available profile names"""
        return list(self._profiles.keys())
    
    def create_profile(self, profile_name: str, profile_data: Dict[str, Any]) -> Profile:
        """Create a new profile"""
        if not profile_name.isalnum():
            raise ValueError("Profile name must be alphanumeric")
            
        profile_path = os.path.join(self.profiles_dir, f"{profile_name}.json")
        if os.path.exists(profile_path):
            raise ValueError(f"Profile {profile_name} already exists")
            
        try:
            profile = Profile.from_dict(profile_data)
            with open(profile_path, 'w') as f:
                json.dump(profile_data, f, indent=4)
            self._profiles[profile_name] = profile
            logger.success(f"Created profile: {profile_name}")
            return profile
        except Exception as e:
            logger.error(f"Error creating profile {profile_name}: {str(e)}")
            raise
    
    def update_profile(self, profile_name: str, profile_data: Dict[str, Any]) -> Profile:
        """Update an existing profile"""
        profile_path = os.path.join(self.profiles_dir, f"{profile_name}.json")
        if not os.path.exists(profile_path):
            raise ValueError(f"Profile {profile_name} does not exist")
            
        try:
            profile = Profile.from_dict(profile_data)
            with open(profile_path, 'w') as f:
                json.dump(profile_data, f, indent=4)
            self._profiles[profile_name] = profile
            logger.success(f"Updated profile: {profile_name}")
            return profile
        except Exception as e:
            logger.error(f"Error updating profile {profile_name}: {str(e)}")
            raise
    
    def delete_profile(self, profile_name: str) -> None:
        """Delete a profile"""
        profile_path = os.path.join(self.profiles_dir, f"{profile_name}.json")
        if not os.path.exists(profile_path):
            raise ValueError(f"Profile {profile_name} does not exist")
            
        try:
            os.remove(profile_path)
            del self._profiles[profile_name]
            logger.success(f"Deleted profile: {profile_name}")
        except Exception as e:
            logger.error(f"Error deleting profile {profile_name}: {str(e)}")
            raise
