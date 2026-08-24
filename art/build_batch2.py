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
    
    # 1. Downscale to native 128x128 pixel art resolution
    img128 = raw.resize((128, 128), Image.Resampling.LANCZOS)
    
    # 2. Darken lower 40% (y >= 74) while maintaining underlying artwork continuity
    darken_lower_band(img128, y_start=74, darken_factor=0.32, tint=tint_color)
    
    # 3. Draw clean bitmap title text in lower 40% band
    if y_positions is None:
        if len(lines) == 1:
            y_positions = [98]
        elif len(lines) == 2:
            y_positions = [88, 106]
            
    for line, y_pos in zip(lines, y_positions):
        draw_bitmap_text(img128, line, 64, y_pos, fg_color=text_color, bg_color=shadow_color)
        
    # 4. Strict 32 color VGA palette quantization (preserving crisp pixel art)
    clean_128 = quantify_palette(img128, 32)
    
    # 5. Exact 4x nearest-neighbor upscale to 512x512 PNG
    img512 = clean_128.resize((512, 512), Image.Resampling.NEAREST)
    save_512(img512, filename)

def main():
    # 5. Commander Keen is deliberately absent. The illustration produced for it
    # depicted the character's signature helmet and pogo stick, which is his
    # protected design however it is redrawn. Librebox falls back to a generated
    # tile for that entry until a version exists that does not depict him.

    # 6. Crystal Caves (amber/orange)
    process_cover(
        prefix="crystal_caves_raw",
        filename="crystal-caves.png",
        lines=["CRYSTAL CAVES"],
        text_color=(255, 225, 75),
        shadow_color=(25, 12, 4),
        tint_color=(35, 20, 8)
    )
    
    # 7. DDNet (blue/cyan)
    process_cover(
        prefix="ddnet_raw",
        filename="ddnet.png",
        lines=["DDNET"],
        text_color=(210, 245, 255),
        shadow_color=(8, 16, 32),
        tint_color=(10, 25, 50)
    )
    
    # 8. Descent (amber/orange)
    process_cover(
        prefix="descent_raw",
        filename="descent-shareware.png",
        lines=["DESCENT"],
        text_color=(255, 215, 60),
        shadow_color=(25, 10, 4),
        tint_color=(35, 18, 8)
    )
    
    # 9. DevilutionX (blue/cyan)
    process_cover(
        prefix="devilutionx_raw",
        filename="devilutionx.png",
        lines=["DEVILUTIONX"],
        text_color=(200, 240, 255),
        shadow_color=(6, 12, 25),
        tint_color=(8, 20, 40)
    )
    
    # 10. DOOM (amber/orange)
    process_cover(
        prefix="doom_raw",
        filename="doom-shareware.png",
        lines=["DOOM"],
        text_color=(255, 220, 50),
        shadow_color=(25, 6, 2),
        tint_color=(40, 12, 4)
    )

if __name__ == "__main__":
    main()
