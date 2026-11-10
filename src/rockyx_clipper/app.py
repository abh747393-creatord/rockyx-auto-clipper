"""Localhost web UI: FastAPI + plain HTML, no Node, no Docker.

Open http://127.0.0.1:8000 in a browser, paste a YouTube link or upload a
file, get ranked vertical clips with captions. Everything runs locally.
"""
from __future__ import annotations

import datetime
import json
import shutil
import threading
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response

from . import config
from . import settings as settings_mod
from .pipeline import retrim_clip, run_job

ROOT = config.ROOT
STATIC_DIR = ROOT / "static"
JOBS: dict[str, dict] = {}


def _friendly_error(exc: Exception) -> tuple[str, str]:
    """Return (short human message, technical detail) for a job failure.

    The UI shows the human message; the technical tail stays behind a
    "details" toggle instead of being dumped raw on screen.
    """
    raw = str(exc)
    low = raw.lower()
    if "impersonate" in low and "not available" in low:
        return ("YouTube download needs a missing helper. In the project folder run: "
                "pip install curl_cffi — then try again.", raw[-800:])
    if "429" in low or "too many requests" in low:
        return ("YouTube is rate-limiting this network right now. Wait a while and retry, "
                "or upload a video file instead — local files always work.", raw[-800:])
    if "video unavailable" in low or "private video" in low:
        return ("That YouTube video cannot be downloaded (unavailable or private). "
                "Check the link, or upload the video file instead.", raw[-800:])
    if "certificate" in low or "ssl" in low:
        return ("This network is blocking YouTube's security check (certificate error) — "
                "the video itself is fine. Try again on another network, or upload the "
                "video file instead — local files always work.", raw[-800:])
    if "no video stream" in low:
        return ("The source has no video stream — pick a different video.", raw[-800:])
    if "no audio stream" in low:
        return ("The source has no audio — silent videos cannot be clipped.", raw[-800:])
    return ("The download failed. Check the link and try again, or upload the video "
            "file instead — local files always work.", raw[-800:])


def _job_status(job_id: str) -> dict:
    state = JOBS.get(job_id, {})
    job_dir = config.JOBS_DIR / job_id
    summary_path = job_dir / "job.json"
    summary = None
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            summary = None
    return {
        "job_id": job_id,
        "stage": state.get("stage", "done" if summary else "unknown"),
        "percent": state.get("percent", 100 if summary else 0),
        "message": state.get("message", ""),
        "error": state.get("error"),
        "error_detail": state.get("error_detail"),
        "summary": summary,
    }


def _run_in_thread(job_id: str, source: str, opts: dict):
    job_dir = config.JOBS_DIR / job_id

    def progress(stage, pct, msg=""):
        JOBS[job_id] = {"stage": stage, "percent": pct, "message": msg}

    try:
        JOBS[job_id] = {"stage": "download", "percent": 1, "message": "starting"}
        run_job(source, job_dir, opts, progress_cb=progress)
        JOBS[job_id] = {"stage": "done", "percent": 100, "message": "done"}
    except Exception as exc:  # noqa: BLE001 - surfaced in the UI
        friendly, detail = _friendly_error(exc)
        JOBS[job_id] = {"stage": "error", "percent": 0, "message": friendly,
                        "error": friendly, "error_detail": detail}


app = FastAPI(title="Rockyx Auto-Clipper", version=config.VERSION)


@app.get("/", response_class=HTMLResponse)
def index():
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/api/health")
def health():
    try:
        import yt_dlp  # noqa: F401
        ytdlp_ok = True
    except ImportError:
        ytdlp_ok = bool(shutil.which("yt-dlp"))
    return {
        "version": config.VERSION,
        "ffmpeg": bool(shutil.which("ffmpeg")),
        "ffprobe": bool(shutil.which("ffprobe")),
        "yt_dlp": ytdlp_ok,
    }


@app.get("/api/settings")
def get_settings():
    """AI settings status. The key itself is NEVER returned, only a mask."""
    return settings_mod.public_status()


@app.post("/api/settings")
def save_settings(payload: dict):
    """Save the Gemini API key and/or default scorer.

    Send {"gemini_api_key": "<key>"} to save, {"gemini_api_key": ""} to clear,
    {"scorer": "auto"|"gemini"|"heuristic"|"local-ml"} to change the default.
    The key is stored only on this machine (~/.rockyx/settings.json).
    """
    try:
        if "gemini_api_key" in payload:
            settings_mod.save_settings(gemini_api_key=str(payload.get("gemini_api_key") or ""))
        if "scorer" in payload:
            settings_mod.save_settings(scorer=str(payload.get("scorer") or "auto"))
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    return settings_mod.public_status()


@app.post("/api/settings/test")
def test_settings():
    """One tiny Gemini call to check the saved key works. Returns OK or a
    plain-language error; the key is never echoed back."""
    from . import gemini_client
    try:
        reply = gemini_client.probe()
    except Exception as exc:  # noqa: BLE001 - surfaced as a plain message
        return {"ok": False, "error": str(exc)}
    return {"ok": True, "reply": reply}


@app.get("/api/fonts")
def list_fonts():
    """Bundled free caption fonts, grouped for the UI dropdown."""
    return {"groups": [[g, fs] for g, fs in config.FONT_GROUPS],
            "fonts": list(config.FONTS)}


@app.get("/api/fonts/preview")
def font_preview(name: str = ""):
    """PNG preview of the sample line in one bundled font (for the picker)."""
    from . import preview as preview_mod
    try:
        data = preview_mod.render_font_preview(name)
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    return Response(content=data, media_type="image/png")


@app.get("/api/jobs")
def list_jobs():
    out = []
    if config.JOBS_DIR.exists():
        for d in sorted(config.JOBS_DIR.iterdir(), reverse=True):
            if d.is_dir():
                out.append(_job_status(d.name))
    return out


@app.post("/api/jobs")
def create_job(
    url: str = Form(default=""),
    file: UploadFile | None = File(default=None),
    num_clips: int = Form(default=config.DEFAULT_NUM_CLIPS),
    min_s: float = Form(default=config.DEFAULT_MIN_CLIP_S),
    max_s: float = Form(default=config.DEFAULT_MAX_CLIP_S),
    style: str = Form(default=config.DEFAULT_CAPTION_STYLE),
    language: str = Form(default=config.DEFAULT_LANGUAGE),
    model: str = Form(default=config.DEFAULT_WHISPER_MODEL),
    scorer: str = Form(default="auto"),
    font: str = Form(default=""),
    section: str = Form(default=""),
):
    job_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    job_dir = config.JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    if file is not None and file.filename:
        dest = job_dir / "work" / "upload" / Path(file.filename).name
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            f.write(file.file.read())
        source = str(dest)
    elif url.strip():
        source = url.strip()
    else:
        return JSONResponse({"error": "give a YouTube URL or upload a file"}, status_code=400)
    sec = None
    if section.strip():
        a, _, b = section.strip().partition("-")
        sec = (float(a), float(b))
    opts = {"num_clips": num_clips, "min_s": min_s, "max_s": max_s, "style": style,
            "language": language, "model": model, "scorer": scorer,
            "font": font if font in config.FONTS else "",
            "section": sec, "track": True}
    JOBS[job_id] = {"stage": "queued", "percent": 0, "message": "queued"}
    threading.Thread(target=_run_in_thread, args=(job_id, source, opts), daemon=True).start()
    return {"job_id": job_id}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    return _job_status(job_id)


def _clip_file(job_id: str, clip_id: str, name: str) -> Path:
    p = config.JOBS_DIR / job_id / "clips" / clip_id / name
    if not p.exists():
        raise FileNotFoundError(name)
    return p


@app.get("/api/jobs/{job_id}/clips/{clip_id}/video")
def clip_video(job_id: str, clip_id: str):
    return FileResponse(_clip_file(job_id, clip_id, f"{clip_id}.mp4"), media_type="video/mp4")


@app.get("/api/jobs/{job_id}/clips/{clip_id}/srt")
def clip_srt(job_id: str, clip_id: str):
    return FileResponse(_clip_file(job_id, clip_id, f"{clip_id}.srt"), media_type="text/plain")


@app.get("/api/jobs/{job_id}/clips/{clip_id}/caption/{platform}")
def clip_caption(job_id: str, clip_id: str, platform: str):
    if platform not in ("instagram", "tiktok", "youtube"):
        return JSONResponse({"error": "unknown platform"}, status_code=400)
    return FileResponse(_clip_file(job_id, clip_id, f"caption-{platform}.txt"),
                        media_type="text/plain")


@app.post("/api/jobs/{job_id}/clips/{clip_id}/retrim")
def clip_retrim(job_id: str, clip_id: str, payload: dict):
    try:
        clip = retrim_clip(
            config.JOBS_DIR / job_id, clip_id,
            new_start=payload.get("start"), new_end=payload.get("end"),
            hook_title=payload.get("hook_title"), style=payload.get("style"),
            font=payload.get("font"))
    except Exception as exc:  # noqa: BLE001
        return JSONResponse({"error": str(exc)}, status_code=400)
    return {"ok": True, "clip": {k: v for k, v in clip.items() if k != "words"}}


@app.post("/api/jobs/{job_id}/clips/{clip_id}/schedule")
def clip_schedule(job_id: str, clip_id: str, payload: dict):
    """Save a posting plan (platform + date/time). No auto-posting: the
    caption pack is ready to paste, and the schedule reminds you when.
    Auto-post needs each platform's OAuth — out of scope for v1."""
    job_dir = config.JOBS_DIR / job_id
    sched_path = job_dir / "schedule.json"
    sched = json.loads(sched_path.read_text(encoding="utf-8")) if sched_path.exists() else []
    sched.append({"clip_id": clip_id, "platform": payload.get("platform"),
                  "when": payload.get("when"), "note": payload.get("note", ""),
                  "saved_at": datetime.datetime.now().isoformat()})
    sched_path.write_text(json.dumps(sched, indent=2), encoding="utf-8")
    return {"ok": True, "schedule": sched}


def run_server(host: str = "127.0.0.1", port: int = 8000):
    import uvicorn
    print(f"Rockyx Auto-Clipper v{config.VERSION} — open http://{host}:{port} in your browser")
    print("Everything runs locally. Press Ctrl+C to stop.")
    uvicorn.run(app, host=host, port=port, log_level="warning")
