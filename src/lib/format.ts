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

/** Stable per-title colour for the placeholder cover tile. */
export function generateColor(title: string): string {
  let hash = 0;
  for (let i = 0; i < title.length; i++) {
    hash = title.charCodeAt(i) + ((hash << 5) - hash);
  }
  return `hsl(${Math.abs(hash) % 360}, 45%, 45%)`;
}
