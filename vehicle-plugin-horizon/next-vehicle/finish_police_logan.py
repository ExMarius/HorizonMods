#!/usr/bin/env python3
"""Refine the Logan steering wheel and cabin without changing wheel positions."""
import argparse,copy,hashlib,io,json,zipfile
from pathlib import Path
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f,polish_logan_body as p,refit_police_logan as q
BASE_SHA1='0dc8d1a76098d8ab752a34366ab3c91fe1dcb010'
C=c.cube
SMOKED='assets/daciapolice/textures/item/smoked_glass.png'
STEER='assets/daciapolice/models/item/steering.json'

def steering():
    parts=[]
    def add(a,b,t='trim'):parts.append(C(a,b,t))
    # Twelve short segments give an octagonal wheel, rather than a square;
    # the smaller display scale is applied by the Dacia rig only.
    add([6,7.55,3.8],[10,8.45,4.5]);add([6,7.55,11.5],[10,8.45,12.2])
    add([3.8,7.55,6],[4.5,8.45,10]);add([11.5,7.55,6],[12.2,8.45,10])
    for x0,x1 in ((4.5,6),(10,11.5)):
        for z0,z1 in ((4.5,5.25),(10.75,11.5)):
            add([x0,7.55,z0],[x1,8.45,z1])
    for x0,x1 in ((4.5,5.25),(10.75,11.5)):
        for z0,z1 in ((5.25,6),(10,10.75)):
            add([x0,7.55,z0],[x1,8.45,z1])
    add([4.5,7.65,7.6],[11.5,8.35,8.4])
    add([7.5,7.6,8.4],[8.5,8.4,11.5])
    add([7,8.46,7],[9,8.8,9],'chrome')
    # The longer shaft compensates for the reduced wheel display scale.
    add([7.35,-2.3,7.35],[8.65,7.5,8.65])
    return {'textures':{'trim':'daciapolice:item/logan_trim','chrome':'daciapolice:item/logan_chrome'},'elements':parts}

def finish(model,phase):
    before=q.refit(p.polish(f.refine_model(r.repair_model({'elements':c.body(phase),'textures':c.TEX},phase),phase),phase),phase)
    if model['elements']!=before['elements'] or model['textures']!=before['textures']:raise ValueError('unexpected Logan body')
    e=copy.deepcopy(model['elements'])
    def change(old,new):
        if e.count(old)!=1:raise ValueError('missing part '+str(old['from']))
        e[e.index(old)]=new
    def add(a,b,t):e.append(C(a,b,t))
    # Restore open rear side windows, including all flash variants.
    windows=[x for x in e if any(face['texture']=='#smoked' for face in x['faces'].values())]
    if len(windows)!=2:raise ValueError('unexpected windows')
    for w in windows:e.remove(w)
    # Move to immediately behind the front backrest at z=4.8. A full four-model-
    # pixel shift would place the grating inside the seats; contact is the goal.
    grid=[]
    for x0,x1 in ((.05,.38),(15.62,15.95)):grid.append(C([x0,3.9,3.1],[x1,14.95,3.42],'trim'))
    for y0,y1 in ((4.,4.25),(14.65,14.9)):grid.append(C([.38,y0,3.1],[15.62,y1,3.42],'trim'))
    for x in (2,4,6,8,10,12,14):grid.append(C([x,4.25,3.13],[x+.14,14.65,3.28],'trim'))
    for y in (7.2,10.8):grid.append(C([.4,y,3.29],[15.6,y+.14,3.43],'trim'))
    for original in grid:
        moved=copy.deepcopy(original)
        for k in ('from','to'):moved[k][2]=round(moved[k][2]+1.37,5)
        change(original,moved)
    for x0,x1 in ((2.8,3.2),(12.8,13.2)):add([x0,7.0,4.79],[x1,7.45,4.81],'trim')
    # Remove the colored dash-textured patch from the pedal floor only.
    change(C([.35,1.7,13.5],[15.65,1.82,17.8],'dash'),C([.35,1.7,13.5],[15.65,1.82,17.8],'trim'))
    # Parcel shelf fills the gap between the backrest and the trunk. Soft side
    # armrests sit above the static tire envelope; the existing inner liners
    # hide the tire faces below them without moving the wheels.
    add([-.55,8.6,-8.34],[16.55,8.74,-5.3],'trim')
    for x0,x1 in ((-.55,2.45),(13.55,16.55)):
        add([x0,5.17,-8.3],[x1,6.0,-3.0],'trim')
        add([x0+.25,6.0,-7.8],[x1-.25,6.18,-3.5],'seat')
    result=copy.deepcopy(model);result['elements']=e;result['textures'].pop('smoked');return result

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected deployed pack')
    files=c.readzip(data)
    if files.get(SMOKED)!=q.smoked_texture() or json.loads(files[STEER])!=q.steering():raise ValueError('unexpected steering or window texture')
    for path,phase in zip(c.PATHS,(-1,0,1)):files[path]=c.encode(finish(json.loads(files[path]),phase))
    files.pop(SMOKED);files[STEER]=c.encode(steering())
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
