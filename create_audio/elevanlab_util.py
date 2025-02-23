from elevenlabs import ElevenLabs
from dotenv import load_dotenv
import os

load_dotenv()

client = ElevenLabs(
    api_key=os.getenv("ELEVANLAB_API_KEY"),
)

response = client.text_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    output_format="mp3_44100_128",
    text="The first move is what sets everything in motion.",
    model_id="eleven_multilingual_v2",
)

# Consume the generator to get the audio bytes
audio_data = b"".join(chunk for chunk in response)

with open("response.mp3", "wb") as f:
    f.write(audio_data)