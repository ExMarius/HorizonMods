"""Adapt the MIT City Vehicles Minecraft bus as an unregistered prototype.

The wheels are baked in as a temporary visual reference, not animated.  The
transformation is uniform to retain the source geometry's proportions.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'third_party/city_vehicles'
BASE = ROOT / 'content/assets/gokart'
SCALE = 0.8
GROUND_OFFSET = 0.375
# Source positions from the yellow bus frame: forward 60, -41, -23 texels.
AXLES_Z = (-60 / 16, 41 / 16, 23 / 16)
TRACK_X = 15 / 16
HASHES = {
    'bus.obj': '672d583e07129cf148d2ed693ce586639e99d6871870d10247c4adae18fcfcf1',
    'bus_wheel.obj': 'd1a5576a7507fa9c792b8b6c7449491f2f6b4e66129daca0e5848c4a7eba2dde',
    'yellow_bus.png': 'fba9bbd450aa2984c18224d240e94c430b98ada2587b22260b4aaa9026d3718f',
    'bus_wheel.png': '24d20470f693323bdc7ed25fdb5b4323ad309e2ec4250e711d25dc4edcc996f6',
}


def export():
    for name, expected in HASHES.items():
        if hashlib.sha256((SRC / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Unexpected City Vehicles source asset: {name}')
    out = ['# FoundationGames City Vehicles, MIT; see third_party/city_vehicles.',
           '# Rescaled, rotated and assembled for a static WIP prototype.',
           'mtllib prototype_city_bus.mtl']
    counts = [0, 0, 0]

    def add_mesh(name, material, dx=0, dz=0, mirror=1):
        # OBJ face indices are local to each source file; rebase all three kinds.
        offsets = counts.copy()
        for line in (SRC / name).read_text(encoding='utf-8').splitlines():
            fields = line.split()
            if not fields or fields[0] in ('mtllib', 'usemtl'):
                continue
            tag = fields[0]
            if tag == 'v':
                x, y, z = map(float, fields[1:4])
                out.append(f'v {0.5-SCALE*(mirror*x+dx):.6f} {GROUND_OFFSET+SCALE*y:.6f} {0.5-SCALE*(mirror*z+dz):.6f}')
                counts[0] += 1
            elif tag == 'vn':
                x, y, z = map(float, fields[1:4])
                # Both transformations are rotations (180° about Y).
                out.append(f'vn {-mirror*x:.8f} {y:.8f} {-mirror*z:.8f}')
                counts[2] += 1
            elif tag == 'vt':
                out.append(line)
                counts[1] += 1
            elif tag == 'f':
                vertices = []
                for vertex in fields[1:]:
                    parts = vertex.split('/')
                    if any(p and int(p) <= 0 for p in parts):
                        raise ValueError('Relative OBJ indices are not supported')
                    vertices.append('/'.join(str(int(p) + offsets[i]) if p else '' for i, p in enumerate(parts)))
                out.append('f ' + ' '.join(vertices))
            elif tag in ('o', 'g'):
                out.append(line)
                out.append('usemtl ' + material)
            else:
                out.append(line)

    add_mesh('bus.obj', 'bus')
    for z in AXLES_Z:
        for x in (-TRACK_X, TRACK_X):
            add_mesh('bus_wheel.obj', 'wheel', x, z, 1 if x < 0 else -1)
    model_dir = BASE / 'models/block'
    (model_dir / 'prototype_city_bus.obj').write_text('\n'.join(out) + '\n')
    (model_dir / 'prototype_city_bus.mtl').write_text('newmtl bus\nmap_Kd #bus\nnewmtl wheel\nmap_Kd #wheel\n')
    tex_dir = BASE / 'textures/block'
    for source, target in [('yellow_bus.png', 'prototype_city_bus.png'),
                           ('bus_wheel.png', 'prototype_city_bus_wheel.png')]:
        (tex_dir / target).write_bytes((SRC / source).read_bytes())
    model = {'loader': 'neoforge:obj', 'model': 'gokart:models/block/prototype_city_bus.obj',
             'flip_v': True, 'shade_quads': True,
             'textures': {'bus': 'gokart:block/prototype_city_bus',
                          'wheel': 'gokart:block/prototype_city_bus_wheel'}}
    (model_dir / 'prototype_minibus_body.json').write_text(json.dumps(model, indent=2) + '\n')
