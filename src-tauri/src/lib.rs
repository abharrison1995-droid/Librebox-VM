mod catalog;
mod db;
mod download;
mod launch;

use catalog::{CatalogFilter, CatalogGame, SyncResult, CATALOG_URL};
use db::{Database, Game};
use download::{InstallError, InstallPhase};
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use tauri::{AppHandle, Emitter, Manager};

/// An install in flight. Progress lives here rather than in the database: it
/// changes many times a second, and routing it through the DB lock would
/// serialise every UI query behind the download.
#[derive(Clone)]
struct InstallJob {
    cancel: Arc<AtomicBool>,
    phase: InstallPhase,
    downloaded: u64,
    total: Option<u64>,
}

#[derive(Clone, serde::Serialize)]
struct InstallProgress {
    catalog_id: String,
    phase: InstallPhase,
    downloaded: u64,
    total: Option<u64>,
}

/// `Database` already guards its connection, and `installs` has its own lock,
/// so the state itself is shared unwrapped. A single outer mutex would put
/// download progress and catalog queries behind the same lock.
struct AppState {
    db: Database,
    installs: Mutex<HashMap<String, InstallJob>>,
    /// Games currently running, keyed by game id.
    running: Mutex<HashMap<String, RunningGame>>,
}

// ------------------------------------------------------------------- library

#[tauri::command]
fn list_games(state: tauri::State<AppState>) -> Result<Vec<Game>, String> {
    state.db.list_games().map_err(|e| e.to_string())
}

/// Builds the `runtime_config` for a game the user already owns, resolving the
/// program they named inside the folder they picked.
///
/// Uses the same resolution as an installed game, so "the exe is in a
/// subfolder" works identically whether the files came from the catalog or
/// from the user's own disk.
fn byo_runtime_config(dir: &Path, executable: &str) -> Result<String, String> {
    let found = download::resolve_executable(dir, executable)
        .ok_or_else(|| format!("could not find {executable} anywhere in that folder"))?;
    serde_json::to_string(&serde_json::json!({
        "executable": executable,
        "executable_path": found.to_string_lossy().replace('\\', "/"),
    }))
    .map_err(|e| e.to_string())
}

/// Adds a game the user already owns.
///
/// When a folder and executable are supplied the executable is resolved inside
/// that folder — the same way an installed game's is — so a game added this way
/// is launchable rather than just catalogued.
#[tauri::command]
fn add_game(
    state: tauri::State<AppState>,
    title: String,
    platform: String,
    year: Option<i32>,
    publisher: Option<String>,
    install_path: Option<String>,
    runtime: Option<String>,
    executable: Option<String>,
) -> Result<Game, String> {
    let title = title.trim().to_string();
    if title.is_empty() {
        return Err("a title is required".into());
    }

    let mut runtime_config = None;
    let install_path = match install_path.as_deref().map(str::trim).filter(|p| !p.is_empty()) {
        None => None,
        Some(path) => {
            let dir = Path::new(path);
            if !dir.is_dir() {
                return Err("that folder does not exist".into());
            }
            if let Some(exe) = executable.as_deref().map(str::trim).filter(|e| !e.is_empty()) {
                runtime_config = Some(byo_runtime_config(dir, exe)?);
            }
            Some(path.to_string())
        }
    };

    // A runtime without a resolved executable could never launch, so do not
    // record one; the game is still catalogued.
    let runtime = runtime.filter(|_| runtime_config.is_some());

    let game = Game {
        id: uuid::Uuid::new_v4().to_string(),
        title,
        year,
        publisher: publisher.filter(|p| !p.trim().is_empty()),
        platform,
        engine: None,
        source: "byo".to_string(),
        install_path,
        cover_path: None,
        last_played: None,
        playtime_s: 0,
        catalog_id: None,
        runtime,
        runtime_config,
    };
    state.db.add_game(&game).map_err(|e| e.to_string())?;
    Ok(game)
}

#[tauri::command]
fn remove_game(state: tauri::State<AppState>, id: String) -> Result<(), String> {
    state.db.remove_game(&id).map_err(|e| e.to_string())
}

// ------------------------------------------------------------------- catalog

#[tauri::command]
async fn sync_catalog(state: tauri::State<'_, AppState>) -> Result<SyncResult, String> {
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
    state
        .db
        .replace_catalog(&games, source)
        .map_err(|e| e.to_string())?;

    Ok(SyncResult {
        source: source.to_string(),
        entry_count,
        synced_at: state
            .db
            .catalog_meta_get("last_sync")
            .ok()
            .flatten()
            .unwrap_or_default(),
        fallback_reason,
    })
}

#[tauri::command]
fn list_catalog(
    state: tauri::State<AppState>,
    platform: Option<String>,
    runtime: Option<String>,
    license: Option<String>,
    search: Option<String>,
) -> Result<Vec<CatalogGame>, String> {
    state
        .db
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
    state: tauri::State<AppState>,
    id: String,
) -> Result<Option<CatalogGame>, String> {
    state.db.get_catalog_game(&id).map_err(|e| e.to_string())
}

#[derive(serde::Serialize)]
struct CatalogStatus {
    last_sync: Option<String>,
    source: Option<String>,
    entry_count: i64,
}

#[tauri::command]
fn catalog_status(state: tauri::State<AppState>) -> Result<CatalogStatus, String> {
    Ok(CatalogStatus {
        last_sync: state.db.catalog_meta_get("last_sync").ok().flatten(),
        source: state.db.catalog_meta_get("source").ok().flatten(),
        entry_count: state
            .db
            .catalog_meta_get("entry_count")
            .ok()
            .flatten()
            .and_then(|v| v.parse().ok())
            .unwrap_or(0),
    })
}

// ------------------------------------------------------------------ installs

/// Catalog ids the user already has on disk, for marking the catalog view.
#[tauri::command]
fn installed_ids(state: tauri::State<AppState>) -> Result<Vec<String>, String> {
    state
        .db
        .installed_catalog_ids()
        .map(|s| s.into_iter().collect())
        .map_err(|e| e.to_string())
}

/// In-flight installs, so the UI can rehydrate after a navigation or reload.
#[tauri::command]
fn active_installs(state: tauri::State<AppState>) -> Vec<InstallProgress> {
    let jobs = match state.installs.lock() {
        Ok(j) => j,
        Err(_) => return Vec::new(),
    };
    jobs.iter()
        .map(|(id, job)| InstallProgress {
            catalog_id: id.clone(),
            phase: job.phase,
            downloaded: job.downloaded,
            total: job.total,
        })
        .collect()
}

#[tauri::command]
fn cancel_install(state: tauri::State<AppState>, catalog_id: String) -> Result<(), String> {
    let jobs = state.installs.lock().map_err(|e| e.to_string())?;
    match jobs.get(&catalog_id) {
        Some(job) => {
            job.cancel.store(true, Ordering::Relaxed);
            Ok(())
        }
        None => Err("no install in progress for that game".into()),
    }
}

struct InstallPaths {
    part: PathBuf,
    staging: PathBuf,
    final_dir: PathBuf,
}

fn install_paths(app: &AppHandle, catalog_id: &str) -> Result<InstallPaths, String> {
    let root = app.path().app_data_dir().map_err(|e| e.to_string())?;
    Ok(InstallPaths {
        part: root.join("downloads").join(format!("{catalog_id}.part")),
        staging: root.join("staging").join(catalog_id),
        final_dir: root.join("games").join(catalog_id),
    })
}

/// Downloads, verifies, extracts, and registers a catalog game.
///
/// Nothing is written to the library until every fallible step has succeeded,
/// and the install directory is only touched by the final atomic rename — a
/// failure can never leave a half-install that looks complete.
#[tauri::command]
async fn install_game(
    app: AppHandle,
    state: tauri::State<'_, AppState>,
    catalog_id: String,
) -> Result<Game, String> {
    let entry = state
        .db
        .get_catalog_game(&catalog_id)
        .map_err(|e| e.to_string())?
        .ok_or_else(|| format!("'{catalog_id}' is not in the catalog"))?;

    // Refuse formats we cannot unpack before spending bandwidth on them.
    if !download::is_supported_format(entry.download.format.as_deref()) {
        return Err(
            InstallError::UnsupportedFormat(entry.download.format.clone().unwrap_or_default())
                .to_string(),
        );
    }

    {
        let mut jobs = state.installs.lock().map_err(|e| e.to_string())?;
        if jobs.contains_key(&catalog_id) {
            return Err("that game is already installing".into());
        }
        jobs.insert(
            catalog_id.clone(),
            InstallJob {
                cancel: Arc::new(AtomicBool::new(false)),
                phase: InstallPhase::Downloading,
                downloaded: 0,
                total: entry.download.size_bytes.map(|n| n as u64),
            },
        );
    }

    let paths = install_paths(&app, &catalog_id)?;
    let result = {
        let emitter = app.clone();
        run_install(&state.db, &state.installs, &entry, &paths, &move |p| {
            let _ = emitter.emit("install:progress", p);
        })
        .await
    };

    // Always drop the job and sweep scratch files, whatever happened.
    if let Ok(mut jobs) = state.installs.lock() {
        jobs.remove(&catalog_id);
    }
    let _ = std::fs::remove_file(&paths.part);
    let _ = std::fs::remove_dir_all(&paths.staging);

    match result {
        Ok(game) => {
            let _ = app.emit(
                "install:done",
                serde_json::json!({ "catalog_id": catalog_id, "game_id": game.id }),
            );
            Ok(game)
        }
        Err(e) => {
            let message = e.to_string();
            let _ = app.emit(
                "install:failed",
                serde_json::json!({ "catalog_id": catalog_id, "error": message }),
            );
            Err(message)
        }
    }
}

/// The install flow proper.
///
/// Takes the database and job map directly rather than a Tauri `State`, and
/// reports progress through a closure rather than an `AppHandle`, so the whole
/// flow can be exercised in tests without an app instance.
async fn run_install(
    db: &Database,
    installs: &Mutex<HashMap<String, InstallJob>>,
    entry: &CatalogGame,
    paths: &InstallPaths,
    // Send + Sync because this future is spawned by Tauri's runtime.
    emit: &(dyn Fn(InstallProgress) + Send + Sync),
) -> Result<Game, InstallError> {
    let catalog_id = entry.id.clone();
    let cancel = {
        let jobs = installs.lock().map_err(|e| InstallError::Io(e.to_string()))?;
        jobs.get(&catalog_id)
            .map(|j| j.cancel.clone())
            .ok_or(InstallError::Cancelled)?
    };
    let set_phase = |phase: InstallPhase| {
        if let Ok(mut jobs) = installs.lock() {
            if let Some(job) = jobs.get_mut(&catalog_id) {
                job.phase = phase;
            }
        }
        emit(InstallProgress {
            catalog_id: catalog_id.clone(),
            phase,
            downloaded: 0,
            total: None,
        });
    };

    // --- download ---------------------------------------------------------
    {
        let id = catalog_id.clone();
        download::download_to_file(&entry.download.url, &paths.part, &cancel, |done, total| {
            if let Ok(mut jobs) = installs.lock() {
                if let Some(job) = jobs.get_mut(&id) {
                    job.downloaded = done;
                    job.total = total;
                }
            }
            emit(InstallProgress {
                catalog_id: id.clone(),
                phase: InstallPhase::Downloading,
                downloaded: done,
                total,
            });
        })
        .await?;
    }

    // --- verify -----------------------------------------------------------
    // Verify when the catalog gives us a hash. A remote catalog that predates
    // the hash backfill will not, and refusing to install in that case would be
    // worse than proceeding with a warning.
    match entry.download.sha256.as_deref() {
        Some(expected) => {
            set_phase(InstallPhase::Verifying);
            download::verify_sha256(&paths.part, expected).await?;
        }
        None => eprintln!("install: {catalog_id} has no sha256 in the catalog; skipping verification"),
    }

    if cancel.load(Ordering::Relaxed) {
        return Err(InstallError::Cancelled);
    }

    // --- extract ----------------------------------------------------------
    set_phase(InstallPhase::Extracting);
    let _ = std::fs::remove_dir_all(&paths.staging);
    download::extract_zip(&paths.part, &paths.staging).await?;

    // --- locate the executable -------------------------------------------
    // The catalog names a bare filename; archives disagree about whether it
    // sits at the root. Resolve it now so the launcher never has to guess, and
    // so a bad archive fails here rather than at first play.
    let declared = entry
        .runtime_config
        .get("executable")
        .and_then(|v| v.as_str())
        .map(str::to_string);

    let mut runtime_config = entry.runtime_config.clone();
    if let Some(exe) = declared.as_deref() {
        let found = download::resolve_executable(&paths.staging, exe)
            .ok_or_else(|| InstallError::ExecutableNotFound(exe.to_string()))?;
        if let Some(obj) = runtime_config.as_object_mut() {
            obj.insert(
                "executable_path".into(),
                serde_json::Value::String(found.to_string_lossy().replace('\\', "/")),
            );
        }
    }

    // --- promote ----------------------------------------------------------
    download::promote(&paths.staging, &paths.final_dir)?;

    // --- register ---------------------------------------------------------
    let install_path = paths.final_dir.to_string_lossy().to_string();
    let existing = db
        .get_game_by_catalog_id(&catalog_id)
        .map_err(|e| InstallError::Io(e.to_string()))?;

    let game = Game {
        id: existing
            .as_ref()
            .map(|g| g.id.clone())
            .unwrap_or_else(|| uuid::Uuid::new_v4().to_string()),
        title: entry.title.clone(),
        year: entry.year,
        publisher: entry.publisher.clone(),
        platform: entry.platform.clone(),
        engine: None,
        source: "catalog".into(),
        install_path: Some(install_path),
        cover_path: entry.cover_url.clone(),
        // Reinstalling must not wipe how long you have played.
        last_played: existing.as_ref().and_then(|g| g.last_played.clone()),
        playtime_s: existing.as_ref().map(|g| g.playtime_s).unwrap_or(0),
        catalog_id: Some(catalog_id.clone()),
        runtime: Some(entry.runtime.clone()),
        runtime_config: serde_json::to_string(&runtime_config).ok(),
    };

    if existing.is_some() {
        db.update_game(&game)
    } else {
        db.add_game(&game)
    }
    .map_err(|e| InstallError::Io(e.to_string()))?;

    Ok(game)
}

// ------------------------------------------------------------------ playing

#[derive(Clone, serde::Serialize)]
struct RunningGame {
    game_id: String,
    title: String,
}

#[tauri::command]
fn running_games(state: tauri::State<AppState>) -> Vec<RunningGame> {
    state
        .running
        .lock()
        .map(|r| r.values().cloned().collect())
        .unwrap_or_default()
}

/// Starts an installed game, fetching its runtime first if we do not have it.
///
/// Returns once the game has been spawned; the process is then watched by a
/// background task that records playtime when it exits.
#[tauri::command]
async fn launch_game(
    app: AppHandle,
    state: tauri::State<'_, AppState>,
    id: String,
) -> Result<(), String> {
    let game = state
        .db
        .get_game(&id)
        .map_err(|e| e.to_string())?
        .ok_or("no such game")?;

    if state.running.lock().map(|r| r.contains_key(&id)).unwrap_or(false) {
        return Err("that game is already running".into());
    }

    let install_dir = game
        .install_path
        .as_deref()
        .map(PathBuf::from)
        .ok_or("that game is not installed")?;
    if !install_dir.exists() {
        return Err("the install directory is missing — try reinstalling".into());
    }

    let runtime = game.runtime.as_deref().unwrap_or("native");
    let config: serde_json::Value = game
        .runtime_config
        .as_deref()
        .and_then(|c| serde_json::from_str(c).ok())
        .unwrap_or(serde_json::Value::Object(Default::default()));

    let root = app.path().app_data_dir().map_err(|e| e.to_string())?;

    // Fetch the emulator if this is the first game that needs it. Reuses the
    // install pipeline, so it is verified against the catalog's hash too.
    let runtime_exe = match runtime {
        "dosbox" | "scummvm" => {
            let spec = state
                .db
                .get_runtime(runtime)
                .map_err(|e| e.to_string())?
                .ok_or_else(|| format!("the catalog has no '{runtime}' runtime"))?;

            if launch::installed_runtime(&root, &spec).is_none() {
                let _ = app.emit(
                    "runtime:progress",
                    serde_json::json!({ "runtime": runtime, "name": spec.name, "downloaded": 0, "total": spec.download.size_bytes }),
                );
            }
            let never = AtomicBool::new(false);
            let emitter = app.clone();
            let rt = runtime.to_string();
            let name = spec.name.clone();
            let exe = launch::ensure_runtime(&root, &spec, &never, move |done, total| {
                let _ = emitter.emit(
                    "runtime:progress",
                    serde_json::json!({ "runtime": rt, "name": name, "downloaded": done, "total": total }),
                );
            })
            .await
            .map_err(|e| format!("could not set up {}: {e}", spec.name))?;
            let _ = app.emit("runtime:ready", serde_json::json!({ "runtime": runtime }));
            Some(exe)
        }
        _ => None,
    };

    let conf_path = root.join("conf").join(format!("{id}.conf"));
    let plan = launch::plan_launch(
        runtime,
        runtime_exe.as_deref(),
        &install_dir,
        &config,
        &conf_path,
    )?;

    let mut child = tokio::process::Command::new(&plan.program)
        .args(&plan.args)
        .current_dir(&plan.cwd)
        .spawn()
        .map_err(|e| format!("could not start {}: {e}", plan.program.display()))?;

    if let Ok(mut running) = state.running.lock() {
        running.insert(
            id.clone(),
            RunningGame {
                game_id: id.clone(),
                title: game.title.clone(),
            },
        );
    }
    let _ = app.emit(
        "game:launched",
        serde_json::json!({ "game_id": id, "title": game.title }),
    );

    // Watch for exit off the command's thread so the UI is not blocked for the
    // whole play session.
    let handle = app.clone();
    let watched = id.clone();
    let started = std::time::Instant::now();
    tauri::async_runtime::spawn(async move {
        let status = child.wait().await;
        let seconds = started.elapsed().as_secs() as i64;

        if let Some(state) = handle.try_state::<AppState>() {
            if let Ok(mut running) = state.running.lock() {
                running.remove(&watched);
            }
            // Ignore sessions too short to be a real play — a crash on startup
            // should not accumulate playtime.
            if seconds >= 5 {
                if let Err(e) = state.db.record_play(&watched, seconds) {
                    eprintln!("launch: could not record playtime: {e}");
                }
            }
        }

        let _ = handle.emit(
            "game:exited",
            serde_json::json!({
                "game_id": watched,
                "seconds": seconds,
                "ok": status.map(|s| s.success()).unwrap_or(false),
            }),
        );
    });

    Ok(())
}

/// Removes an installed game's files and its library row.
#[tauri::command]
fn uninstall_game(
    app: AppHandle,
    state: tauri::State<AppState>,
    id: String,
) -> Result<(), String> {
    let game = state
        .db
        .get_game(&id)
        .map_err(|e| e.to_string())?
        .ok_or("no such game")?;

    if let Some(path) = game.install_path.as_deref() {
        // Only ever delete inside our own install root.
        let root = app
            .path()
            .app_data_dir()
            .map_err(|e| e.to_string())?
            .join("games");
        let target = Path::new(path);
        if target.starts_with(&root) && target.exists() {
            std::fs::remove_dir_all(target).map_err(|e| e.to_string())?;
        }
    }

    state.db.remove_game(&id).map_err(|e| e.to_string())
}

// ---------------------------------------------------------------------- setup

/// Clears scratch left behind by a crash or a kill mid-install.
/// Only `downloads/` and `staging/` are swept; `games/` holds real installs.
///
/// Removes the *contents* rather than the directories themselves: on Windows a
/// directory that was recently in use is often still held by the indexer or a
/// virus scanner, and `remove_dir_all` on it fails with a sharing violation
/// even when it is empty. Deleting per entry is also more precise — we only
/// ever want to clear scratch, not remove the folders.
fn sweep_scratch(app: &AppHandle) {
    let Ok(root) = app.path().app_data_dir() else {
        return;
    };
    for dir in ["downloads", "staging"] {
        let path = root.join(dir);
        let Ok(entries) = std::fs::read_dir(&path) else {
            continue; // not created yet, which is the common case
        };
        for entry in entries.flatten() {
            let target = entry.path();
            let result = if target.is_dir() {
                std::fs::remove_dir_all(&target)
            } else {
                std::fs::remove_file(&target)
            };
            if let Err(e) = result {
                eprintln!("startup: could not clear {}: {e}", target.display());
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn job_map(catalog_id: &str) -> Mutex<HashMap<String, InstallJob>> {
        let mut m = HashMap::new();
        m.insert(
            catalog_id.to_string(),
            InstallJob {
                cancel: Arc::new(AtomicBool::new(false)),
                phase: InstallPhase::Downloading,
                downloaded: 0,
                total: None,
            },
        );
        Mutex::new(m)
    }

    #[test]
    fn byo_config_resolves_an_executable_at_the_root() {
        let dir = tempfile::tempdir().unwrap();
        std::fs::write(dir.path().join("GAME.EXE"), b"").unwrap();

        let json = byo_runtime_config(dir.path(), "GAME.EXE").unwrap();
        let v: serde_json::Value = serde_json::from_str(&json).unwrap();
        assert_eq!(v["executable"], "GAME.EXE");
        assert_eq!(v["executable_path"], "GAME.EXE");
    }

    #[test]
    fn byo_config_finds_an_executable_in_a_subfolder() {
        // The common case for a game copied off an old drive.
        let dir = tempfile::tempdir().unwrap();
        let sub = dir.path().join("GAME");
        std::fs::create_dir_all(&sub).unwrap();
        std::fs::write(sub.join("game.exe"), b"").unwrap();

        let json = byo_runtime_config(dir.path(), "GAME.EXE").unwrap();
        let v: serde_json::Value = serde_json::from_str(&json).unwrap();
        // Forward slashes so the stored path matches what the catalog uses.
        assert_eq!(v["executable_path"], "GAME/game.exe");
    }

    #[test]
    fn byo_config_reports_a_missing_executable_by_name() {
        let dir = tempfile::tempdir().unwrap();
        std::fs::write(dir.path().join("README.TXT"), b"").unwrap();

        let err = byo_runtime_config(dir.path(), "GAME.EXE").unwrap_err();
        assert!(err.contains("GAME.EXE"), "the error must name what we looked for: {err}");
    }

    /// The complete install flow against a real catalog entry, including
    /// database registration. Network-bound, so opt-in:
    ///
    ///   cargo test --lib -- --ignored real_
    #[tokio::test]
    #[ignore = "hits the network"]
    async fn real_install_registers_the_game() {
        let bundled = catalog::load_bundled().unwrap();
        let entry = bundled
            .games
            .iter()
            .filter(|g| g.runtime == "dosbox" && g.download.format.as_deref() == Some("zip"))
            .min_by_key(|g| g.download.size_bytes.unwrap_or(i64::MAX))
            .unwrap()
            .clone();

        let dir = tempfile::tempdir().unwrap();
        let db = Database::open(&dir.path().join("t.db")).unwrap();
        let paths = InstallPaths {
            part: dir.path().join("downloads").join("g.part"),
            staging: dir.path().join("staging"),
            final_dir: dir.path().join("games").join(&entry.id),
        };
        let installs = job_map(&entry.id);

        // Mutex rather than RefCell: the callback must be Sync.
        let seen = Mutex::new(Vec::new());
        let game = run_install(&db, &installs, &entry, &paths, &|p| {
            seen.lock().unwrap().push(p.phase);
        })
        .await
        .expect("install should succeed");
        let phases = seen.into_inner().unwrap();

        // Files are where we said they would be.
        assert!(paths.final_dir.exists(), "install directory must exist");
        assert!(!paths.staging.exists(), "staging must be consumed by the promote");

        // The resolved executable path was recorded and actually points at a file.
        let cfg: serde_json::Value =
            serde_json::from_str(game.runtime_config.as_deref().unwrap()).unwrap();
        let rel = cfg["executable_path"].as_str().expect("executable_path recorded");
        assert!(
            paths.final_dir.join(rel).exists(),
            "recorded executable_path {rel} must exist on disk"
        );

        // Provenance is written so the launcher and catalog view can find it.
        assert_eq!(game.catalog_id.as_deref(), Some(entry.id.as_str()));
        assert_eq!(game.source, "catalog");
        assert_eq!(game.runtime.as_deref(), Some("dosbox"));
        assert!(game.install_path.is_some());

        // It is in the library and marked installed.
        assert_eq!(db.list_games().unwrap().len(), 1);
        assert!(db.installed_catalog_ids().unwrap().contains(&entry.id));

        // Progress ran through the real phases in order.
        assert!(phases.contains(&InstallPhase::Downloading));
        assert!(phases.contains(&InstallPhase::Verifying), "hash must be checked");
        assert!(phases.contains(&InstallPhase::Extracting));
    }

    /// Reinstalling must reuse the row and keep playtime rather than
    /// duplicating the game.
    #[tokio::test]
    #[ignore = "hits the network"]
    async fn real_reinstall_preserves_playtime() {
        let bundled = catalog::load_bundled().unwrap();
        let entry = bundled
            .games
            .iter()
            .filter(|g| g.runtime == "dosbox" && g.download.format.as_deref() == Some("zip"))
            .min_by_key(|g| g.download.size_bytes.unwrap_or(i64::MAX))
            .unwrap()
            .clone();

        let dir = tempfile::tempdir().unwrap();
        let db = Database::open(&dir.path().join("t.db")).unwrap();
        let mk = |n: &str| InstallPaths {
            part: dir.path().join("downloads").join(format!("{n}.part")),
            staging: dir.path().join("staging").join(n),
            final_dir: dir.path().join("games").join(&entry.id),
        };

        let first = run_install(&db, &job_map(&entry.id), &entry, &mk("a"), &|_| {})
            .await
            .unwrap();

        // Pretend the user played it.
        let mut played = db.get_game(&first.id).unwrap().unwrap();
        played.playtime_s = 7200;
        played.last_played = Some("2026-08-23 12:00:00".into());
        db.update_game(&played).unwrap();

        let second = run_install(&db, &job_map(&entry.id), &entry, &mk("b"), &|_| {})
            .await
            .unwrap();

        assert_eq!(second.id, first.id, "reinstall must reuse the row");
        assert_eq!(db.list_games().unwrap().len(), 1, "no duplicate row");
        assert_eq!(second.playtime_s, 7200, "playtime must survive a reinstall");
        assert_eq!(second.last_played.as_deref(), Some("2026-08-23 12:00:00"));
    }

    /// A tampered download must fail closed. Network-bound because the
    /// download runs before the hash is checked.
    #[tokio::test]
    #[ignore = "hits the network"]
    async fn real_install_refuses_a_bad_hash_and_leaves_no_trace() {
        let bundled = catalog::load_bundled().unwrap();
        let mut entry = bundled
            .games
            .iter()
            .find(|g| g.id == "commander-keen-1")
            .unwrap()
            .clone();
        entry.download.sha256 = Some("b".repeat(64));

        let dir = tempfile::tempdir().unwrap();
        let db = Database::open(&dir.path().join("t.db")).unwrap();
        let paths = InstallPaths {
            part: dir.path().join("downloads").join("g.part"),
            staging: dir.path().join("staging"),
            final_dir: dir.path().join("games").join("x"),
        };
        let installs = job_map(&entry.id);
        let result = run_install(&db, &installs, &entry, &paths, &|_| {}).await;

        assert!(result.is_err(), "a wrong hash must fail the install");
        assert!(!paths.final_dir.exists(), "nothing may be promoted");
        assert_eq!(db.list_games().unwrap().len(), 0, "no library row on failure");
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        // Must be registered first. Two instances would race over one SQLite
        // file, and the startup sweep below would delete the other's in-flight
        // downloads, so focus the existing window instead of opening a second.
        .plugin(tauri_plugin_single_instance::init(|app, _argv, _cwd| {
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.unminimize();
                let _ = window.set_focus();
            }
        }))
        .plugin(tauri_plugin_opener::init())
        // Folder picking for adding a game you already own.
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            let data_dir = app.path().app_data_dir()?;
            let db_path = data_dir.join("librebox.db");
            let database = Database::open(&db_path)?;
            app.manage(AppState {
                db: database,
                installs: Mutex::new(HashMap::new()),
                running: Mutex::new(HashMap::new()),
            });

            sweep_scratch(app.handle());

            // Seed the catalog immediately from the bundled copy so the UI has
            // data on first paint, then refresh from the network in the
            // background. A slow or absent network never blocks startup.
            if let Ok(bundled) = catalog::load_bundled() {
                if let Some(state) = app.try_state::<AppState>() {
                    if let Err(e) = state.db.replace_catalog(&bundled.games, "bundled") {
                        eprintln!("catalog: could not seed bundled copy: {e}");
                    }
                    let _ = state.db.set_runtimes(&bundled.runtimes);
                }
            }

            let handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                match catalog::fetch_remote(CATALOG_URL).await {
                    Ok(file) => {
                        if let Some(state) = handle.try_state::<AppState>() {
                            if let Err(e) = state.db.replace_catalog(&file.games, "remote") {
                                eprintln!("catalog: failed to cache remote copy: {e}");
                            }
                            // Only replace runtimes when the remote actually
                            // carries them; an older catalog must not wipe ours.
                            if !file.runtimes.is_empty() {
                                let _ = state.db.set_runtimes(&file.runtimes);
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
            installed_ids,
            active_installs,
            install_game,
            cancel_install,
            uninstall_game,
            launch_game,
            running_games,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
