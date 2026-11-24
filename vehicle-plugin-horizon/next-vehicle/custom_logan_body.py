#!/usr/bin/env python3
"""Hand-authored replacement cabin and body, aligned to existing Paper Logan rig.

Coordinates are explicit model pixels, not a generated sedan template. The wheel
and seat attachments are unchanged; this model is new and deliberately replaces
all old body elements. Existing user-owned Horizon textures are reused.
"""
import argparse, copy, hashlib, io, json, zipfile
from pathlib import Path
from prepare_police import readzip
BASE_SHA1='8bd4d0043b7dde65dc761b87cfc667041acd8ec5'
MODEL='assets/daciapolice/models/item/body.json'
PATHS=[MODEL, 'assets/daciapolice/models/item/body_flash_0.json', 'assets/daciapolice/models/item/body_flash_1.json']
TEX={
 'body':'daciapolice:item/logan_body_white', 'trim':'daciapolice:item/logan_trim',
 'seat':'daciapolice:item/horizon_seat', 'chrome':'daciapolice:item/logan_chrome',
 'dash':'daciapolice:item/custom_dash', 'grille':'daciapolice:item/logan_grille',
 'head':'daciapolice:item/logan_headlamp', 'tail':'daciapolice:item/logan_tail',
 'plate':'daciapolice:item/logan_plate', 'livery':'daciapolice:item/logan_livery',
 'red':'daciapolice:item/horizon_siren_red','blue':'daciapolice:item/horizon_siren_blue',
 'red_dim':'daciapolice:item/siren_red_dim','blue_dim':'daciapolice:item/siren_blue_dim',
 'amber':'daciapolice:item/custom_amber',
}
ROOT=Path(__file__).resolve().parents[2]
def encode(x):return json.dumps(x,separators=(',',':')).encode()
def cube(frm,to,tex,rotation=None):
    faces={k:{'texture':'#'+tex,'uv':[0,0,16,16]} for k in ('north','south','west','east','up','down')}
    if tex=='body':
        for face in faces.values():face['tintindex']=0
    e={'from':frm,'to':to,'faces':faces}
    if rotation is not None:e['rotation']=rotation
    return e

def body(phase):
    E=[]
    def part(lo,hi,t,rot=None):E.append(cube(lo,hi,t,rot))
    # Floor/chassis: no opaque panels across the cabin or wheel wells.
    part([0,0,-10.8],[16,1.0,27.5],'trim')
    part([-1.8,.9,-2.3],[17.8,1.35,17.5],'body')
    # Lower quarter panels end at the wheel wells, rather than covering the tires.
    for x0,x1 in ((-1.8,-.65),(16.65,17.8)):
        part([x0,1.35,-15.3],[x1,5.5,-11.65],'body')
        part([x0,1.35,-2.3],[x1,5.5,19.0],'body')
        part([x0,1.35,28.85],[x1,5.5,31.0],'body')
        # Upper sills bridge over the front and rear wheel openings.
        part([x0,5.5,-15.3],[x1,8.65,31.0],'body')
    # Wheel-arch surrounds follow each separate opening. They use short angled
    # pieces instead of a solid rectangle, so Horizon tires remain unobstructed.
    for x0,x1 in ((-1.86,-1.80),(17.80,17.86)):
        for z in (-6.95,23.95):
            part([x0,5.18,z-2.2],[x1,5.48,z+2.2],'trim')
            part([x0,4.88,z-3.1],[x1,5.48,z-2.2],'trim')
            part([x0,4.28,z-3.85],[x1,4.88,z-3.1],'trim')
            part([x0,3.4,z-4.65],[x1,4.28,z-3.85],'trim')
            part([x0,4.88,z+2.2],[x1,5.48,z+3.1],'trim')
            part([x0,4.28,z+3.1],[x1,4.88,z+3.85],'trim')
            part([x0,3.4,z+3.85],[x1,4.28,z+4.65],'trim')
            part([x0,1.55,z-4.88],[x1,3.4,z-4.62],'trim')
            part([x0,1.55,z+4.62],[x1,3.4,z+4.88],'trim')
    # Bumper wings and the front apron, scaled for the existing Logan grille.
    part([-1.55,1.6,29.8],[17.55,5.55,31.65],'body')
    part([-1.55,5.55,29.65],[17.55,8.4,31.05],'body')
    part([-1.5,1.35,30.95],[17.5,1.75,31.75],'trim')
    # Bonnet: two levels and a sloping leading panel with proper legal rotation.
    part([-.65,8.4,17.7],[16.65,9.0,25.0],'body')
    part([-.65,8.15,25.0],[16.65,8.95,30.65],'body',
         {'axis':'x','angle':22.5,'origin':[8,8.95,25.0]})
    part([2.0,9.015,18.0],[2.18,9.10,24.85],'chrome')
    part([13.82,9.015,18.0],[14.0,9.10,24.85],'chrome')
    # Nose: dark radiator with chrome rim, emblem, lamps, fog lamps and plate.
    part([3.35,5.0,31.07],[12.65,7.75,31.80],'grille')
    part([3.35,7.75,31.05],[12.65,7.93,31.82],'chrome')
    part([3.35,4.83,31.67],[12.65,5.0,31.85],'chrome')
    part([7.1,5.45,31.8],[8.9,7.3,31.91],'chrome')
    part([7.4,5.75,31.91],[8.6,7.05,31.96],'grille')
    part([-1.35,6.0,31.06],[3.30,8.15,31.75],'head')
    part([12.7,6.0,31.06],[17.35,8.15,31.75],'head')
    part([2.9,2.15,31.66],[13.1,3.8,31.85],'grille')
    part([2.9,2.02,31.66],[13.1,2.15,31.88],'chrome')
    part([-1.2,2.15,31.66],[2.4,4.0,31.86],'trim')
    part([13.6,2.15,31.66],[17.2,4.0,31.86],'trim')
    part([-.7,2.55,31.86],[1.8,3.45,31.95],'head')
    part([14.2,2.55,31.86],[16.7,3.45,31.95],'head')
    part([4.85,3.85,31.85],[11.15,4.8,31.96],'plate')
    # Tail and trunk, with separate light clusters and plate.
    part([-1.6,1.6,-15.8],[17.6,5.6,-13.7],'body')
    part([-1.6,5.6,-15.55],[17.6,8.75,-12.65],'body')
    part([-1.45,8.75,-15.25],[17.45,9.2,-8.35],'body')
    part([-1.6,1.45,-15.85],[17.6,1.8,-15.65],'trim')
    part([-1.15,5.3,-15.7],[2.6,8.4,-15.52],'tail')
    part([13.4,5.3,-15.7],[17.15,8.4,-15.52],'tail')
    part([4.75,5.2,-15.72],[11.25,6.3,-15.56],'plate')
    part([6.85,7.65,-15.67],[9.15,7.84,-15.52],'chrome')
    # Separate side door skins; beltline is above tires and below open windows.
    for x0,x1 in ((-1.8,-.65),(16.65,17.8)):
        part([x0,1.35,-2.25],[x1,8.6,5.0],'body')
        part([x0,1.35,5.1],[x1,8.6,17.4],'body')
    # Roof and open window frames, no solid window blocks. Pivots attach to the
    # front cowl and rear quarter, not floating inside the old cabin.
    part([-.55,15.2,-5.4],[16.55,16.15,12.9],'body')
    part([0,14.95,12.5],[16,15.65,13.25],'trim')
    part([0,14.95,-5.5],[16,15.55,-4.9],'trim')
    for x0,x1 in ((-.65,.35),(15.65,16.65)):
        part([x0,8.45,17.65],[x1,18.15,18.35],'body',
             {'axis':'x','angle':-45,'origin':[x0,9.0,18.0]})
        part([x0,8.35,-7.8],[x1,15.8,-7.05],'body',
             {'axis':'x','angle':22.5,'origin':[x0,9.0,-7.4]})
        part([x0,8.5,4.8],[x1,15.4,5.5],'trim')
        part([x0,8.55,-1.9],[x1,15.2,-1.4],'body')
    # Rear screen frame: opening stays open and pillars meet trunk/roof.
    part([.4,8.7,-8.35],[15.6,9.15,-7.8],'trim')
    part([.4,14.5,-5.55],[15.6,15.15,-5.0],'trim')
    # Blue word-free checkered livery and lower sill detail, attached to sides.
    for side,x in (('west',-1.815),('east',17.815)):
        uv=[16,0,0,16] if side=='west' else [0,0,16,16]
        E.append({'from':[x,3.2,-2.15],'to':[x,8.35,17.25],
                  'faces':{side:{'texture':'#livery','uv':uv}}})
        E.append({'from':[x,1.3,-2.15],'to':[x,1.7,17.25],
                  'faces':{side:{'texture':'#trim','uv':[0,0,16,16]}}})
        for z in (4.98,):part([x-.015,2.1,z],[x+.015,8.45,z+.11],'trim')
        for z in (0.4,9.0):
            part([x-.025,7.6,z],[x+.025,7.95,z+1.4],'trim')
            part([x-.03,7.9,z+.12],[x+.03,8.02,z+1.28],'chrome')
    # Mirrors, black bottoms and white caps.
    part([-3.5,9.05,15.3],[-1.8,10.1,16.75],'trim')
    part([-3.5,10.1,15.3],[-1.8,10.8,16.75],'body')
    part([17.8,9.05,15.3],[19.5,10.1,16.75],'trim')
    part([17.8,10.1,15.3],[19.5,10.8,16.75],'body')
    # Distinct, separate front seats: cushions, backs, side bolsters, headrests.
    for x0,x1 in ((2.0,6.6),(9.4,14.0)):
        part([x0,2.0,4.8],[x1,3.75,10.2],'seat')
        part([x0,3.4,3.9],[x1,9.45,5.15],'seat',
             {'axis':'x','angle':-22.5,'origin':[x0,3.4,4.4]})
        part([x0,3.55,5.0],[x0+.5,5.2,9.9],'seat')
        part([x1-.5,3.55,5.0],[x1,5.2,9.9],'seat')
        part([x0+.8,9.0,2.1],[x1-.8,11.1,3.25],'seat')
    # Two rear cushion areas and one rear backrest, maintaining four rider locations.
    part([1.8,1.9,-3.9],[7.3,3.7,1.5],'seat')
    part([8.7,1.9,-3.9],[14.2,3.7,1.5],'seat')
    part([1.8,3.4,-5.3],[14.2,8.6,-3.8],'seat')
    part([2.6,8.1,-5.35],[6.3,9.5,-4.25],'seat')
    part([9.7,8.1,-5.35],[13.4,9.5,-4.25],'seat')
    # Dashboard and central console. Driver is at x=12, passenger at x=4.
    part([.5,6.0,14.35],[15.5,8.45,17.25],'dash')
    part([9.25,8.45,14.5],[14.6,9.05,16.25],'trim')
    part([9.7,8.7,14.44],[14.1,8.95,14.53],'chrome')
    part([6.45,5.4,13.55],[9.55,8.3,16.0],'trim')
    part([6.95,7.05,13.48],[9.05,8.05,13.56],'chrome')
    part([7.2,6.1,13.43],[7.55,6.4,13.53],'amber')
    part([8.0,6.1,13.43],[8.35,6.4,13.53],'chrome')
    # Gear lever and handbrake on the tunnel; static visuals, not fake controls.
    part([7.05,1.0,7.5],[8.95,2.5,13.5],'trim')
    part([7.72,2.4,10.3],[8.28,4.1,10.9],'chrome')
    part([7.55,3.95,10.1],[8.45,4.55,11.1],'trim')
    part([7.0,2.4,7.0],[7.35,3.0,9.5],'trim')
    # Pedals in the driver's footwell, visible geometry only.
    for x0,x1 in ((10.1,10.75),(11.35,12.0),(12.6,13.2)):
        part([x0,1.0,13.4],[x1,2.2,14.05],'trim')
        part([x0,2.05,13.25],[x1,2.25,14.0],'chrome')
    # Horizon-inspired low-profile dual-colour lightbar. Phases match siren F.
    part([2.0,16.15,5.7],[3.0,16.65,8.7],'trim')
    part([13.0,16.15,5.7],[14.0,16.65,8.7],'trim')
    part([1.15,16.65,5.55],[14.85,17.2,8.85],'trim')
    part([7.4,17.2,5.65],[8.6,18.15,8.75],'chrome')
    part([1.35,17.2,5.65],[7.4,18.15,8.75],'blue' if phase==0 else 'blue_dim')
    part([8.6,17.2,5.65],[14.65,18.15,8.75],'red' if phase==1 else 'red_dim')
    part([1.35,18.15,5.65],[14.65,18.3,8.75],'trim')
    # Small raised roof antenna, avoiding imaginary glowing blocks.
    part([7.87,16.15,-1.8],[8.13,18.4,-1.54],'trim',
         {'axis':'x','angle':22.5,'origin':[8.0,16.15,-1.7]})
    return E

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected selected pack')
    files=readzip(data)
    if any(p not in files for p in PATHS):raise ValueError('missing Dacia body variants')
    # Three complete models avoid requiring extra entities and keep existing siren control.
    for path,phase in zip(PATHS,(-1,0,1)):
        old=json.loads(files[path]);m={'credit':old['credit'],'textures':TEX,'elements':body(phase)}
        for e in m['elements']:
            if any(not -16<=v<=32 for k in ('from','to') for v in e[k]):raise ValueError('illegal vanilla model coordinate')
            r=e.get('rotation')
            if r and (r['axis'] not in ('x','y','z') or r['angle'] not in (-45,-22.5,0,22.5,45) or any(not -16<=v<=32 for v in r['origin'])):raise ValueError('illegal vanilla rotation')
        files[path]=encode(m)
    additions={}
    for name in ('dash','amber'):
        n='assets/daciapolice/textures/item/custom_'+name+'.png'
        if n in files:raise ValueError('refusing collision '+n)
        additions[n]=(ROOT/'content/assets/gokart/textures/block'/('kart_'+name+'.png')).read_bytes()
    files.update(additions);out=io.BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name,value in sorted(files.items()):
            i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,value)
    return out.getvalue()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('base',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.base.resolve()==a.output.resolve():p.error('output cannot overwrite input')
    data=build(a.base.read_bytes());a.output.write_bytes(data);print('SHA-1',hashlib.sha1(data).hexdigest(),'SHA-256',hashlib.sha256(data).hexdigest())
if __name__=='__main__':main()
