#!/usr/bin/env python3
"""Assemble the installed resource-pack cubes into one editable Blockbench project.

This is an editing view, not a replacement for the separate game item models.
One block is four Blockbench units, matching the authored resource-pack scale.
"""
import base64, json, uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ASSETS = HERE / 'assets'

def uid(): return str(uuid.uuid4())
def read_model(name): return json.loads((ASSETS/'models/item'/('horizon_service_'+name+'.json')).read_text())
textures=[]; texture_ids={}; elements=[]; groups=[]

def texture_id(resource):
    if resource not in texture_ids:
        ns,name=resource.split(':',1); name=name.split('/')[-1]
        path = ASSETS/'textures/item'/(name+'.png') if ns=='vehicle' else ROOT/'content/assets/gokart/textures/block'/(name+'.png')
        raw=path.read_bytes(); ident=uid(); idx=len(textures)
        textures.append({'id':str(idx),'uuid':ident,'name':name+'.png','relative_path':'','folder':'', 'namespace':ns,
                         'particle':False,'render_mode':'default','render_sides':'auto','frame_time':1,'frame_order_type':'loop',
                         'frame_order':'','frame_interpolate':False,'visible':True,'mode':'bitmap','saved':False,
                         'source':'data:image/png;base64,'+base64.b64encode(raw).decode('ascii')})
        texture_ids[resource]=idx
    return texture_ids[resource]

def add_group(label, model_name, offset=(0,0,0), scale=1.0, folded_ramp=False):
    model=read_model(model_name); children=[]
    def transform(p):
        x,y,z=[(v-8)*scale for v in p]
        if folded_ramp: y,z=-z,y
        return [round(8+x+offset[0]*4,5),round(8+y+offset[1]*4,5),round(8+z+offset[2]*4,5)]
    for number,e in enumerate(model['elements']):
        a,b=transform(e['from']),transform(e['to'])
        faces={}
        # For ramps the 90 degree fold rotates the face directions too.
        remap={'north':'down','south':'up','up':'north','down':'south','east':'east','west':'west'} if folded_ramp else {}
        for face,info in e['faces'].items():
            tex=info.get('texture','').lstrip('#'); resource=model['textures'][tex]
            faces[remap.get(face,face)]={'uv':info.get('uv',[0,0,16,16]),'texture':texture_id(resource)}
        rotation=e.get('rotation'); angles=[0,0,0]
        origin=transform(rotation['origin']) if rotation else transform([8,8,8])
        if rotation: angles['xyz'.index(rotation['axis'])]=rotation['angle']
        cube={'name':e.get('name',label+' '+str(number+1)),'box_uv':False,'rescale':False,
              'locked':False,'allow_mirror_modeling':True,'from':[min(a[i],b[i]) for i in range(3)],
              'to':[max(a[i],b[i]) for i in range(3)],'autouv':0,'color':0,'origin':origin,
              'rotation':angles,'faces':faces,'type':'cube','uuid':uid()}
        elements.append(cube);children.append(cube['uuid'])
    groups.append({'name':label,'origin':[round(8+v*4,5) for v in offset],'color':0,'children':children,'uuid':uid(),'export':True,'isOpen':False})

add_group('Cabina si interior','cab')
add_group('Platforma si cutie','flatbed')
add_group('Volan','steering')
for side,x in [('stanga',-1.35),('dreapta',1.35)]: add_group('Roata fata '+side,'wheel',(x,.53,-1.488),1.18)
for side,x in [('stanga',-1.20),('dreapta',1.20)]: add_group('Roata spate '+side,'wheel',(x,.35,3.22),.35/.45)
for side,x in [('stanga',-1.05),('dreapta',1.05)]: add_group('Rampa '+side,'ramp',(x,.86,5.35),1,True)
project={'meta':{'format_version':'4.10','model_format':'free','box_uv':False},'name':'Horizon Recovery - editare completa',
         'model_identifier':'horizon_recovery_editabil','visible_box':[12,12,0], 'variable_placeholders':'',
         'resolution':{'width':16,'height':16},'elements':elements,'outliner':groups,'textures':textures}
out=ROOT/'downloads'/'horizon-recovery-complet.bbmodel';out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(project,ensure_ascii=False,separators=(',',':'))+'\n')
print(out, len(elements),len(textures))
