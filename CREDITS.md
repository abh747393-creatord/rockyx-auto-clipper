# Rocky x Auto-Clipper — CREDITS & LICENSES

Free, local, no watermark, no minute limits. Built by combining the best
free open-source clipping tools, plus paid tools' *features* re-implemented
with open components (their code is closed-source and was NOT copied).

## Foundation

**OpenClip Studio** — https://github.com/paragbml/open-clip-studio — MIT
The foundation of this tool. Vendored (adapted) into `src/rockyx_clipper/`:
- `transcribe.py` ← `server/services/transcribe_local.py` (faster-whisper,
  word timestamps, VAD; adapted: adaptive CPU threads, neutral prompt)
- `track.py` ← `server/services/tracker_local.py` (YuNet face detection,
  dual-speaker clustering, EMA + deadband + Gaussian smoothing; adapted:
  package model path, `shutil.which` ffmpeg, face-width + face-height
  trajectory for auto-zoom / vertical centring)
- `ml_local/` ← `server/ml/` (virality_inference, feature_extractor,
  semantic_scorer, acoustic_analyzer, virality_model.pkl, MiniLM tokenizer;
  adapted: relative imports; optional — skipped gracefully if deps missing)
- `models/yunet_2023mar.onnx` ← `server/services/models/` (YuNet face model)
License: `licenses/open-clip-studio-MIT.txt`. Original repo stays untouched
in `vendor/open-clip-studio/`.

## What was taken from each other tool

**AutoClip** — https://github.com/zhouxiaoka/autoclip — MIT
- Pipeline step design (outline → timeline → scoring → title → clustering
  → video) and the idea of speaker-tracked reframe + cover/post-text.
- No code copied (its prompts are Chinese; ours are original English).
  License: `licenses/autoclip-MIT.txt`. Repo in `vendor/autoclip/`.

**SupoClip** — https://github.com/FujiwaraChoki/supoclip — AGPL-3.0
- Web-UI flow (paste link → live progress → ranked clips → editor),
  virality dimensions (hook / engagement / value / shareability),
  hook titles, trim/split/merge editor concept.
- IDEAS ONLY — no SupoClip code is in this project (AGPL code was not
  copied). Its LICENSE is preserved at `licenses/supoclip-AGPL-3.0.txt`
  and the repo stays in `vendor/supoclip/`.

**Video Wizard** — https://github.com/el-frontend/video-wizard — MIT
- 0–100 viral scoring design and the 9 caption-template idea
  (Hormozi / MrBeast / Minimal / Neon styles, our own ASS implementation).
  License: `licenses/video-wizard-MIT.txt`. Repo in `vendor/video-wizard/`.

**OpenShorts** — https://github.com/mutonby/openshorts — MIT
- Split-screen layout for two speakers, hook grounding, caption-on-the-seam,
  active-speaker concept. License: `licenses/openshorts-MIT.txt`.
  Repo in `vendor/openshorts/`.

## Paid tools' features (re-implemented, not copied)

| Paid feature | How Rocky x does it (open components) |
|---|---|
| Opus Clip / Vizard virality score 0–100 + ranking | Gemini LLM scoring + OpenClip local ML model + heuristic scorer |
| Opus / Klap face-aware 9:16 reframe + auto-zoom | YuNet face tracking (OpenCV) + face-size auto-zoom |
| Submagic / Crayo kinetic word captions | ASS word-highlight captions, 4 styles (our renderer) |
| Klap / Quso multi-language captions | Whisper auto-detect + language select (en/hi/ur/auto) |
| Vizard / 2short hook titles + hashtags | Gemini generates hook title + title + hashtags per clip |
| Descript transcript editor | Web UI: edit start/end/hook/style, re-render clip |
| Opus dual-speaker split-screen | Tracker detects 2 speakers → stacked layout, captions on seam |
| Opus / Vizard B-roll | Gemini suggests B-roll per clip (text suggestion in v1) |
| Vizard / SendShort scheduling + posting | Export caption pack + saved schedule; auto-post needs platform OAuth (out of scope v1) |
| Ssemble / WayinVideo cheap exports | 1080×1920 H.264 crf 18, loudnorm −16 LUFS, no watermark, unlimited |

## This project's own code

`src/rockyx_clipper/download.py`, `gemini_client.py`, `score.py`,
`captions.py`, `render.py`, `pipeline.py`, `app.py`, `__main__.py`,
`config.py`, `prompts/`, `static/index.html` — written for this project.
Free to use; keep the attributions above when redistributing.
