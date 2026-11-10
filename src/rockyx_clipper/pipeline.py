"""Pipeline orchestration: source -> transcript -> moments -> clips.

Stages: download -> probe -> audio extract -> transcribe (faster-whisper,
word timestamps) -> candidates -> scoring (Gemini / local ML / heuristic) ->
face tracking -> kinetic captions -> render -> caption pack + job summary.

Progress is reported through progress_cb(stage, percent, message).
Everything is local; nothing is uploaded or posted.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

from . import captions as captions_mod
from . import config, download as download_mod, render as render_mod, score as score_mod
from .track import track_subject


def _run_module(module: str, args: list[str], timeout: int = 1800) -> str:
    env = {"PYTHONPATH": str(config.ROOT / "src")}
    import os
    full_env = dict(os.environ)
    full_env["PYTHONPATH"] = str(config.ROOT / "src") + os.pathsep + full_env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [sys.executable, "-m", module] + args,
        capture_output=True, text=True, timeout=timeout, env=full_env,
        cwd=str(config.ROOT),
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "")
        # Keep head AND tail: the tail is often just a warning, the error is earlier.
        snippet = err[:400] + (" ... " + err[-400:] if len(err) > 800 else "")
        raise RuntimeError(f"{module} failed: {snippet}")
    return proc.stdout


def transcribe_audio(wav_path: Path, model: str = "base", language: str = "en") -> dict:
    args = [str(wav_path), "--model", model, "--language", language]
    out = _run_module("rockyx_clipper.transcribe", args, timeout=3600)
    # transcribe.py prints one JSON object (last line).
    for line in reversed(out.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            data = json.loads(line)
            if data.get("success"):
                return data
            raise RuntimeError(f"transcription failed: {data.get('error')}")
    raise RuntimeError("transcription produced no JSON output")


def _caption_pack_text(clip: dict, platform: str = "instagram") -> str:
    title = clip.get("title") or clip.get("hook_title") or "New clip"
    tags = " ".join("#" + t for t in clip.get("hashtags", []))
    hook = clip.get("hook_title", "")
    lines = [title, "", f"Hook: {hook}" if hook else "", tags, "",
             f"Score: {clip.get('score', 0)}/100 ({clip.get('score_source', '?')})",
             f"Source: {clip.get('start', 0):.1f}s - {clip.get('end', 0):.1f}s"]
    if clip.get("reason"):
        lines += ["", f"Why it works: {clip['reason']}"]
    if clip.get("broll_suggestion"):
        lines += ["", f"B-roll idea: {clip['broll_suggestion']}"]
    return "\n".join(l for l in lines if l != "" or True).strip() + "\n"


def _decide_split(tracking: dict | None, layout: str) -> bool:
    """Split-screen decision. layout: auto (follow face tracking) /
    single (never split) / split (always split). Auto is what misfired on
    gameplay streams before the facecam guard — a small corner face is a
    webcam overlay, not a second speaker."""
    if layout == "single":
        return False
    if layout == "split":
        return True
    return bool(tracking and tracking.get("hasTwoSpeakers"))


def run_job(source: str, job_dir: Path, opts: dict | None = None,
            progress_cb=None) -> dict:
    opts = opts or {}
    num_clips = int(opts.get("num_clips", config.DEFAULT_NUM_CLIPS))
    min_s = float(opts.get("min_s", config.DEFAULT_MIN_CLIP_S))
    max_s = float(opts.get("max_s", config.DEFAULT_MAX_CLIP_S))
    style = opts.get("style", config.DEFAULT_CAPTION_STYLE)
    language = opts.get("language", config.DEFAULT_LANGUAGE)
    model = opts.get("model", config.DEFAULT_WHISPER_MODEL)
    scorer = opts.get("scorer", "auto")  # auto | gemini | heuristic | local-ml
    font = opts.get("font", "")  # bundled font name from config.FONTS, "" = style default
    section = opts.get("section")
    do_track = bool(opts.get("track", True))
    captions_on = bool(opts.get("captions", True))  # False: source already has captions on screen
    layout = str(opts.get("layout", "auto"))  # auto | single | split
    started = time.time()

    def progress(stage, pct, msg=""):
        if progress_cb:
            progress_cb(stage, pct, msg)
        print(f"[{stage}] {pct}% {msg}", flush=True)

    job_dir = Path(job_dir)
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / "clips").mkdir(exist_ok=True)

    progress("download", 2, "preparing source")
    video, meta = download_mod.prepare_source(source, job_dir / "work", section=section)
    info = render_mod.probe(video)
    vstreams = [s for s in info["streams"] if s["codec_type"] == "video"]
    astreams = [s for s in info["streams"] if s["codec_type"] == "audio"]
    if not vstreams:
        raise RuntimeError("source has no video stream")
    if not astreams:
        raise RuntimeError("source has no audio stream (silent video cannot be clipped)")
    src_dur = float(info["format"]["duration"])

    progress("transcribe", 10, "extracting audio")
    wav = render_mod.extract_audio_wav(video, job_dir / "work" / "audio.wav")
    progress("transcribe", 15, f"transcribing with faster-whisper ({model})")
    transcript = transcribe_audio(wav, model=model,
                                  language="" if language == "auto" else language)
    words = transcript.get("words", [])
    if not words:
        raise RuntimeError("transcription produced no words — check the audio")
    (job_dir / "transcript.json").write_text(json.dumps(transcript), encoding="utf-8")
    progress("transcribe", 45, f"{len(words)} words, {transcript.get('language')}")

    progress("score", 50, "finding moments")
    candidates = score_mod.build_candidates(words, min_s=min_s, max_s=max_s)
    if not candidates:
        raise RuntimeError("no clip candidates found (video too short or too quiet?)")
    ranked = score_mod.score_candidates_heuristic(candidates)
    picked: list[dict] = []
    gemini_ok = False
    if scorer in ("auto", "gemini"):
        try:
            g = score_mod.gemini_pick_moments(words, num_clips=num_clips,
                                              min_s=min_s, max_s=max_s,
                                              language=transcript.get("language", "en"))
            if g:
                picked = g
                gemini_ok = True
                progress("score", 60, f"Gemini picked {len(g)} moments")
        except Exception as exc:  # noqa: BLE001 - Gemini failure falls back to heuristic
            print(f"[score] Gemini failed, using heuristic: {exc}")
    if len(picked) < num_clips:
        for c in ranked:
            if len(picked) >= num_clips:
                break
            if not any(abs(c["start"] - p["start"]) < 5 for p in picked):
                picked.append(c)
    picked = score_mod.dedupe_clips(picked)[:num_clips]
    if scorer == "local-ml":
        ml_scores = score_mod.local_ml_score(ranked[:20], wav_path=str(wav))
        if ml_scores:
            for i, s in ml_scores.items():
                ranked[i]["ml_score"] = s
            progress("score", 62, "local ML virality model scored candidates")
    # Heuristic picks have no title/hashtags — derive a fallback pack so the
    # caption files are never bare (Gemini picks already carry their own).
    for c in picked:
        if not c.get("title"):
            first = c.get("text", "").split()
            c["title"] = " ".join(first[:12]).strip() or "New clip"
            c["hook_title"] = c["title"][:60]
        if not c.get("hashtags"):
            c["hashtags"] = ["podcast", "clips", "viral"]

    clips_out: list[dict] = []
    for idx, clip in enumerate(picked, 1):
        cid = f"clip{idx:02d}"
        cdir = job_dir / "clips" / cid
        cdir.mkdir(parents=True, exist_ok=True)
        start, end = clip["start"], clip["end"]
        progress("track", 65, f"{cid}: face tracking {start:.0f}-{end:.0f}s")
        tracking = None
        if do_track:
            try:
                tracking = track_subject(str(video), start, end - start)
            except Exception as exc:  # noqa: BLE001 - tracking is best-effort
                print(f"[track] {cid} tracking failed, centre crop: {exc}")
        progress("captions", 72, f"{cid}: kinetic captions ({style})" if captions_on else f"{cid}: captions off")
        clip_words = [w for w in words if w["end"] > start and w["start"] < end]
        split = _decide_split(tracking, layout)
        ass_path = None
        if captions_on:
            ass_path = cdir / f"{cid}.ass"
            captions_mod.words_to_ass(
                clip_words, start, end, style_name=style,
                hook_title=clip.get("hook_title", ""),
                out_path=ass_path, margin_v=860 if split else None, font=font)
        srt_path = cdir / f"{cid}.srt"
        captions_mod.words_to_srt(clip_words, start, end, out_path=srt_path)

        progress("render", 78, f"{cid}: rendering 1080x1920")
        out_path = cdir / f"{cid}.mp4"
        if split:
            render_mod.render_split_screen(video, start, end, ass_path, out_path, tracking)
        else:
            render_mod.render_clip(video, start, end, ass_path, out_path, tracking)
        # Caption pack: ready-to-post text per platform.
        cap = dict(clip)
        cap.update({
            "id": cid, "file": str(out_path), "srt": str(srt_path),
            "ass": str(ass_path) if ass_path else None, "split_screen": split, "font": font,
            "captions": captions_on, "layout": layout,
            "tracking": {"hasTwoSpeakers": bool(tracking and tracking.get("hasTwoSpeakers")),
                         "avgX": (tracking or {}).get("avgX"),
                         "avgFw": (tracking or {}).get("avgFw")},
        })
        for platform in ("instagram", "tiktok", "youtube"):
            (cdir / f"caption-{platform}.txt").write_text(
                _caption_pack_text(cap, platform), encoding="utf-8")
        (cdir / "clip.json").write_text(json.dumps(cap, indent=2), encoding="utf-8")
        clips_out.append(cap)
        progress("render", 78 + int(20 * idx / max(1, len(picked))), f"{cid} done")

    summary = {
        "job": job_dir.name, "source": str(video), "title": meta.get("title"),
        "duration": src_dur, "language": transcript.get("language"),
        "num_words": len(words), "scorer": "gemini" if gemini_ok else "heuristic",
        "style": style, "captions": captions_on, "layout": layout,
        "elapsed_s": round(time.time() - started, 1),
        "clips": [{k: v for k, v in c.items() if k != "words"} for c in clips_out],
    }
    (job_dir / "job.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    progress("done", 100, f"{len(clips_out)} clips in {summary['elapsed_s']}s")
    return summary


def retrim_clip(job_dir: Path, clip_id: str, new_start: float | None = None,
                new_end: float | None = None, hook_title: str | None = None,
                style: str | None = None, progress_cb=None,
                font: str | None = None, captions: bool | None = None,
                layout: str | None = None) -> dict:
    """Re-render one clip with edited start/end/title/style (transcript editor)."""
    job_dir = Path(job_dir)
    summary = json.loads((job_dir / "job.json").read_text(encoding="utf-8"))
    transcript = json.loads((job_dir / "transcript.json").read_text(encoding="utf-8"))
    words = transcript["words"]
    clip = next(c for c in summary["clips"] if c["id"] == clip_id)
    start = float(new_start) if new_start is not None else clip["start"]
    end = float(new_end) if new_end is not None else clip["end"]
    if end - start < 5:
        raise ValueError("clip must be at least 5 seconds")
    style = style or summary.get("style", config.DEFAULT_CAPTION_STYLE)
    font = font if font is not None else clip.get("font", "")
    captions_on = summary.get("captions", True) if captions is None else bool(captions)
    layout = layout or summary.get("layout", "auto")
    hook = hook_title if hook_title is not None else clip.get("hook_title", "")
    video = Path(summary["source"])
    cdir = job_dir / "clips" / clip_id
    tracking = None
    try:
        tracking = track_subject(str(video), start, end - start)
    except Exception as exc:  # noqa: BLE001
        print(f"[retrim] tracking failed, centre crop: {exc}")
    clip_words = [w for w in words if w["end"] > start and w["start"] < end]
    split = _decide_split(tracking, layout)
    ass_path = None
    if captions_on:
        ass_path = cdir / f"{clip_id}.ass"
        captions_mod.words_to_ass(clip_words, start, end, style_name=style,
                                  hook_title=hook, out_path=ass_path,
                                  margin_v=860 if split else None, font=font)
    captions_mod.words_to_srt(clip_words, start, end, out_path=cdir / f"{clip_id}.srt")
    out_path = cdir / f"{clip_id}.mp4"
    if split:
        render_mod.render_split_screen(video, start, end, ass_path, out_path, tracking)
    else:
        render_mod.render_clip(video, start, end, ass_path, out_path, tracking)
    clip.update({"start": start, "end": end, "hook_title": hook, "split_screen": split,
                 "captions": captions_on, "layout": layout,
                 "text": " ".join(w["word"] for w in clip_words)})
    (cdir / "clip.json").write_text(json.dumps(clip, indent=2), encoding="utf-8")
    for platform in ("instagram", "tiktok", "youtube"):
        (cdir / f"caption-{platform}.txt").write_text(
            _caption_pack_text(clip, platform), encoding="utf-8")
    (job_dir / "job.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return clip
