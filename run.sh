#!/usr/bin/env bash
# Rocky x Auto-Clipper — one command:  ./run.sh
# Opens the localhost web UI at http://127.0.0.1:8000
set -e
cd "$(dirname "$0")"
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
# Muse VM: shared package dir with faster-whisper / cv2 / fastapi.
if [ -d "$HOME/workspace/pytools" ]; then
  export PYTHONPATH="$HOME/workspace/pytools:$PYTHONPATH"
fi
command -v ffmpeg >/dev/null 2>&1 || { echo "ffmpeg not found. Ubuntu: sudo apt install ffmpeg"; exit 1; }
command -v ffprobe >/dev/null 2>&1 || { echo "ffprobe not found (comes with ffmpeg)."; exit 1; }
exec python3 -m rockyx_clipper serve --port 8000
