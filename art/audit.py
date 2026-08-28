"""Reports covers that are too alike to tell apart on a shelf.

    python art/audit.py            report
    python art/audit.py --json     machine-readable, for building a work order

"Does this look like the same shelf?" is the one cover requirement that cannot
be checked per-file: a tile can be well drawn, correctly sized and on-palette
and still be the fourth near-identical orange gradient in a row. This compares
each cover against every other and flags the pairs a user could not distinguish.

Only the art above the title band is compared, and each tile is normalised for
brightness and contrast first, so the runtime tint does not by itself make two
covers look alike.
"""

import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
COVERS = os.path.join(ROOT, "static", "covers")
CATALOG = os.path.join(ROOT, "catalog", "catalog.json")

# Covers built from an illustration peak at 0.75 against each other. Anything
# above that is more like another cover than any two distinct illustrations are,
# which makes it a duplicate composition rather than a shared style.
TWIN = 0.79

TITLE_BAND_TOP = 76  # of 128; below this is title, not art

# Every cover built from an illustration uses 24 or more of its 32 colours in
# the art region; the ones that read as an empty gradient use 9 to 19. Colour
# count stands in for having real materials, lighting and depth rather than a
# backdrop with a few shapes on it, and unlike composition it is measurable.
FLAT = 24


def art_region(path):
    im = Image.open(path).convert("RGB").resize((128, 128), Image.NEAREST)
    return im.crop((0, 0, 128, TITLE_BAND_TOP))


def colours(art):
    a = np.asarray(art, dtype=np.uint8).reshape(-1, 3)
    return int(len(np.unique(a, axis=0)))


def features(art):
    v = np.asarray(art.resize((16, 10), Image.BOX), dtype=np.float32) / 255.0
    v = (v - v.mean()) / (v.std() + 1e-6)
    v = v.ravel()
    return v / np.linalg.norm(v)


def main():
    catalog = json.load(open(CATALOG, encoding="utf-8"))
    games = {g["id"]: g for g in catalog["games"]}

    ids, mats, palette = [], [], {}
    for gid in sorted(games):
        path = os.path.join(COVERS, gid + ".png")
        if os.path.exists(path):
            art = art_region(path)
            ids.append(gid)
            mats.append(features(art))
            palette[gid] = colours(art)

    missing = [g for g in sorted(games) if g not in ids]
    sim = np.stack(mats) @ np.stack(mats).T
    np.fill_diagonal(sim, -1.0)

    report = []
    for i, gid in enumerate(ids):
        j = int(sim[i].argmax())
        report.append({
            "id": gid,
            "title": games[gid]["title"],
            "nearest": ids[j],
            "similarity": round(float(sim[i][j]), 3),
            "twin": bool(sim[i][j] >= TWIN),
            "colours": palette[gid],
            "flat": bool(palette[gid] < FLAT),
        })
    report.sort(key=lambda r: -r["similarity"])

    if "--json" in sys.argv:
        json.dump({"twin_threshold": TWIN, "flat_threshold": FLAT,
                   "missing": missing, "covers": report}, sys.stdout, indent=2)
        return

    twins = [r for r in report if r["twin"]]
    flats = [r for r in report if r["flat"]]
    print(f"{len(ids)} covers, {len(missing)} missing, "
          f"{len(twins)} too alike (>= {TWIN}), "
          f"{len(flats)} flat (< {FLAT} colours)\n")
    print(f"{'sim':>5} {'col':>4}  {'cover':<32} nearest")
    for r in report:
        flags = ("!" if r["twin"] else " ") + ("f" if r["flat"] else " ")
        print(f"{r['similarity']:5.2f} {r['colours']:4d}{flags} "
              f"{r['id']:<32} {r['nearest']}")
    if missing:
        print("\nno art:", ", ".join(missing))


if __name__ == "__main__":
    main()
