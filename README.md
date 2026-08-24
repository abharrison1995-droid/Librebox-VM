# Librebox

A retro PC gaming launcher with a curated catalog of games that are genuinely
free to download — freeware, open source, and publisher-released shareware.
Wrapped in a Windows XP Luna interface, because that is the era.

> **Status: pre-release.** Browsing, installing, and launching all work. It has
> not been packaged or tested outside development yet — see the
> [Roadmap](#roadmap).

## What works today

- **Curated catalog** — 40 hand-verified titles: DOOM, Wolfenstein 3D,
  Commander Keen, Tyrian 2000, Beneath a Steel Sky, OpenTTD, Cave Story and
  more. Every download URL is checked in CI before it ships.
- **One-click install** — streams the archive with progress, verifies it against
  a SHA-256 recorded in the catalog, and unpacks it. A failed or cancelled
  install leaves nothing behind.
- **Launching** — DOSBox Staging for DOS games, ScummVM for the adventures, and
  direct execution for native ports. The emulator is fetched automatically the
  first time you need it; there is nothing to install by hand.
- **Playtime tracking** — recorded when a game exits, along with last-played.
- **Bring your own games** — point Librebox at a folder you already have and it
  finds the program and launches it alongside everything else.
- **Browse and filter** — search by title, developer or publisher, and filter
  by platform, runtime, or licence.
- **Cover art** — original 32-colour pixel tiles, one per entry, bundled with the
  app so the grid is populated offline and on first run. None derives from
  published box art; see [`art/README.md`](art/README.md).
- **Licence transparency** — every entry states what makes it free and links to
  a page corroborating that. See [`catalog/README.md`](catalog/README.md).
- **Offline-capable** — the catalog is fetched at launch and cached locally, with
  a copy bundled into the app so it works on a fresh install with no network.
- **XP Luna interface** — custom title bar, tabbed navigation, and a taskbar that
  shows running games and active downloads.

## Roadmap

In rough order:

1. **Packaging** — a signed installer, and a first run verified on a machine
   that is not a development box.
2. **Content Security Policy** — `tauri.conf.json` still ships `"csp": null`.
   Turning it on needs checking against the built SvelteKit output and the
   remote cover images the catalog can reference.
3. **Per-game troubleshooting profiles** — the practical version of "drivers on
   demand": per-title sound card, CPU cycle, and aspect-ratio overrides editable
   from the UI, so a game that runs silently or at ludicrous speed can be fixed
   without hand-editing a config.
4. **Settings** — choosing where games install.
5. **Remaining cover art** — 38 of 40 entries have art. Two are deliberately
   without it, and roughly half of the rest are weaker, near-interchangeable
   compositions that deserve a second pass. See [`art/README.md`](art/README.md).
6. **VM sandbox (before 1.0)** — 86Box integration for Win9x-era titles, with
   guest driver management. The catalog schema already carries an `86box`
   runtime; such entries display as "Not yet playable" until this lands.

## Installers that need a hand

Three catalog entries (Battle for Wesnoth, Widelands, The Ur-Quan Masters) ship
as installer executables rather than archives, so they cannot be set up
automatically. They stay listed and say so.

## Technology

- **Frontend** — [SvelteKit](https://kit.svelte.dev/) 5 + TypeScript + [Vite](https://vitejs.dev/)
- **Backend** — [Tauri](https://tauri.app/) 2 with a Rust core and SQLite storage

## Development

Requires [Node.js](https://nodejs.org/) 18+ and
[Rust](https://www.rust-lang.org/tools/install).

```bash
npm install
```

```bash
npm run tauri dev
```

Other useful commands:

| Command | Purpose |
|---|---|
| `npm run check` | TypeScript and Svelte type checking |
| `npm run lint:catalog` | Validate `catalog.json` structure |
| `npm run lint:catalog:urls` | Also verify every download URL still resolves |
| `npm run hash:catalog` | Backfill missing SHA-256 hashes |
| `npm run build:site` | Build the public catalog page into `_site/` |
| `python art/rebuild_all_40.py` | Regenerate every cover into `static/covers/` |
| `cargo test` (in `src-tauri/`) | Rust tests |
| `cargo test -- --ignored` | Also run the network tests that really install a game |

The catalog URL can be overridden at build time with `LIBREBOX_CATALOG_URL`.

## Contributing a game

Read [`catalog/README.md`](catalog/README.md) for the inclusion criteria and
entry format, then open a pull request. Every entry needs a licence
justification and a working, durable download URL.

## Legal

Librebox lists **only** games that are lawfully free to redistribute: freeware,
open-source, public-domain, and shareware episodes still distributed by their
rights holders. It hosts no game files of its own — every download points at the
publisher's own infrastructure or the Internet Archive.

Cover art is original work, not box art. No tile derives from a published cover,
screenshot, or sprite, and none depicts a licensed character — a game being free
to redistribute says nothing about who owns its packaging, and a pixel filter is
not a licence. See [`art/README.md`](art/README.md).

If you hold rights to something listed here and want it removed, open an issue.
See [`catalog/README.md`](catalog/README.md#takedown).

## Licence

MIT — see [`LICENSE`](LICENSE). This covers the Librebox application only.
Catalogued games remain under their own licences, and the emulators Librebox
downloads (DOSBox Staging, ScummVM) are GPL-licensed by their own projects.
