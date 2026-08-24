import os
import glob
from PIL import Image
from generate_covers import draw_bitmap_text, darken_lower_band, quantify_palette, save_512

# Source illustrations are AI-generated and vendored into the repo, so this
# build reproduces anywhere. They are provenance as much as input: they show the
# art was originated, not filtered from a box scan.
SOURCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sources")

def get_latest_image(prefix):
    matches = sorted(glob.glob(os.path.join(SOURCE_DIR, f"{prefix}*.jpg")))
    if not matches:
        raise FileNotFoundError(f"No image matching {prefix} in {SOURCE_DIR}")
    return matches[-1]

def process_cover(prefix, filename, lines, text_color, shadow_color, tint_color, y_positions=None):
    src_file = get_latest_image(prefix)
    print(f"Processing {prefix} ({src_file}) -> {filename}")
    
    raw = Image.open(src_file).convert('RGB')
    img128 = raw.resize((128, 128), Image.Resampling.LANCZOS)
    darken_lower_band(img128, y_start=74, darken_factor=0.32, tint=tint_color)
    
    if y_positions is None:
        if len(lines) == 1:
            y_positions = [98]
        elif len(lines) == 2:
            y_positions = [88, 106]
            
    for line, y_pos in zip(lines, y_positions):
        draw_bitmap_text(img128, line, 64, y_pos, fg_color=text_color, bg_color=shadow_color)
        
    clean_128 = quantify_palette(img128, 32)
    img512 = clean_128.resize((512, 512), Image.Resampling.NEAREST)
    save_512(img512, filename)

def main():
    # 11. Drascula: The Vampire Strikes Back (violet/magenta)
    process_cover(
        prefix="drascula_raw",
        filename="drascula.png",
        lines=["DRASCULA", "THE VAMPIRE"],
        text_color=(255, 230, 250),
        shadow_color=(15, 5, 20),
        tint_color=(30, 10, 40)
    )
    
    # 12. Duke Nukem II is deliberately absent. The illustration produced for it
    # was recognisably Duke himself — flat-top, shades, red tank top — and that
    # character is a live trademark, not a generic action hero. Librebox falls
    # back to a generated tile for that entry.

    # 13. Endless Sky (blue/cyan)
    process_cover(
        prefix="endless_sky_raw",
        filename="endless-sky.png",
        lines=["ENDLESS SKY"],
        text_color=(210, 245, 255),
        shadow_color=(6, 12, 28),
        tint_color=(10, 20, 45)
    )

if __name__ == "__main__":
    main()
