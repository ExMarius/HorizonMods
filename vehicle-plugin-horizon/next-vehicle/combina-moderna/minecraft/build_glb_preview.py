#!/usr/bin/env python3
"""Make preview-only Blockbench-like JSON from the experimental item pack."""
import argparse,json,struct,zlib,zipfile
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('pack',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(a.pack) as z:
 for variant in ('cereale','porumb'):
  m=json.loads(z.read(f'assets/vehicle/models/item/combina_glb_{variant}.json'));textures=[];keys={}
  for key,path in m['textures'].items():
   raw=z.read('assets/'+path.replace(':','/textures/')+'.png');i=8;idat=b''
   while i<len(raw):
    length=struct.unpack('>I',raw[i:i+4])[0];tag=raw[i+4:i+8];data=raw[i+8:i+8+length];i+=length+12
    if tag==b'IDAT':idat+=data
    if tag==b'IEND':break
   pixel=zlib.decompress(idat);color=pixel[1:4].hex();keys[key]=len(textures);textures.append({'name':'culoare_'+color+'.png'})
  elements=[];children=[]
  for i,e in enumerate(m['elements']):
   n=str(i);face=next(iter(e['faces'].values()));t=keys[face['texture'][1:]]
   elements.append({'uuid':n,'from':[(v-8)*8 for v in e['from']],'to':[(v-8)*8 for v in e['to']],'faces':{'north':{'texture':t}}});children.append(n)
  group_names=['body','header_assembly','unloading_auger','wheel_rl','wheel_rr','wheel_fl','wheel_fr','reel','intake_auger']
  groups=[{'uuid':n,'name':n,'origin':[0,0,0]} for n in group_names]
  outliner=[{'uuid':n,'children':children if n=='body' else []} for n in group_names]
  (a.output/f'glb-{variant}-preview.json').write_text(json.dumps({'textures':textures,'elements':elements,'groups':groups,'outliner':outliner},separators=(',',':')))
  print(variant,len(elements),'cuburi')
