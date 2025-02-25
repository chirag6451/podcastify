"""Profile manager for handling multi-tenant configuration with modular sections."""
import os
import json
from typing import Optional, Dict, Any
from pathlib import Path

class ProfileManager:
    def __init__(self, profiles_dir: str = "profiles"):
        """Initialize the profile manager.
        
        Args:
            profiles_dir: Base directory containing all profile configurations
        """
        self.profiles_dir = profiles_dir
        self.section_names = [
            "global",
            "audio",
            "video",
            "intro",
            "short_video",
            "main_video",
            "outro"
        ]

    def _get_section_path(self, profile_name: str, section: str) -> str:
        """Get the path for a specific section's JSON file.
        
        Args:
            profile_name: Name of the profile (e.g., 'indapoint')
            section: Name of the section (e.g., 'global', 'audio', etc.)
        """
        return os.path.join(self.profiles_dir, profile_name, f"{section}.json")

    def _load_json(self, file_path: str) -> Dict[str, Any]:
        """Load and parse a JSON file.
        
        Args:
            file_path: Path to the JSON file
        Returns:
            Dict containing the JSON data or empty dict if file doesn't exist
        """
        if not os.path.exists(file_path):
            return {}
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in {file_path}")
            return {}
        except Exception as e:
            print(f"Error reading {file_path}: {str(e)}")
            return {}

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries, with override taking precedence.
        
        Args:
            base: Base dictionary
            override: Dictionary with override values
        Returns:
            Merged dictionary
        """
        merged = base.copy()
        
        for key, value in override.items():
            if (
                key in merged and 
                isinstance(merged[key], dict) and 
                isinstance(value, dict)
            ):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = value
                
        return merged

    def get_config(self, profile_name: str, section: Optional[str] = None) -> Dict[str, Any]:
        """Get the configuration for a profile, optionally filtered by section.
        
        Args:
            profile_name: Name of the profile (e.g., 'indapoint')
            section: Optional section name to return only that section's config
        
        Returns:
            Dict containing the merged configuration
        """
        # Always load global settings first
        global_config = self._load_json(self._get_section_path(profile_name, "global"))
        
        if section:
            # If specific section requested, merge global with just that section
            if section == "global":
                return global_config
            
            section_config = self._load_json(self._get_section_path(profile_name, section))
            return self._deep_merge(global_config, section_config)
        
        # Merge all sections
        final_config = global_config
        for section_name in self.section_names[1:]:  # Skip global as we already loaded it
            section_config = self._load_json(self._get_section_path(profile_name, section_name))
            if section_name == "video" and "video_settings" in section_config:
                # Flatten video_settings to root level
                video_settings = section_config.pop("video_settings", {})
                final_config = self._deep_merge(final_config, video_settings)
            final_config = self._deep_merge(final_config, section_config)
            
        return final_config

    def save_section(self, profile_name: str, section: str, config: Dict[str, Any]) -> None:
        """Save configuration for a specific section.
        
        Args:
            profile_name: Name of the profile
            section: Name of the section
            config: Configuration dictionary to save
        """
        if section not in self.section_names:
            raise ValueError(f"Invalid section name. Must be one of: {', '.join(self.section_names)}")
        
        # Ensure profile directory exists
        profile_dir = os.path.join(self.profiles_dir, profile_name)
        os.makedirs(profile_dir, exist_ok=True)
        
        # Save the configuration
        file_path = self._get_section_path(profile_name, section)
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=4)
