mod catalog;
mod db;

use catalog::{CatalogFilter, CatalogGame, SyncResult, CATALOG_URL};
use db::{Database, Game};
use std::sync::Mutex;
use tauri::Manager;

struct AppState {
    db: Database,
}

// ------------------------------------------------------------------- library

#[tauri::command]
fn list_games(state: tauri::State<Mutex<AppState>>) -> Result<Vec<Game>, String> {
    let app = state.lock().map_err(|e| e.to_string())?;
    app.db.list_games().map_err(|e| e.to_string())
}

#[tauri::command]
fn add_game(
    state: tauri::State<Mutex<AppState>>,
    title: String,
    platform: String,
    year: Option<i32>,
    publisher: Option<String>,
) -> Result<Game, String> {
    let app = state.lock().map_err(|e| e.to_string())?;
    let game = Game {
        id: uuid::Uuid::new_v4().to_string(),
        title,
        year,
        publisher,
        platform,
        engine: None,
        source: "byo".to_string(),
        install_path: None,
        cover_path: None,
        last_played: None,
        playtime_s: 0,
        catalog_id: None,
        runtime: None,
        runtime_config: None,
    };
    app.db.add_game(&game).map_err(|e| e.to_string())?;
    Ok(game)
}

#[tauri::command]
fn remove_game(state: tauri::State<Mutex<AppState>>, id: String) -> Result<(), String> {
    let app = state.lock().map_err(|e| e.to_string())?;
    app.db.remove_game(&id).map_err(|e| e.to_string())
}

// ------------------------------------------------------------------- catalog

/// Refreshes the cached catalog. Prefers the published copy and falls back to
/// the bundled one, so this never leaves the user with an empty catalog.
#[tauri::command]
async fn sync_catalog(state: tauri::State<'_, Mutex<AppState>>) -> Result<SyncResult, String> {
    let (games, source, fallback_reason) = match catalog::fetch_remote(CATALOG_URL).await {
        Ok(file) => (file.games, "remote", None),
        Err(remote_err) => {
            let file = catalog::load_bundled().map_err(|bundled_err| {
                format!("remote fetch failed ({remote_err}); bundled catalog also failed ({bundled_err})")
            })?;
            (file.games, "bundled", Some(remote_err.to_string()))
        }
    };

    let entry_count = games.len();
    {
        let app = state.lock().map_err(|e| e.to_string())?;
        app.db
            .replace_catalog(&games, source)
            .map_err(|e| e.to_string())?;
    }

    let synced_at = {
        let app = state.lock().map_err(|e| e.to_string())?;
        app.db
            .catalog_meta_get("last_sync")
            .ok()
            .flatten()
            .unwrap_or_default()
    };

    Ok(SyncResult {
        source: source.to_string(),
        entry_count,
        synced_at,
        fallback_reason,
    })
}

#[tauri::command]
fn list_catalog(
    state: tauri::State<Mutex<AppState>>,
    platform: Option<String>,
    runtime: Option<String>,
    license: Option<String>,
    search: Option<String>,
) -> Result<Vec<CatalogGame>, String> {
    let app = state.lock().map_err(|e| e.to_string())?;
    app.db
        .list_catalog(&CatalogFilter {
            platform,
            runtime,
            license,
            search,
        })
        .map_err(|e| e.to_string())
}

#[tauri::command]
fn get_catalog_game(
    state: tauri::State<Mutex<AppState>>,
    id: String,
) -> Result<Option<CatalogGame>, String> {
    let app = state.lock().map_err(|e| e.to_string())?;
    app.db.get_catalog_game(&id).map_err(|e| e.to_string())
}

#[derive(serde::Serialize)]
struct CatalogStatus {
    last_sync: Option<String>,
    source: Option<String>,
    entry_count: i64,
}

#[tauri::command]
fn catalog_status(state: tauri::State<Mutex<AppState>>) -> Result<CatalogStatus, String> {
    let app = state.lock().map_err(|e| e.to_string())?;
    Ok(CatalogStatus {
        last_sync: app.db.catalog_meta_get("last_sync").ok().flatten(),
        source: app.db.catalog_meta_get("source").ok().flatten(),
        entry_count: app
            .db
            .catalog_meta_get("entry_count")
            .ok()
            .flatten()
            .and_then(|v| v.parse().ok())
            .unwrap_or(0),
    })
}

// ---------------------------------------------------------------------- setup

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            let data_dir = app.path().app_data_dir()?;
            let db_path = data_dir.join("librebox.db");
            let database = Database::open(&db_path)?;
            app.manage(Mutex::new(AppState { db: database }));

            // Seed the catalog immediately from the bundled copy so the UI has
            // data on first paint, then refresh from the network in the
            // background. A slow or absent network never blocks startup.
            if let Ok(bundled) = catalog::load_bundled() {
                if let Some(state) = app.try_state::<Mutex<AppState>>() {
                    if let Ok(guard) = state.lock() {
                        let _ = guard.db.replace_catalog(&bundled.games, "bundled");
                    }
                }
            }

            let handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                match catalog::fetch_remote(CATALOG_URL).await {
                    Ok(file) => {
                        if let Some(state) = handle.try_state::<Mutex<AppState>>() {
                            if let Ok(guard) = state.lock() {
                                if let Err(e) = guard.db.replace_catalog(&file.games, "remote") {
                                    eprintln!("catalog: failed to cache remote copy: {e}");
                                }
                            }
                        }
                    }
                    Err(e) => eprintln!("catalog: using bundled copy ({e})"),
                }
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            list_games,
            add_game,
            remove_game,
            sync_catalog,
            list_catalog,
            get_catalog_game,
            catalog_status,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
