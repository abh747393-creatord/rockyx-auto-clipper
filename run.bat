@echo off
REM Rocky x Auto-Clipper — one command:  run.bat
REM Opens the localhost web UI at http://127.0.0.1:8000
REM Needs: Python 3.10+ (python.org, tick "Add python.exe to PATH")
REM        ffmpeg in PATH (winget install Gyan.FFmpeg  OR  choco install ffmpeg)
REM        pip install -r requirements.txt  (once)
set PYTHONPATH=%~dp0src;%PYTHONPATH%
python -m rockyx_clipper serve --port 8000
pause
