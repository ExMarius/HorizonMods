#!/usr/bin/env python3
"""Restore original wheel centres, conceal seats behind tires, attach mirrors."""
import argparse,copy,hashlib,io,json,zipfile
from pathlib import Path
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f,polish_logan_body as p,refit_police_logan as q,finish_police_logan as t,detail_police_logan as d,complete_police_logan as u,restore_police_wheels as v,seal_police_logan as s,close_logan_wheelwells as w
BASE_SHA1='2069088cc44c8c55157ed6baceba8eda16bcd9a0'
C=c.cube

def connect(model,phase):
    prev={'elements':c.body(phase),'textures':c.TEX}
    for fn in (r.repair_model,f.refine_model,p.polish,q.refit,t.finish,d.detail,u.complete,v.body,s.seal,w.close):prev=fn(prev,phase)
    if model['elements']!=prev['elements'] or model['textures']!=prev['textures']:raise ValueError('unexpected selected Logan model')
    e=copy.deepcopy(model['elements'])
    def replace(old,new):
        if e.count(old)!=1:raise ValueError('missing or ambiguous part '+str(old['from']))
        e[e.index(old)]=new
    def add(a,b,tex):e.append(C(a,b,tex))
    # Widen the dark BACKING, not the tire. It sits just inward of the
    # static tire's inner x extent (2.441/13.559), hiding the seat material
    # and exterior structures exposed through the fender openings.
    for x0,x1 in ((2.45,2.5),(13.5,13.55)):
        for z0,z1 in ((-11.65,-2.9),(19.,28.85)):
            old=C([x0,1.,z0],[x1,5.2,z1],'trim')
            if z0 < 0:
                ax,bx=(2.46,2.49) if x0<8 else (13.51,13.54)
            else:
                # Full 35-degree steering sweeps tires farther inward than
                # their static x bounds; keep the front liner past that sweep.
                ax,bx=(4.72,4.75) if x0<8 else (11.25,11.28)
            replace(old,C([ax,.9,z0-.5],[bx,8.55,z1+.5],'trim'))
    # Mirror mounts touch the existing mirror bodies, door top, and A-pillar.
    add([-1.8,8.65,16.0],[-.65,9.5,17.5],'trim')
    add([16.65,8.65,16.0],[17.8,9.5,17.5],'trim')
    # Centre rear-view mirror: static decorative surface, with a roof mount.
    add([7.85,14.1,12.51],[8.15,15.2,12.9],'trim')
    add([6.85,13.55,12.4],[9.15,14.15,12.8],'trim')
    add([7.05,13.65,12.36],[8.95,14.05,12.39],'chrome')
    out=copy.deepcopy(model);out['elements']=e;return out

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected deployed pack')
    files=c.readzip(data)
    for path,phase in zip(c.PATHS,(-1,0,1)):files[path]=c.encode(connect(json.loads(files[path]),phase))
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for n,value in sorted(files.items()):
            i=zipfile.ZipInfo(n,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,value)
    return b.getvalue()
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args()
    if a.base.resolve()==a.output.resolve():ap.error('cannot overwrite base')
    data=build(a.base.read_bytes());a.output.write_bytes(data);print('SHA-1',hashlib.sha1(data).hexdigest())
if __name__=='__main__':main()
