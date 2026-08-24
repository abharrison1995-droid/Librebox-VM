/** Display helpers shared by the library and catalog views. */

const PLATFORM_LABELS: Record<string, string> = {
  dos: "DOS",
  win9x: "Windows 9x",
  winxp: "Windows XP",
  native: "Native",
};

/** Compact variants for the tight space on a game card. */
const PLATFORM_LABELS_SHORT: Record<string, string> = {
  dos: "DOS",
  win9x: "Win 9x",
  winxp: "Win XP",
  native: "Native",
};

const RUNTIME_LABELS: Record<string, string> = {
  dosbox: "DOSBox",
  scummvm: "ScummVM",
  native: "Native",
  "86box": "86Box VM",
};

const LICENSE_LABELS: Record<string, string> = {
  freeware: "Freeware",
  shareware: "Shareware",
  "open-source": "Open Source",
  "public-domain": "Public Domain",
};

export function platformLabel(p: string, short = false): string {
  const table = short ? PLATFORM_LABELS_SHORT : PLATFORM_LABELS;
  return table[p] ?? p.toUpperCase();
}

export function runtimeLabel(r: string): string {
  return RUNTIME_LABELS[r] ?? r;
}

export function licenseLabel(l: string): string {
  return LICENSE_LABELS[l] ?? l;
}

export function sourceLabel(s: string): string {
  return s === "catalog" ? "Catalog" : "Your Copy";
}

export function formatPlaytime(seconds: number): string {
  if (seconds < 60) return "Never played";
  const hours = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
}

export function formatSize(bytes: number | null): string {
  if (bytes == null || bytes <= 0) return "Unknown size";
  const units = ["B", "KB", "MB", "GB"];
  let value = bytes;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit++;
  }
  return `${value < 10 && unit > 0 ? value.toFixed(1) : Math.round(value)} ${units[unit]}`;
}

/** Renders the SQLite `datetime('now')` UTC timestamp in the user's locale. */
export function formatSyncTime(ts: string | null): string {
  if (!ts) return "never";
  const date = new Date(ts.includes("T") ? ts : ts.replace(" ", "T") + "Z");
  if (Number.isNaN(date.getTime())) return ts;
  return date.toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function hashString(value: string): number {
  let hash = 0;
  for (let i = 0; i < value.length; i++) {
    hash = value.charCodeAt(i) + ((hash << 5) - hash);
  }
  return Math.abs(hash);
}

/** Stable per-title colour. */
export function generateColor(title: string): string {
  return `hsl(${hashString(title) % 360}, 45%, 45%)`;
}

/** Words that shouldn't win the initial slot. */
const SKIP = new Set(["a", "an", "the", "of", "and", "for", "in", "on", "to"]);

/**
 * Up to two initials for a generated cover: "Beneath a Steel Sky" → "BS",
 * "DOOM (Shareware)" → "D".
 */
export function coverInitials(title: string): string {
  const words = title
    .replace(/\([^)]*\)/g, " ") // drop "(Shareware)" and friends
    .replace(/[^\p{L}\p{N}\s]/gu, " ")
    .split(/\s+/)
    .filter((w) => w && !SKIP.has(w.toLowerCase()));

  if (words.length === 0) return title.trim().charAt(0).toUpperCase() || "?";
  // A single word gives one big letter; multiple words give two.
  if (words.length === 1) return words[0].charAt(0).toUpperCase();
  return (words[0].charAt(0) + words[1].charAt(0)).toUpperCase();
}

export interface CoverArt {
  initials: string;
  from: string;
  to: string;
  accent: string;
}

/** Per-runtime accent, so a DOS game reads differently from a modern port. */
const RUNTIME_HUE: Record<string, number> = {
  dosbox: 28, // amber, phosphor-ish
  scummvm: 285, // violet
  native: 205, // blue
  "86box": 150, // green
};

/**
 * Deterministic artwork for a game with no cover image. Derived from the title
 * so it is stable across runs, and tinted by runtime so the grid has some
 * legible structure rather than looking random.
 */
export function coverArt(title: string, runtime?: string | null): CoverArt {
  const hash = hashString(title);
  const base = RUNTIME_HUE[runtime ?? ""] ?? hash % 360;
  // Spread titles within their runtime's family rather than across the wheel.
  const hue = (base + (hash % 40) - 20 + 360) % 360;
  return {
    initials: coverInitials(title),
    from: `hsl(${hue}, 42%, 38%)`,
    to: `hsl(${(hue + 24) % 360}, 48%, 18%)`,
    accent: `hsl(${hue}, 70%, 62%)`,
  };
}
