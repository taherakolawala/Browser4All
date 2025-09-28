# Browser4All
A multi-lingual hands-free speech-to-action AI browser agent. Made to truly expand internet accessbility to all people.

## Setup & Installation

### 1. Prerequisites
- **Python ≥ 3.11** (Python 3.12 recommended)
- **Git** for cloning the repository
- **Microphone** for voice input (optional but recommended)

### 2. Install Package Manager

**Install `uv` (recommended):**

**Windows (PowerShell as Admin):**
```powershell
powershell -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installing, **restart your terminal** and verify:
```bash
uv --version
```

### 3. Project Installation

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

# Install all dependencies (includes tkinter for UI)
uv pip install browser-use elevenlabs pygame aiohttp python-dotenv pydantic SpeechRecognition pyaudio

# Download Chromium browser
uvx playwright install chromium --with-deps --no-shell
```

### 4. API Keys Setup

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

### 5. Microphone Setup (Optional)

**Test your microphone:**
```bash
python microphone_selector.py
```

This will help you:
- Select the correct microphone device
- Test audio recording quality
- Automatically configure speech settings

### 6. Run Browser4All

```bash
python main.py
```

The agent will:
-  **Launch the hovering UI** in the top-right corner of your screen
-  **Greet you with speech** and wait for your voice or text input
-  **Display all activity** in the transparent interface above your browser

##  Alternative Setup (without uv)

If you prefer traditional pip:

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
pip install -r speech_requirements.txt
pip install browser-use

# Download Chromium
playwright install chromium --with-deps
```

##  Speech & Voice Configuration

### Voice Input Settings
Voice input is **enabled by default**. The agent will:
- Listen for your voice responses automatically
- Fall back to text input if voice fails
- Allow you to say "use text input" to switch modes

Configure in [`main.py`](main.py):
```python
configure_speech(
    enabled=True,              # Enable text-to-speech
    speak_questions=True,      # Agent speaks questions aloud
    speak_confirmations=True,  # Agent speaks confirmations
    listen_for_responses=True, # Voice input enabled (NEW!)
    voice_input_default=True,  # Voice is primary input mode (NEW!)
    recognition_timeout=10,    # Voice timeout (seconds)
    debug_audio=True,          # Hear what was recorded (NEW!)
    phrase_timeout=6           # Silence duration to end recording (NEW!)
)
```

### Voice Options
Default voice is **Rachel**. To change, edit [`speech_handler.py`](speech_handler.py):

```python
# Popular voice options:
self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel - Pleasant female (default)
self.voice_id = "ErXwobaYiN019PkySvjV"  # Antoni - Calm male
self.voice_id = "EXAVITQu4vr4xnSDxMaL"  # Bella - Soft female
self.voice_id = "yoZ06aMxZJJ28mfd3POQ"  # Sam - Natural male
self.voice_id = "pNInz6obpgDQGcFmaJgB"  # Adam - Friendly male
```

### Recording Duration Control
The microphone recording duration is controlled by:
- **`phrase_timeout`**: Seconds of silence to end recording (default: 4 seconds)
- **`recognition_timeout`**: Max seconds to wait for speech to start (default: 10 seconds)

To change recording length:
```python
# In main.py configure_speech()
phrase_timeout=8,  # Allow 8 seconds of silence before ending
```

## Browser Configuration

### Window Size & Position
Configure browser appearance in [`main.py`](main.py):

```python
browser = Browser(
    window_size={'width': 1920, 'height': 1080},    # Browser window size
    window_position={'width': 100, 'height': 50},   # Position from top-left
    headless=False,                                  # Show browser window
    viewport={'width': 1280, 'height': 720}         # Content area size
)
```

**Common sizes:**
```python
# Full HD
window_size={'width': 1920, 'height': 1080}

# Laptop standard  
window_size={'width': 1366, 'height': 768}

# Compact window (current default)
window_size={'width': 960, 'height': 540}
```

### Advanced Browser Settings
```python
browser = Browser(
    # Display
    headless=False,                    # Show browser window
    window_size={'width': 1200, 'height': 800},
    
    # Downloads
    accept_downloads=True,             # Auto-accept downloads
    downloads_path='./downloads',      # Download directory
    auto_download_pdfs=True,          # Auto-download PDFs
    
    # Recording & Debugging
    record_video_dir='./recordings',   # Save session videos
    record_har_path='./trace.har',    # Save network traces
    
    # Device Emulation
    user_agent='Mozilla/5.0...',      # Custom user agent
)
```

##  Hovering UI Interface

Browser4All features a **transparent hovering interface** that displays all agent activity in real-time:

- **Transparent overlay**: Hovers above the browser window with customizable opacity
- **Real-time updates**: Shows all terminal output, questions, responses, and agent actions
- ** Color-coded messages**: Questions (blue), success (green), warnings (yellow), errors (red)
- **Draggable & resizable**: Click and drag to reposition, minimize/maximize controls
- **Timestamped logs**: Each message includes timestamp for tracking
- **Always on top**: Stays visible above the browser for continuous monitoring

### UI Configuration
Customize the hovering interface in [`main.py`](main.py):

```python
# Initialize with custom settings
initialize_ui(
    width=500,        # Window width in pixels
    height=400,       # Window height in pixels  
    opacity=0.88      # Transparency (0.0-1.0, higher = more opaque)
)
```

The UI automatically:
- **Positions** in the top-right corner by default
- **Categorizes** messages by content and emoji
- **Auto-scrolls** to show latest activity
- **Manages memory** by limiting stored messages
- **Shuts down** cleanly when the agent exits

## 🎯 How It Works

Browser4All uses **voice-first interaction** with **visual feedback**:

1. **Agent greets you**:  "Hello! What would you like me to help you with?" (appears in hovering UI)
2. **You speak**: "Go to YouTube and search for cat videos" (logged in UI)
3. **Agent acts**: Navigates to YouTube, searches (progress shown in UI)
4. **Agent asks**:  "I found cat videos. What would you like me to do next?" (question highlighted in blue)
5. **You respond**: Voice or text - "Play the first video" (response logged in purple)

### 🎤 Voice Features
- **Automatic microphone calibration** for optimal recording
- **Smart fallback**: Switches to text if voice fails
- **Flexible input**: Say "use text input" to switch modes anytime
- **Debug mode**: Hear your recorded audio played back
- **Visual feedback**: All voice interactions logged in hovering UI

###  UI Features
- **Real-time monitoring**: See all agent activity as it happens
- **Message categorization**: Color-coded by type (questions, responses, errors, etc.)
- **Persistent display**: Stays visible above browser window
- **Interactive controls**: Drag to move, minimize/close buttons
- **Memory efficient**: Auto-manages message history

##  Quick Start Examples

```bash
# Open the launcher:
python launcher.py
```

**Example interactions** (all displayed in real-time UI):
```
[UI] 🚀 Browser4All Assistant Started
[UI] 🔊 Speaking greeting...
You (voice): "reddit"
[UI] 🤔 Agent asks: "What would you like me to do on Reddit?"
You (voice): "find funny posts"  
[UI] 📍 Agent navigating to Reddit...
[UI] ✅ Found funny posts, asking what's next

You (voice): "amazon"
[UI] 🤔 Agent asks: "What would you like me to search for on Amazon?"
You (voice): "wireless headphones under 100 dollars"
[UI] 📍 Searching Amazon...
[UI] ✅ Found results, asking if you want details
```

## 🔧 Installation Troubleshooting

### Package Manager Issues
**`uv` command not found:**
- **Restart your terminal** after installation
- Windows: Run PowerShell as Administrator
- Verify installation: `uv --version`

**Permission errors:**
- Windows: Use PowerShell as Administrator
- macOS/Linux: Don't use `sudo` with uv

### Dependencies
**Chromium installation fails:**
```bash
# Force reinstall
uvx playwright install chromium --force

# Linux additional deps
sudo apt-get install libnss3 libatk-bridge2.0-0 libxcomposite1 libdrm2
```

**PyAudio installation errors:**
```bash
# Windows (if pip fails)
pip install pipwin
pipwin install pyaudio

# Or download wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
```

### Audio Issues
**No speech output:**
- Check volume and speakers/headphones
- Verify `ELEVEN_LABS_API_KEY` in `.env`
- Test: `python -c "import pygame; pygame.mixer.init(); print('Audio OK')"`

**UI not appearing:**
- Check if `tkinter` is installed: `python -c "import tkinter; print('UI OK')"`
- Windows: tkinter included with Python
- Linux: `sudo apt-get install python3-tk`
- Verify screen resolution supports UI positioning

**No microphone input:**
- Check microphone permissions in system settings
- Run `python microphone_selector.py` to test
- Ensure microphone isn't being used by other apps

**Voice recognition fails:**
- Speak clearly with minimal background noise
- Increase `recognition_timeout` to 15+ seconds
- Set `debug_audio=True` to hear recorded audio quality

### API Key Issues
**Invalid OpenAI key:**
- Verify key format: `sk-...` (starts with sk-)
- Check billing status: https://platform.openai.com/usage

**ElevenLabs quota exceeded:**
- Check usage: https://elevenlabs.io/usage
- Free tier: 10,000 characters/month
- Consider upgrading or disable speech: `enabled=False`

##  One-Command Setup

**Windows (complete setup):**
```powershell
# Run in PowerShell as Admin
git clone https://github.com/taherakolawala/Browser4All.git; cd Browser4All; powershell -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"
# Restart terminal, then:
uv venv --python 3.12; .\.venv\Scripts\Activate.ps1; uv pip install browser-use elevenlabs pygame aiohttp python-dotenv pydantic SpeechRecognition pyaudio; uvx playwright install chromium --with-deps --no-shell
# Add API keys to .env file, then: python main.py
```

**macOS/Linux (complete setup):**
```bash
git clone https://github.com/taherakolawala/Browser4All.git && cd Browser4All && curl -LsSf https://astral.sh/uv/install.sh | sh
# Restart terminal, then:
source ~/.bashrc && uv venv --python 3.12 && source .venv/bin/activate && uv pip install browser-use elevenlabs pygame aiohttp python-dotenv pydantic SpeechRecognition pyaudio && uvx playwright install chromium --with-deps --no-shell
# Add API keys to .env file, then: python main.py
```

##  Cost Management

**ElevenLabs (Speech):**
- Free tier: 10,000 characters/month (~200 questions)
- Paid: $5/month for 30,000 characters
- Monitor at: https://elevenlabs.io/usage

**OpenAI (AI Brain):**
- GPT-4.1-mini recommended: ~$0.01-0.05 per session
- Monitor at: https://platform.openai.com/usage

**Total typical cost: $0-10/month** depending on usage.

##  New Features

### Hovering UI Interface
- ** Real-time visual feedback** of all agent activity
- ** Transparent overlay** that hovers above your browser
- ** Color-coded messages** for easy tracking
- ** Interactive controls** - drag, minimize, close
- ** Timestamped logs** for session tracking

### Enhanced Integration
All terminal output automatically appears in both:
- ** Terminal** - Traditional command line output
- ** Hovering UI** - Visual overlay with timestamps and colors

---

**Browser4All** - Voice-controlled browser automation with visual feedback 🎤🤖📺
