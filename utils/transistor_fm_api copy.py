#!/usr/bin/env python3
import os
import requests
import json
from typing import Optional, Dict, List
from dotenv import load_dotenv
from urllib.parse import urlencode

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("TRANSISTOR_FM_API_KEY")

class TransistorFMClient:
    BASE_URL = "https://api.transistor.fm/v1"

    def __init__(self):
        if not API_KEY:
            raise ValueError("TRANSISTOR_FM_API_KEY not found in environment variables")
            
        self.headers = {
            "x-api-key": API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
    def _handle_response(self, response) -> Optional[Dict]:
        """Handle API response and errors"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            print(f"Response: {response.text}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Response: {response.text}")
            return None

    def get_authenticated_user(self) -> Optional[Dict]:
        """Get details of the authenticated user"""
        response = requests.get(f"{self.BASE_URL}", headers=self.headers)
        result = self._handle_response(response)
        if result and 'data' in result:
            print("\nAuthenticated User Details:")
            print(f"Name: {result['data']['attributes'].get('name')}")
            print(f"Created At: {result['data']['attributes'].get('created_at')}")
            print(f"Time Zone: {result['data']['attributes'].get('time_zone')}")
            return result['data']
        return None

    def get_shows(self, page: int = 1, per_page: int = 10) -> Optional[List[Dict]]:
        """Get a list of shows"""
        params = {
            "pagination[page]": page,
            "pagination[per]": per_page
        }
        response = requests.get(f"{self.BASE_URL}/shows", headers=self.headers, params=params)
        result = self._handle_response(response)
        if result and 'data' in result:
            print("\nShows:")
            for show in result['data']:
                print(f"- {show['attributes'].get('title')} (ID: {show['id']})")
            return result['data']
        return None

    def get_show(self, show_id: str) -> Optional[Dict]:
        """Get details of a specific show"""
        response = requests.get(f"{self.BASE_URL}/shows/{show_id}", headers=self.headers)
        result = self._handle_response(response)
        if result and 'data' in result:
            print(f"\nShow Details (ID: {show_id}):")
            print(f"Title: {result['data']['attributes'].get('title')}")
            print(f"Description: {result['data']['attributes'].get('description')}")
            return result['data']
        return None

    def update_show(self, show_id: str, title: Optional[str] = None, description: Optional[str] = None) -> Optional[Dict]:
        """Update a show's details"""
        data = {"show": {}}
        if title:
            data["show"]["title"] = title
        if description:
            data["show"]["description"] = description
            
        response = requests.patch(f"{self.BASE_URL}/shows/{show_id}", headers=self.headers, json=data)
        result = self._handle_response(response)
        return result.get('data') if result else None

    def get_episodes(self, show_id: Optional[str] = None, page: int = 1, per_page: int = 10) -> Optional[List[Dict]]:
        """Get a list of episodes"""
        params = {
            "pagination[page]": page,
            "pagination[per]": per_page
        }
        if show_id:
            params["show_id"] = show_id
            
        response = requests.get(f"{self.BASE_URL}/episodes", headers=self.headers, params=params)
        result = self._handle_response(response)
        if result and 'data' in result:
            print("\nEpisodes:")
            for episode in result['data']:
                print(f"- {episode['attributes'].get('title')} (ID: {episode['id']})")
            return result['data']
        return None

    def create_episode(self, show_id: str, title: str, summary: str, season: Optional[int] = None, number: Optional[int] = None) -> Optional[Dict]:
        """Create a new episode"""
        # Prepare data in the same format as curl example
        data = {
            "episode[show_id]": show_id,
            "episode[title]": title,
            "episode[summary]": summary
        }
        
        if season is not None:
            data["episode[season]"] = str(season)
        if number is not None:
            data["episode[number]"] = str(number)
            
        # Convert data to URL-encoded string
        data_str = urlencode(data)
        
        # Use the same headers as curl
        headers = {
            "x-api-key": API_KEY,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/episodes",
            headers=headers,
            data=data_str
        )
        
        result = self._handle_response(response)
        if result and 'data' in result:
            print(f"\nCreated Episode:")
            print(f"Title: {result['data']['attributes'].get('title')}")
            print(f"Summary: {result['data']['attributes'].get('summary')}")
            print(f"Status: {result['data']['attributes'].get('status')}")
            print(f"Media URL: {result['data']['attributes'].get('media_url')}")
            return result['data']
        return None

    def authorize_upload(self, filename: str) -> Optional[Dict]:
        """Get an authorized URL for uploading an audio file"""
        params = {"filename": filename}
        response = requests.get(
            f"{self.BASE_URL}/episodes/authorize_upload",
            headers=self.headers,
            params=params
        )
        result = self._handle_response(response)
        if result and 'data' in result:
            print("\nAuthorized Upload:")
            print(f"Upload URL: {result['data']['attributes'].get('upload_url')}")
            print(f"Content Type: {result['data']['attributes'].get('content_type')}")
            print(f"Expires In: {result['data']['attributes'].get('expires_in')} seconds")
            return result['data']['attributes']
        return None

    def upload_audio(self, upload_url: str, file_path: str) -> bool:
        """Upload an audio file to the authorized URL"""
        try:
            with open(file_path, 'rb') as audio_file:
                headers = {"Content-Type": "audio/mpeg"}
                response = requests.put(upload_url, headers=headers, data=audio_file)
                response.raise_for_status()
                print("\nAudio Upload Successful!")
                return True
        except Exception as e:
            print(f"\nError uploading audio: {e}")
            return False

    def update_episode_audio(self, episode_id: str, audio_url: str) -> Optional[Dict]:
        """Update an episode with the audio URL"""
        data = {
            "episode[audio_url]": audio_url
        }
        response = requests.patch(
            f"{self.BASE_URL}/episodes/{episode_id}",
            headers={"x-api-key": API_KEY, "Content-Type": "application/x-www-form-urlencoded"},
            data=data
        )
        result = self._handle_response(response)
        if result and 'data' in result:
            print("\nEpisode Updated:")
            print(f"Title: {result['data']['attributes'].get('title')}")
            print(f"Audio URL: {result['data']['attributes'].get('audio_url')}")
            return result['data']
        return None

# Example Usage
if __name__ == "__main__":
    client = TransistorFMClient()
    
    # Get authenticated user details
    user = client.get_authenticated_user()
    if not user:
        print("\nFailed to authenticate. Please check your API key.")
        exit(1)
        
    # List all shows
    shows = client.get_shows()
    if not shows:
        print("\nNo shows found. Please create a show in the Transistor.fm dashboard first.")
        exit(1)

    # Create a new episode
    show_id = "61656"  # Your Test show ID
    episode = client.create_episode(
        show_id=show_id,
        title="My First Test Episode",
        summary="This is a test episode created via the API",
        season=1,
        number=1
    )
    
    if episode:
        # Get upload authorization
        audio_file = "output/indapoint/indapoint/791/final_mix.mp3"  # Replace with your audio file path
        upload_auth = client.authorize_upload(os.path.basename(audio_file))
        
        if upload_auth:
            # Upload the audio file
            if client.upload_audio(upload_auth['upload_url'], audio_file):
                # Update episode with the audio URL
                client.update_episode_audio(episode['id'], upload_auth['audio_url'])
        
        # List all episodes
        episodes = client.get_episodes(show_id)
