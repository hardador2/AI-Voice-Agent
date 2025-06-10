# Import necessary modules
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from pipeline.tts import text_to_speech

async def test():

    '''    Function to test the text-to-speech conversion using the text_to_speech function.   '''
    
    # Convert text to speech and save the audio file
    path = await text_to_speech("Hello! I'm your AI assistant. Let's have a chat.")
    print("Audio saved at:", path)

asyncio.run(test())
