# Import necessary modules
# Ensure the parent directory is in the path for module imports
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from pipeline.llm import generate_response

async def test():
    '''    Function to test the LLM response generation using the generate_response function.   '''
    
    response = await generate_response("What's the weather like in Mumbai today?")
    print("LLM says:", response)

asyncio.run(test())
