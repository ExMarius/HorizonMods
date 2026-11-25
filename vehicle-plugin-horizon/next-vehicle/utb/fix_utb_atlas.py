#!/usr/bin/env python3
"""Repair UTB textures: Minecraft's block atlas scans item/, not utb/."""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import update_utb_body as u
BASE_SHA1='f5a1ee884256dcfa96cfc24c753cf65c22747fc0'
MODELS=(u.BODY,)+tuple(f'assets/vehicle/models/item/{n}.json' for n in u.WHEELS)

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected installed pack')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.testzip() or len(z.namelist())!=len(set(z.namelist())):raise ValueError('invalid pack')
        files={n:z.read(n) for n in z.namelist()}
    if json.loads(files['pack.mcmeta'])['pack']['pack_format']!=46:raise ValueError('wrong pack format')
    for path in MODELS:
        model=json.loads(files[path]);u.validate(model)
        for name in u.TEXTURES:
            if model['textures'].get(name)!=f'vehicle:utb/{name}':raise ValueError('unexpected original texture '+name)
            model['textures'][name]=f'vehicle:item/utb_{name}'
        files[path]=json.dumps(model,separators=(',',':')).encode()
    for name in u.TEXTURES:
        old=f'assets/vehicle/textures/utb/{name}.png';new=f'assets/vehicle/textures/item/utb_{name}.png'
        if new in files or old not in files or not files[old].startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('unexpected texture '+name)
        files[new]=files[old]
    output=io.BytesIO()
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(files.items()):
            info=zipfile.ZipInfo(n,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
    return output.getvalue()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('base',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.base.resolve()==a.output.resolve():p.error('output must differ')
    b=build(a.base.read_bytes());a.output.write_bytes(b);print('SHA-1',hashlib.sha1(b).hexdigest())
if __name__=='__main__':main()
