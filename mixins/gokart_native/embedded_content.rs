// Extracts the embedded `gokart-content.hmod` once to `.horizon-cache/` and passes it as a dev content mod,
// so `gokart_native.hnmod` works as a single self-contained file without needing a separate `.hmod` install.
fn gokart_embedded_content(
    root: &std::path::Path,
    enabled: &std::collections::BTreeSet<String>,
    disabled: &std::collections::BTreeSet<String>,
    dev: &[std::path::PathBuf],
) -> core::ops::ControlFlow<std::path::PathBuf> {
    if disabled.contains("gokart") {
        return core::ops::ControlFlow::Continue(());
    }
    static CONTENT: &[u8] = horizon_client::native_data!("gokart_native", "gokart-content.hmod");
    let dir = std::env::current_dir().unwrap_or_default().join(".horizon-cache");
    let file = dir.join("gokart-embedded-content.hmod");
    if dev.contains(&file) {
        return core::ops::ControlFlow::Continue(());
    }
    let same = std::fs::read(&file).is_ok_and(|on_disk| on_disk == CONTENT);
    if !same
        && std::fs::create_dir_all(&dir)
            .and_then(|()| std::fs::write(&file, CONTENT))
            .is_err()
    {
        log::warn!("Go-Kart: embedded content could not be written to {}", file.display());
        return core::ops::ControlFlow::Continue(());
    }
    let mut with = dev.to_vec();
    with.push(file);
    core::ops::ControlFlow::Break(content_root(root, enabled, disabled, &with))
}
