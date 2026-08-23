use crate::catalog::{CatalogFilter, CatalogGame, DownloadInfo, RuntimeSpec};
use rusqlite::{Connection, Result, params, params_from_iter};
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};
use std::path::Path;
use std::sync::Mutex;

/// Bump when the schema changes and add a matching arm in `migrate`.
const SCHEMA_VERSION: i32 = 1;

/// True if `table` already has `column`.
///
/// Used instead of catching the ALTER error: SQLite reports a duplicate column
/// as a plain `SQLITE_ERROR`, indistinguishable by code from a genuine failure,
/// and matching on the message text is brittle across versions.
fn column_exists(conn: &Connection, table: &str, column: &str) -> Result<bool> {
    // PRAGMA does not accept bound parameters for the table name. Every caller
    // passes a literal from this file, never user input.
    let mut stmt = conn.prepare(&format!("PRAGMA table_info({table})"))?;
    let mut rows = stmt.query([])?;
    while let Some(row) = rows.next()? {
        let name: String = row.get(1)?;
        if name == column {
            return Ok(true);
        }
    }
    Ok(false)
}

/// Column list shared by every `games` query, so the row mapper below always
/// matches the indices it reads.
const GAME_SELECT: &str = "SELECT id, title, year, publisher, platform, engine, source,
            install_path, cover_path, last_played, playtime_s,
            catalog_id, runtime, runtime_config
     FROM games";

fn row_to_game(row: &rusqlite::Row) -> Result<Game> {
    Ok(Game {
        id: row.get(0)?,
        title: row.get(1)?,
        year: row.get(2)?,
        publisher: row.get(3)?,
        platform: row.get(4)?,
        engine: row.get(5)?,
        source: row.get(6)?,
        install_path: row.get(7)?,
        cover_path: row.get(8)?,
        last_played: row.get(9)?,
        playtime_s: row.get(10)?,
        catalog_id: row.get(11)?,
        runtime: row.get(12)?,
        runtime_config: row.get(13)?,
    })
}

fn add_column_if_missing(conn: &Connection, table: &str, column: &str, decl: &str) -> Result<()> {
    if !column_exists(conn, table, column)? {
        conn.execute(&format!("ALTER TABLE {table} ADD COLUMN {column} {decl}"), [])?;
    }
    Ok(())
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Game {
    pub id: String,
    pub title: String,
    pub year: Option<i32>,
    pub publisher: Option<String>,
    pub platform: String,
    pub engine: Option<String>,
    pub source: String,
    pub install_path: Option<String>,
    pub cover_path: Option<String>,
    pub last_played: Option<String>,
    pub playtime_s: i64,
    /// Links an installed game back to the catalog entry it came from.
    /// `None` for games the user added themselves.
    pub catalog_id: Option<String>,
    pub runtime: Option<String>,
    pub runtime_config: Option<String>,
}

pub struct Database {
    conn: Mutex<Connection>,
}

impl Database {
    pub fn open(db_path: &Path) -> Result<Self> {
        if let Some(parent) = db_path.parent() {
            std::fs::create_dir_all(parent).ok();
        }
        let conn = Connection::open(db_path)?;
        // Without this the ON DELETE CASCADE clauses below are inert.
        conn.pragma_update(None, "foreign_keys", "ON")?;
        let db = Database {
            conn: Mutex::new(conn),
        };
        db.init_tables()?;
        db.migrate()?;
        Ok(db)
    }

    /// Applies incremental schema changes to databases created by an older
    /// build. `init_tables` handles fresh databases; this handles existing
    /// ones, which `CREATE TABLE IF NOT EXISTS` silently leaves untouched.
    fn migrate(&self) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        let current: i32 = conn.query_row("PRAGMA user_version", [], |r| r.get(0))?;

        if current < 1 {
            // Added alongside the catalog. A fresh database already has these
            // from init_tables, so each is applied only if absent.
            for (column, decl) in [
                ("catalog_id", "TEXT"),
                ("runtime", "TEXT"),
                ("runtime_config", "TEXT"),
            ] {
                add_column_if_missing(&conn, "games", column, decl)?;
            }
        }

        conn.pragma_update(None, "user_version", SCHEMA_VERSION)?;
        Ok(())
    }

    fn init_tables(&self) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute_batch(
            "CREATE TABLE IF NOT EXISTS games (
                id          TEXT PRIMARY KEY,
                title       TEXT NOT NULL,
                year        INTEGER,
                publisher   TEXT,
                platform    TEXT NOT NULL DEFAULT 'dos',
                engine      TEXT,
                source      TEXT NOT NULL DEFAULT 'byo',
                install_path TEXT,
                cover_path  TEXT,
                last_played TEXT,
                playtime_s  INTEGER NOT NULL DEFAULT 0,
                catalog_id  TEXT,
                runtime     TEXT,
                runtime_config TEXT,
                created_at  TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS engine_profiles (
                id        TEXT PRIMARY KEY,
                game_id   TEXT NOT NULL REFERENCES games(id) ON DELETE CASCADE,
                engine    TEXT NOT NULL,
                config    TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS save_states (
                id         TEXT PRIMARY KEY,
                game_id    TEXT NOT NULL REFERENCES games(id) ON DELETE CASCADE,
                slot       TEXT,
                path       TEXT NOT NULL,
                thumb_path TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            -- A disposable cache of the remote catalog. Wiped and rewritten on
            -- every sync, so it must never hold user state.
            CREATE TABLE IF NOT EXISTS catalog_games (
                id              TEXT PRIMARY KEY,
                title           TEXT NOT NULL,
                year            INTEGER,
                developer       TEXT,
                publisher       TEXT,
                platform        TEXT NOT NULL,
                runtime         TEXT NOT NULL,
                genres          TEXT,
                license         TEXT NOT NULL,
                license_note    TEXT,
                source_url      TEXT,
                description     TEXT,
                cover_url       TEXT,
                download_url    TEXT NOT NULL,
                download_format TEXT,
                download_size   INTEGER,
                download_sha256 TEXT,
                runtime_config  TEXT,
                synced_at       TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_catalog_platform ON catalog_games(platform);
            CREATE INDEX IF NOT EXISTS idx_catalog_runtime  ON catalog_games(runtime);
            CREATE INDEX IF NOT EXISTS idx_catalog_license  ON catalog_games(license);

            CREATE TABLE IF NOT EXISTS catalog_meta (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );"
        )?;
        Ok(())
    }

    pub fn list_games(&self) -> Result<Vec<Game>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare(&format!("{GAME_SELECT} ORDER BY title"))?;
        let rows = stmt.query_map([], row_to_game)?;
        rows.collect()
    }

    pub fn add_game(&self, game: &Game) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute(
            "INSERT INTO games (id, title, year, publisher, platform, engine, source,
                                install_path, cover_path, catalog_id, runtime, runtime_config)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12)",
            params![
                game.id, game.title, game.year, game.publisher,
                game.platform, game.engine, game.source,
                game.install_path, game.cover_path,
                game.catalog_id, game.runtime, game.runtime_config
            ],
        )?;
        Ok(())
    }

    pub fn remove_game(&self, id: &str) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute("DELETE FROM games WHERE id = ?1", params![id])?;
        Ok(())
    }

    pub fn get_game(&self, id: &str) -> Result<Option<Game>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare(&format!("{GAME_SELECT} WHERE id = ?1"))?;
        let mut rows = stmt.query_map(params![id], row_to_game)?;
        rows.next().transpose()
    }

    /// Finds an installed game by the catalog entry it came from. The pipeline
    /// uses this to detect a reinstall and reuse the existing row.
    pub fn get_game_by_catalog_id(&self, catalog_id: &str) -> Result<Option<Game>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare(&format!("{GAME_SELECT} WHERE catalog_id = ?1"))?;
        let mut rows = stmt.query_map(params![catalog_id], row_to_game)?;
        rows.next().transpose()
    }

    /// Overwrites every mutable field of an existing row.
    pub fn update_game(&self, game: &Game) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute(
            "UPDATE games SET
                 title = ?2, year = ?3, publisher = ?4, platform = ?5, engine = ?6,
                 source = ?7, install_path = ?8, cover_path = ?9, last_played = ?10,
                 playtime_s = ?11, catalog_id = ?12, runtime = ?13, runtime_config = ?14
             WHERE id = ?1",
            params![
                game.id, game.title, game.year, game.publisher, game.platform,
                game.engine, game.source, game.install_path, game.cover_path,
                game.last_played, game.playtime_s, game.catalog_id, game.runtime,
                game.runtime_config
            ],
        )?;
        Ok(())
    }

    /// The catalog ids the user already has installed, for marking the catalog
    /// view. One cheap query beats joining per card.
    pub fn installed_catalog_ids(&self) -> Result<HashSet<String>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare(
            "SELECT catalog_id FROM games
             WHERE catalog_id IS NOT NULL AND install_path IS NOT NULL",
        )?;
        let rows = stmt.query_map([], |r| r.get::<_, String>(0))?;
        rows.collect()
    }

    // ---------------------------------------------------------------- catalog

    /// Swaps in a new catalog atomically. A failed sync leaves the previous
    /// catalog intact rather than a half-written one.
    ///
    /// Only touches `catalog_games`; the user's `games` library is untouched.
    pub fn replace_catalog(&self, games: &[CatalogGame], source: &str) -> Result<()> {
        let mut conn = self.conn.lock().unwrap();
        let tx = conn.transaction()?;

        tx.execute("DELETE FROM catalog_games", [])?;
        {
            let mut stmt = tx.prepare(
                "INSERT INTO catalog_games (
                     id, title, year, developer, publisher, platform, runtime, genres,
                     license, license_note, source_url, description, cover_url,
                     download_url, download_format, download_size, download_sha256,
                     runtime_config
                 ) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12, ?13,
                           ?14, ?15, ?16, ?17, ?18)",
            )?;
            for g in games {
                stmt.execute(params![
                    g.id,
                    g.title,
                    g.year,
                    g.developer,
                    g.publisher,
                    g.platform,
                    g.runtime,
                    serde_json::to_string(&g.genres).unwrap_or_else(|_| "[]".into()),
                    g.license,
                    g.license_note,
                    g.source_url,
                    g.description,
                    g.cover_url,
                    g.download.url,
                    g.download.format,
                    g.download.size_bytes,
                    g.download.sha256,
                    serde_json::to_string(&g.runtime_config).ok(),
                ])?;
            }
        }

        for (k, v) in [
            ("source", source.to_string()),
            ("entry_count", games.len().to_string()),
        ] {
            tx.execute(
                "INSERT INTO catalog_meta (key, value) VALUES (?1, ?2)
                 ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                params![k, v],
            )?;
        }
        tx.execute(
            "INSERT INTO catalog_meta (key, value) VALUES ('last_sync', datetime('now'))
             ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            [],
        )?;

        tx.commit()
    }

    pub fn list_catalog(&self, filter: &CatalogFilter) -> Result<Vec<CatalogGame>> {
        let mut sql = String::from(
            "SELECT id, title, year, developer, publisher, platform, runtime, genres,
                    license, license_note, source_url, description, cover_url,
                    download_url, download_format, download_size, download_sha256,
                    runtime_config
             FROM catalog_games WHERE 1=1",
        );
        let mut args: Vec<String> = Vec::new();

        for (clause, value) in [
            (" AND platform = ?", &filter.platform),
            (" AND runtime = ?", &filter.runtime),
            (" AND license = ?", &filter.license),
        ] {
            if let Some(v) = value.as_ref().filter(|v| !v.is_empty()) {
                sql.push_str(clause);
                args.push(v.clone());
            }
        }

        if let Some(term) = filter.search.as_ref().filter(|s| !s.trim().is_empty()) {
            sql.push_str(" AND (title LIKE ? OR publisher LIKE ? OR developer LIKE ?)");
            let like = format!("%{}%", term.trim());
            args.extend([like.clone(), like.clone(), like]);
        }

        sql.push_str(" ORDER BY title");

        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare(&sql)?;
        let rows = stmt.query_map(params_from_iter(args.iter()), row_to_catalog_game)?;
        rows.collect()
    }

    pub fn get_catalog_game(&self, id: &str) -> Result<Option<CatalogGame>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare(
            "SELECT id, title, year, developer, publisher, platform, runtime, genres,
                    license, license_note, source_url, description, cover_url,
                    download_url, download_format, download_size, download_sha256,
                    runtime_config
             FROM catalog_games WHERE id = ?1",
        )?;
        let mut rows = stmt.query_map(params![id], row_to_catalog_game)?;
        rows.next().transpose()
    }

    /// Runtimes are few and only ever read as a set, so they live as one JSON
    /// blob in `catalog_meta` rather than earning their own table.
    pub fn set_runtimes(&self, runtimes: &HashMap<String, RuntimeSpec>) -> Result<()> {
        let json = serde_json::to_string(runtimes).unwrap_or_else(|_| "{}".into());
        let conn = self.conn.lock().unwrap();
        conn.execute(
            "INSERT INTO catalog_meta (key, value) VALUES ('runtimes', ?1)
             ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            params![json],
        )?;
        Ok(())
    }

    pub fn get_runtime(&self, id: &str) -> Result<Option<RuntimeSpec>> {
        Ok(self.get_runtimes()?.remove(id))
    }

    pub fn get_runtimes(&self) -> Result<HashMap<String, RuntimeSpec>> {
        Ok(self
            .catalog_meta_get("runtimes")?
            .and_then(|j| serde_json::from_str(&j).ok())
            .unwrap_or_default())
    }

    /// Adds a play session. Done as one statement so two sessions finishing at
    /// once cannot lose an increment the way a read-modify-write would.
    pub fn record_play(&self, id: &str, seconds: i64) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute(
            "UPDATE games SET playtime_s = playtime_s + ?2, last_played = datetime('now')
             WHERE id = ?1",
            params![id, seconds],
        )?;
        Ok(())
    }

    pub fn catalog_meta_get(&self, key: &str) -> Result<Option<String>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare("SELECT value FROM catalog_meta WHERE key = ?1")?;
        let mut rows = stmt.query_map(params![key], |r| r.get(0))?;
        rows.next().transpose()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::catalog;

    fn temp_db() -> (Database, tempfile::TempDir) {
        let dir = tempfile::tempdir().unwrap();
        let db = Database::open(&dir.path().join("test.db")).unwrap();
        (db, dir)
    }

    fn seeded() -> (Database, tempfile::TempDir) {
        let (db, dir) = temp_db();
        let bundled = catalog::load_bundled().unwrap();
        db.replace_catalog(&bundled.games, "bundled").unwrap();
        (db, dir)
    }

    fn byo(id: &str, title: &str) -> Game {
        Game {
            id: id.into(),
            title: title.into(),
            year: Some(1995),
            publisher: None,
            platform: "dos".into(),
            engine: None,
            source: "byo".into(),
            install_path: None,
            cover_path: None,
            last_played: None,
            playtime_s: 0,
            catalog_id: None,
            runtime: None,
            runtime_config: None,
        }
    }

    #[test]
    fn migration_sets_schema_version() {
        let (db, _dir) = temp_db();
        let conn = db.conn.lock().unwrap();
        let version: i32 = conn.query_row("PRAGMA user_version", [], |r| r.get(0)).unwrap();
        assert_eq!(version, SCHEMA_VERSION);
    }

    #[test]
    fn foreign_keys_are_enabled() {
        let (db, _dir) = temp_db();
        let conn = db.conn.lock().unwrap();
        let on: i32 = conn.query_row("PRAGMA foreign_keys", [], |r| r.get(0)).unwrap();
        assert_eq!(on, 1, "ON DELETE CASCADE is inert without this");
    }

    #[test]
    fn reopening_an_existing_database_is_idempotent() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("test.db");
        {
            let db = Database::open(&path).unwrap();
            db.add_game(&byo("g1", "Kept")).unwrap();
        }
        // Simulates an upgrade: migrate() must not fail on columns that exist.
        let db = Database::open(&path).unwrap();
        assert_eq!(db.list_games().unwrap().len(), 1);
    }

    #[test]
    fn catalog_round_trips() {
        let (db, _dir) = seeded();
        let all = db.list_catalog(&CatalogFilter::default()).unwrap();
        assert!(all.len() >= 30, "expected a populated catalog, got {}", all.len());

        let doom = db.get_catalog_game("doom-shareware").unwrap().unwrap();
        assert_eq!(doom.runtime, "dosbox");
        assert!(!doom.genres.is_empty(), "genres must survive the JSON round-trip");
        assert!(doom.download.size_bytes.unwrap() > 0);
        assert!(doom.license_note.is_some());
    }

    #[test]
    fn unknown_catalog_id_is_none() {
        let (db, _dir) = seeded();
        assert!(db.get_catalog_game("no-such-game").unwrap().is_none());
    }

    #[test]
    fn filters_narrow_results() {
        let (db, _dir) = seeded();
        let all = db.list_catalog(&CatalogFilter::default()).unwrap().len();

        let dosbox = db
            .list_catalog(&CatalogFilter {
                runtime: Some("dosbox".into()),
                ..Default::default()
            })
            .unwrap();
        assert!(!dosbox.is_empty() && dosbox.len() < all);
        assert!(dosbox.iter().all(|g| g.runtime == "dosbox"));

        let shareware = db
            .list_catalog(&CatalogFilter {
                license: Some("shareware".into()),
                ..Default::default()
            })
            .unwrap();
        assert!(shareware.iter().all(|g| g.license == "shareware"));

        // Filters must combine, not override one another.
        let both = db
            .list_catalog(&CatalogFilter {
                runtime: Some("dosbox".into()),
                license: Some("shareware".into()),
                ..Default::default()
            })
            .unwrap();
        assert!(both.len() <= dosbox.len().min(shareware.len()));
        assert!(both
            .iter()
            .all(|g| g.runtime == "dosbox" && g.license == "shareware"));
    }

    #[test]
    fn search_matches_title_and_is_case_insensitive() {
        let (db, _dir) = seeded();
        let hits = db
            .list_catalog(&CatalogFilter {
                search: Some("doom".into()),
                ..Default::default()
            })
            .unwrap();
        assert!(hits.iter().any(|g| g.id == "doom-shareware"));

        let upper = db
            .list_catalog(&CatalogFilter {
                search: Some("DOOM".into()),
                ..Default::default()
            })
            .unwrap();
        assert_eq!(hits.len(), upper.len());
    }

    #[test]
    fn empty_filter_strings_are_ignored() {
        let (db, _dir) = seeded();
        let all = db.list_catalog(&CatalogFilter::default()).unwrap().len();
        // The UI sends "" for an unset dropdown; that must not match zero rows.
        let blank = db
            .list_catalog(&CatalogFilter {
                platform: Some(String::new()),
                search: Some("   ".into()),
                ..Default::default()
            })
            .unwrap();
        assert_eq!(blank.len(), all);
    }

    #[test]
    fn sync_does_not_touch_the_user_library() {
        let (db, _dir) = seeded();
        db.add_game(&byo("mine", "My Own Copy")).unwrap();

        let bundled = catalog::load_bundled().unwrap();
        db.replace_catalog(&bundled.games, "remote").unwrap();

        let library = db.list_games().unwrap();
        assert_eq!(library.len(), 1, "a catalog sync must not clobber the library");
        assert_eq!(library[0].id, "mine");
    }

    #[test]
    fn replace_catalog_is_not_additive() {
        let (db, _dir) = seeded();
        let first = db.list_catalog(&CatalogFilter::default()).unwrap().len();
        let bundled = catalog::load_bundled().unwrap();
        db.replace_catalog(&bundled.games, "remote").unwrap();
        assert_eq!(
            db.list_catalog(&CatalogFilter::default()).unwrap().len(),
            first,
            "re-syncing must replace rows, not duplicate them"
        );
    }

    #[test]
    fn meta_reflects_the_last_sync() {
        let (db, _dir) = seeded();
        assert_eq!(db.catalog_meta_get("source").unwrap().unwrap(), "bundled");

        let bundled = catalog::load_bundled().unwrap();
        db.replace_catalog(&bundled.games, "remote").unwrap();
        assert_eq!(db.catalog_meta_get("source").unwrap().unwrap(), "remote");
        assert!(db.catalog_meta_get("last_sync").unwrap().is_some());
        assert_eq!(
            db.catalog_meta_get("entry_count").unwrap().unwrap(),
            bundled.games.len().to_string()
        );
    }

    #[test]
    fn get_game_finds_by_id_and_catalog_id() {
        let (db, _dir) = temp_db();
        let mut g = byo("g1", "Installed");
        g.catalog_id = Some("doom-shareware".into());
        g.install_path = Some("C:/games/doom".into());
        db.add_game(&g).unwrap();

        assert_eq!(db.get_game("g1").unwrap().unwrap().title, "Installed");
        assert!(db.get_game("nope").unwrap().is_none());
        assert_eq!(
            db.get_game_by_catalog_id("doom-shareware").unwrap().unwrap().id,
            "g1"
        );
        assert!(db.get_game_by_catalog_id("not-installed").unwrap().is_none());
    }

    #[test]
    fn update_game_overwrites_without_duplicating() {
        let (db, _dir) = temp_db();
        db.add_game(&byo("g1", "Before")).unwrap();

        let mut g = db.get_game("g1").unwrap().unwrap();
        g.title = "After".into();
        g.install_path = Some("C:/games/x".into());
        g.playtime_s = 3600;
        db.update_game(&g).unwrap();

        let all = db.list_games().unwrap();
        assert_eq!(all.len(), 1, "update must not insert a second row");
        assert_eq!(all[0].title, "After");
        assert_eq!(all[0].install_path.as_deref(), Some("C:/games/x"));
        assert_eq!(all[0].playtime_s, 3600);
    }

    #[test]
    fn installed_ids_only_counts_games_on_disk() {
        let (db, _dir) = temp_db();

        // Installed from the catalog.
        let mut installed = byo("g1", "Installed");
        installed.catalog_id = Some("doom-shareware".into());
        installed.install_path = Some("C:/games/doom".into());
        db.add_game(&installed).unwrap();

        // From the catalog but with no files yet — must not count.
        let mut pending = byo("g2", "Pending");
        pending.catalog_id = Some("tyrian-2000".into());
        db.add_game(&pending).unwrap();

        // A user's own copy has no catalog id at all.
        db.add_game(&byo("g3", "My Own")).unwrap();

        let ids = db.installed_catalog_ids().unwrap();
        assert_eq!(ids.len(), 1);
        assert!(ids.contains("doom-shareware"));
    }

    #[test]
    fn record_play_accumulates_and_stamps() {
        let (db, _dir) = temp_db();
        db.add_game(&byo("g1", "Doom")).unwrap();

        db.record_play("g1", 600).unwrap();
        db.record_play("g1", 300).unwrap();

        let g = db.get_game("g1").unwrap().unwrap();
        assert_eq!(g.playtime_s, 900, "sessions must add, not overwrite");
        assert!(g.last_played.is_some(), "last_played must be stamped");
    }

    #[test]
    fn runtimes_round_trip() {
        let (db, _dir) = temp_db();
        let bundled = catalog::load_bundled().unwrap();
        assert!(!bundled.runtimes.is_empty(), "catalog must declare runtimes");

        db.set_runtimes(&bundled.runtimes).unwrap();
        let dosbox = db.get_runtime("dosbox").unwrap().expect("dosbox must persist");
        assert_eq!(dosbox.executable, "dosbox.exe");
        assert!(dosbox.download.sha256.is_some());
        assert!(db.get_runtime("nope").unwrap().is_none());
    }

    #[test]
    fn every_declared_game_runtime_is_obtainable() {
        // A game whose runtime the catalog does not provide can never launch.
        let bundled = catalog::load_bundled().unwrap();
        for g in &bundled.games {
            if g.runtime == "native" || g.runtime == "86box" {
                continue;
            }
            assert!(
                bundled.runtimes.contains_key(&g.runtime),
                "{} needs runtime '{}' which the catalog does not provide",
                g.id,
                g.runtime
            );
        }
    }

    #[test]
    fn library_round_trips_catalog_provenance() {
        let (db, _dir) = temp_db();
        let mut g = byo("installed", "From Catalog");
        g.source = "catalog".into();
        g.catalog_id = Some("doom-shareware".into());
        g.runtime = Some("dosbox".into());
        g.runtime_config = Some(r#"{"executable":"DOOM.EXE"}"#.into());
        db.add_game(&g).unwrap();

        let got = &db.list_games().unwrap()[0];
        assert_eq!(got.catalog_id.as_deref(), Some("doom-shareware"));
        assert_eq!(got.runtime.as_deref(), Some("dosbox"));
        assert!(got.runtime_config.as_ref().unwrap().contains("DOOM.EXE"));
    }
}

fn row_to_catalog_game(row: &rusqlite::Row) -> Result<CatalogGame> {
    let genres: Option<String> = row.get(7)?;
    let runtime_config: Option<String> = row.get(17)?;
    Ok(CatalogGame {
        id: row.get(0)?,
        title: row.get(1)?,
        year: row.get(2)?,
        developer: row.get(3)?,
        publisher: row.get(4)?,
        platform: row.get(5)?,
        runtime: row.get(6)?,
        genres: genres
            .and_then(|g| serde_json::from_str(&g).ok())
            .unwrap_or_default(),
        license: row.get(8)?,
        license_note: row.get(9)?,
        source_url: row.get(10)?,
        description: row.get(11)?,
        cover_url: row.get(12)?,
        download: DownloadInfo {
            url: row.get(13)?,
            format: row.get(14)?,
            size_bytes: row.get(15)?,
            sha256: row.get(16)?,
        },
        runtime_config: runtime_config
            .and_then(|c| serde_json::from_str(&c).ok())
            .unwrap_or(serde_json::Value::Null),
    })
}
