use rusqlite::{Connection, Result, params};
use serde::{Deserialize, Serialize};
use std::path::Path;
use std::sync::Mutex;

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
        let db = Database {
            conn: Mutex::new(conn),
        };
        db.init_tables()?;
        Ok(db)
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
            );"
        )?;
        Ok(())
    }

    pub fn list_games(&self) -> Result<Vec<Game>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare(
            "SELECT id, title, year, publisher, platform, engine, source,
                    install_path, cover_path, last_played, playtime_s
             FROM games ORDER BY title"
        )?;
        let rows = stmt.query_map([], |row| {
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
            })
        })?;
        rows.collect()
    }

    pub fn add_game(&self, game: &Game) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute(
            "INSERT INTO games (id, title, year, publisher, platform, engine, source, install_path, cover_path)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9)",
            params![
                game.id, game.title, game.year, game.publisher,
                game.platform, game.engine, game.source,
                game.install_path, game.cover_path
            ],
        )?;
        Ok(())
    }

    pub fn remove_game(&self, id: &str) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute("DELETE FROM games WHERE id = ?1", params![id])?;
        Ok(())
    }
}
