//! Catalog data model and sync.
//!
//! The catalog is a remote JSON document listing games Librebox can install.
//! It is fetched at launch and cached in SQLite; a copy is bundled into the
//! binary so the app is useful offline and on first run.

use serde::{Deserialize, Serialize};

/// Highest `schema_version` this build understands. A catalog declaring a
/// newer version is rejected in favour of the bundled copy rather than being
/// partially misread.
pub const SUPPORTED_SCHEMA_VERSION: u32 = 1;

/// Where the published catalog lives. Overridable at build time so forks and
/// local testing do not have to patch the source.
pub const CATALOG_URL: &str = match option_env!("LIBREBOX_CATALOG_URL") {
    Some(url) => url,
    None => "https://abharrison1995-droid.github.io/Librebox-VM/catalog.json",
};

const BUNDLED: &str = include_str!("../../catalog/catalog.json");

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DownloadInfo {
    pub url: String,
    pub format: Option<String>,
    pub size_bytes: Option<i64>,
    pub sha256: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CatalogGame {
    pub id: String,
    pub title: String,
    pub year: Option<i32>,
    pub developer: Option<String>,
    pub publisher: Option<String>,
    pub platform: String,
    pub runtime: String,
    #[serde(default)]
    pub genres: Vec<String>,
    pub license: String,
    pub license_note: Option<String>,
    pub source_url: Option<String>,
    pub description: Option<String>,
    pub cover_url: Option<String>,
    pub download: DownloadInfo,
    #[serde(default)]
    pub runtime_config: serde_json::Value,
}

/// An emulator or interpreter Librebox fetches on demand. Described in the
/// catalog rather than hardcoded so a version bump needs no app release, and
/// so it is downloaded and hash-verified by exactly the same pipeline as games.
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct RuntimeSpec {
    pub id: String,
    pub name: String,
    pub version: String,
    /// Executable to look for inside the extracted archive.
    pub executable: String,
    pub source_url: Option<String>,
    pub license_note: Option<String>,
    pub download: DownloadInfo,
}

#[derive(Debug, Deserialize)]
pub struct CatalogFile {
    pub schema_version: u32,
    /// Publication date of the catalog. Part of the wire format; not yet
    /// surfaced in the UI, which reports its own last-sync time instead.
    #[serde(default)]
    #[allow(dead_code)]
    pub updated: Option<String>,
    /// Keyed by runtime id (`dosbox`, `scummvm`). Optional so a catalog written
    /// before runtimes existed still parses.
    #[serde(default)]
    pub runtimes: std::collections::HashMap<String, RuntimeSpec>,
    pub games: Vec<CatalogGame>,
}

/// Filter passed from the UI to narrow a catalog listing. All fields optional;
/// `None` means "no constraint".
#[derive(Debug, Default, Deserialize)]
pub struct CatalogFilter {
    pub platform: Option<String>,
    pub runtime: Option<String>,
    pub license: Option<String>,
    pub search: Option<String>,
}

/// Outcome of a sync, surfaced in the UI so users can see whether they are
/// looking at live or bundled data.
#[derive(Debug, Serialize, Clone)]
pub struct SyncResult {
    /// `"remote"` or `"bundled"`.
    pub source: String,
    pub entry_count: usize,
    pub synced_at: String,
    /// Why the remote fetch was not used, when it wasn't.
    pub fallback_reason: Option<String>,
}

#[derive(Debug)]
pub enum CatalogError {
    Network(String),
    Parse(String),
    UnsupportedVersion { found: u32, supported: u32 },
}

impl std::fmt::Display for CatalogError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            CatalogError::Network(m) => write!(f, "network error: {m}"),
            CatalogError::Parse(m) => write!(f, "malformed catalog: {m}"),
            CatalogError::UnsupportedVersion { found, supported } => write!(
                f,
                "catalog schema_version {found} is newer than supported version {supported}"
            ),
        }
    }
}

fn validate(file: CatalogFile) -> Result<CatalogFile, CatalogError> {
    if file.schema_version > SUPPORTED_SCHEMA_VERSION {
        return Err(CatalogError::UnsupportedVersion {
            found: file.schema_version,
            supported: SUPPORTED_SCHEMA_VERSION,
        });
    }
    Ok(file)
}

/// Fetch the published catalog. Times out quickly — a slow network should fall
/// back to bundled data, not stall the app.
pub async fn fetch_remote(url: &str) -> Result<CatalogFile, CatalogError> {
    let client = reqwest::Client::builder()
        .connect_timeout(std::time::Duration::from_secs(5))
        .timeout(std::time::Duration::from_secs(15))
        .user_agent(concat!("Librebox/", env!("CARGO_PKG_VERSION")))
        .build()
        .map_err(|e| CatalogError::Network(e.to_string()))?;

    let res = client
        .get(url)
        .send()
        .await
        .map_err(|e| CatalogError::Network(e.to_string()))?;

    if !res.status().is_success() {
        return Err(CatalogError::Network(format!("HTTP {}", res.status())));
    }

    let body = res
        .text()
        .await
        .map_err(|e| CatalogError::Network(e.to_string()))?;

    let file: CatalogFile =
        serde_json::from_str(&body).map_err(|e| CatalogError::Parse(e.to_string()))?;
    validate(file)
}

/// The copy compiled into the binary. Only fails if the shipped file is itself
/// broken, which the catalog linter exists to prevent.
pub fn load_bundled() -> Result<CatalogFile, CatalogError> {
    let file: CatalogFile =
        serde_json::from_str(BUNDLED).map_err(|e| CatalogError::Parse(e.to_string()))?;
    validate(file)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn bundled_catalog_parses() {
        let file = load_bundled().expect("bundled catalog must parse");
        assert_eq!(file.schema_version, SUPPORTED_SCHEMA_VERSION);
        assert!(!file.games.is_empty(), "bundled catalog must not be empty");
    }

    #[test]
    fn bundled_catalog_is_well_formed() {
        let file = load_bundled().unwrap();
        let mut ids = std::collections::HashSet::new();
        for g in &file.games {
            assert!(ids.insert(&g.id), "duplicate catalog id: {}", g.id);
            assert!(!g.download.url.is_empty(), "{} has no download url", g.id);
            assert!(
                matches!(g.runtime.as_str(), "dosbox" | "scummvm" | "native" | "86box"),
                "{} has unknown runtime {}",
                g.id,
                g.runtime
            );
            assert!(
                matches!(
                    g.license.as_str(),
                    "freeware" | "shareware" | "open-source" | "public-domain"
                ),
                "{} has unknown license {}",
                g.id,
                g.license
            );
        }
    }

    #[test]
    fn rejects_newer_schema_version() {
        let json = r#"{"schema_version": 999, "games": []}"#;
        let file: CatalogFile = serde_json::from_str(json).unwrap();
        assert!(matches!(
            validate(file),
            Err(CatalogError::UnsupportedVersion { .. })
        ));
    }
}
