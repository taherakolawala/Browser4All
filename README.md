# Browser4All 🤖🔊

An intelligent browser automation agent with natural speech interaction that asks clarifying questions instead of making assumptions.

## 🚀 Setup & Installation

### 1. Prerequisites
- **Python ≥ 3.11** (Python 3.12 recommended)
- **Git** for cloning the repository

### 2. Install Browser-Use Dependencies

**Install `uv` (recommended package manager):**

**Windows (PowerShell as Admin):**
```powershell
powershell -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installing, close and re-open your terminal, then verify:
```bash
uv --version
```

### 3. Project Setup

```bash
# Clone the repository
git clone https://github.com/taherakolawala/Browser4All.git
cd Browser4All

# Create virtual environment
uv venv --python 3.12

# Activate environment
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Install browser-use
uv pip install browser-use

# Install speech dependencies
uv pip install elevenlabs pygame aiohttp python-dotenv pydantic

# Download Chromium browser
uvx playwright install chromium --with-deps --no-shell
```

### 4. API Keys Configuration

Create a `.env` file in the project root:
```env
# OpenAI API Key (required for browser agent)
OPENAI_API_KEY=your_openai_api_key_here

# ElevenLabs API Key (required for speech)
ELEVEN_LABS_API_KEY=your_elevenlabs_api_key_here
```

**Get API Keys:**
- **OpenAI**: https://platform.openai.com/api-keys
- **ElevenLabs**: https://elevenlabs.io/ (free tier: 10,000 characters/month)

### 5. Run the Agent

```bash
python main.py
```

## ⚙️ Alternative Setup (without uv)

If you prefer not to use `uv`:

```bash
# Clone and enter directory
git clone https://github.com/taherakolawala/Browser4All.git
cd Browser4All

# Create virtual environment
python -m venv .venv

# Activate environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install browser-use elevenlabs pygame aiohttp python-dotenv pydantic

# Download Chromium
playwright install chromium
```

## 🎵 ElevenLabs Speech Configuration

### Voice Options
Default voice is **Bella** (soft, gentle female). To change the voice, edit `speech_handler.py`:

```python
# Available voices:
self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel - Pleasant female, clear
self.voice_id = "ErXwobaYiN019PkySvjV"  # Antoni - Calm male, professional  
self.voice_id = "EXAVITQu4vr4xnSDxMaL"  # Bella - Soft female, gentle (default)
self.voice_id = "yoZ06aMxZJJ28mfd3POQ"  # Sam - Natural male, conversational
self.voice_id = "pNInz6obpgDQGcFmaJgB"  # Adam - Friendly male, casual
```

### Speech Settings
In `main.py`, you can configure:
```python
configure_speech(
    enabled=True,           # Enable/disable speech
    speak_questions=True,   # Speak clarifying questions
    speak_confirmations=True, # Speak task completions
    speak_errors=False      # Don't speak error messages
)
```

## 🎯 How It Works

Browser4All asks clarifying questions instead of making assumptions:

1. **You type**: "reddit"
2. **Agent asks**: 🔊 "What would you like me to do on Reddit?"
3. **You respond**: "search for python tutorials"
4. **Agent acts**: Navigates, searches, then asks what to do next

## 📋 Example Usage

```bash
# Start the agent
python main.py

# Agent speaks: "Hello! What would you like me to help you with?"
# You type: find information
# Agent asks: "What specific information and from which source?"
# You type: latest iPhone price from Apple website
# Agent navigates to Apple, finds iPhone, then asks what to do next
```

## 🔧 Troubleshooting

### Common Issues

**`uv` command not found:**
- Close and re-open your terminal after installation
- On Windows, run PowerShell as Administrator

**No Audio Output:**
- Check speakers/headphones and volume
- Verify `ELEVEN_LABS_API_KEY` in `.env` file
- Test with: `python -c "import pygame; pygame.mixer.init(); print('Audio system OK')"`

**Chromium Installation Errors:**
- Try: `uvx playwright install chromium --force`
- On Linux: `sudo apt-get install libnss3 libatk-bridge2.0-0 libxcomposite1`

**Agent Not Asking Questions:**
- Ensure `speech_handler.py` is in the same directory as `main.py`
- Check that both API keys are set correctly in `.env`

**Event Loop Errors:**
- The agent uses synchronous speech to avoid asyncio conflicts
- If errors persist, set `enabled=False` in `configure_speech()`

### Cost Management

**ElevenLabs Usage:**
- Free tier: 10,000 characters/month
- Typical question: 50-200 characters
- Monitor usage at: https://elevenlabs.io/usage

**OpenAI Usage:**
- GPT-4.1-mini recommended for cost efficiency
- Typical session: $0.01-0.05 per task

## 🚀 Quick Start Commands

```bash
# Complete setup (Windows)
git clone https://github.com/taherakolawala/Browser4All.git
cd Browser4All
powershell -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"
# Restart terminal
uv venv --python 3.12
.\.venv\Scripts\Activate.ps1
uv pip install browser-use elevenlabs pygame aiohttp python-dotenv pydantic
uvx playwright install chromium --with-deps --no-shell
# Add API keys to .env file
python main.py
```

---

**Browser4All** - Smart browser automation with natural speech interaction 🚀