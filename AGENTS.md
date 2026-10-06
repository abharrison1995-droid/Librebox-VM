# Librebox — agent context (canonical; CLAUDE.md imports this)

Tauri 2 (Rust) + SvelteKit 5 desktop launcher for lawfully free retro PC games.
Windows is the only shipping target (catalog pins `dosbox.exe` / `scummvm.exe`).

## Map
- `src-tauri/src/lib.rs` — Tauri commands, app state, install orchestration (`run_install`), launch + playtime watcher
- `src-tauri/src/download.rs` — stream → `.part` → sha256 → zip extract (zip-slip safe) → atomic `promote`
- `src-tauri/src/launch.rs` — runtime fetch (`ensure_runtime`), DOSBox `.conf` generation, `plan_launch`
- `src-tauri/src/db.rs` — SQLite; `games` = user state, `catalog_games` = disposable cache, `catalog_meta` holds runtimes JSON
- `src-tauri/src/catalog.rs` — catalog types, remote fetch, bundled copy (`include_str!`)
- `src/lib/{downloads,launcher}.svelte.ts` — global event stores, initialised once in `+layout.svelte`
- `src/lib/types.ts` — must mirror the Rust structs; change both together
- `catalog/catalog.json` — source of truth for games and runtimes; rules in `catalog/README.md`

## Commands
- `npm run check` · `npm run build` · `npm run lint:catalog` (`:urls` before any catalog commit)
- `cd src-tauri && cargo test` (add `-- --ignored` for network installs)

## Invariants — do not break
- A failed/cancelled install leaves nothing registered or promoted; a failed reinstall leaves the previous install working.
- `catalog_games` never holds user state; `games` is never touched by a sync. A failed remote fetch never replaces the cached catalog.
- The remote catalog is untrusted until its signature verifies (signing lands in plan milestone M3). Checksums are never skipped.
- Librebox only deletes inside roots it created. BYO folders are never deleted.
- The frontend passes ids, never filesystem paths to run, open or delete.
- Behaviour changes ship with tests and with the doc lines they invalidate.
- Every catalog entry needs `license`, `license_note`, `source_url`, a zip (or explicit manual-install format) and a sha256.
- Covers: original art only — never derived from box art/screenshots/sprites, never a recognisable licensed character. See `art/README.md`.
- New Tauri commands need registering in `generate_handler!`; new window APIs need a permission in `capabilities/default.json`.

## Don't read unless the task is about them
`src-tauri/Cargo.lock`, `package-lock.json`, `src-tauri/icons/`, `art/sources/`, `static/covers/`, `screenshots/`, `build/`, `.svelte-kit/`, `src-tauri/target/`.
`catalog/catalog.json` is ~11k tokens — query it with `node -e` rather than reading it whole.
`art/*.py` is ~4k lines; only open the file `art/rebuild_all_40.py` routes to for the cover in question.

## Style
British English in UI and docs. Comments explain *why*, not what. Keep README status/roadmap in sync when behaviour changes.
