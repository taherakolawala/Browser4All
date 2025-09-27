#!/usr/bin/env python3
"""
Microphone Detection Tool
Shows all available microphones and identifies which one is being used for recording.
"""

import speech_recognition as sr
import pyaudio
import sys

def list_all_microphones():
    """List all available audio input devices"""
    print("🎤 Available Audio Input Devices")
    print("=" * 40)
    
    try:
        # Initialize PyAudio to get device info
        p = pyaudio.PyAudio()
        
        device_count = p.get_device_count()
        input_devices = []
        
        for i in range(device_count):
            device_info = p.get_device_info_by_index(i)
            
            # Only show input devices (microphones)
            if device_info['maxInputChannels'] > 0:
                input_devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxInputChannels'],
                    'sample_rate': int(device_info['defaultSampleRate']),
                    'is_default': i == p.get_default_input_device_info()['index']
                })
        
        p.terminate()
        
        if not input_devices:
            print("❌ No microphones found!")
            return None
            
        # Display all input devices
        for i, device in enumerate(input_devices):
            default_marker = " (DEFAULT)" if device['is_default'] else ""
            print(f"{device['index']:2d}: {device['name']}{default_marker}")
            print(f"     Channels: {device['channels']}, Sample Rate: {device['sample_rate']} Hz")
        
        return input_devices
        
    except Exception as e:
        print(f"❌ Error listing microphones: {e}")
        return None

def get_speech_recognition_microphone():
    """Get the microphone that speech_recognition will use"""
    print("\n🎙️ Speech Recognition Microphone")
    print("=" * 35)
    
    try:
        # Create a recognizer and microphone instance
        r = sr.Recognizer()
        
        # Get default microphone
        mic = sr.Microphone()
        
        print(f"Device Index: {mic.device_index}")
        
        # Get device info using PyAudio
        p = pyaudio.PyAudio()
        
        if mic.device_index is None:
            # Using system default
            default_device = p.get_default_input_device_info()
            device_info = default_device
            print("Using: System Default Microphone")
        else:
            # Using specific device index
            device_info = p.get_device_info_by_index(mic.device_index)
            print(f"Using: Device #{mic.device_index}")
        
        print(f"Name: {device_info['name']}")
        print(f"Channels: {device_info['maxInputChannels']}")
        print(f"Sample Rate: {int(device_info['defaultSampleRate'])} Hz")
        
        p.terminate()
        
        return device_info
        
    except Exception as e:
        print(f"❌ Error getting speech recognition microphone: {e}")
        return None

def test_microphone_recording():
    """Test if the microphone can record audio"""
    print("\n🔬 Microphone Test")
    print("=" * 18)
    
    try:
        r = sr.Recognizer()
        mic = sr.Microphone()
        
        print("🔧 Calibrating microphone...")
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=1)
        
        print("✅ Microphone calibration successful")
        print("🎤 Testing audio capture (2 seconds)...")
        
        with mic as source:
            audio = r.listen(source, timeout=1, phrase_time_limit=2)
        
        print("✅ Audio capture successful")
        print(f"📊 Audio data size: {len(audio.get_wav_data())} bytes")
        
        return True
        
    except sr.WaitTimeoutError:
        print("⚠️ No audio detected (this is normal if you didn't speak)")
        return True
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False

def show_microphone_usage_in_browser4all():
    """Show which microphone Browser4All will use"""
    print("\n🤖 Browser4All Microphone Usage")
    print("=" * 32)
    
    try:
        # Import our speech handler to see what it detects
        from speech_handler import SpeechRecognizer
        
        recognizer = SpeechRecognizer()
        
        if recognizer.microphone is None:
            print("❌ Browser4All cannot detect a microphone")
            return False
        else:
            print("✅ Browser4All can use microphone")
            
            # Get the device index that our recognizer is using
            device_index = recognizer.microphone.device_index
            
            p = pyaudio.PyAudio()
            
            if device_index is None:
                device_info = p.get_default_input_device_info()
                print("Using: System Default Microphone")
            else:
                device_info = p.get_device_info_by_index(device_index)
                print(f"Using: Device #{device_index}")
            
            print(f"Name: {device_info['name']}")
            print(f"Channels: {device_info['maxInputChannels']}")
            
            p.terminate()
            return True
            
    except ImportError:
        print("⚠️ Browser4All speech_handler not available")
        print("   (This is normal if you're not in the Browser4All directory)")
        return False
    except Exception as e:
        print(f"❌ Error checking Browser4All microphone: {e}")
        return False

def main():
    """Main function to display all microphone information"""
    print("🎤 Microphone Detection and Analysis Tool")
    print("=" * 50)
    print()
    
    # List all available microphones
    devices = list_all_microphones()
    
    if devices is None:
        print("Cannot continue without microphone devices.")
        return
    
    # Show which one speech_recognition uses
    get_speech_recognition_microphone()
    
    # Test microphone functionality
    test_microphone_recording()
    
    # Show Browser4All specific usage
    show_microphone_usage_in_browser4all()
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print(f"   • Found {len(devices)} microphone(s)")
    
    default_devices = [d for d in devices if d['is_default']]
    if default_devices:
        print(f"   • Default: {default_devices[0]['name']}")
    
    print("   • Speech recognition: Ready")
    print("\n💡 Tip: If you have multiple microphones, the default one will be used.")
    print("    You can change the default microphone in Windows Sound settings.")

if __name__ == "__main__":
    main()