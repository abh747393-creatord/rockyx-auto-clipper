import sys
import json
import os
import argparse
from faster_whisper import WhisperModel

# Compat shim (Rockyx adaptation): faster-whisper 1.2.1 calls
# av.open(..., metadata_errors="ignore"), but PyAV 19 removed that keyword
# (it now goes through the options dict). Drop the unsupported kwarg so
# transcription works on PyAV 19; harmless for WAV input.
try:
    import av as _av

    _orig_av_open = _av.open

    def _av_open_compat(file, mode="r", **kwargs):
        kwargs.pop("metadata_errors", None)
        return _orig_av_open(file, mode=mode, **kwargs)

    _av.open = _av_open_compat
except Exception:
    pass

def run_transcription(audio_path, model_size="base.en", language="en", max_duration=None, progress_file=None):
    if not os.path.exists(audio_path):
        print(json.dumps({"error": f"Audio file not found: {audio_path}"}))
        sys.exit(1)

    try:
        # Adaptive CPU threads: this VM has 1.5 shared CPUs, Rocky's PC has more.
        import os as _os
        num_threads = max(1, min(4, _os.cpu_count() or 2))
        num_workers = 1

        # Prefer English-optimized base.en when language is English or default
        effective_model = model_size
        if effective_model == "tiny" or effective_model == "base.en":
            effective_model = "base.en" if language == "en" else "base"

        model = WhisperModel(
            effective_model,
            device="cpu",
            compute_type="int8",
            cpu_threads=num_threads,
            num_workers=num_workers
        )

        # Conversational initial prompt for high accuracy on podcasts/interviews
        stream_prompt = "podcast, interview, conversation, YouTube, clip, shorts, story, reaction, debate."

        # Silero VAD skips silence and background music
        # condition_on_previous_text=False + hallucination_silence_threshold prevents repetition loops
        transcribe_kwargs = {
            "word_timestamps": True,
            "beam_size": 2,
            "best_of": 1,
            "temperature": 0.0,
            "initial_prompt": stream_prompt,
            "condition_on_previous_text": False,
            "vad_filter": True,
            "vad_parameters": dict(min_silence_duration_ms=400),
            "hallucination_silence_threshold": 2.0,
            "no_speech_threshold": 0.6
        }
        if not effective_model.endswith(".en") and language:
            transcribe_kwargs["language"] = language

        segments, info = model.transcribe(audio_path, **transcribe_kwargs)

        words = []
        full_text_parts = []
        total_duration = info.duration
        if max_duration and max_duration > 0:
            total_duration = min(total_duration, float(max_duration))

        for segment in segments:
            # Stop early if max_duration was specified
            if max_duration and segment.start > float(max_duration):
                break

            full_text_parts.append(segment.text.strip())

            # Write real-time progress for frontend progress bar
            if progress_file:
                try:
                    pct = min(99, round((segment.end / total_duration) * 100, 1))
                    with open(progress_file, "w") as pf:
                        json.dump({
                            "currentSec": round(segment.end, 1),
                            "totalSec": round(total_duration, 1),
                            "percent": pct
                        }, pf)
                except Exception:
                    pass

            if segment.words:
                for w in segment.words:
                    clean_word = w.word.strip()
                    if clean_word:
                        words.append({
                            "word": clean_word,
                            "start": round(w.start, 3),
                            "end": round(w.end, 3),
                            "probability": round(w.probability, 3)
                        })
            else:
                raw_words = segment.text.strip().split()
                if raw_words:
                    seg_dur = max(0.2, segment.end - segment.start)
                    w_dur = seg_dur / len(raw_words)
                    for i, rw in enumerate(raw_words):
                        words.append({
                            "word": rw,
                            "start": round(segment.start + i * w_dur, 3),
                            "end": round(segment.start + (i + 1) * w_dur, 3),
                            "probability": 0.85
                        })

        if progress_file:
            try:
                with open(progress_file, "w") as pf:
                    json.dump({
                        "currentSec": round(total_duration, 1),
                        "totalSec": round(total_duration, 1),
                        "percent": 100.0,
                        "done": True
                    }, pf)
            except Exception:
                pass

        result = {
            "success": True,
            "text": " ".join(full_text_parts),
            "language": info.language,
            "duration": round(total_duration, 2),
            "words": words
        }
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio_path")
    parser.add_argument("--model", default="base.en")
    parser.add_argument("--language", default="en")
    parser.add_argument("--max-duration", type=float, default=None)
    parser.add_argument("--progress-file", default=None)

    args = parser.parse_args()
    run_transcription(
        args.audio_path,
        model_size=args.model,
        language=args.language,
        max_duration=args.max_duration,
        progress_file=args.progress_file
    )
