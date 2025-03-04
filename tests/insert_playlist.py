import requests
import json

# Configuration
BASE_URL = "http://0.0.0.0:8011/api/publish"  # Updated to match your server
API_KEY = "indapoint2025"
USER_EMAIL = "info@indapoint.com"
CHANNEL_ID = "UCjsp-HaZASVdOq48PwMDTxg"  # Updated with correct channel ID
PLAYLIST_ID = "PLv8bszWmOt2PqiWc7y5kcpyUR84Wyy7YU"

def test_save_channel():
    """Test saving a YouTube channel"""
    url = f"{BASE_URL}/youtube/channels/{CHANNEL_ID}/save"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    params = {
        "user_email": USER_EMAIL
    }
    
    response = requests.post(url, headers=headers, params=params)
    print("\nTest Save Channel:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code != 204 else 'Success'}")
    return response.status_code in [200, 201, 204]

def test_save_playlist():
    """Test saving a YouTube playlist"""
    url = f"{BASE_URL}/youtube/playlists/{PLAYLIST_ID}/save"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    params = {
        "user_email": USER_EMAIL,
        "channel_id": CHANNEL_ID
    }
    
    response = requests.post(url, headers=headers, params=params)
    print("\nTest Save Playlist:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code != 204 else 'Success'}")
    return response.status_code in [200, 201, 204]

def main():
    print("Starting YouTube Playlist Tests...")
    
    # First save the channel
    if test_save_channel():
        print("\n✅ Channel saved successfully")
    else:
        print("\n❌ Failed to save channel")
        return
    
    # Then save the playlist
    if test_save_playlist():
        print("\n✅ Playlist saved successfully")
    else:
        print("\n❌ Failed to save playlist")

if __name__ == "__main__":
    main()