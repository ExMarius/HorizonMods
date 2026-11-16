// Extracts the embedded `gokart-content.hmod` once to `.horizon-cache/` and passes it as a dev content mod,
// so `gokart_native.hnmod` works as a single self-contained file without needing a separate `.hmod` install.
// If `mods/gokart-content.hmod` exists on disk, it takes priority so 3D model/texture/sound updates apply
// on simple game restart with ZERO Rust rebuild!
fn gokart_embedded_content(
    root: &std::path::Path,
    enabled: &std::collections::BTreeSet<String>,
    disabled: &std::collections::BTreeSet<String>,
    dev: &[std::path::PathBuf],
) -> core::ops::ControlFlow<std::path::PathBuf> {
    if disabled.contains("gokart") {
        return core::ops::ControlFlow::Continue(());
    }
    let cwd = std::env::current_dir().unwrap_or_default();
    let override_file = cwd.join("mods").join("gokart-content.hmod");
    let dir = cwd.join(".horizon-cache");
    let cache_file = dir.join("gokart-embedded-content.hmod");
    if dev.contains(&override_file) || dev.contains(&cache_file) {
        return core::ops::ControlFlow::Continue(());
    }
    let chosen = if override_file.is_file() {
        override_file
    } else {
        static CONTENT: &[u8] = horizon_client::native_data!("gokart_native", "gokart-content.hmod");
        let same = std::fs::read(&cache_file).is_ok_and(|on_disk| on_disk == CONTENT);
        if !same
            && std::fs::create_dir_all(&dir)
                .and_then(|()| std::fs::write(&cache_file, CONTENT))
                .is_err()
        {
            log::warn!("Go-Kart: embedded content could not be written to {}", cache_file.display());
            return core::ops::ControlFlow::Continue(());
        }
        cache_file
    };
    let mut with = dev.to_vec();
    with.push(chosen);
    core::ops::ControlFlow::Break(content_root(root, enabled, disabled, &with))
}
