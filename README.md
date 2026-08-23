# Librebox

A retro PC gaming launcher with a curated catalog of games that are genuinely
free to download — freeware, open source, and publisher-released shareware.
Wrapped in a Windows XP Luna interface, because that is the era.

> **Status: early development.** The catalog and library browser work. Actually
> downloading and launching games does not yet — see the [Roadmap](#roadmap).

## What works today

- **Curated catalog** — 40 hand-verified titles: DOOM, Wolfenstein 3D,
  Commander Keen, Tyrian 2000, Beneath a Steel Sky, OpenTTD, Cave Story and
  more. Every download URL is checked by CI-able tooling before it ships.
- **Browse and filter** — search by title, developer or publisher, and filter
  by platform, runtime, or licence.
- **Licence transparency** — every entry states what makes it free and links to
  a page corroborating that. See [`catalog/README.md`](catalog/README.md).
- **Offline-capable** — the catalog is fetched at launch and cached locally, with
  a copy bundled into the app so it works on a fresh install with no network.
- **Library** — tracks the games you own, kept strictly separate from the
  catalog so refreshing one never disturbs the other.
- **XP Luna interface** — custom title bar, taskbar, and tabbed navigation.

## Roadmap

In rough order:

1. **Downloads and installs** — fetch, checksum-verify, and extract catalog
   entries to disk with progress reporting.
2. **Launching** — DOSBox-Staging and ScummVM integration, plus direct execution
   for native games. Playtime and last-played tracking.
3. **Per-game troubleshooting profiles** — the practical version of "drivers on
   demand": per-title sound card, CPU cycle, and aspect-ratio overrides, so a
   game that runs silently or at ludicrous speed can be fixed from the UI.
4. **VM sandbox (before 1.0)** — 86Box integration for Win9x-era titles, with
   guest driver management. The catalog schema already carries an `86box`
   runtime; such entries display as "Not yet playable" until this lands.

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
| `cargo test` (in `src-tauri/`) | Rust unit and integration tests |

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

If you hold rights to something listed here and want it removed, open an issue.
See [`catalog/README.md`](catalog/README.md#takedown).

## Licence

MIT — see [`package.json`](package.json). This covers the Librebox application
only. Catalogued games remain under their own respective licences.
