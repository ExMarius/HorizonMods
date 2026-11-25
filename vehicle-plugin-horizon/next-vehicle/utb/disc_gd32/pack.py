#!/usr/bin/env python3
"""Add the *candidate* GD-3.2 models to a pack, never overwriting its inputs.

An explicit SHA-1 is mandatory: verify it against the installed pack before use.
This script only constructs a local candidate, it does not install anything.
"""
import argparse, hashlib, io, json, subprocess, sys, tempfile, zipfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
PARTS = ('body', 'gang_frame', 'gang_front', 'gang_rear', 'wheel', 'axle', 'jack')
COLORS = ('blue', 'darkblue', 'dark', 'steel', 'rubber', 'cream', 'weight')

def build(base, expected):
    if hashlib.sha1(base).hexdigest() != expected.lower():
        raise ValueError('base pack hash mismatch')
    with zipfile.ZipFile(io.BytesIO(base)) as src:
        names = src.namelist()
        if len(names) != len(set(names)) or src.testzip():
            raise ValueError('corrupt or duplicate zip entries')
        files = {n: src.read(n) for n in names}
    if json.loads(files['pack.mcmeta'])['pack']['pack_format'] != 46:
        raise ValueError('unsupported pack format')
    with tempfile.TemporaryDirectory() as d:
        subprocess.run([sys.executable, str(HERE/'build_models.py'), d], check=True, stdout=subprocess.DEVNULL)
        generated = Path(d)
        additions = {}
        for part in PARTS:
            name = 'gd32_' + part
            additions[f'assets/vehicle/models/item/{name}.json'] = (generated/(name+'.json')).read_bytes()
            additions[f'assets/vehicle/items/{name}.json'] = json.dumps(
                {'model': {'type': 'minecraft:model', 'model': 'vehicle:item/'+name}}, separators=(',', ':')).encode()
        for color in COLORS:
            name = 'gd32_'+color
            additions[f'assets/vehicle/textures/item/{name}.png'] = (generated/(name+'.png')).read_bytes()
        if set(files) & set(additions):
            raise ValueError('candidate asset already exists; refusing overwrite')
        files.update(additions)
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as dst:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (1980,1,1,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            dst.writestr(info, data)
    return out.getvalue()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('base', type=Path); p.add_argument('output', type=Path)
    p.add_argument('--expected-sha1', required=True)
    a=p.parse_args()
    if a.base.resolve() == a.output.resolve(): p.error('output must differ from input')
    if a.output.exists(): p.error('output already exists')
    result=build(a.base.read_bytes(), a.expected_sha1)
    with a.output.open('xb') as f: f.write(result)
    print('Candidate SHA-1:', hashlib.sha1(result).hexdigest())
if __name__=='__main__': main()
