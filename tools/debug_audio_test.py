#!/usr/bin/env python3
"""
Quick debug audio test - just tests the audio recording and playback
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_debug_audio():
    """Test debug audio recording and playback"""
    print("🎤 Debug Audio Test - Record and Playback")
    print("=" * 45)
    
    try:
        from speech_handler import configure_speech, get_user_input_with_voice
        
        # Enable debug audio
        configure_speech(
            enabled=False,  # Disable TTS to focus on recording
            listen_for_responses=True,
            debug_audio=True,  # This is what we're testing!
            recognition_timeout=5  # Shorter timeout for testing
        )
        
        print("🔧 Debug audio is ENABLED - you will hear your recording played back!")
        print("📝 This test will:")
        print("   1. Record your voice for up to 5 seconds")
        print("   2. Save the recording to a temporary file")
        print("   3. Play it back so you can hear what was captured")
        print("   4. Process the speech recognition")
        
        input("\nPress Enter when ready to start the test...")
        
        print("\n🎤 Starting debug audio test...")
        result = get_user_input_with_voice(
            prompt="Debug test complete. Result: ",
            voice_prompt="Please say 'This is a debug audio test' clearly"
        )
        
        print(f"\n✅ Test completed!")
        print(f"📝 Recognized text: '{result}'")
        print("🔊 Did you hear the playback of your recording? That's the debug feature!")
        
    except Exception as e:
        print(f"❌ Debug audio test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_debug_audio()