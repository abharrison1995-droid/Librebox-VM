//! Download, verify, and extract a catalog game onto disk.
//!
//! The flow is deliberately conservative: bytes land in a `.part` file, the
//! hash is checked before anything is unpacked, extraction goes to a temp
//! directory, and only a successful extraction is renamed into place. At no
//! point does a failed install leave something that looks installed.

use futures_util::StreamExt;
use sha2::{Digest, Sha256};
use std::io::Read;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::{Duration, Instant};
use tokio::io::AsyncWriteExt;

/// Minimum gap between progress callbacks. A 1 GB download produces tens of
/// thousands of chunks; emitting an IPC event for each would swamp the webview.
const PROGRESS_INTERVAL: Duration = Duration::from_millis(250);

#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize)]
#[serde(rename_all = "lowercase")]
pub enum InstallPhase {
    Downloading,
    Verifying,
    Extracting,
}

#[derive(Debug)]
pub enum InstallError {
    Cancelled,
    Network(String),
    Io(String),
    /// The downloaded bytes did not match the catalog's recorded hash.
    ChecksumMismatch { expected: String, actual: String },
    /// The archive format is not one we can unpack (e.g. an .exe installer).
    UnsupportedFormat(String),
    /// The archive unpacked, but the executable the catalog names is not in it.
    ExecutableNotFound(String),
    /// A zip entry tried to escape the destination directory.
    UnsafeArchive(String),
}

impl std::fmt::Display for InstallError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            InstallError::Cancelled => write!(f, "cancelled"),
            InstallError::Network(m) => write!(f, "download failed: {m}"),
            InstallError::Io(m) => write!(f, "file error: {m}"),
            InstallError::ChecksumMismatch { expected, actual } => write!(
                f,
                "checksum mismatch: expected {}…, got {}…",
                &expected[..expected.len().min(12)],
                &actual[..actual.len().min(12)]
            ),
            InstallError::UnsupportedFormat(fmt) => write!(
                f,
                "'{fmt}' downloads cannot be installed automatically yet — this title needs manual installation"
            ),
            InstallError::ExecutableNotFound(exe) => {
                write!(f, "could not find {exe} anywhere in the archive")
            }
            InstallError::UnsafeArchive(entry) => {
                write!(f, "archive contains an unsafe path: {entry}")
            }
        }
    }
}

impl std::error::Error for InstallError {}

fn io<E: std::fmt::Display>(e: E) -> InstallError {
    InstallError::Io(e.to_string())
}

/// Formats we can unpack. Anything else is refused up front rather than
/// downloaded and then found to be uninstallable.
pub fn is_supported_format(format: Option<&str>) -> bool {
    matches!(format, Some("zip"))
}

/// Streams `url` into `dest`, reporting progress at most every
/// [`PROGRESS_INTERVAL`]. Checks `cancel` on every chunk so a cancelled
/// download stops promptly rather than at the end of the transfer.
///
/// On cancellation or error the partial file is removed by the caller — see
/// [`install`], which owns the cleanup.
pub async fn download_to_file<F>(
    url: &str,
    dest: &Path,
    cancel: &AtomicBool,
    mut on_progress: F,
) -> Result<u64, InstallError>
where
    F: FnMut(u64, Option<u64>),
{
    let client = reqwest::Client::builder()
        .connect_timeout(Duration::from_secs(15))
        .user_agent(concat!("Librebox/", env!("CARGO_PKG_VERSION")))
        .build()
        .map_err(|e| InstallError::Network(e.to_string()))?;

    let res = client
        .get(url)
        .send()
        .await
        .map_err(|e| InstallError::Network(e.to_string()))?;

    if !res.status().is_success() {
        return Err(InstallError::Network(format!("HTTP {}", res.status())));
    }

    // Prefer what the server reports over the catalog's recorded size; the
    // catalog can be stale and this only drives the progress bar.
    let total = res.content_length();

    if let Some(parent) = dest.parent() {
        tokio::fs::create_dir_all(parent).await.map_err(io)?;
    }
    let mut file = tokio::fs::File::create(dest).await.map_err(io)?;

    let mut downloaded: u64 = 0;
    let mut last_emit = Instant::now();
    on_progress(0, total);

    let mut stream = res.bytes_stream();
    while let Some(chunk) = stream.next().await {
        if cancel.load(Ordering::Relaxed) {
            return Err(InstallError::Cancelled);
        }
        let chunk = chunk.map_err(|e| InstallError::Network(e.to_string()))?;
        file.write_all(&chunk).await.map_err(io)?;
        downloaded += chunk.len() as u64;

        if last_emit.elapsed() >= PROGRESS_INTERVAL {
            on_progress(downloaded, total);
            last_emit = Instant::now();
        }
    }

    file.flush().await.map_err(io)?;
    on_progress(downloaded, total);
    Ok(downloaded)
}

/// Hashes a file in 64 KiB blocks. Runs on the blocking pool because it is
/// CPU-bound and files can be over a gigabyte.
pub async fn verify_sha256(path: &Path, expected: &str) -> Result<(), InstallError> {
    let path = path.to_path_buf();
    let expected = expected.to_ascii_lowercase();

    tokio::task::spawn_blocking(move || {
        let mut file = std::fs::File::open(&path).map_err(io)?;
        let mut hasher = Sha256::new();
        let mut buf = vec![0u8; 64 * 1024];
        loop {
            let n = file.read(&mut buf).map_err(io)?;
            if n == 0 {
                break;
            }
            hasher.update(&buf[..n]);
        }
        let actual = format!("{:x}", hasher.finalize());
        if actual == expected {
            Ok(())
        } else {
            Err(InstallError::ChecksumMismatch { expected, actual })
        }
    })
    .await
    .map_err(io)?
}

/// Unpacks a zip into `dest`.
///
/// Rejects any entry whose path escapes the destination — the catalog pulls
/// archives from third-party hosts, and naive extraction of a crafted zip can
/// write anywhere on disk ("zip slip"). `enclosed_name` returns `None` for
/// absolute paths and anything containing `..`, which is exactly the check we
/// want; we treat that as fatal rather than skipping the entry silently.
pub async fn extract_zip(archive: &Path, dest: &Path) -> Result<(), InstallError> {
    let archive = archive.to_path_buf();
    let dest = dest.to_path_buf();

    tokio::task::spawn_blocking(move || {
        let file = std::fs::File::open(&archive).map_err(io)?;
        let mut zip = zip::ZipArchive::new(file)
            .map_err(|e| InstallError::UnsupportedFormat(format!("not a readable zip: {e}")))?;

        std::fs::create_dir_all(&dest).map_err(io)?;

        for i in 0..zip.len() {
            let mut entry = zip.by_index(i).map_err(io)?;

            let relative = match entry.enclosed_name() {
                Some(p) => p.to_path_buf(),
                None => return Err(InstallError::UnsafeArchive(entry.name().to_string())),
            };
            let out = dest.join(&relative);

            // Belt and braces: confirm the joined path really is inside dest.
            if !out.starts_with(&dest) {
                return Err(InstallError::UnsafeArchive(entry.name().to_string()));
            }

            if entry.is_dir() {
                std::fs::create_dir_all(&out).map_err(io)?;
                continue;
            }
            if let Some(parent) = out.parent() {
                std::fs::create_dir_all(parent).map_err(io)?;
            }
            let mut writer = std::fs::File::create(&out).map_err(io)?;
            std::io::copy(&mut entry, &mut writer).map_err(io)?;
        }
        Ok(())
    })
    .await
    .map_err(io)?
}

/// Finds `filename` anywhere under `root`, comparing case-insensitively, and
/// returns its path relative to `root`.
///
/// The catalog records executables as bare filenames (`"DOOM.EXE"`) but archives
/// are inconsistent about whether the game sits at the root or inside a
/// subdirectory. Resolving this at install time means the launcher never has to
/// guess, and a mismatch surfaces now rather than on first play.
pub fn resolve_executable(root: &Path, filename: &str) -> Option<PathBuf> {
    fn walk(dir: &Path, target: &str, depth: usize) -> Option<PathBuf> {
        if depth > 8 {
            return None;
        }
        let entries = std::fs::read_dir(dir).ok()?;
        let mut subdirs = Vec::new();

        // Prefer a match in the current directory before descending, so a
        // shallower hit wins over a deeper one.
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                subdirs.push(path);
            } else if path
                .file_name()
                .and_then(|n| n.to_str())
                .is_some_and(|n| n.eq_ignore_ascii_case(target))
            {
                return Some(path);
            }
        }
        subdirs.sort();
        subdirs.iter().find_map(|d| walk(d, target, depth + 1))
    }

    walk(root, filename, 0).and_then(|abs| {
        abs.strip_prefix(root)
            .ok()
            .map(|rel| rel.to_path_buf())
    })
}

/// Replaces `dest` with `src`, removing any previous install first.
///
/// Separated so the caller can do all the fallible work in a temp location and
/// only touch the real install directory at the very end.
pub fn promote(src: &Path, dest: &Path) -> Result<(), InstallError> {
    if dest.exists() {
        std::fs::remove_dir_all(dest).map_err(io)?;
    }
    if let Some(parent) = dest.parent() {
        std::fs::create_dir_all(parent).map_err(io)?;
    }
    // rename fails across volumes; both paths live under app_data_dir so this
    // is a same-volume move in practice.
    std::fs::rename(src, dest).map_err(io)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use std::sync::Arc;

    fn zip_with(entries: &[(&str, &[u8])]) -> (tempfile::TempDir, PathBuf) {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("test.zip");
        let file = std::fs::File::create(&path).unwrap();
        let mut w = zip::ZipWriter::new(file);
        let opts: zip::write::FileOptions<()> = zip::write::FileOptions::default();
        for (name, body) in entries {
            w.start_file(*name, opts).unwrap();
            w.write_all(body).unwrap();
        }
        w.finish().unwrap();
        (dir, path)
    }

    #[test]
    fn supported_formats() {
        assert!(is_supported_format(Some("zip")));
        assert!(!is_supported_format(Some("exe")));
        assert!(!is_supported_format(Some("7z")));
        assert!(!is_supported_format(None));
    }

    #[tokio::test]
    async fn extracts_a_flat_zip() {
        let (_d, archive) = zip_with(&[("DOOM.EXE", b"mz"), ("README.TXT", b"hi")]);
        let out = tempfile::tempdir().unwrap();
        extract_zip(&archive, out.path()).await.unwrap();
        assert!(out.path().join("DOOM.EXE").exists());
        assert!(out.path().join("README.TXT").exists());
    }

    #[tokio::test]
    async fn extracts_a_nested_zip() {
        let (_d, archive) = zip_with(&[("doom1/DOOM.EXE", b"mz")]);
        let out = tempfile::tempdir().unwrap();
        extract_zip(&archive, out.path()).await.unwrap();
        assert!(out.path().join("doom1").join("DOOM.EXE").exists());
    }

    #[tokio::test]
    async fn rejects_zip_slip() {
        // An entry escaping the destination must abort the whole extraction.
        let (_d, archive) = zip_with(&[("../evil.txt", b"pwned")]);
        let out = tempfile::tempdir().unwrap();
        let err = extract_zip(&archive, out.path()).await.unwrap_err();
        assert!(
            matches!(err, InstallError::UnsafeArchive(_)),
            "expected UnsafeArchive, got {err:?}"
        );
        assert!(!out.path().parent().unwrap().join("evil.txt").exists());
    }

    #[tokio::test]
    async fn rejects_a_non_zip() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("not.zip");
        std::fs::write(&path, b"this is not a zip file").unwrap();
        let out = tempfile::tempdir().unwrap();
        assert!(matches!(
            extract_zip(&path, out.path()).await.unwrap_err(),
            InstallError::UnsupportedFormat(_)
        ));
    }

    #[test]
    fn resolves_executable_at_root() {
        let dir = tempfile::tempdir().unwrap();
        std::fs::write(dir.path().join("DOOM.EXE"), b"").unwrap();
        assert_eq!(
            resolve_executable(dir.path(), "DOOM.EXE").unwrap(),
            PathBuf::from("DOOM.EXE")
        );
    }

    #[test]
    fn resolves_executable_in_a_subdirectory() {
        let dir = tempfile::tempdir().unwrap();
        let sub = dir.path().join("doom1");
        std::fs::create_dir_all(&sub).unwrap();
        std::fs::write(sub.join("DOOM.EXE"), b"").unwrap();
        assert_eq!(
            resolve_executable(dir.path(), "DOOM.EXE").unwrap(),
            PathBuf::from("doom1").join("DOOM.EXE")
        );
    }

    #[test]
    fn resolves_executable_case_insensitively() {
        // Archive.org zips are wildly inconsistent about casing.
        let dir = tempfile::tempdir().unwrap();
        std::fs::write(dir.path().join("doom.exe"), b"").unwrap();
        assert!(resolve_executable(dir.path(), "DOOM.EXE").is_some());
    }

    #[test]
    fn prefers_a_shallower_match() {
        let dir = tempfile::tempdir().unwrap();
        let sub = dir.path().join("extras");
        std::fs::create_dir_all(&sub).unwrap();
        std::fs::write(sub.join("DOOM.EXE"), b"").unwrap();
        std::fs::write(dir.path().join("DOOM.EXE"), b"").unwrap();
        assert_eq!(
            resolve_executable(dir.path(), "DOOM.EXE").unwrap(),
            PathBuf::from("DOOM.EXE")
        );
    }

    #[test]
    fn missing_executable_is_none() {
        let dir = tempfile::tempdir().unwrap();
        std::fs::write(dir.path().join("README.TXT"), b"").unwrap();
        assert!(resolve_executable(dir.path(), "DOOM.EXE").is_none());
    }

    #[tokio::test]
    async fn verifies_a_correct_hash() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("f.bin");
        std::fs::write(&path, b"hello").unwrap();
        // sha256("hello")
        let expected = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824";
        verify_sha256(&path, expected).await.unwrap();
    }

    #[tokio::test]
    async fn rejects_a_wrong_hash() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("f.bin");
        std::fs::write(&path, b"tampered").unwrap();
        let err = verify_sha256(&path, &"a".repeat(64)).await.unwrap_err();
        assert!(matches!(err, InstallError::ChecksumMismatch { .. }));
    }

    #[tokio::test]
    async fn hash_check_is_case_insensitive() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("f.bin");
        std::fs::write(&path, b"hello").unwrap();
        let upper = "2CF24DBA5FB0A30E26E83B2AC5B9E29E1B161E5C1FA7425E73043362938B9824";
        verify_sha256(&path, upper).await.unwrap();
    }

    #[tokio::test]
    async fn cancellation_stops_the_download() {
        let cancel = Arc::new(AtomicBool::new(true));
        let dir = tempfile::tempdir().unwrap();
        let dest = dir.path().join("out.bin");
        // Already-cancelled: the very first chunk check should bail. Uses a
        // real but tiny request so we exercise the actual code path.
        let err = download_to_file(
            "https://archive.org/download/Bs-aog-sw1/bstone.zip",
            &dest,
            &cancel,
            |_, _| {},
        )
        .await;
        assert!(matches!(err, Err(InstallError::Cancelled)), "got {err:?}");
    }

    /// The whole pipeline against a real catalog entry: download, verify the
    /// hash recorded in catalog.json, extract, and locate the executable the
    /// catalog names. Network-bound, so it is opt-in:
    ///
    ///   cargo test --lib -- --ignored real_
    #[tokio::test]
    #[ignore = "hits the network"]
    async fn real_install_of_the_smallest_catalog_entry() {
        let bundled = crate::catalog::load_bundled().unwrap();
        let entry = bundled
            .games
            .iter()
            .filter(|g| g.runtime == "dosbox" && g.download.format.as_deref() == Some("zip"))
            .min_by_key(|g| g.download.size_bytes.unwrap_or(i64::MAX))
            .expect("catalog must contain a zipped dosbox game");

        let sha = entry
            .download
            .sha256
            .as_deref()
            .expect("entry must have a hash by now");
        let exe = entry.runtime_config["executable"].as_str().unwrap();
        eprintln!("installing {} ({} bytes)", entry.id, entry.download.size_bytes.unwrap_or(0));

        let dir = tempfile::tempdir().unwrap();
        let part = dir.path().join("game.part");
        let staging = dir.path().join("staging");
        let cancel = AtomicBool::new(false);

        let mut ticks = 0;
        let bytes = download_to_file(&entry.download.url, &part, &cancel, |_, _| ticks += 1)
            .await
            .expect("download should succeed");
        assert!(bytes > 0);

        verify_sha256(&part, sha)
            .await
            .expect("the catalog's recorded hash must match what the server serves");

        extract_zip(&part, &staging).await.expect("should extract");

        let found = resolve_executable(&staging, exe)
            .unwrap_or_else(|| panic!("{exe} not found in the {} archive", entry.id));
        eprintln!("resolved {exe} -> {}", found.display());
        assert!(staging.join(&found).exists());
    }

    #[test]
    fn promote_replaces_an_existing_install() {
        let root = tempfile::tempdir().unwrap();
        let src = root.path().join("staged");
        let dest = root.path().join("final");
        std::fs::create_dir_all(&src).unwrap();
        std::fs::write(src.join("new.txt"), b"new").unwrap();
        std::fs::create_dir_all(&dest).unwrap();
        std::fs::write(dest.join("old.txt"), b"old").unwrap();

        promote(&src, &dest).unwrap();
        assert!(dest.join("new.txt").exists());
        assert!(!dest.join("old.txt").exists(), "stale files must not survive");
        assert!(!src.exists());
    }
}
