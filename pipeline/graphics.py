"""
Motion-graphics renderer for YouTube Shorts (1080×1920, 9:16, 30 fps).

Each scene is built as a CompositeVideoClip containing:
  - Animated gradient background (slow zoom)
  - Thin accent bar (fade in)
  - Large headline text (slide_up / fade_in / zoom_in)
  - Smaller subtext (delayed fade in)
  - Progress dots row (bottom of frame)

Scenes are joined with a smooth crossfade transition.
"""

from __future__ import annotations

import glob
import os
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    CompositeVideoClip,
    ImageClip,
    VideoClip,
    concatenate_videoclips,
)
from moviepy.video.fx import FadeIn, FadeOut, Resize

from .models import Scene, Script

# ── Canvas constants ────────────────────────────────────────────────────────
W = 1080
H = 1920
FPS = 30
TRANS = 0.45  # crossfade duration in seconds


# ── Colour helpers ───────────────────────────────────────────────────────────

def _hex_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


# ── Font loader ──────────────────────────────────────────────────────────────

_FONT_CACHE: dict[int, ImageFont.FreeTypeFont | ImageFont.ImageFont] = {}

_FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/lato/Lato-Bold.ttf",
    "/usr/share/fonts/truetype/open-sans/OpenSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def _find_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if size in _FONT_CACHE:
        return _FONT_CACHE[size]

    for path in _FONT_PATHS:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, size)
                _FONT_CACHE[size] = font
                return font
            except Exception:
                continue

    # Glob search for any bold TTF on the system
    for pattern in [
        "/usr/share/fonts/**/*[Bb]old*.ttf",
        "/usr/share/fonts/**/*[Bb]old*.otf",
        os.path.expanduser("~/.fonts/**/*[Bb]old*.ttf"),
    ]:
        for path in glob.glob(pattern, recursive=True):
            try:
                font = ImageFont.truetype(path, size)
                _FONT_CACHE[size] = font
                return font
            except Exception:
                continue

    # Fallback: PIL built-in (small but always present)
    try:
        font = ImageFont.load_default(size=size)
    except TypeError:
        font = ImageFont.load_default()
    _FONT_CACHE[size] = font
    return font


# ── Image helpers ────────────────────────────────────────────────────────────

def _gradient_bg(color_start: str, color_end: str) -> np.ndarray:
    """Vertical gradient background, shape (H, W, 3) uint8."""
    c1 = np.array(_hex_rgb(color_start), dtype=np.float32)
    c2 = np.array(_hex_rgb(color_end), dtype=np.float32)
    t = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None, None]
    img = (c1 * (1.0 - t) + c2 * t).astype(np.uint8)
    return np.broadcast_to(img, (H, W, 3)).copy()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont, max_px: int) -> list[str]:
    """Word-wrap text so each line fits within max_px pixels wide."""
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join(current + [word])
        bb = dummy.textbbox((0, 0), candidate, font=font)
        if bb[2] - bb[0] <= max_px:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines or [text]


def _text_image(
    text: str,
    font_size: int,
    color: str = "#FFFFFF",
    stroke_color: str = "#000000",
    stroke_width: int = 3,
    max_width: int = W - 80,
) -> np.ndarray:
    """Render text onto a transparent canvas; returns RGBA uint8 array (H, W, 4)."""
    font = _find_font(font_size)
    lines = _wrap_text(text, font, max_width)

    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    line_sizes: list[tuple[int, int]] = []
    for line in lines:
        bb = dummy.textbbox((0, 0), line, font=font)
        line_sizes.append((bb[2] - bb[0], bb[3] - bb[1]))

    line_gap = max(8, font_size // 8)
    total_h = sum(h for _, h in line_sizes) + line_gap * (len(lines) - 1)
    total_w = max(w for w, _ in line_sizes) if line_sizes else 1
    pad = stroke_width + 6
    canvas_w = total_w + pad * 2
    canvas_h = total_h + pad * 2

    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    fr, fg, fb = _hex_rgb(color)
    sr, sg, sb = _hex_rgb(stroke_color)
    y = pad
    for i, line in enumerate(lines):
        x = (canvas_w - line_sizes[i][0]) // 2
        draw.text(
            (x, y),
            line,
            font=font,
            fill=(fr, fg, fb, 255),
            stroke_fill=(sr, sg, sb, 210),
            stroke_width=stroke_width,
        )
        y += line_sizes[i][1] + line_gap

    return np.array(img)


def _accent_bar(accent: str, width: int = 200, height: int = 6) -> np.ndarray:
    """Thin horizontal coloured bar, RGBA (H, W, 4)."""
    r, g, b = _hex_rgb(accent)
    img = np.zeros((height, width, 4), dtype=np.uint8)
    img[:, :, 0] = r
    img[:, :, 1] = g
    img[:, :, 2] = b
    img[:, :, 3] = 255
    return img


def _progress_dots(current: int, total: int, accent: str) -> np.ndarray:
    """Row of dots showing position in the short; active dot is filled."""
    dot = 12
    gap = 18
    total_w = total * (dot + gap) - gap
    h = dot + 16
    img = Image.new("RGBA", (total_w + 8, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    r, g, b = _hex_rgb(accent)
    for i in range(total):
        x = 4 + i * (dot + gap)
        y = 8
        alpha = 255 if i == current else 70
        draw.ellipse([x, y, x + dot, y + dot], fill=(r, g, b, alpha))
    return np.array(img)


# ── Clip builder helpers ─────────────────────────────────────────────────────

def _rgba_clip(rgba: np.ndarray, duration: float) -> ImageClip:
    """ImageClip with proper alpha mask from an RGBA array."""
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3].astype(np.float32) / 255.0
    clip = ImageClip(rgb).with_duration(duration)
    mask = ImageClip(alpha, is_mask=True).with_duration(duration)
    return clip.with_mask(mask)


def _slide_up_pos(base_y: int) -> Callable[[float], tuple]:
    """Returns a position function that eases a clip upward over 0.55 s."""
    def pos(t: float) -> tuple:
        if t >= 0.55:
            return ("center", base_y)
        ease = 1.0 - (1.0 - t / 0.55) ** 3  # cubic ease-out
        offset = int(110 * (1.0 - ease))
        return ("center", base_y + offset)
    return pos


# ── Scene compositor ─────────────────────────────────────────────────────────

def _build_scene(scene: Scene, scene_idx: int, total_scenes: int) -> CompositeVideoClip:
    d = scene.duration

    # ── Background: gradient with a gentle zoom-in ───────────────────────────
    bg_arr = _gradient_bg(scene.bg_color_start, scene.bg_color_end)
    bg_clip = (
        ImageClip(bg_arr)
        .with_duration(d)
        .with_fps(FPS)
        .with_effects([Resize(lambda t, _d=d: 1.0 + 0.04 * (t / _d))])
        .with_position("center")
    )

    layers: list = [bg_clip]

    # ── Accent bar ───────────────────────────────────────────────────────────
    bar_arr = _accent_bar(scene.accent_color, width=220, height=6)
    bar_y = H // 2 - 180
    bar_clip = (
        _rgba_clip(bar_arr, d)
        .with_position(("center", bar_y))
        .with_effects([FadeIn(0.35)])
    )
    layers.append(bar_clip)

    # ── Headline ─────────────────────────────────────────────────────────────
    hl_arr = _text_image(scene.headline, 90, "#FFFFFF", stroke_width=4)
    hl_h = hl_arr.shape[0]
    hl_y = H // 2 - hl_h // 2 - 40
    hl_clip = _rgba_clip(hl_arr, d)

    if scene.animation == "slide_up":
        hl_clip = hl_clip.with_position(_slide_up_pos(hl_y)).with_effects([FadeIn(0.3)])
    elif scene.animation == "zoom_in":
        hl_clip = (
            hl_clip
            .with_position(("center", hl_y))
            .with_effects([
                Resize(lambda t: max(0.82, min(1.0, 0.82 + 0.18 * (t / 0.55)))),
                FadeIn(0.35),
            ])
        )
    else:  # fade_in
        hl_clip = hl_clip.with_position(("center", hl_y)).with_effects([FadeIn(0.55)])

    layers.append(hl_clip)

    # ── Subtext ──────────────────────────────────────────────────────────────
    st_arr = _text_image(scene.subtext, 46, "#D8D8D8", stroke_width=2, max_width=W - 120)
    st_y = hl_y + hl_h + 36
    st_clip = (
        _rgba_clip(st_arr, d - 0.4)
        .with_start(0.4)
        .with_position(("center", st_y))
        .with_effects([FadeIn(0.5)])
    )
    layers.append(st_clip)

    # ── Progress dots ────────────────────────────────────────────────────────
    dot_arr = _progress_dots(scene_idx, total_scenes, scene.accent_color)
    dot_clip = (
        _rgba_clip(dot_arr, d)
        .with_position(("center", H - 110))
        .with_effects([FadeIn(0.3)])
    )
    layers.append(dot_clip)

    return CompositeVideoClip(layers, size=(W, H)).with_duration(d)


# ── Public renderer ──────────────────────────────────────────────────────────

def render_video(script: Script, output_path: str) -> None:
    """Composite all scenes with crossfade transitions and write a 9:16 MP4."""
    scene_clips = []
    for i, scene in enumerate(script.scenes):
        print(f"  Scene {i + 1}/{len(script.scenes)}: "{scene.headline}"")
        clip = _build_scene(scene, i, len(script.scenes))
        scene_clips.append(clip)

    # Crossfade: FadeOut on outgoing, FadeIn on incoming, clips overlap by TRANS
    print("  Compositing transitions…")
    fx_clips: list = []
    starts: list[float] = []
    current = 0.0
    for i, clip in enumerate(scene_clips):
        effects = []
        if i > 0:
            effects.append(FadeIn(TRANS))
        if i < len(scene_clips) - 1:
            effects.append(FadeOut(TRANS))
        fx_clips.append(clip.with_effects(effects) if effects else clip)
        starts.append(current)
        current += clip.duration - (TRANS if i < len(scene_clips) - 1 else 0.0)

    total_dur = starts[-1] + scene_clips[-1].duration
    positioned = [c.with_start(s) for c, s in zip(fx_clips, starts)]
    final = CompositeVideoClip(positioned, size=(W, H)).with_duration(total_dur)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"  Encoding → {out}  ({W}×{H}, {FPS} fps, ~{total_dur:.0f}s)…")
    final.write_videofile(
        str(out),
        fps=FPS,
        codec="libx264",
        audio=False,
        preset="fast",
        ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p"],
        logger=None,
    )
    print(f"  ✓ Saved: {out.resolve()}")
