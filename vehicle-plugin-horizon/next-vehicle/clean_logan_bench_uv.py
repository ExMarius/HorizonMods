#!/usr/bin/env python3
"""Remove repeated red seams from rear seat extensions without moving geometry."""
import argparse, copy, hashlib, io, json, zipfile
from pathlib import Path
import custom_logan_body as c
BASE_SHA1='3a404797106c7812cce96f4cb7790bf8e853c6e8'
# Main cushion, backrest and headrests retain the original Horizon seams.
KEEP={(2.5,1.7,-3.9),(2.5,3.7,-5.3),(2.6,8.1,-5.35),(9.7,8.1,-5.35)}

def clean(model):
    model=copy.deepcopy(model)
    count=0
    for part in model['elements']:
        if part['from'][2]>=0 or tuple(part['from']) in KEEP: continue
        faces=[face for face in part['faces'].values() if face['texture']=='#seat']
        if not faces: continue
        # The source 16x16 Horizon upholstery has red stitching in columns
        # 2 and 13. Sample only the black fabric between those columns on
        # the extra pieces, preserving the main bench's original stitching.
        for face in faces:
            if face.get('uv') != [0,0,16,16]: raise ValueError('unexpected seat UV')
            face['uv']=[3,0,13,16]
        count+=1
    if count!=12: raise ValueError(f'unexpected rear extension count: {count}')
    return model

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected installed pack')
    files=c.readzip(data)
    for path in c.PATHS:files[path]=c.encode(clean(json.loads(files[path])))
    output=io.BytesIO()
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name,value in sorted(files.items()):
            item=zipfile.ZipInfo(name,(1980,1,1,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED;z.writestr(item,value)
    return output.getvalue()

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args()
    if a.base.resolve()==a.output.resolve():ap.error('cannot overwrite base')
    out=build(a.base.read_bytes());a.output.write_bytes(out);print('SHA-1',hashlib.sha1(out).hexdigest())
if __name__=='__main__':main()
