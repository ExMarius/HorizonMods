#!/usr/bin/env python3
"""Produce a separate, reproducible candidate pack; never modifies its inputs."""
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

R39_SHA256 = 'f1d0b35cb54c8c8a0f6bfb323183d3448c528ada52919bfd94bcf2df7167f7ea'

def files(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = [info.filename for info in z.infolist() if not info.is_dir()]
        if len(names) != len(set(names)):
            raise ValueError('duplicate archive entries')
        if any(n.startswith('/') or '\\' in n or '..' in n.split('/') for n in names):
            raise ValueError('unsafe archive entry')
        return {n: z.read(n) for n in names}

def merge(base, transfer, expected_sha=R39_SHA256):
    if hashlib.sha256(base).hexdigest() != expected_sha:
        raise ValueError('base pack does not match the selected r39')
    existing = files(base)
    if json.loads(existing['pack.mcmeta'])['pack']['pack_format'] != 46:
        raise ValueError('base pack is not Paper 1.21.4 format 46')
    bundle = files(transfer)
    candidate = files(bundle['paper-resource-pack.zip'])
    additions = {n: data for n, data in candidate.items() if n.startswith('assets/horizonvehicles/')}
    if not additions or not any(n.startswith('assets/horizonvehicles/items/') for n in additions):
        raise ValueError('transfer is missing item models')
    additions['horizon-off-roader-LICENSE.txt'] = bundle['LICENSE.txt']
    if set(existing) & set(additions):
        raise ValueError('refusing to overwrite any existing pack file')
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted((existing | additions).items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    return output.getvalue()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base', type=Path)
    parser.add_argument('transfer', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.output.resolve() in {args.base.resolve(), args.transfer.resolve()}:
        parser.error('output must be separate from both inputs')
    data = merge(args.base.read_bytes(), args.transfer.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    print('Candidate SHA-256:', hashlib.sha256(data).hexdigest())
    print('Candidate SHA-1:  ', hashlib.sha1(data).hexdigest())
    print('Local candidate only: do not install until the vehicle rig is ready.')

if __name__ == '__main__': main()
