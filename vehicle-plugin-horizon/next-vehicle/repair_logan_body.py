#!/usr/bin/env python3
"""Targeted geometry repairs for the deployed Logan body; no other assets altered."""
import argparse,copy,hashlib,io,json,zipfile
from pathlib import Path
import custom_logan_body as source
BASE_SHA1='0a0105a9f19d90d5cb37425265692a333012379b'
PATHS=source.PATHS
C=source.cube

def repair_model(model, phase):
    elements=copy.deepcopy(model['elements'])
    if elements != source.body(phase):raise ValueError('body is not the selected known revision')
    def remove(part):
        if elements.count(part)!=1:raise ValueError('part missing or ambiguous: '+str(part['from']))
        elements.remove(part)
    def replace(old,new):
        if elements.count(old)!=1:raise ValueError('part missing or ambiguous: '+str(old['from']))
        elements[elements.index(old)]=new
    def add(a,b,t):elements.append(C(a,b,t))

    # The long sills already form the door skins. Four identical overlaid skins
    # produced co-planar faces and z-fighting. Remove only the redundant copies.
    for x0,x1 in ((-1.8,-.65),(16.65,17.8)):
        remove(C([x0,1.35,-2.25],[x1,8.6,5.0],'body'))
        remove(C([x0,1.35,5.1],[x1,8.6,17.4],'body'))
    # Extrude the paint and handles farther than the underlying exterior surface.
    # Keep every trim/handle's alignment relative to the livery panel.
    for e in elements:
        if e.get('rotation'):continue
        if -1.86 <= e['from'][0] <= -1.78 and -1.86 <= e['to'][0] <= -1.78 and e['from'][2]>=-2.15 and e['to'][2]<=17.25:
            e['from'][0]=round(e['from'][0]-.06,5);e['to'][0]=round(e['to'][0]-.06,5)
        elif 17.78 <= e['from'][0] <= 17.86 and 17.78 <= e['to'][0] <= 17.86 and e['from'][2]>=-2.15 and e['to'][2]<=17.25:
            e['from'][0]=round(e['from'][0]+.06,5);e['to'][0]=round(e['to'][0]+.06,5)
    # Full continuous interior floor: meets the inner door faces and extends to
    # behind the rear seat and under the dashboard. It does not fill wheel arches.
    add([-.65,1.35,-8.3],[16.65,1.7,17.35],'trim')
    # Replace the 22.5-degree hood panel that dived into the front bumper with
    # connected stepped pieces. Adjacent surfaces slightly overlap vertically.
    replace(C([-.65,8.4,17.7],[16.65,9.0,25.0],'body'), C([-.65,8.4,17.15],[16.65,9.0,25.05],'body'))
    remove(C([-.65,8.15,25.0],[16.65,8.95,30.65],'body',{'axis':'x','angle':22.5,'origin':[8,8.95,25.0]}))
    for z0,z1,top in ((25.05,26.55,8.95),(26.55,28.05,8.80),(28.05,29.55,8.65),(29.55,31.04,8.50)):
        add([-.65,8.37,z0],[16.65,top,z1],'body')
    # Rebuild the two front seats IN FRONT of the B-pillar (z=4.8..5.5).
    # Dimensions are the actual Horizon Off-Roader seat dimensions converted
    # through the 1.42/1.38 Horizon and 1.7 Logan body scales. The rider
    # attachments remain the source Logan values; only seat geometry changes.
    for x0,x1,lo,hi in ((2.0,6.6,1.27,6.73),(9.4,14.0,9.27,14.73)):
        remove(C([x0,2.0,4.8],[x1,3.75,10.2],'seat'))
        remove(C([x0,3.4,3.9],[x1,9.45,5.15],'seat',{'axis':'x','angle':-22.5,'origin':[x0,3.4,4.4]}))
        remove(C([x0,3.55,5.0],[x0+.5,5.2,9.9],'seat'))
        remove(C([x1-.5,3.55,5.0],[x1,5.2,9.9],'seat'))
        remove(C([x0+.8,9.0,2.1],[x1-.8,11.1,3.25],'seat'))
        # 5.46 x 5.35 pixels at 1.7 ~= Horizon's 6.55 x 6.4 at 1.42.
        add([lo,1.7,5.8],[hi,2.85,11.15],'seat')
        add([lo,2.85,5.55],[hi,10.22,6.8],'seat')
        # Bolsters start at the cushion top, avoiding coplanar overlay faces.
        add([lo+.04,2.85,6.82],[lo+.55,4.1,10.95],'seat')
        add([hi-.55,2.85,6.82],[hi-.04,4.1,10.95],'seat')
        add([lo+.85,10.22,5.58],[hi-.85,11.75,6.78],'seat')
    # Other known overlapping visible planes: rear bench edges and pedal covers.
    replace(C([1.8,3.4,-5.3],[14.2,8.6,-3.8],'seat'),C([1.85,3.4,-5.3],[14.15,8.6,-3.8],'seat'))
    for x0,x1 in ((10.1,10.75),(11.35,12.0),(12.6,13.2)):
        replace(C([x0,2.05,13.25],[x1,2.25,14.0],'chrome'),C([x0+.03,2.2,13.25],[x1-.03,2.35,14.0],'chrome'))
    replace(C([-1.5,1.35,30.95],[17.5,1.75,31.75],'trim'),C([-1.5,1.31,30.95],[17.5,1.75,31.75],'trim'))
    replace(C([-1.6,1.45,-15.85],[17.6,1.8,-15.65],'trim'),C([-1.64,1.45,-15.85],[17.64,1.8,-15.65],'trim'))
    model=copy.deepcopy(model);model['elements']=elements;return model

def repair(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected deployed pack')
    files=source.readzip(data)
    for path,phase in zip(PATHS,(-1,0,1)):
        files[path]=source.encode(repair_model(json.loads(files[path]),phase))
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name,value in sorted(files.items()):
            i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,value)
    return out.getvalue()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('base',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.base.resolve()==a.output.resolve():p.error('output must differ from input')
    data=repair(a.base.read_bytes());a.output.write_bytes(data);print('SHA-1',hashlib.sha1(data).hexdigest(),'SHA-256',hashlib.sha256(data).hexdigest())
if __name__=='__main__':main()
