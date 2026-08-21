<script lang="ts">
  import { getCurrentWindow } from "@tauri-apps/api/window";

  let isMaximized = $state(false);

  async function checkMaximized() {
    isMaximized = await getCurrentWindow().isMaximized();
  }

  async function minimize() {
    await getCurrentWindow().minimize();
  }

  async function toggleMaximize() {
    await getCurrentWindow().toggleMaximize();
    await checkMaximized();
  }

  async function close() {
    await getCurrentWindow().close();
  }

  $effect(() => {
    checkMaximized();
  });
</script>

<header class="titlebar" data-tauri-drag-region>
  <div class="titlebar-icon" data-tauri-drag-region>
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <rect x="1" y="2" width="14" height="12" rx="2" fill="#4A90D9" opacity="0.8"/>
      <rect x="3" y="5" width="4" height="3" rx="0.5" fill="#FFF" opacity="0.9"/>
      <rect x="9" y="5" width="4" height="3" rx="0.5" fill="#FFF" opacity="0.7"/>
      <rect x="3" y="9.5" width="10" height="2.5" rx="0.5" fill="#FFF" opacity="0.5"/>
    </svg>
  </div>
  <span class="titlebar-text" data-tauri-drag-region>Librebox</span>

  <div class="titlebar-controls">
    <button class="control-btn minimize" onclick={minimize} aria-label="Minimize">
      <svg width="10" height="10" viewBox="0 0 10 10"><rect x="1" y="7" width="8" height="2" fill="currentColor"/></svg>
    </button>
    <button class="control-btn maximize" onclick={toggleMaximize} aria-label="Maximize">
      {#if isMaximized}
        <svg width="10" height="10" viewBox="0 0 10 10">
          <rect x="2" y="0" width="8" height="8" fill="none" stroke="currentColor" stroke-width="1.5"/>
          <rect x="0" y="2" width="8" height="8" fill="var(--luna-title-start)" stroke="currentColor" stroke-width="1.5"/>
        </svg>
      {:else}
        <svg width="10" height="10" viewBox="0 0 10 10"><rect x="0.5" y="0.5" width="9" height="9" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>
      {/if}
    </button>
    <button class="control-btn close" onclick={close} aria-label="Close">
      <svg width="10" height="10" viewBox="0 0 10 10">
        <line x1="1" y1="1" x2="9" y2="9" stroke="currentColor" stroke-width="1.8"/>
        <line x1="9" y1="1" x2="1" y2="9" stroke="currentColor" stroke-width="1.8"/>
      </svg>
    </button>
  </div>
</header>

<style>
  .titlebar {
    display: flex;
    align-items: center;
    height: var(--luna-title-height);
    background: linear-gradient(180deg, #0A69F0 0%, #0353CC 45%, #0245A8 55%, #024FCC 100%);
    padding: 0 4px;
    flex-shrink: 0;
    border-bottom: 1px solid #003399;
  }

  .titlebar-icon {
    display: flex;
    align-items: center;
    padding: 0 4px 0 2px;
  }

  .titlebar-text {
    font-family: var(--luna-font-title);
    font-size: 13px;
    font-weight: 700;
    color: var(--luna-title-text);
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.4);
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .titlebar-controls {
    display: flex;
    gap: 2px;
    padding-right: 2px;
  }

  .control-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    border: none;
    border-radius: 3px;
    color: white;
    cursor: pointer;
    background: linear-gradient(180deg,
      rgba(255,255,255,0.25) 0%,
      rgba(255,255,255,0.1) 45%,
      rgba(0,0,0,0.05) 55%,
      rgba(0,0,0,0.1) 100%
    );
    outline: none;
  }
  .control-btn:hover {
    background: linear-gradient(180deg,
      rgba(255,255,255,0.4) 0%,
      rgba(255,255,255,0.2) 45%,
      rgba(0,0,0,0.0) 55%,
      rgba(0,0,0,0.05) 100%
    );
  }
  .control-btn:active {
    background: linear-gradient(180deg,
      rgba(0,0,0,0.1) 0%,
      rgba(0,0,0,0.05) 45%,
      rgba(255,255,255,0.05) 55%,
      rgba(255,255,255,0.1) 100%
    );
  }

  .close:hover {
    background: linear-gradient(180deg, #E04040 0%, #C02020 100%);
  }
  .close:active {
    background: linear-gradient(180deg, #A01010 0%, #C02020 100%);
  }
</style>
