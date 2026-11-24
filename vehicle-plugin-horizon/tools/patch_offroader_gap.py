#!/usr/bin/env python3
"""Extend the existing cowl element to overlap the hood; preserve every other file."""
import argparse, hashlib, io, json, zipfile
from pathlib import Path
BASE_SHA1='ca0413462ebbbc2fde1b8c2f1cfaf43620709661'
PATH='assets/horizonvehicles/models/item/off_roader_body_part_00.json'

def patch(data,expected_sha1=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected_sha1: raise ValueError('unexpected Horizon pack')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names=[i.filename for i in z.infolist() if not i.is_dir()]
        if len(names)!=len(set(names)): raise ValueError('duplicate entries')
        files={name:z.read(name) for name in names}
    model=json.loads(files[PATH]); matches=[e for e in model['elements'] if e['from']==[-2.55,9.8,14.35] and e['to']==[18.55,13.5,16.4]]
    if len(matches)!=1: raise ValueError('cowl geometry not as expected')
    # The nearby hood starts at z=17.2; a 0.05-pixel overlap avoids a seam.
    matches[0]['to'][2]=17.25
    files[PATH]=json.dumps(model,separators=(',',':')).encode()
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for n,content in sorted(files.items()):
            info=zipfile.ZipInfo(n,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,content)
    return out.getvalue()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('base',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.base.resolve()==a.output.resolve():p.error('output must not overwrite input')
    data=patch(a.base.read_bytes());a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(data)
    print('SHA-256:',hashlib.sha256(data).hexdigest(),'SHA-1:',hashlib.sha1(data).hexdigest())
if __name__=='__main__':main()
