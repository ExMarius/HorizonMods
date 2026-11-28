#!/usr/bin/env python3
"""Refine the verified installed Logan model while retaining its physical rig."""
import argparse,copy,hashlib,io,json,zipfile
from pathlib import Path
import custom_logan_body as base
import repair_logan_body as previous
BASE_SHA1='9d73687b1be4272c02c7acd91ed8408e9f3faf02'
C=base.cube

def refine_model(model,phase):
    expected=previous.repair_model({'elements':base.body(phase)},phase)['elements']
    elements=copy.deepcopy(model['elements'])
    if elements!=expected:raise ValueError('unexpected current Logan model')
    def replace(old,new):
        if elements.count(old)!=1:raise ValueError('missing or ambiguous element '+str(old['from']))
        elements[elements.index(old)]=new
    # Shorten only the body beyond the front wheel opening. Do not move axles,
    # wheels, steering geometry, or the wheel-arch edging. Smoothly compress the
    # nose ahead of its wheel-well tangent, including hood, lights and bumper.
    def nose(z):return round(28.85+(z-28.85)*.60,5) if z>28.85 else z
    for e in elements:
        e['from'][2]=nose(e['from'][2]);e['to'][2]=nose(e['to'][2])
        if 'rotation' in e:e['rotation']['origin'][2]=nose(e['rotation']['origin'][2])
    # Put the front seat backs slightly behind the B pillar, keeping cushions
    # under the original rider anchors, with useful front footwell clearance.
    for lo,hi in ((1.27,6.73),(9.27,14.73)):
        for old,new in [
            (C([lo,1.7,5.8],[hi,2.85,11.15],'seat'),C([lo,1.7,5.05],[hi,2.85,10.4],'seat')),
            (C([lo,2.85,5.55],[hi,10.22,6.8],'seat'),C([lo,2.85,4.8],[hi,10.22,6.05],'seat')),
            (C([lo+.04,2.85,6.82],[lo+.55,4.1,10.95],'seat'),C([lo+.04,2.85,6.07],[lo+.55,4.1,10.2],'seat')),
            (C([hi-.55,2.85,6.82],[hi-.04,4.1,10.95],'seat'),C([hi-.55,2.85,6.07],[hi-.04,4.1,10.2],'seat')),
            (C([lo+.85,10.22,5.58],[hi-.85,11.75,6.78],'seat'),C([lo+.85,10.22,4.83],[hi-.85,11.75,6.03],'seat')),
        ]:replace(old,new)
    # Full-width rear bench. Join the back to the cushion without overlaying
    # the same visible face, retain both rear passenger anchors and headrests.
    replace(C([1.8,1.9,-3.9],[7.3,3.7,1.5],'seat'),C([.55,1.7,-3.9],[15.45,3.7,1.5],'seat'))
    elements.remove(C([8.7,1.9,-3.9],[14.2,3.7,1.5],'seat'))
    replace(C([1.85,3.4,-5.3],[14.15,8.6,-3.8],'seat'),C([.58,3.7,-5.3],[15.42,8.6,-3.9],'seat'))
    # Extend dashboard into the bonnet while leaving the existing wheel and
    # steering-wheel attachments alone. Move its cluster/console as a unit.
    dash=[
        ([.5,6,14.35],[15.5,8.45,17.25],'dash'),
        ([9.25,8.45,14.5],[14.6,9.05,16.25],'trim'),
        ([9.7,8.7,14.44],[14.1,8.95,14.53],'chrome'),
        ([6.45,5.4,13.55],[9.55,8.3,16.0],'trim'),
        ([6.95,7.05,13.48],[9.05,8.05,13.56],'chrome'),
        ([7.2,6.1,13.43],[7.55,6.4,13.53],'amber'),
        ([8.0,6.1,13.43],[8.35,6.4,13.53],'chrome')]
    for a,b,t in dash:
        na=a.copy();nb=b.copy();na[2]=round(na[2]+.45,5);nb[2]=round(nb[2]+.45,5)
        replace(C(a,b,t),C(na,nb,t))
    # Extend footwell and transmission tunnel surfaces to the shifted dash.
    elements.append(C([.35,1.7,13.5],[15.65,1.82,17.8],'dash'))
    # Lower interior door cards meet the continuous floor and upper sills.
    elements.extend((C([-.65,1.7,-7.9],[-.48,5.4,17.3],'trim'),
                     C([16.48,1.7,-7.9],[16.65,5.4,17.3],'trim')))
    # Reverse antenna lean without moving its mounting point.
    replace(C([7.87,16.15,-1.8],[8.13,18.4,-1.54],'trim',{'axis':'x','angle':22.5,'origin':[8.0,16.15,-1.7]}),
            C([7.87,16.15,-1.8],[8.13,18.4,-1.54],'trim',{'axis':'x','angle':-22.5,'origin':[8.0,16.15,-1.7]}))
    for e in elements:
        if any(not -16<=v<=32 for k in ('from','to') for v in e[k]):raise ValueError('invalid model coordinate')
    out=copy.deepcopy(model);out['elements']=elements;return out

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected deployed pack')
    files=base.readzip(data)
    for path,phase in zip(base.PATHS,(-1,0,1)):
        files[path]=base.encode(refine_model(json.loads(files[path]),phase))
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for n,v in sorted(files.items()):
            i=zipfile.ZipInfo(n,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,v)
    return b.getvalue()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('base',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.base.resolve()==a.output.resolve():p.error('cannot overwrite base')
    data=build(a.base.read_bytes());a.output.write_bytes(data);print('SHA-1',hashlib.sha1(data).hexdigest())
if __name__=='__main__':main()
