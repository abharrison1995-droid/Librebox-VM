import os
from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COVERS_DIR = os.path.join(REPO_ROOT, "static", "covers")
OUT_IMG = os.path.join(REPO_ROOT, "art", "full_catalog_grid.png")

# 40 games in catalog order
GAMES = [
    "beneath-a-steel-sky", "bio-menace", "blake-stone-shareware", "cave-story",
    "commander-keen-1", "crystal-caves", "ddnet", "descent-shareware",
    "devilutionx", "doom-shareware", "drascula", "duke-nukem-2",
    "endless-sky", "epic-pinball-shareware", "flight-of-the-amazon-queen", "freedoom",
    "heretic-shareware", "hocus-pocus", "jazz-jackrabbit-shareware", "keen-dreams",
    "lure-of-the-temptress", "major-stryker", "monster-bash", "one-must-fall-2097",
    "openra", "openttd", "raptor-call-of-the-shadows", "rise-of-the-triad-shareware",
    "secret-agent", "soltys", "supertux", "supertuxkart",
    "terminal-velocity-shareware", "the-battle-for-wesnoth", "the-ur-quan-masters", "tyrian-2000",
    "warzone-2100", "widelands", "wolfenstein-3d-shareware", "xonotic"
]

def make_grid():
    cols = 8
    rows = 5
    tile_size = 128
    grid_img = Image.new('RGB', (cols * tile_size, rows * tile_size), (10, 10, 15))
    
    for idx, gid in enumerate(GAMES):
        c = idx % cols
        r = idx // cols
        path = os.path.join(COVERS_DIR, f"{gid}.png")
        if os.path.exists(path):
            tile = Image.open(path).resize((tile_size, tile_size), Image.NEAREST)
            grid_img.paste(tile, (c * tile_size, r * tile_size))
        else:
            print(f"Missing: {gid}")
            
    grid_img.save(OUT_IMG)
    print(f"Full catalog grid saved to {OUT_IMG}")

if __name__ == "__main__":
    make_grid()
