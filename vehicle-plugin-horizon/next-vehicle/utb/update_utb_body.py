#!/usr/bin/env python3
"""Install the authored UTB body in the matching pack; touch no other asset."""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
BASE_SHA1='5ef2a14348ab3973904bcb4b314d64c476126cb1'
BODY='assets/vehicle/models/item/utb_650_body.json'
MODEL=Path(__file__).with_name('assets')/'utb_650_body.json'

def validate(m):
    if not 60 <= len(m['elements']) <= 200: raise ValueError('unexpected body size')
    for part in m['elements']:
        if any(not -16 <= x <= 32 for key in ('from','to') for x in part[key]): raise ValueError('body coordinates exceed vanilla bounds')
        if any(a>=b for a,b in zip(part['from'],part['to'])): raise ValueError('invalid cuboid')
        if 'rotation' in part: raise ValueError('unexpected rotation')
        if set(part['faces']) != {'north','south','east','west','up','down'}: raise ValueError('missing face')
        for face in part['faces'].values():
            if face['texture'].lstrip('#') not in m['textures']: raise ValueError('missing texture')

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected: raise ValueError('unexpected deployed pack')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.testzip() or len(z.namelist())!=len(set(z.namelist())): raise ValueError('invalid pack')
        files={n:z.read(n) for n in z.namelist()}
    if BODY not in files or json.loads(files['pack.mcmeta'])['pack']['pack_format']!=46: raise ValueError('not the expected pack')
    m=json.loads(MODEL.read_text());validate(m)
    files[BODY]=json.dumps(m,separators=(',',':')).encode()
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
