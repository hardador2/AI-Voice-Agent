# This module implements a voice agent pipeline that processes audio input, transcribes it, generates a response using an LLM, and converts the response to speech using TTS. It also measures various latencies in the process.

# Import necessary libraries
import time
import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import pipeline components
from stt import transcribe_audio
from llm import generate_response
from tts import text_to_speech

async def voice_agent_pipeline(audio_path: str, language: str = "en"):

    """ Voice Agent Pipeline: Processes audio input, transcribes it, generates a response, and converts it to speech.
    This function orchestrates the entire voice agent pipeline, measuring latencies and handling audio processing."""

    print("Starting voice agent pipeline...")

    # 1. STT - transcribe user speech with language parameter
    start_stt = time.time()
    transcript, eou_time, detected_language = await asyncio.to_thread(transcribe_audio, audio_path, language)
    stt_end = time.time()
    print(f"STT Transcript: {transcript}")
    print(f"EOU time (sec): {eou_time}")
    print(f"Detected Language: {detected_language}")

    # Calculate EOU delay (silence detection latency)
    eou_delay = eou_time  # assuming returned EOU is delay after end of utterance

    # 2. LLM - generate response
    start_llm = time.time()
    response = await generate_response(transcript)
    llm_end = time.time()
    print(f"LLM Response: {response}")

    # 3. TTS - convert LLM response to speech
    start_tts = time.time()
    audio_output_path = await text_to_speech(response, language=detected_language)
    tts_end = time.time()
    print(f"TTS audio saved at: {audio_output_path}")

    # Optional: Playback the generated TTS audio
    import pygame

    pygame.mixer.init()
    pygame.mixer.music.load(audio_output_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


    # Calculate Metrics
    ttft = start_llm - stt_end          # Time from STT done to LLM start (approx)
    ttfb = start_tts - llm_end          # Time from LLM done to TTS start (approx)
    total_latency = tts_end - start_stt # Total time from STT start to TTS done

    print("\n=== Metrics ===")
    print(f"EOU Delay: {eou_delay:.3f} sec")
    print(f"TTFT (STT->LLM): {ttft:.3f} sec")
    print(f"TTFB (LLM->TTS): {ttfb:.3f} sec")
    print(f"Total Latency (STT->TTS done): {total_latency:.3f} sec")

    return {
        "transcript": transcript,
        "detected_language": detected_language,
        "response": response,
        "audio_path": audio_output_path,
        "metrics": {
            "EOU Delay": eou_delay,
            "TTFT": ttft,
            "TTFB": ttfb,
            "Total Latency": total_latency
        }
    }

if __name__ == "__main__":
    import sys
    audio_file = sys.argv[1] if len(sys.argv) > 1 else "app/test/test_audio.wav"
    # Optionally, accept language arg too
    language_arg = sys.argv[2] if len(sys.argv) > 2 else "en"
    asyncio.run(voice_agent_pipeline(audio_file, language=language_arg))