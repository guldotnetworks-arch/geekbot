"""
Renders each script segment as a MoviePy clip with motion graphics,
then composites them with transitions into a final 9:16 vertical MP4.

Resolution: 1080 × 1920  (portrait / YouTube Shorts)
Frame rate : 30 fps
"""

from __future__ import annotations

import os
import textwrap
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    ColorClip,
    CompositeVideoClip,
    ImageClip,
    concatenate_videoclips,
)
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout

# ── Constants ─────────────────────────────────────────────────────────────────
W, H = 1080, 1920
FPS = 30
FONT_PATH_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
]


def _find_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for p in FONT_PATH_CANDIDATES:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


# ── Gradient background ────────────────────────────────────────────────────────

def _gradient_frame(bg_hex: str, accent_hex: str) -> np.ndarray:
    """Vertical gradient from bg_color (top) → darkened accent (bottom)."""
    bg = np.array(_hex_to_rgb(bg_hex), dtype=np.float32)
    ac = np.array(_hex_to_rgb(accent_hex), dtype=np.float32) * 0.35
    frame = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        t = y / H
        frame[y] = (bg * (1 - t) + ac * t).clip(0, 255).astype(np.uint8)
    return frame


# ── Decorative elements ────────────────────────────────────────────────────────

def _draw_accent_bar(draw: ImageDraw.Draw, accent_hex: str, y: int, width: int = 8) -> None:
    color = _hex_to_rgb(accent_hex)
    draw.rectangle([80, y, 80 + width, y + 90], fill=color)


def _draw_progress_dots(
    draw: ImageDraw.Draw, total: int, current: int, accent_hex: str
) -> None:
    """Row of dots near bottom showing segment progress."""
    dot_r = 10
    gap = 28
    total_w = total * (dot_r * 2) + (total - 1) * gap
    x0 = (W - total_w) // 2
    y = H - 100
    for i in range(total):
        x = x0 + i * (dot_r * 2 + gap)
        color = _hex_to_rgb(accent_hex) if i == current else (80, 80, 80)
        draw.ellipse([x, y, x + dot_r * 2, y + dot_r * 2], fill=color)


# ── Single segment frame ───────────────────────────────────────────────────────

def _render_segment_frame(
    segment: dict,
    seg_index: int,
    total_segments: int,
) -> np.ndarray:
    bg_hex = segment["bg_color"]
    ac_hex = segment["accent_color"]
    headline = segment["headline"]
    body = segment["body"]
    seg_type = segment["type"]

    base = _gradient_frame(bg_hex, ac_hex)
    img = Image.fromarray(base)
    draw = ImageDraw.Draw(img)

    accent_rgb = _hex_to_rgb(ac_hex)

    # ── Type badge (HOOK / FACT / CTA) ────────────────────────────────────────
    badge_font = _find_font(36)
    badge_text = seg_type.upper()
    bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    bw = bbox[2] - bbox[0] + 40
    draw.rounded_rectangle([80, 140, 80 + bw, 200], radius=8, fill=accent_rgb)
    draw.text((100, 148), badge_text, font=badge_font, fill=(255, 255, 255))

    # ── Accent bar ─────────────────────────────────────────────────────────────
    _draw_accent_bar(draw, ac_hex, y=240)

    # ── Headline ───────────────────────────────────────────────────────────────
    hl_font = _find_font(96)
    wrapped = textwrap.fill(headline, width=16)
    draw.text((80, 260), wrapped, font=hl_font, fill=(255, 255, 255))

    # Measure headline height to position body below it
    hl_bbox = draw.multiline_textbbox((80, 260), wrapped, font=hl_font)
    hl_bottom = hl_bbox[3] + 40

    # ── Body text ──────────────────────────────────────────────────────────────
    body_font = _find_font(54)
    body_wrapped = textwrap.fill(body, width=26)
    draw.multiline_text(
        (80, hl_bottom),
        body_wrapped,
        font=body_font,
        fill=(200, 200, 220),
        spacing=12,
    )

    # ── Bottom accent line ─────────────────────────────────────────────────────
    draw.rectangle([80, H - 160, W - 80, H - 155], fill=accent_rgb)

    # ── Progress dots ─────────────────────────────────────────────────────────
    _draw_progress_dots(draw, total_segments, seg_index, ac_hex)

    return np.array(img)


# ── Animation helpers ──────────────────────────────────────────────────────────

def _apply_animation(
    clip: ImageClip, animation: str, duration: float
) -> CompositeVideoClip:
    """Wrap *clip* in a motion animation."""
    if animation == "slide_up":
        def slide_pos(t: float):
            progress = min(t / 0.4, 1.0)
            ease = 1 - (1 - progress) ** 3
            offset = int((1 - ease) * 120)
            return ("center", offset)
        return clip.set_position(slide_pos)

    elif animation == "zoom":
        def zoom_scale(t: float):
            progress = min(t / 0.5, 1.0)
            ease = 1 - (1 - progress) ** 2
            return 1.0 + 0.04 * (1 - ease)
        return clip.resize(zoom_scale)

    else:  # fade
        return fadein(clip, 0.4)


# ── Build one segment clip ─────────────────────────────────────────────────────

def _build_segment_clip(
    segment: dict,
    seg_index: int,
    total_segments: int,
) -> CompositeVideoClip:
    duration = float(segment["duration"])
    frame = _render_segment_frame(segment, seg_index, total_segments)

    base_clip = (
        ImageClip(frame)
        .set_duration(duration)
        .set_fps(FPS)
    )

    animated = _apply_animation(base_clip, segment.get("animation", "fade"), duration)

    # Fade out last 0.3 s for smooth transition
    result = fadeout(animated, 0.3)
    return result.set_duration(duration)


# ── Public render function ─────────────────────────────────────────────────────

def render_video(script: dict, output_path: str | Path) -> Path:
    """
    Render a full YouTube Short from *script* and write it to *output_path*.

    Returns the resolved output path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    segments = script["segments"]
    n = len(segments)
    clips = [_build_segment_clip(seg, i, n) for i, seg in enumerate(segments)]

    final = concatenate_videoclips(clips, method="compose")
    final = final.set_fps(FPS)

    final.write_videofile(
        str(output_path),
        fps=FPS,
        codec="libx264",
        audio=False,
        preset="fast",
        ffmpeg_params=["-crf", "23", "-pix_fmt", "yuv420p"],
        logger=None,
    )

    return output_path
