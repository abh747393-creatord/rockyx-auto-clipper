"""Font preview images for the UI's font picker.

Renders the sample line "Viral Clips 123!" in a bundled font (white with a
black outline, like the captions) so the user can see each font before
picking it. Rendered on demand with Pillow from the bundled TTF — no image
files to ship, and the preview always matches the font the clips use.
"""
from __future__ import annotations

import io

from PIL import Image, ImageDraw, ImageFont

from . import config

SAMPLE = "Viral Clips 123!"
WIDTH, HEIGHT = 640, 150
BG = (17, 17, 17)       # matches the page background
FG = (255, 255, 255)    # caption white
OUTLINE = (0, 0, 0)     # caption outline

_cache: dict[str, bytes] = {}


def render_font_preview(font_name: str) -> bytes:
    """PNG bytes (640x150) of the sample line in the named bundled font."""
    if font_name not in config.FONTS:
        raise ValueError(f"unknown font: {font_name}")
    if font_name in _cache:
        return _cache[font_name]
    path = config.FONTS_DIR / config.FONTS[font_name]
    if not path.exists():
        raise ValueError(f"font file missing: {path.name}")
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    size = 76
    font = ImageFont.truetype(str(path), size)
    while size > 20 and draw.textlength(SAMPLE, font=font) > WIDTH - 40:
        size -= 4
        font = ImageFont.truetype(str(path), size)
    tw = draw.textlength(SAMPLE, font=font)
    bbox = draw.textbbox((0, 0), SAMPLE, font=font)
    th = bbox[3] - bbox[1]
    x = (WIDTH - tw) / 2
    y = (HEIGHT - th) / 2 - bbox[1]
    draw.text((x, y), SAMPLE, font=font, fill=FG, stroke_width=2, stroke_fill=OUTLINE)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    data = buf.getvalue()
    _cache[font_name] = data
    return data
