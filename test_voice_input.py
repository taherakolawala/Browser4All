#!/usr/bin/env python3
"""
Test script for voice input functionality
Run this to verify that speech recognition is working before using the main agent.
"""

import sys
import os

def test_speech_recognition():
    """Test speech recognition setup"""
    print("🎤 Testing Speech Recognition Setup")
    print("=" * 40)
    
    try:
        import speech_recognition as sr
        print("✅ SpeechRecognition library imported successfully")
    except ImportError:
        print("❌ SpeechRecognition not installed. Run: pip install SpeechRecognition")
        return False
    
    try:
        import pyaudio
        print("✅ PyAudio imported successfully")
    except ImportError:
        print("❌ PyAudio not installed. Run: pip install pyaudio")
        print("   If Windows installation fails, try:")
        print("   pip install pipwin; pipwin install pyaudio")
        return False
    
    # Test microphone
    try:
        r = sr.Recognizer()
        mic = sr.Microphone()
        print("✅ Microphone detected")
        
        # Test ambient noise adjustment
        print("🔧 Calibrating microphone (please be quiet)...")
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=1)
        print("✅ Microphone calibrated")
        
        return True
        
    except Exception as e:
        print(f"❌ Microphone setup failed: {e}")
        return False

def test_voice_input():
    """Test actual voice recognition with audio debugging"""
    print("\n🎤 Testing Voice Recognition with Audio Debugging")
    print("=" * 50)
    
    try:
        from speech_handler import get_user_input_with_voice, configure_speech
        
        print("📝 This will test voice input with audio playback. You can:")
        print("   • Press Enter to test speaking (you'll hear what was recorded)")
        print("   • Type 'skip' to skip voice test")
        
        response = input("Press Enter to test voice, or type 'skip': ").strip().lower()
        
        if response == 'skip':
            print("⏭️ Voice test skipped")
            return True
        
        # Enable debug audio for testing
        configure_speech(debug_audio=True)
        
        print("\n🎤 Testing voice input with audio debugging...")
        print("📣 You will hear your recording played back after you speak!")
        result = get_user_input_with_voice(
            prompt="Voice test prompt: ",
            voice_prompt="Please say 'Hello Browser4All' for the voice test"
        )
        
        print(f"✅ Voice input result: '{result}'")
        return True
        
    except Exception as e:
        print(f"❌ Voice input test failed: {e}")
        return False

def test_text_to_speech():
    """Test text-to-speech functionality"""
    print("\n🔊 Testing Text-to-Speech")
    print("=" * 25)
    
    try:
        from speech_handler import speak_text_sync, configure_speech
        
        # Configure speech for testing
        configure_speech(
            enabled=True,
            speak_questions=True
        )
        
        print("🔊 Testing text-to-speech (you should hear audio)...")
        result = speak_text_sync("Hello! This is a test of the text to speech system.")
        
        if result:
            print("✅ Text-to-speech test successful")
        else:
            print("⚠️ Text-to-speech may not be working (check ElevenLabs API key)")
        
        return True
        
    except Exception as e:
        print(f"❌ Text-to-speech test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Browser4All Voice Input Test Suite")
    print("=" * 50)
    
    # Test basic setup
    if not test_speech_recognition():
        print("\n❌ Basic setup failed. Please install missing dependencies.")
        return
    
    # Test text-to-speech
    test_text_to_speech()
    
    # Test voice input
    test_voice_input()
    
    print("\n✅ Testing complete!")
    print("If all tests passed, your voice input system should work correctly.")
    print("Run 'python main.py' to start Browser4All with voice support.")

if __name__ == "__main__":
    main()