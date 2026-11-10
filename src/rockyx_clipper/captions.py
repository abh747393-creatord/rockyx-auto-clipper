"""Kinetic word-by-word burned-in captions.

10 styles: Hormozi / MrBeast / Minimal / Neon (paid-tool looks, our own
code) + Pop / News box / Outline (hollow) / Fire / Ocean / Gold (v0.1.5).
Technique: the full line stays on screen and the *current word* is
highlighted with a colour + bold override, one ASS event per word. This
renders correctly in libass (ffmpeg subtitles filter) on Linux and Windows,
with no karaoke-fill quirks.

Fonts: 22 free OFL Google Fonts bundled in fonts/ (see config.FONTS) — the
user picks one in the UI and libass finds it via the subtitles filter's
fontsdir, so they work on any machine with no install. Without a pick (or
ROCKYX_FONT unset): DejaVu Sans on Linux, Arial on Windows. A font name
given here that is not bundled is still passed through — libass then falls
back to the closest system font.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

# style_name -> (font_size, primary BGR hex, highlight BGR hex, outline, shadow)
# ASS colours are &HAABBGGRR (alpha, blue, green, red).
STYLES = {
    "hormozi": {
        "font_size": 68, "primary": "&H00FFFFFF", "highlight": "&H0000C8FF",
        "outline": "&H00000000", "back": "&H80000000", "outline_w": 3, "shadow": 1,
        "bold": -1, "margin_v": 300, "alignment": 2,
    },
    "mrbeast": {
        "font_size": 76, "primary": "&H0000D8FF", "highlight": "&H00FFFFFF",
        "outline": "&H00000000", "back": "&H80000000", "outline_w": 4, "shadow": 2,
        "bold": -1, "margin_v": 300, "alignment": 2,
    },
    "minimal": {
        "font_size": 56, "primary": "&H00FFFFFF", "highlight": "&H00FFFFFF",
        "outline": "&H00000000", "back": "&H80000000", "outline_w": 2, "shadow": 1,
        "bold": 0, "margin_v": 260, "alignment": 2,
    },
    "neon": {
        "font_size": 68, "primary": "&H00FFFFFF", "highlight": "&H00FF80FF",
        "outline": "&H00FF00AA", "back": "&H80000000", "outline_w": 3, "shadow": 2,
        "bold": -1, "margin_v": 300, "alignment": 2,
    },
    # --- v0.1.5: six more looks. Colours are ASS &HAABBGGRR. ---
    "pop": {  # loudest: huge type, thick outline, hard shadow
        "font_size": 84, "primary": "&H00FFFFFF", "highlight": "&H0000C8FF",
        "outline": "&H00000000", "back": "&H80000000", "outline_w": 5, "shadow": 3,
        "bold": -1, "margin_v": 300, "alignment": 2,
    },
    "news": {  # white type on a solid black box (BorderStyle 3, opaque back)
        "font_size": 60, "primary": "&H00FFFFFF", "highlight": "&H0000C8FF",
        "outline": "&H00000000", "back": "&H00000000", "outline_w": 0, "shadow": 0,
        "bold": -1, "margin_v": 300, "alignment": 2, "border_style": 3,
    },
    "outline": {  # hollow letters: transparent fill, yellow outline;
        # the spoken word fills solid yellow (highlight override forces opaque)
        "font_size": 72, "primary": "&HFF000000", "highlight": "&H0000C8FF",
        "outline": "&H0000C8FF", "back": "&H80000000", "outline_w": 4, "shadow": 1,
        "bold": -1, "margin_v": 300, "alignment": 2,
    },
    "fire": {  # orange fire type, yellow highlight, dark red outline
        "font_size": 72, "primary": "&H00356BFF", "highlight": "&H0000C8FF",
        "outline": "&H0000008C", "back": "&H80000000", "outline_w": 3, "shadow": 2,
        "bold": -1, "margin_v": 300, "alignment": 2,
    },
    "ocean": {  # cyan type, white highlight, dark blue outline
        "font_size": 68, "primary": "&H00FFD400", "highlight": "&H00FFFFFF",
        "outline": "&H008C3A00", "back": "&H80000000", "outline_w": 3, "shadow": 2,
        "bold": -1, "margin_v": 300, "alignment": 2,
    },
    "gold": {  # gold type, white highlight, dark brown outline
        "font_size": 70, "primary": "&H0000D7FF", "highlight": "&H00FFFFFF",
        "outline": "&H00004E6B", "back": "&H80000000", "outline_w": 3, "shadow": 2,
        "bold": -1, "margin_v": 300, "alignment": 2,
    },
}


def resolve_font() -> str:
    env = os.environ.get("ROCKYX_FONT")
    if env:
        return env
    return "Arial" if os.name == "nt" else "DejaVu Sans"


def _ass_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def _srt_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def chunk_words(words: list[dict], max_words: int = 5, max_s: float = 2.4) -> list[list[dict]]:
    """Group words into readable caption lines."""
    lines: list[list[dict]] = []
    cur: list[dict] = []
    for w in words:
        if cur and (len(cur) >= max_words or (w["start"] - cur[0]["start"]) > max_s):
            lines.append(cur)
            cur = []
        cur.append(w)
        if re.search(r"[.!?,;:]$", w["word"]):
            lines.append(cur)
            cur = []
    if cur:
        lines.append(cur)
    return lines


def words_to_ass(words: list[dict], clip_start: float, clip_end: float,
                 style_name: str = "hormozi", hook_title: str = "",
                 out_path: Path | None = None, margin_v: int | None = None,
                 font: str = "") -> str:
    """Build an ASS subtitle string (word-highlight kinetic captions).

    Times are relative to the clip (clip_start subtracted).
    margin_v overrides the caption height (split-screen puts captions on the seam).
    font overrides the style's font (a bundled font name from config.FONTS,
    or any system font name); empty means the style default.
    """
    style = dict(STYLES.get(style_name, STYLES["hormozi"]))
    if margin_v is not None:
        style["margin_v"] = margin_v
    font = font or resolve_font()
    rel = [dict(w, start=w["start"] - clip_start, end=w["end"] - clip_start)
           for w in words if w["end"] > clip_start and w["start"] < clip_end]
    lines = chunk_words(rel)
    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        "PlayResX: 1080\n"
        "PlayResY: 1920\n"
        "ScaledBorderAndShadow: yes\n"
        "WrapStyle: 0\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Cap,{font},{style['font_size']},{style['primary']},{style['primary']},"
        f"{style['outline']},{style['back']},{style['bold']},0,0,0,100,100,0,0,"
        f"{style.get('border_style', 1)},{style['outline_w']},{style['shadow']},{style['alignment']},60,60,{style['margin_v']},1\n"
        f"Style: Hook,{font},54,&H0000D8FF,&H0000D8FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,8,60,60,140,1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    events: list[str] = []
    if hook_title:
        events.append(
            f"Dialogue: 0,{_ass_time(0)},{_ass_time(min(3.0, clip_end - clip_start))},"
            f"Hook,,0,0,0,,{hook_title}"
        )
    for line in lines:
        line_text = " ".join(w["word"] for w in line)
        for i, w in enumerate(line):
            start = w["start"]
            end = line[i + 1]["start"] if i + 1 < len(line) else min(w["end"] + 0.25, line[-1]["end"] + 0.25)
            end = max(end, start + 0.08)
            parts = []
            for j, lw in enumerate(line):
                word = lw["word"].replace("{", "").replace("}", "")
                if j == i:
                    # \1a&H00& forces the spoken word fully opaque — needed
                    # by the hollow "outline" style, whose fill is transparent.
                    parts.append(f"{{\\1c{style['highlight'][4:]}\\1a&H00&\\b1}}{word}{{\\r}}")
                else:
                    parts.append(word)
            text = " ".join(parts)
            events.append(
                f"Dialogue: 0,{_ass_time(start)},{_ass_time(end)},Cap,,0,0,0,,{text}"
            )
    ass = header + "\n".join(events) + "\n"
    if out_path:
        Path(out_path).write_text(ass, encoding="utf-8")
    return ass


def words_to_srt(words: list[dict], clip_start: float, clip_end: float,
                 out_path: Path | None = None) -> str:
    """Plain SRT (one line per caption chunk) — for the caption pack."""
    rel = [dict(w, start=w["start"] - clip_start, end=w["end"] - clip_start)
           for w in words if w["end"] > clip_start and w["start"] < clip_end]
    lines = chunk_words(rel, max_words=8, max_s=3.5)
    out = []
    for i, line in enumerate(lines, 1):
        out.append(str(i))
        out.append(f"{_srt_time(line[0]['start'])} --> {_srt_time(line[-1]['end'])}")
        out.append(" ".join(w["word"] for w in line))
        out.append("")
    srt = "\n".join(out)
    if out_path:
        Path(out_path).write_text(srt, encoding="utf-8")
    return srt
