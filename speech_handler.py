import os
import asyncio
import aiohttp
import pygame
import tempfile
from pathlib import Path
from typing import Optional
import logging
import speech_recognition as sr
import threading
import time
import wave

class ElevenLabsSpeech:
    """Natural-sounding speech using ElevenLabs API"""
    
    def __init__(self, api_key: Optional[str] = None, voice_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVEN_LABS_API_KEY")
        # Default to Rachel (pleasant, clear female voice) - you can change this
        self.voice_id = voice_id or "EXAVITQu4vr4xnSDxMaL" 
        self.base_url = "https://api.elevenlabs.io/v1"
        
        if not self.api_key:
            raise ValueError("ElevenLabs API key is required. Set ELEVEN_LABS_API_KEY environment variable.")
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Create temp directory for audio files
        self.temp_dir = Path(tempfile.gettempdir()) / "browser_agent_speech"
        self.temp_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def speak(self, text: str, voice_settings: Optional[dict] = None) -> bool:
        """
        Convert text to speech and play it
        
        Args:
            text: Text to convert to speech
            voice_settings: Optional voice configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Default voice settings for natural speech
            default_settings = {
                "stability": 0.75,      # More stable = less variation
                "similarity_boost": 0.8, # Higher = more like original voice
                "style": 0.2,           # Lower = more natural, less dramatic  
                "use_speaker_boost": True
            }
            
            if voice_settings:
                default_settings.update(voice_settings)
            
            # Generate audio
            audio_data = await self._generate_audio(text, default_settings)
            if not audio_data:
                return False
            
            # Save and play audio
            audio_file = await self._save_audio(audio_data)
            if audio_file:
                await self._play_audio(audio_file)
                # Clean up temp file
                try:
                    os.unlink(audio_file)
                except:
                    pass
                return True
                
        except Exception as e:
            self.logger.error(f"Speech generation failed: {e}")
            return False
        
        return False

    async def _generate_audio(self, text: str, voice_settings: dict) -> Optional[bytes]:
        """Generate audio using ElevenLabs API"""
        url = f"{self.base_url}/text-to-speech/{self.voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",  # Fast, high-quality model
            "voice_settings": voice_settings
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        error_text = await response.text()
                        self.logger.error(f"ElevenLabs API error {response.status}: {error_text}")
                        return None
        except Exception as e:
            self.logger.error(f"Network error generating audio: {e}")
            return None

    async def _save_audio(self, audio_data: bytes) -> Optional[str]:
        """Save audio data to temporary file"""
        try:
            temp_file = self.temp_dir / f"speech_{asyncio.get_event_loop().time()}.mp3"
            with open(temp_file, 'wb') as f:
                f.write(audio_data)
            return str(temp_file)
        except Exception as e:
            self.logger.error(f"Failed to save audio: {e}")
            return None

    async def _play_audio(self, audio_file: str):
        """Play audio file using pygame"""
        try:
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
                
        except Exception as e:
            self.logger.error(f"Failed to play audio: {e}")

    def set_voice(self, voice_id: str):
        """Change the voice used for speech"""
        self.voice_id = voice_id

    def get_available_voices(self):
        """Return some popular ElevenLabs voice IDs with descriptions"""
        return {
            "21m00Tcm4TlvDq8ikWAM": "Rachel - Pleasant female, clear",
            "AZnzlk1XvdvUeBnXmlld": "Domi - Confident female, strong", 
            "EXAVITQu4vr4xnSDxMaL": "Bella - Soft female, gentle",
            "ErXwobaYiN019PkySvjV": "Antoni - Calm male, professional",
            "VR6AewLTigWG4xSOukaG": "Arnold - Deep male, authoritative",
            "pNInz6obpgDQGcFmaJgB": "Adam - Friendly male, casual",
            "yoZ06aMxZJJ28mfd3POQ": "Sam - Natural male, conversational"
        }


class SpeechRecognizer:
    """Speech recognition using Google's Web Speech API"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        self.logger = logging.getLogger(__name__)
        
        # Initialize microphone
        self._init_microphone()
        
        # Recognition settings
        self.recognition_timeout = 30  # seconds to wait for speech
        self.phrase_timeout = 10  # seconds of silence to end phrase
        
    def _init_microphone(self):
        """Initialize the microphone with error handling"""
        try:
            # Get default microphone
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.microphone as source:
                print("🎤 Calibrating microphone for ambient noise (this may take a moment)...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
            self.logger.info("Microphone initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize microphone: {e}")
            self.microphone = None
    
    def listen_for_speech(self, prompt: str = None, debug_audio: bool = False) -> Optional[str]:
        """
        Listen for speech input and convert to text
        
        Args:
            prompt: Optional prompt to display to user
            debug_audio: If True, save and play back recorded audio for debugging
            
        Returns:
            Recognized text or None if recognition failed
        """
        if not self.microphone:
            print("❌ No microphone available. Please type your response instead.")
            return None
            
        try:
            # Re-calibrate microphone before each listening session to avoid cached audio issues
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            if prompt:
                print(f"🎤 {prompt}")
            else:
                print("🎤 Listening... (speak now)")
                
            self.is_listening = True
            
            # Listen for audio with timeout - create fresh audio capture
            with self.microphone as source:
                # Clear any previous audio buffer and listen for fresh speech
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.recognition_timeout,
                    phrase_time_limit=self.phrase_timeout
                )
            
            self.is_listening = False
            print("🔄 Processing speech...")
            
            # Debug: Save and play back recorded audio
            if debug_audio:
                self._debug_save_and_play_audio(audio)
            
            # Recognize speech using Google's service with fresh request each time
            try:
                # Force fresh recognition by ensuring no cached results
                text = self.recognizer.recognize_google(audio, show_all=False)
                if text and text.strip():
                    print(f"✅ Recognized: '{text}'")
                    return text.strip()
                else:
                    print("❌ Empty recognition result. Please try again.")
                    return None
                
            except sr.UnknownValueError:
                print("❌ Sorry, I couldn't understand what you said. Please try again or type your response.")
                return None
                
            except sr.RequestError as e:
                print(f"❌ Speech recognition service error: {e}")
                print("Please type your response instead.")
                return None
                
        except sr.WaitTimeoutError:
            print("⏱️ No speech detected within timeout. Please try again or type your response.")
            return None
            
        except Exception as e:
            self.logger.error(f"Speech recognition error: {e}")
            print("❌ Speech recognition failed. Please type your response instead.")
            return None
        
        finally:
            self.is_listening = False
    
    def _debug_save_and_play_audio(self, audio_data):
        """
        Save recorded audio to file and play it back for debugging
        
        Args:
            audio_data: AudioData object from speech_recognition
        """
        try:
            # Create temp directory for debug audio
            debug_dir = Path(tempfile.gettempdir()) / "browser_agent_debug_audio"
            debug_dir.mkdir(exist_ok=True)
            
            # Generate unique filename
            timestamp = int(time.time() * 1000)
            audio_filename = debug_dir / f"recorded_audio_{timestamp}.wav"
            
            # Save audio data as WAV file
            with open(audio_filename, "wb") as f:
                f.write(audio_data.get_wav_data())
            
            print(f"🔧 Debug: Recorded audio saved to {audio_filename}")
            print("🔊 Playing back what was recorded...")
            
            # Play back the recorded audio
            pygame.mixer.music.load(str(audio_filename))
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            print("✅ Debug: Playback complete")
            
            # Clean up the debug file after a short delay
            try:
                time.sleep(0.5)  # Brief delay to ensure file isn't locked
                os.unlink(audio_filename)
            except:
                pass  # Don't worry if cleanup fails
                
        except Exception as e:
            self.logger.error(f"Debug audio playback failed: {e}")
            print("⚠️ Debug audio playback failed, but speech recognition will continue")
    
    def is_available(self) -> bool:
        """Check if speech recognition is available"""
        return self.microphone is not None


class SpeechConfig:
    """Configuration for speech settings"""
    
    def __init__(self):
        self.enabled = True
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel by default
        self.voice_settings = {
            "stability": 0.75,
            "similarity_boost": 0.8, 
            "style": 0.2,
            "use_speaker_boost": True
        }
        self.speak_questions = True
        self.speak_confirmations = True
        self.speak_errors = False  # Usually don't speak errors
        
        # Speech-to-text settings
        self.listen_for_responses = True  # Enable voice input
        self.recognition_timeout = 10  # seconds
        self.offer_voice_input = True  # Show voice input option
        self.debug_audio = False  # Play back recorded audio for debugging
        self.voice_input_default = True  # Make voice input the default mode
        
    def disable_speech(self):
        """Disable all speech"""
        self.enabled = False
        
    def enable_speech(self):
        """Enable speech"""
        self.enabled = True
        
    def set_voice(self, voice_id: str):
        """Change voice"""
        self.voice_id = voice_id
        
    def disable_voice_input(self):
        """Disable voice input while keeping text-to-speech"""
        self.listen_for_responses = False
        
    def enable_voice_input(self):
        """Enable voice input"""
        self.listen_for_responses = True
        
    def enable_debug_audio(self):
        """Enable audio debugging (playback of recorded audio)"""
        self.debug_audio = True
        
    def disable_debug_audio(self):
        """Disable audio debugging"""
        self.debug_audio = False


# Global speech instances - will be initialized when needed
_speech_instance: Optional[ElevenLabsSpeech] = None
_speech_recognizer: Optional[SpeechRecognizer] = None
_speech_config = SpeechConfig()

def get_speech_instance() -> Optional[ElevenLabsSpeech]:
    """Get or create the global speech instance"""
    global _speech_instance
    
    if not _speech_config.enabled:
        return None
        
    if _speech_instance is None:
        try:
            _speech_instance = ElevenLabsSpeech(voice_id=_speech_config.voice_id)
        except ValueError as e:
            logging.warning(f"Speech disabled: {e}")
            return None
    
    return _speech_instance

def get_speech_recognizer() -> Optional[SpeechRecognizer]:
    """Get or create the global speech recognizer instance"""
    global _speech_recognizer
    
    if not _speech_config.listen_for_responses:
        return None
        
    if _speech_recognizer is None:
        try:
            _speech_recognizer = SpeechRecognizer()
        except Exception as e:
            logging.warning(f"Speech recognition disabled: {e}")
            return None
    
    return _speech_recognizer

def reset_speech_recognizer():
    """Reset the speech recognizer to ensure fresh recognition"""
    global _speech_recognizer
    _speech_recognizer = None

async def speak_text(text: str, force: bool = False) -> bool:
    """
    Speak text using ElevenLabs
    
    Args:
        text: Text to speak
        force: Speak even if speech is disabled
        
    Returns:
        bool: True if speech was played successfully
    """
    if not force and not _speech_config.enabled:
        return False
        
    speech = get_speech_instance()
    if speech:
        return await speech.speak(text, _speech_config.voice_settings)
    
    return False

def speak_text_sync(text: str, force: bool = False) -> bool:
    """
    Synchronous version of speak_text that can be called from non-async contexts
    
    Args:
        text: Text to speak
        force: Speak even if speech is disabled
        
    Returns:
        bool: True if speech was played successfully
    """
    if not force and not _speech_config.enabled:
        return False
        
    try:
        # Try to get existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, we need to create a new task
            # But since we're in sync context, we'll skip speech to avoid blocking
            print("⚠️ Speech skipped - in async context")
            return False
        else:
            # Loop exists but not running, we can use it
            return loop.run_until_complete(_async_speak_text(text, force))
    except RuntimeError:
        # No event loop exists, create a new one
        try:
            return asyncio.run(_async_speak_text(text, force))
        except Exception as e:
            logging.warning(f"Speech failed: {e}")
            return False

async def _async_speak_text(text: str, force: bool = False) -> bool:
    """Internal async version of speak_text"""
    if not force and not _speech_config.enabled:
        return False
        
    speech = get_speech_instance()
    if speech:
        return await speech.speak(text, _speech_config.voice_settings)
    
    return False

def get_user_input_with_voice(prompt: str = "Your response: ", voice_prompt: str = None) -> str:
    """
    Get user input with voice recognition as the default mode
    
    Args:
        prompt: Text prompt for typed input fallback
        voice_prompt: Optional different prompt for voice input
        
    Returns:
        User's input as text
    """
    # Get fresh recognizer for each input to prevent transcript caching
    recognizer = get_speech_recognizer()
    
    if recognizer and recognizer.is_available() and _speech_config.offer_voice_input:
        if _speech_config.voice_input_default:
            # Voice-first mode: Start listening immediately
            print(f"\n💬 🎤 Listening for your response... (say 'use text input' to switch to typing)")
            
            # Try voice input first (default mode)
            voice_text = recognizer.listen_for_speech(
                voice_prompt or "Please speak your response:",
                debug_audio=_speech_config.debug_audio
            )
            
            if voice_text:
                # Check if user requested text input mode
                if voice_text.lower() in ['use text input', 'text input', 'type', 'typing', 'keyboard']:
                    print("\n⌨️ Switching to text input:")
                    return input(prompt).strip()
                else:
                    return voice_text
            else:
                # Voice failed, offer options
                print("\n⚠️ Voice input failed. Would you like to:")
                print("   1. Try voice again (press Enter)")
                print("   2. Use text input (type anything)")
                
                fallback_choice = input("Your choice: ").strip()
                
                if not fallback_choice:  # Pressed Enter - try voice again
                    print("🎤 Trying voice input again...")
                    voice_text_retry = recognizer.listen_for_speech(
                        voice_prompt or "Please speak your response (second attempt):",
                        debug_audio=_speech_config.debug_audio
                    )
                    if voice_text_retry:
                        return voice_text_retry
                    else:
                        print("\n⌨️ Voice failed again. Falling back to text input:")
                        return input(prompt).strip()
                else:
                    # User chose text input
                    return fallback_choice
        else:
            # Original mode: Ask user to choose
            print(f"\n💬 You can:")
            print(f"   • Press Enter and speak your response")
            print(f"   • Type your response directly")
            
            # Get user choice
            user_choice = input("Press Enter to speak, or start typing: ").strip()
            
            if not user_choice:  # User pressed Enter without typing
                # Ensure fresh recognition by re-calibrating microphone
                print("🎤 Preparing to listen...")
                
                # Try voice input with debug audio if enabled
                voice_text = recognizer.listen_for_speech(
                    voice_prompt or "Please speak your response:",
                    debug_audio=_speech_config.debug_audio
                )
                
                if voice_text:
                    return voice_text
                else:
                    # Fallback to text input
                    print("\nFalling back to text input:")
                    return input(prompt).strip()
            else:
                # User started typing
                return user_choice
    else:
        # Voice not available, use text input only
        print("⌨️ Voice input not available. Using text input:")
        return input(prompt).strip()

def configure_speech(**kwargs):
    """Configure speech settings"""
    global _speech_config
    
    if 'enabled' in kwargs:
        _speech_config.enabled = kwargs['enabled']
    if 'voice_id' in kwargs:
        _speech_config.voice_id = kwargs['voice_id']
    if 'voice_settings' in kwargs:
        _speech_config.voice_settings.update(kwargs['voice_settings'])
    if 'speak_questions' in kwargs:
        _speech_config.speak_questions = kwargs['speak_questions']
    if 'speak_confirmations' in kwargs:
        _speech_config.speak_confirmations = kwargs['speak_confirmations']
    if 'speak_errors' in kwargs:
        _speech_config.speak_errors = kwargs['speak_errors']
    if 'listen_for_responses' in kwargs:
        _speech_config.listen_for_responses = kwargs['listen_for_responses']
    if 'offer_voice_input' in kwargs:
        _speech_config.offer_voice_input = kwargs['offer_voice_input']
    if 'recognition_timeout' in kwargs:
        _speech_config.recognition_timeout = kwargs['recognition_timeout']
    if 'debug_audio' in kwargs:
        _speech_config.debug_audio = kwargs['debug_audio']
    if 'voice_input_default' in kwargs:
        _speech_config.voice_input_default = kwargs['voice_input_default']