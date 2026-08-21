<script lang="ts">
  import "$lib/theme/luna.css";
  import TitleBar from "$lib/components/TitleBar.svelte";
  import Taskbar from "$lib/components/Taskbar.svelte";
  import type { Snippet } from "svelte";

  let { children }: { children: Snippet } = $props();
</script>

<div class="app-shell">
  <TitleBar />
  <main class="app-content">
    {@render children()}
  </main>
  <Taskbar />
</div>

<style>
  .app-shell {
    display: flex;
    flex-direction: column;
    height: 100vh;
    width: 100vw;
    overflow: hidden;
  }
  .app-content {
    flex: 1;
    overflow: hidden;
    display: flex;
  }
</style>
