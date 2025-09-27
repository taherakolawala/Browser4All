@echo off
echo Installing Speech Dependencies for Browser Agent
echo ============================================

echo.
echo Installing Python packages...
pip install elevenlabs pygame aiohttp

echo.
echo Installation complete!
echo.
echo Next steps:
echo 1. Get an ElevenLabs API key from https://elevenlabs.io/
echo 2. Add it to your .env file as ELEVEN_LABS_API_KEY=your_key_here
echo 3. Run: python test_speech.py to test the setup
echo 4. Run: python main.py to use the speaking agent
echo.
pause