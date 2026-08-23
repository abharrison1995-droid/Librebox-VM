<script lang="ts">
  import { page } from "$app/state";

  const tabs = [
    { href: "/", label: "Library" },
    { href: "/catalog", label: "Catalog" },
  ];

  let current = $derived(page.url.pathname);
</script>

<nav class="tab-strip" aria-label="Main sections">
  {#each tabs as tab (tab.href)}
    <a
      class="tab"
      class:active={current === tab.href}
      href={tab.href}
      aria-current={current === tab.href ? "page" : undefined}
    >
      {tab.label}
    </a>
  {/each}
</nav>

<style>
  .tab-strip {
    display: flex;
    align-items: flex-end;
    gap: 2px;
    padding: 4px 8px 0;
    background: var(--luna-window-bg);
    border-bottom: 1px solid var(--luna-panel-border);
    flex-shrink: 0;
  }

  .tab {
    font-family: var(--luna-font);
    font-size: 11px;
    padding: 4px 14px 5px;
    border: 1px solid var(--luna-panel-border);
    border-bottom: none;
    border-radius: 3px 3px 0 0;
    background: linear-gradient(to bottom, #f6f4ec, #e4e0d2);
    color: var(--luna-text-secondary);
    text-decoration: none;
    position: relative;
    top: 1px;
  }
  .tab:hover {
    background: linear-gradient(to bottom, #fdfcf8, #ece8dc);
    color: var(--luna-text);
  }
  .tab.active {
    background: var(--luna-window-bg);
    color: var(--luna-text);
    font-weight: 600;
    padding-bottom: 6px;
    /* Sits over the strip's bottom border so the active tab reads as
       continuous with the content below it. */
    z-index: 1;
  }
  .tab:focus-visible {
    outline: 1px dotted var(--luna-text);
    outline-offset: -3px;
  }
</style>
