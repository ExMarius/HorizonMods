"""Adapt a Minecraft Automobility bus model as an unregistered Horizon prototype."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'third_party/city_vehicles'
BASE = ROOT / 'content/assets/gokart'


def export():
    text = (SRC / 'bus.obj').read_text(encoding='utf-8')
    out = ['# Original Minecraft Blockbench model by FoundationGames; MIT.',
           '# Rescaled for Horizon; see third_party/city_vehicles/README.md.',
           'mtllib prototype_city_bus.mtl']
    for line in text.splitlines():
        fields = line.split()
        if not fields or fields[0] in ('mtllib', 'usemtl'):
            continue
        if fields[0] == 'v':
            # The source faces -Z; our vehicle renderer uses +Z as forward.
            x, y, z = map(float, fields[1:4])
            out.append(f'v {0.5 - 0.60*x:.6f} {0.22 + 0.50*y:.6f} {0.5 - 0.35*z:.6f}')
        elif fields[0] in ('o', 'g'):
            out.append(line)
            out.append('usemtl bus')
        else:
            out.append(line)
    model_dir = BASE / 'models/block'
    (model_dir / 'prototype_city_bus.obj').write_text('\n'.join(out) + '\n')
    (model_dir / 'prototype_city_bus.mtl').write_text('newmtl bus\nmap_Kd #bus\n')
    tex_dir = BASE / 'textures/block'
    (tex_dir / 'prototype_city_bus.png').write_bytes((SRC / 'yellow_bus.png').read_bytes())
    model = {'loader': 'neoforge:obj', 'model': 'gokart:models/block/prototype_city_bus.obj',
             'flip_v': True, 'shade_quads': True,
             'textures': {'bus': 'gokart:block/prototype_city_bus'}}
    (model_dir / 'prototype_minibus_body.json').write_text(json.dumps(model, indent=2) + '\n')
