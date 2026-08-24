#!/usr/bin/env node
/**
 * Builds the GitHub Pages site into _site/.
 *
 *   _site/catalog.json  the file the desktop app fetches at launch
 *   _site/index.html    a browsable listing of the catalog
 *
 * Both are generated from catalog/catalog.json, so the app and the website can
 * never disagree about what is in the catalog.
 */

import { readFileSync, writeFileSync, mkdirSync, copyFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..");
const OUT = join(ROOT, "_site");

const REPO = "https://github.com/abharrison1995-droid/Librebox-VM";

const catalog = JSON.parse(readFileSync(join(HERE, "catalog.json"), "utf8"));

const RUNTIME_LABELS = {
  dosbox: "DOSBox",
  scummvm: "ScummVM",
  native: "Native",
  "86box": "86Box VM",
};
const PLATFORM_LABELS = {
  dos: "DOS",
  win9x: "Windows 9x",
  winxp: "Windows XP",
  native: "Native",
};
const LICENSE_LABELS = {
  freeware: "Freeware",
  shareware: "Shareware",
  "open-source": "Open Source",
  "public-domain": "Public Domain",
};

const esc = (s) =>
  String(s ?? "").replace(
    /[&<>"']/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]
  );

function formatSize(bytes) {
  if (!bytes) return "—";
  const units = ["B", "KB", "MB", "GB"];
  let v = bytes;
  let u = 0;
  while (v >= 1024 && u < units.length - 1) {
    v /= 1024;
    u++;
  }
  return `${v < 10 && u > 0 ? v.toFixed(1) : Math.round(v)} ${units[u]}`;
}

function hue(title) {
  let hash = 0;
  for (let i = 0; i < title.length; i++) hash = title.charCodeAt(i) + ((hash << 5) - hash);
  return Math.abs(hash) % 360;
}

const counts = catalog.games.reduce((acc, g) => {
  acc[g.runtime] = (acc[g.runtime] ?? 0) + 1;
  return acc;
}, {});

const cards = catalog.games
  .map((g) => {
    const meta = [PLATFORM_LABELS[g.platform] ?? g.platform, g.year].filter(Boolean).join(" · ");
    return `
      <article class="card"
        data-platform="${esc(g.platform)}"
        data-runtime="${esc(g.runtime)}"
        data-license="${esc(g.license)}"
        data-search="${esc(`${g.title} ${g.developer ?? ""} ${g.publisher ?? ""}`.toLowerCase())}">
        ${
          g.cover_url
            // Relative, so the page works on any host and in a local _site preview.
            ? `<img class="tile art" src="covers/${esc(g.id)}.png" alt="${esc(g.title)} cover" loading="lazy" width="512" height="512">`
            : `<div class="tile" style="--h:${hue(g.title)}">${esc(g.title.charAt(0).toUpperCase())}</div>`
        }
        <div class="body">
          <h3>${esc(g.title)}</h3>
          <p class="meta">${esc(meta)}</p>
          ${g.description ? `<p class="desc">${esc(g.description)}</p>` : ""}
          <p class="tags">
            <span class="tag lic" data-license="${esc(g.license)}">${esc(LICENSE_LABELS[g.license] ?? g.license)}</span>
            <span class="tag">${esc(RUNTIME_LABELS[g.runtime] ?? g.runtime)}</span>
            <span class="tag size">${esc(formatSize(g.download.size_bytes))}</span>
          </p>
          ${g.license_note ? `<p class="note">${esc(g.license_note)}</p>` : ""}
          ${g.source_url ? `<a class="src" href="${esc(g.source_url)}" rel="noopener">Source ↗</a>` : ""}
        </div>
      </article>`;
  })
  .join("\n");

const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Librebox Catalog</title>
<meta name="description" content="A curated catalog of ${catalog.games.length} classic PC games that are genuinely free to download — freeware, open source, and publisher-released shareware.">
<style>
  :root {
    --bg: #f4f2ea; --panel: #fff; --ink: #1d1c18; --muted: #6a675d;
    --line: #d9d5c6; --accent: #0058e6; --radius: 8px;
  }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#16150f; --panel:#201f18; --ink:#eceadf; --muted:#9c9a8c; --line:#33312a; --accent:#5b9cff; }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--ink);
    font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif;
  }
  .wrap { max-width: 1100px; margin: 0 auto; padding: 0 20px; }
  header { padding: 56px 0 32px; border-bottom: 1px solid var(--line); }
  h1 { margin: 0 0 8px; font-size: 40px; letter-spacing: -0.02em; }
  .lede { margin: 0 0 20px; font-size: 17px; color: var(--muted); max-width: 60ch; }
  .stats { display: flex; flex-wrap: wrap; gap: 20px; font-size: 14px; color: var(--muted); }
  .stats b { color: var(--ink); font-size: 20px; display: block; }
  .cta { display: inline-block; margin-top: 20px; padding: 9px 18px; border-radius: 6px;
         background: var(--accent); color: #fff; text-decoration: none; font-weight: 600; }

  .controls { display: flex; flex-wrap: wrap; gap: 10px; padding: 20px 0; position: sticky; top: 0;
              background: var(--bg); border-bottom: 1px solid var(--line); z-index: 2; }
  input, select {
    font: inherit; padding: 7px 10px; border: 1px solid var(--line);
    border-radius: 6px; background: var(--panel); color: var(--ink);
  }
  input { flex: 1; min-width: 200px; }

  .grid { display: grid; gap: 14px; padding: 22px 0 60px;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
  .card { display: flex; gap: 12px; padding: 12px; background: var(--panel);
          border: 1px solid var(--line); border-radius: var(--radius); }
  .card[hidden] { display: none; }
  .tile { flex: 0 0 56px; height: 56px; border-radius: 6px; display: grid; place-items: center;
          font-size: 26px; font-weight: 700; color: #fff;
          background: hsl(var(--h) 45% 45%); }
  /* The art is pixel art; let it stay blocky rather than being smoothed. */
  .tile.art { width: 56px; background: none; object-fit: cover;
              image-rendering: pixelated; }
  .body { min-width: 0; }
  h3 { margin: 0 0 2px; font-size: 15px; }
  .meta { margin: 0 0 6px; font-size: 12px; color: var(--muted); }
  .desc { margin: 0 0 8px; font-size: 13px; color: var(--muted); }
  .tags { display: flex; flex-wrap: wrap; gap: 5px; margin: 0 0 6px; }
  .tag { font-size: 11px; padding: 2px 7px; border-radius: 20px;
         border: 1px solid var(--line); color: var(--muted); }
  .lic[data-license="freeware"]     { background:#e6f4e6; border-color:#7ab07a; color:#2d5f2d; }
  .lic[data-license="shareware"]    { background:#fdf1dc; border-color:#d4a544; color:#7a5411; }
  .lic[data-license="open-source"]  { background:#e2ecf9; border-color:#7da4d4; color:#1c4a80; }
  .lic[data-license="public-domain"]{ background:#efe7f7; border-color:#a98cc4; color:#55307a; }
  .note { margin: 0 0 6px; font-size: 11px; color: var(--muted);
          border-left: 2px solid var(--line); padding-left: 7px; }
  .src { font-size: 12px; color: var(--accent); text-decoration: none; }
  .src:hover { text-decoration: underline; }

  .empty { padding: 40px; text-align: center; color: var(--muted); grid-column: 1 / -1; }
  footer { border-top: 1px solid var(--line); padding: 24px 0 48px;
           font-size: 13px; color: var(--muted); }
  footer a { color: var(--accent); }
</style>
</head>
<body>
<header>
  <div class="wrap">
    <h1>Librebox Catalog</h1>
    <p class="lede">
      A curated catalog of classic PC games that are genuinely free to download —
      freeware, open source, and shareware episodes still distributed by their
      rights holders. Every entry states what makes it free.
    </p>
    <div class="stats">
      <span><b>${catalog.games.length}</b> titles</span>
      <span><b>${counts.dosbox ?? 0}</b> DOS</span>
      <span><b>${counts.native ?? 0}</b> native</span>
      <span><b>${counts.scummvm ?? 0}</b> ScummVM</span>
    </div>
    <a class="cta" href="${REPO}">Get Librebox on GitHub</a>
  </div>
</header>

<div class="wrap">
  <div class="controls">
    <input id="q" type="search" placeholder="Search titles, developers, publishers…" aria-label="Search">
    <select id="platform" aria-label="Platform"><option value="">All platforms</option>
      ${Object.entries(PLATFORM_LABELS).map(([v, l]) => `<option value="${v}">${l}</option>`).join("")}
    </select>
    <select id="runtime" aria-label="Runtime"><option value="">All runtimes</option>
      ${Object.entries(RUNTIME_LABELS).map(([v, l]) => `<option value="${v}">${l}</option>`).join("")}
    </select>
    <select id="license" aria-label="Licence"><option value="">All licences</option>
      ${Object.entries(LICENSE_LABELS).map(([v, l]) => `<option value="${v}">${l}</option>`).join("")}
    </select>
  </div>

  <div class="grid" id="grid">
    ${cards}
    <p class="empty" id="empty" hidden>No titles match those filters.</p>
  </div>
</div>

<footer>
  <div class="wrap">
    <p>
      Machine-readable catalog: <a href="catalog.json">catalog.json</a> ·
      <a href="${REPO}/blob/master/catalog/README.md">Inclusion criteria &amp; takedown</a> ·
      <a href="${REPO}">Source</a>
    </p>
    <p>
      Librebox hosts no game files. Every download points at the publisher's own
      infrastructure or the Internet Archive. Catalogued games remain under their
      own licences.
    </p>
  </div>
</footer>

<script>
  const cards = [...document.querySelectorAll('.card')];
  const inputs = ['q', 'platform', 'runtime', 'license'].map((id) => document.getElementById(id));
  const empty = document.getElementById('empty');

  function apply() {
    const [q, platform, runtime, license] = inputs.map((el) => el.value.trim().toLowerCase());
    let shown = 0;
    for (const card of cards) {
      const ok =
        (!q || card.dataset.search.includes(q)) &&
        (!platform || card.dataset.platform === platform) &&
        (!runtime || card.dataset.runtime === runtime) &&
        (!license || card.dataset.license === license);
      card.hidden = !ok;
      if (ok) shown++;
    }
    empty.hidden = shown > 0;
  }

  for (const el of inputs) el.addEventListener('input', apply);
</script>
</body>
</html>
`;

mkdirSync(OUT, { recursive: true });
copyFileSync(join(HERE, "catalog.json"), join(OUT, "catalog.json"));
writeFileSync(join(OUT, "index.html"), html);

// Every cover_url points here, so publishing the catalog without the art would
// leave each entry pointing at a 404. The app has its own bundled copy, but the
// website and any other client rely on these.
const COVERS_SRC = join(ROOT, "static", "covers");
const COVERS_OUT = join(OUT, "covers");
mkdirSync(COVERS_OUT, { recursive: true });
let copied = 0;
for (const game of catalog.games) {
  if (!game.cover_url) continue;
  copyFileSync(join(COVERS_SRC, `${game.id}.png`), join(COVERS_OUT, `${game.id}.png`));
  copied += 1;
}
console.log(`Built _site/ with ${catalog.games.length} entries and ${copied} covers`);
