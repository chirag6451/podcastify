"""Script to create or update section configurations."""
from profile_utils import ProfileUtils
import json

def create_intro_section(profile_name: str):
    utils = ProfileUtils()
    
    # Custom intro configuration
    intro_config = {
        "duration": 15,
        "background_music": "video_creator/defaults/bgmusic/intro.mp3",
        "title_animation": "slide_fade",
        "show_logo": True,
        "transition_effect": "fade",
        "overlay_text": "Welcome to our podcast!",
        "custom_settings": {
            "font_size": 40,
            "font_color": "#FFFFFF",
            "background_opacity": 0.8
        }
    }
    
    # Save the configuration
    utils.set_section_config(profile_name, "intro", intro_config)
    
    # Verify the saved configuration (this will include global settings)
    saved_config = utils.get_section_config(profile_name, "intro")
    print("\nSaved Intro Configuration:")
    print(json.dumps(saved_config, indent=2))

def create_custom_section(profile_name: str, section_name: str, config: dict):
    utils = ProfileUtils()
    
    # Register the new section type if it's custom
    utils.register_section(section_name)
    
    # Save the configuration
    utils.set_section_config(profile_name, section_name, config)
    
    # Verify the saved configuration (this will include global settings)
    saved_config = utils.get_section_config(profile_name, section_name)
    print(f"\nSaved {section_name} Configuration:")
    print(json.dumps(saved_config, indent=2))

if __name__ == "__main__":
    # Example 1: Create intro section
    create_intro_section("indapoint")
    
    # Example 2: Create a custom highlights section
    highlights_config = {
        "duration": 30,
        "max_clips": 5,
        "transition": "fast_fade",
        "background_music": "video_creator/defaults/bgmusic/upbeat.mp3",
        "text_overlay": {
            "position": "bottom",
            "font_size": 24,
            "font_color": "#FFD700"
        },
        "effects": {
            "zoom": True,
            "speed": 1.5,
            "highlight_color": "#FF4500"
        }
    }
    create_custom_section("indapoint", "highlights", highlights_config)
    
    # Example 3: Create a custom sponsor section
    sponsor_config = {
        "duration": 20,
        "position": "mid_roll",
        "transition": "smooth_fade",
        "background": "blur",
        "logo_display": {
            "size": [200, 100],
            "position": "center",
            "animation": "fade_in"
        }
    }
    create_custom_section("indapoint", "sponsor", sponsor_config)
