import os
import sys
import importlib.util
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.profiles_dir = os.path.join(self.base_dir, "profiles")
        self.current_profile = None
        self.config = None

    def _get_profile_path(self, profile_name: str) -> str:
        """Get the absolute path to a profile directory"""
        return os.path.join(self.profiles_dir, profile_name)

    def _get_config_path(self, profile_name: str) -> str:
        """Get the absolute path to a profile's config.py file"""
        return os.path.join(self._get_profile_path(profile_name), "config.py")

    def _load_config_module(self, profile_name: str) -> Optional[Any]:
        """Load a profile's config.py as a module"""
        config_path = self._get_config_path(profile_name)
        if not os.path.exists(config_path):
            logger.error(f"Config file not found: {config_path}")
            return None

        try:
            spec = importlib.util.spec_from_file_location("config", config_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {str(e)}")
            return None

    def list_profiles(self) -> list:
        """List all available profiles"""
        if not os.path.exists(self.profiles_dir):
            return []
        return [d for d in os.listdir(self.profiles_dir) 
                if os.path.isdir(os.path.join(self.profiles_dir, d))]

    def load_profile(self, profile_name: str = "default") -> bool:
        """Load a profile's configuration"""
        if not os.path.exists(self._get_profile_path(profile_name)):
            logger.error(f"Profile not found: {profile_name}")
            if profile_name != "default":
                logger.info("Falling back to default profile")
                return self.load_profile("default")
            return False

        config = self._load_config_module(profile_name)
        if config is None:
            if profile_name != "default":
                logger.info("Falling back to default profile")
                return self.load_profile("default")
            return False

        self.current_profile = profile_name
        self.config = config
        logger.info(f"Loaded profile: {profile_name}")
        return True

    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration as a dictionary"""
        if self.config is None:
            self.load_profile("default")
        
        if self.config is None:
            raise ValueError("No configuration loaded and default profile not available")

        return {name: getattr(self.config, name) 
                for name in dir(self.config) 
                if not name.startswith('_')}

    def get_profile_path(self, subpath: str = "") -> str:
        """Get the absolute path to a file/directory within the current profile"""
        if self.current_profile is None:
            self.load_profile("default")
        
        if self.current_profile is None:
            raise ValueError("No profile loaded and default profile not available")
            
        path = self._get_profile_path(self.current_profile)
        if subpath:
            path = os.path.join(path, subpath)
        return path

    def resolve_path(self, path: str) -> str:
        """Resolve a path relative to the current profile directory"""
        if os.path.isabs(path):
            return path
            
        # Get the current profile path
        profile_path = self.get_profile_path()
        
        # If path starts with "profiles/", remove it to avoid duplication
        if path.startswith("profiles/"):
            path = path[len("profiles/"):]
            path = path[path.find("/")+1:]  # Remove profile name as well
            
        return os.path.join(profile_path, path)

# Create a global instance
config_manager = ConfigManager()
