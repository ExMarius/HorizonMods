#!/usr/bin/env python3
"""Use a complete Horizon tire and add wheel liners and a Horizon-style wheel."""
import argparse,copy,hashlib,io,json,zipfile
from pathlib import Path
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f,polish_logan_body as p,refit_police_logan as q,finish_police_logan as t,detail_police_logan as d,complete_police_logan as u
ROOT=Path(__file__).resolve().parents[2]
BASE_SHA1='13521f225f298923a18b6cdc8dc6fd0f9330259b'
C=c.cube
STEER=t.STEER
NEW={'assets/daciapolice/models/item/wheel_complete.json','assets/daciapolice/items/wheel_complete.json'}

def wheel():
    original=json.loads((ROOT/'content/assets/gokart/models/block/wheel_sports.json').read_bytes())
    model=copy.deepcopy(original)
    model['textures']={k:v.replace('gokart:block/','horizonvehicles:item/') for k,v in model['textures'].items()}
    # The only non-vanilla angle is 67.5. Its two perpendicular pieces become
    # the SAME two boxes rotated -22.5 instead (67.5 = -22.5 + 90). Swapping
    # their Y/Z extents preserves their geometry while retaining all 17 pieces.
    for i,j in ((6,7),(7,6)):
        part=model['elements'][i];other=original['elements'][j]
        for key in ('from','to'):part[key][1:3]=other[key][1:3]
        part['faces']=copy.deepcopy(other['faces'])
        part['rotation']['angle']=-22.5
    return model

def steering():
    source=json.loads((ROOT/'content/assets/gokart/models/block/go_kart_steering_wheel.json').read_bytes())
    textures={k:v.replace('gokart:block/','horizonvehicles:item/') for k,v in source['textures'].items()}
    elements=[]
    for old in source['elements']:
        part=copy.deepcopy(old)
        for key in ('from','to'):part[key][1],part[key][2]=part[key][2],part[key][1]
        # Preserve UVs along their corresponding transformed surfaces.
        faces=part['faces'];faces['up'],faces['south']=faces['south'],faces['up'];faces['down'],faces['north']=faces['north'],faces['down']
        rotation=part.get('rotation')
        if rotation:
            rotation['axis']='y';rotation['angle']=-rotation['angle']
            if abs(rotation['angle'])==12.0:part.pop('rotation') # subtle straight spokes in one legal model
        elements.append(part)
    elements.append(C([7.35,-2.3,7.35],[8.65,7.5,8.65],'frame'))
    return {'textures':textures,'elements':elements}

def body(model,phase):
    prev=u.complete(d.detail(t.finish(q.refit(p.polish(f.refine_model(r.repair_model({'elements':c.body(phase),'textures':c.TEX},phase),phase),phase),phase),phase),phase),phase)
    if model['elements']!=prev['elements'] or model['textures']!=prev['textures']:raise ValueError('unexpected body revision')
    e=copy.deepcopy(model['elements'])
    def add(a,b,tex):e.append(C(a,b,tex))
    # Dark liners form a roof and front/rear walls INSIDE each wheelhouse.
    # They connect to existing fender lips and floor but do not fill tire space.
    for x0,x1 in ((-.65,2.44),(13.56,16.65)):
        for z0,z1 in ((-11.1,-2.9),(19.25,28.65)):
            add([x0,5.20,z0],[x1,5.44,z1],'trim')
        for z0,z1 in ((-11.3,-11.1),(19.0,19.25),(28.65,28.85)):
            add([x0,1.35,z0],[x1,5.20,z1],'trim')
    # Inner front wheelhouse walls, matching the existing rear seat liners.
    for x0,x1 in ((2.45,2.5),(13.5,13.55)):
        add([x0,1.0,19.25],[x1,5.20,28.65],'trim')
    result=copy.deepcopy(model);result['elements']=e;return result

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected deployed pack')
    files=c.readzip(data)
    if NEW & set(files) or json.loads(files[STEER])!=t.steering():raise ValueError('unexpected steering or wheel resource collision')
    for path,phase in zip(c.PATHS,(-1,0,1)):files[path]=c.encode(body(json.loads(files[path]),phase))
    files[STEER]=c.encode(steering())
    files['assets/daciapolice/models/item/wheel_complete.json']=c.encode(wheel())
    files['assets/daciapolice/items/wheel_complete.json']=c.encode({'model':{'type':'minecraft:model','model':'daciapolice:item/wheel_complete'}})
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for n,v in sorted(files.items()):
            i=zipfile.ZipInfo(n,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,v)
    return b.getvalue()
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args()
    if a.base.resolve()==a.output.resolve():ap.error('cannot overwrite base')
    data=build(a.base.read_bytes());a.output.write_bytes(data);print('SHA-1',hashlib.sha1(data).hexdigest())
if __name__=='__main__':main()
