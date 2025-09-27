import os
import asyncio
import aiohttp
import pygame
import tempfile
from pathlib import Path
from typing import Optional
import logging

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
        
    def disable_speech(self):
        """Disable all speech"""
        self.enabled = False
        
    def enable_speech(self):
        """Enable speech"""
        self.enabled = True
        
    def set_voice(self, voice_id: str):
        """Change voice"""
        self.voice_id = voice_id


# Global speech instance - will be initialized when needed
_speech_instance: Optional[ElevenLabsSpeech] = None
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