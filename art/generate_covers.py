import os
import math
import numpy as np
from PIL import Image, ImageDraw

# Resolved from this file, not the working directory, so the build produces the
# same tree whether it is run from art/ or from the repo root. static/covers is
# the single home for the art: SvelteKit bundles it into the app, and
# catalog/build-site.mjs copies it to the published site.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO_ROOT, "static", "covers")
os.makedirs(OUT_DIR, exist_ok=True)

# -------------------------------------------------------------
# BITMAP PIXEL FONT DEFINITIONS (authored for 128x128 canvas)
# -------------------------------------------------------------
# Bold, crisp 6x7 to 7x9 bitmap font for game titles
FONT_7X9 = {
    'A': [
        " 11110 ",
        "100001 ",
        "100001 ",
        "111111 ",
        "100001 ",
        "100001 ",
        "100001 ",
    ],
    'B': [
        "111110 ",
        "100001 ",
        "111110 ",
        "100001 ",
        "100001 ",
        "111110 ",
    ],
    'C': [
        " 11111 ",
        "100000 ",
        "100000 ",
        "100000 ",
        "100000 ",
        " 11111 ",
    ],
    'D': [
        "111110 ",
        "100001 ",
        "100001 ",
        "100001 ",
        "100001 ",
        "111110 ",
    ],
    'E': [
        "111111 ",
        "100000 ",
        "111110 ",
        "100000 ",
        "100000 ",
        "111111 ",
    ],
    'F': [
        "111111 ",
        "100000 ",
        "111110 ",
        "100000 ",
        "100000 ",
        "100000 ",
    ],
    'G': [
        " 11111 ",
        "100000 ",
        "100000 ",
        "100111 ",
        "100001 ",
        " 11111 ",
    ],
    'H': [
        "100001 ",
        "100001 ",
        "111111 ",
        "100001 ",
        "100001 ",
        "100001 ",
    ],
    'I': [
        "11111",
        "  1  ",
        "  1  ",
        "  1  ",
        "  1  ",
        "11111",
    ],
    'J': [
        "  1111",
        "    1 ",
        "    1 ",
        "    1 ",
        "10001 ",
        " 0110 ",
    ],
    'K': [
        "100011 ",
        "100100 ",
        "111000 ",
        "100100 ",
        "100010 ",
        "100011 ",
    ],
    'L': [
        "100000 ",
        "100000 ",
        "100000 ",
        "100000 ",
        "100000 ",
        "111111 ",
    ],
    'M': [
        "1100011",
        "1010101",
        "1001001",
        "1000001",
        "1000001",
        "1000001",
    ],
    'N': [
        "110001 ",
        "101001 ",
        "100101 ",
        "100011 ",
        "100001 ",
        "100001 ",
    ],
    'O': [
        " 11110 ",
        "100001 ",
        "100001 ",
        "100001 ",
        "100001 ",
        " 11110 ",
    ],
    'P': [
        "111110 ",
        "100001 ",
        "111110 ",
        "100000 ",
        "100000 ",
        "100000 ",
    ],
    'Q': [
        " 11110 ",
        "100001 ",
        "100001 ",
        "100001 ",
        "100101 ",
        " 11110 ",
        "      1",
    ],
    'R': [
        "111110 ",
        "100001 ",
        "111110 ",
        "100100 ",
        "100010 ",
        "100001 ",
    ],
    'S': [
        " 11111 ",
        "100000 ",
        " 11110 ",
        "    01 ",
        "100001 ",
        " 11110 ",
    ],
    'T': [
        "1111111",
        "  010  ",
        "  010  ",
        "  010  ",
        "  010  ",
        "  010  ",
    ],
    'U': [
        "100001 ",
        "100001 ",
        "100001 ",
        "100001 ",
        "100001 ",
        " 01110 ",
    ],
    'V': [
        "100001 ",
        "100001 ",
        "100001 ",
        " 10010 ",
        " 01010 ",
        "  010  ",
    ],
    'W': [
        "1000001",
        "1000001",
        "1001001",
        "1010101",
        "1100011",
        "1000001",
    ],
    'X': [
        "100001 ",
        " 10010 ",
        "  010  ",
        " 10010 ",
        "100001 ",
        "100001 ",
    ],
    'Y': [
        "100001 ",
        " 10010 ",
        "  010  ",
        "  010  ",
        "  010  ",
        "  010  ",
    ],
    'Z': [
        "111111 ",
        "    01 ",
        "   10  ",
        "  10   ",
        " 10    ",
        "111111 ",
    ],
    '0': [
        " 11110 ",
        "100001 ",
        "100011 ",
        "110001 ",
        "100001 ",
        " 11110 ",
    ],
    '1': [
        "  11  ",
        " 101  ",
        "   1  ",
        "   1  ",
        "   1  ",
        " 1111 ",
    ],
    '2': [
        " 11110 ",
        "100001 ",
        "    01 ",
        "  0110 ",
        " 10000 ",
        "111111 ",
    ],
    '3': [
        "111110 ",
        "    01 ",
        "  1110 ",
        "    01 ",
        "100001 ",
        " 11110 ",
    ],
    '4': [
        "10001  ",
        "10001  ",
        "10001  ",
        "111111 ",
        "    1  ",
        "    1  ",
    ],
    '5': [
        "111111 ",
        "100000 ",
        "111110 ",
        "    01 ",
        "100001 ",
        " 11110 ",
    ],
    '6': [
        " 11110 ",
        "100000 ",
        "111110 ",
        "100001 ",
        "100001 ",
        " 11110 ",
    ],
    '7': [
        "111111 ",
        "    01 ",
        "   10  ",
        "  10   ",
        " 10    ",
        " 10    ",
    ],
    '8': [
        " 11110 ",
        "100001 ",
        " 11110 ",
        "100001 ",
        "100001 ",
        " 11110 ",
    ],
    '9': [
        " 11110 ",
        "100001 ",
        "100001 ",
        " 01111 ",
        "    01 ",
        " 11110 ",
    ],
    '\'': [
        " 11 ",
        " 10 ",
        " 1  ",
        "    ",
        "    ",
        "    ",
    ],
    ':': [
        "   ",
        " 1 ",
        "   ",
        "   ",
        " 1 ",
        "   ",
    ],
    '-': [
        "      ",
        "      ",
        "11111 ",
        "      ",
        "      ",
        "      ",
    ],
    '.': [
        "   ",
        "   ",
        "   ",
        "   ",
        " 1 ",
        " 1 ",
    ],
    '&': [
        " 0110  ",
        " 1001  ",
        "  010  ",
        " 10101 ",
        "100010 ",
        " 01101 ",
    ],
    ' ': [
        "   ",
        "   ",
        "   ",
        "   ",
        "   ",
        "   ",
    ]
}

BAYER_4X4 = [
    [ 0,  8,  2, 10],
    [12,  4, 14,  6],
    [ 3, 11,  1,  9],
    [15,  7, 13,  5]
]

def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )

def dither_lerp(c1, c2, t, x, y):
    """Bayer dither between c1 and c2."""
    t = max(0.0, min(1.0, t))
    threshold = (BAYER_4X4[y % 4][x % 4] + 0.5) / 16.0
    return c2 if t > threshold else c1

def dither_gradient_v(img, y0, y1, c_top, c_bot, x0=0, x1=128):
    pixels = img.load()
    h = max(1, y1 - y0)
    for y in range(y0, y1):
        if y < 0 or y >= 128:
            continue
        t = (y - y0) / float(h)
        for x in range(x0, x1):
            if x < 0 or x >= 128:
                continue
            pixels[x, y] = dither_lerp(c_top, c_bot, t, x, y)

def draw_bitmap_text(img, text, cx, cy, fg_color, bg_color=(8, 6, 12)):
    """Render uppercase text centered at (cx, cy) with 1px dark drop shadow / outline."""
    text = text.upper()
    glyphs = [FONT_7X9.get(ch, FONT_7X9[' ']) for ch in text]
    widths = [len(g[0]) for g in glyphs]
    total_w = sum(widths) + (len(text) - 1) * 1
    
    start_x = int(cx - total_w / 2)
    start_y = int(cy - 3)
    
    pixels = img.load()
    
    # 1px outline/shadow pass
    if bg_color is not None:
        cur_x = start_x
        for g in glyphs:
            gw = len(g[0])
            gh = len(g)
            for r in range(gh):
                for c in range(gw):
                    if g[r][c] == '1':
                        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (-1, 1), (1, -1), (-1, -1), (0, 2)]:
                            px, py = cur_x + c + ox, start_y + r + oy
                            if 0 <= px < 128 and 0 <= py < 128:
                                pixels[px, py] = bg_color
            cur_x += gw + 1
            
    # Text foreground pass
    cur_x = start_x
    for g in glyphs:
        gw = len(g[0])
        gh = len(g)
        for r in range(gh):
            for c in range(gw):
                if g[r][c] == '1':
                    px, py = cur_x + c, start_y + r
                    if 0 <= px < 128 and 0 <= py < 128:
                        pixels[px, py] = fg_color
        cur_x += gw + 1

def darken_lower_band(img, y_start=76, darken_factor=0.36, tint=(20, 12, 28)):
    """Darkens the bottom ~40% for title contrast while maintaining artwork continuity."""
    pixels = img.load()
    for y in range(y_start, 128):
        blend = min(1.0, (y - y_start + 1) / 5.0)
        eff_factor = 1.0 - (1.0 - darken_factor) * blend
        for x in range(128):
            r, g, b = pixels[x, y]
            nr = int(r * eff_factor + tint[0] * (1.0 - eff_factor) * 0.3)
            ng = int(g * eff_factor + tint[1] * (1.0 - eff_factor) * 0.3)
            nb = int(b * eff_factor + tint[2] * (1.0 - eff_factor) * 0.3)
            pixels[x, y] = (nr, ng, nb)

def quantify_palette(img, max_colors=32):
    """Ensures the image strictly has <= max_colors."""
    # Convert to adaptive palette with no dither to preserve exact pixel art
    pal_img = img.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    return pal_img.convert('RGB')

def save_cover(img128, filename):
    """Enforces palette count <= 32 and saves 4x nearest-neighbor 512x512 PNG."""
    clean_128 = quantify_palette(img128, 32)
    img512 = clean_128.resize((512, 512), Image.Resampling.NEAREST)
    save_512(img512, filename)


def save_512(img512, filename):
    """Writes a finished 512x512 tile. The one place covers are written."""
    os.makedirs(OUT_DIR, exist_ok=True)
    img512.save(os.path.join(OUT_DIR, filename), "PNG")
    print(f"Generated {filename} -> 512x512 PNG")

