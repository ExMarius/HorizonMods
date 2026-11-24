#!/usr/bin/env python3
"""Refit the Dacia cabin and wheel wells without moving original wheel centres."""
import argparse,copy,hashlib,io,json,struct,zlib,zipfile
from pathlib import Path
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f,polish_logan_body as p
BASE_SHA1='ba7b73145f5312aac04d4158d2340576da4afb9e'
C=c.cube
ADDITIONS={'assets/vehicle/items/dacia_police_steering.json','assets/daciapolice/models/item/steering.json','assets/daciapolice/textures/item/smoked_glass.png'}

def smoked_texture():
    # Binary-alpha stippling is intentionally used instead of unsupported
    # translucent render-type extensions in vanilla item displays.
    rows=b''.join(b'\x00'+b''.join(bytes((42,52,61,255 if (x+y)%2==0 else 0)) for x in range(16)) for y in range(16))
    def chunk(name,data):return struct.pack('!I',len(data))+name+data+struct.pack('!I',zlib.crc32(name+data)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!IIBBBBB',16,16,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(rows,9))+chunk(b'IEND',b'')

def steering():
    e=[]
    def add(a,b,t):e.append(C(a,b,t))
    # Ring and spokes in local X/Z plane, turning around local Y along with
    # the steering animation. Shaft extends toward the dashboard after tilt.
    add([4,7.5,4.8],[4.65,8.5,11.2],'trim');add([11.35,7.5,4.8],[12,8.5,11.2],'trim')
    add([4.65,7.5,4],[11.35,8.5,4.65],'trim');add([4.65,7.5,11.35],[11.35,8.5,12],'trim')
    for x0,x1 in ((4,4.65),(11.35,12)):
        for z0,z1 in ((4,4.8),(11.2,12)):add([x0,7.55,z0],[x1,8.45,z1],'trim')
    add([4.65,7.65,7.6],[11.35,8.35,8.4],'trim')
    add([7.3,7.5,8.4],[8.7,8.5,11.35],'trim')
    add([6.9,8.5,6.9],[9.1,8.8,9.1],'chrome')
    add([7.25,0.8,7.25],[8.75,7.5,8.75],'trim')
    return {'textures':{'trim':'daciapolice:item/logan_trim','chrome':'daciapolice:item/logan_chrome'},'elements':e}

def refit(model,phase):
    old=p.polish(f.refine_model(r.repair_model({'elements':c.body(phase)},phase),phase),phase)
    if model['elements']!=old['elements']:raise ValueError('unexpected body revision')
    e=copy.deepcopy(model['elements'])
    def change(old,new):
        if e.count(old)!=1:raise ValueError('missing or ambiguous '+str(old['from']))
        e[e.index(old)]=new
    def add(a,b,t):e.append(C(a,b,t))
    # Original rear wheel centres are x=-.2 and 16.2. At their inner edge,
    # Horizon hubs extend to x=2.441/13.559. The rear bench and floor are
    # narrowed only where the wheel wells actually pass through them.
    change(C([.55,1.7,-3.9],[15.45,3.7,1.5],'seat'),C([2.5,1.7,-3.9],[13.5,3.7,1.5],'seat'))
    change(C([.58,3.7,-5.3],[15.42,8.6,-3.9],'seat'),C([2.5,3.7,-5.3],[13.5,8.6,-3.9],'seat'))
    for x0,x1 in ((.55,2.5),(13.5,15.45)):add([x0,1.7,-2.9],[x1,3.7,1.5],'seat')
    change(C([-.65,1.35,-8.3],[16.65,1.7,17.35],'trim'),C([2.5,1.35,-8.3],[13.5,1.7,-2.9],'trim'))
    add([-.65,1.35,-2.9],[16.65,1.7,17.35],'trim')
    change(C([-.65,1.699,17.35],[16.65,8.38,18.05],'dash'),C([-.65,1.699,17.35],[16.65,8.38,18.05],'trim'))
    change(C([2.4,0,-10.8],[13.6,1.0,27.5],'trim'),C([2.5,0,-10.8],[13.5,1.0,27.5],'trim'))
    # Interior-facing wheel-well liners close the sides of the narrowed floor
    # without crossing the static inner tire bounds.
    for x0,x1 in ((2.45,2.5),(13.5,13.55)):
        add([x0,1.0,-8.3],[x1,5.15,-2.9],'trim')
    # Reinforced underside strips remain within the clear central tunnel.
    for x0,x1 in ((2.55,3.1),(12.9,13.45)):
        add([x0,-.2,-10.7],[x1,0,27.4],'trim')
    add([7.2,-.24,-15.7],[8.8,0,-10.75],'trim')
    # Open, see-through safety partition immediately behind the front backs.
    for x0,x1 in ((.05,.38),(15.62,15.95)):
        add([x0,3.9,3.1],[x1,14.95,3.42],'trim')
    for y0,y1 in ((4.0,4.25),(14.65,14.9)):
        add([.38,y0,3.1],[15.62,y1,3.42],'trim')
    for x in (2,4,6,8,10,12,14):add([x,4.25,3.13],[x+.14,14.65,3.28],'trim')
    for y in (7.2,10.8):add([.4,y,3.29],[15.6,y+.14,3.43],'trim')
    # Flat dithered rear side windows. Only outer faces are drawn to avoid
    # coincident doubled surfaces; alpha holes remain visible from both sides
    # in the vanilla double-sided item renderer only if that renderer permits.
    for side,x in (('west',-.70),('east',16.70)):
        e.append({'from':[x,9.05,-5.35],'to':[x,14.85,-2.02],
                  'faces':{side:{'texture':'#smoked','uv':[0,0,16,16]},
                           ('east' if side=='west' else 'west'):{'texture':'#smoked','uv':[0,0,16,16]}}})
    # Bring rear lamps/plate forward of the tail surface, add dark lower bumper
    # and a small chrome bar; the front lower lip gains a matching highlight.
    for x0,x1 in ((-1.15,2.6),(13.4,17.15)):
        change(C([x0,5.3,-15.7],[x1,8.4,-15.52],'tail'),C([x0,5.3,-15.92],[x1,8.4,-15.8],'tail'))
    change(C([4.75,5.2,-15.72],[11.25,6.3,-15.56],'plate'),C([4.75,5.2,-15.93],[11.25,6.3,-15.8],'plate'))
    add([-1.45,1.85,-15.98],[17.45,2.45,-15.87],'trim')
    add([5.1,7.4,-15.96],[10.9,7.58,-15.93],'chrome')
    add([3.1,1.82,30.60],[12.9,1.98,30.72],'chrome')
    result=copy.deepcopy(model);result['elements']=e;result['textures']['smoked']='daciapolice:item/smoked_glass';return result

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected deployed pack')
    files=c.readzip(data)
    if ADDITIONS & set(files):raise ValueError('resource collision')
    for path,phase in zip(c.PATHS,(-1,0,1)):files[path]=c.encode(refit(json.loads(files[path]),phase))
    files['assets/vehicle/items/dacia_police_steering.json']=c.encode({'model':{'type':'minecraft:model','model':'daciapolice:item/steering'}})
    files['assets/daciapolice/models/item/steering.json']=c.encode(steering())
    files['assets/daciapolice/textures/item/smoked_glass.png']=smoked_texture()
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
