# Rocky x Auto-Clipper — TEST LOG

Rocky's QA rule: **minimum 100 test runs before handover.** Every run is
logged honestly — run number, time, input, what was tested, result,
mistakes found, fix applied, retest result. Never fake a count.

| Run | Date/time (PKT) | Input | Test | Result | Mistakes found | Fix applied | Retest |
|-----|-----------------|-------|------|--------|----------------|-------------|--------|
| 1 | 2026-11-10 02:56 | package | imports | PASS | 11 modules import clean |  |  |
| 2 | 2026-11-10 02:56 | repo files | config-paths | PASS | model + prompt + 5 licences present |  |  |
| 3 | 2026-11-10 02:56 | synthetic 400 words | candidates-normal | PASS | 14 candidates, lengths in range |  |  |
| 4 | 2026-11-10 02:56 | synthetic 0/3 words | candidates-empty | PASS | empty/short input -> no candidates (no crash) |  |  |
| 5 | 2026-11-10 02:56 | synthetic hook vs filler | heuristic-ranking | PASS | hook=27.0 filler=15.4 |  |  |
| 6 | 2026-11-10 02:56 | synthetic overlapping clips | dedupe-clips | PASS | overlap dropped, best kept |  |  |
| 7 | 2026-11-10 02:56 | synthetic 100 words | transcript-lines | PASS | 2 lines, [mm:ss] format |  |  |
| 8 | 2026-11-10 02:56 | synthetic 40 words | captions-all-styles | PASS | 4 styles ASS+SRT ok |  |  |
| 9 | 2026-11-10 02:56 | synthetic braces | captions-escaping | PASS | braces stripped, no ASS injection |  |  |
| 10 | 2026-11-10 02:56 | synthetic Hindi words | captions-hindi | PASS | Devanagari writes to ASS (shaping depends on font — see README) |  |  |
| 11 | 2026-11-10 02:56 | synthetic 240-pt trajectory | crop-expression | PASS | 60s tracked expr 1246 chars; empty->centre |  |  |
| 12 | 2026-11-10 02:56 | synthetic measured values | loudnorm-filter | PASS | measured + fallback strings ok |  |  |
| 13 | 2026-11-10 02:57 | synthetic 5s 720p | render-tiny | PASS | 1080x1920, v=5.00 a=5.00 |  |  |
| 14 | 2026-11-10 02:57 | synthetic 4s 720x1280 | render-vertical-source | PASS | vertical 720x1280 source -> 1080x1920 ok |  |  |
| 15 | 2026-11-10 02:57 | synthetic 4s 720p | render-split-screen | PASS | split-screen 1080x1920 ok |  |  |
| 16 | 2026-11-10 02:57 | synthetic A/V mismatch | verify-durations-rejects | PASS | mismatched A/V correctly rejected |  |  |
| 17 | 2026-11-10 02:57 | synthetic 6s colour video | track-no-face | PASS | no-face -> centre fallback, 24 samples |  |  |
| 18 | 2026-11-10 02:57 | nonexistent path | track-missing-file | PASS | missing file -> safe fallback dict |  |  |
| 19 | 2026-11-10 02:57 | bad path / bad string | download-errors | PASS | bad local path / bad string -> ValueError |  |  |
| 20 | 2026-11-10 02:57 | prompts/moment-picking.txt | prompt-loads | PASS | moment-picking prompt has all placeholders |  |  |
| 21 | 2026-11-10 02:57 | localhost:8137 | webui-smoke | PASS | health + index + bad-job 400 ok |  |  |
| 22 | 2026-11-10 02:57 | Gemini vault credential | gemini-probe | PASS | Gemini replied: OK |  |  |
| 23 | 2026-11-10 02:57 | ml_local package | local-ml-import | PASS | virality_inference imports (model load tested in e2e) |  |  |
| 24 | 2026-11-10 02:57 | package | imports | PASS | 11 modules import clean |  |  |
| 25 | 2026-11-10 02:57 | repo files | config-paths | PASS | model + prompt + 5 licences present |  |  |
| 26 | 2026-11-10 02:57 | synthetic 400 words | candidates-normal | PASS | 14 candidates, lengths in range |  |  |
| 27 | 2026-11-10 02:57 | synthetic 0/3 words | candidates-empty | PASS | empty/short input -> no candidates (no crash) |  |  |
| 28 | 2026-11-10 02:57 | synthetic hook vs filler | heuristic-ranking | PASS | hook=42.0 filler=15.4 |  |  |
| 29 | 2026-11-10 02:57 | synthetic overlapping clips | dedupe-clips | PASS | overlap dropped, best kept |  |  |
| 30 | 2026-11-10 02:57 | synthetic 100 words | transcript-lines | PASS | 2 lines, [mm:ss] format |  |  |
| 31 | 2026-11-10 02:57 | synthetic 40 words | captions-all-styles | PASS | 4 styles ASS+SRT ok |  |  |
| 32 | 2026-11-10 02:57 | synthetic braces | captions-escaping | PASS | braces stripped, no ASS injection |  |  |
| 33 | 2026-11-10 02:57 | synthetic Hindi words | captions-hindi | PASS | Devanagari writes to ASS (shaping depends on font — see README) |  |  |
| 34 | 2026-11-10 02:57 | synthetic 240-pt trajectory | crop-expression | PASS | 60s tracked expr 1246 chars; empty->centre |  |  |
| 35 | 2026-11-10 02:57 | synthetic measured values | loudnorm-filter | PASS | measured + fallback strings ok |  |  |
| 36 | 2026-11-10 02:57 | synthetic 5s 720p | render-tiny | PASS | 1080x1920, v=5.00 a=5.00 |  |  |
| 37 | 2026-11-10 02:57 | synthetic 4s 720x1280 | render-vertical-source | PASS | vertical 720x1280 source -> 1080x1920 ok |  |  |
| 38 | 2026-11-10 02:57 | synthetic 4s 720p | render-split-screen | PASS | split-screen 1080x1920 ok |  |  |
| 39 | 2026-11-10 02:57 | synthetic A/V mismatch | verify-durations-rejects | PASS | mismatched A/V correctly rejected |  |  |
| 40 | 2026-11-10 02:57 | synthetic 6s colour video | track-no-face | PASS | no-face -> centre fallback, 24 samples |  |  |
| 41 | 2026-11-10 02:57 | nonexistent path | track-missing-file | PASS | missing file -> safe fallback dict |  |  |
| 42 | 2026-11-10 02:57 | bad path / bad string | download-errors | PASS | bad local path / bad string -> ValueError |  |  |
| 43 | 2026-11-10 02:57 | prompts/moment-picking.txt | prompt-loads | PASS | moment-picking prompt has all placeholders |  |  |
| 44 | 2026-11-10 02:57 | localhost:8137 | webui-smoke | PASS | health + index + bad-job 400 ok |  |  |
| 45 | 2026-11-10 02:58 | Gemini vault credential | gemini-probe | PASS | Gemini replied: OK |  |  |
| 46 | 2026-11-10 02:58 | ml_local package | local-ml-import | PASS | virality_inference imports (model load tested in e2e) |  |  |
| 47 | 2026-11-10 02:58 | clipvault simulation seg.mp4 (90s podcast) | e2e-clipvault-heuristic | FAIL | TypeError: e2e_clipvault_heuristic() missing 1 required positional argument: 'tmp' | TypeError: e2e_clipvault_heuristic() missing 1 required positional argument: 'tmp' |  |  |
| 48 | 2026-11-10 02:58 | clipvault nuclear seg.mp4 (80s podcast) | e2e-clipvault-gemini | FAIL | TypeError: e2e_clipvault_gemini() missing 1 required positional argument: 'tmp' | TypeError: e2e_clipvault_gemini() missing 1 required positional argument: 'tmp' |  |  |
| 49 | 2026-11-10 02:58 | kids-evolved long 706s (no face) | e2e-no-face-long | FAIL | TypeError: e2e_no_face_long() missing 1 required positional argument: 'tmp' | TypeError: e2e_no_face_long() missing 1 required positional argument: 'tmp' |  |  |
| 50 | 2026-11-10 02:58 | synthetic 10s silent video | e2e-silent-video | FAIL | TypeError: e2e_silent_video() missing 1 required positional argument: 'tmp' | TypeError: e2e_silent_video() missing 1 required positional argument: 'tmp' |  |  |
| 51 | 2026-11-10 02:58 | Minions 10-min section (movie dialogue) | e2e-minions-section | FAIL | TypeError: e2e_minions_section() missing 1 required positional argument: 'tmp' | TypeError: e2e_minions_section() missing 1 required positional argument: 'tmp' |  |  |
| 52 | 2026-11-10 02:58 | Lex Fridman #400 600-1200s | e2e-youtube | FAIL | TypeError: e2e_youtube() missing 1 required positional argument: 'tmp' | TypeError: e2e_youtube() missing 1 required positional argument: 'tmp' |  |  |
| 53 | 2026-11-10 02:58 | localhost:8137 | webui-smoke | PASS | health + index + bad-job 400 ok |  |  |
| 54 | 2026-11-10 02:58 | synthetic hook vs filler | heuristic-ranking | PASS | hook=42.0 filler=15.4 |  |  |
| 55 | 2026-11-10 02:59 | prompts/moment-picking.txt | prompt-loads | PASS | moment-picking prompt has all placeholders |  |  |
| 56 | 2026-11-10 03:00 | clipvault simulation seg.mp4 (90s podcast) | e2e-clipvault-heuristic | FAIL | RuntimeError: rockyx_clipper.transcribe failed: Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads. |  |  |
| 57 | 2026-11-10 03:00 | clipvault nuclear seg.mp4 (80s podcast) | e2e-clipvault-gemini | FAIL | RuntimeError: rockyx_clipper.transcribe failed: Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads. |  |  |
| 58 | 2026-11-10 03:01 | kids-evolved long 706s (no face) | e2e-no-face-long | FAIL | RuntimeError: rockyx_clipper.transcribe failed: Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads. |  |  |
| 59 | 2026-11-10 03:01 | synthetic 10s silent video | e2e-silent-video | PASS | silent video rejected with clear error |  |  |
| 60 | 2026-11-10 03:11 | Minions 10-min section (movie dialogue) | e2e-minions-section | FAIL | TimeoutExpired: Command '['ffmpeg', '-v', 'error', '-y', '-ss', '300', '-t', '600', '-i', '/home/hatch/workspace/minions-rise-of-guru-2022.mkv', '-map', '0:v:0', '-map', '0:a:1', '-c:v', 'libx264', '-crf', '20', '-c: | subprocess.TimeoutExpired: Command '['ffmpeg', '-v', 'error', '-y', '-ss', '300', '-t', '600', '-i', '/home/hatch/workspace/minions-rise-of-guru-2022.mkv', '-map', '0:v:0', '-map', '0:a:1', '-c:v', 'l |  |  |
| 61 | 2026-11-10 03:11 | Lex Fridman #400 600-1200s | e2e-youtube | FAIL | RuntimeError: yt-dlp -J failed: outube] dZg6rfcGx8Q: Unable to download API page: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1000) (caused by Ce |  |  |  |
| 62 | 2026-11-10 03:18 | clipvault simulation seg.mp4 (90s podcast) | e2e-clipvault-heuristic | PASS | 2 clips, scorer=heuristic, 106.6s; sample saved: output/elon-simulation-clip01.mp4 |  |  |
| 63 | 2026-11-10 03:19 | package | imports | PASS | 11 modules import clean |  |  |
| 64 | 2026-11-10 03:19 | repo files | config-paths | PASS | model + prompt + 5 licences present |  |  |
| 65 | 2026-11-10 03:19 | synthetic 400 words | candidates-normal | PASS | 14 candidates, lengths in range |  |  |
| 66 | 2026-11-10 03:19 | synthetic 0/3 words | candidates-empty | PASS | empty/short input -> no candidates (no crash) |  |  |
| 67 | 2026-11-10 03:19 | synthetic hook vs filler | heuristic-ranking | PASS | hook=42.0 filler=15.4 |  |  |
| 68 | 2026-11-10 03:19 | synthetic overlapping clips | dedupe-clips | PASS | overlap dropped, best kept |  |  |
| 69 | 2026-11-10 03:19 | synthetic 100 words | transcript-lines | PASS | 2 lines, [mm:ss] format |  |  |
| 70 | 2026-11-10 03:19 | synthetic 40 words | captions-all-styles | PASS | 4 styles ASS+SRT ok |  |  |
| 71 | 2026-11-10 03:19 | synthetic braces | captions-escaping | PASS | braces stripped, no ASS injection |  |  |
| 72 | 2026-11-10 03:19 | synthetic Hindi words | captions-hindi | PASS | Devanagari writes to ASS (shaping depends on font — see README) |  |  |
| 73 | 2026-11-10 03:19 | synthetic 240-pt trajectory | crop-expression | PASS | 60s tracked expr 1246 chars; empty->centre |  |  |
| 74 | 2026-11-10 03:19 | synthetic measured values | loudnorm-filter | PASS | measured + fallback strings ok |  |  |
| 75 | 2026-11-10 03:19 | synthetic 5s 720p | render-tiny | PASS | 1080x1920, v=5.00 a=5.00 |  |  |
| 76 | 2026-11-10 03:20 | synthetic 4s 720x1280 | render-vertical-source | PASS | vertical 720x1280 source -> 1080x1920 ok |  |  |
| 77 | 2026-11-10 03:20 | synthetic 4s 720p | render-split-screen | PASS | split-screen 1080x1920 ok |  |  |
| 78 | 2026-11-10 03:20 | synthetic A/V mismatch | verify-durations-rejects | PASS | mismatched A/V correctly rejected |  |  |
| 79 | 2026-11-10 03:20 | synthetic 6s colour video | track-no-face | PASS | no-face -> centre fallback, 24 samples |  |  |
| 80 | 2026-11-10 03:20 | nonexistent path | track-missing-file | PASS | missing file -> safe fallback dict |  |  |
| 81 | 2026-11-10 03:20 | bad path / bad string | download-errors | PASS | bad local path / bad string -> ValueError |  |  |
| 82 | 2026-11-10 03:20 | prompts/moment-picking.txt | prompt-loads | PASS | moment-picking prompt has all placeholders |  |  |
| 83 | 2026-11-10 03:20 | localhost:8137 | webui-smoke | PASS | health + index + bad-job 400 ok |  |  |
| 84 | 2026-11-10 03:20 | clipvault nuclear seg.mp4 (80s podcast) | e2e-clipvault-gemini | PASS | 2 clips, scorer=gemini, 104.6s; sample saved: output/elon-nuclear-clip01.mp4 |  |  |
| 85 | 2026-11-10 03:21 | Gemini vault credential | gemini-probe | FAIL | RuntimeError: Gemini failed on all models: Gemini HTTP 503: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later. / RuntimeError: Gemini failed on all models: Gemini HTTP 503: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later. |  |  |
| 86 | 2026-11-10 03:21 | ml_local package | local-ml-import | PASS | virality_inference imports (model load tested in e2e) |  |  |
| 87 | 2026-11-10 03:21 | Gemini vault credential | gemini-probe | PASS | Gemini replied: OK |  |  |
| 88 | 2026-11-10 03:23 | kids-evolved long 706s (no face) | e2e-no-face-long | PASS | no-face long video -> 1 clip, 126.1s |  |  |
| 89 | 2026-11-10 03:24 | package | imports | PASS | 11 modules import clean |  |  |
| 90 | 2026-11-10 03:24 | repo files | config-paths | PASS | model + prompt + 5 licences present |  |  |
| 91 | 2026-11-10 03:24 | synthetic 400 words | candidates-normal | PASS | 14 candidates, lengths in range |  |  |
| 92 | 2026-11-10 03:24 | synthetic 0/3 words | candidates-empty | PASS | empty/short input -> no candidates (no crash) |  |  |
| 93 | 2026-11-10 03:24 | synthetic hook vs filler | heuristic-ranking | PASS | hook=42.0 filler=15.4 |  |  |
| 94 | 2026-11-10 03:24 | synthetic overlapping clips | dedupe-clips | PASS | overlap dropped, best kept |  |  |
| 95 | 2026-11-10 03:24 | synthetic 100 words | transcript-lines | PASS | 2 lines, [mm:ss] format |  |  |
| 96 | 2026-11-10 03:24 | synthetic 40 words | captions-all-styles | PASS | 4 styles ASS+SRT ok |  |  |
| 97 | 2026-11-10 03:24 | synthetic braces | captions-escaping | PASS | braces stripped, no ASS injection |  |  |
| 98 | 2026-11-10 03:24 | synthetic Hindi words | captions-hindi | PASS | Devanagari writes to ASS (shaping depends on font — see README) |  |  |
| 99 | 2026-11-10 03:24 | synthetic 240-pt trajectory | crop-expression | PASS | 60s tracked expr 1246 chars; empty->centre |  |  |
| 100 | 2026-11-10 03:24 | synthetic measured values | loudnorm-filter | PASS | measured + fallback strings ok |  |  |
| 101 | 2026-11-10 03:24 | synthetic 5s 720p | render-tiny | PASS | 1080x1920, v=5.00 a=5.00 |  |  |
| 102 | 2026-11-10 03:24 | synthetic 4s 720x1280 | render-vertical-source | PASS | vertical 720x1280 source -> 1080x1920 ok |  |  |
| 103 | 2026-11-10 03:24 | synthetic 4s 720p | render-split-screen | PASS | split-screen 1080x1920 ok |  |  |
| 104 | 2026-11-10 03:24 | synthetic A/V mismatch | verify-durations-rejects | PASS | mismatched A/V correctly rejected |  |  |
| 105 | 2026-11-10 03:24 | synthetic 6s colour video | track-no-face | PASS | no-face -> centre fallback, 24 samples |  |  |
| 106 | 2026-11-10 03:24 | nonexistent path | track-missing-file | PASS | missing file -> safe fallback dict |  |  |
| 107 | 2026-11-10 03:24 | bad path / bad string | download-errors | PASS | bad local path / bad string -> ValueError |  |  |
| 108 | 2026-11-10 03:24 | prompts/moment-picking.txt | prompt-loads | PASS | moment-picking prompt has all placeholders |  |  |
| 109 | 2026-11-10 03:24 | localhost:8137 | webui-smoke | PASS | health + index + bad-job 400 ok |  |  |
| 110 | 2026-11-10 03:24 | Gemini vault credential | gemini-probe | PASS | Gemini replied: OK |  |  |
| 111 | 2026-11-10 03:24 | ml_local package | local-ml-import | PASS | virality_inference imports (model load tested in e2e) |  |  |
| 112 | 2026-11-10 03:26 | Minions 10-min section (movie dialogue) | e2e-minions-section | PASS | 10-min movie section -> 2 clips, 147.1s |  |  |
| 113 | 2026-11-10 03:26 | Lex Fridman #400 600-1200s | e2e-youtube | FAIL | RuntimeError: yt-dlp -J failed: outube] dZg6rfcGx8Q: Unable to download API page: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1000) (caused by Ce / |  |  |
| 114 | 2026-11-10 13:15 | package | imports | PASS | 11 modules import clean |  |  |
| 115 | 2026-11-10 13:15 | repo files | config-paths | PASS | model + prompt + 5 licences present |  |  |
| 116 | 2026-11-10 13:15 | synthetic 400 words | candidates-normal | PASS | 14 candidates, lengths in range |  |  |
| 117 | 2026-11-10 13:15 | synthetic 0/3 words | candidates-empty | PASS | empty/short input -> no candidates (no crash) |  |  |
| 118 | 2026-11-10 13:15 | synthetic hook vs filler | heuristic-ranking | PASS | hook=42.0 filler=15.4 |  |  |
| 119 | 2026-11-10 13:15 | synthetic overlapping clips | dedupe-clips | PASS | overlap dropped, best kept |  |  |
| 120 | 2026-11-10 13:15 | synthetic 100 words | transcript-lines | PASS | 2 lines, [mm:ss] format |  |  |
| 121 | 2026-11-10 13:15 | synthetic 40 words | captions-all-styles | PASS | 4 styles ASS+SRT ok |  |  |
| 122 | 2026-11-10 13:15 | synthetic braces | captions-escaping | PASS | braces stripped, no ASS injection |  |  |
| 123 | 2026-11-10 13:15 | synthetic Hindi words | captions-hindi | PASS | Devanagari writes to ASS (shaping depends on font — see README) |  |  |
| 124 | 2026-11-10 13:15 | synthetic 240-pt trajectory | crop-expression | PASS | 60s tracked expr 1246 chars; empty->centre |  |  |
| 125 | 2026-11-10 13:15 | synthetic measured values | loudnorm-filter | PASS | measured + fallback strings ok |  |  |
| 126 | 2026-11-10 13:15 | synthetic 5s 720p | render-tiny | PASS | 1080x1920, v=5.00 a=5.00 |  |  |
| 127 | 2026-11-10 13:15 | synthetic 4s 720x1280 | render-vertical-source | PASS | vertical 720x1280 source -> 1080x1920 ok |  |  |
| 128 | 2026-11-10 13:15 | synthetic 4s 720p | render-split-screen | PASS | split-screen 1080x1920 ok |  |  |
| 129 | 2026-11-10 13:15 | synthetic A/V mismatch | verify-durations-rejects | PASS | mismatched A/V correctly rejected |  |  |
| 130 | 2026-11-10 13:15 | synthetic 6s colour video | track-no-face | PASS | no-face -> centre fallback, 24 samples |  |  |
| 131 | 2026-11-10 13:15 | nonexistent path | track-missing-file | PASS | missing file -> safe fallback dict |  |  |
| 132 | 2026-11-10 13:15 | bad path / bad string | download-errors | PASS | bad local path / bad string -> ValueError |  |  |
| 133 | 2026-11-10 13:15 | prompts/moment-picking.txt | prompt-loads | PASS | moment-picking prompt has all placeholders |  |  |
| 134 | 2026-11-10 13:15 | localhost:8137 | webui-smoke | PASS | health + index + bad-job 400 ok |  |  |
| 135 | 2026-11-10 13:16 | Gemini vault credential | gemini-probe | FAIL | RuntimeError: Gemini failed on all models: Gemini HTTP 503: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later. / RuntimeError: Gemini failed on all models: Gemini HTTP 503: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later. |  |  |
| 136 | 2026-11-10 13:16 | ml_local package | local-ml-import | PASS | virality_inference imports (model load tested in e2e) |  |  |
| 137 | 2026-11-10 14:01 | Rocky exact URL sRH-XIBE2cQ 600-1500 | e2e-youtube-rocky-exact (v0.1.1) | FAIL | -J probe cert error killed job BEFORE download fallback; generic friendly error, no SSL branch; v0.1.1 batch had no YouTube download test | probe tolerance + cert message (runs 138-141) | run 138 |
| 138 | 2026-11-10 14:03 | Rocky exact URL sRH-XIBE2cQ 600-1500 | e2e-youtube-rocky-exact-retest | FAIL | egress cert block persists here (expected); job now reaches download (yt-dlp Retrying 2/3, 3/3 in detail) and shows cert-specific message, no raw traceback | - | - |
| 139 | 2026-11-10 14:05 | Rocky's exact impersonate error + 429 + cert strings | friendly-error-mapping | PASS | impersonate -> pip install curl_cffi message; 429 -> rate-limit message; cert -> new certificate message | - | - |
| 140 | 2026-11-10 14:04 | elon-nuclear-clip01.mp4 upload | e2e-local-file | PASS | 1 clip in 22.4s; clip01.mp4 verified on disk v=8.40 a=8.39, captions present | - | - |
| 141 | 2026-11-10 14:05 | /nonexistent/file.mp4, "not-a-url" | prepare_source-regression | PASS | both still ValueError | - | - |
| 142 | 2026-11-10 15:05 | settings save/load (dummy key) | settings-round-trip | PASS | 12/12: defaults, save, perms 0600, mask AIza...7890, settings beats env, bad scorer rejected, corrupt file -> defaults, clear | - | - |
| 143 | 2026-11-10 15:06 | dummy key, vault disabled (Rocky PC sim) | gemini-key-plumbing | PASS | dummy key -> HTTP 400 "API key not valid" (key WAS sent); key never in error; no key -> "paste one in AI Settings" | - | - |
| 144 | 2026-11-10 15:06 | localhost:8139 | settings-api-smoke | PASS | GET/POST settings masked AIza...7890, test -> OK (via Muse vault on this VM), clear, UI has AI Settings card, key in 0 responses | - | - |
| 145 | 2026-11-10 15:07 | elon-nuclear-clip01.mp4, scorer gemini | e2e-local-file | PASS | 1 clip in ~49s, scorer gemini, clip01.mp4 + captions present | - | - |
| 146 | 2026-11-10 15:14 | 22 bundled Google Fonts (OFL) | fonts-verify | PASS | all files valid TTF, nameID1 == registry, groups cover 22 once, total 2494 KB | - | - |
| 147 | 2026-11-10 15:15 | elon-nuclear-clip01.mp4, font Bebas Neue vs default | e2e-font-render | PASS | .ass has Bebas Neue; pixel-diff at t=5.6 (active caption): bebas/default/no-fontsdir all differ; visual check shows Bebas caps. First t=5.0 check was vacuous (dead-air gap) — re-ran at 5.6 | - | - |
| 148 | 2026-11-10 15:18 | localhost:8140 | fonts-api-smoke | PASS | /api/fonts 22 fonts in 4 groups; index has font dropdown; unknown font -> default; startJob sends font | - | - |
| 149 | 2026-11-10 15:20 | all 22 bundled fonts | font-preview-render | PASS | 22/22 valid PNGs, all unique md5s, cache identical, unknown font raises, size 640x150 | - | - |
| 150 | 2026-11-10 15:20 | localhost:8141 | font-preview-api-smoke | PASS | /api/fonts/preview 200 image/png 11006 B; unknown/no name -> 400; index has preview UI; version 0.1.4 | - | - |
| 151 | 2026-11-10 15:21 | Bebas Neue, Luckiest Guy, Montserrat ExtraBold previews | font-preview-visual | PASS | Bebas tall condensed caps, Luckiest Guy rounded cartoon, Montserrat bold geometric — all correct, white + black outline on dark | - | - |
| 152 | 2026-11-10 17:17 | all 10 caption styles | styles-unit | PASS | 6 new styles: sizes, news BorderStyle 3 + opaque box, hollow transparent primary, highlight alpha fix; 4 old styles unchanged; unknown style falls back to hormozi | - | - |
| 153 | 2026-11-10 17:17 | Bebas Neue + pop/news/outline previews | style-preview-render | PASS | pop vs hormozi differ, news vs hormozi differ, size 1080x220, unknown style raises, news black-box band verified (597 vs 155 black px); 3 previews visually checked | - | - |
| 154 | 2026-11-10 17:18 | localhost:8142 | style-preview-api-smoke | PASS | preview?style=pop 200 image/png 13006 B; unknown style -> 400; index has 6 new style options + &style= wiring; version 0.1.5 | - | - |
| 155 | 2026-11-10 17:19 | elon-nuclear-clip01.mp4, style pop, font Bebas Neue | e2e-style-render | PASS | 1 clip; .ass Style Cap,Bebas Neue,84 outline 5 shadow 3; highlight override has alpha fix; job.json font stored | - | - |
| 156 | 2026-11-10 17:36 | decide_two_speakers (synthetic faces) | split-guard-unit | PASS | stream facecam + gameplay face -> NO split; facecam bottom-right -> NO split; real podcast -> SPLIT; speakers too close -> NO split; single face / few samples / centre-heavy -> NO split | - | - |
| 157 | 2026-11-10 17:37 | red|blue split source, facecam vs normal tracking | render-facecam-guard | PASS | facecam tracking -> centre crop (left red, right blue); normal tracking -> face crop (all red). First 157a run "failed" on a wrong assertion (compared red channels across halves); assertion fixed, re-run 0 failures — code was never wrong | - | - |
| 158 | 2026-11-10 17:38 | elon-nuclear-clip01.mp4, --no-captions vs default | captions-off-e2e | PASS | no .ass, .srt kept, job.json captions=false, captioned vs no-caption frames differ in caption band (mean abs diff 8.1) | - | - |
| 159 | 2026-11-10 17:41 | localhost:8143, API job captions=off layout=single | api-smoke-new-fields | PASS | job 20261110-174120 done; job.json captions=false layout=single split_screen=false ass=None; no .ass file. First POST raced server startup (empty response); retry OK | - | - |
| 160 | 2026-11-10 17:40 | _decide_split | layout-unit | PASS | auto follows tracking; single never splits; split always splits; unknown layout falls back to tracking | - | - |
| 161 | 2026-11-10 18:14 | provider dispatcher (deepseek/ollama/gemini) | provider-dispatch-unit | PASS | deepseek dummy key -> HTTP 401 in 0.6s (key sent as Bearer); ollama no server -> plain-language not-running error; unknown provider -> gemini; MODELS == [gemini-3.8-flash]. First 161a run hit a 120s transient egress stall; re-run 0.6s PASS, code unchanged | - | - |
| 162 | 2026-11-10 18:14 | settings round-trip | settings-provider-unit | PASS | provider + deepseek key + ollama model/host save/load; mask sk-t...1234; public_status has new fields, no key in it; unknown provider/scorer ValueError; corrupt file -> defaults | - | - |
| 163 | 2026-11-10 18:21 | elon-nuclear-clip01.mp4, provider=deepseek dummy key, scorer auto | e2e-provider-fallback | PASS | job 20261110-182142 done in ~46s; job.json scorer=heuristic (DeepSeek 401 -> heuristic fallback); clip01.mp4 1080x1920 31.9s + .srt/.ass + hook/hashtags | - | - |
| 164 | 2026-11-10 18:23 | localhost:8144 | provider-api-smoke | PASS | GET /api/settings has new fields; POST deepseek key -> masked sk-d...7890, key nowhere in responses; test deepseek -> DeepSeek HTTP 401; test ollama -> not-running error; index has provider select + deepseek input + ollama note; health version 0.1.7 | - | - |
| 165 | 2026-11-10 18:24 | gemini_client.probe() via vault | gemini-model-fix-live | PASS | MODELS fixed: no 404, request reached gemini-3.8-flash in 0.9s; HTTP 503 high demand — same 503 seen on Rocky's key and the vault key, i.e. live Gemini overload, not a code/key problem | - | - |
| 166 | 2026-11-10 18:48 | package | imports | PASS | 11 modules import clean |  |  |
| 167 | 2026-11-10 18:48 | repo files | config-paths | PASS | model + prompt + 5 licences present |  |  |
| 168 | 2026-11-10 18:48 | synthetic 400 words | candidates-normal | PASS | 14 candidates, lengths in range |  |  |
| 169 | 2026-11-10 18:48 | synthetic 0/3 words | candidates-empty | PASS | empty/short input -> no candidates (no crash) |  |  |
| 170 | 2026-11-10 18:48 | synthetic hook vs filler | heuristic-ranking | PASS | hook=42.0 filler=15.4 |  |  |
| 171 | 2026-11-10 18:48 | synthetic overlapping clips | dedupe-clips | PASS | overlap dropped, best kept |  |  |
| 172 | 2026-11-10 18:48 | synthetic 100 words | transcript-lines | PASS | 2 lines, [mm:ss] format |  |  |
| 173 | 2026-11-10 18:48 | synthetic 40 words | captions-all-styles | PASS | 4 styles ASS+SRT ok |  |  |
| 174 | 2026-11-10 18:48 | synthetic braces | captions-escaping | PASS | braces stripped, no ASS injection |  |  |
| 175 | 2026-11-10 18:48 | synthetic Hindi words | captions-hindi | PASS | Devanagari writes to ASS (shaping depends on font — see README) |  |  |
| 176 | 2026-11-10 18:48 | synthetic 240-pt trajectory | crop-expression | PASS | 60s tracked expr 1246 chars; empty->centre |  |  |
| 177 | 2026-11-10 18:48 | synthetic measured values | loudnorm-filter | PASS | measured + fallback strings ok |  |  |
| 178 | 2026-11-10 18:48 | synthetic 5s 720p | render-tiny | PASS | 1080x1920, v=5.00 a=5.00 |  |  |
| 179 | 2026-11-10 18:48 | synthetic 4s 720x1280 | render-vertical-source | PASS | vertical 720x1280 source -> 1080x1920 ok |  |  |
| 180 | 2026-11-10 18:48 | synthetic 4s 720p | render-split-screen | PASS | split-screen 1080x1920 ok |  |  |
| 181 | 2026-11-10 18:48 | synthetic A/V mismatch | verify-durations-rejects | PASS | mismatched A/V correctly rejected |  |  |
| 182 | 2026-11-10 18:48 | synthetic 6s colour video | track-no-face | PASS | no-face -> centre fallback, 24 samples |  |  |
| 183 | 2026-11-10 18:48 | nonexistent path | track-missing-file | PASS | missing file -> safe fallback dict |  |  |
| 184 | 2026-11-10 18:48 | bad path / bad string | download-errors | PASS | bad local path / bad string -> ValueError |  |  |
| 185 | 2026-11-10 18:48 | prompts/moment-picking.txt | prompt-loads | PASS | moment-picking prompt has all placeholders |  |  |
| 186 | 2026-11-10 18:48 | localhost:8137 | webui-smoke | PASS | health + index + bad-job 400 ok |  |  |
| 187 | 2026-11-10 18:49 | Gemini vault credential | gemini-probe | FAIL | RuntimeError: Gemini failed on all models: Gemini HTTP 503: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later. / RuntimeError: Gemini failed on all models: Gemini HTTP 503: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later. |  |  |
| 188 | 2026-11-10 18:49 | ml_local package | local-ml-import | PASS | virality_inference imports (model load tested in e2e) |  |  |
| 189 | 2026-11-10 19:28 | mock OpenAI server (in-process) | custom-client-unit | PASS | provider=custom routes to custom_client; Bearer key + model qwen2.5:3b sent; path /v1/chat/completions; no key -> no auth header; 401 -> clean error; dead server -> plain-language could-not-reach error. First run's 401 check failed on a wrong mock path test (endswith vs contains); test fixed, re-run 0 failures — code was never wrong | - | - |
| 190 | 2026-11-10 19:28 | settings round-trip | settings-custom-unit | PASS | provider + custom_base_url + custom_model + custom_api_key save/load; mask sk-d...-456; public_status has custom fields, no key in it | - | - |
| 191 | 2026-11-10 19:26 | elon-nuclear-clip01.mp4, provider=custom qwen2.5:3b, mock moments server :8151 | e2e-custom-provider | PASS | job 20261110-192642 done in ~46s; log "custom picked 1 moments"; job.json scorer=custom, clip score_source=custom 90.0; clip01.mp4 + .srt/.ass + caption pack; mock log proves model + Bearer key sent | - | - |
| 192 | 2026-11-10 19:31 | localhost:8145 + mock probe server :8152 | custom-api-smoke | PASS | GET /api/settings lists custom + fields; POST custom key -> masked sk-d...-123, key nowhere in responses; test -> {"ok": true, "reply": "OK", "provider": "custom"}; index has custom option + 3 fields; health version 0.1.8 | - | - |
| 193 | 2026-11-10 19:33 | package | imports | PASS | 11 modules import clean |  |  |
| 194 | 2026-11-10 19:33 | repo files | config-paths | PASS | model + prompt + 5 licences present |  |  |
| 195 | 2026-11-10 19:33 | synthetic 400 words | candidates-normal | PASS | 14 candidates, lengths in range |  |  |
| 196 | 2026-11-10 19:33 | synthetic 0/3 words | candidates-empty | PASS | empty/short input -> no candidates (no crash) |  |  |
| 197 | 2026-11-10 19:33 | synthetic hook vs filler | heuristic-ranking | PASS | hook=42.0 filler=15.4 |  |  |
| 198 | 2026-11-10 19:33 | synthetic overlapping clips | dedupe-clips | PASS | overlap dropped, best kept |  |  |
| 199 | 2026-11-10 19:33 | synthetic 100 words | transcript-lines | PASS | 2 lines, [mm:ss] format |  |  |
| 200 | 2026-11-10 19:33 | synthetic 40 words | captions-all-styles | PASS | 4 styles ASS+SRT ok |  |  |
| 201 | 2026-11-10 19:33 | synthetic braces | captions-escaping | PASS | braces stripped, no ASS injection |  |  |
| 202 | 2026-11-10 19:33 | synthetic Hindi words | captions-hindi | PASS | Devanagari writes to ASS (shaping depends on font — see README) |  |  |
| 203 | 2026-11-10 19:33 | synthetic 240-pt trajectory | crop-expression | PASS | 60s tracked expr 1246 chars; empty->centre |  |  |
| 204 | 2026-11-10 19:33 | synthetic measured values | loudnorm-filter | PASS | measured + fallback strings ok |  |  |
| 205 | 2026-11-10 19:33 | synthetic 5s 720p | render-tiny | PASS | 1080x1920, v=5.00 a=5.00 |  |  |
| 206 | 2026-11-10 19:33 | synthetic 4s 720x1280 | render-vertical-source | PASS | vertical 720x1280 source -> 1080x1920 ok |  |  |
| 207 | 2026-11-10 19:33 | synthetic 4s 720p | render-split-screen | PASS | split-screen 1080x1920 ok |  |  |
| 208 | 2026-11-10 19:33 | synthetic A/V mismatch | verify-durations-rejects | PASS | mismatched A/V correctly rejected |  |  |
| 209 | 2026-11-10 19:33 | synthetic 6s colour video | track-no-face | PASS | no-face -> centre fallback, 24 samples |  |  |
| 210 | 2026-11-10 19:33 | nonexistent path | track-missing-file | PASS | missing file -> safe fallback dict |  |  |
| 211 | 2026-11-10 19:33 | bad path / bad string | download-errors | PASS | bad local path / bad string -> ValueError |  |  |
| 212 | 2026-11-10 19:33 | prompts/moment-picking.txt | prompt-loads | PASS | moment-picking prompt has all placeholders |  |  |
| 213 | 2026-11-10 19:33 | localhost:8137 | webui-smoke | PASS | health + index + bad-job 400 ok |  |  |
| 214 | 2026-11-10 19:33 | Gemini vault credential | gemini-probe | FAIL | RuntimeError: Gemini failed on all models: Gemini HTTP 503: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later. / RuntimeError: Gemini failed on all models: Gemini HTTP 503: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later. |  |  |
| 215 | 2026-11-10 19:33 | ml_local package | local-ml-import | PASS | virality_inference imports (model load tested in e2e) |  |  |
