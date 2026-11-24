#!/usr/bin/env python3
"""Align Logan wheelhouse joints and eliminate upholstery on the underbody."""
import argparse,copy,hashlib,io,json,zipfile
from pathlib import Path
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f,polish_logan_body as p,refit_police_logan as q,finish_police_logan as t,detail_police_logan as d,complete_police_logan as u,restore_police_wheels as v
BASE_SHA1='9159951f45d8449c9e70f4e9a925f1d537df207b'
C=c.cube

def seal(model,phase):
    prev={'elements':c.body(phase),'textures':c.TEX}
    for fn in (r.repair_model,f.refine_model,p.polish,q.refit,t.finish,d.detail,u.complete,v.body):prev=fn(prev,phase)
    if model['elements']!=prev['elements'] or model['textures']!=prev['textures']:raise ValueError('unexpected selected Logan model')
    e=copy.deepcopy(model['elements'])
    def replace(old,new):
        if e.count(old)!=1:raise ValueError('missing or ambiguous part '+str(old['from']))
        e[e.index(old)]=new
    # This plate was explicitly assigned the seat texture, and is exposed on
    # the underside. Use the same dark mechanical material as the chassis.
    replace(C([4.1,-.18,-2.2],[11.9,-.08,4.4],'seat'),C([4.1,-.18,-2.2],[11.9,-.08,4.4],'trim'))
    # Backrests meet the armrests along their entire width; split the small
    # armrest pads at the backrests instead of stacking them in the same space.
    for lo,hi,pad0,pad1 in ((-.55,2.5,-.55+.25,2.45-.25),(13.5,16.55,13.55+.25,16.55-.25)):
        replace(C([lo,6.18,-5.3],[hi,8.6,-3.9],'seat'),C([lo,6.0,-5.3],[hi,8.6,-3.9],'seat'))
        pad=C([pad0,6.0,-7.8],[pad1,6.18,-3.5],'seat')
        if e.count(pad)!=1:raise ValueError('unexpected armrest pad')
        e.remove(pad)
        for z0,z1 in ((-7.8,-5.3),(-3.9,-3.5)):
            e.append(C([pad0,6.0,z0],[pad1,6.18,z1],'seat'))
    for lo,hi in ((2.45,2.5),(13.5,13.55)):
        replace(C([lo,1.0,-10.8],[hi,5.18,-2.9],'seat'),C([lo,1.0,-10.8],[hi,5.2,-2.9],'seat'))
    # Do not show upholstery on the underside of cushions or liners. Keep
    # their inward/upward visible seat faces untouched.
    for part in e:
        down=part['faces'].get('down')
        if down and down['texture']=='#seat':down['texture']='#trim'
    # Split rear wheelhouse roofs around the adjacent armrests. They now meet
    # rather than overlap, including the narrow outer strip and inside liner.
    for lo,hi,outer0,outer1 in ((-.65,2.44,-.65,-.55),(13.56,16.65,16.55,16.65)):
        old=C([lo,5.2,-11.1],[hi,5.44,-2.9],'trim')
        if e.count(old)!=1:raise ValueError('unexpected rear liner roof')
        e.remove(old)
        edge=2.5 if lo<0 else 13.5
        a,b=(lo,edge) if lo<0 else (edge,hi)
        for z0,z1 in ((-11.1,-8.3),(-3.0,-2.9)):
            e.append(C([a,5.2,z0],[b,5.44,z1],'trim'))
        e.append(C([outer0,5.2,-8.3],[outer1,5.44,-3.0],'trim'))
        inner0,inner1=(2.45,2.5) if lo<0 else (13.5,13.55)
        e.append(C([inner0,5.2,-8.3],[inner1,5.44,-3.0],'trim'))
    # Front roofs and end walls meet their inner liner exactly (0.01 model
    # pixel gaps were left by the previous anti-z-fighting workaround).
    for z0,z1 in ((19.25,28.65),):
        for a,b,aa,bb in ((-.65,2.44,-.65,2.45),(13.56,16.65,13.55,16.65)):
            replace(C([a,5.2,z0],[b,5.44,z1],'trim'),C([aa,5.2,z0],[bb,5.44,z1],'trim'))
    for z0,z1 in ((-11.3,-11.1),(19.0,19.25),(28.65,28.85)):
        for a,b,aa,bb in ((-.65,2.44,-.65,2.45),(13.56,16.65,13.55,16.65)):
            replace(C([a,1.35,z0],[b,5.2,z1],'trim'),C([aa,1.35,z0],[bb,5.2,z1],'trim'))
    out=copy.deepcopy(model);out['elements']=e;return out

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected deployed pack')
    files=c.readzip(data)
    for path,phase in zip(c.PATHS,(-1,0,1)):files[path]=c.encode(seal(json.loads(files[path]),phase))
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
