# Browser-Use Setup Guide

A step-by-step setup guide for **browser-use** using the recommended `uv` workflow.

**Requirements:** Python ≥ 3.11 (Python 3.12 recommended)

## Setup Steps

### 1. Prerequisites

Make sure you have **Python 3.11+** installed. If not, install from [python.org](https://python.org) or your OS package manager.

### 2. Install `uv` (one-time setup)

**Windows (PowerShell, run as Admin):**
```powershell
powershell -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"
```

*Alternative with winget:*
```powershell
winget install --id=astral-sh.uv -e
```

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installing, close and re-open your terminal, then verify:
```bash
uv --version
```

### 3. Create & activate virtual environment

From your project folder:
```bash
# Create venv using uv
uv venv --python 3.12
```

**Activate the environment:**

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

### 4. Install browser-use

```bash
uv pip install browser-use
```

### 5. Download Chromium browser

```bash
uvx playwright install chromium --with-deps --no-shell
```

### 6. Set up your API key

Create a `.env` file in your project root:
```
GEMINI_API_KEY=your_api_key_here
```

## Quick Setup Checklist

**Windows PowerShell:**
```powershell
# 1. Install uv (one-time)
powershell -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Create and activate venv
uv venv --python 3.12
.\.venv\Scripts\Activate.ps1

# 3. Install browser-use
uv pip install browser-use

# 4. Download Chromium
uvx playwright install chromium --with-deps --no-shell

# 5. Create .env file with your GEMINI_API_KEY
```

**macOS / Linux:**
```bash
# 1. Install uv (one-time)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create and activate venv
uv venv --python 3.12
source .venv/bin/activate

# 3. Install browser-use
uv pip install browser-use

# 4. Download Chromium
uvx playwright install chromium --with-deps --no-shell

# 5. Create .env file with your GEMINI_API_KEY
```

## Common Issues

- **`uv` command not found**: Close and re-open your terminal after installation
- **`playwright` not recognized**: Use `uvx playwright install ...` instead of `playwright install ...`
- **Permission errors**: Run PowerShell as Administrator on Windows

You're now ready to use browser-use! 🎉