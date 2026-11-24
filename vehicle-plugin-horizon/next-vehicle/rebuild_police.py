#!/usr/bin/env python3
"""Rebuild the user's police Dacia styling without touching other vehicles."""
import argparse, copy, hashlib, io, json, zipfile
from pathlib import Path
from prepare_police import readzip
BASE_SHA1='162d4dd9ff52d0980d1eb4adbe9057f024b779c7'
BODY='assets/daciapolice/models/item/body.json'
BASE=Path(__file__).resolve().parent
SEATS=set(range(109,117))
# Narrow opaque panels fill the paired rear-quarter windows; retain pillars 39,43-47.
REAR_WINDOW_FILL=set(range(34,39)) | set(range(40,43))
OLD_LIGHTBAR=set(range(224,232))
OLD_POLICE_TEXT=set(range(232,268))
def encode(x): return json.dumps(x,separators=(',',':')).encode()
def cube(frm,to,tex):
    return {'from':frm,'to':to,'faces':{side:{'texture':'#'+tex,'uv':[0,0,16,16]} for side in ('north','south','east','west','up','down')}}
def rebuild(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected: raise ValueError('unexpected base pack')
    files=readzip(data); original=json.loads(files[BODY])
    if len(original['elements'])!=271 or len(original['elements'][:268])!=268: raise ValueError('unexpected base model')
    m=copy.deepcopy(original);m['elements']=[]
    m['textures'].update({'interior':'daciapolice:item/horizon_seat', 'livery':'daciapolice:item/logan_livery',
        'trim':'daciapolice:item/logan_trim','silver':'daciapolice:item/logan_silver',
        'red_dim':'daciapolice:item/siren_red_dim','blue_dim':'daciapolice:item/siren_blue_dim'})
    for index,element in enumerate(original['elements'][:268]):
        if index in (REAR_WINDOW_FILL | OLD_LIGHTBAR | OLD_POLICE_TEXT): continue
        e=copy.deepcopy(element)
        if index in SEATS:
            for face in e['faces'].values():
                face['texture']='#interior';face['uv']=[0,0,16,16];face.pop('tintindex',None)
        m['elements'].append(e)
    # Word-free blue livery. Originals remain beneath it, avoiding body reshaping.
    for side,x in [('west',-1.025),('east',17.025)]:
        uv=[16,0,0,16] if side=='west' else [0,0,16,16]
        m['elements'].append({'from':[x,3.2,-2.3], 'to':[x,8.75,15.4],
                              'faces':{side:{'texture':'#livery','uv':uv}}})
        # Discrete lower sill trim follows the existing door rectangle.
        m['elements'].append({'from':[x,1.3,-2.3], 'to':[x,1.8,15.4],
                              'faces':{side:{'texture':'#trim','uv':[0,0,16,16]}}})
    # Sleek roof bar replacing every original roof-light piece.
    m['elements'] += [cube([2,16.7,7.0],[3,17.2,9.0],'trim'),
                      cube([13,16.7,7.0],[14,17.2,9.0],'trim'),
                      cube([1.1,17.15,6.9],[14.9,17.65,9.4],'trim'),
                      cube([1.3,18.6,7.0],[14.7,18.72,9.3],'trim'),
                      cube([7.4,17.65,7.0],[8.6,18.6,9.3],'silver')]
    blue_index=len(m['elements']);m['elements'].append(cube([1.3,17.65,7.0],[7.4,18.6,9.3],'blue_dim'))
    red_index=len(m['elements']);m['elements'].append(cube([8.6,17.65,7.0],[14.7,18.6,9.3],'red_dim'))
    files[BODY]=encode(m)
    for phase in (0,1):
        variant=copy.deepcopy(m)
        for index,texture in ((blue_index,'horizon_blue' if phase==0 else 'blue_dim'),
                              (red_index,'red_dim' if phase==0 else 'horizon_red')):
            for face in variant['elements'][index]['faces'].values():face['texture']='#'+texture
        files[f'assets/daciapolice/models/item/body_flash_{phase}.json']=encode(variant)
    added={}
    for name in ('logan_livery','logan_trim','logan_silver','siren_red_dim','siren_blue_dim'):
        added['assets/daciapolice/textures/item/'+name+'.png']=(BASE/'assets'/f'{name}.png').read_bytes()
    added['assets/daciapolice/textures/item/horizon_seat.png']=(BASE.parents[1]/'content/assets/gokart/textures/block/kart_seat.png').read_bytes()
    if set(files)&set(added):raise ValueError('refusing resource collision')
    files.update(added);out=io.BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for n,v in sorted(files.items()):
            i=zipfile.ZipInfo(n,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,v)
    return out.getvalue()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('base',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.base.resolve()==a.output.resolve():p.error('output cannot overwrite input')
    result=rebuild(a.base.read_bytes());a.output.write_bytes(result);print('SHA-1',hashlib.sha1(result).hexdigest(),'SHA-256',hashlib.sha256(result).hexdigest())
if __name__=='__main__':main()
