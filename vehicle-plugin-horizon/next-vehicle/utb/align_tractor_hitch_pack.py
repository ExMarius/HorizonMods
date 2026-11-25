#!/usr/bin/env python3
"""Replace only the two models on the verified installed vehicle pack."""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import update_utb_body as u
BASE_SHA1='4c2fde06fa7e6932e2f01df1c259581d10da8f56'
MODELS={u.BODY:u.MODEL,'assets/vehicle/models/item/tractor_trailer_body.json':u.ASSETS/'tractor_trailer_body.json'}
def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected installed pack')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.testzip() or len(z.namelist())!=len(set(z.namelist())):raise ValueError('invalid pack')
        files={n:z.read(n) for n in z.namelist()}
    if json.loads(files['pack.mcmeta'])['pack']['pack_format']!=46:raise ValueError('wrong pack format')
    for name,path in MODELS.items():
        if name not in files:raise ValueError('missing model '+name)
        data=path.read_bytes();m=json.loads(data);u.validate(m)
        for ref in m['textures'].values():
            ns,tex=ref.split(':')
            if f'assets/{ns}/textures/{tex}.png' not in files:raise ValueError('missing texture '+ref)
        files[name]=data
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
