#!/usr/bin/env python3
"""Export a Blockbench free model to a Minecraft 1.21.4 item-model parts pack.

Cuboid rotations are carried by external display transforms rather than being
rounded to Minecraft's five allowed element angles. This pack is NOT a rig;
consume the manifest to create and animate displays, and profile in-game.
"""
import argparse, base64, hashlib, io, json, math, zipfile
from collections import defaultdict
from pathlib import Path

FACES=('north','south','east','west','up','down')
SCALE=8.0  # model coordinates / 8; display scale 8 restores authored size

def compact(x):return json.dumps(x,separators=(',',':'),ensure_ascii=False).encode()
def export(source,variant):
    data=json.loads(source.read_text()); groups={x['uuid']:x for x in data['groups']};elements={x['uuid']:x for x in data['elements']}
    if len(groups)!=len(data['groups']) or len(elements)!=len(data['elements']):raise ValueError('Duplicate UUIDs')
    files={};textures={}
    for i,t in enumerate(data['textures']):
        src=t.get('source','');prefix='data:image/png;base64,'
        if not src.startswith(prefix):raise ValueError('Only embedded PNG textures supported: '+t.get('name','?'))
        img=base64.b64decode(src[len(prefix):],validate=True)
        if not img.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('Invalid PNG')
        key=f't{i}'; textures[key]=f'vehicle:item/combina/{variant}/{key}';files[f'assets/vehicle/textures/item/combina/{variant}/{key}.png']=img
    records=[];bones=[];index=0
    def visit(node,parent):
        nonlocal index
        g=groups[node['uuid']];name=g['name']; origin=g.get('origin',[0,0,0]);rotation=g.get('rotation',[0,0,0]);
        if any(not math.isfinite(float(v)) for v in origin+rotation):raise ValueError('non-finite group transform')
        bones.append({'name':name,'uuid':g['uuid'],'parent':parent,'origin':origin,'rotation_degrees_xyz':rotation})
        batches=defaultdict(list)
        for child in node.get('children',[]):
            if isinstance(child,dict):continue
            e=elements[child]
            if not e.get('export',True) or not e.get('visibility',True):continue
            if e.get('type','cube')!='cube':raise ValueError('Only cubes are supported')
            rot=e.get('rotation',[0,0,0]);pivot=e.get('origin',[(a+b)/2 for a,b in zip(e['from'],e['to'])]) if any(rot) else origin
            key=(tuple(pivot),tuple(rot));batches[key].append(e)
        for (pivot,rot),items in batches.items():
            model_elements=[]
            for e in items:
                low=[8+(e['from'][i]-pivot[i])/SCALE for i in range(3)];high=[8+(e['to'][i]-pivot[i])/SCALE for i in range(3)]
                if any(not math.isfinite(v) or v < -16 or v > 32 for v in low+high):raise ValueError('Coordinate outside vanilla model limits: '+e.get('name','?'))
                if any(a>=b for a,b in zip(low,high)):raise ValueError('Empty cuboid')
                faces={}
                for face in FACES:
                    f=e.get('faces',{}).get(face)
                    if not f or f.get('texture') is None:continue
                    ti=f['texture']
                    if not isinstance(ti,int) or ti<0 or ti>=len(textures):raise ValueError('Unsupported face texture')
                    entry={'texture':'#t'+str(ti),'uv':f.get('uv',[0,0,16,16])}
                    if f.get('rotation',0):entry['rotation']=f['rotation']
                    faces[face]=entry
                if faces:model_elements.append({'from':low,'to':high,'faces':faces})
            if not model_elements:continue
            item=f'combina_{variant}_{index:04d}';index+=1
            model={'textures':textures,'elements':model_elements,'display':{'fixed':{'rotation':[0,0,0],'translation':[0,0,0],'scale':[1,1,1]}}}
            # Source glass has alpha; a translucent item render type is needed.
            if any(any(face['texture']=='#t'+str(i) for face in e['faces'].values()) for e in model_elements for i,t in enumerate(data['textures']) if t['name'].startswith('sticla_')):model['render_type']='minecraft:translucent'
            files[f'assets/vehicle/models/item/{item}.json']=compact(model)
            files[f'assets/vehicle/items/{item}.json']=compact({'model':{'type':'minecraft:model','model':'vehicle:item/'+item}})
            records.append({'item_model':'vehicle:'+item,'bone':name,'bone_uuid':g['uuid'],'pivot':pivot,'rotation_degrees_xyz':rot,'display_scale':SCALE,'element_count':len(model_elements)})
        for child in node.get('children',[]):
            if isinstance(child,dict):visit(child,g['uuid'])
    for n in data['outliner']:
        if not isinstance(n,dict):raise ValueError('Root-level loose element unsupported')
        visit(n,None)
    files['pack.mcmeta']=compact({'pack':{'pack_format':46,'description':'Horizon combina: modele experimentale, necesita rig Paper'}})
    manifest={'format':1,'source':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'variant':variant,'unit':'1/16 block','axes':'front -Z, up +Y','model_scale_divisor':SCALE,'notes':'Experimental assets only; needs ItemDisplay rig and in-game verification. Apply bone hierarchy then part pivot/rotation with Blockbench XYZ Euler order ZYX; use FIXED item display and uniform display_scale.', 'bones':bones,'parts':records}
    return files,manifest

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('source',type=Path);ap.add_argument('--variant',choices=('cereale','porumb'),required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--manifest',type=Path,required=True);a=ap.parse_args()
    if a.source.resolve() in (a.output.resolve(),a.manifest.resolve()) or a.output.resolve()==a.manifest.resolve():ap.error('Input and outputs must be different')
    files,manifest=export(a.source,a.variant);a.output.parent.mkdir(parents=True,exist_ok=True);a.manifest.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.output,'w',zipfile.ZIP_DEFLATED) as z:
        for name,content in sorted(files.items()):
            zi=zipfile.ZipInfo(name,(1980,1,1,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,content)
    a.manifest.write_bytes(compact(manifest)+b'\n')
    print(f"{a.variant}: {len(manifest['parts'])} display parts, {sum(p['element_count'] for p in manifest['parts'])} cubes; {a.output}")
if __name__=='__main__':main()
