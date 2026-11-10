"""Moment finding + virality scoring (0-100) + ranking.

Three scorers, best-first:
1. Gemini LLM (vault credential) — picks moments, scores 0-100, writes hook
   titles, hashtags and B-roll suggestions. Prompt: prompts/moment-picking.txt
2. Local ML virality model (OpenClip Studio, MIT) — optional; needs
   scikit-learn/joblib + the MiniLM ONNX model. Skipped gracefully if absent.
3. Heuristic scorer (always available, no API) — hook/curiosity/shock-word
   patterns, payoff detection, lexical density, filler ratio, speech cadence,
   dead-air. Pattern lists adapted from OpenClip Studio's feature_extractor.py
   (MIT, see CREDITS.md); weights and combination are our own.

Final score = Gemini when it returns, else heuristic. Local ML (when it runs)
is blended in as a tie-breaker signal, never required.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

from . import config

# --- Pattern lists (adapted from OpenClip Studio feature_extractor.py, MIT) ---
CURIOSITY_PATTERNS = [
    re.compile(r"\b(the best way to|the most important thing|the secret to|the single biggest|the number one|the key to|how to actually|how you can|here is how)\b", re.I),
    re.compile(r"\b(here's why|the reason why|nobody talks about|nobody knows|the truth about|the real reason|this is why|what happens when|you have to understand)\b", re.I),
    re.compile(r"\b(stop doing|never do|biggest mistake|worst thing|you won't believe|you should never|don't ever|huge problem)\b", re.I),
    re.compile(r"\b(people don't realize|everyone thinks|what if i told you|what you have to realize|most people don't|most people have heard)\b", re.I),
    re.compile(r"\b(if you want to|if you are trying to|if you were going to|when you do this|the moment you|if i give you)\b", re.I),
]
SHOCK_WORDS = {
    "insane", "crazy", "unbelievable", "impossible", "shocking", "omg", "no way",
    "mind-blowing", "wild", "destroyed", "killed", "died", "million", "billion",
    "arrested", "guilty", "exposed", "scam", "conspiracy", "disaster", "catastrophe",
    "dangerous", "unshakeable", "unbreakable", "elite", "collapse", "spike", "amplify",
}
EMOTION_WORDS = {
    "wow", "whoa", "omg", "insane", "crazy", "unbelievable", "incredible", "shocking",
    "funny", "hilarious", "laugh", "joke", "wrong", "disagree", "argue", "fight",
    "versus", "debate", "lie", "problem", "mistake", "research", "study", "proven",
    "data", "fact", "expert", "evidence", "now", "today", "immediately", "stop",
    "must", "need", "critical", "warning", "important", "first",
}
PAYOFF_PATTERNS = [
    re.compile(r"\b(that's why|that's the reason|and that's|at the end of the day|bottom line|the point is|essentially is)\b", re.I),
    re.compile(r"\b(exactly|period|solution|guaranteed|remember that|takeaway|optimal|full spectrum|disappear)\b", re.I),
]
FILLER_WORDS = {"um", "uh", "like", "you know", "sort of", "kind of", "i mean",
                "basically", "literally", "right", "actually", "anyway"}
DANGLING_WORDS = {"a", "an", "the", "and", "but", "or", "so", "because", "like", "if",
                  "that", "which", "with", "to", "when", "as", "then", "than", "of", "in",
                  "on", "at", "by", "for", "about", "is", "are", "was", "were", "just",
                  "very", "really", "also", "even", "who"}
QUESTION_WORDS = {"what", "why", "how", "when", "where", "who", "which", "is", "are",
                  "can", "could", "should", "do", "does", "did"}


def _fmt_ts(seconds: float) -> str:
    m = int(seconds // 60)
    s = seconds - m * 60
    return f"{m:02d}:{s:05.2f}"


def transcript_lines(words: list[dict], chunk_s: float = 30.0) -> str:
    """Transcript as timestamped lines for the LLM: '[mm:ss] spoken text'."""
    if not words:
        return ""
    lines = []
    cur_start = words[0]["start"]
    buf = []
    for w in words:
        if w["start"] - cur_start >= chunk_s and buf:
            lines.append(f"[{_fmt_ts(cur_start)}] " + " ".join(buf))
            cur_start = w["start"]
            buf = [w["word"]]
        else:
            buf.append(w["word"])
    if buf:
        lines.append(f"[{_fmt_ts(cur_start)}] " + " ".join(buf))
    return "\n".join(lines)


def build_candidates(words: list[dict], min_s: float = 30.0, max_s: float = 60.0,
                     target_s: float = 45.0, step_s: float = 10.0) -> list[dict]:
    """Sliding windows over the word stream, cut on natural pauses.

    A window starts at a word after a pause (>0.4s) or every step_s seconds,
    and ends at a pause near the target length. Returns dicts with
    start/end/text/words.
    """
    if not words:
        return []
    starts: list[int] = []
    last_start_t = -1e9
    for i, w in enumerate(words):
        gap = (w["start"] - words[i - 1]["end"]) if i > 0 else 99.0
        if gap > 0.4 or (w["start"] - last_start_t) >= step_s:
            starts.append(i)
            last_start_t = w["start"]
    candidates = []
    seen: set[tuple[float, float]] = set()
    for si in starts:
        start_t = words[si]["start"]
        # Extend to target length, then stop at the next pause after min_s.
        end_i = si
        for j in range(si, len(words)):
            end_i = j
            dur = words[j]["end"] - start_t
            if dur >= target_s:
                break
            if dur >= min_s and j + 1 < len(words) and (words[j + 1]["start"] - words[j]["end"]) > 0.4:
                break
        end_t = words[end_i]["end"]
        if end_t - start_t < min_s * 0.8:
            continue
        if end_t - start_t > max_s:
            # Trim to max_s at a word boundary.
            for j in range(si, len(words)):
                if words[j]["end"] - start_t > max_s:
                    end_i = max(si, j - 1)
                    end_t = words[end_i]["end"]
                    break
        key = (round(start_t, 1), round(end_t, 1))
        if key in seen:
            continue
        seen.add(key)
        seg_words = words[si:end_i + 1]
        candidates.append({
            "start": round(start_t, 2),
            "end": round(end_t, 2),
            "text": " ".join(w["word"] for w in seg_words),
            "words": seg_words,
        })
    return candidates


def heuristic_score(cand: dict) -> tuple[float, str]:
    """0-100 heuristic virality score + one-line reason. No API needed."""
    text = cand["text"]
    words = cand["words"]
    if not words:
        return 10.0, "empty segment"
    dur = max(0.1, cand["end"] - cand["start"])
    low = text.lower()
    tokens = re.findall(r"[a-z']+", low)
    n = max(1, len(tokens))

    # Hook: first ~4 seconds of speech.
    hook_words = [w for w in words if w["start"] - cand["start"] <= 4.0]
    hook_text = " ".join(w["word"] for w in hook_words).lower()
    hook = 0.0
    reasons = []
    hook_tokens = hook_text.strip().split()
    if hook_tokens and hook_tokens[0] in QUESTION_WORDS:
        hook += 25.0
        reasons.append("opening question hook")
    elif any(t in QUESTION_WORDS for t in hook_tokens[:6]) or "what if" in hook_text:
        hook += 15.0
        reasons.append("question-style opening")
    if any(p.search(hook_text) for p in CURIOSITY_PATTERNS):
        hook += 25.0
        reasons.append("curiosity-gap opening")
    if any(w in SHOCK_WORDS for w in re.findall(r"[a-z']+", hook_text)):
        hook += 20.0
        reasons.append("high-impact opening words")
    emo = sum(1 for w in re.findall(r"[a-z']+", hook_text) if w in EMOTION_WORDS)
    if emo >= 2:
        hook += 10.0
        reasons.append("emotional opening")

    # Payoff: last ~5 seconds.
    tail_words = [w for w in words if cand["end"] - w["end"] <= 5.0]
    tail_text = " ".join(w["word"] for w in tail_words).lower()
    payoff = 0.0
    if any(p.search(tail_text) for p in PAYOFF_PATTERNS):
        payoff += 15.0
        reasons.append("clear payoff close")
    last_word = tokens[-1] if tokens else ""
    if last_word not in DANGLING_WORDS and len(tokens) > 5:
        payoff += 10.0
        reasons.append("complete closing thought")

    # Lexical density: unique-word ratio + compression-ish signal.
    unique_ratio = len(set(tokens)) / n
    density = max(0.0, min(1.0, (unique_ratio - 0.35) / 0.45)) * 10.0

    # Filler penalty.
    filler = sum(1 for t in tokens if t in FILLER_WORDS) / n
    filler_pen = min(10.0, filler * 100.0)

    # Cadence: 135-195 WPM is the viral sweet spot.
    wpm = n / (dur / 60.0)
    if 135 <= wpm <= 195:
        cadence = 10.0
        reasons.append(f"punchy cadence ({int(wpm)} WPM)")
    elif 110 <= wpm < 135 or 195 < wpm <= 230:
        cadence = 6.0
    else:
        cadence = 2.0

    # Dead air: long gaps inside the window.
    gaps = [words[i]["start"] - words[i - 1]["end"] for i in range(1, len(words))]
    dead = sum(g for g in gaps if g > 1.0)
    dead_pen = min(10.0, dead * 2.0)

    # Length: prefer 35-55s.
    if 35 <= dur <= 55:
        length = 5.0
    elif 30 <= dur < 35 or 55 < dur <= 60:
        length = 3.0
    else:
        length = 1.0

    score = hook + payoff + density + cadence + length - filler_pen - dead_pen
    score = max(10.0, min(99.0, score))
    if not reasons:
        reasons.append("coherent standalone segment")
    return round(score, 1), ", ".join(reasons[:3])


def score_candidates_heuristic(candidates: list[dict]) -> list[dict]:
    for c in candidates:
        s, reason = heuristic_score(c)
        c["heuristic_score"] = s
        c["heuristic_reason"] = reason
        c["score"] = s
        c["score_source"] = "heuristic"
    return sorted(candidates, key=lambda c: c["score"], reverse=True)


def gemini_pick_moments(words: list[dict], num_clips: int = 3,
                        min_s: float = 30.0, max_s: float = 60.0,
                        language: str = "en") -> list[dict] | None:
    """Ask Gemini to pick the strongest moments. Returns clips or None."""
    from . import gemini_client

    prompt_path = config.PROMPTS_DIR / "moment-picking.txt"
    template = prompt_path.read_text(encoding="utf-8")
    transcript = transcript_lines(words)
    duration = words[-1]["end"] if words else 0.0
    prompt = template.format(
        num_clips=num_clips, min_s=int(min_s), max_s=int(max_s),
        duration=round(duration, 1), language=language, transcript=transcript,
    )
    raw = gemini_client.generate_text(
        prompt,
        system="You are a short-form video editor. Reply with JSON only.",
        max_tokens=4000, temperature=0.7,
    )
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned).strip()
    data = json.loads(cleaned)
    clips = data.get("clips", []) if isinstance(data, dict) else data
    out = []
    for c in clips:
        try:
            start = float(c["start"])
            end = float(c["end"])
        except (KeyError, TypeError, ValueError):
            continue
        if end - start < min_s * 0.8 or end - start > max_s + 5 or start < 0:
            continue
        seg_words = [w for w in words if w["start"] >= start - 0.2 and w["end"] <= end + 0.2]
        out.append({
            "start": round(start, 2),
            "end": round(end, 2),
            "text": " ".join(w["word"] for w in seg_words),
            "words": seg_words,
            "score": float(c.get("virality_score", c.get("score", 50))),
            "score_source": "gemini",
            "reason": str(c.get("reason", ""))[:300],
            "title": str(c.get("title", ""))[:120],
            "hook_title": str(c.get("hook_title", c.get("title", "")))[:120],
            "hashtags": list(c.get("hashtags", []))[:12],
            "broll_suggestion": str(c.get("broll_suggestion", ""))[:300],
            "hook_score": c.get("hook_score"),
            "shareability_score": c.get("shareability_score"),
        })
    out.sort(key=lambda c: c["score"], reverse=True)
    return out[:num_clips] if out else None


def local_ml_score(candidates: list[dict], wav_path: str | None = None) -> dict[int, float] | None:
    """Optional OpenClip local ML virality model. Returns {index: score} or None."""
    try:
        from .ml_local import virality_inference
    except Exception as exc:  # noqa: BLE001 - optional component
        print(f"[score] local ML scorer unavailable: {exc}")
        return None
    try:
        segments = []
        for i, c in enumerate(candidates):
            segments.append({"id": f"clip_{i + 1}", "words": c["words"],
                             "start": c["start"], "end": c["end"]})
        results = virality_inference.score_segments(segments, default_wav_path=wav_path)
        return {i: float(r["viralityScore"]) for i, r in enumerate(results)}
    except Exception as exc:  # noqa: BLE001 - model load/inference failure is non-fatal
        print(f"[score] local ML scoring failed: {exc}")
        return None


def dedupe_clips(clips: list[dict], min_gap_s: float = 5.0) -> list[dict]:
    """Drop clips that overlap an earlier, higher-scored clip."""
    kept: list[dict] = []
    for c in sorted(clips, key=lambda x: x["score"], reverse=True):
        overlap = False
        for k in kept:
            if c["start"] < k["end"] - min_gap_s and c["end"] > k["start"] + min_gap_s:
                overlap = True
                break
        if not overlap:
            kept.append(c)
    return kept
