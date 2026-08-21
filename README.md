# Librebox VM

A retro gaming VM sandbox frontend that brings classic games to your fingertips. Librebox provides simplified downloads for a curated collection of free classic games, packaged in an easy-to-use virtual machine environment.

## Features

- **Retro Game Library**: Play a curated selection of classic games in an isolated VM sandbox
- **Simplified Downloads**: One-click game installation with no complex setup required
- **Driver Management**: On-demand driver installation and troubleshooting tools
- **System Diagnostics**: Built-in tools to help diagnose and resolve compatibility issues
- **Lightweight**: Desktop application built with Tauri for minimal resource usage

## Technology Stack

Built with:
- **Frontend**: [SvelteKit](https://kit.svelte.dev/) + TypeScript + [Vite](https://vitejs.dev/)
- **Desktop**: [Tauri](https://tauri.app/) for cross-platform app distribution

## Getting Started

### Prerequisites
- [Node.js](https://nodejs.org/) (v18+)
- [Rust](https://www.rust-lang.org/tools/install)

### Development

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Build the desktop app
npm run tauri build
```

## Recommended IDE Setup

[VS Code](https://code.visualstudio.com/) + [Svelte](https://marketplace.visualstudio.com/items?itemName=svelte.svelte-vscode) + [Tauri](https://marketplace.visualstudio.com/items?itemName=tauri-apps.tauri-vscode) + [rust-analyzer](https://marketplace.visualstudio.com/items?itemName=rust-lang.rust-analyzer).

## License

MIT
