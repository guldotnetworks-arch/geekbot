import math
from PIL import Image, ImageDraw

# --- Palette ---
BG       = (10, 10, 20)
GRID     = (22, 28, 50)
CYAN     = (0, 212, 255)
PURPLE   = (123, 47, 255)
WHITE    = (255, 255, 255)
DIM      = (80, 90, 120)


def draw_grid(draw, w, h, spacing=80, color=GRID):
    for x in range(0, w, spacing):
        draw.line([(x, 0), (x, h)], fill=color, width=1)
    for y in range(0, h, spacing):
        draw.line([(0, y), (w, y)], fill=color, width=1)


def hex_points(cx, cy, r, angle_offset=0):
    pts = []
    for i in range(6):
        a = math.radians(60 * i + angle_offset)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw_hexagon(draw, cx, cy, r, outline, width=2, angle_offset=0):
    pts = hex_points(cx, cy, r, angle_offset)
    draw.polygon(pts, outline=outline, width=width)


def gradient_rect(img, x0, y0, x1, y1, color_left, color_right):
    draw = ImageDraw.Draw(img)
    width = x1 - x0
    for i in range(width):
        t = i / max(width - 1, 1)
        r = int(color_left[0] + t * (color_right[0] - color_left[0]))
        g = int(color_left[1] + t * (color_right[1] - color_left[1]))
        b = int(color_left[2] + t * (color_right[2] - color_left[2]))
        draw.line([(x0 + i, y0), (x0 + i, y1)], fill=(r, g, b))


def glow_circle(img, cx, cy, radius, color, steps=30):
    draw = ImageDraw.Draw(img, 'RGBA')
    for i in range(steps, 0, -1):
        r_i = int(radius * i / steps)
        alpha = int(60 * (1 - i / steps))
        c = color + (alpha,)
        draw.ellipse(
            [cx - r_i, cy - r_i, cx + r_i, cy + r_i],
            fill=c
        )


# ─────────────────────────────────────────────
# BANNER  2560 × 1440
# ─────────────────────────────────────────────
def make_banner():
    W, H = 2560, 1440
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Grid
    draw_grid(draw, W, H, spacing=80)

    # Faint diagonal accent lines
    for offset in range(-2000, 4000, 180):
        x0, y0 = offset, 0
        x1, y1 = offset + H, H
        draw.line([(x0, y0), (x1, y1)], fill=(18, 24, 45), width=1)

    # Horizontal gradient accent bar near bottom third
    gradient_rect(img, 0, H - 6, W, H, PURPLE, CYAN)

    # Glowing orbs
    glow_circle(img, 480, 720, 420, PURPLE, steps=50)
    glow_circle(img, W - 520, 680, 380, CYAN, steps=50)

    draw = ImageDraw.Draw(img)

    # Large hollow hexagons — left cluster
    for r, alpha_hint in [(260, 60), (340, 35), (420, 20)]:
        draw_hexagon(draw, 480, 720, r, PURPLE + (alpha_hint,) if False else (
            int(PURPLE[0] * alpha_hint / 60),
            int(PURPLE[1] * alpha_hint / 60),
            int(PURPLE[2] * alpha_hint / 60),
        ), width=2, angle_offset=30)

    # Large hollow hexagons — right cluster
    for r, col in [(240, CYAN), (310, (0, 150, 200)), (380, (0, 100, 140))]:
        draw_hexagon(draw, W - 520, 680, r, col, width=2, angle_offset=0)

    # Small decorative hexagons scattered
    small_hexes = [
        (900, 280, 60, CYAN),
        (1100, 900, 45, PURPLE),
        (1600, 340, 55, CYAN),
        (1900, 980, 50, PURPLE),
        (700, 1100, 40, CYAN),
        (2100, 300, 48, CYAN),
    ]
    for cx, cy, r, col in small_hexes:
        draw_hexagon(draw, cx, cy, r, col, width=1, angle_offset=30)

    # Connecting lines between small hexes and glow centres
    for cx, cy, r, col in small_hexes[:3]:
        draw.line([(480, 720), (cx, cy)], fill=(60, 20, 120), width=1)
    for cx, cy, r, col in small_hexes[3:]:
        draw.line([(W - 520, 680), (cx, cy)], fill=(0, 80, 120), width=1)

    # Central text block
    # "GEEKBOT" in large blocky lettering using draw.text
    # We'll simulate bold large text with rectangles since we can't guarantee fonts
    center_x, center_y = W // 2, H // 2

    # Title bar: a horizontal accent strip behind the text
    bar_h = 110
    gradient_rect(img, center_x - 460, center_y - bar_h // 2,
                  center_x + 460, center_y + bar_h // 2,
                  (20, 10, 40), (10, 30, 50))
    draw = ImageDraw.Draw(img)
    draw.rectangle(
        [center_x - 460, center_y - bar_h // 2,
         center_x + 460, center_y + bar_h // 2],
        outline=CYAN, width=2
    )

    # Corner accents on the title box
    corner = 30
    cx0, cy0 = center_x - 460, center_y - bar_h // 2
    cx1, cy1 = center_x + 460, center_y + bar_h // 2
    for sx, sy, ex1, ey1, ex2, ey2 in [
        (cx0, cy0, cx0 + corner, cy0, cx0, cy0 + corner),
        (cx1, cy0, cx1 - corner, cy0, cx1, cy0 + corner),
        (cx0, cy1, cx0 + corner, cy1, cx0, cy1 - corner),
        (cx1, cy1, cx1 - corner, cy1, cx1, cy1 - corner),
    ]:
        draw.line([(sx, sy), (ex1, ey1)], fill=PURPLE, width=4)
        draw.line([(sx, sy), (ex2, ey2)], fill=PURPLE, width=4)

    # Draw "GEEKBOT" text — large pixel font simulation with rectangles
    def draw_pixel_letter(draw, letter, ox, oy, scale=10, color=WHITE):
        """Simple 5×7 pixel font for uppercase letters."""
        glyphs = {
            'G': [(0,0),(1,0),(2,0),(3,0),(4,0),
                  (0,1),(0,2),(0,3),(3,3),(4,3),
                  (0,4),(3,4),(4,4),(0,5),(0,6),
                  (1,6),(2,6),(3,6),(4,6)],
            'E': [(0,0),(1,0),(2,0),(3,0),(4,0),
                  (0,1),(0,2),(1,2),(2,2),(3,2),
                  (0,3),(0,4),(0,5),(0,6),
                  (1,6),(2,6),(3,6),(4,6)],
            'K': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),
                  (3,0),(2,1),(1,2),(2,3),(1,3),
                  (2,4),(3,5),(4,6)],
            'B': [(0,0),(1,0),(2,0),(3,0),
                  (0,1),(4,1),(0,2),(4,2),
                  (0,3),(1,3),(2,3),(3,3),
                  (0,4),(4,4),(0,5),(4,5),
                  (0,6),(1,6),(2,6),(3,6)],
            'O': [(1,0),(2,0),(3,0),
                  (0,1),(4,1),(0,2),(4,2),(0,3),(4,3),
                  (0,4),(4,4),(0,5),(4,5),
                  (1,6),(2,6),(3,6)],
            'T': [(0,0),(1,0),(2,0),(3,0),(4,0),
                  (2,1),(2,2),(2,3),(2,4),(2,5),(2,6)],
        }
        pixels = glyphs.get(letter, [])
        for px, py in pixels:
            draw.rectangle(
                [ox + px * scale, oy + py * scale,
                 ox + px * scale + scale - 2,
                 oy + py * scale + scale - 2],
                fill=color
            )

    word = 'GEEKBOT'
    letter_w = 5 * 14 + 8   # scale=14, gap=8
    total_w = len(word) * letter_w - 8
    tx = center_x - total_w // 2
    ty = center_y - 7 * 14 // 2

    colors = [CYAN, CYAN, WHITE, WHITE, PURPLE, PURPLE, PURPLE]
    for i, ch in enumerate(word):
        draw_pixel_letter(draw, ch, tx + i * letter_w, ty, scale=14, color=colors[i])

    # Tagline dots
    tag_y = center_y + bar_h // 2 + 36
    for i, dot_x in enumerate(range(center_x - 60, center_x + 70, 30)):
        col = CYAN if i % 2 == 0 else PURPLE
        draw.ellipse([dot_x - 6, tag_y - 6, dot_x + 6, tag_y + 6], fill=col)

    # Thin horizontal lines above & below center block
    for dy in [-200, 200]:
        y = center_y + dy
        gradient_rect(img, center_x - 800, y - 1, center_x + 800, y + 1,
                      (0, 0, 0), CYAN)
        gradient_rect(img, center_x - 800, y - 1, center_x + 800, y + 1,
                      PURPLE, (0, 0, 0))

    img.save('youtube_banner.png')
    print('Saved youtube_banner.png')


# ─────────────────────────────────────────────
# PROFILE PICTURE  800 × 800
# ─────────────────────────────────────────────
def make_profile():
    W, H = 800, 800
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Subtle grid
    draw_grid(draw, W, H, spacing=50)

    cx, cy = W // 2, H // 2

    # Glowing background orb
    glow_circle(img, cx, cy, 340, PURPLE, steps=60)
    glow_circle(img, cx, cy, 200, CYAN, steps=40)

    draw = ImageDraw.Draw(img)

    # Outer hexagon ring
    draw_hexagon(draw, cx, cy, 330, PURPLE, width=3, angle_offset=30)
    draw_hexagon(draw, cx, cy, 310, (80, 30, 160), width=1, angle_offset=30)

    # Inner hexagon
    draw_hexagon(draw, cx, cy, 220, CYAN, width=3, angle_offset=0)
    draw_hexagon(draw, cx, cy, 200, (0, 140, 180), width=1, angle_offset=0)

    # Spokes from outer to inner hex
    outer_pts = hex_points(cx, cy, 310, angle_offset=30)
    inner_pts = hex_points(cx, cy, 220, angle_offset=0)
    for i in range(6):
        op = outer_pts[i]
        ip = inner_pts[i % 6]
        draw.line([op, ip], fill=(40, 20, 80), width=1)

    # Innermost hexagon fill
    inner_fill_pts = hex_points(cx, cy, 180, angle_offset=0)
    draw.polygon(inner_fill_pts, fill=(14, 14, 30))
    draw_hexagon(draw, cx, cy, 180, CYAN, width=2, angle_offset=0)

    # Central "G" pixel letter
    scale = 18
    gw = 5 * scale
    gh = 7 * scale
    ox = cx - gw // 2
    oy = cy - gh // 2

    G_pixels = [
        (0,0),(1,0),(2,0),(3,0),(4,0),
        (0,1),(0,2),(0,3),(3,3),(4,3),
        (0,4),(3,4),(4,4),(0,5),
        (0,6),(1,6),(2,6),(3,6),(4,6),
    ]
    for px, py in G_pixels:
        draw.rectangle(
            [ox + px * scale, oy + py * scale,
             ox + px * scale + scale - 3,
             oy + py * scale + scale - 3],
            fill=WHITE
        )

    # Small corner dots
    for dx, dy in [(-cx + 40, -cy + 40), (cx - 40, -cy + 40),
                   (-cx + 40, cy - 40), (cx - 40, cy - 40)]:
        draw.ellipse(
            [cx + dx - 8, cy + dy - 8, cx + dx + 8, cy + dy + 8],
            fill=CYAN
        )

    # Bottom accent bar
    gradient_rect(img, 0, H - 4, W, H, PURPLE, CYAN)

    img.save('youtube_profile.png')
    print('Saved youtube_profile.png')


make_banner()
make_profile()
