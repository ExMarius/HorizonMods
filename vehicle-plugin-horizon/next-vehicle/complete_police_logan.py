#!/usr/bin/env python3
"""Complete rear interior, wheel-arch metal and underbody of the police Logan."""
import argparse,copy,hashlib,io,json,zipfile
from pathlib import Path
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f,polish_logan_body as p,refit_police_logan as q,finish_police_logan as t,detail_police_logan as d
BASE_SHA1='b2db5a9cec7d4d81eeaba9d3dcd77c3ca3efa235'
C=c.cube

def complete(model,phase):
    prev=d.detail(t.finish(q.refit(p.polish(f.refine_model(r.repair_model({'elements':c.body(phase),'textures':c.TEX},phase),phase),phase),phase),phase),phase)
    if model['elements']!=prev['elements'] or model['textures']!=prev['textures']:raise ValueError('unexpected body revision')
    e=copy.deepcopy(model['elements'])
    def change(old,new):
        if e.count(old)!=1:raise ValueError('missing or ambiguous part '+str(old['from']))
        e[e.index(old)]=new
    def add(a,b,tex):e.append(C(a,b,tex))
    # Fill the two holes per side: lower joins the wheelhouse armrest and the
    # rear window pillar; upper is an upholstered extension of the backrest.
    for x0,x1 in ((-.55,2.45),(13.55,16.55)):
        add([x0,3.7,-3.0],[x1,5.17,-1.89],'seat')
    for x0,x1 in ((-.55,2.5),(13.5,16.55)):
        add([x0,6.18,-5.3],[x1,8.6,-3.9],'seat')
    # Body-colour infill between each stepped arch trim and its upper fender.
    # All pieces are above/outside a 4.1px radius swept envelope of the tires;
    # the central openings themselves remain unobstructed.
    for x0,x1 in ((-1.8,-.65),(16.65,17.8)):
        for z in (-6.95,23.95):
            for a,b,y in ((-4.65,-3.85,4.28),(-3.85,-3.1,4.88),(-3.1,-2.2,4.88),
                          (2.2,3.1,4.88),(3.1,3.85,4.88),(3.85,4.65,4.28)):
                add([x0,y,round(z+a,5)],[x1,5.17,round(z+b,5)],'body')
    # Remove the loose rear underside strip, which looked like an unattached
    # hook. Extend the centre chassis to both ends and add wheel-safe pans.
    loose=C([7.2,-.24,-15.7],[8.8,0,-10.75],'trim')
    if e.count(loose)!=1:raise ValueError('unexpected rear strip')
    e.remove(loose)
    change(C([2.5,0,-10.8],[13.5,1.,27.5],'trim'),C([2.5,-.08,-10.8],[13.5,1.,27.5],'trim'))
    for x0,x1 in ((-1.6,2.5),(13.5,17.6)):
        add([x0,0,-2.3],[x1,.9,17.5],'trim')
    add([-1.5,0,-15.3],[17.5,1.35,-11.1],'trim')
    add([-1.49,0,29.0],[17.49,1.35,30.14],'trim')
    add([2.5,0,-11.1],[13.5,1.,-10.8],'trim')
    add([2.5,0,27.5],[13.5,1.,29.0],'trim')
    # Underbody detail stays attached to the bottom plate, not a free hook.
    add([4.1,-.18,-2.2],[11.9,-.08,4.4],'seat')
    add([5.2,-.18,12.0],[10.8,-.08,18.5],'trim')
    result=copy.deepcopy(model);result['elements']=e;return result

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected deployed pack')
    files=c.readzip(data)
    for path,phase in zip(c.PATHS,(-1,0,1)):files[path]=c.encode(complete(json.loads(files[path]),phase))
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
