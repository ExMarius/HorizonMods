#!/usr/bin/env python3
"""Update only UTB body/wheels and two UTB sprites in the verified live pack."""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import update_utb_body as u
BASE_SHA1='23fc16c0e0870a323fa4d5f06d9806b8fc613a90'
MODELS={u.BODY:'utb_650_body.json',**{f'assets/vehicle/models/item/{n}.json':n+'.json' for n in u.WHEELS}}
CREAM='assets/vehicle/textures/item/utb_cream.png'
AMBER='assets/vehicle/textures/item/utb_amber.png'
GAUGES='assets/vehicle/textures/item/utb_gauges.png'

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected installed pack')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.testzip() or len(z.namelist())!=len(set(z.namelist())):raise ValueError('invalid pack')
        files={n:z.read(n) for n in z.namelist()}
    if json.loads(files['pack.mcmeta'])['pack']['pack_format']!=46:raise ValueError('wrong pack version')
    if CREAM not in files or AMBER in files or GAUGES in files:raise ValueError('unexpected UTB sprites')
    for path,filename in MODELS.items():
        if path not in files:raise ValueError('missing installed UTB model')
        model=json.loads((u.ASSETS/filename).read_text());u.validate(model)
        if any(not ref.startswith('vehicle:item/utb_') for ref in model['textures'].values()):raise ValueError('texture is not in default atlas')
        files[path]=json.dumps(model,separators=(',',':')).encode()
    for path,name in ((CREAM,'cream'),(AMBER,'amber'),(GAUGES,'gauges')):
        b=(u.ASSETS/'textures'/(name+'.png')).read_bytes()
        if not b.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('bad PNG')
        files[path]=b
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(files.items()):
            info=zipfile.ZipInfo(n,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
    return out.getvalue()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('base',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.base.resolve()==a.output.resolve():p.error('output must differ')
    b=build(a.base.read_bytes());a.output.write_bytes(b);print('SHA-1',hashlib.sha1(b).hexdigest())
if __name__=='__main__':main()
