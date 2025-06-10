# AI Voice Agent - proPAL AI Backend Engineering Assignment

A real-time voice interaction system that combines Speech-to-Text, Large Language Model, and Text-to-Speech capabilities to create an interactive voice agent.

## Features

- Speech-to-Text (STT) using OpenAI's Whisper
- LLM integration with Groq (Llama3-70B model)
- Text-to-Speech using ElevenLabs
- Comprehensive metrics tracking and logging
- Multi-language support

## Requirements

Install the required dependencies:

```sh
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file with your API keys:
```
GROQ_API_KEY=your_groq_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

## Project Structure

- `app/pipeline/` - Core pipeline components
  - `stt.py` - Speech-to-Text using Whisper
  - `llm.py` - Language model integration using Groq
  - `tts.py` - Text-to-Speech using ElevenLabs
  - `voice_agent.py` - Main voice agent pipeline
  - `livekit_backend.py` - LiveKit real-time audio streaming
  - `agent.py` - Voice processing pipeline

## Usage

### Running Tests

Test individual components:

```sh
python app/pipeline/test_stt.py
python app/pipeline/test_llm.py
python app/pipeline/test_tts.py
python app/pipeline/test_agent.py
```

### Running the Voice Agent

```sh
python app/pipeline/voice_agent.py
```

## Performance Metrics

The system tracks several key metrics:
- EOU (End of Utterance) Delay
- TTFT (Time to First Token)
- TTFB (Time to First Byte)
- Total Latency

## Future Improvements

1. Real-time streaming support via LiveKit

2. Smarter language detection

3. Improved end-of-utterance (EOU) timing

4. Web or mobile interface integration

