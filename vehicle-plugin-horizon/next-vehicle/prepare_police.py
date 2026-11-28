#!/usr/bin/env python3
"""Add the user's original Dacia police model and siren to the current pack."""
import argparse, hashlib, io, json, zipfile
from pathlib import Path
BASE_SHA1='62ae2a64b6966143e06882b9beca519668241ec7'
MODEL='vehicle/models/vehicle/dacia_logan_police_body.json'
CONFIG='vehicle/vehicles/dacia_logan_police.json'
SOUND='vehicle/sounds/entity/vehicle/sirena_mono.ogg'
LEGAL={-45.0,-22.5,0.0,22.5,45.0}

def readzip(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names=[i.filename for i in z.infolist() if not i.is_dir()]
        if len(names)!=len(set(names)) or any(n.startswith('/') or '\\' in n or '..' in n.split('/') for n in names): raise ValueError('unsafe archive')
        return {n:z.read(n) for n in names}

def prepare(base, source, expected_sha1=BASE_SHA1):
    if hashlib.sha1(base).hexdigest()!=expected_sha1: raise ValueError('unexpected selected pack')
    existing=readzip(base); src=readzip(source)
    if json.loads(existing['pack.mcmeta'])['pack']['pack_format']!=46: raise ValueError('wrong pack format')
    model=json.loads(src[MODEL]); parts=model['elements']
    if len(parts)!=268: raise ValueError('unexpected model geometry')
    for e in parts:
        if any(not -16<=v<=32 for k in ('from','to') for v in e[k]): raise ValueError('element out of bounds')
        r=e.get('rotation')
        if r and (r.get('axis') not in ('x','y','z') or float(r.get('angle',999)) not in LEGAL or len(r.get('origin',[]))!=3 or any(not -16<=v<=32 for v in r['origin'])): raise ValueError('unsupported rotation')
    textures={}; additions={}
    for slot,ref in model['textures'].items():
        if not ref.startswith('vehicle:vehicle/'): raise ValueError('unexpected texture')
        name=ref.split(':',1)[1]; target='assets/daciapolice/textures/item/'+name.replace('/','_')+'.png'
        texture=src['vehicle/textures/'+name+'.png']
        if target in additions and additions[target]!=texture: raise ValueError('texture collision')
        additions[target]=texture; textures[slot]='daciapolice:item/'+name.replace('/','_')
    new_model={'credit':model['credit'],'textures':textures,'elements':parts}
    additions['assets/daciapolice/models/item/body.json']=json.dumps(new_model,separators=(',',':')).encode()
    tints=[{'type':'minecraft:dye','default':-1}]+[{'type':'minecraft:constant','value':-1}]*3
    additions['assets/daciapolice/items/body.json']=json.dumps({'model':{'type':'minecraft:model','model':'daciapolice:item/body','tints':tints}},separators=(',',':')).encode()
    additions['assets/daciapolice/sounds/sirena_mono.ogg']=src[SOUND]
    additions['assets/daciapolice/sounds.json']=json.dumps({'sirena':{'sounds':['daciapolice:sirena_mono']}},separators=(',',':')).encode()
    additions['dacia-logan-police-source-layout.json']=src[CONFIG]
    if set(existing)&set(additions): raise ValueError('refusing to replace existing resources')
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted((existing|additions).items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
    return out.getvalue()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('base',type=Path);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.output.resolve() in (a.base.resolve(),a.source.resolve()):p.error('output cannot overwrite inputs')
    result=prepare(a.base.read_bytes(),a.source.read_bytes());a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(result)
    print('SHA-256',hashlib.sha256(result).hexdigest(),'SHA-1',hashlib.sha1(result).hexdigest())
if __name__=='__main__':main()
