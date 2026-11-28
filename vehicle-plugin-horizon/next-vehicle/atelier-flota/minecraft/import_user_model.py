#!/usr/bin/env python3
"""Apply the user's complete Blockbench edits to separate Minecraft assets."""
import base64, copy, json, math, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
source=ROOT/'downloads/horizon-recovery-complet.bbmodel'
out=Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'assets'
p=json.loads(source.read_text()); groups={g['uuid']:g for g in p['groups']}; cubes={e['uuid']:e for e in p['elements']}
names={groups[o['uuid']]['name']:o for o in p['outliner']}
texnames={};texture_dir=out/'textures/item';texture_dir.mkdir(parents=True,exist_ok=True)
for n,tex in enumerate(p['textures']):
    data=tex['source']; prefix='data:image/png;base64,'
    if not data.startswith(prefix):raise ValueError('Texture is not embedded PNG: '+tex['name'])
    name=f'horizon_recovery_edit_{n:02d}'; (texture_dir/(name+'.png')).write_bytes(base64.b64decode(data[len(prefix):],validate=True))
    texnames[n]=name
texture_map={f't{i}':f'vehicle:item/{name}' for i,name in texnames.items()}

for title,modelname in [('Cabina si interior','cab'),('Platforma si cutie','flatbed'),('Volan','steering')]:
    group=names[title]; groupdata=groups[group['uuid']]
    if any(groupdata.get('rotation',[0,0,0])):raise ValueError('Rotated parent group requires conversion: '+title)
    elements=[];approximated=[]
    for k in group['children']:
        e=copy.deepcopy(cubes[k]); a=e['from'];b=e['to']; rot=e.get('rotation',[0,0,0]);origin=e.get('origin',[8,8,8])
        if e['name']=='horizon_service_cab_172':
            # A fixed shaft tilted with the wheel, pivoting at its hub.
            a[1]=13.77; b[1]=14.07; origin=[5.52,13.92,2.504];rot=[-22.5,0,0]
        if any(v < -16 or v > 32 for v in [*a,*b]):raise ValueError('Cube exceeds Minecraft model bounds: '+e['name'])
        if any(a[i]>=b[i] for i in range(3)):raise ValueError('Invalid cube: '+e['name'])
        faces={}
        for side,f in e['faces'].items():
            if f.get('texture') is None:continue
            face={'uv':f.get('uv',[0,0,16,16]),'texture':'#t'+str(f['texture'])}
            if f.get('rotation',0):face['rotation']=f['rotation']
            if f.get('tint') is not None and f['tint']!=-1:face['tintindex']=f['tint']
            faces[side]=face
        piece={'name':e['name'],'from':a,'to':b,'faces':faces}
        # Vanilla model-element rotations cannot express 11 degrees. Export
        # each such bar around its own pivot as a separate item display; the
        # rig applies the exact angle with a display transformation instead.
        if title=='Cabina si interior' and abs(rot[0])==11 and not rot[1] and not rot[2]:
            idx={'horizon_service_cab_49':0,'horizon_service_cab_51':1,
                 'horizon_service_cab_52':2,'horizon_service_cab_50':3}[e['name']]
            item=f'horizon_recovery_arch_{idx}'
            piece['from']=[round(a[i]-origin[i]+8,6) for i in range(3)]
            piece['to']=[round(b[i]-origin[i]+8,6) for i in range(3)]
            (out/'models/item'/f'{item}.json').write_text(json.dumps({'textures':texture_map,'elements':[piece]},indent=2)+'\n')
            (out/'items'/f'{item}.json').write_text(json.dumps({'model':{'type':'minecraft:model','model':'vehicle:item/'+item}},indent=2)+'\n')
            print('Separate exact-angle bar:',e['name'],rot[0],origin)
            continue
        axes=[i for i,v in enumerate(rot) if abs(v)>1e-6]
        if len(axes)>1:raise ValueError('Minecraft cannot export multi-axis rotation: '+e['name'])
        if axes:
            axis=axes[0];angle=rot[axis]; snapped=min([-45,-22.5,0,22.5,45],key=lambda x:abs(angle-x))
            if abs(angle-snapped)>1e-6:approximated.append([e['name'],angle,snapped])
            if snapped:piece['rotation']={'origin':origin,'axis':'xyz'[axis],'angle':snapped}
        elements.append(piece)
    (out/'models/item'/f'horizon_service_{modelname}.json').write_text(json.dumps({'textures':texture_map,'elements':elements},indent=2)+'\n')
    print(title, len(elements),'angle approximations',approximated)
# Reconstruct the two folded ramps in their hinge-local coordinates. They
# share one animated game model, so reject asymmetric edits instead of losing one.
def unfold_ramp(title):
    group=names[title];pivot=groups[group['uuid']]['origin'];pieces=[]
    for k in group['children']:
        e=cubes[k];a=e['from'];b=e['to']
        lo=[8+a[0]-pivot[0],8+a[2]-pivot[2],8-(b[1]-pivot[1])]
        hi=[8+b[0]-pivot[0],8+b[2]-pivot[2],8-(a[1]-pivot[1])]
        faces={}
        inverse={'north':'up','south':'down','up':'south','down':'north','east':'east','west':'west'}
        for side,f in e['faces'].items():
            if f.get('texture') is None:continue
            face={'uv':f.get('uv',[0,0,16,16]),'texture':'#t'+str(f['texture'])}
            if f.get('rotation',0):face['rotation']=f['rotation']
            faces[inverse[side]]=face
        if any(e.get('rotation',[0,0,0])):raise ValueError('Edited ramp cube rotation requires conversion')
        pieces.append({'name':e['name'],'from':[round(v,5) for v in lo], 'to':[round(v,5) for v in hi], 'faces':faces})
    return pieces
ramp=unfold_ramp('Rampa stanga')
if ramp!=unfold_ramp('Rampa dreapta'):raise ValueError('Ramp edits differ; cannot use a shared ramp model')
(out/'models/item/horizon_service_ramp.json').write_text(json.dumps({'textures':texture_map,'elements':ramp},indent=2)+'\n')

# Front wheel group origins are the wheel pivots, in the same four-units-per-block space.
for side in ['stanga','dreapta']:
    group=groups[names['Roata fata '+side]['uuid']];print('front wheel',side,[(v-8)/4 for v in group['origin']])
