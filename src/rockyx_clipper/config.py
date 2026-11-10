"""Rockyx Auto-Clipper — shared paths and defaults.

Cross-platform: all paths via pathlib, ffmpeg resolved from PATH
(Windows: winget install ffmpeg / choco install ffmpeg; Ubuntu: apt install ffmpeg).
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

VERSION = "0.1.0"

ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = ROOT / "src" / "rockyx_clipper"
MODELS_DIR = ROOT / "models"
PROMPTS_DIR = ROOT / "prompts"
OUTPUT_DIR = ROOT / "output"
JOBS_DIR = ROOT / "jobs"
YUNET_MODEL = MODELS_DIR / "yunet_2023mar.onnx"

# Whisper model: "base" is multilingual, "base.en" is English-only and faster.
# On CPU-only machines base/small are the sane choices; "small" is ~2x slower.
DEFAULT_WHISPER_MODEL = "base"
DEFAULT_LANGUAGE = "en"  # "auto" = let Whisper detect

# Clip defaults (paid tools use 15-60s; Opus/Vizard sweet spot is 30-60s)
DEFAULT_NUM_CLIPS = 3
DEFAULT_MIN_CLIP_S = 30
DEFAULT_MAX_CLIP_S = 60
DEFAULT_CAPTION_STYLE = "hormozi"

# Export spec: 1080x1920, H.264 crf 18, AAC, -16 LUFS
EXPORT_WIDTH = 1080
EXPORT_HEIGHT = 1920
EXPORT_CRF = 18
TARGET_LUFS = -16.0

# Gemini (vault credential) — key is NEVER in files, args, env or logs.
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-3.8-flash"]


def ffmpeg_bin() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    env = os.environ.get("FFMPEG_PATH")
    if env and Path(env).exists():
        return env
    return "ffmpeg"


def ffprobe_bin() -> str:
    found = shutil.which("ffprobe")
    if found:
        return found
    env = os.environ.get("FFPROBE_PATH")
    if env and Path(env).exists():
        return env
    return "ffprobe"


def ytdlp_bin() -> str:
    found = shutil.which("yt-dlp")
    if found:
        return found
    return "yt-dlp"
