<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import GameCard from "$lib/components/GameCard.svelte";
  import CoverTile from "$lib/components/CoverTile.svelte";
  import AddGameDialog from "$lib/components/AddGameDialog.svelte";
  import { platformLabel, formatPlaytime, sourceLabel } from "$lib/format";
  import { downloads } from "$lib/downloads.svelte";
  import { launcher } from "$lib/launcher.svelte";
  import type { Game } from "$lib/types";

  let games = $state<Game[]>([]);
  let selectedId = $state<string | null>(null);
  let loading = $state(true);
  let viewMode = $state<"grid" | "list">("grid");
  let busy = $state(false);
  let showAdd = $state(false);

  async function loadGames() {
    try {
      games = await invoke<Game[]>("list_games");
    } catch (e) {
      console.error("Failed to load games:", e);
    } finally {
      loading = false;
    }
  }

  // Re-runs when an install completes (so a game downloaded on the Catalog tab
  // appears here) and when a game exits (so its new playtime shows).
  $effect(() => {
    downloads.installed;
    launcher.running;
    loadGames();
  });

  let selectedGame = $derived(games.find((g) => g.id === selectedId) ?? null);

  async function uninstall(game: Game) {
    busy = true;
    try {
      await invoke("uninstall_game", { id: game.id });
      selectedId = null;
      await downloads.refreshInstalled();
      await loadGames();
    } catch (e) {
      console.error("Failed to uninstall:", e);
    } finally {
      busy = false;
    }
  }
</script>

<div class="library-page">
  <!-- Toolbar -->
  <div class="toolbar">
    <div class="toolbar-left">
      <span class="toolbar-title">Game Library</span>
      <span class="toolbar-count">{games.length} title{games.length !== 1 ? 's' : ''}</span>
    </div>
    <div class="toolbar-right">
      <button class="xp-button add-btn" onclick={() => (showAdd = true)}>
        + Add Game
      </button>
      <div class="view-toggle">
        <button
          class="toggle-btn"
          class:active={viewMode === "grid"}
          onclick={() => viewMode = "grid"}
          aria-label="Grid view"
        >
          <svg width="14" height="14" viewBox="0 0 14 14">
            <rect x="1" y="1" width="5" height="5" fill="currentColor"/>
            <rect x="8" y="1" width="5" height="5" fill="currentColor"/>
            <rect x="1" y="8" width="5" height="5" fill="currentColor"/>
            <rect x="8" y="8" width="5" height="5" fill="currentColor"/>
          </svg>
        </button>
        <button
          class="toggle-btn"
          class:active={viewMode === "list"}
          onclick={() => viewMode = "list"}
          aria-label="List view"
        >
          <svg width="14" height="14" viewBox="0 0 14 14">
            <rect x="1" y="1.5" width="12" height="2.5" fill="currentColor"/>
            <rect x="1" y="5.5" width="12" height="2.5" fill="currentColor"/>
            <rect x="1" y="9.5" width="12" height="2.5" fill="currentColor"/>
          </svg>
        </button>
      </div>
    </div>
  </div>

  <div class="library-body">
    <!-- Game grid/list -->
    <div class="game-area xp-panel-sunken">
      {#if loading}
        <div class="empty-state">Loading library...</div>
      {:else if games.length === 0}
        <div class="empty-state">
          <div class="empty-icon">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <rect x="6" y="10" width="36" height="28" rx="3" stroke="var(--luna-text-disabled)" stroke-width="2" fill="none"/>
              <path d="M6 16H42" stroke="var(--luna-text-disabled)" stroke-width="2"/>
              <circle cx="24" cy="29" r="5" stroke="var(--luna-text-disabled)" stroke-width="2" fill="none"/>
              <path d="M22 29L25 29M24 27L24 31" stroke="var(--luna-text-disabled)" stroke-width="1.5"/>
            </svg>
          </div>
          <p class="empty-title">Your library is empty</p>
          <p class="empty-hint">
            Browse the <a href="/catalog">free catalog</a>, or
            <button class="link" onclick={() => (showAdd = true)}>add a game you own</button>.
          </p>
        </div>
      {:else if viewMode === "grid"}
        <div class="game-grid">
          {#each games as game (game.id)}
            <GameCard
              title={game.title}
              year={game.year}
              platform={game.platform}
              runtime={game.runtime}
              coverPath={game.cover_path}
              selected={selectedId === game.id}
              onclick={() => selectedId = game.id}
            />
          {/each}
        </div>
      {:else}
        <div class="game-list">
          <div class="list-header">
            <span class="col-title">Title</span>
            <span class="col-platform">Platform</span>
            <span class="col-year">Year</span>
            <span class="col-playtime">Playtime</span>
          </div>
          {#each games as game (game.id)}
            <button
              class="list-row"
              class:selected={selectedId === game.id}
              onclick={() => selectedId = game.id}
              type="button"
            >
              <span class="col-title">{game.title}</span>
              <span class="col-platform">{platformLabel(game.platform)}</span>
              <span class="col-year">{game.year ?? "—"}</span>
              <span class="col-playtime">{formatPlaytime(game.playtime_s)}</span>
            </button>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Detail panel -->
    {#if selectedGame}
      <aside class="detail-panel">
        <div class="detail-cover">
          <CoverTile
            title={selectedGame.title}
            src={selectedGame.cover_path}
            runtime={selectedGame.runtime}
            letterSize={56}
          />
        </div>
        <h2 class="detail-title">{selectedGame.title}</h2>
        <div class="detail-meta">
          {#if selectedGame.publisher}
            <div class="meta-row">
              <span class="meta-label">Publisher</span>
              <span class="meta-value">{selectedGame.publisher}</span>
            </div>
          {/if}
          <div class="meta-row">
            <span class="meta-label">Platform</span>
            <span class="meta-value">{platformLabel(selectedGame.platform)}</span>
          </div>
          {#if selectedGame.year}
            <div class="meta-row">
              <span class="meta-label">Year</span>
              <span class="meta-value">{selectedGame.year}</span>
            </div>
          {/if}
          <div class="meta-row">
            <span class="meta-label">Playtime</span>
            <span class="meta-value">{formatPlaytime(selectedGame.playtime_s)}</span>
          </div>
          <div class="meta-row">
            <span class="meta-label">Source</span>
            <span class="meta-value">{sourceLabel(selectedGame.source)}</span>
          </div>
        </div>
        {#if !selectedGame.install_path}
          <button class="launch-btn xp-button" disabled title="This game has no files on disk">
            Not installed
          </button>
        {:else if !selectedGame.runtime_config}
          <!-- Added with a folder but no program name, so there is nothing to run. -->
          <button class="launch-btn xp-button" disabled>No program set</button>
          <p class="launch-hint">Re-add this game with a program name to launch it.</p>
        {:else if launcher.isRunning(selectedGame.id)}
          <button class="launch-btn xp-button" disabled>Running…</button>
          <p class="launch-hint">Close the game window to return.</p>
        {:else}
          <button
            class="launch-btn xp-button"
            disabled={launcher.isStarting(selectedGame.id)}
            onclick={() => launcher.launch(selectedGame!.id)}
          >
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M2 1L10 6L2 11V1Z" fill="var(--luna-start-bg)"/>
            </svg>
            {launcher.isStarting(selectedGame.id) ? "Starting…" : "Launch Game"}
          </button>
          {#if launcher.runtimeFetch && launcher.isStarting(selectedGame.id)}
            <p class="launch-hint">
              Getting {launcher.runtimeFetch.name}
              {#if launcher.runtimeFetch.total}
                — {Math.round((launcher.runtimeFetch.downloaded / launcher.runtimeFetch.total) * 100)}%
              {/if}
              <br />First time only.
            </p>
          {/if}
        {/if}

        {#if launcher.errors[selectedGame.id]}
          <p class="launch-error" role="alert">
            {launcher.errors[selectedGame.id]}
            <button class="dismiss" onclick={() => launcher.dismissError(selectedGame!.id)}>
              Dismiss
            </button>
          </p>
        {/if}

        {#if selectedGame.install_path}
          <button
            class="xp-button uninstall-btn"
            disabled={busy || launcher.isRunning(selectedGame.id)}
            onclick={() => uninstall(selectedGame!)}
          >
            {busy ? "Removing…" : selectedGame.source === "byo" ? "Remove from Library" : "Uninstall"}
          </button>
        {/if}
      </aside>
    {/if}
  </div>
</div>

{#if showAdd}
  <AddGameDialog
    onclose={() => (showAdd = false)}
    onadded={(game) => {
      showAdd = false;
      selectedId = game.id;
      loadGames();
    }}
  />
{/if}

<style>
  .library-page {
    display: flex;
    flex-direction: column;
    flex: 1;
    overflow: hidden;
  }

  /* Toolbar */
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 10px;
    background: var(--luna-panel-bg);
    border-bottom: 1px solid var(--luna-panel-border);
    flex-shrink: 0;
  }
  .toolbar-left {
    display: flex;
    align-items: baseline;
    gap: 8px;
  }
  .toolbar-title {
    font-size: 13px;
    font-weight: 700;
    color: var(--luna-text);
  }
  .toolbar-count {
    font-size: 11px;
    color: var(--luna-text-disabled);
  }
  .toolbar-right {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .view-toggle {
    display: flex;
    border: 1px solid var(--luna-panel-border);
    border-radius: 2px;
    overflow: hidden;
  }
  .toggle-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 22px;
    border: none;
    background: var(--luna-button-face);
    color: var(--luna-text-secondary);
    cursor: pointer;
    outline: none;
  }
  .toggle-btn:not(:last-child) {
    border-right: 1px solid var(--luna-panel-border);
  }
  .toggle-btn:hover {
    background: #E8E4D6;
  }
  .toggle-btn.active {
    background: var(--luna-selection);
    color: var(--luna-selection-text);
  }

  /* Library body */
  .library-body {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  /* Game area */
  .game-area {
    flex: 1;
    overflow-y: auto;
    margin: 6px;
    padding: 8px;
  }

  .game-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    align-content: flex-start;
  }

  /* List view */
  .game-list {
    display: flex;
    flex-direction: column;
  }
  .list-header {
    display: grid;
    grid-template-columns: 1fr 120px 60px 90px;
    gap: 8px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 600;
    color: var(--luna-text-secondary);
    border-bottom: 1px solid var(--luna-panel-border);
    background: var(--luna-panel-bg);
  }
  .list-row {
    display: grid;
    grid-template-columns: 1fr 120px 60px 90px;
    gap: 8px;
    padding: 3px 8px;
    font-family: var(--luna-font);
    font-size: 12px;
    text-align: left;
    background: none;
    border: none;
    border-bottom: 1px solid var(--luna-panel-border);
    cursor: pointer;
    color: var(--luna-text);
    outline: none;
  }
  .list-row:hover {
    background: #E8E4D6;
  }
  .list-row.selected {
    background: var(--luna-selection);
    color: var(--luna-selection-text);
  }

  /* Empty state */
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    padding: 40px;
    text-align: center;
    color: var(--luna-text-disabled);
  }
  .empty-icon { margin-bottom: 12px; }
  .empty-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--luna-text-secondary);
    margin-bottom: 4px;
  }
  .empty-hint {
    font-size: 12px;
    max-width: 280px;
    line-height: 1.5;
  }

  /* Detail panel */
  .detail-panel {
    width: 240px;
    flex-shrink: 0;
    background: var(--luna-panel-bg);
    border-left: 1px solid var(--luna-panel-border);
    padding: 12px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .detail-cover {
    width: 100%;
  }
  .detail-title {
    font-family: var(--luna-font-title);
    font-size: 16px;
    font-weight: 700;
    color: var(--luna-text);
    line-height: 1.2;
  }
  .detail-meta {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .meta-row {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    padding: 2px 0;
    border-bottom: 1px dotted var(--luna-panel-border);
  }
  .meta-label {
    color: var(--luna-text-secondary);
  }
  .meta-value {
    font-weight: 500;
    text-align: right;
  }
  .launch-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    width: 100%;
    padding: 6px 16px;
    font-size: 13px;
    font-weight: 600;
    margin-top: 4px;
  }
  .add-btn {
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
  }
  .link {
    background: none;
    border: none;
    padding: 0;
    font: inherit;
    color: #0645ad;
    text-decoration: underline;
    cursor: pointer;
  }
  .uninstall-btn {
    width: 100%;
    padding: 4px 16px;
    font-size: 11px;
    margin-top: 6px;
  }
  .launch-hint {
    font-size: 10px;
    line-height: 1.4;
    color: var(--luna-text-disabled);
    text-align: center;
    margin: 4px 0 0;
  }
  .launch-error {
    font-size: 10px;
    line-height: 1.4;
    color: #7a1c1c;
    background: #fbe6e6;
    border: 1px solid #d48a8a;
    border-radius: 3px;
    padding: 5px 6px;
    margin: 6px 0 0;
  }
  .dismiss {
    display: block;
    margin-top: 4px;
    background: none;
    border: none;
    padding: 0;
    font-family: var(--luna-font);
    font-size: 10px;
    color: #7a1c1c;
    text-decoration: underline;
    cursor: pointer;
  }
</style>
