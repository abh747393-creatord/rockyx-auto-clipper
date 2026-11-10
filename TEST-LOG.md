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
