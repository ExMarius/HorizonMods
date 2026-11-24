#!/usr/bin/env python3
"""Close visible gaps behind the Logan tires using full-height inner liners."""
import argparse,copy,hashlib,io,json,zipfile
from pathlib import Path
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f,polish_logan_body as p,refit_police_logan as q,finish_police_logan as t,detail_police_logan as d,complete_police_logan as u,restore_police_wheels as v,seal_police_logan as s
BASE_SHA1='c8a29468657a7a4b08c47bc657a372280073e924'
C=c.cube

def close(model,phase):
    prev={'elements':c.body(phase),'textures':c.TEX}
    for fn in (r.repair_model,f.refine_model,p.polish,q.refit,t.finish,d.detail,u.complete,v.body,s.seal):prev=fn(prev,phase)
    if model['elements']!=prev['elements'] or model['textures']!=prev['textures']:raise ValueError('unexpected selected Logan model')
    elements=copy.deepcopy(model['elements'])
    for x0,x1 in ((2.45,2.5),(13.5,13.55)):
        for z0,z1,texture in ((-10.8,-2.9,'#seat'),(19.25,28.65,'#trim')):
            found=[a for a in elements if a['from']==[x0,1.0,z0] and a['to']==[x1,5.2,z1] and a['faces']['east']['texture']==texture]
            if len(found)!=1:raise ValueError('missing or ambiguous wheelhouse inner liner')
            part=found[0]
            # Extend backing to both ends of the actual wheel opening. The
            # plane remains just inside the tire's maximum static X extent.
            part['from'][2],part['to'][2]=(-11.65,-2.9) if z0<0 else (19.0,28.85)
            for face in part['faces'].values():face['texture']='#trim'
    # Join each rear end panel to the liner and seat without leaving a thin
    # vertical slit by the B-pillar. It begins exactly where the liner ends.
    for oldx,newx in (((-.55,2.45),(-.55,2.5)),((13.55,16.55),(13.5,16.55))):
        found=[a for a in elements if a['from']==[oldx[0],3.7,-3.0] and a['to']==[oldx[1],5.17,-1.89]]
        if len(found)!=1:raise ValueError('missing rear end panel')
        found[0]['from'][0],found[0]['to'][0]=newx
        found[0]['from'][2]=-2.9
    out=copy.deepcopy(model);out['elements']=elements;return out

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected deployed pack')
    files=c.readzip(data)
    for path,phase in zip(c.PATHS,(-1,0,1)):files[path]=c.encode(close(json.loads(files[path]),phase))
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
