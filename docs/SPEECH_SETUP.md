# Speech-Enabled Browser Agent Setup

## Prerequisites

1. **ElevenLabs API Key**: Get one from https://elevenlabs.io/
2. **Python Packages**: Install the required dependencies

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r speech_requirements.txt
```

### 2. Set Environment Variables
Add to your `.env` file:
```env
ELEVEN_LABS_API_KEY=your_elevenlabs_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Test Speech
```bash
python test_speech.py
```

### 4. Run Main Agent
```bash
python main.py
```

## Voice Options

The agent uses Rachel (pleasant female voice) by default. You can change voices by modifying the `voice_id` in `speech_handler.py`.

Available voices:
- **Rachel** (21m00Tcm4TlvDq8ikWAM) - Pleasant female, clear
- **Antoni** (ErXwobaYiN019PkySvjV) - Calm male, professional  
- **Bella** (EXAVITQu4vr4xnSDxMaL) - Soft female, gentle
- **Sam** (yoZ06aMxZJJ28mfd3POQ) - Natural male, conversational
- **Adam** (pNInz6obpgDQGcFmaJgB) - Friendly male, casual

## Speech Configuration

In `main.py`, you can configure:
```python
configure_speech(
    enabled=True,           # Enable/disable speech
    speak_questions=True,   # Speak clarifying questions
    speak_confirmations=True, # Speak task completions
    speak_errors=False      # Don't speak errors (usually)
)
```

## Troubleshooting

### No Audio Output
- Check your system audio/speakers
- Verify pygame is installed correctly
- Try running `test_speech.py` 

### ElevenLabs API Errors
- Verify your API key is correct
- Check your ElevenLabs account balance
- Ensure you have an active subscription

### Speech Too Slow/Fast
Modify voice settings in `speech_handler.py`:
```python
voice_settings = {
    "stability": 0.75,      # 0-1, higher = more stable
    "similarity_boost": 0.8, # 0-1, higher = more like original
    "style": 0.2,           # 0-1, lower = more natural
}
```

## Cost Management

ElevenLabs charges per character:
- Free tier: 10,000 characters/month
- Starter: $5/month for 30,000 characters
- Creator: $22/month for 100,000 characters

The agent typically uses 50-200 characters per question, so even the free tier should handle hundreds of interactions.