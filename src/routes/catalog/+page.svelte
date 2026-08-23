<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import { openUrl } from "@tauri-apps/plugin-opener";
  import CatalogCard from "$lib/components/CatalogCard.svelte";
  import CoverTile from "$lib/components/CoverTile.svelte";
  import {
    platformLabel,
    licenseLabel,
    runtimeLabel,
    formatSize,
    formatSyncTime,
  } from "$lib/format";
  import { isPlayable, type CatalogGame, type CatalogStatus, type SyncResult } from "$lib/types";

  let games = $state<CatalogGame[]>([]);
  let status = $state<CatalogStatus | null>(null);
  let selectedId = $state<string | null>(null);
  let loading = $state(true);
  let syncing = $state(false);
  let error = $state<string | null>(null);
  let viewMode = $state<"grid" | "list">("grid");

  let platform = $state("");
  let runtime = $state("");
  let license = $state("");
  let search = $state("");

  let selectedGame = $derived(games.find((g) => g.id === selectedId) ?? null);

  async function load() {
    try {
      games = await invoke<CatalogGame[]>("list_catalog", {
        platform: platform || null,
        runtime: runtime || null,
        license: license || null,
        search: search.trim() || null,
      });
      error = null;
    } catch (e) {
      error = String(e);
    } finally {
      loading = false;
    }
  }

  async function loadStatus() {
    try {
      status = await invoke<CatalogStatus>("catalog_status");
    } catch {
      // Status is decorative; a failure here should not blank the catalog.
    }
  }

  async function refresh() {
    syncing = true;
    try {
      const result = await invoke<SyncResult>("sync_catalog");
      if (result.fallback_reason) {
        error = `Showing the bundled catalog — could not reach the server (${result.fallback_reason})`;
      } else {
        error = null;
      }
      await Promise.all([load(), loadStatus()]);
    } catch (e) {
      error = String(e);
    } finally {
      syncing = false;
    }
  }

  // Re-query whenever a filter changes. Reading the filter state here is what
  // registers the dependency; the search box is debounced separately below.
  $effect(() => {
    platform;
    runtime;
    license;
    search;
    load();
  });

  $effect(() => {
    loadStatus();
  });

  let searchInput = $state("");
  let debounce: ReturnType<typeof setTimeout>;
  function onSearchInput(value: string) {
    searchInput = value;
    clearTimeout(debounce);
    debounce = setTimeout(() => (search = value), 200);
  }

  function clearFilters() {
    platform = "";
    runtime = "";
    license = "";
    search = "";
    searchInput = "";
  }

  let hasFilters = $derived(!!(platform || runtime || license || search.trim()));
</script>

<div class="catalog-page">
  <div class="toolbar">
    <div class="toolbar-left">
      <span class="toolbar-title">Catalog</span>
      <span class="toolbar-count">
        {games.length} title{games.length !== 1 ? "s" : ""}
        {#if hasFilters}<span class="filtered">filtered</span>{/if}
      </span>
    </div>
    <div class="toolbar-right">
      <button class="xp-button" onclick={refresh} disabled={syncing}>
        {syncing ? "Refreshing..." : "Refresh"}
      </button>
      <div class="view-toggle">
        <button
          class="toggle-btn"
          class:active={viewMode === "grid"}
          onclick={() => (viewMode = "grid")}
          aria-label="Grid view"
        >
          <svg width="14" height="14" viewBox="0 0 14 14">
            <rect x="1" y="1" width="5" height="5" fill="currentColor" />
            <rect x="8" y="1" width="5" height="5" fill="currentColor" />
            <rect x="1" y="8" width="5" height="5" fill="currentColor" />
            <rect x="8" y="8" width="5" height="5" fill="currentColor" />
          </svg>
        </button>
        <button
          class="toggle-btn"
          class:active={viewMode === "list"}
          onclick={() => (viewMode = "list")}
          aria-label="List view"
        >
          <svg width="14" height="14" viewBox="0 0 14 14">
            <rect x="1" y="1.5" width="12" height="2.5" fill="currentColor" />
            <rect x="1" y="5.5" width="12" height="2.5" fill="currentColor" />
            <rect x="1" y="9.5" width="12" height="2.5" fill="currentColor" />
          </svg>
        </button>
      </div>
    </div>
  </div>

  <div class="filter-bar">
    <input
      class="xp-input search"
      type="search"
      placeholder="Search titles, developers, publishers..."
      value={searchInput}
      oninput={(e) => onSearchInput(e.currentTarget.value)}
    />
    <label>
      Platform
      <select class="xp-input" bind:value={platform}>
        <option value="">All</option>
        <option value="dos">DOS</option>
        <option value="win9x">Windows 9x</option>
        <option value="winxp">Windows XP</option>
        <option value="native">Native</option>
      </select>
    </label>
    <label>
      Runtime
      <select class="xp-input" bind:value={runtime}>
        <option value="">All</option>
        <option value="dosbox">DOSBox</option>
        <option value="scummvm">ScummVM</option>
        <option value="native">Native</option>
        <option value="86box">86Box VM</option>
      </select>
    </label>
    <label>
      Licence
      <select class="xp-input" bind:value={license}>
        <option value="">All</option>
        <option value="freeware">Freeware</option>
        <option value="shareware">Shareware</option>
        <option value="open-source">Open Source</option>
        <option value="public-domain">Public Domain</option>
      </select>
    </label>
    {#if hasFilters}
      <button class="xp-button" onclick={clearFilters}>Clear</button>
    {/if}
  </div>

  {#if error}
    <div class="banner" role="status">{error}</div>
  {/if}

  <div class="catalog-body">
    <div class="game-area xp-panel-sunken">
      {#if loading}
        <div class="empty-state">Loading catalog...</div>
      {:else if games.length === 0}
        <div class="empty-state">
          <p class="empty-title">
            {hasFilters ? "No titles match those filters" : "Catalog is empty"}
          </p>
          <p class="empty-hint">
            {hasFilters
              ? "Try widening your search."
              : "Press Refresh to fetch the catalog."}
          </p>
        </div>
      {:else if viewMode === "grid"}
        <div class="game-grid">
          {#each games as game (game.id)}
            <CatalogCard
              {game}
              selected={selectedId === game.id}
              onclick={() => (selectedId = game.id)}
            />
          {/each}
        </div>
      {:else}
        <div class="list-header">
          <span>Title</span>
          <span>Platform</span>
          <span>Runtime</span>
          <span>Licence</span>
          <span>Size</span>
        </div>
        {#each games as game (game.id)}
          <button
            class="list-row"
            class:selected={selectedId === game.id}
            onclick={() => (selectedId = game.id)}
            type="button"
          >
            <span class="cell-title">{game.title}</span>
            <span>{platformLabel(game.platform)}</span>
            <span>{runtimeLabel(game.runtime)}</span>
            <span>{licenseLabel(game.license)}</span>
            <span>{formatSize(game.download.size_bytes)}</span>
          </button>
        {/each}
      {/if}
    </div>

    {#if selectedGame}
      <aside class="detail-panel xp-panel">
        <div class="detail-cover">
          <CoverTile title={selectedGame.title} src={selectedGame.cover_url} letterSize={56} />
        </div>
        <h2 class="detail-title">{selectedGame.title}</h2>

        {#if selectedGame.description}
          <p class="detail-description">{selectedGame.description}</p>
        {/if}

        <dl class="detail-meta">
          {#if selectedGame.developer}
            <dt>Developer</dt><dd>{selectedGame.developer}</dd>
          {/if}
          {#if selectedGame.publisher}
            <dt>Publisher</dt><dd>{selectedGame.publisher}</dd>
          {/if}
          {#if selectedGame.year}
            <dt>Year</dt><dd>{selectedGame.year}</dd>
          {/if}
          <dt>Platform</dt><dd>{platformLabel(selectedGame.platform)}</dd>
          <dt>Runtime</dt><dd>{runtimeLabel(selectedGame.runtime)}</dd>
          <dt>Licence</dt><dd>{licenseLabel(selectedGame.license)}</dd>
          <dt>Size</dt><dd>{formatSize(selectedGame.download.size_bytes)}</dd>
        </dl>

        {#if selectedGame.license_note}
          <p class="licence-note">{selectedGame.license_note}</p>
        {/if}

        {#if selectedGame.source_url}
          <button
            class="link-button"
            onclick={() => openUrl(selectedGame!.source_url!)}
            type="button"
          >
            View source page
          </button>
        {/if}

        <button class="xp-button install-button" disabled>
          {isPlayable(selectedGame.runtime) ? "Install (coming soon)" : "Not yet playable"}
        </button>
        <p class="install-hint">
          {isPlayable(selectedGame.runtime)
            ? "Downloads are not implemented yet."
            : `${runtimeLabel(selectedGame.runtime)} support is on the roadmap.`}
        </p>
      </aside>
    {/if}
  </div>

  <div class="status-bar">
    <span>
      Last synced {formatSyncTime(status?.last_sync ?? null)}
      {#if status?.source}
        <span class="source-tag" data-source={status.source}>{status.source}</span>
      {/if}
    </span>
    <span>{status?.entry_count ?? 0} in catalog</span>
  </div>
</div>

<style>
  .catalog-page {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-width: 0;
    padding: 8px;
    gap: 8px;
  }

  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
  }
  .toolbar-left {
    display: flex;
    align-items: baseline;
    gap: 8px;
  }
  .toolbar-title {
    font-size: 14px;
    font-weight: 700;
  }
  .toolbar-count {
    font-size: 11px;
    color: var(--luna-text-secondary);
  }
  .filtered {
    font-style: italic;
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
    border-radius: 3px;
    overflow: hidden;
  }
  .toggle-btn {
    display: flex;
    align-items: center;
    padding: 3px 6px;
    background: var(--luna-button-face);
    border: none;
    cursor: pointer;
    color: var(--luna-text-secondary);
  }
  .toggle-btn.active {
    background: var(--luna-selection);
    color: var(--luna-selection-text);
  }

  .filter-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    flex-shrink: 0;
    font-size: 11px;
  }
  .filter-bar label {
    display: flex;
    align-items: center;
    gap: 4px;
    color: var(--luna-text-secondary);
  }
  .filter-bar select {
    font-size: 11px;
    padding: 2px 4px;
  }
  .search {
    flex: 1;
    min-width: 180px;
    font-size: 11px;
    padding: 3px 6px;
  }

  .banner {
    flex-shrink: 0;
    padding: 5px 8px;
    font-size: 11px;
    background: #fdf1dc;
    border: 1px solid #d4a544;
    border-radius: 3px;
    color: #7a5411;
  }

  .catalog-body {
    display: flex;
    gap: 8px;
    flex: 1;
    min-height: 0;
  }
  .game-area {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
    min-width: 0;
  }
  .game-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-content: flex-start;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 4px;
    color: var(--luna-text-secondary);
    font-size: 12px;
  }
  .empty-title {
    font-weight: 600;
  }
  .empty-hint {
    font-size: 11px;
    color: var(--luna-text-disabled);
  }

  .list-header,
  .list-row {
    display: grid;
    grid-template-columns: 1fr 110px 90px 110px 90px;
    gap: 8px;
    align-items: center;
    padding: 4px 6px;
    font-size: 11px;
    text-align: left;
  }
  .list-header {
    font-weight: 700;
    border-bottom: 1px solid var(--luna-panel-border);
    color: var(--luna-text-secondary);
  }
  .list-row {
    background: none;
    border: none;
    width: 100%;
    cursor: pointer;
    font-family: var(--luna-font);
    color: var(--luna-text);
  }
  .list-row:hover {
    background: #e8e4d6;
  }
  .list-row.selected {
    background: var(--luna-selection);
    color: var(--luna-selection-text);
  }
  .cell-title {
    font-weight: 600;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .detail-panel {
    width: 240px;
    flex-shrink: 0;
    padding: 10px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .detail-cover {
    width: 120px;
    align-self: center;
  }
  .detail-title {
    font-size: 13px;
    font-weight: 700;
    text-align: center;
    margin: 0;
  }
  .detail-description {
    font-size: 11px;
    color: var(--luna-text-secondary);
    margin: 0;
    line-height: 1.4;
  }

  .detail-meta {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 2px 8px;
    font-size: 11px;
    margin: 0;
  }
  .detail-meta dt {
    color: var(--luna-text-secondary);
  }
  .detail-meta dd {
    margin: 0;
    text-align: right;
  }

  .licence-note {
    font-size: 10px;
    line-height: 1.4;
    color: var(--luna-text-secondary);
    background: rgba(0, 0, 0, 0.04);
    border-left: 2px solid var(--luna-panel-border);
    padding: 5px 6px;
    margin: 0;
  }

  .link-button {
    background: none;
    border: none;
    padding: 0;
    font-family: var(--luna-font);
    font-size: 11px;
    color: #0645ad;
    text-decoration: underline;
    cursor: pointer;
    align-self: flex-start;
  }

  .install-button {
    margin-top: auto;
  }
  .install-hint {
    font-size: 10px;
    color: var(--luna-text-disabled);
    text-align: center;
    margin: 0;
  }

  .status-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
    font-size: 10px;
    color: var(--luna-text-secondary);
    border-top: 1px solid var(--luna-panel-border);
    padding-top: 4px;
  }
  .source-tag {
    font-family: var(--luna-font-mono);
    font-size: 9px;
    padding: 0 4px;
    border-radius: 2px;
    background: var(--luna-panel-border);
  }
  .source-tag[data-source="bundled"] {
    background: #fdf1dc;
    color: #7a5411;
  }
</style>
