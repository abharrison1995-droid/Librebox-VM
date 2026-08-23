/**
 * Running-game state.
 *
 * Separate from the install pipeline in `downloads.svelte.ts`: that module is
 * about getting games onto disk, this one about running them. Both are
 * initialised from the layout so their listeners outlive any single route.
 */

import { invoke } from "@tauri-apps/api/core";
import { listen, type UnlistenFn } from "@tauri-apps/api/event";
import type { GameExited, RunningGame, RuntimeProgress } from "./types";

class Launcher {
  /** Game id → title, for games currently running. */
  running = $state<Record<string, string>>({});
  /** Set while an emulator is being fetched on first use. */
  runtimeFetch = $state<RuntimeProgress | null>(null);
  /** Game id → message for the most recent launch failure. */
  errors = $state<Record<string, string>>({});
  /** Games we have asked to start but which have not reported back yet. */
  starting = $state<Set<string>>(new Set());

  #started = false;
  #unlisten: UnlistenFn[] = [];

  isRunning(gameId: string): boolean {
    return gameId in this.running;
  }

  isStarting(gameId: string): boolean {
    return this.starting.has(gameId);
  }

  async launch(gameId: string) {
    this.starting = new Set(this.starting).add(gameId);
    this.dismissError(gameId);
    try {
      await invoke("launch_game", { id: gameId });
    } catch (e) {
      this.errors = { ...this.errors, [gameId]: String(e) };
    } finally {
      const next = new Set(this.starting);
      next.delete(gameId);
      this.starting = next;
      this.runtimeFetch = null;
    }
  }

  dismissError(gameId: string) {
    const { [gameId]: _, ...rest } = this.errors;
    this.errors = rest;
  }

  async init() {
    if (this.#started) return;
    this.#started = true;

    this.#unlisten.push(
      await listen<RunningGame>("game:launched", ({ payload }) => {
        this.running = { ...this.running, [payload.game_id]: payload.title };
        this.runtimeFetch = null;
      })
    );

    this.#unlisten.push(
      await listen<GameExited>("game:exited", ({ payload }) => {
        const { [payload.game_id]: _, ...rest } = this.running;
        this.running = rest;
      })
    );

    this.#unlisten.push(
      await listen<RuntimeProgress>("runtime:progress", ({ payload }) => {
        this.runtimeFetch = payload;
      })
    );

    this.#unlisten.push(
      await listen("runtime:ready", () => {
        this.runtimeFetch = null;
      })
    );

    await this.refresh();
  }

  /** Rehydrate after a window reload; games keep running regardless. */
  async refresh() {
    try {
      const games = await invoke<RunningGame[]>("running_games");
      const next: Record<string, string> = {};
      for (const g of games) next[g.game_id] = g.title;
      this.running = next;
    } catch (e) {
      console.error("Failed to read running games:", e);
    }
  }

  destroy() {
    for (const off of this.#unlisten) off();
    this.#unlisten = [];
    this.#started = false;
  }
}

export const launcher = new Launcher();
