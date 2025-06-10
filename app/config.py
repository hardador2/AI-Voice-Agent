# Configuration settings for the application

# Import necessary libraries
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Settings:

    """Configuration settings for the application."""

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Default to Rachel
    ELEVENLABS_VOICE_MAP = {
        "en": os.getenv("ELEVENLABS_VOICE_ID_EN", "21m00Tcm4TlvDq8ikWAM"),  # Rachel (English)
        "es": os.getenv("ELEVENLABS_VOICE_ID_ES", "EXAMPLE_VOICE_ID_ES"),    # Spanish voice (replace with actual)
        "fr": os.getenv("ELEVENLABS_VOICE_ID_FR", "EXAMPLE_VOICE_ID_FR"),    # French voice
        # Add more languages and their voice IDs here
    }
    GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/v1/")  # Default URL

settings = Settings()
