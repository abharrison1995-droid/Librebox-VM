import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import make_batch1
import build_batch2
import build_batch3_partial
import build_all_remaining
import build_all_28_replacements

def run_all_builds():
    print("=== REBUILDING ALL 40 COVERS ===")
    
    print("1. Rebuilding 12 Keepers...")
    make_batch1.make_beneath_a_steel_sky()
    make_batch1.make_blake_stone()
    build_batch2.process_cover("crystal_caves_raw", "crystal-caves.png", ["CRYSTAL CAVES"], (255, 225, 75), (25, 12, 4), (35, 20, 8))
    build_batch2.process_cover("ddnet_raw", "ddnet.png", ["DDNET"], (210, 245, 255), (8, 16, 32), (10, 25, 50))
    build_batch2.process_cover("descent_raw", "descent-shareware.png", ["DESCENT"], (255, 215, 60), (25, 10, 4), (35, 18, 8))
    build_batch2.process_cover("devilutionx_raw", "devilutionx.png", ["DEVILUTIONX"], (200, 240, 255), (6, 12, 25), (8, 20, 40))
    build_batch2.process_cover("doom_raw", "doom-shareware.png", ["DOOM"], (255, 220, 50), (25, 6, 2), (40, 12, 4))
    build_batch3_partial.process_cover("drascula_raw", "drascula.png", ["DRASCULA", "THE VAMPIRE"], (240, 225, 255), (18, 8, 28), (30, 12, 40))
    build_batch3_partial.process_cover("endless_sky_raw", "endless-sky.png", ["ENDLESS SKY"], (210, 245, 255), (8, 16, 32), (10, 25, 50))
    build_all_remaining.make_epic_pinball()
    build_all_remaining.make_flight_amazon_queen()
    build_all_remaining.make_openttd()

    print("2. Rebuilding 28 Replacement Cards...")
    build_all_28_replacements.build_all_28()

    print("=== ALL 40 COVERS SUCCESSFULLY REBUILT ===")

if __name__ == "__main__":
    run_all_builds()
