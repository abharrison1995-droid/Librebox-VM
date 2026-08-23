<script lang="ts">
  import CoverTile from "./CoverTile.svelte";
  import { platformLabel, licenseLabel } from "$lib/format";
  import { isPlayable, type CatalogGame } from "$lib/types";

  interface Props {
    game: CatalogGame;
    selected?: boolean;
    onclick?: () => void;
  }

  let { game, selected = false, onclick }: Props = $props();

  let playable = $derived(isPlayable(game.runtime));
</script>

<button class="catalog-card" class:selected {onclick} type="button">
  <div class="cover-slot">
    <CoverTile title={game.title} src={game.cover_url} />
    {#if !playable}
      <span class="unplayable" title="This runtime is not implemented yet">Not yet playable</span>
    {/if}
  </div>
  <div class="meta">
    <span class="title">{game.title}</span>
    <span class="info">
      <span class="platform-badge">{platformLabel(game.platform, true)}</span>
      {#if game.year}<span class="year">{game.year}</span>{/if}
    </span>
    <span class="license-badge" data-license={game.license}>
      {licenseLabel(game.license)}
    </span>
  </div>
</button>

<style>
  .catalog-card {
    display: flex;
    flex-direction: column;
    width: 140px;
    background: var(--luna-button-face);
    border: 1px solid transparent;
    border-radius: 3px;
    padding: 6px;
    cursor: pointer;
    text-align: left;
    font-family: var(--luna-font);
    outline: none;
    transition: background 0.1s;
  }
  .catalog-card:hover {
    background: #e8e4d6;
    border-color: var(--luna-panel-border);
  }
  .catalog-card.selected {
    background: var(--luna-selection);
    border-color: var(--luna-selection);
    color: var(--luna-selection-text);
  }
  .catalog-card:focus-visible {
    outline: 1px dotted var(--luna-text);
    outline-offset: -2px;
  }
  .catalog-card.selected:focus-visible {
    outline-color: var(--luna-selection-text);
  }

  .cover-slot {
    position: relative;
    margin-bottom: 6px;
  }
  .unplayable {
    position: absolute;
    inset: auto 0 0 0;
    background: rgba(0, 0, 0, 0.72);
    color: #fff;
    font-size: 9px;
    font-weight: 600;
    text-align: center;
    padding: 2px 0;
  }

  .meta {
    display: flex;
    flex-direction: column;
    gap: 3px;
    min-width: 0;
  }
  .title {
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: inherit;
  }
  .info {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 10px;
    color: var(--luna-text-secondary);
  }
  .selected .info {
    color: rgba(255, 255, 255, 0.8);
  }

  .platform-badge {
    font-family: var(--luna-font-mono);
    font-size: 9px;
    font-weight: 600;
    padding: 1px 4px;
    border-radius: 2px;
    background: var(--luna-panel-border);
    color: var(--luna-text-secondary);
  }
  .selected .platform-badge {
    background: rgba(255, 255, 255, 0.25);
    color: var(--luna-selection-text);
  }
  .year {
    color: var(--luna-text-disabled);
  }
  .selected .year {
    color: rgba(255, 255, 255, 0.6);
  }

  .license-badge {
    align-self: flex-start;
    font-size: 9px;
    font-weight: 600;
    padding: 1px 5px;
    border-radius: 8px;
    border: 1px solid;
  }
  .license-badge[data-license="freeware"] {
    background: #e6f4e6;
    border-color: #7ab07a;
    color: #2d5f2d;
  }
  .license-badge[data-license="shareware"] {
    background: #fdf1dc;
    border-color: #d4a544;
    color: #7a5411;
  }
  .license-badge[data-license="open-source"] {
    background: #e2ecf9;
    border-color: #7da4d4;
    color: #1c4a80;
  }
  .license-badge[data-license="public-domain"] {
    background: #efe7f7;
    border-color: #a98cc4;
    color: #55307a;
  }
  /* Keep the badge readable against the blue selection fill. */
  .selected .license-badge {
    background: rgba(255, 255, 255, 0.9);
  }
</style>
