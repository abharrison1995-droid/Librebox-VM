<script lang="ts">
  import { coverArt } from "$lib/format";

  interface Props {
    title: string;
    /** Catalog id, used to find the cover bundled with the app. */
    id?: string | null;
    src?: string | null;
    /** Runtime, used to tint the generated cover. */
    runtime?: string | null;
    /** Nominal size of the initials, in px, when no image is available. */
    letterSize?: number;
  }

  let { title, id, src, runtime, letterSize = 40 }: Props = $props();

  // Bundled art first, so covers work offline and on first run before any sync;
  // then the catalog's URL, which can carry art newer than the installed app;
  // then a generated tile. Each step is only reached if the previous 404s.
  let sources = $derived(
    [id ? `/covers/${id}.png` : null, src].filter((s): s is string => !!s),
  );
  let attempt = $state(0);
  let current = $derived(sources[attempt] ?? null);
  let art = $derived(coverArt(title, runtime));

  // Selecting a different game reuses this component, so the cursor has to go
  // back to the start or the new game inherits the old one's failures.
  $effect(() => {
    sources;
    attempt = 0;
  });

  // Two initials need to be smaller than one to fit the same box.
  let fontSize = $derived(art.initials.length > 1 ? letterSize * 0.72 : letterSize);
  // Unique per instance so multiple tiles don't share gradient ids.
  const uid = Math.random().toString(36).slice(2, 9);
</script>

<div class="cover">
  {#if current}
    <img src={current} alt="{title} cover art" onerror={() => (attempt += 1)} />
  {:else}
    <!-- Generated rather than scraped: box art is copyrighted independently of
         whether a game is freely redistributable. -->
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" role="img" aria-label="{title} cover">
      <defs>
        <linearGradient id="g{uid}" x1="0" y1="0" x2="0.6" y2="1">
          <stop offset="0" stop-color={art.from} />
          <stop offset="1" stop-color={art.to} />
        </linearGradient>
        <pattern id="s{uid}" width="100" height="3" patternUnits="userSpaceOnUse">
          <rect width="100" height="1.5" fill="#fff" opacity="0.055" />
        </pattern>
      </defs>

      <rect width="100" height="100" fill="url(#g{uid})" />
      <!-- A soft corner glow keeps the flat fill from looking like a swatch. -->
      <circle cx="18" cy="14" r="46" fill={art.accent} opacity="0.16" />
      <rect width="100" height="100" fill="url(#s{uid})" />
      <!-- Accent rule, echoing a spine on a game box. -->
      <rect x="0" y="0" width="3.5" height="100" fill={art.accent} opacity="0.85" />
    </svg>
    <span class="initials" style="font-size: {fontSize}px">{art.initials}</span>
  {/if}
</div>

<style>
  .cover {
    position: relative;
    width: 100%;
    aspect-ratio: 1 / 1;
    border-radius: 2px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(0, 0, 0, 0.18);
  }
  .cover img,
  .cover svg {
    width: 100%;
    height: 100%;
    display: block;
    object-fit: cover;
  }
  /* Covers are 128px art upscaled 4x. Bilinear smoothing on the way back down
     turns the deliberate pixels to mush, which is the whole look. */
  .cover img {
    image-rendering: pixelated;
  }
  .initials {
    position: absolute;
    font-family: var(--luna-font-title);
    font-weight: 700;
    letter-spacing: 0.02em;
    color: rgba(255, 255, 255, 0.92);
    text-shadow: 0 2px 6px rgba(0, 0, 0, 0.45);
    line-height: 1;
    pointer-events: none;
  }
</style>
