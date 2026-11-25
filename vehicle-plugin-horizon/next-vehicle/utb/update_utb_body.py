#!/usr/bin/env python3
"""Replace only the UTB body and add its independent wheels/textures to the pack."""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
BASE_SHA1='045bfc6c38e80373e6d985e2b534e95fb801855b'
BODY='assets/vehicle/models/item/utb_650_body.json'
ASSETS=Path(__file__).with_name('assets')
MODEL=ASSETS/'utb_650_body.json'
WHEELS=('utb_650_wheel_front','utb_650_wheel_rear')
TEXTURES=('red','cream','roof','black','frame','metal','silver','lamp','tail','seat','logo')

def validate(m):
    if not 10 <= len(m['elements']) <= 200: raise ValueError('unexpected model size')
    for part in m['elements']:
        if any(not -16 <= x <= 32 for key in ('from','to') for x in part[key]): raise ValueError('body coordinates exceed vanilla bounds')
        if any(a>=b for a,b in zip(part['from'],part['to'])): raise ValueError('invalid cuboid')
        if set(part['faces']) != {'north','south','east','west','up','down'}: raise ValueError('missing face')
        r=part.get('rotation')
        if r and (r['axis'] not in ('x','y','z') or r['angle'] not in (-45,-22.5,0,22.5,45) or any(not -16<=v<=32 for v in r['origin'])):raise ValueError('invalid rotation')
        for face in part['faces'].values():
            if face['texture'].lstrip('#') not in m['textures']: raise ValueError('missing texture')
            if any(not 0<=v<=16 for v in face['uv']):raise ValueError('bad UV')

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected: raise ValueError('unexpected deployed pack')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.testzip() or len(z.namelist())!=len(set(z.namelist())): raise ValueError('invalid pack')
        files={n:z.read(n) for n in z.namelist()}
    if BODY not in files or json.loads(files['pack.mcmeta'])['pack']['pack_format']!=46: raise ValueError('not the expected pack')
    m=json.loads(MODEL.read_text());validate(m)
    files[BODY]=json.dumps(m,separators=(',',':')).encode()
    for name in WHEELS:
        model=json.loads((ASSETS/(name+'.json')).read_text());validate(model)
        itempath=f'assets/vehicle/items/{name}.json';modelpath=f'assets/vehicle/models/item/{name}.json'
        if itempath in files or modelpath in files:raise ValueError('wheel already exists')
        files[itempath]=json.dumps({'model':{'type':'minecraft:model','model':'vehicle:item/'+name}},separators=(',',':')).encode()
        files[modelpath]=json.dumps(model,separators=(',',':')).encode()
    for name in TEXTURES:
        path=f'assets/vehicle/textures/item/utb_{name}.png'
        if path in files:raise ValueError('texture already exists')
        files[path]=(ASSETS/'textures'/(name+'.png')).read_bytes()
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
