#!/usr/bin/env python3
"""Create a reproducible Horizon Off-Roader transfer bundle and 1.21.4 pack."""
import importlib.util
import json
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / 'paper-vehicles'
spec = importlib.util.spec_from_file_location('compile_go_kart', PAPER / 'tools/compile_go_kart.py')
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)
PARTS = ('off_roader_body', 'wheel_sports', 'wheel_standard', 'go_kart_steering_wheel')
LAYOUT = {
    'units': 'blocks', 'axes': 'Horizon local, +Z forward, +Y up; verify target yaw convention',
    'body': {'model': 'off_roader_body', 'scale': [1.42, 1.38, 1.42], 'center': [0, 0.69, 0]},
    'wheel_model_default': 'wheel_sports',
    'wheel_scale': [1.55, 1.56, 1.56],
    'wheels': [{'pivot': [x, 0.390, z], 'steers': z > 0} for z in (14.5 * 1.42 / 16, -14.5 * 1.42 / 16) for x in (14.74 / 16, -14.74 / 16)],
    'steering': {'model': 'go_kart_steering_wheel', 'pivot': [6.816 / 16, 17.30 / 16, 4.45 / 16], 'scale': [1.16] * 3, 'tilt_degrees': 32},
    'spare': {'model': 'wheel_sports', 'pivot': [0, 14.8 / 16, -34.6 / 16], 'scale': [1.24, 1.32, 1.32], 'rotation_y_degrees': 90},
    'driver_seat_attach_horizon_only': [6.816 / 16, 9.108 / 16, -3.550 / 16],
    'step_height': 1.06, 'fuel_mb': 4000,
}

def add(archive, name, data):
    info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, data)

def build(destination):
    converter.PARTS = PARTS
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='off-roader-transfer-') as tmp:
        pack = Path(tmp) / 'paper-resource-pack.zip'
        descriptor = converter.build_zip(pack)
        assets = ROOT / 'content/assets/gokart'
        textures = set()
        with zipfile.ZipFile(destination, 'w') as archive:
            add(archive, 'README.md', (PAPER / 'transfer/off-roader/README.md').read_bytes())
            add(archive, 'LICENSE.txt', (ROOT / 'LICENSE').read_bytes())
            add(archive, 'paper-resource-pack.zip', pack.read_bytes())
            add(archive, 'source/runtime-layout.json', json.dumps(LAYOUT, indent=2).encode() + b'\n')
            for part in PARTS:
                data = (assets / 'models/block' / (part + '.json')).read_bytes()
                add(archive, 'source/models/' + part + '.json', data)
                textures.update(ref.split('/')[-1] for ref in json.loads(data)['textures'].values())
            for texture in sorted(textures):
                add(archive, 'source/textures/' + texture + '.png', (assets / 'textures/block' / (texture + '.png')).read_bytes())
        return descriptor

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    desc = build(parser.parse_args().output)
    for name, groups in desc['parts'].items():
        print(f"{name}: {sum(g['element_count'] for g in groups)} elements, {len(groups)} display groups")
