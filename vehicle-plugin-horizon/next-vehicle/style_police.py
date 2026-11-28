#!/usr/bin/env python3
"""Restyle ONLY the Dacia police resources in the verified installed pack."""
import argparse, copy, hashlib, io, json, zipfile
from pathlib import Path
from prepare_police import readzip
BASE_SHA1='4357e64281b5889d4c24d3e85faf35010e0d709e'
BODY='assets/daciapolice/models/item/body.json'
SOUNDS='assets/daciapolice/sounds.json'
ROOT=Path(__file__).resolve().parents[2]
def encode(value): return json.dumps(value,separators=(',',':')).encode()
def style(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected: raise ValueError('unexpected selected pack')
    files=readzip(data); original=json.loads(files[BODY]); sounds=json.loads(files[SOUNDS])
    if len(original['elements'])!=268 or 'sirena' not in sounds: raise ValueError('unexpected police assets')
    model=copy.deepcopy(original)
    # Flat livery panels over the existing front and rear doors. No source body
    # element is moved, removed or resized. Assets are the user's Horizon livery.
    model['textures'].update({'horizon_side':'daciapolice:item/horizon_police_side',
                              'horizon_hood':'daciapolice:item/horizon_police_hood',
                              'horizon_red':'daciapolice:item/horizon_siren_red',
                              'horizon_blue':'daciapolice:item/horizon_siren_blue'})
    for side,x in [('west',-1.015),('east',17.015)]:
        face={'texture':'#horizon_side','uv':[0,0,16,16]}
        if side=='west': face['uv']=[16,0,0,16]
        model['elements'].append({'from':[x,3.3,-2.2],'to':[x,8.8,15.3], 'faces':{side:face}})
    # Hood surface, centered on the existing bonnet. Thin decal, no deformation.
    model['elements'].append({'from':[2.0,8.985,20.8], 'to':[14.0,8.985,25.5],
                              'faces':{'up':{'texture':'#horizon_hood','uv':[0,0,16,16]}}})
    files[BODY]=encode(model)
    added={}
    for name in ('police_side','police_hood','siren_red','siren_blue'):
        added['assets/daciapolice/textures/item/horizon_'+name+'.png']=(ROOT/'content/assets/gokart/textures/block'/f'{name}.png').read_bytes()
    # Only recolor the original two roof-lens elements in the ON variants.
    for phase in (0,1):
        variant=copy.deepcopy(model)
        for index,color in ((224,'blue' if phase==0 else 'red'),(227,'red' if phase==0 else 'blue')):
            for face in variant['elements'][index]['faces'].values():
                face['texture']='#horizon_'+color;face['uv']=[0,0,16,16];face.pop('tintindex',None)
        name='body_flash_'+str(phase)
        added['assets/daciapolice/models/item/'+name+'.json']=encode(variant)
        added['assets/daciapolice/items/'+name+'.json']=encode({'model':{'type':'minecraft:model','model':'daciapolice:item/'+name,'tints':[{'type':'minecraft:dye','default':-1}]+[{'type':'minecraft:constant','value':-1}]*3}})
    # Separate keys prevent one car's stop packet silencing other police cars.
    for i in range(16): sounds['sirena_'+str(i)]={'sounds':['daciapolice:sirena_mono']}
    files[SOUNDS]=encode(sounds)
    if set(files)&set(added): raise ValueError('refusing resource collision')
    files.update(added)
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for n,v in sorted(files.items()):
            info=zipfile.ZipInfo(n,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,v)
    return out.getvalue()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('base',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.base.resolve()==a.output.resolve():p.error('output cannot overwrite input')
    out=style(a.base.read_bytes());a.output.write_bytes(out);print('SHA-1',hashlib.sha1(out).hexdigest(),'SHA-256',hashlib.sha256(out).hexdigest())
if __name__=='__main__':main()
