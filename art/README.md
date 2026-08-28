# Cover art

Generates the cover tiles in `static/covers/`, one per catalog entry, named for
its catalog id. Rebuild the whole set with:

```bash
python art/rebuild_all_40.py
```

The build is deterministic — a rebuild reproduces every existing tile
byte-for-byte — so a change to one cover shows up as exactly one changed file.

## Format

- **512×512 PNG**, authored at 128×128 and scaled 4× with nearest-neighbour, so
  every pixel is a hard 4×4 block.
- **32 colours maximum**, VGA-era palette.
- Full-bleed art with the title set over a darkened band of the artwork itself,
  in a bitmap face, legible at the ~150px the app's grid actually renders.
- Tinted by runtime so the grid has structure: DOS amber, ScummVM violet,
  native blue. This matches the generated fallback tile in `CoverTile.svelte`,
  so real and generated covers sit on the same shelf.

## Where the art comes from

Two kinds, both original:

- **Procedural** — drawn in code against `pixel_art_engine.py`.
- **Illustrated** — an AI-generated illustration in `sources/`, reduced to
  128×128 and quantised. `sources/` is committed deliberately: it is the
  provenance record showing the art was originated rather than filtered from a
  box scan.

## The rule

**No cover may derive from published box art, screenshots, or sprites, and none
may depict a recognisable licensed character.**

A game being free to redistribute says nothing about its packaging art, which is
almost always separately owned and still enforced. Pixelating a scan produces a
derivative work, not a clean one — a filter is not a licence.

What is fine to draw on: genre convention, era rendering technique, and the
game's actual subject matter as described in its catalog entry. A prospector in
a crystal mine is a scene; Mylo Steamwitz is a character.

**Two entries are deliberately without art.** Illustrations produced for
Commander Keen and Duke Nukem II depicted the characters themselves — the
helmet and pogo stick, the flat-top and shades — which are protected designs
however they are redrawn. Both were dropped rather than shipped, and the app
falls back to a generated tile for them. Replacements must not depict either
character.

## Checking the set

```bash
python art/audit.py
```

Runs two checks over the art region of every cover, above the title band.

**Too alike** - compares each cover against every other and flags pairs scoring
0.79 or above. Covers built from an illustration score at most 0.75 against each
other, so anything higher is a duplicated composition rather than a shared house
style.

**Flat** - flags any cover using fewer than 24 of its 32 colours. Every cover
built from an illustration uses 24 to 32; the ones that read as an empty
gradient use 9 to 19. Colour count is a usable stand-in for having real
materials, lighting and depth rather than a backdrop with a few shapes on it,
and unlike composition it can be measured.

Eight covers currently pass both. Four more are kept despite being flat, because
they are legible and unmistakably about their game - a train on a viaduct, a
pinball table, a plane over jungle.

This exists because "does it look like the same shelf?" is the one requirement
that cannot be checked per file. A tile can be well drawn, correctly sized and
on-palette and still be the fourth near-identical orange gradient in a row.

## Adding or replacing a cover

1. Add a `make_*` function, or an entry to `build_batch2.py` /
   `build_batch3_partial.py` if working from an illustration in `sources/`.
2. Call it from `rebuild_all_40.py`.
3. Run the rebuild, then check the tile at 150px, not at 512.
4. Set `cover_url` in `catalog.json` to
   `https://abharrison1995-droid.github.io/Librebox-VM/covers/<id>.png`.

`npm run lint:catalog` enforces step 4 in both directions: art present without a
`cover_url` fails, and a `cover_url` without committed art fails. That pairing
is what stops the published catalog pointing at images that were never
deployed.
