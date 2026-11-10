"""Download: YouTube URL or local file -> local video file.

Uses yt-dlp with the WEB client + --impersonate chrome (per AGENTS.md:
YouTube HD is NOT gated; always list formats with the web client first and
take true 1080p, never upscale 360p). Falls back to a plain download if
impersonation is unavailable.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from . import config

WEB_FORMATS = "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/bv*[height<=1080]+ba/b[height<=1080]"


def _run(cmd, timeout=None):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def list_formats(url: str) -> dict:
    """Return {title, duration, formats} via yt-dlp -J (web client)."""
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--impersonate", "chrome",
        "--extractor-args", "youtube:player_client=web",
        "-J", "--no-playlist", url,
    ]
    proc = _run(cmd, timeout=120)
    if proc.returncode != 0:
        # Retry without impersonation (older yt-dlp / missing curl_cffi).
        cmd2 = [sys.executable, "-m", "yt_dlp", "-J", "--no-playlist", url]
        proc = _run(cmd2, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(f"yt-dlp -J failed: {(proc.stderr or proc.stdout or '')[-500:]}")
    info = json.loads(proc.stdout)
    return {
        "title": info.get("title", "video"),
        "duration": info.get("duration"),
        "id": info.get("id", ""),
        "formats": info.get("formats", []),
    }


def best_1080p_format(info: dict) -> str:
    """Pick the best <=1080p video+audio format string from -J output."""
    formats = info.get("formats", [])
    video = [f for f in formats if f.get("vcodec") not in (None, "none")
             and f.get("height") and f["height"] <= 1080]
    if not video:
        return "bv*[height<=1080]+ba/b[height<=1080]"
    video.sort(key=lambda f: (f["height"], f.get("tbr") or 0))
    best = video[-1]
    return f"{best['format_id']}+ba/b[height<=1080]"


def download_youtube(url: str, out_dir: Path, section: tuple[float, float] | None = None,
                     title_hint: str = "video") -> Path:
    """Download a YouTube URL (optionally only [start,end] seconds).

    Tries Chrome impersonation first (best quality / bot-check bypass), then
    falls back to a plain download when curl_cffi is missing — a fresh
    install without it must NOT hard-fail with an impersonate error.
    Returns the downloaded file path. Verifies the file exists and is non-empty.
    Raises RuntimeError with yt-dlp's tail output on failure (e.g. HTTP 429
    when YouTube rate-limits the egress IP — retry later, it is transient).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    out_tmpl = str(out_dir / "%(title).80s-%(id)s.%(ext)s")
    common = [
        sys.executable, "-m", "yt_dlp",
        "--extractor-args", "youtube:player_client=web",
        "-f", WEB_FORMATS,
        "--merge-output-format", "mp4",
        "--no-playlist",
        "-o", out_tmpl,
    ]
    if section:
        start, end = section
        common += ["--download-sections", f"*{start}-{end}", "--force-keyframes-at-cuts"]
    common.append(url)
    attempts = [
        common[:3] + ["--impersonate", "chrome"] + common[3:],
        common,  # plain fallback: no impersonation (missing curl_cffi)
    ]
    last_err = ""
    for cmd in attempts:
        proc = _run(cmd, timeout=1800)
        if proc.returncode == 0:
            break
        last_err = (proc.stderr or proc.stdout or "")[-800:]
    else:
        raise RuntimeError(f"yt-dlp download failed: {last_err}")
    files = sorted(out_dir.glob("*"), key=lambda p: p.stat().st_mtime)
    files = [f for f in files if f.is_file() and f.stat().st_size > 0
             and f.suffix.lower() in (".mp4", ".mkv", ".webm")]
    if not files:
        raise RuntimeError("yt-dlp reported success but no video file appeared in " + str(out_dir))
    return files[-1]


def prepare_source(source: str, work_dir: Path,
                   section: tuple[float, float] | None = None) -> tuple[Path, dict]:
    """Accept a YouTube URL or a local file path. Returns (video_path, meta)."""
    work_dir.mkdir(parents=True, exist_ok=True)
    p = Path(source)
    if p.exists() and p.is_file():
        return p, {"title": p.stem, "duration": None, "source": "local"}
    if source.startswith("http://") or source.startswith("https://"):
        try:
            info = list_formats(source)
        except Exception:
            # The -J probe is only metadata (title/duration). If it fails
            # (e.g. a proxy cert error), the download itself — which has its
            # own impersonate -> plain fallback — may still succeed, so do
            # not kill the job here. Fall back to placeholder metadata.
            info = {"title": "video", "duration": None}
        video = download_youtube(source, work_dir / "source", section=section)
        return video, {"title": info.get("title", "video"),
                       "duration": info.get("duration"), "source": "youtube"}
    raise ValueError(f"Not a local file or URL: {source}")
