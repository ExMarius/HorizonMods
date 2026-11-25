#!/usr/bin/env python3
"""Restore the authored bar and add the modern trailer to the verified pack."""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import update_utb_body as u
BASE_SHA1='5d8260da16cbcf3e3a9a2941baa023c950214199'
MODEL='assets/vehicle/models/item/tractor_trailer_modern_body.json'
ITEM='assets/vehicle/items/tractor_trailer_modern_body.json'
FRONT='assets/vehicle/models/item/tractor_trailer_modern_front.json'
FRONT_ITEM='assets/vehicle/items/tractor_trailer_modern_front.json'
NEW_TEXTURES={f'assets/vehicle/textures/item/utb_{n}.png': u.ASSETS/'textures'/f'{n}.png' for n in ('rm_green','rm_dark','rm_hose_blue')}
def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected installed pack')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.testzip() or len(z.namelist())!=len(set(z.namelist())):raise ValueError('invalid pack')
        files={n:z.read(n) for n in z.namelist()}
    if json.loads(files['pack.mcmeta'])['pack']['pack_format']!=46 or any(n in files for n in (MODEL,ITEM,FRONT,FRONT_ITEM)) or u.BODY not in files:raise ValueError('unexpected pack layout')
    for name,path in NEW_TEXTURES.items():
        if name in files: raise ValueError('new texture already exists: '+name)
        data=path.read_bytes()
        if not data.startswith(b'\x89PNG\r\n\x1a\n'): raise ValueError('invalid texture '+name)
        files[name]=data
    for dest,path in ((u.BODY,u.MODEL),(MODEL,u.ASSETS/'tractor_trailer_modern_body.json'),(FRONT,u.ASSETS/'tractor_trailer_modern_front.json')):
        data=path.read_bytes();m=json.loads(data);u.validate(m)
        for ref in m['textures'].values():
            ns,tex=ref.split(':')
            if f'assets/{ns}/textures/{tex}.png' not in files:raise ValueError('missing texture '+ref)
        files[dest]=data
    files[ITEM]=json.dumps({'model':{'type':'minecraft:model','model':'vehicle:item/tractor_trailer_modern_body'}},separators=(',',':')).encode()
    files[FRONT_ITEM]=json.dumps({'model':{'type':'minecraft:model','model':'vehicle:item/tractor_trailer_modern_front'}},separators=(',',':')).encode()
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(files.items()):
            info=zipfile.ZipInfo(n,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
    return out.getvalue()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('base',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.base.resolve()==a.output.resolve():p.error('output must differ')
    result=build(a.base.read_bytes());a.output.write_bytes(result);print('SHA-1',hashlib.sha1(result).hexdigest())
if __name__=='__main__':main()
