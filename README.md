# AI Voice Agent - proPAL AI - Assignment

A real-time voice interaction system built with LiveKit that combines Speech-to-Text, Large Language Model, and Text-to-Speech capabilities to create an interactive voice agent.

## Features

- Speech-to-Text (STT) using OpenAI's Whisper
- Large Language Model (LLM) integration with Groq (Llama3-70B model)
- Text-to-Speech (TTS) using ElevenLabs
- Real-time streaming support via LiveKit
- Comprehensive metrics tracking and logging to Excel
- Multi-language support

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)

### 2. Installation

```bash
# Clone or download the project files
git clone https://github.com/allwin107/AI-Voice-Agent.git
cd ai-voice-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Requirements

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file with your API keys:

```bash
GROQ_API_KEY=your_groq_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
```
### Getting API Keys

1. **Gorq (free LLM)** [console.groq.com](https://console.groq.com) - Fast LLM inference
2. **ElevenLabs**: [elevenlabs.io](https://elevenlabs.io/) - Text-to-Speech
3. **Livekit**: [LiveKit Cloud](https://cloud.livekit.io/) - Real-time communication


## Project Structure

- `app/pipeline/` - Core pipeline components
  - `stt.py` - Speech-to-Text using Whisper
  - `llm.py` - Language model integration using Groq
  - `tts.py` - Text-to-Speech using ElevenLabs
  - `voice_agent.py` - Main voice agent pipeline
  - `livekit_backend.py` - Livekit Integration
- `app/test/` - Testing Scripts
  - `test_stt.py` - Tests the transcription functionality of the STT (Speech-to-Text) module.
  - `test_llm.py` - This script is used to test the LLM response generation functionality.
  - `test_tts.py` - Test the text-to-speech functionality of the application.
  - `test_agent.py` - Test script for the voice agent pipeline
  - `test_audio` - Test .wav audio file
- `app/config.py` - Configuration settings for the application
- `.env` - Environment Variables
- `README.md`
- `requirements.txt`

## Usage

### Running Tests

Test individual components:

```bash
python app/pipeline/test_stt.py
python app/pipeline/test_llm.py
python app/pipeline/test_tts.py
python app/pipeline/test_agent.py
```

### Running the Voice Agent

```bash
python app/pipeline/voice_agent.py
```

## Test Your Agent with LiveKit

### 1. Prerequisites Check

Make sure you’ve done this:

1. Activated a LiveKit Cloud instance
2. Have the following values into .env :

- LIVEKIT_WS_URL=wss://<your-instance>.livekit.cloud
- LIVEKIT_API_KEY=...
- LIVEKIT_API_SECRET=...

### 2. Start Your Voice Agent Locally

Run your `livekit_backend.py` script from terminal:

```bash
python app/pipeline/livekit_backend.py
```

If working correctly, logs will say:

Connected to room `your-livekit-room` as `your-participant-name`

This means the agent is live and ready to receive audio.

### 3. Join the Same Room as a Human User

Use the LiveKit Agent Playground:
https://agent.livekit.io

This is essential for testing as the "other participant"

Steps:

1. Go to the Playground URL
2. Input the same Room Name (your-livekit-room)
3. Use your LiveKit credentials:
  - API Key, API Secret
  - Click Join Room

🎙️ Now when you speak, your local VoiceAgentBot should:

1. Detect your voice
2. Transcribe it
3. Send it to the LLM
4. Reply back via audio in real-time
5. Log metrics

## Performance Metrics

The system tracks several key metrics:
- EOU (End of Utterance) Delay
- TTFT (Time to First Token)
- TTFB (Time to First Byte)
- Total Latency

## Future Improvements

1. Smarter language detection
2. Improved end-of-utterance (EOU) timing
3. Web or mobile interface integration

## 📜 License

This project is created for the proPAL AI Backend Engineering Internship assignment.

**Built with ❤️ for proPAL**