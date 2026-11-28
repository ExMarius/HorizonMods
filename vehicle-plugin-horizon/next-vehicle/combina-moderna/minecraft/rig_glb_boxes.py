#!/usr/bin/env python3
"""Separate a GLB-derived voxel item model into provisional Blockbench bones.

Classification is spatial and intentionally approximate. This is editable,
not yet a Minecraft runtime rig; pivots require visual in-game calibration.
"""
import argparse,base64,json,struct,uuid,zipfile,zlib
from pathlib import Path

def uid():return str(uuid.uuid4())
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('pack',type=Path);ap.add_argument('manifest',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args();manifest=json.loads(a.manifest.read_text());scale=manifest['source_unit_to_model_units'];ground=manifest['source_ground_y']
 with zipfile.ZipFile(a.pack) as z:
  for variant in ('cereale','porumb'):
   record=next(v for v in manifest['variants'] if v['variant']==variant);center_x=record['source_center_x'];center_z=record['source_center_z'];model=json.loads(z.read(f'assets/vehicle/models/item/combina_glb_{variant}.json'))
   def world(x,y,z):return [-(x-center_x)*scale,(y-ground)*scale,-(z-center_z)*scale]
   definitions=[('body',world(center_x,ground,center_z),None),('header_assembly',world(center_x,40,320),'body'),('wheel_fl',world(center_x+120,62,243),'body'),('wheel_fr',world(center_x-120,62,243),'body'),('wheel_rl',world(center_x+90,43,0),'body'),('wheel_rr',world(center_x-90,43,0),'body'),('reel',world(center_x,60,365),'header_assembly'),('intake_auger',world(center_x,45,350),'header_assembly'),('unloading_auger',world(center_x+80,200,0),'body')]
   ids={n:uid() for n,_,_ in definitions};groups=[];nodes={};roots=[];textures=[];keys={}
   for key,path in model['textures'].items():
    raw=z.read('assets/'+path.replace(':','/textures/')+'.png');data=b'';i=8
    while i<len(raw):
     n=struct.unpack('>I',raw[i:i+4])[0];tag=raw[i+4:i+8];part=raw[i+8:i+8+n];i+=n+12
     if tag==b'IDAT':data+=part
     if tag==b'IEND':break
    color=zlib.decompress(data)[1:4].hex();keys[key]=len(textures);textures.append({'name':'glb_'+color+'.png','id':str(len(textures)),'uuid':uid(),'width':1,'height':1,'uv_width':16,'uv_height':16,'particle':False,'render_mode':'default','mode':'bitmap','saved':False,'source':'data:image/png;base64,'+base64.b64encode(raw).decode()})
   for name,origin,parent in definitions:
    groups.append({'name':name,'uuid':ids[name],'origin':origin,'rotation':[0,0,0],'export':True,'visibility':True});node={'uuid':ids[name],'children':[]};nodes[name]=node;(nodes[parent]['children'] if parent else roots).append(node)
   elements=[];counts={n:0 for n,_,_ in definitions}
   for e in model['elements']:
    lo=[(v-8)*8 for v in e['from']];hi=[(v-8)*8 for v in e['to']];c=[(lo[i]+hi[i])/2 for i in range(3)]
    sx=center_x-c[0]/scale;sy=ground+c[1]/scale;sz=center_z-c[2]/scale;dx=sx-center_x
    # Geometry assignment is a provisional crop, not a component-aware rig.
    if sz>320 and sy<130:bone='header_assembly'
    elif abs(dx)>65 and 170<sz<310 and sy<125:bone='wheel_fl' if dx>0 else 'wheel_fr'
    elif abs(dx)>65 and -55<sz<55 and sy<95:bone='wheel_rl' if dx>0 else 'wheel_rr'
    else:bone='body'
    face=next(iter(e['faces'].values()));texture=keys[face['texture'][1:]];eid=uid()
    elements.append({'name':'GLB '+bone,'type':'cube','uuid':eid,'from':lo,'to':hi,'origin':[(lo[i]+hi[i])/2 for i in range(3)],'faces':{f:{'uv':[0,0,16,16],'texture':texture} for f in ('north','south','east','west','up','down')},'box_uv':False,'export':True,'visibility':True});nodes[bone]['children'].append(eid);counts[bone]+=1
   model={'meta':{'format_version':'5.0','model_format':'free','box_uv':False},'name':'Horizon GLB '+variant+' - piese provizorii','resolution':{'width':16,'height':16},'elements':elements,'textures':textures,'groups':groups,'outliner':roots}
   a.output.mkdir(parents=True,exist_ok=True);out=a.output/f'glb-{variant}-piese.bbmodel';out.write_text(json.dumps(model,separators=(',',':'))+'\n');print(variant,counts)
if __name__=='__main__':main()
