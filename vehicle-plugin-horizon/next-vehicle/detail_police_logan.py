#!/usr/bin/env python3
"""Connect the Logan's rear bench, door pillars and full-height partition."""
import argparse,copy,hashlib,io,json,zipfile
from pathlib import Path
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f,polish_logan_body as p,refit_police_logan as q,finish_police_logan as t
BASE_SHA1='e2df98516df738c740e1160c81ce8dc0cd870963'
C=c.cube

def detail(model,phase):
    original=t.finish(q.refit(p.polish(f.refine_model(r.repair_model({'elements':c.body(phase),'textures':c.TEX},phase),phase),phase),phase),phase)
    if model['elements']!=original['elements'] or model['textures']!=original['textures']:raise ValueError('unexpected body')
    e=copy.deepcopy(model['elements'])
    def change(old,new):
        if e.count(old)!=1:raise ValueError('missing or ambiguous part '+str(old['from']))
        e[e.index(old)]=new
    def add(a,b,tex):e.append(C(a,b,tex))
    # Extend the original two door-window pillars down along their exact
    # existing x/z outline until they meet the cabin floor.
    for x0,x1 in ((-.65,.35),(15.65,16.65)):
        change(C([x0,8.5,4.8],[x1,15.4,5.5],'trim'),C([x0,1.7,4.8],[x1,15.4,5.5],'trim'))
        change(C([x0,8.55,-1.9],[x1,15.2,-1.4],'body'),C([x0,1.7,-1.9],[x1,15.2,-1.4],'body'))
    # Split the door cards at the newly extended pillars, rather than leaving
    # coplanar faces and z-fighting inside the door outline.
    for x0,x1 in ((-.65,-.48),(16.48,16.65)):
        old=C([x0,1.7,-2.3],[x1,5.4,17.3],'trim')
        if e.count(old)!=1:raise ValueError('unexpected door card')
        e.remove(old)
        for z0,z1 in ((-2.3,-1.9),(-1.4,4.8),(5.5,17.3)):
            add([x0,1.7,z0],[x1,5.4,z1],'trim')
    # The divider remains at the seat backs, extending from floor to roof.
    for x0,x1 in ((.05,.38),(15.62,15.95)):
        change(C([x0,3.9,4.47],[x1,14.95,4.79],'trim'),C([x0,1.7,4.47],[x1,15.2,4.79],'trim'))
    change(C([.38,4.,4.47],[15.62,4.25,4.79],'trim'),C([.38,1.7,4.47],[15.62,1.95,4.79],'trim'))
    change(C([.38,14.65,4.47],[15.62,14.9,4.79],'trim'),C([.38,14.95,4.47],[15.62,15.2,4.79],'trim'))
    for x in (2,4,6,8,10,12,14):
        change(C([x,4.25,4.5],[x+.14,14.65,4.65],'trim'),C([x,1.95,4.5],[x+.14,14.95,4.65],'trim'))
    # Extend the trunk lid one model pixel towards the bench.
    change(C([-1.45,8.75,-15.25],[17.45,9.2,-8.35],'body'),C([-1.45,8.75,-15.25],[17.45,9.2,-7.35],'body'))
    # Wrap the visible inner sides of the rear wheelhouses up to the armrests.
    # Their inner x faces stay beyond the static tire extent (2.441/13.559).
    for x0,x1 in ((2.45,2.5),(13.5,13.55)):
        change(C([x0,1.0,-8.3],[x1,5.15,-2.9],'trim'),C([x0,1.0,-10.8],[x1,5.18,-2.9],'seat'))
    # End wall prevents seeing through the rear wheel wells toward the trunk.
    add([2.5,1.0,-10.8],[13.5,8.6,-10.6],'trim')
    # Upholstered raised inner sections form a continuation of the rear bench,
    # against the liners and under the armrest, never across the tire envelope.
    for x0,x1 in ((2.5,2.95),(13.05,13.5)):
        add([x0,3.7,-3.9],[x1,5.18,-3.0],'seat')
    result=copy.deepcopy(model);result['elements']=e;return result

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected deployed pack')
    files=c.readzip(data)
    for path,phase in zip(c.PATHS,(-1,0,1)):files[path]=c.encode(detail(json.loads(files[path]),phase))
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
