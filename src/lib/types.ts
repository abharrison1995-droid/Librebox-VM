/** Shared types mirroring the Rust structs in src-tauri/src/. */

/** A game in the user's library. Mirrors `db::Game`. */
export interface Game {
  id: string;
  title: string;
  year: number | null;
  publisher: string | null;
  platform: string;
  engine: string | null;
  source: string;
  install_path: string | null;
  cover_path: string | null;
  last_played: string | null;
  playtime_s: number;
  /** Set when the game came from the catalog; null for user-added games. */
  catalog_id: string | null;
  runtime: string | null;
  runtime_config: string | null;
}

export interface DownloadInfo {
  url: string;
  format: string | null;
  size_bytes: number | null;
  sha256: string | null;
}

/** An installable game in the catalog. Mirrors `catalog::CatalogGame`. */
export interface CatalogGame {
  id: string;
  title: string;
  year: number | null;
  developer: string | null;
  publisher: string | null;
  platform: string;
  runtime: Runtime;
  genres: string[];
  license: License;
  license_note: string | null;
  source_url: string | null;
  description: string | null;
  cover_url: string | null;
  download: DownloadInfo;
  runtime_config: unknown;
}

export interface CatalogFilter {
  platform?: string;
  runtime?: string;
  license?: string;
  search?: string;
}

export interface SyncResult {
  source: "remote" | "bundled";
  entry_count: number;
  synced_at: string;
  /** Why the remote copy was not used, when it wasn't. */
  fallback_reason: string | null;
}

export interface CatalogStatus {
  last_sync: string | null;
  source: string | null;
  entry_count: number;
}

export type InstallPhase = "downloading" | "verifying" | "extracting";

/** Payload of the `install:progress` event. */
export interface InstallProgress {
  catalog_id: string;
  phase: InstallPhase;
  downloaded: number;
  total: number | null;
}

export interface InstallDone {
  catalog_id: string;
  game_id: string;
}

export interface InstallFailed {
  catalog_id: string;
  error: string;
}

/** Formats the install pipeline can unpack. Anything else needs manual setup. */
export const INSTALLABLE_FORMATS = ["zip"] as const;

export function isInstallable(game: CatalogGame): boolean {
  return (
    isPlayable(game.runtime) &&
    !!game.download.format &&
    (INSTALLABLE_FORMATS as readonly string[]).includes(game.download.format)
  );
}

export type Runtime = "dosbox" | "scummvm" | "native" | "86box";
export type License = "freeware" | "shareware" | "open-source" | "public-domain";

/** Runtimes that can actually launch a game today. */
export const PLAYABLE_RUNTIMES: readonly Runtime[] = ["dosbox", "scummvm", "native"];

export function isPlayable(runtime: string): boolean {
  return (PLAYABLE_RUNTIMES as readonly string[]).includes(runtime);
}
