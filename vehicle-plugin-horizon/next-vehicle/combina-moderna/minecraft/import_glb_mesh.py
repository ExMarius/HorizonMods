#!/usr/bin/env python3
"""Separate the supplied three-vehicle GLB into editable Blockbench mesh JSON.

Requires numpy and trimesh. Free-format Blockbench mesh files are NOT vanilla
Minecraft item models. Source coordinates are uniformly scaled and shifted;
all triangle positions, material base colors and triangle topology are kept.
"""
import argparse, base64, json, hashlib, struct, uuid, zlib
from pathlib import Path
import numpy as np
import trimesh

def png(rgba):
 def chunk(tag,data): return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b'\0'+bytes(rgba)))+chunk(b'IEND',b'')
def uid():return str(uuid.uuid4())
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('glb',type=Path);ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--height',type=float,default=3.65,help='Combined source height in Minecraft blocks; assumed, not measured')
 a=ap.parse_args();scene=trimesh.load(a.glb,force='scene'); ground=float(scene.bounds[0,1]);span=float(scene.bounds[1,1]-ground)
 if not np.isfinite(span) or span<=0 or not np.isfinite(a.height) or a.height<=0:raise ValueError('invalid height')
 scale=16*a.height/span
 # The supplied layout contains vehicles with centres near these X coordinates.
 centres=[-585.0,29.0,561.0];names=['porumb','cereale','fara-heder'];buckets=[[],[],[]]
 for node in scene.graph.nodes_geometry:
  matrix,key=scene.graph[node];mesh=scene.geometry[key];points=trimesh.transform_points(mesh.vertices,matrix)
  if not len(points):continue
  centre=(points.min(axis=0)+points.max(axis=0))/2; idx=int(np.argmin(np.abs(np.array(centres)-centre[0])));buckets[idx].append((node,mesh,points))
 a.output_dir.mkdir(parents=True,exist_ok=True)
 for idx,entries in enumerate(buckets):
  if not entries:raise ValueError('source is not the expected three-vehicle layout')
  allpoints=np.concatenate([p for _,_,p in entries]);zbounds=[allpoints[:,2].min(),allpoints[:,2].max()];zcentre=float(sum(zbounds)/2)
  textures=[];color_indices={};elements=[];children=[]
  for name,mesh,points in entries:
   material=getattr(mesh.visual,'material',None);color=getattr(material,'baseColorFactor',None)
   color=tuple(int(v) for v in (color if color is not None else [180,180,180,255]));
   if len(color)!=4:raise ValueError('unsupported material color')
   if getattr(material,'baseColorTexture',None) is not None:raise ValueError('textured GLB not supported; refusing to discard textures')
   if color not in color_indices:
    i=len(textures);color_indices[color]=i;h=''.join(f'{v:02x}' for v in color);textures.append({'name':h+'.png','id':str(i),'uuid':uid(),'width':1,'height':1,'uv_width':16,'uv_height':16,'particle':False,'render_mode':'default','mode':'bitmap','saved':False,'source':'data:image/png;base64,'+base64.b64encode(png(color)).decode()})
   tid=color_indices[color];v={str(i):[round(-(float(p[0])-centres[idx])*scale,5),round((float(p[1])-ground)*scale,5),round(-(float(p[2])-zcentre)*scale,5)] for i,p in enumerate(points)}
   faces={str(i):{'vertices':[str(int(x)) for x in f], 'uv':{str(int(x)):[8,8] for x in f},'texture':tid} for i,f in enumerate(mesh.faces)}
   eid=uid();elements.append({'name':name,'type':'mesh','origin':[0,0,0],'rotation':[0,0,0],'vertices':v,'faces':faces,'uuid':eid,'export':True,'visibility':True});children.append(eid)
  gid=uid();project={'meta':{'format_version':'5.0','model_format':'free','box_uv':False},'name':'GLB original '+names[idx],'resolution':{'width':16,'height':16},'elements':elements,'groups':[{'name':'model_importat','origin':[0,0,0],'rotation':[0,0,0],'uuid':gid,'export':True,'visibility':True}],'outliner':[{'uuid':gid,'children':children}],'textures':textures}
  out=a.output_dir/('glb-original-'+names[idx]+'.bbmodel');out.write_text(json.dumps(project,separators=(',',':'))+'\n');print(out,'mesh-uri',len(elements),'triunghiuri',sum(len(x['faces']) for x in elements),'unitati/un. sursa',scale)
 print('source SHA256',hashlib.sha256(a.glb.read_bytes()).hexdigest())
if __name__=='__main__':main()
