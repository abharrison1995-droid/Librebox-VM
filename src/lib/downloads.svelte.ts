/**
 * Shared install state.
 *
 * Owns the Tauri event listeners for the install pipeline and the set of
 * installed catalog ids. This lives outside any route on purpose: navigating
 * from Catalog to Library must not tear down a listener while a download is
 * still running.
 *
 * Import `downloads` anywhere; call `initDownloads()` once from the layout.
 */

import { invoke } from "@tauri-apps/api/core";
import { listen, type UnlistenFn } from "@tauri-apps/api/event";
import type {
  InstallDone,
  InstallFailed,
  InstallProgress,
  InstallPhase,
} from "./types";

export interface ActiveInstall {
  phase: InstallPhase;
  downloaded: number;
  total: number | null;
}

class Downloads {
  /** Catalog id → live progress, for installs currently running. */
  active = $state<Record<string, ActiveInstall>>({});
  /** Catalog ids the user already has on disk. */
  installed = $state<Set<string>>(new Set());
  /** Catalog id → message, for the most recent failure per game. */
  errors = $state<Record<string, string>>({});

  #started = false;
  #unlisten: UnlistenFn[] = [];

  isInstalling(catalogId: string): boolean {
    return catalogId in this.active;
  }

  isInstalled(catalogId: string): boolean {
    return this.installed.has(catalogId);
  }

  /** Fraction 0–1, or null when the total size is unknown. */
  fraction(catalogId: string): number | null {
    const job = this.active[catalogId];
    if (!job?.total) return null;
    return Math.min(1, job.downloaded / job.total);
  }

  async start(catalogId: string) {
    // Optimistically show the pending state so the button reacts immediately
    // rather than waiting for the first progress event.
    this.active = {
      ...this.active,
      [catalogId]: { phase: "downloading", downloaded: 0, total: null },
    };
    delete this.errors[catalogId];

    try {
      await invoke("install_game", { catalogId });
    } catch (e) {
      // The backend also emits install:failed; this catches the case where the
      // command itself rejects before any event is sent.
      this.#clear(catalogId);
      this.errors = { ...this.errors, [catalogId]: String(e) };
    }
  }

  async cancel(catalogId: string) {
    try {
      await invoke("cancel_install", { catalogId });
    } catch {
      // Job already finished between render and click; the state will settle
      // from the events either way.
    }
  }

  async refreshInstalled() {
    try {
      const ids = await invoke<string[]>("installed_ids");
      this.installed = new Set(ids);
    } catch (e) {
      console.error("Failed to load installed games:", e);
    }
  }

  dismissError(catalogId: string) {
    const { [catalogId]: _, ...rest } = this.errors;
    this.errors = rest;
  }

  #clear(catalogId: string) {
    const { [catalogId]: _, ...rest } = this.active;
    this.active = rest;
  }

  /** Idempotent: safe to call from a layout effect that may re-run. */
  async init() {
    if (this.#started) return;
    this.#started = true;

    this.#unlisten.push(
      await listen<InstallProgress>("install:progress", ({ payload }) => {
        this.active = {
          ...this.active,
          [payload.catalog_id]: {
            phase: payload.phase,
            downloaded: payload.downloaded,
            total: payload.total,
          },
        };
      })
    );

    this.#unlisten.push(
      await listen<InstallDone>("install:done", ({ payload }) => {
        this.#clear(payload.catalog_id);
        this.installed = new Set(this.installed).add(payload.catalog_id);
      })
    );

    this.#unlisten.push(
      await listen<InstallFailed>("install:failed", ({ payload }) => {
        this.#clear(payload.catalog_id);
        // "cancelled" is a user action, not an error worth surfacing.
        if (!/cancelled/i.test(payload.error)) {
          this.errors = { ...this.errors, [payload.catalog_id]: payload.error };
        }
      })
    );

    // Rehydrate: the window may have reloaded while installs were running.
    await Promise.all([this.refreshInstalled(), this.#rehydrateActive()]);
  }

  async #rehydrateActive() {
    try {
      const jobs = await invoke<(InstallProgress & { catalog_id: string })[]>(
        "active_installs"
      );
      const next: Record<string, ActiveInstall> = {};
      for (const j of jobs) {
        next[j.catalog_id] = {
          phase: j.phase,
          downloaded: j.downloaded,
          total: j.total,
        };
      }
      this.active = next;
    } catch (e) {
      console.error("Failed to read active installs:", e);
    }
  }

  destroy() {
    for (const off of this.#unlisten) off();
    this.#unlisten = [];
    this.#started = false;
  }
}

export const downloads = new Downloads();
