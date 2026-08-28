import os
import math
import numpy as np
from PIL import Image, ImageDraw
from generate_covers import draw_bitmap_text, darken_lower_band, quantify_palette, save_512
from build_batch2 import process_cover

SOURCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sources")

BAYER_4X4 = [
    [ 0,  8,  2, 10],
    [12,  4, 14,  6],
    [ 3, 11,  1,  9],
    [15,  7, 13,  5]
]

def lerp(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )

def dither_lerp(c1, c2, t, x, y):
    t = max(0.0, min(1.0, t))
    thresh = (BAYER_4X4[y % 4][x % 4] + 0.5) / 16.0
    return c2 if t > thresh else c1

def dither_rect(px, x0, y0, x1, y1, c1, c2, vertical=True):
    for y in range(y0, y1):
        if y < 0 or y >= 128:
            continue
        for x in range(x0, x1):
            if x < 0 or x >= 128:
                continue
            t = (y - y0) / float(max(1, y1 - y0)) if vertical else (x - x0) / float(max(1, x1 - x0))
            px[x, y] = dither_lerp(c1, c2, t, x, y)

def dither_radial(px, cx, cy, radius, c_center, c_edge):
    r_sq = radius * radius
    for y in range(max(0, cy - radius), min(128, cy + radius + 1)):
        for x in range(max(0, cx - radius), min(128, cx + radius + 1)):
            dist_sq = (x - cx) ** 2 + (y - cy) ** 2
            if dist_sq <= r_sq:
                t = math.sqrt(dist_sq) / float(radius)
                px[x, y] = dither_lerp(c_center, c_edge, t, x, y)

def save_and_process(img, prefix, filename, lines, text_color, shadow_color, tint_color, y_positions=None):
    # These scenes are composed in code, so nothing is written to sources/.
    # That directory holds genuine source illustrations and is the record of
    # what was drawn rather than generated; procedural output saved there would
    # claim an illustration exists where none does.
    # Same reduction as process_cover, but the 128x128 canvas is already in
    # hand, so there is nothing to load and nothing to downscale.
    darken_lower_band(img, y_start=74, darken_factor=0.32, tint=tint_color)
    if y_positions is None:
        y_positions = [98] if len(lines) == 1 else [88, 106]
    for line, y_pos in zip(lines, y_positions):
        draw_bitmap_text(img, line, 64, y_pos, fg_color=text_color, bg_color=shadow_color)
    clean_128 = quantify_palette(img, 32)
    save_512(clean_128.resize((512, 512), Image.Resampling.NEAREST), filename)

# =========================================================================
# 13. ONE MUST FALL 2097 (amber/orange)
# =========================================================================
def make_one_must_fall():
    img = Image.new('RGB', (128, 128), (20, 10, 5))
    px = img.load()
    
    # Arena Bleachers & Crowd (y=0..50)
    dither_rect(px, 0, 0, 128, 50, (25, 10, 4), (65, 28, 10), vertical=True)
    for ry in [10, 18, 26, 34, 42]:
        for x in range(0, 128):
            px[x, ry] = (85, 38, 12)
            if (x + ry) % 3 == 0:
                px[x, ry - 1] = (15, 6, 2)
                px[x, ry - 2] = (18, 8, 3)
                if x % 7 == 0:
                    px[x, ry - 3] = (25, 10, 4)

    # Overhead truss & spotlights
    for x in range(0, 128):
        px[x, 5] = (110, 55, 18)
        px[x, 7] = (70, 32, 10)
        if x % 16 == 0:
            for y in range(0, 50):
                px[x, y] = (95, 45, 14)

    for lx in [18, 46, 82, 110]:
        for bx in range(lx - 4, lx + 5):
            for by in range(2, 6):
                px[bx, by] = (255, 245, 200)
        for y in range(6, 48):
            w = int(2 + (y - 6) * 0.3)
            for x in range(lx - w, lx + w + 1):
                if 0 <= x < 128 and (x + y) % 2 == 0:
                    px[x, y] = (160, 95, 30)

    # Steel Hazard Floor (y=50..128)
    for y in range(50, 128):
        t = (y - 50) / 78.0
        for x in range(0, 128):
            base_r = int(45 + t * 35)
            base_g = int(24 + t * 20)
            base_b = int(14 + t * 10)
            px[x, y] = (base_r, base_g, base_b)
            if x % 12 == 0 or (y - 50) % 10 == 0:
                px[x, y] = (base_r + 30, base_g + 18, base_b + 10)
            if 50 <= y <= 54 and (x % 16 < 8):
                px[x, y] = (235, 160, 20)

    # Left Blue/Chrome Cyber-Ninja Mech (Katana, x=24..68, y=28..74)
    for y in range(28, 36):
        for x in range(32, 42):
            px[x, y] = (30, 65, 135)
            if x == 32 or y == 28:
                px[x, y] = (75, 135, 220)
    for x in range(35, 42):
        px[x, 31] = (0, 245, 255)
        px[x, 32] = (180, 250, 255)

    for y in range(36, 54):
        for x in range(28, 44):
            px[x, y] = (35, 75, 150)
            if x == 28 or y == 36:
                px[x, y] = (90, 155, 240)
            if 42 <= y <= 48 and 32 <= x <= 40:
                px[x, y] = (15, 35, 75)

    for y in range(34, 42):
        for x in range(24, 30):
            px[x, y] = (80, 140, 225)
        for x in range(42, 48):
            px[x, y] = (80, 140, 225)

    for x in range(44, 66):
        for y in range(37, 43):
            px[x, y] = (45, 95, 185)
            if y == 37:
                px[x, y] = (110, 180, 250)
    for y in range(36, 44):
        for x in range(64, 70):
            px[x, y] = (130, 195, 255)

    for y in range(54, 74):
        for x in range(22, 32):
            px[x, y] = (25, 55, 115)
            if x == 22:
                px[x, y] = (65, 120, 200)
        for x in range(36, 48):
            px[x, y] = (35, 75, 145)
            if x == 47:
                px[x, y] = (80, 145, 225)

    # Impact Clash Sparks
    for r in range(1, 10):
        for deg in range(0, 360, 45):
            rad = math.radians(deg)
            sx = int(67 + r * math.cos(rad))
            sy = int(40 + r * math.sin(rad))
            if 0 <= sx < 128 and 0 <= sy < 128:
                px[sx, sy] = (255, 255, 240) if r < 4 else (255, 210, 40)
    for ex, ey in [(66, 32), (72, 30), (76, 42), (74, 48), (64, 48), (58, 44), (78, 36), (82, 42)]:
        px[ex, ey] = (255, 255, 255)
        px[ex+1, ey] = (0, 240, 255)

    # Right Red/Bronze Heavy Brawler Mech (Pyros, x=70..106, y=26..74)
    for y in range(28, 36):
        for x in range(80, 92):
            px[x, y] = (180, 42, 18)
            if x == 80 or y == 28:
                px[x, y] = (235, 95, 35)
    for y in range(24, 30):
        px[78, y] = (245, 185, 30)
        px[93, y] = (245, 185, 30)
    px[83, 31] = (255, 220, 50)
    px[88, 31] = (255, 220, 50)

    for y in range(36, 56):
        for x in range(74, 96):
            px[x, y] = (165, 38, 16)
            if x == 95 or y == 36:
                px[x, y] = (225, 85, 30)
            if 40 <= y <= 50 and 80 <= x <= 90:
                px[x, y] = (245, 175, 25)

    for y in range(32, 42):
        for x in range(68, 76):
            px[x, y] = (200, 55, 22)
        for x in range(94, 104):
            px[x, y] = (150, 32, 14)
    for y in range(40, 58):
        for x in range(96, 104):
            px[x, y] = (140, 30, 14)
    for y in range(56, 74):
        for x in range(74, 84):
            px[x, y] = (130, 28, 12)
        for x in range(88, 100):
            px[x, y] = (110, 22, 10)

    save_and_process(img, "one_must_fall_raw", "one-must-fall-2097.png", ["ONE MUST FALL", "2097"], (255, 225, 75), (25, 8, 4), (35, 18, 8))

# =========================================================================
# 14. OPENRA (blue/cyan)
# =========================================================================
def make_openra():
    img = Image.new('RGB', (128, 128), (8, 22, 38))
    px = img.load()
    
    dither_rect(px, 0, 0, 128, 38, (12, 35, 75), (45, 120, 190), vertical=True)
    for cx, cy in [(20, 12), (75, 8), (110, 16)]:
        dither_radial(px, cx, cy, 8, (180, 220, 255), (60, 130, 195))

    for y in range(28, 128):
        for x in range(0, 128):
            px[x, y] = (25, 85, 45)
            if (x + y * 2) % 5 == 0:
                px[x, y] = (35, 115, 60)
            if (x * 7 + y * 11) % 17 == 0:
                px[x, y] = (18, 60, 32)
            if (x * 5 + y * 3) % 23 == 0:
                px[x, y] = (110, 85, 40)

    dither_radial(px, 105, 42, 26, (0, 240, 230), (20, 95, 65))
    for y in range(18, 74):
        for x in range(70, 128):
            dist = math.hypot((x - 105) * 0.8, (y - 42) * 1.0)
            if dist <= 24:
                px[x, y] = (0, 150, 170)
                if (x + y) % 3 == 0:
                    px[x, y] = (0, 245, 235)
                if (x * 7 + y * 13) % 11 == 0:
                    px[x, y] = (215, 255, 250)
                if (x + y) % 5 == 0:
                    px[x, y] = (35, 255, 165)
                if (x * 3 + y * 7) % 17 == 0:
                    px[x, y] = (185, 85, 255)
                if x % 5 == 0 and y % 4 == 0:
                    for cy in range(max(0, y-5), y):
                        px[x, cy] = (0, 255, 240)

    for y in range(32, 64):
        for x in range(8, 58):
            px[x, y] = (45, 55, 68)
            if x == 8 or y == 32:
                px[x, y] = (95, 115, 140)
            if (x + y) % 7 == 0:
                px[x, y] = (65, 75, 90)
    for y in range(20, 46):
        for x in range(12, 40):
            px[x, y] = (50, 85, 130)
            if x == 12 or y == 20:
                px[x, y] = (100, 160, 220)
            if (x * y) % 9 == 0:
                px[x, y] = (140, 190, 245)
    dither_radial(px, 26, 18, 7, (220, 245, 255), (70, 110, 150))
    px[26, 18] = (255, 255, 255)
    for y in range(38, 56):
        for x in range(42, 56):
            px[x, y] = (30, 45, 65)
            if y % 4 == 0:
                px[x, y] = (60, 235, 255)
    px[16, 22] = (255, 45, 35)
    px[20, 22] = (45, 255, 65)
    px[44, 40] = (255, 140, 30)

    for y in range(58, 74):
        for x in range(50, 84):
            px[x, y] = (20, 25, 32)
            if y == 58 or y == 73 or (x % 5 == 0):
                px[x, y] = (80, 95, 115)
    for y in range(46, 64):
        for x in range(52, 82):
            px[x, y] = (225, 150, 25)
            if x == 52 or y == 46:
                px[x, y] = (255, 210, 50)
            if 50 <= y <= 58 and 56 <= x <= 72:
                px[x, y] = (175, 95, 15)
    for y in range(52, 68):
        for x in range(76, 88):
            px[x, y] = (70, 85, 105)
            if (x + y) % 2 == 0:
                px[x, y] = (0, 255, 240)

    save_and_process(img, "openra_raw", "openra.png", ["OPENRA"], (210, 245, 255), (8, 14, 28), (10, 22, 45))

# =========================================================================
# 15. RAPTOR: CALL OF THE SHADOWS (amber/orange)
# =========================================================================
def make_raptor():
    img = Image.new('RGB', (128, 128), (25, 12, 4))
    px = img.load()
    
    dither_rect(px, 0, 0, 128, 50, (45, 18, 6), (160, 80, 20), vertical=True)
    
    for y in range(30, 128):
        for x in range(0, 128):
            px[x, y] = (75, 38, 14)
            if (x * 3 + y * 7) % 9 == 0:
                px[x, y] = (110, 60, 20)
            if (x + y) % 11 == 0:
                px[x, y] = (50, 24, 8)
            if (x * 13 + y * 5) % 23 == 0:
                px[x, y] = (145, 80, 25)
            if (x * 7 + y * 19) % 31 == 0:
                px[x, y] = (195, 140, 60)
            if (x * 3 + y * 17) % 37 == 0:
                px[x, y] = (40, 20, 8)

    for y in range(6, 74):
        for x in range(28, 48):
            px[x, y] = (45, 26, 12)
            if x == 38 and y % 8 < 4:
                px[x, y] = (230, 160, 30)
            if (x == 28 or x == 47) and y % 6 == 0:
                px[x, y] = (0, 240, 255)
    for y in range(8, 42):
        for x in range(82, 120):
            px[x, y] = (55, 30, 12)
            if x == 82 or y == 8:
                px[x, y] = (110, 65, 25)
            if y == 24 and 86 <= x <= 114:
                px[x, y] = (20, 10, 4)
            if (x + y) % 6 < 3 and (x >= 115 or y <= 12):
                px[x, y] = (235, 175, 20)
    for y in range(12, 28):
        px[18, y] = (120, 125, 135)
    dither_radial(px, 18, 12, 5, (200, 240, 255), (80, 85, 95))
    px[18, 12] = (255, 40, 30)

    dither_radial(px, 102, 54, 12, (150, 75, 25), (45, 22, 8))
    dither_radial(px, 104, 28, 18, (110, 70, 45), (45, 22, 8))
    dither_radial(px, 104, 28, 14, (235, 120, 15), (190, 45, 10))
    dither_radial(px, 104, 28, 8, (255, 210, 40), (235, 120, 15))
    px[104, 28] = (255, 255, 255)
    for sx, sy in [(98, 20), (112, 22), (108, 36), (96, 32), (116, 30)]:
        px[sx, sy] = (180, 120, 80)

    for y in range(20, 66):
        span = int((y - 20) * 0.9)
        for x in range(63 - span, 64 + span):
            if 0 <= x < 128:
                px[x, y] = (65, 70, 85)
                if x == 63 - span or x == 63 + span:
                    px[x, y] = (170, 175, 195)
                if (x + y) % 5 == 0:
                    px[x, y] = (110, 115, 135)
                if x in [63 - span + 1, 63 + span - 1]:
                    px[x, y] = (25, 30, 40)
    for y in range(14, 62):
        for x in range(58, 69):
            px[x, y] = (110, 115, 135)
            if y == 14 or x == 58:
                px[x, y] = (170, 175, 195)
            if y == 38 and 60 <= x <= 66:
                px[x, y] = (220, 30, 20)
    for y in range(22, 36):
        for x in range(60, 67):
            px[x, y] = (0, 240, 255)
            if x == 60 or y == 22:
                px[x, y] = (220, 250, 255)
            if x == 63 and y == 28:
                px[x, y] = (15, 60, 90)
    for y in range(64, 76):
        for x in range(59, 63):
            px[x, y] = (255, 160, 20)
        for x in range(64, 68):
            px[x, y] = (255, 160, 20)
        px[61, y] = (255, 255, 200)
        px[66, y] = (255, 255, 200)

    for y in range(0, 20):
        px[50, y] = (255, 240, 80)
        px[51, y] = (255, 140, 20)
        px[76, y] = (255, 240, 80)
        px[77, y] = (255, 140, 20)
        if y % 3 == 0:
            px[49, y] = (255, 255, 255)
            px[78, y] = (255, 255, 255)

    save_and_process(img, "raptor_raw", "raptor-call-of-the-shadows.png", ["RAPTOR", "CALL OF SHADOWS"], (255, 225, 75), (25, 8, 4), (35, 18, 8))

# =========================================================================
# 16. RISE OF THE TRIAD (amber/orange)
# =========================================================================
def make_rise_of_the_triad():
    img = Image.new('RGB', (128, 128), (25, 10, 4))
    px = img.load()
    
    dither_rect(px, 0, 0, 128, 45, (18, 6, 2), (85, 30, 8), vertical=True)
    
    for y in range(12, 128):
        for x in range(70, 128):
            px[x, y] = (65, 35, 15)
            if y % 6 == 0 or x % 10 == 0:
                px[x, y] = (30, 14, 6)
            if 18 <= y <= 32 and 84 <= x <= 96:
                px[x, y] = (15, 6, 2)
    for x in range(70, 128, 8):
        for y in range(8, 12):
            px[x, y] = (75, 40, 18)

    for y in range(40, 74):
        for x in range(12, 38):
            px[x, y] = (35, 45, 55)
            if x == 12 or y == 40:
                px[x, y] = (85, 105, 130)
    for y in range(32, 40):
        for x in range(18, 30):
            px[x, y] = (235, 180, 130)
            if y == 32:
                px[x, y] = (45, 25, 12)

    for x in range(28, 56):
        for y in range(36, 42):
            px[x, y] = (50, 55, 65)
            if y == 36:
                px[x, y] = (110, 120, 140)

    for x in range(54, 100):
        t = (x - 54) / 46.0
        y = int(38 - 8 * math.sin(t * 3.14))
        for dy in range(-2, 3):
            if 0 <= y + dy < 128:
                px[x, y + dy] = (255, 180, 40)
        px[x, y] = (255, 255, 220)
        if x % 4 == 0:
            for sy in range(y - 5, y + 6):
                if 0 <= sy < 128:
                    px[x, sy] = (180, 170, 160)

    dither_radial(px, 102, 30, 20, (255, 255, 220), (220, 70, 10))
    dither_radial(px, 102, 30, 10, (255, 255, 255), (255, 180, 30))

    save_and_process(img, "rise_of_the_triad_raw", "rise-of-the-triad-shareware.png", ["RISE OF THE TRIAD"], (255, 225, 75), (25, 8, 4), (35, 18, 8))

# =========================================================================
# 17. SECRET AGENT (amber/orange)
# =========================================================================
def make_secret_agent():
    img = Image.new('RGB', (128, 128), (8, 4, 12))
    px = img.load()
    
    dither_rect(px, 0, 0, 128, 45, (8, 6, 18), (35, 22, 10), vertical=True)
    
    for y in range(25, 128):
        for x in range(60, 128):
            px[x, y] = (55, 28, 14)
            if y % 6 == 0 or (x + y) % 12 == 0:
                px[x, y] = (25, 10, 5)
            if 35 <= y <= 55 and 75 <= x <= 95:
                px[x, y] = (15, 8, 4)
                if (x == 85 or y == 45):
                    px[x, y] = (45, 20, 8)

    for y in range(45, 128):
        for x in range(0, 60):
            px[x, y] = (30, 15, 8)
            if (x + y) % 8 == 0:
                px[x, y] = (50, 25, 12)
    for x in range(0, 60):
        px[x, 44] = (90, 45, 18)
        if x % 10 == 0:
            for y in range(44, 52):
                px[x, y] = (90, 45, 18)

    for y in range(10, 74):
        cx = int(85 - (y - 10) * 0.4)
        w = int(4 + (y - 10) * 0.35)
        for x in range(cx - w, cx + w):
            if 0 <= x < 128 and (x + y) % 2 == 0:
                px[x, y] = (235, 185, 60)

    for y in range(30, 36):
        for x in range(18, 36):
            px[x, y] = (18, 10, 4)
    for x in range(14, 40):
        px[x, 35] = (25, 14, 6)

    for y in range(36, 68):
        for x in range(18, 38):
            px[x, y] = (22, 12, 6)
            if x == 18 or y == 36:
                px[x, y] = (55, 28, 12)
            if 48 <= y <= 52:
                px[x, y] = (12, 6, 2)

    for x in range(36, 54):
        for y in range(42, 45):
            px[x, y] = (60, 65, 75)
    for x in range(54, 128):
        px[x, 43] = (255, 40, 20)

    save_and_process(img, "secret_agent_raw", "secret-agent.png", ["SECRET AGENT"], (255, 225, 75), (25, 8, 4), (35, 18, 8))

# =========================================================================
# 18. SOLTYS (violet/purple)
# =========================================================================
def make_soltys():
    img = Image.new('RGB', (128, 128), (14, 6, 24))
    px = img.load()
    
    dither_rect(px, 0, 0, 128, 45, (18, 6, 32), (65, 22, 75), vertical=True)
    dither_radial(px, 105, 18, 12, (245, 235, 255), (140, 70, 160))

    for y in range(25, 128):
        for x in range(0, 55):
            px[x, y] = (50, 18, 40)
            if y % 5 == 0:
                px[x, y] = (25, 8, 20)
    for x in range(0, 60):
        y = int(25 - (55 - x) * 0.35)
        if 0 <= y < 128:
            px[x, y] = (85, 30, 65)

    for y in range(40, 128):
        for x in range(0, 128):
            if px[x, y] == (14, 6, 24) or y >= 45:
                px[x, y] = (35, 14, 45)
                if (x + y * 2) % 6 == 0:
                    px[x, y] = (55, 20, 65)

    for y in range(32, 40):
        for x in range(60, 72):
            px[x, y] = (235, 180, 140)
    for x in range(58, 74):
        px[x, 32] = (75, 30, 85)
    for x in range(62, 70):
        px[x, 37] = (45, 15, 20)
    for y in range(40, 66):
        for x in range(56, 76):
            px[x, y] = (90, 35, 100)
            if x == 56 or y == 40:
                px[x, y] = (150, 60, 165)
    for x in range(74, 86):
        px[x, 48] = (180, 130, 60)
    for y in range(42, 58):
        px[86, y] = (180, 130, 60)

    save_and_process(img, "soltys_raw", "soltys.png", ["SOLTYS"], (245, 215, 255), (20, 6, 30), (35, 12, 48))

# =========================================================================
# 19. SUPERTUX (blue/cyan)
# =========================================================================
def make_supertux():
    img = Image.new('RGB', (128, 128), (8, 22, 48))
    px = img.load()
    
    dither_rect(px, 0, 0, 128, 45, (8, 20, 55), (35, 105, 185), vertical=True)
    for x in range(0, 128):
        y_aurora = int(14 + 6 * math.sin(x * 0.08))
        if 0 <= y_aurora < 128:
            px[x, y_aurora] = (0, 255, 240)
            if y_aurora + 1 < 128:
                px[x, y_aurora + 1] = (40, 180, 220)
            if y_aurora - 1 >= 0:
                px[x, y_aurora - 1] = (120, 80, 240)

    # Snowy pine trees on left and right
    for tx, ty in [(15, 34), (112, 36)]:
        for dy in range(0, 18):
            w = int(dy * 0.45)
            for dx in range(-w, w + 1):
                if 0 <= tx + dx < 128 and 0 <= ty + dy < 128:
                    px[tx + dx, ty + dy] = (20, 85, 40)
                    if dy % 4 == 0:
                        px[tx + dx, ty + dy] = (245, 250, 255) # Snow dusted needles
                    elif dx == 0:
                        px[tx + dx, ty + dy] = (45, 125, 60)

    for y in range(35, 128):
        for x in range(0, 128):
            t = (y - 35) / 93.0
            px[x, y] = (int(160 + t * 70), int(210 + t * 40), 255)
            if (x + y) % 7 == 0:
                px[x, y] = (130, 190, 245)
            if (x * 3 + y * 5) % 19 == 0:
                px[x, y] = (70, 130, 210)
            if (x * 7 + y * 11) % 29 == 0:
                px[x, y] = (25, 45, 95) # Glacier crevasse
            if (x * 5 + y * 3) % 23 == 0:
                px[x, y] = (255, 255, 255) # Sparkling snow

    for y in range(32, 68):
        for x in range(52, 78):
            px[x, y] = (15, 25, 40)
            if 38 <= y <= 62 and 58 <= x <= 72:
                px[x, y] = (240, 245, 255)
    for x in range(62, 68):
        px[x, 42] = (255, 160, 20)
        px[x, 43] = (255, 210, 50)
    for x in range(54, 76):
        if (x + 68) % 3 == 0:
            px[x, 32] = (220, 30, 20)
            px[x, 33] = (150, 20, 12)
    dither_radial(px, 82, 50, 7, (220, 245, 255), (100, 180, 240))

    save_and_process(img, "supertux_raw", "supertux.png", ["SUPERTUX"], (210, 245, 255), (8, 14, 28), (10, 22, 45))

# =========================================================================
# 20. SUPERTUXKART (blue/cyan)
# =========================================================================
def make_supertuxkart():
    img = Image.new('RGB', (128, 128), (12, 28, 55))
    px = img.load()
    
    dither_rect(px, 0, 0, 128, 35, (15, 35, 80), (50, 130, 210), vertical=True)
    
    for y in range(30, 128):
        for x in range(0, 128):
            px[x, y] = (45, 50, 58)
            if x % 16 == 0:
                px[x, y] = (30, 35, 40)
            if (x == 20 or x == 108) and (y % 8 < 4):
                px[x, y] = (240, 30, 20)
            elif (x == 20 or x == 108):
                px[x, y] = (245, 245, 255)

    for y in range(44, 72):
        for x in range(40, 88):
            px[x, y] = (220, 30, 20)
            if x == 40 or y == 44:
                px[x, y] = (255, 90, 80)
            if 50 <= y <= 66 and 48 <= x <= 80:
                px[x, y] = (160, 20, 15)
    for y in range(48, 70):
        for x in range(34, 42):
            px[x, y] = (15, 18, 22)
        for x in range(86, 94):
            px[x, y] = (15, 18, 22)
    for y in range(36, 52):
        for x in range(56, 72):
            px[x, y] = (15, 25, 40)
            if 42 <= y <= 50 and 60 <= x <= 68:
                px[x, y] = (240, 245, 255)
    for x in range(62, 66):
        px[x, 44] = (255, 160, 20)

    save_and_process(img, "supertuxkart_raw", "supertuxkart.png", ["SUPERTUXKART"], (210, 245, 255), (8, 14, 28), (10, 22, 45))

# =========================================================================
# 21. TERMINAL VELOCITY (amber/orange)
# =========================================================================
def make_terminal_velocity():
    img = Image.new('RGB', (128, 128), (25, 10, 4))
    px = img.load()
    
    dither_rect(px, 0, 0, 128, 50, (45, 14, 4), (240, 120, 18), vertical=True)
    dither_radial(px, 64, 18, 14, (255, 255, 230), (255, 160, 25))

    for y in range(18, 128):
        lx = int(48 - (y - 18) * 0.42)
        for x in range(0, lx):
            px[x, y] = (85, 38, 14)
            if y % 6 == 0 or (x + y) % 9 == 0:
                px[x, y] = (45, 18, 6)
        rx = int(80 + (y - 18) * 0.42)
        for x in range(rx, 128):
            px[x, y] = (70, 30, 10)
            if y % 6 == 0 or (x + y) % 9 == 0:
                px[x, y] = (35, 14, 4)

    for y in range(35, 68):
        span = int((y - 35) * 0.75)
        for x in range(63 - span, 64 + span):
            if 0 <= x < 128:
                px[x, y] = (65, 75, 90)
                if x == 63 - span or x == 63 + span:
                    px[x, y] = (150, 170, 200)
    for y in range(28, 60):
        for x in range(60, 68):
            px[x, y] = (85, 95, 115)
            if 34 <= y <= 44:
                px[x, y] = (0, 240, 255)
    for y in range(66, 76):
        px[62, y] = (255, 160, 20)
        px[65, y] = (255, 160, 20)

    save_and_process(img, "terminal_velocity_raw", "terminal-velocity-shareware.png", ["TERMINAL", "VELOCITY"], (255, 225, 75), (25, 8, 4), (35, 18, 8))

# =========================================================================
# 22. THE BATTLE FOR WESNOTH (blue/cyan)
# =========================================================================
def make_the_battle_for_wesnoth():
    img = Image.new('RGB', (128, 128), (8, 18, 42))
    px = img.load()
    
    dither_rect(px, 0, 0, 128, 45, (8, 16, 48), (25, 65, 135), vertical=True)
    dither_radial(px, 105, 18, 12, (255, 255, 255), (100, 160, 230))
    px[105, 18] = (255, 255, 255)

    # Distant mountain silhouettes
    for x in range(0, 128):
        my = int(28 + 8 * math.sin(x * 0.05 + 1.2))
        for y in range(my, 45):
            px[x, y] = (30, 50, 95)

    for y in range(25, 55):
        for x in range(65, 120):
            px[x, y] = (65, 95, 145)
            if y % 6 == 0 or x % 8 == 0:
                px[x, y] = (35, 55, 85)
            if y == 25 and x % 6 < 3:
                px[x, y] = (100, 140, 200) # Castle battlement

    for y in range(35, 128):
        for x in range(0, 128):
            px[x, y] = (18, 55, 32)
            if (x + y * 2) % 5 == 0:
                px[x, y] = (35, 95, 50)
            if (x * 7 + y * 13) % 19 == 0:
                px[x, y] = (12, 38, 20)
            if (x * 3 + y * 11) % 23 == 0:
                px[x, y] = (120, 95, 50) # Dirt path
            if (x * 5 + y * 17) % 31 == 0:
                px[x, y] = (65, 135, 75)

    # Armored Knight with Runic Sword
    for y in range(25, 68):
        for x in range(25, 42):
            px[x, y] = (130, 150, 180)
            if x == 25 or y == 25:
                px[x, y] = (200, 220, 250)
            if 38 <= y <= 58 and 30 <= x <= 38:
                px[x, y] = (60, 80, 110)
    # Knight Helmet & Plume
    for y in range(18, 26):
        px[33, y] = (210, 30, 20)
        px[34, y] = (255, 220, 40)
    # Runic Glowing Sword
    for y in range(14, 45):
        px[42, y] = (0, 240, 255)
        px[43, y] = (220, 250, 255)
    px[42, 45] = (255, 220, 40) # Gold crossguard
    px[43, 45] = (255, 220, 40)

    save_and_process(img, "wesnoth_raw", "the-battle-for-wesnoth.png", ["BATTLE FOR", "WESNOTH"], (210, 245, 255), (8, 14, 28), (10, 22, 45))

# =========================================================================
# 23. THE UR-QUAN MASTERS (blue/cyan)
# =========================================================================
def make_the_ur_quan_masters():
    img = Image.new('RGB', (128, 128), (4, 8, 22))
    px = img.load()
    
    dither_rect(px, 0, 0, 128, 128, (4, 8, 22), (18, 35, 75), vertical=True)
    dither_radial(px, 90, 40, 30, (40, 100, 180), (8, 16, 40))

    for y in range(28, 64):
        for x in range(18, 65):
            dist = math.hypot((x - 40) * 0.9, (y - 45) * 1.4)
            if dist <= 18:
                px[x, y] = (120, 140, 165)
                if x == 18 or y == 28:
                    px[x, y] = (210, 230, 255)
                if 42 <= y <= 48 and 32 <= x <= 48:
                    px[x, y] = (0, 240, 255)

    for y in range(32, 68):
        for x in range(75, 115):
            dist = math.hypot((x - 95) * 0.9, (y - 50) * 1.2)
            if dist <= 16:
                px[x, y] = (25, 110, 45)
                if 46 <= y <= 54 and 90 <= x <= 100:
                    px[x, y] = (220, 30, 20)

    save_and_process(img, "ur_quan_raw", "the-ur-quan-masters.png", ["THE UR-QUAN", "MASTERS"], (210, 245, 255), (8, 14, 28), (10, 22, 45))

# =========================================================================
# 24. TYRIAN 2000 (amber/orange)
# =========================================================================
def make_tyrian_2000():
    img = Image.new('RGB', (128, 128), (22, 8, 4))
    px = img.load()
    
    dither_rect(px, 0, 0, 128, 128, (22, 8, 4), (65, 25, 8), vertical=True)
    dither_radial(px, 35, 30, 16, (140, 65, 20), (35, 12, 4))
    dither_radial(px, 95, 45, 22, (160, 75, 25), (45, 16, 6))

    for y in range(25, 68):
        span = int((y - 25) * 0.8)
        for x in range(63 - span, 64 + span):
            if 0 <= x < 128:
                px[x, y] = (210, 150, 30)
                if x == 63 - span or x == 63 + span:
                    px[x, y] = (255, 220, 75)
    for y in range(18, 58):
        for x in range(60, 68):
            px[x, y] = (235, 175, 45)
            if 26 <= y <= 38:
                px[x, y] = (0, 240, 255)
    for x in [54, 73]:
        for y in range(0, 28):
            px[x, y] = (255, 240, 100)

    save_and_process(img, "tyrian_2000_raw", "tyrian-2000.png", ["TYRIAN 2000"], (255, 225, 75), (25, 8, 4), (35, 18, 8))

# =========================================================================
# 25. WARZONE 2100 (blue/cyan)
# =========================================================================
def make_warzone_2100():
    img = Image.new('RGB', (128, 128), (8, 20, 45))
    px = img.load()
    
    # 1. Twilight Cyber Sky & Radar Sweep (y=0..45)
    dither_rect(px, 0, 0, 128, 45, (8, 20, 45), (25, 75, 145), vertical=True)
    for x in range(0, 128):
        y_sweep = int(12 + 5 * math.sin(x * 0.07))
        if 0 <= y_sweep < 128:
            px[x, y_sweep] = (0, 255, 240) # Radar sweep arc
            if y_sweep - 1 >= 0:
                px[x, y_sweep - 1] = (120, 220, 255)
        # Horizon amber glow
        if (x + 35) % 4 == 0:
            px[x, 34] = (220, 140, 40)
            px[x, 35] = (180, 95, 25)

    # 2. Wasteland dunes & crater texture (y=30..128)
    for y in range(30, 128):
        for x in range(0, 128):
            px[x, y] = (18, 38, 65)
            if (x + y * 2) % 6 == 0:
                px[x, y] = (28, 58, 95)
            if (x * 7 + y * 13) % 23 == 0:
                px[x, y] = (110, 85, 45) # Wasteland dust
            if (x * 5 + y * 11) % 29 == 0:
                px[x, y] = (65, 45, 20) # Crater shadow
            if (x * 3 + y * 17) % 31 == 0:
                px[x, y] = (140, 180, 230)
            if (x * 11 + y * 7) % 37 == 0:
                px[x, y] = (30, 200, 160) # Mineral vein
            if (x * 13 + y * 19) % 41 == 0:
                px[x, y] = (185, 125, 60) # Red clay deposit

    # 3. Fortified Geodesic Radar Command Bunker (right, x=75..120, y=16..64)
    dither_radial(px, 95, 38, 20, (80, 180, 255), (25, 55, 95))
    for y in range(22, 54):
        for x in range(78, 112):
            if (x + y) % 4 == 0:
                px[x, y] = (0, 240, 255) # Glowing neon grid
            if (x * 3 + y * 5) % 11 == 0:
                px[x, y] = (200, 245, 255)
    # Red Warning Tower
    for y in range(14, 22):
        for x in range(93, 97):
            px[x, y] = (255, 40, 30)
    # Amber Command Terminal & Windows
    for y in range(38, 48):
        for x in range(86, 96):
            px[x, y] = (255, 180, 30) if (x + y) % 2 == 0 else (255, 230, 70)
    # Green Biosensor Grid
    for y in range(40, 50):
        for x in range(98, 108):
            px[x, y] = (40, 255, 80) if (x + y) % 2 == 0 else (15, 160, 50)

    # 4. Heavy Tracked Assault Hover Tank (left, x=16..72, y=44..74)
    for y in range(44, 68):
        for x in range(18, 68):
            px[x, y] = (70, 110, 160)
            if x == 18 or y == 44:
                px[x, y] = (130, 170, 220)
            if 52 <= y <= 60 and 26 <= x <= 46:
                px[x, y] = (240, 140, 25) # Hazard plate
    # Glowing Cyan Hover Skirt Cushion
    for y in range(62, 72):
        for x in range(20, 66):
            px[x, y] = (0, 255, 240) if (x + y) % 2 == 0 else (15, 25, 40)
    # Twin plasma cannons & muzzle charge
    for x in range(48, 78):
        px[x, 48] = (130, 170, 220)
        px[x, 52] = (130, 170, 220)
    for x in range(78, 86):
        px[x, 48] = (255, 240, 120)
        px[x, 52] = (255, 240, 120)
    px[86, 48] = (255, 255, 255)
    px[86, 52] = (255, 255, 255)

    save_and_process(img, "warzone_2100_raw", "warzone-2100.png", ["WARZONE 2100"], (210, 245, 255), (8, 14, 28), (10, 22, 45))

# =========================================================================
# 26. WIDELANDS (green/olive)
# =========================================================================
def make_widelands():
    img = Image.new('RGB', (128, 128), (12, 32, 20))
    px = img.load()
    
    dither_rect(px, 0, 0, 128, 35, (15, 45, 65), (255, 245, 200), vertical=True)
    
    # Distant mountain peaks
    for x in range(0, 128):
        my = int(22 + 6 * math.sin(x * 0.08))
        for y in range(my, 35):
            px[x, y] = (85, 120, 155)
            if y == my:
                px[x, y] = (140, 190, 230)

    # Rolling green meadows & stone quarry
    for y in range(25, 128):
        for x in range(0, 128):
            px[x, y] = (28, 85, 38)
            if (x + y * 2) % 5 == 0:
                px[x, y] = (45, 135, 55)
            if (x * 7 + y * 13) % 23 == 0:
                px[x, y] = (120, 95, 45)
            if (x * 3 + y * 11) % 19 == 0:
                px[x, y] = (15, 50, 22)
            if (x * 5 + y * 17) % 29 == 0:
                px[x, y] = (190, 160, 95) # Wheat field

    # Stream & Watermill
    for y in range(40, 74):
        for x in range(80, 110):
            if (x + y) % 3 == 0:
                px[x, y] = (40, 140, 210) # Water stream

    # Wooden building & stonemason
    for y in range(30, 64):
        for x in range(24, 60):
            px[x, y] = (120, 80, 40)
            if x == 24 or y == 30:
                px[x, y] = (180, 130, 70)
            if 48 <= y <= 60 and 42 <= x <= 56:
                px[x, y] = (160, 170, 185) # Cut stone block
    dither_radial(px, 70, 48, 16, (80, 55, 30), (35, 20, 10))

    # Stonemason carrying stone
    px[50, 44] = (235, 180, 135) # Head
    px[50, 45] = (180, 45, 30) # Shirt

    save_and_process(img, "widelands_raw", "widelands.png", ["WIDELANDS"], (225, 245, 215), (10, 25, 12), (18, 38, 22))

# =========================================================================
# 27. WOLFENSTEIN 3D (amber/orange)
# =========================================================================
def make_wolfenstein_3d():
    img = Image.new('RGB', (128, 128), (22, 10, 4))
    px = img.load()
    
    for y in range(0, 20):
        for x in range(0, 128):
            px[x, y] = (35, 16, 6)
            if (x + y) % 8 == 0 or x % 16 == 0:
                px[x, y] = (18, 8, 3)

    for y in range(12, 76):
        lx = int(42 - (y - 12) * 0.38)
        for x in range(0, lx):
            px[x, y] = (65, 30, 12)
            if y % 6 == 0 or x % 10 == 0:
                px[x, y] = (25, 10, 4)
            if (x + y * 2) % 7 == 0:
                px[x, y] = (95, 48, 18)
        rx = int(86 + (y - 12) * 0.38)
        for x in range(rx, 128):
            px[x, y] = (50, 22, 8)
            if y % 6 == 0 or x % 10 == 0:
                px[x, y] = (20, 8, 3)
            if (x + y * 2) % 7 == 0:
                px[x, y] = (80, 38, 14)

    for y in range(45, 76):
        t = (y - 45) / 31.0
        for x in range(0, 128):
            if int(42 - (y - 12) * 0.38) <= x <= int(86 + (y - 12) * 0.38):
                px[x, y] = (45 + int(t * 25), 20 + int(t * 12), 8 + int(t * 5))
                if y % 5 == 0:
                    px[x, y] = (25, 10, 4)
                if (x * 7 + y * 3) % 11 == 0:
                    px[x, y] = (95, 45, 16)

    for tx, ty in [(18, 28), (108, 28)]:
        for sy in range(ty + 2, ty + 12):
            px[tx, sy] = (20, 8, 3)
            px[tx + 1, sy] = (45, 20, 8)
        for fy in range(ty - 8, ty + 2):
            w = int(3 * (ty + 2 - fy) / 10.0)
            for fx in range(tx - w, tx + w + 1):
                px[fx, fy] = (255, 160, 25)
        px[tx, ty - 2] = (255, 240, 140)
        px[tx, ty - 4] = (255, 255, 220)

    for y in range(16, 64):
        for x in range(46, 83):
            px[x, y] = (55, 25, 10)
            if x % 6 == 0:
                px[x, y] = (25, 10, 4)
            if y in [20, 36, 52] or x in [46, 82, 64]:
                px[x, y] = (30, 14, 6)
                if y in [20, 36, 52] and (x in [50, 58, 70, 78]):
                    px[x, y] = (140, 75, 25)

    for y in range(36, 42):
        for x in range(32, 40):
            px[x, y] = (235, 175, 125)
    for y in range(34, 38):
        for x in range(30, 41):
            px[x, y] = (65, 55, 25)
    px[38, 38] = (35, 20, 10)
    for y in range(42, 66):
        for x in range(28, 44):
            px[x, y] = (90, 48, 18)
            if x == 28 or y == 42:
                px[x, y] = (150, 85, 35)
            if 54 <= y <= 58:
                px[x, y] = (40, 20, 8)
    for x in range(40, 60):
        for y in range(46, 49):
            px[x, y] = (60, 65, 75)
    px[44, 50] = (30, 32, 38)
    px[44, 51] = (30, 32, 38)

    for y in range(36, 54):
        for x in range(70, 76):
            px[x, y] = (20, 10, 5)
    px[73, 37] = (55, 60, 65)

    save_and_process(img, "wolfenstein_raw", "wolfenstein-3d-shareware.png", ["WOLFENSTEIN 3D"], (255, 225, 75), (25, 8, 4), (35, 18, 8))

# =========================================================================
# 28. XONOTIC (blue/cyan)
# =========================================================================
def make_xonotic():
    img = Image.new('RGB', (128, 128), (8, 16, 38))
    px = img.load()
    
    dither_rect(px, 0, 0, 128, 45, (6, 12, 32), (25, 70, 150), vertical=True)
    
    # Futuristic Arena Platform Grid (y=40..128)
    for y in range(40, 128):
        for x in range(15, 115):
            px[x, y] = (50, 75, 115)
            if x == 15 or x == 114 or y == 40:
                px[x, y] = (0, 255, 240)
            if (x + y) % 6 == 0:
                px[x, y] = (80, 120, 170)
            if (x * 7 + y * 13) % 19 == 0:
                px[x, y] = (140, 60, 255) # Violet plasma arc
            if (x * 3 + y * 17) % 23 == 0:
                px[x, y] = (20, 190, 255)
            if 48 <= y <= 54 and x % 12 < 6:
                px[x, y] = (255, 240, 80) # Hazard warning step

    # Swirling Violet / Blue Warp Portal (top right, x=80..120, y=8..42)
    dither_radial(px, 100, 24, 18, (180, 80, 255), (15, 30, 80))
    for y in range(12, 36):
        for x in range(88, 112):
            if (x + y) % 3 == 0:
                px[x, y] = (240, 200, 255)
            elif (x * y) % 5 == 0:
                px[x, y] = (0, 255, 240)

    # Armored Cyborg with Rocket Launcher (center left, x=35..75, y=24..68)
    for y in range(26, 65):
        for x in range(40, 68):
            px[x, y] = (120, 150, 190)
            if x == 40 or y == 26:
                px[x, y] = (200, 230, 255)
            if 36 <= y <= 50 and 46 <= x <= 62:
                px[x, y] = (0, 255, 240) # Glowing cyber core
            if 28 <= y <= 33 and 48 <= x <= 56:
                px[x, y] = (255, 30, 30) # Red cyborg optic visor
    # Heavy Rocket Launcher tube & exhaust
    for x in range(58, 92):
        for y in range(36, 44):
            px[x, y] = (80, 90, 105)
            if y == 36:
                px[x, y] = (160, 175, 195)
    # Exploding rocket trail
    for x in range(92, 128):
        for y in range(38, 44):
            px[x, y] = (255, 140, 20)
        px[x, 40] = (255, 240, 60)
        px[x, 41] = (255, 255, 255)
    px[90, 40] = (255, 255, 255)

    save_and_process(img, "xonotic_raw", "xonotic.png", ["XONOTIC"], (210, 245, 255), (8, 14, 28), (10, 22, 45))

def generate_all_illustrated():
    make_one_must_fall()
    make_openra()
    make_raptor()
    make_rise_of_the_triad()
    make_secret_agent()
    make_soltys()
    make_supertux()
    make_supertuxkart()
    make_terminal_velocity()
    make_the_battle_for_wesnoth()
    make_the_ur_quan_masters()
    make_tyrian_2000()
    make_warzone_2100()
    make_widelands()
    make_wolfenstein_3d()
    make_xonotic()

if __name__ == "__main__":
    generate_all_illustrated()
