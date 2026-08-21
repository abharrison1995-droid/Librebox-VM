<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import GameCard from "$lib/components/GameCard.svelte";

  interface Game {
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
  }

  let games = $state<Game[]>([]);
  let selectedId = $state<string | null>(null);
  let loading = $state(true);
  let viewMode = $state<"grid" | "list">("grid");

  async function loadGames() {
    try {
      games = await invoke<Game[]>("list_games");
    } catch (e) {
      console.error("Failed to load games:", e);
    } finally {
      loading = false;
    }
  }

  $effect(() => {
    loadGames();
  });

  let selectedGame = $derived(games.find((g) => g.id === selectedId) ?? null);

  function platformLabel(p: string): string {
    switch (p) {
      case "dos": return "DOS";
      case "win9x": return "Windows 9x";
      case "winxp": return "Windows XP";
      default: return p;
    }
  }

  function formatPlaytime(seconds: number): string {
    if (seconds < 60) return "Never played";
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    if (hours > 0) return `${hours}h ${mins}m`;
    return `${mins}m`;
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
          <p class="empty-hint">Add games using the toolbar above, or browse the free catalog to get started.</p>
        </div>
      {:else if viewMode === "grid"}
        <div class="game-grid">
          {#each games as game (game.id)}
            <GameCard
              title={game.title}
              year={game.year}
              platform={game.platform}
              publisher={game.publisher}
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
        <div class="detail-cover" style="background-color: {selectedGame.cover_path ? 'transparent' : `hsl(${Math.abs([...selectedGame.title].reduce((h, c) => c.charCodeAt(0) + ((h << 5) - h), 0)) % 360}, 35%, 45%)`}">
          {#if selectedGame.cover_path}
            <img src={selectedGame.cover_path} alt="{selectedGame.title} cover" />
          {:else}
            <span class="detail-letter">{selectedGame.title.charAt(0).toUpperCase()}</span>
          {/if}
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
            <span class="meta-value">{selectedGame.source === 'catalog' ? 'Catalog' : 'Your Copy'}</span>
          </div>
        </div>
        <button class="launch-btn xp-button">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M2 1L10 6L2 11V1Z" fill="var(--luna-start-bg)"/>
          </svg>
          Launch Game
        </button>
      </aside>
    {/if}
  </div>
</div>

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
    aspect-ratio: 1 / 1;
    border-radius: 3px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(0, 0, 0, 0.1);
  }
  .detail-cover img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  .detail-letter {
    font-family: var(--luna-font-title);
    font-size: 64px;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.8);
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
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
</style>
