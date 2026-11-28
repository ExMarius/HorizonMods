#!/usr/bin/env python3
"""Remodel Dacia's front, rear, bonnet and door details on the user's source mesh."""
import argparse, copy, hashlib, io, json, zipfile
from pathlib import Path
from prepare_police import readzip
from rebuild_police import REAR_WINDOW_FILL,OLD_LIGHTBAR,OLD_POLICE_TEXT,cube,encode
BASE_SHA1='c4b0ccc2ec583a50e2a5f99d3e9a9d6601d66f4f'
BODY='assets/daciapolice/models/item/body.json'
BASE=Path(__file__).resolve().parent
ORIGINAL_COUNT=268
BASE_REMOVED=REAR_WINDOW_FILL|OLD_LIGHTBAR|OLD_POLICE_TEXT
# Remove old front fascia/lamp detailing and rear bumper/lamp detailing, replace below.
REPLACED=set(range(0,10))|{10,13,53,97,98,105,106,107,108}|set(range(56,63))|set(range(76,84))|set(range(129,207))|set(range(207,212))|set(range(212,224))
ORIGINAL_RETAINED=[i for i in range(ORIGINAL_COUNT) if i not in BASE_REMOVED]
def redesign(data,expected=BASE_SHA1):
    if hashlib.sha1(data).hexdigest()!=expected:raise ValueError('unexpected base pack')
    files=readzip(data);models=[]
    paths=[BODY,'assets/daciapolice/models/item/body_flash_0.json','assets/daciapolice/models/item/body_flash_1.json']
    for path in paths:
        m=json.loads(files[path]); original=m['elements']
        if len(original)<len(ORIGINAL_RETAINED) or any(i>=len(original) for i in range(len(ORIGINAL_RETAINED))):raise ValueError('unexpected base model')
        # Audit original identification against canonical source, except explicitly recoloured seats.
        import zipfile as zf
        with zf.ZipFile(BASE.parents[1]/'paper-vehicles/transfer/vehicle-reference/vehicle-fara-mentiune.zip') as source:
            source_elements=json.loads(source.read('vehicle/models/vehicle/dacia_logan_police_body.json'))['elements']
        for pos,idx in enumerate(ORIGINAL_RETAINED):
            if idx not in range(109,117) and original[pos]!=source_elements[idx]:raise ValueError('source geometry mismatch at '+str(idx))
        m['elements']=[e for pos,e in enumerate(original) if pos>=len(ORIGINAL_RETAINED) or ORIGINAL_RETAINED[pos] not in REPLACED]
        m['textures'].update({'new_body':'daciapolice:item/logan_body_white',
            'new_grille':'daciapolice:item/logan_grille','new_head':'daciapolice:item/logan_headlamp',
            'new_tail':'daciapolice:item/logan_tail','new_chrome':'daciapolice:item/logan_chrome',
            'new_plate':'daciapolice:item/logan_plate'})
        # Refined body-coloured front fascia: separate bumper, upper lip, recessed
        # intake, headlight clusters and fog housings; bounded by the old body.
        # Individual door skins replace the single long slabs, keeping the same
        # cabin attachment and opening bounds while giving each door its own seam.
        parts=[
            cube([-1,1,-2.4],[0,9,5.0],'new_body'),
            cube([-1,1,5.06],[0,9,17.6],'new_body'),
            cube([16,1,-2.4],[17,9,5.0],'new_body'),
            cube([16,1,5.06],[17,9,17.6],'new_body'),
            cube([-1.5,2.0,29.25],[17.5,5.55,31.7],'new_body'),
            cube([-1.5,5.55,29.25],[17.5,7.75,31.15],'new_body'),
            cube([3.35,4.95,31.16],[12.65,7.5,31.76],'new_grille'),
            cube([3.35,7.5,31.14],[12.65,7.68,31.76],'new_chrome'),
            cube([3.35,4.78,31.68],[12.65,4.95,31.8],'new_chrome'),
            cube([7.1,5.35,31.77],[8.9,7.25,31.86],'new_chrome'),
            cube([7.4,5.65,31.86],[8.6,6.95,31.9],'new_grille'),
            cube([2.9,2.45,31.71],[13.1,3.95,31.84],'new_grille'),
            cube([2.9,2.3,31.75],[13.1,2.45,31.87],'new_chrome'),
            cube([-1.25,6.05,31.1],[3.3,8.15,31.72],'new_head'),
            cube([12.7,6.05,31.1],[17.25,8.15,31.72],'new_head'),
            cube([-1.2,2.35,31.71],[2.4,4.05,31.84],'trim'),
            cube([13.6,2.35,31.71],[17.2,4.05,31.84],'trim'),
            cube([-.65,2.75,31.84],[1.75,3.55,31.91],'new_head'),
            cube([14.25,2.75,31.84],[16.65,3.55,31.91],'new_head'),
            cube([4.8,3.85,31.84],[11.2,4.7,31.94],'new_plate'),
            # Bonnet creases and subtle black wipers, aligned to source hood/window.
            cube([2.25,8.98,20.1],[2.43,9.06,25.45],'new_chrome'),
            cube([13.57,8.98,20.1],[13.75,9.06,25.45],'new_chrome'),
            cube([2.0,9.3,18.55],[7.4,9.46,18.75],'trim'),
            cube([8.6,9.3,18.55],[14.0,9.46,18.75],'trim'),
            # Contemporary two-tone mirror housings with slim silver glass.
            cube([-1.8,9.75,15.5],[-.9,10.35,17.2],'trim'),
            cube([-3.7,9.55,15.3],[-1.8,11.0,17.2],'new_body'),
            cube([-3.72,9.75,15.3],[-3.7,10.8,17.1],'new_chrome'),
            cube([16.9,9.75,15.5],[17.8,10.35,17.2],'trim'),
            cube([17.8,9.55,15.3],[19.7,11.0,17.2],'new_body'),
            cube([19.7,9.75,15.3],[19.72,10.8,17.1],'new_chrome'),
            # Rear fascia and wide segmented rear lamp housings.
            cube([-1.45,2.1,-15.8],[17.45,5.6,-13.9],'new_body'),
            cube([3.1,2.05,-15.91],[12.9,2.35,-15.8],'trim'),
            cube([-1.05,5.5,-15.82],[2.35,8.55,-15.6],'new_tail'),
            cube([13.65,5.5,-15.82],[17.05,8.55,-15.6],'new_tail'),
            cube([4.6,5.0,-15.85],[11.4,6.1,-15.63],'new_plate'),
            cube([6.8,7.5,-15.82],[9.2,7.72,-15.62],'new_chrome'),
        ]
        # Broader bonnet based on the two original curved panels; this preserves
        # their UVs, pivots and tint while actually changing the panel silhouette.
        for index,lo,hi in ((97,[.65,7.72,19.51304],[15.4,9.0,25.68343]),
                            (98,[1.55,7.70,25.68343],[14.45,8.92,30.95])):
            hood=copy.deepcopy(source_elements[index]);hood['from']=lo;hood['to']=hi
            parts.append(hood)
        # Body side seams and handles sit outside the livery planes, not over windows.
        for side,x0,x1 in [('west',-1.055,-1.035),('east',17.035,17.055)]:
            for z in (5.0,): parts.append(cube([x0,3.0,z],[x1,8.7,z+.13],'trim'))
            for z in (-.1,8.5):
                parts.append(cube([x0,7.8,z],[x1,8.15,z+1.35],'trim'))
                parts.append(cube([x0,8.02,z+.12],[x1,8.16,z+1.2],'new_chrome'))
        m['elements']+=parts
        # Inherited colour-bearing body parts remain dyeable, accessories stay fixed.
        for e in parts:
            if all(face['texture']=='#new_body' for face in e['faces'].values()):
                for face in e['faces'].values():face['tintindex']=0
        for e in m['elements']:
            if any(not -16<=v<=32 for field in ('from','to') for v in e[field]):raise ValueError('model bounds')
        models.append(m)
    for name,model in zip(paths,models):files[name]=encode(model)
    new={}
    for name in ('logan_grille','logan_headlamp','logan_tail'):
        new['assets/daciapolice/textures/item/'+name+'.png']=(BASE/'assets/redesign'/f'{name}.png').read_bytes()
    root=BASE.parents[1]/'content/assets/gokart/textures/block'
    new['assets/daciapolice/textures/item/logan_body_white.png']=(root/'kart_body.png').read_bytes()
    new['assets/daciapolice/textures/item/logan_chrome.png']=(root/'kart_chrome.png').read_bytes()
    new['assets/daciapolice/textures/item/logan_plate.png']=(root/'plate_ro.png').read_bytes()
    if set(new)&set(files):raise ValueError('texture collision')
    files.update(new)
    # This one existing Dacia-only texture intentionally gets a word-free redesign.
    files['assets/daciapolice/textures/item/logan_livery.png']=(BASE/'assets/redesign/logan_livery.png').read_bytes()
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
    return out.getvalue()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('base',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.base.resolve()==a.output.resolve():p.error('output must differ from input')
    data=redesign(a.base.read_bytes());a.output.write_bytes(data);print('SHA-1',hashlib.sha1(data).hexdigest(),'SHA-256',hashlib.sha256(data).hexdigest())
if __name__=='__main__':main()
