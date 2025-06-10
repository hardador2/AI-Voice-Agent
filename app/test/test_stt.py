# Import necessary modules
import os
import sys

# Print the current working directory for debugging
print("Current working directory:", os.getcwd())

# Adjust import if running from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.stt import transcribe_audio

def test():
    '''    Function to test the transcription of audio files using the transcribe_audio function.   '''
    
    # Path to the audio file to be transcribed
    file_path = "app/test/test_audio.wav" 

    # Test without specifying language (auto detect)
    text, eou, detected_lang = transcribe_audio(file_path)
    print("Transcription (auto language):", text)
    print("EOU Time:", eou)
    print("Detected Language:", detected_lang)

    # Test specifying language explicitly (example: English 'en')
    text2, eou2, detected_lang2 = transcribe_audio(file_path, language="en")
    print("Transcription (language='en'):", text2)
    print("EOU Time:", eou2)
    print("Detected Language:", detected_lang2)

if __name__ == "__main__":
    test()
