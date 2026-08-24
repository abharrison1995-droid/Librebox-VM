import os
import math
import numpy as np
from PIL import Image
from generate_covers import (FONT_7X9, BAYER_4X4, draw_bitmap_text, darken_lower_band,
                             quantify_palette, dither_lerp, save_512)

# Resolved from this file, not the working directory, so the build produces the
# same tree whether it is run from art/ or from the repo root.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO_ROOT, "static", "covers")


class PixelCanvas:
    def __init__(self, bg_color=(10, 8, 16)):
        self.img = Image.new('RGB', (128, 128), bg_color)
        self.pixels = self.img.load()

    def dither_gradient_v(self, y0, y1, c_top, c_bot, x0=0, x1=128):
        h = max(1, y1 - y0)
        for y in range(y0, y1):
            if y < 0 or y >= 128:
                continue
            t = (y - y0) / float(h)
            for x in range(x0, x1):
                if x < 0 or x >= 128:
                    continue
                self.pixels[x, y] = dither_lerp(c_top, c_bot, t, x, y)

    def draw_dithered_radial(self, cx, cy, radius, c_center, c_edge):
        for y in range(max(0, cy - radius), min(128, cy + radius + 1)):
            for x in range(max(0, cx - radius), min(128, cx + radius + 1)):
                dist = math.hypot(x - cx, y - cy)
                if dist <= radius:
                    t = dist / float(radius)
                    self.pixels[x, y] = dither_lerp(c_center, c_edge, t, x, y)

    def draw_sprite(self, x_pos, y_pos, sprite_lines, palette_map):
        """
        Renders a multi-color ASCII/character matrix sprite.
        palette_map is a dict mapping characters to RGB tuples.
        '.' or ' ' are transparent.
        """
        gh = len(sprite_lines)
        for r, line in enumerate(sprite_lines):
            py = y_pos + r
            if py < 0 or py >= 128:
                continue
            for c, ch in enumerate(line):
                px = x_pos + c
                if px < 0 or px >= 128:
                    continue
                if ch in palette_map:
                    self.pixels[px, py] = palette_map[ch]

    def finalize_cover(self, filename, lines, text_color, shadow_color, tint_color, y_positions=None):
        darken_lower_band(self.img, y_start=76, darken_factor=0.32, tint=tint_color)
        
        if y_positions is None:
            if len(lines) == 1:
                y_positions = [98]
            elif len(lines) == 2:
                y_positions = [88, 106]
                
        for line, y_pos in zip(lines, y_positions):
            draw_bitmap_text(self.img, line, 64, y_pos, fg_color=text_color, bg_color=shadow_color)
            
        clean_128 = quantify_palette(self.img, 32)
        img512 = clean_128.resize((512, 512), Image.Resampling.NEAREST)

        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, filename)
        img512.save(path, "PNG")
        print(f"Generated {filename} -> 512x512 PNG (<=32 colors)")

print("PixelCanvas engine ready.")
