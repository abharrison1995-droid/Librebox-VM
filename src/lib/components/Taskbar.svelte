<script lang="ts">
  import { downloads } from "$lib/downloads.svelte";
  import { launcher } from "$lib/launcher.svelte";

  let now = $state(new Date());

  let active = $derived(Object.entries(downloads.active));
  let running = $derived(Object.entries(launcher.running));

  function percent(downloaded: number, total: number | null): string {
    if (!total) return "";
    return ` ${Math.round((downloaded / total) * 100)}%`;
  }

  $effect(() => {
    const interval = setInterval(() => {
      now = new Date();
    }, 30_000);
    return () => clearInterval(interval);
  });

  function formatTime(date: Date): string {
    return date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  }
</script>

<footer class="taskbar">
  <button class="start-button">
    <svg class="start-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
      <rect x="1" y="1" width="6" height="6" rx="1" fill="#FF6B35"/>
      <rect x="9" y="1" width="6" height="6" rx="1" fill="#7EB742"/>
      <rect x="1" y="9" width="6" height="6" rx="1" fill="#3A86E0"/>
      <rect x="9" y="9" width="6" height="6" rx="1" fill="#FFC107"/>
    </svg>
    <span class="start-label">start</span>
  </button>

  <div class="taskbar-apps">
    {#each running as [gameId, title] (gameId)}
      <span class="task-button running" title="{title} is running">
        <span class="task-label">{title}</span>
      </span>
    {/each}
    {#each active as [catalogId, job] (catalogId)}
      <span class="task-button" title="{catalogId}: {job.phase}">
        <span class="task-label">{catalogId}{percent(job.downloaded, job.total)}</span>
      </span>
    {/each}
  </div>

  <div class="system-tray">
    <span class="tray-clock">{formatTime(now)}</span>
  </div>
</footer>

<style>
  .task-button {
    display: flex;
    align-items: center;
    max-width: 180px;
    padding: 2px 8px;
    border-radius: 3px;
    background: rgba(255, 255, 255, 0.22);
    border: 1px solid rgba(255, 255, 255, 0.28);
    color: #fff;
    font-size: 11px;
  }
  .task-label {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  /* A running game reads as pressed-in, the way an active XP task button did. */
  .task-button.running {
    background: rgba(0, 0, 0, 0.22);
    border-color: rgba(0, 0, 0, 0.3);
    font-weight: 600;
  }

  .taskbar {
    display: flex;
    align-items: center;
    height: var(--luna-taskbar-height);
    background: linear-gradient(180deg, #2A6EF0 0%, #1856CC 6%, #245EDC 50%, #1B4BC8 94%, #153DA8 100%);
    border-top: 1px solid #5C9AFF;
    flex-shrink: 0;
    padding: 0 2px;
    gap: 4px;
  }

  .start-button {
    display: flex;
    align-items: center;
    gap: 4px;
    height: 30px;
    padding: 0 12px 0 6px;
    border: none;
    border-radius: 0 8px 8px 0;
    cursor: pointer;
    color: var(--luna-start-text);
    font-family: var(--luna-font-title);
    font-size: 14px;
    font-weight: 700;
    font-style: italic;
    background: linear-gradient(180deg, #5DBF62 0%, #3FAF44 10%, #3C9E44 50%, #2E8B38 90%, #237A2C 100%);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.3);
    text-shadow: 0 1px 1px rgba(0, 0, 0, 0.3);
    outline: none;
  }
  .start-button:hover {
    background: linear-gradient(180deg, #6ED072 0%, #4CBF50 10%, #48AF4C 50%, #38A03E 90%, #2C8C32 100%);
  }
  .start-button:active {
    background: linear-gradient(180deg, #2E8B38 0%, #3C9E44 50%, #4AB654 100%);
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.3);
  }

  .start-icon {
    flex-shrink: 0;
  }

  .start-label {
    letter-spacing: 0.02em;
  }

  .taskbar-apps {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 3px;
    padding: 0 4px;
    min-width: 0;
  }

  .system-tray {
    display: flex;
    align-items: center;
    height: 28px;
    padding: 0 10px;
    background: linear-gradient(180deg, #1A56BD 0%, #1248A0 50%, #0E3D8C 100%);
    border-left: 1px solid rgba(255,255,255,0.15);
    border-radius: 2px;
  }

  .tray-clock {
    font-family: var(--luna-font);
    font-size: 12px;
    color: #FFFFFF;
    text-shadow: 0 1px 1px rgba(0, 0, 0, 0.3);
    white-space: nowrap;
  }
</style>
