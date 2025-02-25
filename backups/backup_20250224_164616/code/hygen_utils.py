import requests
import os
import time
from dotenv import load_dotenv
import json

load_dotenv()

# ID: Judith_expressive_2024120201
# ID: Leszek_standing_outdoorbusiness_front
# bg image asset id f978e4db1f2743d3a4001c0b3e6b6bb7

class HeyGenAPI:
    def __init__(self):
        self.api_key = os.getenv("HEYGEN_API_KEY")
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        self.base_url_v1 = "https://api.heygen.com/v1"
        self.base_url_v2 = "https://api.heygen.com/v2"
        self.upload_url = "https://upload.heygen.com/v1"

    def list_avatars(self):
        """Fetch the list of available avatars."""
        url = f"{self.base_url_v2}/avatars"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def list_voices(self):
        """Fetch the list of available voices."""
        url = f"{self.base_url_v1}/voice.list"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def generate_video(self, video_inputs: list, dimension: dict = None, background: dict = None):
        """
        Generate a video using the provided video_inputs list.
        
        Optionally specify:
          - dimension: e.g. {"width": 1280, "height": 720}
          - background: a dictionary supporting background settings.
        
        Background Settings:
          Color Background:
            { "type": "color", "value": "#f6f6fc" }
          Image Background:
            { "type": "image", "url": "<image_url>", "image_asset_id": "<asset_id>", "fit": "cover" }
          Video Background:
            { "type": "video", "url": "<video_url>", "video_asset_id": "<asset_id>", "play_style": "loop", "fit": "cover" }
        
        If a background is provided and a given video_input does not already have one, it will be added.
        """
        # If a background dict is provided, add it to each video input if not already set
        if background:
            for vi in video_inputs:
                if "background" not in vi:
                    vi["background"] = background

        url = f"{self.base_url_v2}/video/generate"
        data = {"video_inputs": video_inputs}
        if dimension:
            data["dimension"] = dimension

        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def check_video_status(self, video_id: str):
        """Check the status of a generated video using its video_id."""
        url = f"{self.base_url_v1}/video_status.get"
        params = {"video_id": video_id}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def wait_for_video_completion(self, video_id: str, interval: int = 5, timeout: int = 300):
        """
        Polls the video status every `interval` seconds until the video status is 'completed' or 'failed'.
        
        Parameters:
            video_id (str): The ID of the video to check.
            interval (int): Time in seconds between each status check. Default is 5 seconds.
            timeout (int): Maximum time in seconds to wait. Default is 300 seconds (5 minutes).
            
        Returns:
            dict: The final video status response.
            
        Raises:
            TimeoutError: If the video status does not become 'completed' or 'failed' within the timeout period.
        """
        start_time = time.time()
        while True:
            status_response = self.check_video_status(video_id)
            status = status_response.get("data", {}).get("status", "").lower()
            print(f"Current status: {status}")  # Debug output
            if status in ("completed", "failed"):
                return status_response
            
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Timeout reached: Video status did not become 'completed' or 'failed' within {timeout} seconds.")
            
            time.sleep(interval)

    def download_video(self, video_url: str, output_file: str):
        """Download the video or file from the given URL and save it to output_file."""
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return os.path.abspath(output_file)

    def upload_talking_photo(self, file_path: str):
        """
        Upload a talking photo image.
        The file should be a JPEG or PNG and meet the required image guidelines.
        """
        url = f"{self.upload_url}/talking_photo"
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ('.jpg', '.jpeg'):
            content_type = 'image/jpeg'
        elif ext == '.png':
            content_type = 'image/png'
        else:
            raise ValueError("Unsupported file type. Only JPEG and PNG are allowed.")
        
        headers = self.headers.copy()
        headers['Content-Type'] = content_type

        with open(file_path, 'rb') as f:
            response = requests.post(url, headers=headers, data=f)
        response.raise_for_status()
        return response.json()

    def list_talking_photos(self):
        """Retrieve a list of already uploaded talking photos."""
        url = f"{self.base_url_v1}/talking_photo.list"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def generate_talking_photo_video(self, talking_photo_id: str, input_text: str, voice_id: str, background_color: str = "#FFFFFF"):
        """
        Generate a video using a talking photo.
        
        Parameters:
            talking_photo_id (str): The ID of the uploaded talking photo.
            input_text (str): The text for the voice-over.
            voice_id (str): The voice ID to be used.
            background_color (str): Background color in hex. Default is "#FFFFFF".
            
        Returns:
            dict: Response from the video generation API.
        """
        url = f"{self.base_url_v2}/video/generate"
        data = {
            "video_inputs": [
                {
                    "character": {
                        "type": "talking_photo",
                        "talking_photo_id": talking_photo_id
                    },
                    "voice": {
                        "type": "text",
                        "input_text": input_text,
                        "voice_id": voice_id
                    },
                    "background": {
                        "type": "color",
                        "value": background_color
                    }
                }
            ]
        }
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def generate_video_with_audio_source(self, avatar_id: str, voice_audio_asset_id: str, background_color: str = None, avatar_style: str = "normal"):
        """
        Generate a video using an audio asset as the voice.
        
        Parameters:
            avatar_id (str): The ID of the avatar.
            voice_audio_asset_id (str): The audio asset ID.
            background_color (str, optional): Background color as a hex value.
            avatar_style (str): The style of the avatar. Default is "normal".
            
        Returns:
            dict: Response from the video generation API.
        """
        url = f"{self.base_url_v2}/video/generate"
        video_input = {
            "character": {
                "type": "avatar",
                "avatar_id": avatar_id,
                "avatar_style": avatar_style
            },
            "voice": {
                "type": "audio",
                "audio_asset_id": voice_audio_asset_id
            }
        }
        if background_color:
            video_input["background"] = {
                "type": "color",
                "value": background_color
            }
        data = {"video_inputs": [video_input]}
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def upload_asset(self, file_path: str):
        """
        Upload an asset (image, video, or audio) to HeyGen.
        
        The content type is automatically determined based on the file extension:
          - JPEG: image/jpeg
          - PNG: image/png
          - MP4: video/mp4
          - WEBM: video/webm
          - MPEG: audio/mpeg
        
        Parameters:
            file_path (str): The local path to the asset file.
            
        Returns:
            dict: The JSON response from the API containing the asset ID and other details.
        """
        url = f"{self.upload_url}/asset"
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ('.jpg', '.jpeg'):
            content_type = "image/jpeg"
        elif ext == '.png':
            content_type = "image/png"
        elif ext == '.mp4':
            content_type = "video/mp4"
        elif ext == '.webm':
            content_type = "video/webm"
        elif ext in ('.mp3', '.mpeg'):
            content_type = "audio/mpeg"
        else:
            raise ValueError("Unsupported file type for asset upload.")

        headers = self.headers.copy()
        headers["Content-Type"] = content_type

        with open(file_path, "rb") as file:
            response = requests.post(url, headers=headers, data=file)
        response.raise_for_status()
        return response.json()
    
    def generate_and_download_video_simple(
        self,
        # Character and voice settings
        character_type: str = "avatar",
        avatar_id: str = "Judith_expressive_2024120201",
        avatar_style: str = "normal",
        voice_type: str = "text",
        input_text: str = "Welcome to the HeyGen API!",
        voice_id: str = "c4be407b9d94405a9eb403190d77c851",
        speed: float = 1.1,
        # Video dimensions
        width: int = 1280,
        height: int = 720,
        # Background settings (default assumes a video background)
        background_type: str = "video",  # Options: "video", "image", "color"
        background_asset_id: str = "f978e4db1f2743d3a4001c0b3e6b6bb7",
        play_style: str = "loop",  # Only used for video backgrounds
        fit: str = "cover",        # Used for video and image backgrounds
        # Output file names and polling parameters
        video_output_file: str = "output_video.mp4",
        thumbnail_output_file: str = "thumbnail.jpg",
        poll_interval: int = 5,
        timeout: int = 300
    ) -> tuple:
        """
        Generate a video using individual parameters, wait for it to complete,
        and download both the video and its thumbnail.

        Parameters:
            character_type (str): Type of character (default "avatar").
            avatar_id (str): ID for the avatar.
            avatar_style (str): Style of the avatar.
            voice_type (str): Type of voice input (default "text").
            input_text (str): Text to be converted into speech.
            voice_id (str): Voice ID to use.
            speed (float): Speed factor for the voice.
            width (int): Width of the video.
            height (int): Height of the video.
            background_type (str): Type of background ("video", "image", or "color").
            background_asset_id (str): Asset ID for the background. For a color background, pass a hex value.
            play_style (str): Video play style (only used for video backgrounds).
            fit (str): Fit mode for the background.
            video_output_file (str): File path for saving the output video.
            thumbnail_output_file (str): File path for saving the thumbnail image.
            poll_interval (int): Seconds between status checks.
            timeout (int): Maximum seconds to wait for video generation.

        Returns:
            tuple: (video_file_path, thumbnail_file_path)
        """
        # Build the video_inputs dictionary
        video_inputs = [{
            "character": {
                "type": character_type,
                "avatar_id": avatar_id,
                "avatar_style": avatar_style
            },
            "voice": {
                "type": voice_type,
                "input_text": input_text,
                "voice_id": voice_id,
                "speed": speed
            }
        }]

        # Build the dimension dictionary
        dimension = {"width": width, "height": height}

        # Build the background dictionary based on the provided type
        background = None
        if background_type.lower() == "video":
            background = {
                "type": "video",
                "video_asset_id": background_asset_id,
                "play_style": play_style,
                "fit": fit
            }
        elif background_type.lower() == "image":
            background = {
                "type": "image",
                "image_asset_id": background_asset_id,
                "fit": fit
            }
        elif background_type.lower() == "color":
            background = {
                "type": "color",
                "value": background_asset_id  # For color, the asset id parameter should be a color hex code
            }

        # Generate the video
        gen_response = self.generate_video(video_inputs, dimension, background)
        video_id = gen_response['data']['video_id']

        # Wait for the video to complete
        final_status = self.wait_for_video_completion(video_id, interval=poll_interval, timeout=timeout)

        # Extract URLs for video and thumbnail
        video_url = final_status["data"]["video_url"]
        thumbnail_url = final_status["data"]["thumbnail_url"]

        # Download the video and thumbnail
        video_file_path = self.download_video(video_url, video_output_file)
        thumbnail_file_path = self.download_video(thumbnail_url, thumbnail_output_file)

        return video_file_path, thumbnail_file_path



if __name__ == "__main__":
    api = HeyGenAPI()

    try:
        video_path, thumbnail_path = api.generate_and_download_video_simple(
            # Character and voice parameters
            character_type="avatar",
            avatar_id="Judith_expressive_2024120201",
            avatar_style="normal",
            voice_type="text",
            input_text="Artificial Intelligence is transforming our world... It automates complex tasks, streamlines decision-making, and unlocks endless creative potential! In healthcare, finance, education, and beyond, AI reduces errors and saves valuable time — empowering us to focus on what truly matters... Embrace the future where technology inspires innovation and enriches every aspect of our lives!",
            voice_id="c4be407b9d94405a9eb403190d77c851",
            speed=1.1,
            # Video dimensions
            width=1280,
            height=720,
            # Background parameters (defaults to video background)
            background_type="video",
            background_asset_id="f978e4db1f2743d3a4001c0b3e6b6bb7",
            play_style="loop",
            fit="cover",
            # Output and polling parameters
            video_output_file="output_video.mp4",
            thumbnail_output_file="thumbnail.jpg",
            poll_interval=5,
            timeout=300
        )
        print("Video saved at:", video_path)
        print("Thumbnail saved at:", thumbnail_path)
    except Exception as e:
        print("Error generating video:", e)

