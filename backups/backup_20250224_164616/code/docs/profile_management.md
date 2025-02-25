# Profile Management System Documentation

## Overview
The Profile Management System provides a modular and extensible way to manage configuration profiles for different tenants. Each profile is split into sections (like global, audio, video, intro, etc.) that can be managed independently while maintaining the ability to inherit and override settings.

## Directory Structure
```
profiles/
  ├── indapoint/              # Tenant profile directory
  │   ├── global.json         # Global settings
  │   ├── audio.json         # Audio settings
  │   ├── video.json         # Video settings
  │   ├── intro.json         # Intro section settings
  │   ├── outro.json         # Outro section settings
  │   └── custom_section.json # Custom section settings
  └── another_tenant/         # Another tenant profile
      └── ...
```

## Core Components

### 1. ProfileManager
Low-level class that handles file operations and section management.

```python
from profile_manager import ProfileManager

# Initialize
manager = ProfileManager(profiles_dir="profiles")

# Register new section types
manager.register_section("my_custom_section")

# Save section configuration
manager.save_section("tenant_name", "section_name", config_dict)
```

### 2. ProfileUtils
High-level utility class that provides convenient methods for profile management.

```python
from profile_utils import ProfileUtils

# Initialize
utils = ProfileUtils()

# Get complete profile configuration
config = utils.get_profile_config("indapoint")

# Get specific section configuration
video_config = utils.get_video_settings("indapoint")
intro_config = utils.get_section_config("indapoint", "intro")
```

## Section Types

### 1. Global Section (global.json)
Contains default settings that apply across all sections.
```json
{
    "profile_name": "Tenant Name",
    "business_info": {
        "name": "Business Name",
        "website": "www.example.com"
    },
    "default_settings": {
        "num_turns": 5,
        "conversation_mood": "professional"
    }
}
```

### 2. Audio Section (audio.json)
Contains voice and audio-related settings.
```json
{
    "voice_settings": {
        "welcome_voice_id": "voice_id",
        "voice_id1": "speaker1_id",
        "voice_id2": "speaker2_id",
        "language": "English"
    }
}
```

### 3. Video Section (video.json)
Contains video-related settings.
```json
{
    "video_settings": {
        "resolution": [1920, 1080],
        "bg_music_volume": 0.1,
        "speaker1_video_path": "path/to/video1",
        "speaker2_video_path": "path/to/video2"
    }
}
```

## Creating New Sections

### Method 1: Using Templates
```python
from profile_utils import ProfileUtils

utils = ProfileUtils()

# Get template for a section
template = utils.create_section_template("intro")

# Save the template
utils.set_section_config("tenant_name", "intro", template)
```

### Method 2: Custom Configuration
```python
from profile_utils import ProfileUtils

utils = ProfileUtils()

# Register new section type
utils.register_section("custom_section")

# Create and save configuration
config = {
    "duration": 30,
    "custom_setting": "value"
}
utils.set_section_config("tenant_name", "custom_section", config)
```

### Method 3: Using Helper Script
```python
from create_section import create_custom_section

config = {
    "duration": 25,
    "effect": "fade"
}
create_custom_section("tenant_name", "section_name", config)
```

## Configuration Inheritance
1. All sections automatically inherit settings from `global.json`
2. Section-specific settings override global settings
3. The merge is deep, so nested dictionaries are properly combined

Example:
```python
# Global settings
global_config = {
    "business_info": {"name": "Company"},
    "default_font": "Arial"
}

# Section settings
section_config = {
    "default_font": "Helvetica"  # This overrides global
}

# Final merged config will be:
{
    "business_info": {"name": "Company"},
    "default_font": "Helvetica"
}
```

## Best Practices

1. **Section Organization**
   - Keep related settings together in appropriate sections
   - Use global.json for truly global settings
   - Create new sections for distinct features

2. **Configuration Management**
   - Always use ProfileUtils methods instead of direct file access
   - Register new section types before using them
   - Use templates for standard sections
   - Document custom section structures

3. **Error Handling**
   - All ProfileUtils methods handle missing files gracefully
   - Always check returned configurations for required fields
   - Use try-except blocks when working with configurations

## Common Tasks

### Adding a New Tenant
```python
from profile_utils import ProfileUtils

utils = ProfileUtils()

# Create global config
global_config = {
    "profile_name": "New Tenant",
    "business_info": {...}
}
utils.set_section_config("new_tenant", "global", global_config)

# Add required sections
utils.set_section_config("new_tenant", "audio", audio_config)
utils.set_section_config("new_tenant", "video", video_config)
```

### Updating Specific Settings
```python
from profile_utils import ProfileUtils

utils = ProfileUtils()

# Update specific fields
utils.update_section_config("tenant_name", "video", {
    "resolution": [1280, 720]
})
```

### Getting Available Profiles
```python
from profile_utils import ProfileUtils

utils = ProfileUtils()

# List all profiles
profiles = utils.get_available_profiles()
```

## Troubleshooting

1. **Missing Configuration**
   - Check if the profile directory exists
   - Verify section JSON files are present
   - Ensure section type is registered

2. **Invalid Configuration**
   - Validate JSON syntax
   - Check for required fields
   - Verify file permissions

3. **Inheritance Issues**
   - Check global.json exists and is valid
   - Verify section configuration structure
   - Debug using get_section_config() to see merged result
