#!/usr/bin/env python3
"""Apply only the small hitch and registration plates to the installed pack."""
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import update_utb_body as u
BASE_SHA1 = '51258b834bdd24fe2ab2cce4cb289780974d6bcd'
MODELS = {u.BODY:u.MODEL, 'assets/vehicle/models/item/tractor_trailer_body.json':u.ASSETS/'tractor_trailer_body.json'}
TEXTURES = {f'assets/vehicle/textures/item/utb_{n}.png':u.ASSETS/'textures'/f'{n}.png' for n in ('plate_tractor','plate_trailer')}
def build(data, expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected: raise ValueError('unexpected installed pack')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.testzip() or len(z.namelist())!=len(set(z.namelist())): raise ValueError('invalid pack')
        files={n:z.read(n) for n in z.namelist()}
    if json.loads(files['pack.mcmeta'])['pack']['pack_format']!=46: raise ValueError('wrong pack format')
    for name,path in TEXTURES.items():
        if name in files: raise ValueError('texture already exists')
        data=path.read_bytes()
        if not data.startswith(b'\x89PNG\r\n\x1a\n'): raise ValueError('invalid texture')
        files[name]=data
    for name,path in MODELS.items():
        if name not in files: raise ValueError('missing model '+name)
        data=path.read_bytes(); model=json.loads(data); u.validate(model)
        for ref in model['textures'].values():
            ns,tex=ref.split(':')
            if f'assets/{ns}/textures/{tex}.png' not in files: raise ValueError('missing texture '+ref)
        files[name]=data
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(files.items()):
            info=zipfile.ZipInfo(n,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
    return out.getvalue()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('base',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.base.resolve()==a.output.resolve(): p.error('output must differ')
    result=build(a.base.read_bytes());a.output.write_bytes(result);print('SHA-1',hashlib.sha1(result).hexdigest())
if __name__=='__main__': main()
