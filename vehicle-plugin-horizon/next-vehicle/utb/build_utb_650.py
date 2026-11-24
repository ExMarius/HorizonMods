#!/usr/bin/env python3
"""Build a separate red U-650-inspired tractor without altering existing pack assets.

Body starts from the existing Paper tractor's authored model so its established
seat, wheel and hitch layout stays compatible. Cab and visual details are new.
"""
import argparse, copy, hashlib, io, json, zipfile
from pathlib import Path
BASE_SHA1='ec159abcd4250da7c991015e35a65b3440ed3e41'
BODY='assets/vehicle/models/item/utb_650_body.json'
ITEM='assets/vehicle/items/utb_650_body.json'
BASE='assets/vehicle/models/item/tractor_body.json'
LEGAL={-45,-22.5,0,22.5,45}

def box(lo,hi,texture):
    return {'from':lo,'to':hi,'faces':{face:{'texture':'#'+texture,'uv':[0,0,16,16]}
            for face in ('north','south','east','west','up','down')}}

def model(old):
    result=copy.deepcopy(old)
    if len(result.get('elements',[]))!=56 or 'color' not in result.get('textures',{}):raise ValueError('unexpected installed tractor model')
    # Original badge is deliberately replaced; keep the other source parts.
    result['elements']=result['elements'][:54]
    result['textures'].update({'color':'minecraft:block/red_concrete','utb_red':'minecraft:block/red_concrete',
        'utb_dark':'minecraft:block/black_concrete','utb_metal':'minecraft:block/gray_concrete',
        'utb_lamp':'minecraft:block/sea_lantern','utb_glass':'minecraft:block/light_blue_stained_glass',
        'utb_amber':'minecraft:block/orange_concrete','utb_rim':'minecraft:block/light_gray_concrete'})
    e=result['elements']; add=lambda a,b,t:e.append(box(a,b,t))
    # Flat roof, red posts and cabin frame, located over the existing tractor seat.
    add([.55,31.,-11.9],[15.45,32.,2.2],'utb_red')
    add([1.3,30.75,-11.2],[14.7,31.,1.5],'utb_dark')
    for x0,x1 in ((.65,1.35),(14.65,15.35)):
        for z0,z1 in ((-11.5,-10.8),(1.0,1.7)):
            add([x0,13.6,z0],[x1,31.,z1],'utb_red')
        # Door waistline and a separate center pillar frame.
        add([x0,18.0,-10.8],[x1,18.55,1.0],'utb_red')
        add([x0,18.55,-4.8],[x1,30.75,-4.25],'utb_red')
        add([x0,29.9,-10.8],[x1,30.75,1.0],'utb_red')
        # Two glazed side openings; no opaque cab-wall geometry across the driver.
        add([x0+.12,18.65,-10.7],[x1-.12,29.8,-4.9],'utb_glass')
        add([x0+.12,18.65,-4.15],[x1-.12,29.8,.9],'utb_glass')
    # Front and rear windscreens framed in black, cab interior remains visible.
    for z0,z1 in ((-11.4,-10.85),(1.05,1.6)):
        add([1.35,18.0,z0],[14.65,18.55,z1],'utb_red')
        add([1.35,29.9,z0],[14.65,30.65,z1],'utb_dark')
        add([1.45,18.65,z0+.08],[14.55,29.8,z1-.08],'utb_glass')
    # Radiator mask and transverse bars on the front, over the old generic grille.
    add([3.4,8.0,28.05],[12.6,17.5,28.3],'utb_dark')
    for y in (9.0,10.8,12.6,14.4,16.2):add([3.7,y,28.31],[12.3,y+.22,28.38],'utb_metal')
    add([6.5,17.6,28.05],[9.5,18.4,28.32],'utb_rim')
    # Two round-looking lamps made from an inset lens and dark housing.
    for x0 in (1.6,12.0):
        add([x0,11.0,27.65],[x0+2.4,13.5,28.05],'utb_dark')
        add([x0+.3,11.3,28.06],[x0+2.1,13.2,28.15],'utb_lamp')
    # Tall capped exhaust and front weight; original lower muffler remains connected.
    add([5.15,26.8,21.05],[6.85,31.2,22.95],'utb_dark')
    add([4.95,31.2,20.9],[7.05,31.7,23.1],'utb_dark')
    add([3.0,2.6,27.65],[13.0,4.3,28.8],'utb_metal')
    # Red marker lamps and orange cab beacon (decorative, not animated).
    add([1.35,31.8,-10.6],[3.0,32.,-9.0],'utb_amber')
    # Door handles and simple two-part attached side mirrors.
    for x0,x1,arm0,arm1 in ((-.6,.6,.6,1.4),(15.4,16.6,14.6,15.4)):
        add([arm0,24.0,-.2],[arm1,24.35,.2],'utb_dark')
        add([x0,23.25,-.55],[x1,25.05,.55],'utb_dark')
        add([x0,17.2,-4.1],[x1,17.55,-2.8],'utb_metal')
    for e in result['elements']:
        for k in ('from','to'):
            if any(not -16<=n<=32 for n in e[k]):raise ValueError('out-of-range element')
        r=e.get('rotation')
        if r and (r.get('angle') not in LEGAL or r.get('axis') not in ('x','y','z') or any(not -16<=n<=32 for n in r['origin'])):raise ValueError('invalid element rotation')
    return result

def build(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected deployed pack')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names=z.namelist()
        if z.testzip() or len(names)!=len(set(names)):raise ValueError('invalid zip')
        files={n:z.read(n) for n in names}
    if BODY in files or ITEM in files:raise ValueError('model already exists; refusing overwrite')
    if json.loads(files['pack.mcmeta'])['pack']['pack_format']!=46:raise ValueError('not a 1.21.4 pack')
    files[BODY]=json.dumps(model(json.loads(files[BASE])),separators=(',',':')).encode()
    files[ITEM]=json.dumps({'model':{'type':'minecraft:model','model':'vehicle:item/utb_650_body','tints':[{'type':'minecraft:dye','default':-1}]}},separators=(',',':')).encode()
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(files.items()):
            info=zipfile.ZipInfo(n,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
    return out.getvalue()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('base',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.base.resolve()==a.output.resolve():p.error('output must differ')
    result=build(a.base.read_bytes());a.output.write_bytes(result);print('SHA-1',hashlib.sha1(result).hexdigest())
if __name__=='__main__':main()
