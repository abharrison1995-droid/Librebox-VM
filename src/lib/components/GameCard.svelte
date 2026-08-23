<script lang="ts">
  import CoverTile from "./CoverTile.svelte";
  import { platformLabel } from "$lib/format";

  interface Props {
    title: string;
    year?: number | null;
    platform: string;
    coverPath?: string | null;
    selected?: boolean;
    ondblclick?: () => void;
    onclick?: () => void;
  }

  let { title, year, platform, coverPath, selected = false, ondblclick, onclick }: Props = $props();
</script>

<button
  class="game-card"
  class:selected
  {ondblclick}
  {onclick}
  type="button"
>
  <div class="cover-slot">
    <CoverTile {title} src={coverPath} />
  </div>
  <div class="meta">
    <span class="title">{title}</span>
    <span class="info">
      <span class="platform-badge">{platformLabel(platform, true)}</span>
      {#if year}
        <span class="year">{year}</span>
      {/if}
    </span>
  </div>
</button>

<style>
  .game-card {
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
  .game-card:hover {
    background: #E8E4D6;
    border-color: var(--luna-panel-border);
  }
  .game-card.selected {
    background: var(--luna-selection);
    border-color: var(--luna-selection);
    color: var(--luna-selection-text);
  }
  .game-card:focus-visible {
    outline: 1px dotted var(--luna-text);
    outline-offset: -2px;
  }
  .game-card.selected:focus-visible {
    outline-color: var(--luna-selection-text);
  }

  .cover-slot {
    margin-bottom: 6px;
  }

  .meta {
    display: flex;
    flex-direction: column;
    gap: 2px;
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
</style>
