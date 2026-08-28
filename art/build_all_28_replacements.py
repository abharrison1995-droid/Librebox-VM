import os
import sys
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
COVERS_STATIC = os.path.join(ROOT, "static", "covers")
COVERS_ROOT = os.path.join(ROOT, "covers")

sys.path.insert(0, HERE)
from build_batch2 import process_cover
from build_illustrated_replacements import (
    make_one_must_fall,
    make_openra,
    make_raptor,
    make_rise_of_the_triad,
    make_secret_agent,
    make_soltys,
    make_supertux,
    make_supertuxkart,
    make_terminal_velocity,
    make_the_battle_for_wesnoth,
    make_the_ur_quan_masters,
    make_tyrian_2000,
    make_warzone_2100,
    make_widelands,
    make_wolfenstein_3d,
    make_xonotic
)

def build_all_28():
    print("=== BUILDING ALL 28 REPLACEMENT THUMBNAIL CARDS ===")
    
    # 1. AI-illustrated cards (12 cards)
    print("--- Processing 12 AI-Illustrated Source Cards ---")
    process_cover('bio_menace_raw', 'bio-menace.png', ['BIO MENACE'], (255, 225, 75), (25, 12, 4), (35, 20, 8))
    process_cover('cave_story_raw', 'cave-story.png', ['CAVE STORY'], (200, 245, 255), (8, 16, 32), (10, 25, 50))
    process_cover('commander_keen_raw', 'commander-keen-1.png', ['COMMANDER KEEN'], (255, 230, 80), (25, 10, 4), (35, 18, 8))
    process_cover('duke_nukem_2_raw', 'duke-nukem-2.png', ['DUKE NUKEM II'], (255, 220, 75), (25, 10, 4), (35, 18, 8))
    process_cover('freedoom_raw', 'freedoom.png', ['FREEDOOM', 'PHASE 1 & 2'], (210, 245, 255), (8, 14, 28), (10, 22, 45))
    process_cover('heretic_raw', 'heretic-shareware.png', ['HERETIC'], (255, 225, 75), (25, 8, 2), (35, 15, 6))
    process_cover('hocus_pocus_raw', 'hocus-pocus.png', ['HOCUS POCUS'], (255, 225, 75), (25, 10, 4), (35, 18, 8))
    process_cover('jazz_jackrabbit_raw', 'jazz-jackrabbit-shareware.png', ['JAZZ JACKRABBIT'], (255, 225, 75), (25, 10, 4), (35, 18, 8))
    process_cover('keen_dreams_raw', 'keen-dreams.png', ['KEEN DREAMS'], (255, 225, 75), (25, 10, 4), (35, 18, 8))
    process_cover('lure_of_the_temptress_raw', 'lure-of-the-temptress.png', ['LURE OF THE', 'TEMPTRESS'], (255, 235, 250), (15, 4, 20), (25, 8, 35))
    process_cover('major_stryker_raw', 'major-stryker.png', ['MAJOR STRYKER'], (255, 225, 75), (25, 10, 4), (35, 18, 8))
    process_cover('monster_bash_raw', 'monster-bash.png', ['MONSTER BASH'], (255, 225, 75), (25, 10, 4), (35, 18, 8))

    # 2. Illustrated Scene Cards (16 cards)
    print("--- Processing 16 Illustrated Scene Cards ---")
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

    # Sync to covers/ directory if it exists
    if os.path.exists(COVERS_ROOT):
        for f in os.listdir(COVERS_STATIC):
            if f.endswith('.png'):
                shutil.copy2(os.path.join(COVERS_STATIC, f), os.path.join(COVERS_ROOT, f))

    print("=== FINISHED BUILDING ALL 28 REPLACEMENTS ===")

if __name__ == "__main__":
    build_all_28()
