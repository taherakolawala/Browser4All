```
 __________                                            _____    _____  .__  .__   
 \______   \_______  ______  _  ________ ___________  /  |  |  /  _  \ |  | |  |  
  |    |  _/\_  __ \/  _ \ \/ \/ /  ___// __ \_  __ \/   |  |_/  /_\  \|  | |  |  
  |    |   \ |  | \(  <_> )     /\___ \\  ___/|  | \/    ^   /    |    \  |_|  |__
  |______  / |__|   \____/ \/\_//____  >\___  >__|  \____   |\____|__  /____/____/
         \/                          \/     \/           |__|        \/            
```

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![ShellHacks](https://img.shields.io/badge/ShellHacks_2024-Semifinalist-orange)
![License](https://img.shields.io/badge/license-MIT-green)

**ShellHacks 2025 Semifinalist**

A hands-free, multi-lingual AI browser agent built for accessibility. Speak any command in your language and watch the browser act. Designed for users who can't easily use a keyboard or mouse.

Built with: Python, OpenAI GPT-4.1, ElevenLabs TTS, Playwright, browser-use

---

## Features

- Voice-controlled browser automation (Google, Amazon, Reddit, YouTube, etc.)
- Multi-language speech recognition
- Transparent hovering UI overlay with real-time activity logs
- Automatic fallback from voice to text input
- Color-coded message categorization (questions, errors, confirmations)

---

## Setup

### Requirements
- Python >= 3.11
- Microphone (for voice input)
- OpenAI API key
- ElevenLabs API key

### Install

```bash
git clone https://github.com/taherakolawala/Browser4All.git
cd Browser4All
```

**Install `uv` (recommended package manager):**

Windows (PowerShell as Admin):
```powershell
powershell -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS / Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart terminal after installing, then:

```bash
uv venv --python 3.12

# Windows:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

uv pip install browser-use elevenlabs pygame aiohttp python-dotenv pydantic SpeechRecognition pyaudio
uvx playwright install chromium --with-deps --no-shell
```

### API Keys

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
ELEVEN_LABS_API_KEY=your_elevenlabs_api_key_here
```

- OpenAI: https://platform.openai.com/api-keys
- ElevenLabs: https://elevenlabs.io (free tier: 10,000 chars/month)

### Run

```bash
python launcher.py
```

Select your language and the agent launches. A transparent overlay appears in the top-right corner showing all activity.

---

## Optional: Microphone Setup

```bash
python tools/microphone_selector.py
```

Use this to pick the right device and test recording quality before running the agent.

---

## Alternative Setup (without uv)

```bash
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r speech_requirements.txt
pip install browser-use
playwright install chromium --with-deps
```

---

## Configuration

### Voice Settings

In `main.py`:

```python
configure_speech(
    enabled=True,
    speak_questions=True,
    listen_for_responses=True,
    voice_input_default=True,
    recognition_timeout=10,
    phrase_timeout=6
)
```

### Change Voice

In `speech_handler.py`:

```python
self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel (default)
self.voice_id = "ErXwobaYiN019PkySvjV"  # Antoni
self.voice_id = "EXAVITQu4vr4xnSDxMaL"  # Bella
```

### Browser Window

In `main.py`:

```python
browser = Browser(
    window_size={'width': 1920, 'height': 1080},
    window_position={'width': 100, 'height': 50},
    headless=False
)
```

---

## Troubleshooting

**`uv` not found:** Restart terminal after installing.

**Chromium install fails:**
```bash
uvx playwright install chromium --force
# Linux: sudo apt-get install libnss3 libatk-bridge2.0-0 libxcomposite1 libdrm2
```

**PyAudio errors (Windows):**
```bash
pip install pipwin && pipwin install pyaudio
```

**No speech output:** Check `ELEVEN_LABS_API_KEY` in `.env` and verify speakers.

**UI not showing:** Run `python -c "import tkinter; print('OK')"`. Linux: `sudo apt-get install python3-tk`.

**Voice not recognized:** Run `python tools/microphone_selector.py` and increase `recognition_timeout` to 15+.

---

## Cost Estimate

| Service | Free Tier | Paid |
|---|---|---|
| ElevenLabs | 10,000 chars/month | $5/mo for 30k |
| OpenAI (GPT-4.1-mini) | N/A | ~$0.01-0.05/session |

Typical usage: $0-10/month.
