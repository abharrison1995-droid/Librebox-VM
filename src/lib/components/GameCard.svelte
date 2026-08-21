<script lang="ts">
  interface Props {
    title: string;
    year?: number | null;
    platform: string;
    publisher?: string | null;
    coverPath?: string | null;
    selected?: boolean;
    ondblclick?: () => void;
    onclick?: () => void;
  }

  let { title, year, platform, publisher, coverPath, selected = false, ondblclick, onclick }: Props = $props();

  function platformLabel(p: string): string {
    switch (p) {
      case "dos": return "DOS";
      case "win9x": return "Win 9x";
      case "winxp": return "Win XP";
      default: return p.toUpperCase();
    }
  }

  function generateColor(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const h = Math.abs(hash) % 360;
    return `hsl(${h}, 35%, 45%)`;
  }
</script>

<button
  class="game-card"
  class:selected
  {ondblclick}
  {onclick}
  type="button"
>
  <div class="cover" style="background-color: {coverPath ? 'transparent' : generateColor(title)}">
    {#if coverPath}
      <img src={coverPath} alt="{title} cover art" />
    {:else}
      <span class="cover-letter">{title.charAt(0).toUpperCase()}</span>
    {/if}
  </div>
  <div class="meta">
    <span class="title">{title}</span>
    <span class="info">
      <span class="platform-badge">{platformLabel(platform)}</span>
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

  .cover {
    width: 100%;
    aspect-ratio: 1 / 1;
    border-radius: 2px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(0, 0, 0, 0.1);
    margin-bottom: 6px;
  }
  .cover img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  .cover-letter {
    font-family: var(--luna-font-title);
    font-size: 40px;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.8);
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
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
