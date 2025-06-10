# Test script for the voice agent pipeline

# Import necessary modules
import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to Python path to locate the pipeline module
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
from pipeline.voice_agent import voice_agent_pipeline

async def test():

    '''    Function to test the voice agent pipeline using a sample audio file.
    This function simulates a voice interaction, processes the audio, and prints the results.   '''

    # Test with default English audio
    print("Testing with English audio...")
    test_audio = "app/test/test_audio.wav"
    result = await voice_agent_pipeline(test_audio, language="en")
    
    # Print the results
    print("\n=== Test Results ===")
    print(f"Transcript: {result['transcript']}")
    print(f"Detected Language: {result['detected_language']}")
    print(f"Bot Response: {result['response']}")
    print(f"Audio Output: {result['audio_path']}")
    print("\nMetrics:")
    for metric, value in result['metrics'].items():
        print(f"{metric}: {value:.3f} sec")

if __name__ == "__main__":
    asyncio.run(test())
