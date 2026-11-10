"""Rockyx Auto-Clipper — shared paths and defaults.

Cross-platform: all paths via pathlib, ffmpeg resolved from PATH
(Windows: winget install ffmpeg / choco install ffmpeg; Ubuntu: apt install ffmpeg).
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

VERSION = "0.1.7"

ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = ROOT / "src" / "rockyx_clipper"
MODELS_DIR = ROOT / "models"
PROMPTS_DIR = ROOT / "prompts"
OUTPUT_DIR = ROOT / "output"
JOBS_DIR = ROOT / "jobs"
FONTS_DIR = ROOT / "fonts"
YUNET_MODEL = MODELS_DIR / "yunet_2023mar.onnx"

# Bundled caption fonts — 22 free OFL Google Fonts, shipped in fonts/ so they
# work on any machine with no install. Key = the ASS font name (the TTF's
# nameID 1, exactly what libass matches); value = the file in fonts/.
# libass finds them via the subtitles filter's fontsdir (see render.py).
FONTS = {
    "Montserrat ExtraBold": "montserrat.ttf",
    "Poppins": "poppins.ttf",
    "Bebas Neue": "bebas-neue.ttf",
    "Anton": "anton.ttf",
    "Oswald SemiBold": "oswald.ttf",
    "Archivo Black": "archivo-black.ttf",
    "Roboto Black": "roboto.ttf",
    "Inter ExtraBold": "inter.ttf",
    "Open Sans ExtraBold": "open-sans.ttf",
    "Lato Black": "lato.ttf",
    "Nunito ExtraBold": "nunito.ttf",
    "Quicksand": "quicksand.ttf",
    "Fredoka SemiBold": "fredoka.ttf",
    "Baloo 2 ExtraBold": "baloo-2.ttf",
    "Luckiest Guy": "luckiest-guy.ttf",
    "Bangers": "bangers.ttf",
    "Titan One": "titan-one.ttf",
    "Alfa Slab One": "alfa-slab-one.ttf",
    "Bungee": "bungee.ttf",
    "Righteous": "righteous.ttf",
    "Russo One": "russo-one.ttf",
    "Permanent Marker": "permanent-marker.ttf",
}
FONT_GROUPS = [
    ("Popular", ["Montserrat ExtraBold", "Poppins", "Bebas Neue", "Anton",
                 "Oswald SemiBold", "Archivo Black"]),
    ("Bold & heavy", ["Roboto Black", "Inter ExtraBold", "Open Sans ExtraBold",
                      "Lato Black"]),
    ("Rounded & friendly", ["Nunito ExtraBold", "Quicksand", "Fredoka SemiBold",
                            "Baloo 2 ExtraBold"]),
    ("Fun & display", ["Luckiest Guy", "Bangers", "Titan One", "Alfa Slab One",
                       "Bungee", "Righteous", "Russo One", "Permanent Marker"]),
]

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
