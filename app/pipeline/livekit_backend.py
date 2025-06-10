import asyncio
import time
import io
import wave
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging
from collections import deque
import numpy as np

try:
    # Core imports
    from livekit.rtc import Room
    from livekit.rtc.participant import LocalParticipant, RemoteParticipant

    # Track and Audio imports
    from livekit.rtc.track import (
        LocalAudioTrack,
        AudioTrack,        
        )
    from livekit.rtc.audio_source import AudioSource, AudioFrame 
    from livekit.rtc._proto.track_pb2 import TrackKind
    # Track kind and publication imports
    from livekit.rtc.track_publication import (
        TrackPublication,
        RemoteTrackPublication,
        LocalTrackPublication
    )
    
    # Auth imports
    from livekit.api import AccessToken, VideoGrants, SIPGrants
    from livekit.api.livekit_api import LiveKitAPI

    print("✓ All LiveKit imports successful")
    
except ImportError as e:
    print(f"LiveKit import error: {e}")
    print("Please install required packages:")
    print("pip install livekit==1.0.8")
    exit(1)


from stt import transcribe_audio
from llm import generate_response
from tts import text_to_speech
from config import settings

# LiveKit Configuration
LIVEKIT_API_KEY = settings.LIVEKIT_API_KEY
LIVEKIT_API_SECRET = settings.LIVEKIT_API_SECRET
LIVEKIT_WS_URL = settings.LIVEKIT_API_URL
ROOM_NAME = settings.LIVEKIT_ROOM_NAME
BOT_PARTICIPANT_NAME = settings.LIVEKIT_PARTICIPANT_NAME

# Add after LiveKit Configuration section
if not all([LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_WS_URL, ROOM_NAME, BOT_PARTICIPANT_NAME]):
    missing = []
    if not LIVEKIT_API_KEY: missing.append("LIVEKIT_API_KEY")
    if not LIVEKIT_API_SECRET: missing.append("LIVEKIT_API_SECRET")
    if not LIVEKIT_WS_URL: missing.append("LIVEKIT_API_URL")
    if not ROOM_NAME: missing.append("LIVEKIT_ROOM_NAME")
    if not BOT_PARTICIPANT_NAME: missing.append("LIVEKIT_PARTICIPANT_NAME")
    raise ValueError(f"Missing required LiveKit configuration: {', '.join(missing)}")

class VoiceAgent:
    def __init__(self):
        self.room = Room()
        self.audio_source = AudioSource(sample_rate=16000, num_channels=1)
        self.local_track = LocalAudioTrack.create_audio_track("agent-audio", self.audio_source)

        # Audio processing
        self.audio_buffer = deque()
        self.is_processing = False
        self.is_speaking = False
        self.stop_tts = False  
        self.silence_threshold = 0.01
        self.silence_duration_threshold = 1.0
        self.last_audio_time = 0

        # Session metrics
        self.session_start_time = None
        self.session_metrics = []
        self.conversation_count = 0
        self.total_audio_duration = 0

        # Excel logging
        self.excel_filename = f"voice_agent_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def generate_token(self, identity: str, room_name: str) -> str:
        """Generate LiveKit access token for the bot"""
        try:
            token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
            token.identity = identity
            token.name = identity 
            
            # Create and configure the grant
            grant = VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True
            )
            
            # Set the grant
            token.video_grant = grant
            
            # Generate and return the JWT token
            jwt_token = token.to_jwt()
            self.logger.debug(f"Generated token for {identity} in room {room_name}")
            return jwt_token
        except Exception as e:
            self.logger.error(f"Error generating token: {e}")
            raise


    async def connect(self):
        """Connect to LiveKit room and set up event handlers"""
        token = self.generate_token(identity=BOT_PARTICIPANT_NAME, room_name=ROOM_NAME)

        # Debug logging
        self.logger.info(f"Connecting with URL: {LIVEKIT_WS_URL}")
        self.logger.info(f"Room name: {ROOM_NAME}")
        self.logger.info(f"Identity: {BOT_PARTICIPANT_NAME}")
        self.logger.info(f"Generated token: {token[:20]}... (truncated for security)")
        self.logger.info("Connecting to LiveKit...")

        url = LIVEKIT_WS_URL.rstrip('/')
        if not url.startswith(('ws://', 'wss://')):
            url = f"wss://{url}"

        try:
            # Connect with a timeout
            connect_task = self.room.connect(url=url, token=token)
            await asyncio.wait_for(connect_task, timeout=30.0)

            # Publish local track
            await self.room.local_participant.publish_track(self.local_track)
            
            self.session_start_time = time.time()
            self.logger.info(f"Successfully connected to room '{ROOM_NAME}' as {BOT_PARTICIPANT_NAME}")

            # Set up event handlers
            self.room.on("participant_connected", self.on_participant_connected)
            self.room.on("participant_disconnected", self.on_participant_disconnected)
            self.room.on("track_published", self.on_track_published)
            
        except asyncio.TimeoutError:
            self.logger.error("Connection timeout")
            raise
        except Exception as e:
            self.logger.error(f"Failed to connect to LiveKit: {str(e)}")
            raise

    def on_participant_connected(self, participant):
        self.logger.info(f"Participant connected: {participant.identity}")

    def on_participant_disconnected(self, participant):
        self.logger.info(f"Participant disconnected: {participant.identity}")
        # Log session summary when participant leaves
        asyncio.create_task(self.log_session_summary())

    async def on_track_published(self, publication: RemoteTrackPublication, participant):
        """Handle new audio track from participant"""
        if publication.kind == TrackKind.AUDIO:
            self.logger.info(f"Audio track published by {participant.identity}")
            track = publication.track
            
            if track:
                await track.start()
                asyncio.create_task(self.process_audio_stream(track))

    async def process_audio_stream(self, track):
        """Process incoming audio stream in real-time"""
        audio_frames = []
        last_frame_time = time.time()

        async for audio_frame in track.recv():
            current_time = time.time()

            # Handle interruption: If user speaks during TTS playback
            if self.is_speaking:
                self.logger.info("Interruption detected - stopping TTS playback")
                self.stop_tts = True
                # Wait until TTS streaming is halted before continuing
                while self.is_speaking:
                    await asyncio.sleep(0.01)

            # Convert audio frame to numpy array
            audio_data = np.frombuffer(audio_frame.data, dtype=np.int16)
            audio_frames.append(audio_data)

            # Voice activity detection
            rms = np.sqrt(np.mean(audio_data.astype(float) ** 2))
            if rms > self.silence_threshold:
                last_frame_time = current_time

            silence_duration = current_time - last_frame_time
            if silence_duration > self.silence_duration_threshold and audio_frames and not self.is_processing:
                self.is_processing = True
                asyncio.create_task(self.process_voice_input(audio_frames.copy()))
                audio_frames.clear()

    async def process_voice_input(self, audio_frames):
        """Process voice input through STT -> LLM -> TTS pipeline"""
        try:
            conversation_start = time.time()
            metrics = {"conversation_id": self.conversation_count + 1}

            # Convert audio frames to WAV
            audio_data = np.concatenate(audio_frames)
            temp_audio_path = f"temp_audio_{int(time.time())}.wav"
            with wave.open(temp_audio_path, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(16000)
                wav_file.writeframes(audio_data.tobytes())

            # Duration
            audio_duration = len(audio_data) / 16000
            self.total_audio_duration += audio_duration
            metrics["audio_duration"] = round(audio_duration, 3)

            # STT
            stt_start = time.time()
            transcribed_text, eou_time, detected_language = await asyncio.to_thread(
                transcribe_audio, temp_audio_path
            )
            stt_end = time.time()

            if not transcribed_text.strip():
                self.logger.info("No speech detected, skipping processing")
                self.is_processing = False
                Path(temp_audio_path).unlink(missing_ok=True)
                return

            metrics["eou_delay"] = round(eou_time, 3)
            metrics["stt_latency"] = round(stt_end - stt_start, 3)
            metrics["transcription"] = transcribed_text
            metrics["detected_language"] = detected_language

            self.logger.info(f"STT: {transcribed_text}")

            # LLM
            llm_start = time.time()
            llm_response = await generate_response(transcribed_text)
            llm_end = time.time()

            metrics["ttft"] = round(llm_end - llm_start, 3)
            metrics["llm_response"] = llm_response

            self.logger.info(f"LLM: {llm_response}")

            # TTS
            tts_start = time.time()
            self.stop_tts = False  # Reset before playback
            tts_output_path = await text_to_speech(llm_response, language=detected_language)
            tts_end = time.time()

            metrics["ttfb"] = round(tts_end - tts_start, 3)
            metrics["total_latency"] = round(tts_end - conversation_start, 3)

            # Play TTS
            await self.stream_audio_to_room(tts_output_path)

            # Metrics
            metrics["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.session_metrics.append(metrics)
            self.conversation_count += 1

            self.logger.info(f"Metrics - EOU: {metrics['eou_delay']}s, TTFT: {metrics['ttft']}s, "
                            f"TTFB: {metrics['ttfb']}s, Total: {metrics['total_latency']}s")

            if metrics['total_latency'] > 2.0:
                self.logger.warning(f"Latency exceeded 2s: {metrics['total_latency']}s")

            # Cleanup
            Path(temp_audio_path).unlink(missing_ok=True)
            Path(tts_output_path).unlink(missing_ok=True)

        except Exception as e:
            self.logger.error(f"Error processing voice input: {e}")
        finally:
            self.is_processing = False
            self.last_audio_time = time.time()
            self.stop_tts = False
            self.logger.info("Processing complete, ready for next input")


    async def stream_audio_to_room(self, audio_file_path):
        """Stream TTS audio back to the LiveKit room"""
        try:
            self.is_speaking = True
            self.stop_tts = False  # Reset flag before streaming

            with wave.open(audio_file_path, 'rb') as wav_file:
                sample_rate = wav_file.getframerate()
                num_channels = wav_file.getnchannels()
                chunk_size = int(sample_rate * 0.02)

                while True:
                    if self.stop_tts:  # Interruption check
                        self.logger.info("TTS playback interrupted by new speech input.")
                        break

                    audio_data = wav_file.readframes(chunk_size)
                    if not audio_data:
                        break

                    audio_array = np.frombuffer(audio_data, dtype=np.int16)

                    frame = AudioFrame(
                        data=audio_array.tobytes(),
                        sample_rate=sample_rate,
                        num_channels=num_channels,
                        samples_per_channel=len(audio_array) // num_channels
                    )

                    await self.audio_source.capture_frame(frame)
                    await asyncio.sleep(0.02)

            self.logger.info("Finished streaming TTS audio")

        except Exception as e:
            self.logger.error(f"Error streaming audio: {e}")

        finally:
            self.is_speaking = False

    async def log_session_summary(self):
        """Log session metrics to Excel file"""
        try:
            if not self.session_metrics:
                self.logger.info("No metrics to log")
                return
            
            # Create detailed metrics DataFrame
            df_metrics = pd.DataFrame(self.session_metrics)
            
            # Create session summary
            session_duration = time.time() - self.session_start_time if self.session_start_time else 0
            avg_latency = df_metrics['total_latency'].mean() if not df_metrics.empty else 0
            avg_eou_delay = df_metrics['eou_delay'].mean() if not df_metrics.empty else 0
            avg_ttft = df_metrics['ttft'].mean() if not df_metrics.empty else 0
            avg_ttfb = df_metrics['ttfb'].mean() if not df_metrics.empty else 0
            
            session_summary = {
                'Session Start': [datetime.fromtimestamp(self.session_start_time).strftime("%Y-%m-%d %H:%M:%S")],
                'Session Duration (s)': [round(session_duration, 3)],
                'Total Conversations': [self.conversation_count],
                'Total Audio Duration (s)': [round(self.total_audio_duration, 3)],
                'Average EOU Delay (s)': [round(avg_eou_delay, 3)],
                'Average TTFT (s)': [round(avg_ttft, 3)],
                'Average TTFB (s)': [round(avg_ttfb, 3)],
                'Average Total Latency (s)': [round(avg_latency, 3)],
                'Latency Target Met': ['Yes' if avg_latency < 2.0 else 'No'],
                'Max Latency (s)': [round(df_metrics['total_latency'].max(), 3) if not df_metrics.empty else 0],
                'Min Latency (s)': [round(df_metrics['total_latency'].min(), 3) if not df_metrics.empty else 0]
            }
            
            df_summary = pd.DataFrame(session_summary)
            
            # Write to Excel with multiple sheets
            with pd.ExcelWriter(self.excel_filename, engine='openpyxl') as writer:
                df_summary.to_excel(writer, sheet_name='Session Summary', index=False)
                df_metrics.to_excel(writer, sheet_name='Detailed Metrics', index=False)
            
            self.logger.info(f"Metrics logged to {self.excel_filename}")
            self.logger.info(f"Session Summary - Duration: {session_duration:.1f}s, "
                           f"Conversations: {self.conversation_count}, "
                           f"Avg Latency: {avg_latency:.3f}s")
            
        except Exception as e:
            self.logger.error(f"Error logging to Excel: {e}")

    async def run(self):
        """Main run loop"""
        await self.connect()
        
        try:
            # Keep the agent running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Shutting down voice agent...")
            await self.log_session_summary()
            await self.room.disconnect()

async def main():
    agent = VoiceAgent()
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())