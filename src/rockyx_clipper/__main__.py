"""CLI: python -m rockyx_clipper <source> [options]  |  python -m rockyx_clipper serve

source: YouTube URL or local video file.
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rockyx_clipper import config  # noqa: E402
from rockyx_clipper.pipeline import run_job  # noqa: E402


def _parse_section(text: str | None):
    if not text:
        return None
    a, _, b = text.partition("-")
    return (float(a), float(b))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Rockyx Auto-Clipper (free, local)")
    sub = parser.add_subparsers(dest="cmd")

    p_run = sub.add_parser("run", help="clip a video (default when a source is given)")
    p_run.add_argument("source", help="YouTube URL or local video file")
    p_run.add_argument("--out", default=None, help="job directory (default jobs/<timestamp>)")
    p_run.add_argument("--num-clips", type=int, default=config.DEFAULT_NUM_CLIPS)
    p_run.add_argument("--min-s", type=float, default=config.DEFAULT_MIN_CLIP_S)
    p_run.add_argument("--max-s", type=float, default=config.DEFAULT_MAX_CLIP_S)
    p_run.add_argument("--style", default=config.DEFAULT_CAPTION_STYLE,
                       choices=list(__import__("rockyx_clipper.captions", fromlist=["STYLES"]).STYLES))
    p_run.add_argument("--language", default=config.DEFAULT_LANGUAGE)
    p_run.add_argument("--model", default=config.DEFAULT_WHISPER_MODEL)
    p_run.add_argument("--scorer", default="auto",
                       choices=["auto", "gemini", "heuristic", "local-ml"])
    p_run.add_argument("--section", default=None, help="YouTube only: START-END seconds")
    p_run.add_argument("--no-track", action="store_true", help="centre crop, no face tracking")

    p_serve = sub.add_parser("serve", help="start the localhost web UI")
    p_serve.add_argument("--port", type=int, default=8000)
    p_serve.add_argument("--host", default="127.0.0.1")

    p_probe = sub.add_parser("probe", help="check Gemini + ffmpeg + whisper setup")
    args = parser.parse_args(argv)

    if args.cmd == "serve":
        from rockyx_clipper.app import run_server
        run_server(host=args.host, port=args.port)
        return 0
    if args.cmd == "probe":
        from rockyx_clipper import gemini_client
        import shutil
        print("ffmpeg:", shutil.which("ffmpeg") or "MISSING")
        print("ffprobe:", shutil.which("ffprobe") or "MISSING")
        try:
            print("gemini:", gemini_client.probe())
        except Exception as exc:  # noqa: BLE001
            print("gemini: FAILED -", exc)
        return 0

    # Default: run (allow `python -m rockyx_clipper <source>` without "run").
    if args.cmd is None:
        # Re-parse with the run parser.
        args = p_run.parse_args(argv)
        args.cmd = "run"
    if args.cmd != "run":
        parser.print_help()
        return 2

    job_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    job_dir = Path(args.out) if args.out else config.JOBS_DIR / job_id
    opts = {
        "num_clips": args.num_clips, "min_s": args.min_s, "max_s": args.max_s,
        "style": args.style, "language": args.language, "model": args.model,
        "scorer": args.scorer, "section": _parse_section(args.section),
        "track": not args.no_track,
    }
    print(f"Rockyx Auto-Clipper v{config.VERSION} — job {job_dir}")
    try:
        summary = run_job(args.source, job_dir, opts)
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2))
    print(f"\nClips in {job_dir / 'clips'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
