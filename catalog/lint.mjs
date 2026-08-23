#!/usr/bin/env node
/**
 * Validates catalog.json against the Librebox catalog schema.
 *
 *   node catalog/lint.mjs               structural validation only
 *   node catalog/lint.mjs --check-urls  additionally HEAD every download URL
 *   node catalog/lint.mjs --write-sizes as above, then write back real sizes
 *
 * Exits non-zero if any entry fails.
 */

import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const CATALOG_PATH = join(HERE, "catalog.json");

const SCHEMA_VERSION = 1;

const RUNTIMES = ["dosbox", "scummvm", "native", "86box"];
const PLATFORMS = ["dos", "win9x", "winxp", "native"];
const LICENSES = ["freeware", "shareware", "open-source", "public-domain"];
const FORMATS = ["zip", "7z", "exe", "tar.gz"];

const REQUIRED = ["id", "title", "platform", "runtime", "license", "license_note", "source_url", "download"];

const ID_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;

const errors = [];
const warnings = [];

function err(id, msg) {
  errors.push(`${id}: ${msg}`);
}
function warn(id, msg) {
  warnings.push(`${id}: ${msg}`);
}

function isHttpUrl(value) {
  try {
    const u = new URL(value);
    return u.protocol === "http:" || u.protocol === "https:";
  } catch {
    return false;
  }
}

// ---------------------------------------------------------------- load

let catalog;
try {
  catalog = JSON.parse(readFileSync(CATALOG_PATH, "utf8"));
} catch (e) {
  console.error(`Could not read or parse ${CATALOG_PATH}\n  ${e.message}`);
  process.exit(1);
}

if (catalog.schema_version !== SCHEMA_VERSION) {
  err("<file>", `schema_version must be ${SCHEMA_VERSION}, got ${catalog.schema_version}`);
}
if (!Array.isArray(catalog.games)) {
  console.error("catalog.games must be an array");
  process.exit(1);
}

// ------------------------------------------------------------- runtimes

// Emulators are fetched and verified by the same pipeline as games, so they
// are held to the same standard.
const RUNTIME_REQUIRED = ["id", "name", "version", "executable", "download"];

for (const [key, rt] of Object.entries(catalog.runtimes ?? {})) {
  const id = `runtime:${key}`;
  for (const field of RUNTIME_REQUIRED) {
    if (rt[field] === undefined || rt[field] === null || rt[field] === "") {
      err(id, `missing required field '${field}'`);
    }
  }
  if (rt.id && rt.id !== key) {
    err(id, `id '${rt.id}' does not match its key '${key}'`);
  }
  if (!RUNTIMES.includes(key)) {
    err(id, `'${key}' is not a known runtime`);
  }
  const dl = rt.download;
  if (dl && typeof dl === "object") {
    if (!dl.url || !isHttpUrl(dl.url)) err(id, `download.url is not a valid URL: ${dl.url}`);
    // Only zip can be unpacked automatically, and a runtime the user cannot
    // install automatically defeats the point.
    if (dl.format !== "zip") err(id, `download.format must be 'zip', got '${dl.format}'`);
    if (dl.sha256 == null) err(id, "no sha256 recorded — run `npm run hash:catalog`");
    else if (!/^[a-f0-9]{64}$/.test(dl.sha256)) err(id, "download.sha256 must be 64 lowercase hex chars");
  }
}

// Every runtime a game declares must actually be obtainable, or that game can
// never be launched.
const declaredRuntimes = new Set(Object.keys(catalog.runtimes ?? {}));
for (const rt of new Set(catalog.games.map((g) => g.runtime))) {
  // native needs no runtime; 86box is knowingly unimplemented.
  if (rt === "native" || rt === "86box") continue;
  if (!declaredRuntimes.has(rt)) {
    err("<file>", `games declare runtime '${rt}' but the catalog does not provide it`);
  }
}

// ---------------------------------------------------------- structural

const seen = new Set();

for (const [i, game] of catalog.games.entries()) {
  const id = game.id ?? `<index ${i}>`;

  for (const field of REQUIRED) {
    const v = game[field];
    if (v === undefined || v === null || v === "") {
      err(id, `missing required field '${field}'`);
    }
  }

  if (game.id) {
    if (!ID_RE.test(game.id)) {
      err(id, "id must be lowercase kebab-case");
    }
    if (seen.has(game.id)) {
      err(id, "duplicate id");
    }
    seen.add(game.id);
  }

  if (game.runtime && !RUNTIMES.includes(game.runtime)) {
    err(id, `runtime '${game.runtime}' not one of ${RUNTIMES.join(", ")}`);
  }
  if (game.platform && !PLATFORMS.includes(game.platform)) {
    err(id, `platform '${game.platform}' not one of ${PLATFORMS.join(", ")}`);
  }
  if (game.license && !LICENSES.includes(game.license)) {
    err(id, `license '${game.license}' not one of ${LICENSES.join(", ")}`);
  }

  if (game.year != null && (!Number.isInteger(game.year) || game.year < 1970 || game.year > 2100)) {
    err(id, `year '${game.year}' is not a plausible integer year`);
  }

  if (game.genres != null && !Array.isArray(game.genres)) {
    err(id, "genres must be an array");
  }

  if (game.source_url && !isHttpUrl(game.source_url)) {
    err(id, `source_url is not a valid http(s) URL: ${game.source_url}`);
  }
  if (game.cover_url && !isHttpUrl(game.cover_url)) {
    err(id, `cover_url is not a valid http(s) URL: ${game.cover_url}`);
  }

  const dl = game.download;
  if (dl && typeof dl === "object") {
    if (!dl.url || !isHttpUrl(dl.url)) {
      err(id, `download.url is not a valid http(s) URL: ${dl.url}`);
    }
    if (dl.format && !FORMATS.includes(dl.format)) {
      err(id, `download.format '${dl.format}' not one of ${FORMATS.join(", ")}`);
    }
    if (dl.size_bytes != null && (!Number.isInteger(dl.size_bytes) || dl.size_bytes <= 0)) {
      err(id, "download.size_bytes must be a positive integer");
    }
    if (dl.sha256 != null && !/^[a-f0-9]{64}$/.test(dl.sha256)) {
      err(id, "download.sha256 must be 64 lowercase hex chars");
    }
    // The install pipeline verifies against this, so it is no longer optional.
    // Populate with `npm run hash:catalog`.
    if (dl.sha256 == null) {
      err(id, "no sha256 recorded — run `npm run hash:catalog`");
    }
  } else if (game.download !== undefined) {
    err(id, "download must be an object");
  }

  if (game.runtime_config != null && typeof game.runtime_config !== "object") {
    err(id, "runtime_config must be an object");
  }

  // dosbox entries need an executable to launch
  if (game.runtime === "dosbox" && !game.runtime_config?.executable) {
    warn(id, "dosbox entry has no runtime_config.executable");
  }
}

// ------------------------------------------------------------ network

const checkUrls = process.argv.includes("--check-urls");
const writeSizes = process.argv.includes("--write-sizes");

if (checkUrls || writeSizes) {
  console.log(`Checking ${catalog.games.length} download URLs...\n`);

  const results = await Promise.all(
    catalog.games.map(async (game) => {
      const url = game.download?.url;
      if (!url) return { game, ok: false, reason: "no url" };
      try {
        // Some hosts reject HEAD; fall back to a ranged GET.
        let res = await fetch(url, { method: "HEAD", redirect: "follow" });
        if (!res.ok || res.headers.get("content-length") == null) {
          res = await fetch(url, { method: "GET", redirect: "follow", headers: { Range: "bytes=0-0" } });
        }
        if (!res.ok && res.status !== 206) {
          return { game, ok: false, reason: `HTTP ${res.status}` };
        }
        // A URL that serves HTML is a landing page, not a download.
        const ctype = res.headers.get("content-type") ?? "";
        if (ctype.includes("text/html")) {
          return { game, ok: false, reason: "serves HTML, not a file" };
        }
        const cr = res.headers.get("content-range");
        const size = cr
          ? Number(cr.split("/")[1])
          : Number(res.headers.get("content-length"));
        return { game, ok: true, size: Number.isFinite(size) && size > 0 ? size : null };
      } catch (e) {
        return { game, ok: false, reason: e.message };
      }
    })
  );

  for (const r of results) {
    if (!r.ok) {
      err(r.game.id, `download URL unreachable (${r.reason}): ${r.game.download?.url}`);
      continue;
    }
    const recorded = r.game.download.size_bytes;
    if (r.size == null) {
      warn(r.game.id, "server did not report a size");
    } else if (recorded == null) {
      if (writeSizes) r.game.download.size_bytes = r.size;
      else warn(r.game.id, `no size_bytes recorded (server says ${r.size})`);
    } else if (recorded !== r.size) {
      if (writeSizes) r.game.download.size_bytes = r.size;
      else err(r.game.id, `size_bytes ${recorded} but server says ${r.size}`);
    }
  }

  if (writeSizes) {
    writeFileSync(CATALOG_PATH, JSON.stringify(catalog, null, 2) + "\n");
    console.log("Wrote real sizes back to catalog.json\n");
  }
}

// ------------------------------------------------------------- report

const byRuntime = {};
for (const g of catalog.games) byRuntime[g.runtime] = (byRuntime[g.runtime] ?? 0) + 1;

console.log(`${catalog.games.length} entries: ` +
  Object.entries(byRuntime).map(([k, v]) => `${v} ${k}`).join(", "));

if (warnings.length) {
  console.log(`\n${warnings.length} warning(s):`);
  for (const w of warnings) console.log(`  ! ${w}`);
}

if (errors.length) {
  console.error(`\n${errors.length} error(s):`);
  for (const e of errors) console.error(`  x ${e}`);
  process.exit(1);
}

console.log("\nCatalog OK");
