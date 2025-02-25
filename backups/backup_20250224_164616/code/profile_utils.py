"""Utility functions for working with profile configurations."""
from typing import Optional, Dict, Any, List
from profile_manager import ProfileManager
import os
import json
from config import OUTPUTS_DIR
from utils.path_validator import validate_and_fix_paths
import logging
from datetime import datetime

__all__ = ['ProfileUtils', 'get_merged_config']

logger = logging.getLogger(__name__)

class ProfileUtils:
    def __init__(self, profiles_dir: str = "profiles"):
        """Initialize the profile utilities.
        
        Args:
            profiles_dir: Base directory containing all profile configurations
        """
        self.profile_manager = ProfileManager(profiles_dir)
        
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """Flatten nested dictionary by concatenating nested keys."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
        
    def merge_all_to_global(self, profile_name: str) -> Dict[str, Any]:
        """Merge all unique keys from all JSON files into global.json.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            Dict containing merged configuration
        """
        # Get all config files
        profile_dir = os.path.join(self.profile_manager.profiles_dir, profile_name)
        global_path = os.path.join(profile_dir, "global.json")
        
        # Load current global config
        global_config = {}
        if os.path.exists(global_path):
            try:
                with open(global_path, 'r') as f:
                    global_config = json.load(f)
            except json.JSONDecodeError:
                # If global.json is invalid, start with empty dict
                global_config = {}
        
        # Load and merge all JSON files
        for section in self.profile_manager.section_names:
            section_path = os.path.join(profile_dir, f"{section}.json")
            if not os.path.exists(section_path):
                continue
                
            try:
                with open(section_path, 'r') as f:
                    section_config = json.load(f)
                    
                # If it's video config, handle video_settings
                if section == "video" and "video_settings" in section_config:
                    video_settings = section_config.pop("video_settings", {})
                    # Flatten all nested settings with their original keys
                    flattened_video = {}
                    for key, value in video_settings.items():
                        if isinstance(value, dict):
                            # For nested dicts like footer_settings, flatten with prefix
                            for sub_key, sub_value in value.items():
                                flattened_video[f"{key}_{sub_key}"] = sub_value
                        else:
                            # For direct values like title_font_size
                            flattened_video[key] = value
                    section_config.update(flattened_video)
                
                # Merge flattened section config
                flattened = self._flatten_dict(section_config)
                global_config.update(flattened)
            except json.JSONDecodeError:
                print(f"Warning: Invalid JSON in {section_path}")
                continue
        
        return global_config
    
    def get_merged_config(self, profile_name: str, section: Optional[str] = None, theme: str = "default") -> Dict[str, Any]:
        """Get merged configuration for a profile, optionally with section-specific overrides.
        
        Args:
            profile_name: Name of the profile
            section: Optional section name to get section-specific overrides
            theme: Theme name to use (defaults to "default")
            
        Returns:
            Merged configuration dictionary
        """
        # First merge all configs to global
        global_config = self.merge_all_to_global(profile_name)
        
        if section:
            # If section is specified, get section-specific config
            section_path = os.path.join(self.profile_manager.profiles_dir, profile_name, f"{section}.json")
            if os.path.exists(section_path):
                try:
                    with open(section_path, 'r') as f:
                        section_config = json.load(f)
                    
                    # If it's video config, handle video_settings
                    if section == "video" and "video_settings" in section_config:
                        video_settings = section_config.pop("video_settings", {})
                        # Flatten all nested settings with their original keys
                        flattened_video = {}
                        for key, value in video_settings.items():
                            if isinstance(value, dict):
                                # For nested dicts like footer_settings, flatten with prefix
                                for sub_key, sub_value in value.items():
                                    flattened_video[f"{key}_{sub_key}"] = sub_value
                            else:
                                # For direct values like title_font_size
                                flattened_video[key] = value
                        section_config.update(flattened_video)
                    
                    # Override global config with section-specific settings
                    global_config.update(self._flatten_dict(section_config))
                except json.JSONDecodeError:
                    print(f"Warning: Invalid JSON in {section_path}")
        
        return global_config
    
    def get_profile_config(self, profile_name: str, theme: str = "default") -> Dict[str, Any]:
        """Get the complete configuration for a profile.
        
        Args:
            profile_name: Name of the profile (e.g., 'indapoint')
            theme: Theme name to use (defaults to "default")
            
        Returns:
            Complete merged configuration dictionary
        """
        # Get merged config with video section and theme
        return self.get_merged_config(profile_name, section="video", theme=theme)
    
    def get_voice_settings(self, profile_name: str) -> Dict[str, Any]:
        """Get voice settings for a profile.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            Voice settings dictionary
        """
        audio_config = self.profile_manager.get_config(profile_name, "audio")
        return audio_config.get("voice_settings", {})
    
    def get_video_settings(self, profile_name: str) -> Dict[str, Any]:
        """Get video settings for a profile.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            Video settings dictionary
        """
        video_config = self.profile_manager.get_config(profile_name, "video")
        return video_config.get("video_settings", {})
    
    def get_business_info(self, profile_name: str) -> Dict[str, Any]:
        """Get business information for a profile.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            Business info dictionary
        """
        global_config = self.profile_manager.get_config(profile_name, "global")
        return global_config.get("business_info", {})
    
    def get_default_settings(self, profile_name: str) -> Dict[str, Any]:
        """Get default settings for a profile.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            Default settings dictionary
        """
        global_config = self.profile_manager.get_config(profile_name, "global")
        return global_config.get("default_settings", {})
    
    def get_speaker_paths(self, profile_name: str) -> Dict[str, str]:
        """Get speaker video paths for a profile.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            Dictionary containing speaker1 and speaker2 video paths
        """
        video_settings = self.get_video_settings(profile_name)
        return {
            "speaker1_video_path": video_settings.get("speaker1_video_path"),
            "speaker2_video_path": video_settings.get("speaker2_video_path")
        }
    
    def get_logo_settings(self, profile_name: str) -> Dict[str, Any]:
        """Get logo settings for a profile.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            Logo settings dictionary
        """
        video_settings = self.get_video_settings(profile_name)
        return video_settings.get("logo_settings", {})
    
    def get_footer_settings(self, profile_name: str) -> Dict[str, Any]:
        """Get footer settings for a profile.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            Footer settings dictionary
        """
        video_settings = self.get_video_settings(profile_name)
        return video_settings.get("footer_settings", {})
    
    def get_available_profiles(self) -> List[str]:
        """Get list of available profile names.
        
        Returns:
            List of profile names
        """
        profiles = []
        for item in os.listdir(self.profile_manager.profiles_dir):
            if os.path.isdir(os.path.join(self.profile_manager.profiles_dir, item)):
                profiles.append(item)
        return profiles
    
    def create_customer_output_dir(self, profile_name: str, customer_id: str) -> str:
        """Create and return a unique output directory for a customer.
        
        Args:
            profile_name: Name of the profile
            customer_id: Unique identifier for the customer
            
        Returns:
            Path to the created output directory
        """
        # Create timestamp in format YYYYMMDD_HHMMSS
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create path: profiles/<profile_name>/output/<customer_id>/<timestamp>
        output_dir = os.path.join(
            self.profile_manager.profiles_dir,
            profile_name,
            "output",
            customer_id,
            timestamp
        )
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        return output_dir
    
# Example usage:
if __name__ == "__main__":
    # Initialize utils
    utils = ProfileUtils()
    
    # Example: Get all available profiles
    profiles = utils.get_available_profiles()
    print(f"Available profiles: {profiles}")
    
    # Example: Get complete config for indapoint
    profile_name = "indapoint"
    if profile_name in profiles:
        # Get voice settings
        voice_settings = utils.get_voice_settings(profile_name)
        print(f"\nVoice Settings for {profile_name}:")
        print(voice_settings)
        
        # Get video settings
        video_settings = utils.get_video_settings(profile_name)
        print(f"\nVideo Settings for {profile_name}:")
        print(video_settings)
        
        # Get speaker paths
        speaker_paths = utils.get_speaker_paths(profile_name)
        print(f"\nSpeaker Paths for {profile_name}:")
        print(speaker_paths)
