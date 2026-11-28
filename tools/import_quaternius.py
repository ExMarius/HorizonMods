"""Export the Quaternius CC0 sports-car body into Horizon's NeoForge OBJ loader.

Only the body is exported; the four animated in-game wheels remain separate.
The pinned GLB is local, so ordinary builds need no network or extra packages.
"""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'third_party/quaternius/sports_car.glb'
SHA256 = 'bbb1c718d2aaf5f4344e9fb2cd66d8332a998a515b09ddd4dfa14698d787124e'
COLORS = [0xF4F6F8, 0xF07618, 0xC846B8, 0x3AAFD9, 0xF8C628, 0x70C926,
          0xED80A6, 0x464C54, 0xA2A8B0, 0x189C9D, 0x8432B8, 0x2E54C4,
          0x825232, 0x2E7D32, 0xE03430, 0x22252A]


def export(write_png):
    blob = SOURCE.read_bytes()
    if hashlib.sha256(blob).hexdigest() != SHA256:
        raise ValueError('Unexpected Quaternius source model hash')
    magic, version, length = struct.unpack_from('<4sII', blob, 0)
    if (magic, version, length) != (b'glTF', 2, len(blob)):
        raise ValueError('Invalid GLB')
    json_len, json_type = struct.unpack_from('<I4s', blob, 12)
    assert json_type == b'JSON'
    doc = json.loads(blob[20:20 + json_len])
    offset = 20 + json_len
    bin_len, bin_type = struct.unpack_from('<I4s', blob, offset)
    assert bin_type == b'BIN\0'
    binary = blob[offset + 8:offset + 8 + bin_len]

    def accessor(index):
        acc = doc['accessors'][index]
        view = doc['bufferViews'][acc['bufferView']]
        kind = {5126: 'f', 5123: 'H', 5125: 'I'}[acc['componentType']]
        n = {'SCALAR': 1, 'VEC3': 3}[acc['type']]
        fmt = '<' + kind * n
        size = struct.calcsize(fmt)
        stride = view.get('byteStride', size)
        start = view.get('byteOffset', 0) + acc.get('byteOffset', 0)
        values = [struct.unpack_from(fmt, binary, start + i * stride) for i in range(acc['count'])]
        return values

    node = next(n for n in doc['nodes'] if n['name'] == 'SportsCar2_Cube.006')
    assert not any(k in node for k in ('matrix', 'scale', 'rotation', 'translation'))
    parts = doc['meshes'][node['mesh']]['primitives']
    out = ['# Quaternius Sports Car body, CC0; converted from the pinned GLB.',
           'mtllib quaternius_sport.mtl', 'vt 0.5 0.5']
    first = 1
    for part in parts:
        assert part['mode'] == 4
        positions = accessor(part['attributes']['POSITION'])
        faces = accessor(part['indices'])
        material = doc['materials'][part['material']]['name'].lower()
        assert material in ('white', 'windows', 'grey', 'headlights', 'taillights')
        out += ['o ' + material, 'usemtl ' + material]
        for x, y, z in positions:
            # Block units: match existing sedan wheel mounts and chassis scale.
            out.append(f'v {0.5 + x * 13.7 / 16:.6f} {(y * 13 + 0.6) / 16:.6f} {0.5 + (z * 11 + 0.715) / 16:.6f}')
        for i in range(0, len(faces), 3):
            a, b, c = (first + faces[i + k][0] for k in range(3))
            out.append(f'f {a}/1 {b}/1 {c}/1')
        first += len(positions)
    base = ROOT / 'content/assets/gokart'
    model_dir = base / 'models/block'
    (model_dir / 'quaternius_sport.obj').write_text('\n'.join(out) + '\n')
    (model_dir / 'quaternius_sport.mtl').write_text(''.join(
        f'newmtl {slot}\nmap_Kd #{slot}\n' for slot in ('white', 'windows', 'grey', 'headlights', 'taillights')))
    for name, color in [('sport_window', (36, 55, 68, 255)), ('sport_trim', (38, 43, 49, 255)),
                        ('sport_head', (246, 238, 199, 255)), ('sport_tail', (198, 35, 34, 255))]:
        write_png(base / 'textures/block' / (name + '.png'), 16, 16, [color] * 256)
    for i, rgb in enumerate(COLORS):
        color = (rgb >> 16, (rgb >> 8) & 255, rgb & 255, 255)
        write_png(base / f'textures/block/sport_paint_{i:02}.png', 16, 16, [color] * 256)
        model = {'loader': 'neoforge:obj', 'model': 'gokart:models/block/quaternius_sport.obj',
                 'shade_quads': True, 'textures': {
                     'white': f'gokart:block/sport_paint_{i:02}', 'windows': 'gokart:block/sport_window',
                     'grey': 'gokart:block/sport_trim', 'headlights': 'gokart:block/sport_head',
                     'taillights': 'gokart:block/sport_tail'}}
        (model_dir / f'supercar_mesh_{i:02}.json').write_text(json.dumps(model, indent=2) + '\n')
    # Default uncoloured reference points at the blue variant too.
    (model_dir / 'supercar_body.json').write_text(json.dumps(model | {'textures': model['textures'] | {'white': 'gokart:block/sport_paint_11'}}, indent=2) + '\n')
