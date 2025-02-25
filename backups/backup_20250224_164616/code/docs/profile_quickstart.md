# Profile Management Quick Start Guide

## Common Tasks

### 1. Get Profile Configuration
```python
from profile_utils import ProfileUtils

utils = ProfileUtils()

# Get complete profile
config = utils.get_profile_config("indapoint")

# Get specific sections
video_config = utils.get_video_settings("indapoint")
voice_config = utils.get_voice_settings("indapoint")
business_info = utils.get_business_info("indapoint")
```

### 2. Create New Section
```python
from profile_utils import ProfileUtils

utils = ProfileUtils()

# Using template
intro_template = utils.create_section_template("intro")
utils.set_section_config("indapoint", "intro", intro_template)

# Custom section
utils.register_section("my_section")
my_config = {
    "duration": 30,
    "custom_setting": "value"
}
utils.set_section_config("indapoint", "my_section", my_config)
```

### 3. Update Settings
```python
from profile_utils import ProfileUtils

utils = ProfileUtils()

# Update specific fields
utils.update_section_config("indapoint", "video", {
    "resolution": [1920, 1080],
    "bg_music_volume": 0.2
})
```

### 4. Create New Profile
```python
from profile_utils import ProfileUtils

utils = ProfileUtils()

# Set global config
global_config = {
    "profile_name": "New Tenant",
    "business_info": {
        "name": "Business Name",
        "website": "www.example.com"
    }
}
utils.set_section_config("new_tenant", "global", global_config)

# Add standard sections
video_config = utils.create_section_template("video")
utils.set_section_config("new_tenant", "video", video_config)

audio_config = utils.create_section_template("audio")
utils.set_section_config("new_tenant", "audio", audio_config)
```

### 5. Get Available Profiles
```python
from profile_utils import ProfileUtils

utils = ProfileUtils()

# List all profiles
profiles = utils.get_available_profiles()
print(f"Available profiles: {profiles}")
```

## Template Examples

### Intro Section Template
```python
intro_config = {
    "duration": 10,
    "background_music": "path/to/intro.mp3",
    "title_animation": "fade",
    "show_logo": True
}
```

### Outro Section Template
```python
outro_config = {
    "duration": 15,
    "show_credits": True,
    "call_to_action": "Subscribe for more!",
    "social_links": True
}
```

### Custom Section Template
```python
custom_config = {
    "duration": 20,
    "position": "mid_roll",
    "transition": "smooth_fade",
    "custom_settings": {
        "setting1": "value1",
        "setting2": "value2"
    }
}
```

## Quick Tips

1. Always use `ProfileUtils` instead of direct file access
2. Register new section types before using them
3. Use templates for standard sections when available
4. Check returned configurations for required fields
5. Remember that section configs inherit from global config
