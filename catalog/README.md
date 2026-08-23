# Librebox Catalog

`catalog.json` is the single source of truth for the games Librebox offers. The
desktop app ships with a bundled copy and fetches a newer one at launch, so
adding a game here reaches users without an app release.

## Inclusion criteria

A game may be listed **only** if it is lawfully free to redistribute. Every
entry must record which of these applies, in its `license` field:

| `license` | Meaning |
|---|---|
| `freeware` | The rights holder released the complete game at no cost (e.g. Cave Story, One Must Fall 2097). |
| `shareware` | The rights holder distributes a free episode or demo and permits redistribution (e.g. DOOM Episode 1, Wolfenstein 3D Episode 1). |
| `open-source` | Released under an OSI-approved licence (e.g. OpenTTD, SuperTuxKart). |
| `public-domain` | Copyright has expired or been waived. |

Three fields are **mandatory on every entry** and exist specifically so each
listing carries its own justification:

- `license` — the category above.
- `license_note` — one sentence naming *who* made it free and *what* is covered.
  "Episode 1 is freely redistributable shareware released by id Software" is
  adequate; "it's old" is not.
- `source_url` — a human-readable page corroborating that claim.

**Not acceptable:** full commercial games, cracked or patched binaries,
abandonware whose rights holder has not actually released it, ROMs of
copyrighted console titles, or any download whose provenance you cannot
establish. "It is widely available online" is not a licence.

Engines are welcome even when their game data is not (OpenXcom, DevilutionX).
Say so in `license_note` — the app will tell users what they must supply.

## Entry format

See the schema enforced by `lint.mjs`. Controlled vocabularies:

- `runtime` — `dosbox` | `scummvm` | `native` | `86box`
- `platform` — `dos` | `win9x` | `winxp` | `native`
- `license` — as above
- `download.format` — `zip` | `7z` | `exe` | `tar.gz`

`86box` entries are accepted and stored, but the VM runtime is not implemented
yet, so the app shows them as "Not yet playable".

`runtime_config` is a free-form object whose shape depends on `runtime`:

```jsonc
// dosbox
{ "executable": "DOOM.EXE", "cpu_cycles": "20000", "sound": "sb16", "aspect": true }
// scummvm
{ "game_id": "sky" }
// native
{ "executable": "openttd.exe" }
```

## Validating

```bash
npm run lint:catalog
```

Structural checks only — required fields, enum values, unique ids, URL syntax.

```bash
npm run lint:catalog:urls
```

Additionally fetches every `download.url` and fails on anything that 404s or
serves HTML instead of a file. **Run this before every commit that touches
`catalog.json`.** Upstream projects retag releases and delete old assets
constantly; a version-pinned GitHub URL that worked last month may be gone.

`node catalog/lint.mjs --write-sizes` refreshes `size_bytes` from what the
servers actually report.

### On `sha256`

Currently `null` for every entry. Hashes are only meaningful once the download
pipeline verifies them, and computing them means downloading ~2 GB. They must
be populated before that pipeline ships — the linter warns until they are.

## Adding a game

1. Confirm it meets the criteria above and find a durable direct download URL.
   Prefer the project's own release infrastructure or the Internet Archive over
   a third-party mirror.
2. Add the entry, sorted by title.
3. Run `npm run lint:catalog:urls` and confirm it passes.
4. Open a pull request quoting the evidence behind your `license_note`.

## Takedown

If you hold rights to something listed here and want it removed, open an issue
on the repository or contact the maintainer. Entries are removed on request
while the claim is reviewed — we would rather drop a game than argue about one.
