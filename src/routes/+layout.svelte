<script lang="ts">
  import "$lib/theme/luna.css";
  import TitleBar from "$lib/components/TitleBar.svelte";
  import Taskbar from "$lib/components/Taskbar.svelte";
  import TabStrip from "$lib/components/TabStrip.svelte";
  import { downloads } from "$lib/downloads.svelte";
  import { launcher } from "$lib/launcher.svelte";
  import type { Snippet } from "svelte";

  let { children }: { children: Snippet } = $props();

  // Registered here, not in a route: an install or a running game must survive
  // navigating between the Library and Catalog tabs.
  $effect(() => {
    downloads.init();
    launcher.init();
    return () => {
      downloads.destroy();
      launcher.destroy();
    };
  });
</script>

<div class="app-shell">
  <TitleBar />
  <TabStrip />
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
