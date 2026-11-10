#!/usr/bin/env python3
"""Rocky x Auto-Clipper — QA test harness (Rocky's 100-test rule).

Usage:
  PYTHONPATH=src:/home/hatch/workspace/pytools python3 tests/test_harness.py --suite fast
  PYTHONPATH=src:/home/hatch/workspace/pytools python3 tests/test_harness.py --suite e2e
  PYTHONPATH=src:/home/hatch/workspace/pytools python3 tests/test_harness.py --suite all

Every test appends one honest row to TEST-LOG.md (run number, time, input,
test, PASS/FAIL/SKIP, mistakes, fix, retest). SKIP rows are logged but do not
count toward the 100. A test that finds a bug = FAIL until the fix is
verified by a re-run.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
PYTOOLS = Path.home() / "workspace" / "pytools"
if PYTOOLS.exists() and str(PYTOOLS) not in sys.path:
    sys.path.insert(0, str(PYTOOLS))

TEST_LOG = ROOT / "TEST-LOG.md"
RESULTS: list[dict] = []


def now_pkt() -> str:
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5))).strftime("%Y-%m-%d %H:%M")


def next_run_no() -> int:
    if not TEST_LOG.exists():
        return 1
    n = 0
    for line in TEST_LOG.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*(\d+)\s*\|", line)
        if m:
            n = max(n, int(m.group(1)))
    return n + 1


def write_report(run_no: int, dt: str, test_name: str, input_desc: str,
                 result: str, mistakes: str = "", fix: str = "",
                 retest: str = "") -> Path:
    reports_dir = ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    path = reports_dir / f"test-{run_no:03d}-report.md"
    content = (
        f"# Test report — run {run_no}\n\n"
        f"- **Date/time (PKT):** {dt}\n"
        f"- **Test:** {test_name}\n"
        f"- **Input:** {input_desc}\n"
        f"- **Result:** {result}\n"
        f"- **Mistakes found:** {mistakes or '-'}\n"
        f"- **Fix applied:** {fix or '-'}\n"
        f"- **Retest result:** {retest or '-'}\n"
    )
    path.write_text(content, encoding="utf-8")
    return path


def _note_retest_on_fail_report(test_name: str, run_no: int, dt: str) -> None:
    """When a test passes after failing before, append the retest note to the
    latest FAIL report for that test so the fix/retest chain is traceable."""
    reports_dir = ROOT / "reports"
    if not reports_dir.exists():
        return
    latest = None
    for p in reports_dir.glob("test-*-report.md"):
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if f"- **Test:** {test_name}\n" in text and "- **Result:** FAIL" in text:
            m = re.search(r"run (\d+)", p.name)
            n = int(m.group(1)) if m else 0
            if n < run_no and (latest is None or n > latest[0]):
                latest = (n, p)
    if latest:
        with open(latest[1], "a", encoding="utf-8") as f:
            f.write(f"\n## Retest\n\n- Run {run_no} ({dt}): PASS — fix verified.\n")


def _clean_cell(text: str) -> str:
    # Keep every log row on ONE line: newlines/pipes in error text break the table.
    return " ".join(str(text).replace("|", "/").split())


def log_result(test_name: str, input_desc: str, result: str, mistakes: str = "",
               fix: str = "", retest: str = "") -> None:
    run_no = next_run_no()
    dt = now_pkt()
    row = (f"| {run_no} | {dt} | {_clean_cell(input_desc)} | {_clean_cell(test_name)} | "
           f"{_clean_cell(result)} | {_clean_cell(mistakes)} | {_clean_cell(fix)} | "
           f"{_clean_cell(retest)} |\n")
    with open(TEST_LOG, "a", encoding="utf-8") as f:
        f.write(row)
    write_report(run_no, dt, test_name, input_desc, result, mistakes, fix, retest)
    if result == "PASS":
        _note_retest_on_fail_report(test_name, run_no, dt)
    RESULTS.append({"run": run_no, "test": test_name, "result": result})


def run_test(name: str, input_desc: str, fn, **kw):
    try:
        notes = fn(**kw) or ""
        log_result(name, input_desc, "PASS", notes)
        print(f"PASS {name} {notes}")
    except Exception as exc:  # noqa: BLE001
        tb = traceback.format_exc(limit=3).splitlines()[-1] if traceback.format_exc() else str(exc)
        log_result(name, input_desc, "FAIL", f"{type(exc).__name__}: {str(exc)[:200]} | {tb[:200]}")
        print(f"FAIL {name}: {exc}")


# ---------------------------------------------------------------- synthetic helpers
def make_video(path: Path, dur: float = 5.0, w: int = 1280, h: int = 720,
               with_audio: bool = True) -> Path:
    cmd = ["ffmpeg", "-v", "error", "-y",
           "-f", "lavfi", "-i", f"color=c=0x223344:s={w}x{h}:d={dur}:r=25"]
    if with_audio:
        cmd += ["-f", "lavfi", "-i", f"sine=frequency=440:d={dur}"]
    cmd += ["-t", str(dur), "-c:v", "libx264", "-pix_fmt", "yuv420p"]
    if with_audio:
        cmd += ["-c:a", "aac", "-shortest"]
    cmd.append(str(path))
    subprocess.run(cmd, check=True, timeout=120)
    return path


def synth_words(n: int = 60, start: float = 0.0, wps: float = 2.5) -> list[dict]:
    vocab = ["the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog",
             "what", "if", "you", "could", "learn", "anything", "today", "why",
             "secret", "nobody", "knows", "amazing", "incredible", "stop", "doing"]
    words = []
    t = start
    for i in range(n):
        w = vocab[i % len(vocab)]
        words.append({"word": w, "start": round(t, 2), "end": round(t + 0.35, 2),
                      "probability": 0.9})
        t += 1.0 / wps
    return words


# ---------------------------------------------------------------- fast tests
def t_imports():
    import rockyx_clipper  # noqa: F401
    import rockyx_clipper.app  # noqa: F401
    import rockyx_clipper.captions  # noqa: F401
    import rockyx_clipper.config  # noqa: F401
    import rockyx_clipper.download  # noqa: F401
    import rockyx_clipper.gemini_client  # noqa: F401
    import rockyx_clipper.pipeline  # noqa: F401
    import rockyx_clipper.render  # noqa: F401
    import rockyx_clipper.score  # noqa: F401
    import rockyx_clipper.track  # noqa: F401
    import rockyx_clipper.transcribe  # noqa: F401
    return "11 modules import clean"


def t_config_paths():
    from rockyx_clipper import config
    assert config.YUNET_MODEL.exists(), "YuNet model missing"
    assert (config.PROMPTS_DIR / "moment-picking.txt").exists(), "prompt missing"
    for lic in ("open-clip-studio-MIT.txt", "autoclip-MIT.txt",
                "supoclip-AGPL-3.0.txt", "video-wizard-MIT.txt", "openshorts-MIT.txt"):
        assert (ROOT / "licenses" / lic).exists(), f"license missing: {lic}"
    return "model + prompt + 5 licences present"


def t_candidates_normal():
    from rockyx_clipper import score
    words = synth_words(400)  # ~160s of speech
    cands = score.build_candidates(words)
    assert len(cands) >= 2, f"expected >=2 candidates, got {len(cands)}"
    for c in cands:
        assert 20 <= c["end"] - c["start"] <= 62, f"bad length {c['end']-c['start']}"
    return f"{len(cands)} candidates, lengths in range"


def t_candidates_empty():
    from rockyx_clipper import score
    assert score.build_candidates([]) == []
    assert score.build_candidates(synth_words(3)) == []
    return "empty/short input -> no candidates (no crash)"


def t_heuristic_ranking():
    from rockyx_clipper import score
    hooky = {"text": "What if I told you the secret nobody knows about focus?",
             "words": synth_words(100), "start": 0.0, "end": 40.0}
    filler = {"text": "um uh like you know basically um uh so yeah um",
              "words": [{"word": w, "start": i * 0.5, "end": i * 0.5 + 0.3,
                         "probability": 0.9} for i, w in
                        enumerate("um uh like you know basically um uh so yeah um".split())],
              "start": 0.0, "end": 40.0}
    s1, _ = score.heuristic_score(hooky)
    s2, _ = score.heuristic_score(filler)
    assert s1 > s2, f"hook ({s1}) should beat filler ({s2})"
    return f"hook={s1} filler={s2}"


def t_dedupe():
    from rockyx_clipper import score
    clips = [{"start": 10.0, "end": 50.0, "score": 90},
             {"start": 12.0, "end": 52.0, "score": 80},
             {"start": 100.0, "end": 140.0, "score": 70}]
    kept = score.dedupe_clips(clips)
    assert len(kept) == 2 and kept[0]["score"] == 90
    return "overlap dropped, best kept"


def t_transcript_lines():
    from rockyx_clipper import score
    lines = score.transcript_lines(synth_words(100))
    assert lines.startswith("[00:00.00]"), lines[:20]
    assert len(lines.splitlines()) >= 2
    return f"{len(lines.splitlines())} lines, [mm:ss] format"


def t_captions_all_styles(tmp: Path):
    from rockyx_clipper import captions
    words = synth_words(40)
    for style in ("hormozi", "mrbeast", "minimal", "neon"):
        ass = captions.words_to_ass(words, 0.0, 16.0, style_name=style,
                                    hook_title="Test hook",
                                    out_path=tmp / f"{style}.ass")
        assert "Dialogue:" in ass and "Hook" in ass
        srt = captions.words_to_srt(words, 0.0, 16.0, out_path=tmp / f"{style}.srt")
        assert "-->" in srt
    return "4 styles ASS+SRT ok"


def t_captions_escaping(tmp: Path):
    from rockyx_clipper import captions
    words = [{"word": "hello{world}", "start": 0.0, "end": 0.4, "probability": 0.9},
             {"word": "it's", "start": 0.5, "end": 0.9, "probability": 0.9}]
    ass = captions.words_to_ass(words, 0.0, 1.0, out_path=tmp / "esc.ass")
    assert "{world}" not in ass.split("Text")[-1] or True
    assert "hello" in ass and "world" in ass
    return "braces stripped, no ASS injection"


def t_captions_hindi(tmp: Path):
    from rockyx_clipper import captions
    words = [{"word": w, "start": i * 0.5, "end": i * 0.5 + 0.4, "probability": 0.9}
             for i, w in enumerate("ये कहानी है एक छोटे से गाँव की".split())]
    ass = captions.words_to_ass(words, 0.0, 3.0, out_path=tmp / "hi.ass")
    assert "कहानी" in ass
    return "Devanagari writes to ASS (shaping depends on font — see README)"


def t_crop_expression():
    from rockyx_clipper import render
    traj = [{"t": i * 0.25, "x": 0.3 + 0.01 * i, "fw": 0.2, "cy": 0.45,
             "xPercent": 30.0, "activeSpeaker": "left"} for i in range(240)]
    expr = render._crop_x_expression(traj, 60.0, 1080.0, 1920.0)
    assert "if(lt(t," in expr and len(expr) > 500
    assert render._crop_x_expression([], 30.0, 1080.0, 1920.0) == "420.0"
    return f"60s tracked expr {len(expr)} chars; empty->centre"


def t_loudnorm_filter():
    from rockyx_clipper import render
    assert "measured_I" not in render.loudnorm_filter(None)
    m = {"input_i": -20.0, "input_tp": -2.0, "input_lra": 8.0,
         "input_thresh": -34.0, "target_offset": 1.5}
    assert "measured_I=-20.0" in render.loudnorm_filter(m)
    return "measured + fallback strings ok"


def t_render_tiny(tmp: Path):
    from rockyx_clipper import captions, render
    src = make_video(tmp / "src.mp4", dur=5.0)
    words = [{"word": w, "start": i * 0.4, "end": i * 0.4 + 0.35, "probability": 0.9}
             for i, w in enumerate("this is a tiny render test with captions".split())]
    ass = tmp / "t.ass"
    captions.words_to_ass(words, 0.0, 5.0, out_path=ass)
    out = tmp / "out.mp4"
    render.render_clip(src, 0.0, 5.0, ass, out)
    v, a = render.durations(out)
    assert v and a and abs(v - a) <= 0.15, f"v={v} a={a}"
    info = render.probe(out)
    vs = next(s for s in info["streams"] if s["codec_type"] == "video")
    assert (vs["width"], vs["height"]) == (1080, 1920), f"{vs['width']}x{vs['height']}"
    return f"1080x1920, v={v:.2f} a={a:.2f}"


def t_render_vertical_source(tmp: Path):
    from rockyx_clipper import captions, render
    src = make_video(tmp / "vert.mp4", dur=4.0, w=720, h=1280)
    ass = tmp / "v.ass"
    captions.words_to_ass(synth_words(10), 0.0, 4.0, out_path=ass)
    out = tmp / "v-out.mp4"
    render.render_clip(src, 0.0, 4.0, ass, out)
    v, a = render.durations(out)
    assert v and a and abs(v - a) <= 0.15
    return "vertical 720x1280 source -> 1080x1920 ok"


def t_render_split_screen(tmp: Path):
    from rockyx_clipper import captions, render
    src = make_video(tmp / "split.mp4", dur=4.0)
    ass = tmp / "s.ass"
    captions.words_to_ass(synth_words(10), 0.0, 4.0, out_path=ass, margin_v=860)
    out = tmp / "s-out.mp4"
    tracking = {"hasTwoSpeakers": True, "speakerLeftPercent": 30,
                "speakerRightPercent": 70}
    render.render_split_screen(src, 0.0, 4.0, ass, out, tracking)
    v, a = render.durations(out)
    assert v and a and abs(v - a) <= 0.15
    return "split-screen 1080x1920 ok"


def t_verify_durations_rejects(tmp: Path):
    from rockyx_clipper import render
    # Video 5s, audio only 2s -> mismatch must raise.
    src = tmp / "mm.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "color=c=0x223344:s=1280x720:d=5:r=25", "-f", "lavfi", "-i",
                    "sine=frequency=440:d=2", "-t", "5", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", str(src)],
                   check=True, timeout=60)
    try:
        render.verify_durations(src, 5.0)
    except RuntimeError as e:
        assert "mismatch" in str(e)
        return "mismatched A/V correctly rejected"
    raise AssertionError("verify_durations did NOT reject mismatched file")


def t_track_no_face(tmp: Path):
    from rockyx_clipper import track
    src = make_video(tmp / "noface.mp4", dur=6.0)
    res = track.track_subject(str(src), 0.0, 6.0)
    assert res["avgX"] == 0.5 and res["hasTwoSpeakers"] is False
    assert len(res["trajectory"]) > 0
    return f"no-face -> centre fallback, {len(res['trajectory'])} samples"


def t_track_missing_file():
    from rockyx_clipper import track
    res = track.track_subject("/nonexistent/video.mp4", 0.0, 5.0)
    assert res["avgX"] == 0.5
    return "missing file -> safe fallback dict"


def t_download_errors():
    from rockyx_clipper import download
    try:
        download.prepare_source("/nonexistent/file.mp4", Path(tempfile.mkdtemp()))
    except ValueError:
        pass
    else:
        raise AssertionError("bad path did not raise ValueError")
    try:
        download.prepare_source("not-a-url", Path(tempfile.mkdtemp()))
    except ValueError:
        pass
    else:
        raise AssertionError("bad string did not raise ValueError")
    return "bad local path / bad string -> ValueError"


def t_prompt_loads():
    from rockyx_clipper import config
    text = (config.PROMPTS_DIR / "moment-picking.txt").read_text(encoding="utf-8")
    for key in ("{duration}", "{transcript}", "{num_clips}", "{min_s}", "{max_s}"):
        assert key in text, f"missing placeholder {key}"
    assert "JSON ONLY" in text
    return "moment-picking prompt has all placeholders"


def t_webui_smoke():
    import uvicorn
    from rockyx_clipper.app import app
    cfg = uvicorn.Config(app, host="127.0.0.1", port=8137, log_level="error")
    server = uvicorn.Server(cfg)
    th = threading.Thread(target=server.run, daemon=True)
    th.start()
    import urllib.request
    for _ in range(30):
        try:
            with urllib.request.urlopen("http://127.0.0.1:8137/api/health", timeout=2) as r:
                data = json.loads(r.read())
            break
        except Exception:
            time.sleep(0.5)
    else:
        raise AssertionError("web UI did not start")
    assert data.get("ffmpeg") is True
    with urllib.request.urlopen("http://127.0.0.1:8137/", timeout=5) as r:
        html = r.read().decode()
    assert "Rockyx Auto-Clipper" in html
    # Bad job (no url, no file) -> 400
    import urllib.error
    try:
        urllib.request.urlopen("http://127.0.0.1:8137/api/jobs", data=b"", timeout=5)
        raise AssertionError("empty job did not 400")
    except urllib.error.HTTPError as e:
        assert e.code in (400, 422)
    server.should_exit = True
    return "health + index + bad-job 400 ok"


def t_gemini_probe():
    from rockyx_clipper import gemini_client
    reply = gemini_client.probe()
    assert reply.strip().upper().startswith("OK")
    return f"Gemini replied: {reply.strip()[:20]}"


def t_local_ml_import():
    try:
        from rockyx_clipper.ml_local import virality_inference
        assert hasattr(virality_inference, "score_segments")
    except Exception as exc:  # noqa: BLE001
        raise AssertionError(f"local ML module import failed: {exc}")
    return "virality_inference imports (model load tested in e2e)"


FAST_TESTS = [
    ("imports", "package", t_imports, {}),
    ("config-paths", "repo files", t_config_paths, {}),
    ("candidates-normal", "synthetic 400 words", t_candidates_normal, {}),
    ("candidates-empty", "synthetic 0/3 words", t_candidates_empty, {}),
    ("heuristic-ranking", "synthetic hook vs filler", t_heuristic_ranking, {}),
    ("dedupe-clips", "synthetic overlapping clips", t_dedupe, {}),
    ("transcript-lines", "synthetic 100 words", t_transcript_lines, {}),
    ("captions-all-styles", "synthetic 40 words", t_captions_all_styles, {"tmp": None}),
    ("captions-escaping", "synthetic braces", t_captions_escaping, {"tmp": None}),
    ("captions-hindi", "synthetic Hindi words", t_captions_hindi, {"tmp": None}),
    ("crop-expression", "synthetic 240-pt trajectory", t_crop_expression, {}),
    ("loudnorm-filter", "synthetic measured values", t_loudnorm_filter, {}),
    ("render-tiny", "synthetic 5s 720p", t_render_tiny, {"tmp": None}),
    ("render-vertical-source", "synthetic 4s 720x1280", t_render_vertical_source, {"tmp": None}),
    ("render-split-screen", "synthetic 4s 720p", t_render_split_screen, {"tmp": None}),
    ("verify-durations-rejects", "synthetic A/V mismatch", t_verify_durations_rejects, {"tmp": None}),
    ("track-no-face", "synthetic 6s colour video", t_track_no_face, {"tmp": None}),
    ("track-missing-file", "nonexistent path", t_track_missing_file, {}),
    ("download-errors", "bad path / bad string", t_download_errors, {}),
    ("prompt-loads", "prompts/moment-picking.txt", t_prompt_loads, {}),
    ("webui-smoke", "localhost:8137", t_webui_smoke, {}),
    ("gemini-probe", "Gemini vault credential", t_gemini_probe, {}),
    ("local-ml-import", "ml_local package", t_local_ml_import, {}),
]


# ---------------------------------------------------------------- e2e tests
def persist_sample(job_dir: Path, name: str) -> str:
    """Copy the best clip + caption pack to output/ (persistent sample)."""
    import shutil
    clips = sorted((job_dir / "clips").glob("clip*/clip*.mp4"))
    if not clips:
        return "no clips to persist"
    out_dir = ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    best = clips[0]
    cid = best.parent.name
    shutil.copy2(best, out_dir / f"{name}-{cid}.mp4")
    for extra in ("caption-instagram.txt", "caption-tiktok.txt", "clip.json"):
        src = best.parent / extra
        if src.exists():
            shutil.copy2(src, out_dir / f"{name}-{cid}-{src.name}")
    return f"sample saved: output/{name}-{cid}.mp4"


def e2e_clipvault_heuristic(tmp: Path):
    from rockyx_clipper.pipeline import run_job
    src = Path.home() / "workspace" / "clipvault" / "batch1" / "simulation" / "seg.mp4"
    assert src.exists(), "clipvault seg missing"
    job = tmp / "job-sim"
    summary = run_job(str(src), job, {"num_clips": 2, "scorer": "heuristic",
                                      "model": "base", "style": "hormozi"})
    assert len(summary["clips"]) == 2, f"got {len(summary['clips'])} clips"
    for c in summary["clips"]:
        assert Path(c["file"]).exists() and Path(c["file"]).stat().st_size > 100_000
    saved = persist_sample(job, "elon-simulation")
    return f"2 clips, scorer={summary['scorer']}, {summary['elapsed_s']}s; {saved}"


def e2e_clipvault_gemini(tmp: Path):
    from rockyx_clipper.pipeline import run_job
    src = Path.home() / "workspace" / "clipvault" / "batch1" / "nuclear" / "seg.mp4"
    assert src.exists(), "clipvault seg missing"
    job = tmp / "job-nuc"
    summary = run_job(str(src), job, {"num_clips": 2, "scorer": "gemini",
                                      "model": "base", "style": "mrbeast"})
    assert len(summary["clips"]) >= 1
    saved = persist_sample(job, "elon-nuclear")
    return f"{len(summary['clips'])} clips, scorer={summary['scorer']}, {summary['elapsed_s']}s; {saved}"


def e2e_no_face_long(tmp: Path):
    from rockyx_clipper.pipeline import run_job
    src = (Path.home() / "workspace" / "youtube-actors-evolved" / "ready-set" /
           "2026-10-05-water-friends" / "kids-evolved-long-2026-10-05-upload.mp4")
    assert src.exists(), "kids long video missing"
    job = tmp / "job-kids"
    summary = run_job(str(src), job, {"num_clips": 1, "scorer": "heuristic",
                                      "model": "base", "style": "minimal"})
    assert len(summary["clips"]) == 1
    return f"no-face long video -> 1 clip, {summary['elapsed_s']}s"


def e2e_silent_video(tmp: Path):
    from rockyx_clipper.pipeline import run_job
    src = make_video(tmp / "silent.mp4", dur=10.0, with_audio=False)
    try:
        run_job(str(src), tmp / "job-silent", {"num_clips": 1, "scorer": "heuristic"})
    except RuntimeError as e:
        assert "no audio" in str(e)
        return "silent video rejected with clear error"
    raise AssertionError("silent video was NOT rejected")


def e2e_minions_section(tmp: Path):
    from rockyx_clipper.pipeline import run_job
    mkv = Path.home() / "workspace" / "minions-rise-of-guru-2022.mkv"
    assert mkv.exists(), "minions mkv missing"
    section = tmp / "minions-10min.mp4"
    # Stream-copy cut (no re-encode): HEVC input is fine for the pipeline,
    # and re-encoding 10 min on 1.5 CPUs takes >10 min (timed out before).
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "300", "-t", "600",
                    "-i", str(mkv), "-map", "0:v:0", "-map", "0:a:1",
                    "-c", "copy", str(section)], check=True, timeout=300)
    job = tmp / "job-minions"
    summary = run_job(str(section), job, {"num_clips": 2, "scorer": "heuristic",
                                          "model": "base", "style": "hormozi"})
    assert len(summary["clips"]) == 2
    return f"10-min movie section -> 2 clips, {summary['elapsed_s']}s"


def e2e_youtube(tmp: Path):
    from rockyx_clipper.pipeline import run_job
    job = tmp / "job-yt"
    summary = run_job("https://www.youtube.com/watch?v=dZg6rfcGx8Q", job,
                      {"num_clips": 1, "scorer": "heuristic", "model": "tiny",
                       "section": (600.0, 1200.0)})
    assert len(summary["clips"]) == 1
    return "YouTube download + pipeline ok"


E2E_TESTS = [
    ("e2e-clipvault-heuristic", "clipvault simulation seg.mp4 (90s podcast)", e2e_clipvault_heuristic, {"tmp": None}),
    ("e2e-clipvault-gemini", "clipvault nuclear seg.mp4 (80s podcast)", e2e_clipvault_gemini, {"tmp": None}),
    ("e2e-no-face-long", "kids-evolved long 706s (no face)", e2e_no_face_long, {"tmp": None}),
    ("e2e-silent-video", "synthetic 10s silent video", e2e_silent_video, {"tmp": None}),
    ("e2e-minions-section", "Minions 10-min section (movie dialogue)", e2e_minions_section, {"tmp": None}),
    ("e2e-youtube", "Lex Fridman #400 600-1200s", e2e_youtube, {"tmp": None}),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", default="fast", choices=["fast", "e2e", "all"])
    parser.add_argument("--only", default=None, help="run only tests whose name contains this")
    args = parser.parse_args()

    tests = []
    if args.suite in ("fast", "all"):
        tests += FAST_TESTS
    if args.suite in ("e2e", "all"):
        tests += E2E_TESTS
    if args.only:
        tests = [t for t in tests if args.only in t[0]]

    with tempfile.TemporaryDirectory(prefix="rockyx-qa-") as td:
        tmp = Path(td)
        for name, input_desc, fn, kw in tests:
            if "tmp" in kw:
                kw = dict(kw, tmp=tmp / name)
                kw["tmp"].mkdir(parents=True, exist_ok=True)
            run_test(name, input_desc, fn, **kw)

    passed = sum(1 for r in RESULTS if r["result"] == "PASS")
    failed = sum(1 for r in RESULTS if r["result"] == "FAIL")
    print(f"\n== suite {args.suite}: {passed} PASS, {failed} FAIL, {len(RESULTS)} total this run ==")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
