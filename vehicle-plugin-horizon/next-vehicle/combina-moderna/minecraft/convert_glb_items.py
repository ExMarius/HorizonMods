#!/usr/bin/env python3
"""Convert the supplied GLB's surfaces into experimental Minecraft item models.

Each mesh is voxelised in world coordinates and same-colour neighbouring
voxels are merged into cuboids. This is a *lossy* approximation: Minecraft item
models cannot express the original triangles. Output is a standalone 1.21.4
pack, not a plugin, and must not overwrite an existing pack.
Requires numpy, scipy and trimesh in a Python virtual environment.
"""
import argparse, base64, hashlib, json, math, struct, uuid, zipfile, zlib
from collections import defaultdict
from pathlib import Path
import numpy as np
import trimesh

CENTRES=(-585.0,29.0,561.0)
NAMES=('porumb','cereale','fara_heder')
FACES=('north','south','east','west','up','down')
def compact(value): return json.dumps(value,separators=(',',':')).encode()
def png(color):
 def chunk(kind,data): return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b'\x00'+bytes(color)))+chunk(b'IEND',b'')
def merge(cells):
 """Greedily merge equal-color occupied voxels to disjoint boxes."""
 cells=set(cells)
 while cells:
  x,y,z=min(cells);xe=x+1
  while (xe,y,z) in cells:xe+=1
  ye=y+1
  while all((i,ye,z) in cells for i in range(x,xe)):ye+=1
  ze=z+1
  while all((i,j,ze) in cells for i in range(x,xe) for j in range(y,ye)):ze+=1
  for i in range(x,xe):
   for j in range(y,ye):
    for k in range(z,ze):cells.remove((i,j,k))
  yield (x,y,z,xe,ye,ze)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('source',type=Path);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--pitch',type=float,default=8.0);ap.add_argument('--height',type=float,default=3.65)
 a=ap.parse_args()
 if not (2<=a.pitch<=20 and .1<=a.height<=10):ap.error('pitch must be 2..20, height .1..10')
 if len({a.source.resolve(),a.output.resolve(),a.manifest.resolve()})!=3:ap.error('Input and outputs must differ')
 scene=trimesh.load(a.source,force='scene');ground=float(scene.bounds[0,1]);height=float(scene.bounds[1,1]-ground);scale=16*a.height/height;regions=[[] for _ in CENTRES]
 for node in scene.graph.nodes_geometry:
  transform,key=scene.graph[node];obj=scene.geometry[key].copy();obj.apply_transform(transform)
  if not len(obj.vertices):continue
  pos=float(obj.bounds[:,0].mean());idx=int(np.argmin(np.abs(np.array(CENTRES)-pos)))
  material=getattr(obj.visual,'material',None);col=getattr(material,'baseColorFactor',None);color=tuple(int(x) for x in (col if col is not None else (180,180,180,255)))
  if len(color)!=4 or getattr(material,'baseColorTexture',None) is not None:raise ValueError('Unsupported material; refusing silent texture loss')
  regions[idx].append((obj,color))
 if any(not x for x in regions):raise ValueError('GLB does not match the expected three-vehicle layout')
 files={'pack.mcmeta':compact({'pack':{'pack_format':46,'description':'Horizon: modele GLB convertite experimental'}})};result=[]
 for idx,meshes in enumerate(regions):
  lo=np.min([m.bounds[0] for m,_ in meshes],axis=0);hi=np.max([m.bounds[1] for m,_ in meshes],axis=0);zc=float((lo[2]+hi[2])/2)
  by_color=defaultdict(set)
  for mesh,color in meshes:
   # Surface voxels: thin features survive, without inferring that a hollow
   # cab is solid. Snap mesh-local voxel grids to one shared global grid.
   points=mesh.voxelized(a.pitch).points
   grid=np.rint(points/a.pitch).astype(np.int64)
   by_color[color].update(map(tuple,grid.tolist()))
  textures={};elements=[]
  for index,(color,cells) in enumerate(sorted(by_color.items())):
   key=f't{index}';texture=f'item/combina_glb/{NAMES[idx]}/{key}'
   textures[key]='vehicle:'+texture;files[f'assets/vehicle/textures/{texture}.png']=png(color)
   for x,y,z,xe,ye,ze in merge(cells):
    # Rotate 180 degrees on Y so the source's attachment points toward -Z.
    wmin=np.array([-(xe-.5)*a.pitch+CENTRES[idx],(y-.5)*a.pitch-ground,-(ze-.5)*a.pitch+zc])*scale
    wmax=np.array([-(x-.5)*a.pitch+CENTRES[idx],(ye-.5)*a.pitch-ground,-(z-.5)*a.pitch+zc])*scale
    # Item model centred at 8; render with uniform ItemDisplay scale 8.
    p=[round(float(8+n/8),5) for n in wmin];q=[round(float(8+n/8),5) for n in wmax]
    if any(not -16<=v<=32 for v in p+q):raise ValueError(f'{NAMES[idx]} exceeds model limits')
    elements.append({'from':p,'to':q,'faces':{f:{'texture':'#'+key,'uv':[0,0,16,16]} for f in FACES}})
  name='combina_glb_'+NAMES[idx]
  files[f'assets/vehicle/models/item/{name}.json']=compact({'textures':textures,'elements':elements})
  files[f'assets/vehicle/items/{name}.json']=compact({'model':{'type':'minecraft:model','model':'vehicle:item/'+name}})
  result.append({'variant':NAMES[idx],'item_model':'vehicle:'+name,'display_scale':8,'meshes':len(meshes),'voxels':sum(map(len,by_color.values())),'cuboids':len(elements),'source_center_x':CENTRES[idx],'source_center_z':zc})
  print(NAMES[idx],len(meshes),'meshes',result[-1]['voxels'],'voxels',len(elements),'cuboids',flush=True)
 manifest={'source_sha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'source_ground_y':ground,'source_units_per_voxel':a.pitch,'assumed_height_blocks':a.height,'source_unit_to_model_units':scale,'warning':'Lossy surface voxelisation; static, no rig or crop logic; not tested in Minecraft. Items are NOT ready for live gameplay.','variants':result}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.manifest.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(a.output,'w',zipfile.ZIP_DEFLATED) as z:
  for name,data in sorted(files.items()):
   zi=zipfile.ZipInfo(name,(1980,1,1,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,data)
 a.manifest.write_bytes(compact(manifest)+b'\n')
if __name__=='__main__':main()
