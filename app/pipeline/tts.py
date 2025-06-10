# This module provides text-to-speech functionality using the ElevenLabs API.
# Import necessary libraries
import httpx
import uuid
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
from app.config import settings

# Define the ElevenLabs API key and voice ID
# Ensure you have the ElevenLabs API key set in your environment or config
ELEVENLABS_API_KEY = settings.ELEVENLABS_API_KEY #"sk_2ded8236624072a34c94c5b6aeec710da4994820994bb742"
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # premade "Rachel"

# Map language codes (ISO 639-1) to ElevenLabs voice IDs (add more as needed)
VOICE_MAP = {
    "en": "21m00Tcm4TlvDq8ikWAM",  # Rachel (English)
    "es": "EXAMPLE_VOICE_ID_ES",    # Spanish voice (replace with actual)
    "fr": "EXAMPLE_VOICE_ID_FR",    # French voice
    # Add more languages and their voice IDs here
}

async def text_to_speech(text: str, language: str = "en", output_path: str = None) -> str:

    """ Function to convert text to speech using ElevenLabs API.    """

    # Validate input parameters
    output_path = output_path or f"tts_output_{uuid.uuid4().hex[:6]}.mp3"
    voice_id = VOICE_MAP.get(language, VOICE_MAP["en"])

    # Construct the API request URL and headers
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    # Use multilingual model if language not English
    model_id = "eleven_monolingual_v1" if language == "en" else "eleven_multilingual_v2"

    # Prepare the payload for the API request
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_id": voice_id,
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }

    timeout = httpx.Timeout(30.0)

    # Make the API request to convert text to speech
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)

    return output_path
