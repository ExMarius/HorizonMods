#!/usr/bin/env python3
"""Close the Logan footwell, clear wheel wells and refine the police nose."""
import argparse,copy,hashlib,io,json,zipfile
from pathlib import Path
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f
BASE_SHA1='566045f084e745bf4b76706435c573763ec07e74'
C=c.cube

def polish(model,phase):
    expected=f.refine_model(r.repair_model({'elements':c.body(phase)},phase),phase)['elements']
    e=copy.deepcopy(model['elements'])
    if e!=expected:raise ValueError('unexpected Logan body revision')
    def change(old,new):
        if e.count(old)!=1:raise ValueError('unexpected body part '+str(old['from']))
        e[e.index(old)]=new
    def add(a,b,t):e.append(C(a,b,t))
    # The long full-width chassis used to run through all four wider Horizon
    # tires. A central spine and the cabin floor retain structure without doing so.
    change(C([0,0,-10.8],[16,1.0,27.5],'trim'),C([2.4,0,-10.8],[13.6,1.0,27.5],'trim'))
    for x0,x1 in ((-.65,-.48),(16.48,16.65)):
        change(C([x0,1.7,-7.9],[x1,5.4,17.3],'trim'),C([x0,1.7,-2.3],[x1,5.4,17.3],'trim'))
    # Close both footwells from floor to dashboard/cowl: a firewall, with its
    # lower edge meeting the entire floor and upper edge under the hood.
    add([-.65,1.699,17.35],[16.65,8.38,18.05],'dash')
    # Connect arch edges to the upper quarter panels above the tire's maximum
    # static height, leaving each well open below for turning/spinning tires.
    for x0,x1 in ((-1.8,-.65),(16.65,17.8)):
        for z0,z1 in ((-11.65,-2.3),(19.0,28.85)):
            add([x0,5.17,z0],[x1,5.5,z1],'body')
    # Replace the blocky upper grille with a narrow, symmetric Logan-inspired
    # black grille, chrome lip, compact center badge, and horizontal highlights.
    for old in (
        C([3.35,5,30.182],[12.65,7.75,30.62],'grille'),
        C([3.35,7.75,30.17],[12.65,7.93,30.632],'chrome'),
        C([3.35,4.83,30.542],[12.65,5,30.65],'chrome'),
        C([7.1,5.45,30.62],[8.9,7.3,30.686],'chrome'),
        C([7.4,5.75,30.686],[8.6,7.05,30.716],'grille')):
        if e.count(old)!=1:raise ValueError('unexpected grille');
        e.remove(old)
    add([3.4,5.45,30.20],[12.6,7.55,30.62],'grille')
    add([3.4,7.56,30.19],[12.6,7.72,30.64],'chrome')
    add([3.7,5.65,30.625],[12.3,5.78,30.68],'chrome')
    add([3.7,6.38,30.625],[12.3,6.51,30.68],'chrome')
    add([7.15,5.92,30.69],[8.85,7.15,30.77],'chrome')
    add([7.42,6.12,30.78],[8.58,6.96,30.82],'grille')
    # Word-free blue bonnet accent, using the existing Romanian-police palette.
    e.append({'from':[5.1,9.011,18.15],'to':[10.9,9.011,24.7],
              'faces':{'up':{'texture':'#livery','uv':[0,0,16,16]}}})
    # Small livery strips on the fenders remain above the wheel openings.
    for side,x in (('west',-1.87),('east',17.87)):
        for z0,z1 in ((-11.5,-2.5),(19.2,28.65)):
            e.append({'from':[x,7.0,z0],'to':[x,8.25,z1],
                      'faces':{side:{'texture':'#livery','uv':[0,0,16,16]}}})
    result=copy.deepcopy(model);result['elements']=e;return result

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected deployed pack')
    files=c.readzip(data)
    for path,phase in zip(c.PATHS,(-1,0,1)):
        files[path]=c.encode(polish(json.loads(files[path]),phase))
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
