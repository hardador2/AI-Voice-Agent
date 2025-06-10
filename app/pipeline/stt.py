# Import necessary libraries
import whisper
from typing import Tuple, Optional

# Load the base Whisper model
model = whisper.load_model("base")

def transcribe_audio(audio_path: str, language: Optional[str] = None) -> Tuple[str, float, str]:
    """
    Transcribes the given audio file using Whisper.
    Args:
        audio_path: Path to audio file.
        language: Optional ISO language code (e.g., 'en', 'fr', 'hi').
    Returns:
        (transcribed_text, fake_eou_time, detected_language)
    """
    options = {}
    if language:
        options["language"] = language

    result = model.transcribe(audio_path, **options)
    text = result["text"].strip()
    detected_language = result.get("language", "unknown")

    fake_eou_time = 0.0  # You can improve later with real timestamps

    return text, fake_eou_time, detected_language
