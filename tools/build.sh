#!/usr/bin/env bash
# Builds and packages the Horizon Go-Kart mod (`gokart_native.hnmod` + `gokart-content.hmod`).
#
# Usage:
#   ./tools/build.sh            # Run unit tests (if cargo is installed) + build deterministic .hmod and .hnmod
#   ./tools/build.sh package    # Package deterministic .hmod and .hnmod into dist/
#   ./tools/build.sh test       # Run standalone Rust unit tests (`cargo test`)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ACTION="${1:-all}"

run_tests() {
    if command -v cargo >/dev/null 2>&1; then
        echo "==> Running Go-Kart physics & codec unit tests (cargo test)..."
        cargo test
    else
        echo "==> Skipping cargo test (cargo not in PATH)."
    fi
}

package_all() {
    echo "==> Generating deterministic assets & translations..."
    python3 tools/generate_assets.py

    echo "==> Packaging content mod (.hmod) and native bundle (.hnmod)..."
    python3 - <<'PY'
import hashlib
import json
import zipfile
from pathlib import Path

root = Path(".").resolve()
compat = json.loads((root / "compatibility.json").read_text())
mixin_dir = root / "mixins" / "gokart_native"
content_dir = root / "content"
dist_dir = root / "dist"
dist_dir.mkdir(parents=True, exist_ok=True)
data_dir = mixin_dir / "data"
data_dir.mkdir(parents=True, exist_ok=True)

def write_deterministic_zip(out_path: Path, files: dict[str, bytes]) -> str:
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, payload in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            zf.writestr(info, payload)
    return hashlib.sha256(out_path.read_bytes()).hexdigest()

# 1. Build content `.hmod`
content_files: dict[str, bytes] = {}
for p in sorted(content_dir.rglob("*")):
    if p.is_file():
        rel = p.relative_to(content_dir).as_posix()
        content_files[rel] = p.read_bytes()

embedded_hmod = data_dir / "gokart-content.hmod"
dist_hmod = dist_dir / "gokart-content.hmod"
hmod_sha = write_deterministic_zip(embedded_hmod, content_files)
dist_hmod.write_bytes(embedded_hmod.read_bytes())

# 2. Build native `.hnmod` (exact `horizon-mods/native/tools/native.py` schema 1 format)
mod_id = "gokart_native"
version = "0.2.0"
native_manifest = {
    "schema": 1,
    "id": mod_id,
    "version": version,
    "game": compat["game"],
    "horizon": compat["horizon_revision"],
    "mixins": compat["horizon_mixins_revision"],
    "hooks": compat["hooks"],
}

hnmod_files: dict[str, bytes] = {
    "horizon-native.json": (json.dumps(native_manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"),
}
for p in sorted(mixin_dir.rglob("*")):
    if not p.is_file():
        continue
    rel = p.relative_to(mixin_dir)
    if p.suffix in (".rs", ".toml") or rel.parts[0] == "data":
        hnmod_files[f"mixins/{mod_id}/{rel.as_posix()}"] = p.read_bytes()

lic = root / "LICENSE"
if lic.is_file():
    hnmod_files.setdefault(f"mixins/{mod_id}/LICENSE", lic.read_bytes())

dist_hnmod = dist_dir / f"{mod_id}.hnmod"
hnmod_sha = write_deterministic_zip(dist_hnmod, hnmod_files)

print(json.dumps({
    "content_hmod": {
        "path": str(dist_hmod.relative_to(root)),
        "size_bytes": dist_hmod.stat().st_size,
        "sha256": hmod_sha,
    },
    "native_hnmod": {
        "path": str(dist_hnmod.relative_to(root)),
        "size_bytes": dist_hnmod.stat().st_size,
        "sha256": hnmod_sha,
    },
}, indent=2))
PY
}

case "$ACTION" in
    test)
        run_tests
        ;;
    package)
        package_all
        ;;
    all)
        run_tests
        package_all
        ;;
    *)
        echo "Usage: $0 [all|test|package]" >&2
        exit 1
        ;;
esac
