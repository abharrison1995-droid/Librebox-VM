#!/usr/bin/env node
/**
 * Backfills download.sha256 for every catalog entry.
 *
 *   node catalog/hash.mjs           hash entries that don't have one
 *   node catalog/hash.mjs --force   re-hash everything
 *
 * Streams each download and hashes it without buffering the file, and writes
 * catalog.json back after every entry — this pulls several GB, so it needs to
 * survive being interrupted and resumed.
 */

import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const CATALOG_PATH = join(HERE, "catalog.json");

const force = process.argv.includes("--force");

const catalog = JSON.parse(readFileSync(CATALOG_PATH, "utf8"));
const todo = catalog.games.filter((g) => force || !g.download.sha256);

if (todo.length === 0) {
  console.log("Every entry already has a sha256.");
  process.exit(0);
}

const totalBytes = todo.reduce((n, g) => n + (g.download.size_bytes ?? 0), 0);
console.log(
  `Hashing ${todo.length} of ${catalog.games.length} entries ` +
    `(${(totalBytes / 1e9).toFixed(2)} GB)\n`
);

function save() {
  writeFileSync(CATALOG_PATH, JSON.stringify(catalog, null, 2) + "\n");
}

const failures = [];
let doneBytes = 0;

for (const [i, game] of todo.entries()) {
  const label = `[${i + 1}/${todo.length}] ${game.id}`;
  const expectedSize = game.download.size_bytes ?? 0;

  try {
    const res = await fetch(game.download.url, { redirect: "follow" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const hash = createHash("sha256");
    let seen = 0;
    for await (const chunk of res.body) {
      hash.update(chunk);
      seen += chunk.length;
    }
    const digest = hash.digest("hex");

    // A size that disagrees with the catalog means the upstream file changed;
    // record the new size rather than leaving a hash that pairs with a stale one.
    if (expectedSize && seen !== expectedSize) {
      console.log(`${label}  size changed ${expectedSize} -> ${seen}`);
      game.download.size_bytes = seen;
    }

    game.download.sha256 = digest;
    save();

    doneBytes += seen;
    const pct = totalBytes ? ((doneBytes / totalBytes) * 100).toFixed(1) : "?";
    console.log(`${label}  ${digest.slice(0, 16)}…  ${(seen / 1e6).toFixed(1)} MB  (${pct}%)`);
  } catch (e) {
    failures.push(`${game.id}: ${e.message}`);
    console.error(`${label}  FAILED: ${e.message}`);
  }
}

save();

const remaining = catalog.games.filter((g) => !g.download.sha256).length;
console.log(`\nDone. ${catalog.games.length - remaining}/${catalog.games.length} entries hashed.`);

if (failures.length) {
  console.error(`\n${failures.length} failure(s):`);
  for (const f of failures) console.error(`  x ${f}`);
  process.exit(1);
}
