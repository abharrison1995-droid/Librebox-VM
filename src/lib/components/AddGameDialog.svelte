<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import { open } from "@tauri-apps/plugin-dialog";
  import type { Game } from "$lib/types";

  interface Props {
    onclose: () => void;
    onadded: (game: Game) => void;
  }

  let { onclose, onadded }: Props = $props();

  let title = $state("");
  let platform = $state("dos");
  let year = $state("");
  let publisher = $state("");
  let folder = $state("");
  let executable = $state("");
  let saving = $state(false);
  let error = $state<string | null>(null);

  // A folder alone catalogues the game; a folder plus an executable makes it
  // launchable. Keep that distinction visible rather than silently degrading.
  let launchable = $derived(!!folder && !!executable.trim());
  // DOS games run under DOSBox; anything else we can start directly.
  let runtime = $derived(platform === "dos" ? "dosbox" : "native");

  async function pickFolder() {
    const chosen = await open({ directory: true, multiple: false, title: "Select the game folder" });
    if (typeof chosen === "string") {
      folder = chosen;
      error = null;
    }
  }

  async function submit(event: Event) {
    event.preventDefault();
    if (!title.trim() || saving) return;

    saving = true;
    error = null;
    try {
      const parsedYear = year.trim() ? Number.parseInt(year, 10) : null;
      const game = await invoke<Game>("add_game", {
        title,
        platform,
        year: Number.isFinite(parsedYear as number) ? parsedYear : null,
        publisher: publisher.trim() || null,
        installPath: folder || null,
        runtime: launchable ? runtime : null,
        executable: executable.trim() || null,
      });
      onadded(game);
    } catch (e) {
      error = String(e);
    } finally {
      saving = false;
    }
  }

  function onKeydown(event: KeyboardEvent) {
    if (event.key === "Escape") onclose();
  }
</script>

<svelte:window onkeydown={onKeydown} />

<!-- Modal scrim. Clicking it dismisses, matching the Escape key. -->
<div
  class="scrim"
  role="button"
  tabindex="-1"
  aria-label="Close dialog"
  onclick={onclose}
  onkeydown={(e) => e.key === "Enter" && onclose()}
></div>

<div class="dialog xp-panel" role="dialog" aria-modal="true" aria-labelledby="add-game-heading">
  <header class="dialog-title">
    <span id="add-game-heading">Add a game you own</span>
    <button class="close" onclick={onclose} aria-label="Close">✕</button>
  </header>

  <form onsubmit={submit}>
    <label class="field">
      <span>Title</span>
      <!-- svelte-ignore a11y_autofocus -->
      <input class="xp-input" bind:value={title} autofocus required placeholder="e.g. Alley Cat" />
    </label>

    <div class="row">
      <label class="field">
        <span>Platform</span>
        <select class="xp-input" bind:value={platform}>
          <option value="dos">DOS</option>
          <option value="win9x">Windows 9x</option>
          <option value="winxp">Windows XP</option>
          <option value="native">Native</option>
        </select>
      </label>
      <label class="field narrow">
        <span>Year</span>
        <input class="xp-input" bind:value={year} inputmode="numeric" placeholder="1984" />
      </label>
    </div>

    <label class="field">
      <span>Publisher <em>optional</em></span>
      <input class="xp-input" bind:value={publisher} />
    </label>

    <fieldset class="files">
      <legend>Files <em>optional</em></legend>
      <div class="row">
        <label class="field">
          <span>Folder</span>
          <input class="xp-input" bind:value={folder} placeholder="No folder selected" readonly />
        </label>
        <button type="button" class="xp-button browse" onclick={pickFolder}>Browse…</button>
      </div>
      <label class="field">
        <span>Program to run</span>
        <input
          class="xp-input"
          bind:value={executable}
          placeholder={platform === "dos" ? "GAME.EXE" : "game.exe"}
        />
      </label>
      <p class="note">
        {#if launchable}
          Will run under {runtime === "dosbox" ? "DOSBox" : "your system"}. Librebox
          searches the folder for that program, so subfolders are fine.
        {:else if folder}
          Without a program name this game is catalogued but cannot be launched.
        {:else}
          Add a folder and program name to make this game launchable.
        {/if}
      </p>
    </fieldset>

    {#if error}
      <p class="error" role="alert">{error}</p>
    {/if}

    <footer class="actions">
      <button type="button" class="xp-button" onclick={onclose}>Cancel</button>
      <button type="submit" class="xp-button primary" disabled={!title.trim() || saving}>
        {saving ? "Adding…" : "Add Game"}
      </button>
    </footer>
  </form>
</div>

<style>
  .scrim {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.35);
    border: none;
    padding: 0;
    z-index: 10;
  }
  .dialog {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 380px;
    max-width: calc(100vw - 32px);
    max-height: calc(100vh - 64px);
    overflow-y: auto;
    z-index: 11;
    padding: 0;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.4);
  }

  .dialog-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 4px 4px 9px;
    background: linear-gradient(
      to bottom,
      var(--luna-title-start, #0058e6),
      var(--luna-title-end, #003fa8)
    );
    color: #fff;
    font-family: var(--luna-font-title);
    font-size: 12px;
    font-weight: 700;
  }
  .close {
    width: 20px;
    height: 18px;
    border: 1px solid rgba(255, 255, 255, 0.5);
    border-radius: 3px;
    background: rgba(255, 255, 255, 0.18);
    color: #fff;
    font-size: 10px;
    cursor: pointer;
  }
  .close:hover {
    background: #d94f4f;
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 9px;
    padding: 12px;
  }
  .field {
    display: flex;
    flex-direction: column;
    gap: 2px;
    font-size: 11px;
    flex: 1;
    min-width: 0;
  }
  .field span {
    color: var(--luna-text-secondary);
  }
  .field em {
    font-style: normal;
    color: var(--luna-text-disabled);
  }
  .field input,
  .field select {
    font-size: 12px;
    padding: 3px 5px;
  }
  .narrow {
    max-width: 84px;
  }
  .row {
    display: flex;
    gap: 8px;
    align-items: flex-end;
  }
  .browse {
    padding: 4px 10px;
    font-size: 11px;
    white-space: nowrap;
  }

  .files {
    border: 1px solid var(--luna-panel-border);
    border-radius: 3px;
    padding: 8px 10px 10px;
    margin: 2px 0 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .files legend {
    font-size: 11px;
    font-weight: 600;
    padding: 0 4px;
  }
  .note {
    font-size: 10px;
    line-height: 1.4;
    color: var(--luna-text-secondary);
    margin: 0;
  }

  .error {
    font-size: 11px;
    color: #7a1c1c;
    background: #fbe6e6;
    border: 1px solid #d48a8a;
    border-radius: 3px;
    padding: 5px 6px;
    margin: 0;
  }

  .actions {
    display: flex;
    justify-content: flex-end;
    gap: 6px;
    margin-top: 2px;
  }
  .actions button {
    min-width: 78px;
    padding: 4px 12px;
    font-size: 11px;
  }
  .primary {
    font-weight: 600;
  }
</style>
