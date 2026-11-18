#!/usr/bin/env python3
"""Experimental OBJ-to-vanilla model conversion for the MIT City Vehicles bus.

Each non-degenerate face is projected into a planar Minecraft element. Faces
with the same normal share one item model and therefore one display entity.
Textures are baked from source UVs, including polygon alpha, without rotating
or snapping the original shape. The output requires a future Paper display
renderer to apply each group's basis and scale; it is NOT a playable vehicle.
"""
import argparse
import json
import math
import tempfile
import zipfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'asset-src/city_bus'
UNIT = 3.5  # model texels per source unit, keeping vanilla coordinates in bounds
PIXELS = 48  # per-face texture preview; not a pixel-perfect atlas conversion


def dot(a, b): return sum(x*y for x, y in zip(a, b))
def sub(a, b): return tuple(x-y for x, y in zip(a, b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def norm(a):
    length = math.sqrt(dot(a, a))
    return tuple(x / length for x in a) if length > 1e-10 else None


def parse_obj(path):
    vertices, uvs, faces = [], [], []
    for line in path.read_text(encoding='utf-8').splitlines():
        fields = line.split()
        if not fields: continue
        if fields[0] == 'v': vertices.append(tuple(map(float, fields[1:4])))
        elif fields[0] == 'vt': uvs.append(tuple(map(float, fields[1:3])))
        elif fields[0] == 'f':
            refs = [part.split('/') for part in fields[1:]]
            if not all(len(ref) >= 2 and ref[0] and ref[1] and int(ref[0]) > 0 and int(ref[1]) > 0 for ref in refs):
                raise ValueError('OBJ faces must have positive vertex and UV indices')
            faces.append([(vertices[int(ref[0])-1], uvs[int(ref[1])-1]) for ref in refs])
    return faces


def basis(face):
    origin = face[0][0]
    normal = None
    for i in range(1, len(face)-1):
        normal = norm(cross(sub(face[i][0], origin), sub(face[i+1][0], origin)))
        if normal: break
    if normal is None: return None
    # Canonicalize opposite normals to reuse models; reverse face direction separately.
    side = 1
    for component in normal:
        if abs(component) > 1e-5:
            if component < 0:
                normal = tuple(-v for v in normal)
                side = -1
            break
    key = tuple(round(x, 4) for x in normal)
    normal = norm(key)
    ref = (0, 1, 0) if abs(normal[1]) < 0.9 else (1, 0, 0)
    u = norm(cross(ref, normal))
    v = cross(normal, u)
    return key, u, v, normal, side


def bake(face, coords, image):
    min_x, max_x = min(p[0] for p in coords), max(p[0] for p in coords)
    min_y, max_y = min(p[1] for p in coords), max(p[1] for p in coords)
    if max_x-min_x < 1e-8 or max_y-min_y < 1e-8: return None
    out = Image.new('RGBA', (PIXELS, PIXELS), (0, 0, 0, 0))
    pix = out.load()
    src = image.load()
    mapped = [((x-min_x)/(max_x-min_x), (max_y-y)/(max_y-min_y)) for x, y, _ in coords]
    for j in range(PIXELS):
        for i in range(PIXELS):
            point = ((i + 0.5)/PIXELS, (j + 0.5)/PIXELS)
            for t in range(1, len(face)-1):
                ia, ib, ic = 0, t, t+1
                a, b, c = mapped[ia], mapped[ib], mapped[ic]
                den = (b[1]-c[1])*(a[0]-c[0]) + (c[0]-b[0])*(a[1]-c[1])
                if abs(den) < 1e-12: continue
                wa = ((b[1]-c[1])*(point[0]-c[0]) + (c[0]-b[0])*(point[1]-c[1])) / den
                wb = ((c[1]-a[1])*(point[0]-c[0]) + (a[0]-c[0])*(point[1]-c[1])) / den
                wc = 1-wa-wb
                if min(wa, wb, wc) < -1e-8: continue
                uv = tuple(wa*face[ia][1][k] + wb*face[ib][1][k] + wc*face[ic][1][k] for k in range(2))
                x = max(0, min(image.width-1, int(uv[0]*image.width)))
                y = max(0, min(image.height-1, int((1-uv[1])*image.height)))
                pix[i, j] = src[x, y]
                break
    return out


def compile_mesh(mesh, texture, output, name):
    models = output / 'assets/horizonvehicles/models/item'
    items = output / 'assets/horizonvehicles/items'
    textures = output / 'assets/horizonvehicles/textures/item'
    for path in (models, items, textures): path.mkdir(parents=True, exist_ok=True)
    groups = {}
    image = Image.open(texture).convert('RGBA')
    total, skipped = 0, 0
    for face in parse_obj(mesh):
        total += 1
        b = basis(face)
        if not b: skipped += 1; continue
        key, u, v, n, side = b
        coords = [(dot(point, u), dot(point, v), dot(point, n)) for point, uv in face]
        if max(c[2] for c in coords)-min(c[2] for c in coords) > .002:
            raise ValueError(f'Nonplanar face {total} in {mesh}')
        baked = bake(face, coords, image)
        if baked is None: skipped += 1; continue
        if key not in groups:
            groups[key] = {'index': len(groups), 'u': u, 'v': v, 'normal': n, 'elements': [], 'textures': {}}
        group = groups[key]
        face_name = f'{name}_face_{total:04}'
        baked.save(textures / (face_name + '.png'), optimize=True)
        lo = [min(c[i] for c in coords) * UNIT + 8 for i in range(3)]
        hi = [max(c[i] for c in coords) * UNIT + 8 for i in range(3)]
        # Quads project to a mathematical plane; use the mean to avoid precision gaps.
        lo[2] = hi[2] = sum(c[2] for c in coords)/len(coords)*UNIT+8
        if min(lo) < -16 or max(hi) > 32: raise ValueError(f'Face {total} exceeds vanilla element bounds')
        element = {'from': [round(v, 5) for v in lo], 'to': [round(v, 5) for v in hi],
                   'faces': {('south' if side > 0 else 'north'): {'uv': [0, 0, 16, 16], 'texture': '#' + face_name}}}
        group['elements'].append(element)
        group['textures'][face_name] = 'horizonvehicles:item/' + face_name
    parts = []
    for group in groups.values():
        part = f'{name}_part_{group["index"]:02}'
        (models / (part + '.json')).write_text(json.dumps({'textures': group['textures'], 'elements': group['elements']}, separators=(',', ':')))
        (items / (part + '.json')).write_text(json.dumps({'model': {'type': 'minecraft:model', 'model': 'horizonvehicles:item/' + part}}))
        parts.append({'item_model': 'horizonvehicles:' + part, 'u': group['u'], 'v': group['v'], 'normal': group['normal']})
    return {'source_faces': total, 'skipped_degenerate_faces': skipped, 'parts': parts}


def build(output):
    output.mkdir(parents=True, exist_ok=True)
    (output / 'pack.mcmeta').write_text(json.dumps({'pack': {'pack_format': 46, 'description': 'Experimental City Bus (MIT)'}}))
    (output / 'LICENSE-city-bus.txt').write_bytes((SRC / 'LICENSE').read_bytes())
    descriptor = {'status': 'experimental: not yet integrated or validated in game', 'units_per_source_unit': UNIT,
                  'body': compile_mesh(SRC/'bus.obj', SRC/'yellow_bus.png', output, 'city_bus'),
                  'wheel': compile_mesh(SRC/'bus_wheel.obj', SRC/'bus_wheel.png', output, 'city_bus_wheel')}
    (output / 'city_bus_parts.json').write_text(json.dumps(descriptor, indent=2))
    return descriptor


def build_zip(destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='city-bus-pack-') as temp:
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
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path, help='output .zip or empty output directory')
    args = parser.parse_args()
    if args.output.suffix == '.zip':
        info = build_zip(args.output)
    else:
        if args.output.exists() and any(args.output.iterdir()):
            parser.error('output directory must be empty')
        info = build(args.output)
    for name in ('body', 'wheel'):
        print(name, 'faces:', info[name]['source_faces'], 'skipped:', info[name]['skipped_degenerate_faces'], 'display groups:', len(info[name]['parts']))
