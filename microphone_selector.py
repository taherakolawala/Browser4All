#!/usr/bin/env python3
"""
Microphone Selector Tool
Allows you to choose which microphone to use for Browser4All voice input.
"""

import speech_recognition as sr
import pyaudio
import sys

def list_microphones():
    """List available microphones with their indices"""
    print("🎤 Available Microphones")
    print("=" * 25)
    
    try:
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
        
        # Show Realtek devices prominently
        realtek_devices = [d for d in input_devices if 'Realtek' in d['name']]
        other_devices = [d for d in input_devices if 'Realtek' not in d['name']]
        
        print("🔊 Realtek Audio Devices:")
        for device in realtek_devices:
            default_marker = " (CURRENT DEFAULT)" if device['is_default'] else ""
            print(f"  {device['index']:2d}: {device['name']}{default_marker}")
            print(f"      Channels: {device['channels']}, Sample Rate: {device['sample_rate']} Hz")
        
        print("\n🎤 Other Microphones:")
        for device in other_devices:
            default_marker = " (CURRENT DEFAULT)" if device['is_default'] else ""
            print(f"  {device['index']:2d}: {device['name']}{default_marker}")
            print(f"      Channels: {device['channels']}, Sample Rate: {device['sample_rate']} Hz")
        
        return input_devices
        
    except Exception as e:
        print(f"❌ Error listing microphones: {e}")
        return []

def test_microphone(device_index):
    """Test a specific microphone"""
    print(f"\n🔬 Testing microphone {device_index}...")
    
    try:
        # Create microphone with specific device index
        r = sr.Recognizer()
        mic = sr.Microphone(device_index=device_index)
        
        print("🔧 Calibrating microphone...")
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=1)
        
        print("✅ Microphone calibration successful")
        print("🎤 Testing audio capture (say something for 2 seconds)...")
        
        with mic as source:
            audio = r.listen(source, timeout=3, phrase_time_limit=2)
        
        print("✅ Audio capture successful")
        print(f"📊 Audio data size: {len(audio.get_wav_data())} bytes")
        
        # Try to recognize what was said
        try:
            text = r.recognize_google(audio)
            print(f"🎯 Recognized: '{text}'")
        except sr.UnknownValueError:
            print("🤷 Could not understand audio (but capture worked)")
        except sr.RequestError:
            print("⚠️ Speech recognition service unavailable (but capture worked)")
        
        return True
        
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False

def create_custom_speech_handler():
    """Create a custom speech handler with selected microphone"""
    devices = list_microphones()
    
    if not devices:
        print("❌ No microphones found!")
        return
    
    # Find Realtek devices
    realtek_devices = [d for d in devices if 'Realtek' in d['name'] and 'Array' in d['name']]
    
    if realtek_devices:
        print(f"\n💡 Recommended Realtek microphones:")
        for device in realtek_devices:
            print(f"   Device {device['index']}: {device['name']}")
    
    print("\n🎯 Choose your microphone:")
    print("   • Enter device number to select")
    print("   • Press Enter to use current default")
    print("   • Type 'quit' to exit")
    
    choice = input("\nYour choice: ").strip()
    
    if choice.lower() == 'quit':
        return
    
    if choice == '':
        print("Using current default microphone")
        device_index = None
    else:
        try:
            device_index = int(choice)
            # Validate device exists
            valid_indices = [d['index'] for d in devices]
            if device_index not in valid_indices:
                print(f"❌ Invalid device index. Available: {valid_indices}")
                return
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            return
    
    # Test the selected microphone
    if device_index is not None:
        selected_device = next((d for d in devices if d['index'] == device_index), None)
        print(f"\n🎤 Selected: {selected_device['name']}")
        
        if not test_microphone(device_index):
            print("❌ Microphone test failed. Please try another device.")
            return
    
    # Generate code for Browser4All
    print("\n" + "="*50)
    print("📝 To use this microphone in Browser4All:")
    print("="*50)
    
    if device_index is None:
        print("✅ You're using the default microphone (no changes needed)")
    else:
        print(f"Add this code to your speech_handler.py:")
        print()
        print("```python")
        print("# In the SpeechRecognizer.__init__ method, change:")
        print("# self.microphone = sr.Microphone()")
        print("# to:")
        print(f"self.microphone = sr.Microphone(device_index={device_index})")
        print("```")
        print()
        print("Or use the automatic update option below...")
    
    return device_index

def update_speech_handler_automatically(device_index):
    """Automatically update speech_handler.py with new microphone"""
    if device_index is None:
        print("No changes needed for default microphone.")
        return
    
    try:
        # Read current speech_handler.py
        with open('speech_handler.py', 'r') as f:
            content = f.read()
        
        # Replace microphone initialization
        old_line = "self.microphone = sr.Microphone()"
        new_line = f"self.microphone = sr.Microphone(device_index={device_index})"
        
        if old_line in content:
            updated_content = content.replace(old_line, new_line)
            
            # Write back to file
            with open('speech_handler.py', 'w') as f:
                f.write(updated_content)
            
            print(f"✅ Updated speech_handler.py to use microphone {device_index}")
            print("🔄 Restart your Browser4All application to use the new microphone")
        else:
            print("⚠️ Could not find microphone initialization line in speech_handler.py")
            print("You may need to update it manually.")
        
    except Exception as e:
        print(f"❌ Error updating speech_handler.py: {e}")

def main():
    """Main microphone selection interface"""
    print("🎤 Microphone Selector for Browser4All")
    print("=" * 40)
    
    device_index = create_custom_speech_handler()
    
    if device_index is not None:
        print("\n🔧 Would you like to automatically update Browser4All?")
        update_choice = input("Update speech_handler.py automatically? (y/n): ").strip().lower()
        
        if update_choice == 'y':
            update_speech_handler_automatically(device_index)
        else:
            print("📝 Manual update instructions provided above.")

if __name__ == "__main__":
    main()