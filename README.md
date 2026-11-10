# 🎬 Rocky x Auto-Clipper

**Your own Opus Clip / Vizard — free forever, no watermark, no minute limits.**
Paste a YouTube link or a video file, get ranked vertical clips (1080×1920)
with kinetic word-by-word captions, hook titles and ready-to-post captions.
Runs on **localhost** — nothing leaves your computer, no account, no cloud.

## What it combines (and why)

| Tool | Licence | What we took |
|---|---|---|
| **OpenClip Studio** — *foundation* | MIT | faster-whisper transcription, YuNet face tracking, local ML virality model, kinetic caption styles |
| AutoClip | MIT | Pipeline step design, speaker-tracked reframe, cover/post-text idea |
| SupoClip | AGPL-3.0 | Web-UI flow, virality dimensions, hook titles, editor concept — **ideas only, no code copied** |
| Video Wizard | MIT | 0–100 viral scoring, 9 caption-template idea |
| OpenShorts | MIT | Dual-speaker split-screen, hook grounding, captions on the seam |

**Why OpenClip Studio as foundation:** it is the only one whose ML layer is
already small, Python-native, CPU-friendly and cross-platform
(faster-whisper + onnxruntime + OpenCV-headless + scikit-learn), with its
face model bundled in the repo. The other four need Docker / Node /
Postgres / paid APIs in their default setup — this tool must run with one
command on Windows and Linux, no Docker. Full attribution: `CREDITS.md`;
original repos stay untouched in `vendor/`; licences in `licenses/`.

**Paid tools' features, re-implemented with open components** (their code is
closed-source and was NOT copied): virality score 0–100 + ranking, face /
speaker-aware 9:16 reframe with auto-zoom, kinetic word captions, multi-
language captions, hook/title + hashtag generation, transcript editor
(re-trim + re-render), dual-speaker split-screen, B-roll suggestions,
export + ready-to-post caption pack, scheduling (saved plan; auto-post
needs platform OAuth — out of scope for v1). See `CREDITS.md` for the
feature-by-feature mapping.

## Quick start

### Windows (Rocky's gaming PC)
```powershell
# 1. Python 3.10+ from python.org (tick "Add python.exe to PATH")
# 2. ffmpeg:  winget install Gyan.FFmpeg
#    (or: choco install ffmpeg) — then close + reopen PowerShell
# 3. Get the code + install Python packages (once):
cd C:\rockyx-clipper
pip install -r requirements.txt
# 4. Run (double-click run.bat, or):
python -m rockyx_clipper serve --port 8000
# 5. Open http://127.0.0.1:8000 in your browser
```
Optional, for free local AI scoring with no API key at all:
```powershell
# Ollama (https://ollama.com/download) — local LLM fallback for scoring
ollama pull qwen2.5:7b
```
Gemini scoring (better picks) needs a Gemini API key — set it once:
```powershell
setx GEMINI_API_KEY "your-key-here"
```
(Inside Muse, the vault credential is used automatically instead.)

### Linux / Ubuntu (this VM)
```bash
sudo apt install ffmpeg python3-pip
pip install -r requirements.txt
./run.sh            # web UI at http://127.0.0.1:8000
```

### CLI (no browser)
```bash
# 3 clips from a YouTube video (true 1080p source, never upscaled)
python -m rockyx_clipper run "https://www.youtube.com/watch?v=VIDEO_ID" --num-clips 3
# Local file, heuristic scoring only (no API key needed)
python -m rockyx_clipper run ./podcast.mp4 --scorer heuristic --style mrbeast
# Only a section of a YouTube video (seconds)
python -m rockyx_clipper run "https://www.youtube.com/watch?v=VIDEO_ID" --section 600-1500
# Check setup (ffmpeg + Gemini)
python -m rockyx_clipper probe
```

## How it works

```
YouTube URL / file → yt-dlp (web client, 1080p) → 16kHz audio
  → faster-whisper (word timestamps, VAD) → candidate windows (30–60s, cut on pauses)
  → scoring: Gemini 0–100 (+ hook/shareability) → fallback: local ML model → heuristic
  → YuNet face tracking (4 fps, smoothed) → kinetic ASS captions (4 styles)
  → ffmpeg: tracked 9:16 crop + auto-zoom (or split-screen) + burned-in captions
  → loudnorm −16 LUFS → H.264 crf 18, 1080×1920, faststart
  → ffprobe verifies video AND audio durations match before the clip ships
```

Each clip ships as a pack: `clipNN.mp4` + `clipNN.srt` + `clipNN.ass` +
`caption-instagram.txt` / `caption-tiktok.txt` / `caption-youtube.txt` +
`clip.json` (scores, times, reason, B-roll suggestion). Jobs live in `jobs/`.

## Web UI

- Paste a YouTube link or upload a file → live progress → ranked clips.
- Click a clip to preview it; download video / captions / `.srt`.
- **Transcript editor:** change start / end / hook title / style → Re-render.
- **Schedule:** pick platform + date/time → saved to `schedule.json`
  (a posting plan; auto-posting needs each platform's OAuth login).
- Recent jobs list on the same page.

## QA — 100-test rule

After every build, the tool is tested a minimum of 100 times (fast
component tests + full end-to-end runs), every failure is fixed and
re-tested. Log: `TEST-LOG.md`. Harness: `tests/test_harness.py`.
Do not hand over until the loop is clean.

**v0.1.1 (2026-11-10):** fixed the fresh-install YouTube failure —
`requirements.txt` was missing `curl_cffi`, so `--impersonate chrome`
failed on a clean PC. Now included, plus the downloader falls back to a
plain download when impersonation is unavailable, errors are shown in
plain language, and the UI has a progress stepper. Verified from a clean
virtualenv install before release.

## What's still missing vs the paid tools

- **Active-speaker switching** (who is talking, frame by frame) — v1 tracks
  the dominant face; speaker diarization is a later step.
- **Auto B-roll overlay** — v1 suggests B-roll per clip as text; rendering
  stock footage over the clip is not in yet.
- **Auto-posting / scheduling to platforms** — v1 exports the pack + saves
  the plan; posting still needs the platform apps / OAuth.
- **Background music / SFX** — not in v1 (loudnorm'd original audio only).
- **Cloud/GPU speed** — CPU-only by design; a 10-min video takes minutes
  on this VM, much faster on a GPU PC.

## Troubleshooting

- **YouTube download fails with "Impersonate target chrome is not available"**: fixed in v0.1.1 — `requirements.txt` now includes `curl_cffi`, and the downloader falls back to a plain download when impersonation is unavailable. If you installed v0.1.0, run `pip install -r requirements.txt` again (or `pip install curl_cffi`).
- **YouTube 429 / "Video unavailable"**: YouTube rate-limits the shared
  network IP. Wait a while and retry — it is transient. Local files always work.
- **Gemini 503 / no reply**: the model is busy; the tool falls back to
  heuristic scoring automatically. `--scorer heuristic` skips the API.
- **No faces found**: centre crop is used automatically (gameplay, B-roll,
  animation). Tracking never fails a render.
- **Slow transcription**: use `--model tiny` for a quick pass,
  `small` for better accuracy (slower on CPU).
- **Windows font**: captions use DejaVu Sans on Linux, Arial on Windows.
  Set `ROCKYX_FONT` env var to any installed font family to change it.
