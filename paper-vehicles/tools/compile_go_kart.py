#!/usr/bin/env python3
"""Convert our Horizon Go-Kart models to split vanilla Paper item models.

Vanilla 1.21.4 only accepts 22.5-degree element rotations up to 45 degrees.
Instead of snapping angles, rotated cuboids are grouped by pivot and angle;
the future renderer must apply those exact rotations to their ItemDisplays.
This is a resource pack, not a driving or seat implementation.
"""
import copy
import json
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / 'content/assets/gokart'
PARTS = ('go_kart_body', 'wheel_standard', 'go_kart_steering_wheel', 'engine_iron')
LEGAL = {-45, -22.5, 0, 22.5, 45}


def build(output):
    output.mkdir(parents=True, exist_ok=True)
    modeldir = output / 'assets/horizonvehicles/models/item'
    itemdir = output / 'assets/horizonvehicles/items'
    texturedir = output / 'assets/horizonvehicles/textures/item'
    for path in (modeldir, itemdir, texturedir): path.mkdir(parents=True, exist_ok=True)
    (output / 'pack.mcmeta').write_text(json.dumps({'pack': {'pack_format': 46, 'description': 'Horizon Go-Kart development pack'}}))
    (output / 'LICENSE.txt').write_bytes((ROOT / 'LICENSE').read_bytes())
    descriptor = {'status': 'experimental, not playable', 'parts': {}}
    for name in PARTS:
        source = json.loads((ASSETS / 'models/block' / (name + '.json')).read_text())
        textures = {}
        for slot, ref in source['textures'].items():
            if not ref.startswith('gokart:block/'):
                raise ValueError(f'Unexpected texture: {ref}')
            texture = ref.split('/')[-1]
            (texturedir / (texture + '.png')).write_bytes((ASSETS / 'textures/block' / (texture + '.png')).read_bytes())
            textures[slot] = 'horizonvehicles:item/' + texture
        groups = {}
        for source_element in source['elements']:
            element = copy.deepcopy(source_element)
            element.pop('light_emission', None)  # vanilla item models do not provide this feature
            rotation = element.get('rotation')
            if rotation and float(rotation['angle']) not in LEGAL:
                if rotation.get('rescale', False): raise ValueError('Unsupported rotated rescale')
                key = (rotation['axis'], float(rotation['angle']), tuple(rotation['origin']))
                element.pop('rotation')
            else:
                key = None
            groups.setdefault(key, []).append(element)
        parts = []
        for index, (key, elements) in enumerate(groups.items()):
            part = f'{name}_part_{index:02}'
            if any(not -16 <= value <= 32 for e in elements for field in ('from', 'to') for value in e[field]):
                raise ValueError(f'Model {part} exceeds vanilla element bounds')
            model = {'textures': textures, 'elements': elements}
            (modeldir / (part + '.json')).write_text(json.dumps(model, separators=(',', ':')))
            item = {'model': {'type': 'minecraft:model', 'model': 'horizonvehicles:item/' + part,
                               'tints': [{'type': 'minecraft:constant', 'value': 0xFFFFFF}]}}
            (itemdir / (part + '.json')).write_text(json.dumps(item, separators=(',', ':')))
            parts.append({'item_model': 'horizonvehicles:' + part,
                          'rotation': None if key is None else {'axis': key[0], 'angle': key[1], 'origin': key[2]},
                          'element_count': len(elements)})
        descriptor['parts'][name] = parts
    (output / 'go_kart_parts.json').write_text(json.dumps(descriptor, indent=2))
    return descriptor


def build_zip(destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='go-kart-pack-') as temp:
        root = Path(temp)
        descriptor = build(root)
        with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(root.rglob('*')):
                if path.is_file():
                    info = zipfile.ZipInfo(path.relative_to(root).as_posix(), (1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    archive.writestr(info, path.read_bytes())
    return descriptor


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path, help='Output zip file')
    args = parser.parse_args()
    info = build_zip(args.output)
    for name, groups in info['parts'].items():
        print(name, 'elements:', sum(g['element_count'] for g in groups), 'groups:', len(groups))
