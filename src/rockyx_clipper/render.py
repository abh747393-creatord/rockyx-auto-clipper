"""Render: vertical 1080x1920 clips with tracked crop, burned-in captions,
loudnorm -16 LUFS audio, H.264 crf 18. Verifies BOTH stream durations with
ffprobe before/after encoding — a truncated audio track must never ship.

Reframe (from OpenClip Studio's tracker + OpenShorts' split-layout idea):
- Single speaker: YuNet face trajectory -> smooth crop-x expression (2s
  keyframes, linear interpolation), auto-zoom from face size (zoom factor
  clamped 1.0-1.8), vertical centre on the face.
- Two speakers: stacked split-screen, captions on the seam.
- No face found: centred crop (safe fallback, never fails the render).
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from . import config


def probe(path: Path) -> dict:
    cmd = [config.ffprobe_bin(), "-v", "error", "-show_format", "-show_streams",
           "-of", "json", str(path)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {path}: {proc.stderr[-300:]}")
    return json.loads(proc.stdout)


def durations(path: Path) -> tuple[float | None, float | None]:
    """(video_duration, audio_duration) in seconds, None when stream missing."""
    info = probe(path)
    video = audio = None
    for s in info.get("streams", []):
        d = s.get("duration")
        if d is None:
            d = info.get("format", {}).get("duration")
        if s.get("codec_type") == "video" and video is None:
            video = float(d) if d else None
        if s.get("codec_type") == "audio" and audio is None:
            audio = float(d) if d else None
    return video, audio


def verify_durations(path: Path, expect_s: float, tol: float = 0.3) -> None:
    """Both streams must exist and match each other and the expected length."""
    video, audio = durations(path)
    if video is None:
        raise RuntimeError(f"{path.name}: no video stream after render")
    if audio is None:
        raise RuntimeError(f"{path.name}: no audio stream after render")
    if abs(video - audio) > 0.15:
        raise RuntimeError(
            f"{path.name}: A/V duration mismatch video={video:.2f}s audio={audio:.2f}s")
    if abs(video - expect_s) > tol:
        raise RuntimeError(
            f"{path.name}: rendered {video:.2f}s, expected ~{expect_s:.2f}s")


def extract_audio_wav(source: Path, out: Path, sample_rate: int = 16000) -> Path:
    cmd = [config.ffmpeg_bin(), "-v", "error", "-y", "-i", str(source),
           "-vn", "-ac", "1", "-ar", str(sample_rate), "-c:a", "pcm_s16le", str(out)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
    if proc.returncode != 0 or not out.exists() or out.stat().st_size == 0:
        raise RuntimeError(f"audio extract failed: {proc.stderr[-400:]}")
    return out


def _escape_filter_path(path: str) -> str:
    # ffmpeg filter args: escape backslash, colon and single-quote.
    return path.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def measure_loudnorm(source: Path, start: float, dur: float) -> dict | None:
    """First loudnorm pass: returns measured_* values, or None on failure."""
    cmd = [config.ffmpeg_bin(), "-v", "info", "-ss", str(start), "-t", str(dur),
           "-i", str(source), "-vn",
           "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
           "-f", "null", "-"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    text = proc.stderr or ""
    start_i = text.rfind("{")
    end_i = text.rfind("}")
    if start_i < 0 or end_i <= start_i:
        return None
    try:
        return json.loads(text[start_i:end_i + 1])
    except json.JSONDecodeError:
        return None


def loudnorm_filter(measured: dict | None) -> str:
    base = "loudnorm=I=-16:TP=-1.5:LRA=11"
    if measured:
        try:
            return (f"{base}:measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
                    f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:"
                    f"offset={measured['target_offset']}:linear=true")
        except KeyError:
            pass
    return base


def _crop_x_expression(trajectory: list[dict], clip_dur: float,
                       crop_w: float, src_w: float) -> str:
    """Nested-if expression for crop x(t): 2s keyframes, linear interpolation.

    trajectory entries: {"t": seconds-from-clip-start, "x": 0..1 centre}.
    Returns an ffmpeg expression string evaluating to the crop x in pixels.
    """
    if not trajectory:
        return f"{(src_w - crop_w) / 2:.1f}"
    pts: list[tuple[float, float]] = []
    for step in range(0, int(clip_dur) + 3, 2):
        t = float(step)
        # Nearest trajectory sample at or before t (trajectory is 4fps).
        x = None
        for p in trajectory:
            if p["t"] <= t:
                x = p["x"]
            else:
                break
        if x is None:
            x = trajectory[0]["x"]
        cx = max(0.0, min(src_w, x * src_w))
        px = max(0.0, min(src_w - crop_w, cx - crop_w / 2))
        pts.append((t, px))
    # Build from the last interval backwards: if(lt(t,Tn), EXPRn, Pn)
    expr = f"{pts[-1][1]:.1f}"
    for i in range(len(pts) - 2, -1, -1):
        t0, x0 = pts[i]
        t1, x1 = pts[i + 1]
        seg = f"{x0:.1f}+({x1 - x0:.1f})*(t-{t0:.1f})/{t1 - t0:.1f}"
        expr = f"if(lt(t,{t1:.1f}),{seg},{expr})"
    return expr


def render_clip(source: Path, start: float, end: float, ass_path: Path,
                out_path: Path, tracking: dict | None = None,
                preset: str = "veryfast") -> Path:
    """Render one vertical clip. tracking = track_subject() result or None."""
    dur = end - start
    info = probe(source)
    vstream = next(s for s in info["streams"] if s["codec_type"] == "video")
    src_w, src_h = int(vstream["width"]), int(vstream["height"])
    measured = measure_loudnorm(source, start, dur)
    audio_f = loudnorm_filter(measured)

    # Auto-zoom from average face width (OpenClip tracker 'fw').
    zoom = 1.0
    if tracking and tracking.get("avgFw"):
        face_px = tracking["avgFw"] * src_w
        target_crop_w = face_px / 0.35 if face_px > 0 else src_w * 9 / 16
        max_crop_w = src_h * 9 / 16
        zoom = max(1.0, min(1.8, max_crop_w / max(target_crop_w, 1.0)))
    crop_w = int((src_h * 9 / 16) / zoom)
    crop_h = int(crop_w * 16 / 9)
    crop_w -= crop_w % 2
    crop_h -= crop_h % 2
    # Vertical centre: face cy if known, else frame centre.
    cy_frac = 0.5
    if tracking and tracking.get("trajectory"):
        cys = [p.get("cy", 0.5) for p in tracking["trajectory"] if "cy" in p]
        if cys:
            cy_frac = sum(cys) / len(cys)
    crop_y = int(max(0, min(src_h - crop_h, cy_frac * src_h - crop_h / 2)))
    crop_y -= crop_y % 2

    traj = (tracking or {}).get("trajectory") or []
    x_expr = _crop_x_expression(traj, dur, crop_w, src_w)
    vf = (
        f"crop=w={crop_w}:h={crop_h}:x='{x_expr}':y={crop_y},"
        f"scale=1080:1920,"
        f"subtitles=filename='{_escape_filter_path(str(ass_path))}',"
        f"format=yuv420p"
    )
    cmd = [
        config.ffmpeg_bin(), "-v", "error", "-y",
        "-ss", str(start), "-t", str(dur), "-i", str(source),
        "-vf", vf, "-af", audio_f,
        "-c:v", "libx264", "-crf", str(config.EXPORT_CRF), "-preset", preset,
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", str(out_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if proc.returncode != 0:
        # Fallback: fixed centre crop (no tracking expression).
        vf2 = (
            f"crop=w={crop_w}:h={crop_h}:x={(src_w - crop_w) // 2}:y={crop_y},"
            f"scale=1080:1920,"
            f"subtitles=filename='{_escape_filter_path(str(ass_path))}',"
            f"format=yuv420p"
        )
        cmd[cmd.index("-vf") + 1] = vf2
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        if proc.returncode != 0:
            raise RuntimeError(f"render failed: {proc.stderr[-800:]}")
    verify_durations(out_path, dur)
    return out_path


def render_split_screen(source: Path, start: float, end: float, ass_path: Path,
                        out_path: Path, tracking: dict,
                        preset: str = "veryfast") -> Path:
    """Two-speaker stacked layout: left speaker top, right speaker bottom."""
    dur = end - start
    info = probe(source)
    vstream = next(s for s in info["streams"] if s["codec_type"] == "video")
    src_w, src_h = int(vstream["width"]), int(vstream["height"])
    measured = measure_loudnorm(source, start, dur)
    audio_f = loudnorm_filter(measured)

    left_x = tracking.get("speakerLeftPercent", 30) / 100.0 * src_w
    right_x = tracking.get("speakerRightPercent", 70) / 100.0 * src_w
    # Each panel: 1080x960 -> source crop aspect 9:8.
    panel_w = int(src_h * 9 / 8)
    panel_w = min(panel_w, src_w)
    panel_w -= panel_w % 2
    panel_h = int(panel_w * 8 / 9)
    panel_h -= panel_h % 2
    cy = src_h // 2
    y0 = max(0, min(src_h - panel_h, cy - panel_h // 2))
    y0 -= y0 % 2
    x_left = int(max(0, min(src_w - panel_w, left_x - panel_w / 2)))
    x_right = int(max(0, min(src_w - panel_w, right_x - panel_w / 2)))

    vf = (
        f"[0:v]crop=w={panel_w}:h={panel_h}:x={x_left}:y={y0},scale=1080:960[top];"
        f"[0:v]crop=w={panel_w}:h={panel_h}:x={x_right}:y={y0},scale=1080:960[bot];"
        f"[top][bot]vstack=inputs=2,"
        f"subtitles=filename='{_escape_filter_path(str(ass_path))}',"
        f"format=yuv420p"
    )
    cmd = [
        config.ffmpeg_bin(), "-v", "error", "-y",
        "-ss", str(start), "-t", str(dur), "-i", str(source),
        "-filter_complex", vf, "-af", audio_f,
        "-c:v", "libx264", "-crf", str(config.EXPORT_CRF), "-preset", preset,
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", str(out_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if proc.returncode != 0:
        raise RuntimeError(f"split-screen render failed: {proc.stderr[-800:]}")
    verify_durations(out_path, dur)
    return out_path
