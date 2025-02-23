import os
import requests
from flask import Flask, render_template_string
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
AVATARS_URL = "https://api.heygen.com/v2/avatars"

@app.route("/")
def index():
    headers = {
        "X-Api-Key": HEYGEN_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(AVATARS_URL, headers=headers)
        response.raise_for_status()
        # Extract avatars from the "data" key in the response JSON.
        response_data = response.json()
        avatars = response_data.get("data", {}).get("avatars", [])
    except Exception as e:
        avatars = []
        print("Error fetching avatars:", e)
    
    # HTML template using Jinja2 syntax
    html_template = """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8">
        <title>HeyGen Avatars Preview</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            margin: 20px;
          }
          .container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
          }
          .avatar {
            border: 1px solid #ccc;
            padding: 10px;
            margin: 10px;
            width: 300px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
          }
          .avatar img, .avatar video {
            width: 100%;
            display: block;
            margin-bottom: 10px;
          }
          .avatar h2 {
            font-size: 1.2em;
            margin: 0 0 5px;
          }
          .avatar p {
            font-size: 0.9em;
            color: #555;
          }
        </style>
      </head>
      <body>
        <h1 style="text-align: center;">HeyGen Avatars Preview</h1>
        <div class="container">
          {% for avatar in avatars %}
          <div class="avatar">
            <h2>{{ avatar.avatar_name }}</h2>
            <p>ID: {{ avatar.avatar_id }}</p>
            <img src="{{ avatar.preview_image_url }}" alt="{{ avatar.avatar_name }} preview image">
            <video controls>
              <source src="{{ avatar.preview_video_url }}" type="video/mp4">
              Your browser does not support the video tag.
            </video>
          </div>
          {% endfor %}
        </div>
      </body>
    </html>
    """
    return render_template_string(html_template, avatars=avatars)

if __name__ == "__main__":
    # Run on port 5001 (or any other port to avoid conflicts with your old project)
    app.run(debug=True, port=5001)
