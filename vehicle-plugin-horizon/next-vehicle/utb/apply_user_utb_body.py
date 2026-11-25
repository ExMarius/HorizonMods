#!/usr/bin/env python3
"""Apply the user's Blockbench body to the verified installed UTB pack."""
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import update_utb_body as u

BASE_SHA1 = '6b4c143119fe02cb439559e03a67fc05a0106353'

def build(data, expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest() != expected:
        raise ValueError('unexpected installed pack')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.testzip() or len(z.namelist()) != len(set(z.namelist())):
            raise ValueError('invalid pack')
        files = {name:z.read(name) for name in z.namelist()}
    if json.loads(files['pack.mcmeta'])['pack']['pack_format'] != 46 or u.BODY not in files:
        raise ValueError('unexpected pack layout')
    body = u.MODEL.read_bytes()
    model = json.loads(body)
    u.validate(model)
    for ref in model['textures'].values():
        ns, path = ref.split(':')
        if f'assets/{ns}/textures/{path}.png' not in files:
            raise ValueError('missing texture ' + ref)
    files[u.BODY] = body
    out = io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for name, content in sorted(files.items()):
            info = zipfile.ZipInfo(name,(1980,1,1,0,0,0)); info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info,content)
    return out.getvalue()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('base',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.base.resolve()==a.output.resolve():p.error('output must differ')
    result=build(a.base.read_bytes());a.output.write_bytes(result);print('SHA-1',hashlib.sha1(result).hexdigest())
if __name__=='__main__':main()
