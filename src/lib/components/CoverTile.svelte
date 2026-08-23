<script lang="ts">
  import { generateColor } from "$lib/format";

  interface Props {
    title: string;
    src?: string | null;
    /** Font size of the fallback letter, in px. */
    letterSize?: number;
  }

  let { title, src, letterSize = 40 }: Props = $props();

  // Covers are remote URLs in the catalog and may 404; fall back to the tile.
  let failed = $state(false);
  let showImage = $derived(!!src && !failed);
</script>

<div class="cover" style="background-color: {showImage ? 'transparent' : generateColor(title)}">
  {#if showImage}
    <img src={src} alt="{title} cover art" onerror={() => (failed = true)} />
  {:else}
    <span class="cover-letter" style="font-size: {letterSize}px">
      {title.charAt(0).toUpperCase()}
    </span>
  {/if}
</div>

<style>
  .cover {
    width: 100%;
    aspect-ratio: 1 / 1;
    border-radius: 2px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(0, 0, 0, 0.1);
  }
  .cover img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  .cover-letter {
    font-family: var(--luna-font-title);
    font-weight: 700;
    color: rgba(255, 255, 255, 0.8);
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }
</style>
