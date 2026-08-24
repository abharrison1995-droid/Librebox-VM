import os
from PIL import Image

def run_all_builds():
    print("Rebuilding Batch 1 (1 to 4)...")
    import make_batch1
    make_batch1.make_beneath_a_steel_sky()
    make_batch1.make_bio_menace()
    make_batch1.make_blake_stone()
    make_batch1.make_cave_story()

    print("Rebuilding Batch 2 (5 to 10)...")
    import build_batch2
    build_batch2.main()

    print("Rebuilding Partial Batch 3 (11 to 13)...")
    import build_batch3_partial
    build_batch3_partial.main()

    print("Rebuilding Remaining (14 to 40)...")
    import build_all_remaining
    build_all_remaining.generate_all_remaining()

    print("All builds completed!")

if __name__ == "__main__":
    run_all_builds()
