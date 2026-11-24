#!/usr/bin/env python3
"""Copy the user's existing Dacia Logan model into a separate 1.21.4 pack candidate."""
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

BASE_SHA1='ca0413462ebbbc2fde1b8c2f1cfaf43620709661'
MODEL='vehicle/models/vehicle/dacialogan_body.json'
CONFIG='vehicle/vehicles/dacia_logan.json'
LEGAL={-45.0,-22.5,0.0,22.5,45.0}

def readzip(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names=[i.filename for i in z.infolist() if not i.is_dir()]
        if len(names)!=len(set(names)) or any(n.startswith('/') or '\\' in n or '..' in n.split('/') for n in names):
            raise ValueError('unsafe or duplicate zip path')
        return {n:z.read(n) for n in names}

def prepare(base, source, expected_sha1=BASE_SHA1):
    if hashlib.sha1(base).hexdigest()!=expected_sha1: raise ValueError('unexpected base pack')
    existing=readzip(base); src=readzip(source)
    if json.loads(existing['pack.mcmeta'])['pack']['pack_format']!=46: raise ValueError('incorrect pack format')
    model=json.loads(src[MODEL]); parts=model['elements']
    if len(parts)!=230: raise ValueError('unexpected model geometry')
    for e in parts:
        if any(not -16 <= v <= 32 for k in ('from','to') for v in e[k]): raise ValueError('model element out of bounds')
        r=e.get('rotation')
        if r and (r.get('axis') not in ('x','y','z') or float(r.get('angle',999)) not in LEGAL
                  or any(not -16 <= v <= 32 for v in r.get('origin',[]))):
            raise ValueError('rotation not supported in vanilla')
    textures={}; additions={}
    for slot,ref in model['textures'].items():
        if not ref.startswith('vehicle:vehicle/'): raise ValueError('unexpected texture reference')
        path=ref.split(':',1)[1]
        name=path.replace('/','_')
        data=src['vehicle/textures/'+path+'.png']
        target='assets/daciavehicle/textures/item/'+name+'.png'
        if target in additions and additions[target]!=data: raise ValueError('texture name collision')
        additions[target]=data
        textures[slot]='daciavehicle:item/'+name
    # Retain authored elements, rotations, UVs, tint indices and credit unchanged.
    converted={'credit':model['credit'],'textures':textures,'elements':parts}
    additions['assets/daciavehicle/models/item/dacia_logan_body.json']=json.dumps(converted,separators=(',',':')).encode()
    additions['assets/daciavehicle/items/dacia_logan_body.json']=json.dumps({'model':{'type':'minecraft:model',
        'model':'daciavehicle:item/dacia_logan_body','tints':[{'type':'minecraft:dye','default':-1}]}},separators=(',',':')).encode()
    # Keep source settings as provenance metadata, not a claim of complete integration.
    additions['dacia-logan-source-layout.json']=src[CONFIG]
    if set(existing)&set(additions): raise ValueError('refusing to overwrite existing resources')
    output=io.BytesIO()
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for n,data in sorted((existing|additions).items()):
            info=zipfile.ZipInfo(n,(1980,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; z.writestr(info,data)
    return output.getvalue()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('base',type=Path);ap.add_argument('source',type=Path);ap.add_argument('output',type=Path)
    args=ap.parse_args()
    if args.output.resolve() in (args.base.resolve(),args.source.resolve()): ap.error('output must not overwrite input')
    result=prepare(args.base.read_bytes(),args.source.read_bytes());args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(result)
    print('Candidate SHA-256:',hashlib.sha256(result).hexdigest())
    print('Candidate only; Dacia is not yet integrated or playable.')
if __name__=='__main__': main()
