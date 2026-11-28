#!/usr/bin/env python3
"""Match the rear fenders to the restored wheel centres and keep liners clear."""
import argparse,copy,hashlib,io,json,zipfile
from pathlib import Path
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f,polish_logan_body as p,refit_police_logan as q,finish_police_logan as t,detail_police_logan as d,complete_police_logan as u,restore_police_wheels as v,seal_police_logan as s,close_logan_wheelwells as w,connect_logan_mirrors as m
BASE_SHA1=m.BASE_SHA1
C=c.cube

def fix(model,phase):
    prev={'elements':c.body(phase),'textures':c.TEX}
    for fn in (r.repair_model,f.refine_model,p.polish,q.refit,t.finish,d.detail,u.complete,v.body,s.seal,w.close,m.connect):prev=fn(prev,phase)
    if model['elements']!=prev['elements'] or model['textures']!=prev['textures']:raise ValueError('unexpected selected Logan model')
    e=copy.deepcopy(model['elements'])
    def replace(old,new):
        if e.count(old)!=1:raise ValueError('missing or ambiguous part '+str(old['from']))
        e[e.index(old)]=new
    for x0,x1 in ((-1.8,-.65),(16.65,17.8)):
        # Original arch was centered one pixel ahead of the actual wheel as
        # transformed by the body item-display yaw. Move its contour, NOT the wheel.
        replace(C([x0,1.35,-15.3],[x1,5.5,-11.65],'body'),C([x0,1.35,-15.3],[x1,5.5,-12.65],'body'))
        replace(C([x0,1.35,-2.3],[x1,5.5,19.0],'body'),C([x0,1.35,-3.3],[x1,5.5,19.0],'body'))
        replace(C([x0,5.17,-11.65],[x1,5.5,-2.3],'body'),C([x0,5.17,-12.65],[x1,5.5,-3.3],'body'))
        for a,b,y in ((-4.65,-3.85,4.28),(-3.85,-3.1,4.88),(-3.1,-2.2,4.88),(2.2,3.1,4.88),(3.1,3.85,4.88),(3.85,4.65,4.28)):
            old=C([x0,y,round(-6.95+a,5)],[x1,5.17,round(-6.95+b,5)],'body')
            new=C([x0,y,round(-7.95+a,5)],[x1,5.17,round(-7.95+b,5)],'body')
            replace(old,new)
    # Each of the nine edge segments on each side follows the same offset.
    for x0,x1 in ((-1.86,-1.8),(17.8,17.86)):
        found=[a for a in e if a['from'][0]==x0 and a['to'][0]==x1 and a['from'][2]<0 and a['to'][2]<0 and a['faces']['west']['texture']=='#trim']
        if len(found)!=9:raise ValueError('unexpected rear edge segments')
        for a in found:
            a['from'][2]=round(a['from'][2]-1,5);a['to'][2]=round(a['to'][2]-1,5)
    # The old cross wall and underside panel actually entered the rear wheel
    # sweep at the restored centre. Pull them back beyond a conservative radius.
    for x0,x1 in ((-.65,2.45),(13.55,16.65)):
        replace(C([x0,1.35,-11.3],[x1,5.2,-11.1],'trim'),C([x0,1.35,-12.65],[x1,5.2,-12.4],'trim'))
    replace(C([-1.5,0,-15.3],[17.5,1.35,-11.1],'trim'),C([-1.5,0,-15.3],[17.5,1.35,-12.1],'trim'))
    replace(C([2.5,0,-11.1],[13.5,1.,-10.8],'trim'),C([2.5,0,-12.1],[13.5,1.,-10.8],'trim'))
    for x0,x1 in ((-.65,2.5),(13.5,16.65)):
        replace(C([x0,5.2,-11.1],[x1,5.44,-8.3],'trim'),C([x0,5.2,-12.4],[x1,5.44,-8.3],'trim'))
    for x0,x1 in ((2.46,2.49),(13.51,13.54)):
        replace(C([x0,.9,-12.15],[x1,8.55,-2.4],'trim'),C([x0,.9,-13.15],[x1,8.55,-2.4],'trim'))
    out=copy.deepcopy(model);out['elements']=e;return out

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected deployed pack')
    files=c.readzip(m.build(data,expected))
    for path,phase in zip(c.PATHS,(-1,0,1)):files[path]=c.encode(fix(json.loads(files[path]),phase))
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
