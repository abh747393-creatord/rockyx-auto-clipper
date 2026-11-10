"""Font + caption-style preview images for the UI's picker.

Renders the sample line "Viral Clips 123!" in a bundled font AND a caption
style (colours, size, outline, box) — the first word in the style's
highlight colour, like a caption mid-word — so the user sees exactly what
a clip's captions will look like before picking. Rendered on demand with
Pillow from the bundled TTF, at the caption's own PlayResX width (1080),
so style font sizes are 1:1; no image files to ship.
"""
from __future__ import annotations

import io

from PIL import Image, ImageDraw, ImageFont

from . import config

SAMPLE = "Viral Clips 123!"
WIDTH, HEIGHT = 1080, 220
BG = (17, 17, 17)  # matches the page background

_cache: dict[tuple[str, str], bytes] = {}


def _bgr_to_rgb(bgr_hex: str) -> tuple[int, int, int]:
    """ASS "&H00BBGGRR" -> (R, G, B)."""
    h = bgr_hex[2:]
    return int(h[6:8], 16), int(h[4:6], 16), int(h[2:4], 16)


def _ass_alpha_to_pil(bgr_hex: str) -> int:
    """ASS alpha (00 opaque .. FF transparent) -> PIL alpha (255 .. 0)."""
    return 255 - int(bgr_hex[2:4], 16)


def render_font_preview(font_name: str, style_name: str = "hormozi") -> bytes:
    """PNG bytes (1080x220) of the sample line in the font + caption style."""
    from .captions import STYLES

    if font_name not in config.FONTS:
        raise ValueError(f"unknown font: {font_name}")
    style = STYLES.get(style_name)
    if style is None:
        raise ValueError(f"unknown style: {style_name}")
    key = (font_name, style_name)
    if key in _cache:
        return _cache[key]
    path = config.FONTS_DIR / config.FONTS[font_name]
    if not path.exists():
        raise ValueError(f"font file missing: {path.name}")

    primary = _bgr_to_rgb(style["primary"])
    primary_a = _ass_alpha_to_pil(style["primary"])
    highlight = _bgr_to_rgb(style["highlight"])
    outline = _bgr_to_rgb(style["outline"])
    outline_w = int(style["outline_w"])

    img = Image.new("RGBA", (WIDTH, HEIGHT), BG + (255,))
    draw = ImageDraw.Draw(img)
    size = int(style["font_size"])
    font = ImageFont.truetype(str(path), size)
    while size > 20 and draw.textlength(SAMPLE, font=font) > WIDTH - 60:
        size -= 4
        font = ImageFont.truetype(str(path), size)

    words = SAMPLE.split(" ")
    space_w = draw.textlength(" ", font=font)
    word_ws = [draw.textlength(w, font=font) for w in words]
    total = sum(word_ws) + space_w * (len(words) - 1)
    bbox = draw.textbbox((0, 0), SAMPLE, font=font)
    th = bbox[3] - bbox[1]
    x = (WIDTH - total) / 2
    y = (HEIGHT - th) / 2 - bbox[1]

    if style.get("border_style", 1) == 3:
        # News box: solid black rectangle behind the whole line.
        draw.rectangle([x - 22, y - 12, x + total + 22, y + th + 12],
                       fill=(0, 0, 0, 255))
    for i, w in enumerate(words):
        fill = highlight + (255,) if i == 0 else primary + (primary_a,)
        draw.text((x, y), w, font=font, fill=fill,
                  stroke_width=outline_w, stroke_fill=outline + (255,))
        x += word_ws[i] + space_w

    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    data = buf.getvalue()
    _cache[key] = data
    return data
