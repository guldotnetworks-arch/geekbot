import math
import random
from PIL import Image, ImageDraw, ImageFilter

# ── Palette ──────────────────────────────────────────────────────────────────
BG        = (8, 10, 18)          # near-black navy
GRID      = (18, 28, 52)         # subtle grid lines
ACCENT1   = (0, 210, 255)        # cyan
ACCENT2   = (80, 60, 240)        # electric indigo
ACCENT3   = (255, 255, 255)      # white
GLOW      = (0, 180, 220, 60)    # translucent cyan glow

random.seed(42)


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ─────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────────────────────

def draw_grid(draw, w, h, spacing=80, color=GRID):
    for x in range(0, w, spacing):
        draw.line([(x, 0), (x, h)], fill=color, width=1)
    for y in range(0, h, spacing):
        draw.line([(0, y), (w, y)], fill=color, width=1)


def draw_dot_nodes(draw, w, h, count=60, radius=3):
    for _ in range(count):
        x = random.randint(0, w)
        y = random.randint(0, h)
        draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                     fill=(*ACCENT1, 120))


def draw_circuit_lines(draw, points, color, width=1):
    """Draw L-shaped circuit traces between consecutive points."""
    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        mx = (x0 + x1) // 2
        draw.line([(x0, y0), (mx, y0)], fill=color, width=width)
        draw.line([(mx, y0), (mx, y1)], fill=color, width=width)
        draw.line([(mx, y1), (x1, y1)], fill=color, width=width)


def draw_hex_grid(draw, cx, cy, radius, rings=3, color=ACCENT1, alpha=40):
    """Draw a honeycomb pattern centred at (cx, cy)."""
    def hex_corners(hx, hy, r):
        return [(hx + r * math.cos(math.radians(60 * i - 30)),
                 hy + r * math.sin(math.radians(60 * i - 30)))
                for i in range(6)]

    dirs = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
    dx = radius * math.sqrt(3)
    dy = radius * 1.5

    visited = set()
    queue = [(0, 0)]
    visited.add((0, 0))

    while queue:
        q, r = queue.pop(0)
        if max(abs(q), abs(r), abs(q + r)) > rings:
            continue
        hx = cx + q * dx + r * dx / 2
        hy = cy + r * dy
        pts = hex_corners(hx, hy, radius - 2)
        draw.polygon(pts, outline=(*color, alpha), fill=None)
        for dq, dr in dirs:
            nq, nr = q + dq, r + dr
            if (nq, nr) not in visited:
                visited.add((nq, nr))
                queue.append((nq, nr))


def add_glow_overlay(img, cx, cy, inner_r, outer_r, color_rgb):
    """Add a radial glow using concentric alpha-blended circles."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    steps = 40
    for i in range(steps, 0, -1):
        r = inner_r + (outer_r - inner_r) * (i / steps)
        alpha = int(60 * (1 - i / steps))
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  fill=(*color_rgb, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


# ─────────────────────────────────────────────────────────────────────────────
# BANNER  2560 × 1440
# ─────────────────────────────────────────────────────────────────────────────

def make_banner():
    W, H = 2560, 1440
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img, "RGBA")

    # Background gradient — left dark, right slightly lighter navy
    for x in range(W):
        t = x / W
        c = lerp_color((4, 6, 14), (12, 16, 34), t)
        draw.line([(x, 0), (x, H)], fill=c)

    # Grid
    draw_grid(draw, W, H, spacing=80)

    # ── Diagonal accent band ─────────────────────────────────────────────────
    band_pts = [(0, H * 0.55), (W, H * 0.38),
                (W, H * 0.42), (0, H * 0.60)]
    draw.polygon(band_pts, fill=(*ACCENT2, 18))

    # ── Hex cluster — left third ─────────────────────────────────────────────
    draw_hex_grid(draw, W * 0.15, H * 0.5, radius=55, rings=4,
                  color=ACCENT1, alpha=35)

    # ── Hex cluster — right ──────────────────────────────────────────────────
    draw_hex_grid(draw, W * 0.88, H * 0.5, radius=45, rings=3,
                  color=ACCENT2[:3], alpha=30)

    # ── Central circle / logo placeholder ────────────────────────────────────
    cx, cy = W // 2, H // 2

    # Glow rings
    for r, a in [(320, 8), (260, 14), (210, 22), (170, 35)]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     outline=(*ACCENT1, a), width=2)

    # Main ring
    draw.ellipse([cx - 130, cy - 130, cx + 130, cy + 130],
                 outline=ACCENT1, width=3)

    # Inner filled circle
    draw.ellipse([cx - 110, cy - 110, cx + 110, cy + 110],
                 fill=(*ACCENT2, 80))

    # Crosshair lines inside circle
    draw.line([(cx - 90, cy), (cx + 90, cy)], fill=(*ACCENT1, 160), width=2)
    draw.line([(cx, cy - 90), (cx, cy + 90)], fill=(*ACCENT1, 160), width=2)

    # Four corner tick marks around ring
    for angle in range(0, 360, 90):
        rad = math.radians(angle)
        ix = cx + int(125 * math.cos(rad))
        iy = cy + int(125 * math.sin(rad))
        ox = cx + int(145 * math.cos(rad))
        oy = cy + int(145 * math.sin(rad))
        draw.line([(ix, iy), (ox, oy)], fill=ACCENT1, width=3)

    # ── Circuit traces ────────────────────────────────────────────────────────
    circuit_color = (*ACCENT1, 80)
    traces = [
        [(cx - 140, cy - 20), (cx - 340, cy - 20),
         (cx - 340, H * 0.2), (cx - 600, H * 0.2)],
        [(cx + 140, cy + 20), (cx + 340, cy + 20),
         (cx + 340, H * 0.8), (cx + 600, H * 0.8)],
        [(cx - 20, cy - 140), (cx - 20, cy - 300),
         (cx - 200, cy - 300), (cx - 200, H * 0.1)],
        [(cx + 20, cy + 140), (cx + 20, cy + 300),
         (cx + 200, cy + 300), (cx + 200, H * 0.9)],
    ]
    for trace in traces:
        draw_circuit_lines(draw, trace, color=circuit_color, width=2)
        # Terminal dot
        ex, ey = trace[-1]
        draw.ellipse([ex - 5, ey - 5, ex + 5, ey + 5],
                     fill=(*ACCENT1, 140))

    # ── Scatter dots ─────────────────────────────────────────────────────────
    draw_dot_nodes(draw, W, H, count=80, radius=2)

    # ── Horizontal accent lines (bottom) ─────────────────────────────────────
    for i, y_off in enumerate([H - 80, H - 60, H - 45]):
        alpha = [60, 40, 25][i]
        draw.line([(0, y_off), (W, y_off)],
                  fill=(*ACCENT1, alpha), width=1)

    # ── Top-left corner bracket ───────────────────────────────────────────────
    bx, by, bl = 60, 60, 60
    draw.line([(bx, by), (bx + bl, by)], fill=ACCENT1, width=2)
    draw.line([(bx, by), (bx, by + bl)], fill=ACCENT1, width=2)

    # ── Bottom-right corner bracket ───────────────────────────────────────────
    bx2, by2 = W - 60, H - 60
    draw.line([(bx2, by2), (bx2 - bl, by2)], fill=ACCENT1, width=2)
    draw.line([(bx2, by2), (bx2, by2 - bl)], fill=ACCENT1, width=2)

    # ── Text: channel name ────────────────────────────────────────────────────
    # Draw text using basic PIL font (no external font required)
    # We'll draw large pixel-style letters manually using rectangles for a
    # techy feel, or simply use the default font scaled up via text.
    # PIL's default bitmap font is small; we scale the image for text then
    # paste it back.

    # Use a simple approach: draw text on a larger canvas then downscale
    # for anti-aliasing effect.
    txt_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(txt_layer)

    # Title: "GEEKBOT" centred below the circle
    title = "GEEKBOT"
    # Draw each character as a block; scale trick for larger text
    scale = 6
    tmp = Image.new("RGBA", (W // scale, 60), (0, 0, 0, 0))
    tdraw2 = ImageDraw.Draw(tmp)
    tdraw2.text((0, 0), title, fill=(*ACCENT3, 230))
    tmp = tmp.resize((W, 60 * scale), Image.NEAREST)
    # Position below circle
    ty = cy + 160
    txt_layer.paste(tmp, (0, ty), tmp)

    # Subtitle
    sub = "TECHNOLOGY  ·  AUTOMATION  ·  AI"
    tmp2 = Image.new("RGBA", (W // scale, 30), (0, 0, 0, 0))
    tdraw3 = ImageDraw.Draw(tmp2)
    tdraw3.text((0, 0), sub, fill=(*ACCENT1, 180))
    tmp2 = tmp2.resize((W, 30 * scale), Image.NEAREST)
    txt_layer.paste(tmp2, (0, ty + 60 * scale + 10), tmp2)

    img = Image.alpha_composite(img.convert("RGBA"), txt_layer)

    # Final subtle blur to soften glow edges
    img = img.convert("RGB")
    return img


# ─────────────────────────────────────────────────────────────────────────────
# PROFILE PICTURE  800 × 800
# ─────────────────────────────────────────────────────────────────────────────

def make_profile():
    S = 800
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    cx, cy = S // 2, S // 2
    R = S // 2 - 4  # outer radius

    # ── Background circle ─────────────────────────────────────────────────────
    draw.ellipse([cx - R, cy - R, cx + R, cy + R], fill=BG)

    # Radial gradient-ish: draw concentric filled circles from dark to slightly
    # lighter toward centre
    for r in range(R, 0, -8):
        t = 1 - r / R
        c = lerp_color(BG, (20, 30, 60), t)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)

    # ── Grid inside circle ────────────────────────────────────────────────────
    # Clip to circle by only drawing lines where they intersect the disc
    grid_layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grid_layer)
    for x in range(0, S, 50):
        gdraw.line([(x, 0), (x, S)], fill=(*GRID, 200), width=1)
    for y in range(0, S, 50):
        gdraw.line([(0, y), (S, y)], fill=(*GRID, 200), width=1)
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
    img.paste(grid_layer, (0, 0), mask)

    draw = ImageDraw.Draw(img, "RGBA")

    # ── Hex pattern ───────────────────────────────────────────────────────────
    draw_hex_grid(draw, cx, cy, radius=38, rings=4,
                  color=ACCENT1, alpha=45)

    # ── Glow rings ────────────────────────────────────────────────────────────
    for r, a in [(310, 6), (280, 10), (250, 18), (220, 28)]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     outline=(*ACCENT1, a), width=1)

    # ── Outer ring ────────────────────────────────────────────────────────────
    draw.ellipse([cx - R, cy - R, cx + R, cy + R],
                 outline=ACCENT1, width=3)

    # ── Inner emblem circle ───────────────────────────────────────────────────
    er = 160
    draw.ellipse([cx - er, cy - er, cx + er, cy + er],
                 fill=(*ACCENT2, 100))
    draw.ellipse([cx - er, cy - er, cx + er, cy + er],
                 outline=ACCENT1, width=3)

    # ── Circuit traces from emblem ────────────────────────────────────────────
    for angle in [30, 120, 210, 300]:
        rad = math.radians(angle)
        sx = cx + int((er + 4) * math.cos(rad))
        sy = cy + int((er + 4) * math.sin(rad))
        ex = cx + int((R - 10) * math.cos(rad))
        ey = cy + int((R - 10) * math.sin(rad))
        draw.line([(sx, sy), (ex, ey)], fill=(*ACCENT1, 90), width=2)
        # Terminal dot
        draw.ellipse([ex - 5, ey - 5, ex + 5, ey + 5],
                     fill=(*ACCENT1, 160))

    # ── Crosshair in emblem ───────────────────────────────────────────────────
    draw.line([(cx - er + 20, cy), (cx + er - 20, cy)],
              fill=(*ACCENT1, 180), width=2)
    draw.line([(cx, cy - er + 20), (cx, cy + er - 20)],
              fill=(*ACCENT1, 180), width=2)

    # Small dot at crosshair centre
    draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10],
                 fill=ACCENT1)
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5],
                 fill=ACCENT3)

    # ── Tick marks around outer ring ──────────────────────────────────────────
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        length = 18 if angle % 90 == 0 else 10
        ix = cx + int((R - length) * math.cos(rad))
        iy = cy + int((R - length) * math.sin(rad))
        ox = cx + int((R - 1) * math.cos(rad))
        oy = cy + int((R - 1) * math.sin(rad))
        alpha = 220 if angle % 90 == 0 else 120
        draw.line([(ix, iy), (ox, oy)], fill=(*ACCENT1, alpha), width=2)

    # ── "GB" monogram ─────────────────────────────────────────────────────────
    scale = 6
    tmp = Image.new("RGBA", (S // scale, 40), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(tmp)
    tdraw.text((0, 0), "GB", fill=(*ACCENT3, 230))
    tmp = tmp.resize((S, 40 * scale), Image.NEAREST)
    # Centre it
    text_y = cy - 40 * scale // 2 - 30
    img.paste(tmp, (0, text_y), tmp)

    # ── Clip entire image to circle ───────────────────────────────────────────
    final_mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(final_mask).ellipse([0, 0, S, S], fill=255)
    img.putalpha(final_mask)

    return img


if __name__ == "__main__":
    print("Generating banner...")
    banner = make_banner()
    banner.save("youtube_banner.png", optimize=True)
    print("Saved youtube_banner.png (2560x1440)")

    print("Generating profile picture...")
    pfp = make_profile()
    pfp.save("youtube_profile.png", optimize=True)
    print("Saved youtube_profile.png (800x800)")

    print("Done.")
