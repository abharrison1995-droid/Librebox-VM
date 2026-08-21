mod db;

use db::{Database, Game};
use std::sync::Mutex;
use tauri::Manager;

struct AppState {
    db: Database,
}

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
    };
    app.db.add_game(&game).map_err(|e| e.to_string())?;
    Ok(game)
}

#[tauri::command]
fn remove_game(state: tauri::State<Mutex<AppState>>, id: String) -> Result<(), String> {
    let app = state.lock().map_err(|e| e.to_string())?;
    app.db.remove_game(&id).map_err(|e| e.to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            let data_dir = app
                .path()
                .app_data_dir()
                .expect("failed to resolve app data dir");
            let db_path = data_dir.join("librebox.db");
            let database =
                Database::open(&db_path).expect("failed to open database");
            app.manage(Mutex::new(AppState { db: database }));
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            list_games,
            add_game,
            remove_game,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
