#!/usr/bin/env python3
"""Replace just UTB's body and add its dashboard atlas sprite."""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import update_utb_body as u
BASE_SHA1='4bd882618d246d096222ad48ebdaaba5677d8ca9'
GAUGES='assets/vehicle/textures/item/utb_gauges.png'

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected installed pack')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.testzip() or len(z.namelist())!=len(set(z.namelist())):raise ValueError('invalid pack')
        files={n:z.read(n) for n in z.namelist()}
    if json.loads(files['pack.mcmeta'])['pack']['pack_format']!=46 or u.BODY not in files or GAUGES in files:raise ValueError('unexpected pack layout')
    model=json.loads(u.MODEL.read_text());u.validate(model)
    if model['textures'].get('gauges')!='vehicle:item/utb_gauges':raise ValueError('wrong texture path')
    for ref in model['textures'].values():
        ns,path=ref.split(':');asset=f'assets/{ns}/textures/{path}.png'
        if asset!=GAUGES and asset not in files:raise ValueError('missing texture '+asset)
    files[u.BODY]=json.dumps(model,separators=(',',':')).encode()
    files[GAUGES]=(u.ASSETS/'textures/gauges.png').read_bytes()
    if not files[GAUGES].startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('invalid gauges PNG')
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
