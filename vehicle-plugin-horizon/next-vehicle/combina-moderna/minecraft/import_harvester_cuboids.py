#!/usr/bin/env python3
"""Recover editable cuboids and embedded textures from the supplied harvester GLB.

Preserves each cuboid's geometry and rotation; retains atlas UV bounding boxes.
UV orientation, tentative pivots, transparency and scale require client review.
The resulting Blockbench free file is not itself a Minecraft resource pack.
Dependencies: numpy, scipy, trimesh. No server or installed pack is modified.
"""
import argparse,base64,collections,json,struct,uuid,warnings
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation

def uid():return str(uuid.uuid4())
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('source',type=Path);ap.add_argument('output',type=Path);ap.add_argument('--width-blocks',type=float,default=4.8);a=ap.parse_args()
 if a.source.resolve()==a.output.resolve():ap.error('input and output must differ')
 raw=a.source.read_bytes()
 if raw[:4]!=b'glTF' or struct.unpack_from('<I',raw,4)[0]!=2:raise ValueError('Expected GLB 2')
 jsonlen,kind=struct.unpack_from('<II',raw,12);gltf=json.loads(raw[20:20+jsonlen]);off=20+jsonlen
 binlen,binkind=struct.unpack_from('<II',raw,off);binary=raw[off+8:off+8+binlen]
 if kind!=0x4e4f534a or binkind!=0x004e4942:raise ValueError('Expected JSON and BIN chunks')
 scene=trimesh.load(a.source,force='scene');width=float(scene.extents[0]);factor=16*a.width_blocks/width
 if not np.isfinite(factor) or factor<=0:raise ValueError('Invalid scaling')
 ground=float(scene.bounds[0,1]);xc=float((scene.bounds[0,0]+scene.bounds[1,0])/2)
 offset=np.array([-xc,-ground,0.0]);matrices=scene.graph;nodeparent={c:i for i,n in enumerate(gltf['nodes']) for c in n.get('children',[])}
 faces_names=('east','west','up','down','south','north');textures=[];material_tex={}
 for mi,m in enumerate(gltf['materials']):
  ti=m.get('pbrMetallicRoughness',{}).get('baseColorTexture',{}).get('index')
  if ti is None:raise ValueError('Material without embedded base color')
  im=gltf['images'][gltf['textures'][ti]['source']];view=gltf['bufferViews'][im['bufferView']]
  data=binary[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']]
  if im.get('mimeType')!='image/png' or data[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError('Only embedded PNG atlases supported')
  w,h=struct.unpack_from('>II',data,16);material_tex[mi]=len(textures);textures.append({'name':f'harvester_atlas_{mi}.png','id':str(len(textures)),'uuid':uid(),'width':w,'height':h,'uv_width':16,'uv_height':16,'particle':False,'render_mode':'default','mode':'bitmap','saved':False,'source':'data:image/png;base64,'+base64.b64encode(data).decode()})
 lookup={'wheel1_20':'wheel_fr','wheel2_38':'wheel_fl','wheel3_75':'wheel_rr','wheel4_93':'wheel_rl','pipe_301':'unloading_auger','SEAT_331':'seat_driver','rullo_481':'reel','SPIKES_423':'header_assembly','SPIKES2_378':'header_assembly'}
 members=collections.defaultdict(list);unsupported=[];other_meshes=[]
 for i,node in enumerate(gltf['nodes']):
  if 'mesh' not in node:continue
  if node.get('name') not in matrices.nodes_geometry:raise ValueError('Missing mesh node '+str(i))
  transform,geom=matrices[node['name']];mesh=scene.geometry[geom]
  # Preserve non-cuboids as Blockbench meshes; vanilla export cannot include them.
  if len(mesh.faces)!=12:
   unsupported.append({'node':node.get('name'),'triangles':len(mesh.faces)});other_meshes.append((i,node,transform,mesh));continue
  n=i;bone=None
  while n in nodeparent:
   n=nodeparent[n];name=gltf['nodes'][n].get('name','')
   if name in lookup:bone=lookup[name];break
  b=trimesh.transform_points(mesh.vertices,transform);center=(b.min(axis=0)+b.max(axis=0))/2
  if bone is None:bone='header_assembly' if center[2]<-2.0 and center[1]<2.2 else 'body'
  members[bone].append((i,node,transform,mesh,b))
 def pivot_for(bone,fallback):
  members_b=members.get(bone,[])
  if not members_b:return list((np.array(fallback)+offset)*factor)
  xyz=np.vstack([v[4] for v in members_b]);return list(((xyz.min(axis=0)+xyz.max(axis=0))/2+offset)*factor)
 definitions=[('body',[0,0,0],None),('header_assembly',list((np.array([0,1.3,-1.8])+offset)*factor),'body'),('reel',pivot_for('reel',[0,1.5,-4.5]),'header_assembly'),('intake_auger',list((np.array([0,1,-3])+offset)*factor),'header_assembly'),('unloading_auger',list((np.array([-1.37,4.8,1.8])+offset)*factor),'body')]
 for n in ('wheel_fl','wheel_fr','wheel_rl','wheel_rr'):definitions.append((n,pivot_for(n,[0,0,0]),'body'))
 definitions.append(('seat_driver',pivot_for('seat_driver',[0,3.5,0]),'body'))
 groups=[];nodes={};roots=[];elements=[]
 for name,origin,parent in definitions:
  id=uid();groups.append({'name':name,'uuid':id,'origin':[round(float(v),5) for v in origin],'rotation':[0,0,0],'export':True,'visibility':True});node={'uuid':id,'children':[]};nodes[name]=node;(roots if parent is None else nodes[parent]['children']).append(node)
 for bone,entries in members.items():
  for idx,node,t,mesh,world in entries:
   axis=np.max(np.abs(mesh.face_normals),axis=1)
   if not np.allclose(axis,1,atol=1e-4):raise ValueError('Non-cuboid mesh '+node['name'])
   mat=t[:3,:3];sc=np.linalg.norm(mat,axis=0)
   if not np.allclose(sc,1,atol=1e-5) or not np.allclose(mat.T@mat,np.eye(3),atol=1e-5) or np.linalg.det(mat)<0:raise ValueError('Unsupported mesh transform '+node['name'])
   with warnings.catch_warnings():
    warnings.simplefilter('ignore');angles=Rotation.from_matrix(mat).as_euler('xyz',degrees=True)
   origin=(t[:3,3]+offset)*factor;lo=(t[:3,3]+mesh.bounds[0]+offset)*factor;hi=(t[:3,3]+mesh.bounds[1]+offset)*factor
   prim=gltf['meshes'][node['mesh']]['primitives'];
   if len(prim)!=1:raise ValueError('Multiple primitives')
   texture=material_tex[prim[0].get('material',0)];uv=mesh.visual.uv;outfaces={}
   for face,axis_idx,sgn in [('east',0,1),('west',0,-1),('up',1,1),('down',1,-1),('south',2,1),('north',2,-1)]:
    mask=mesh.face_normals[:,axis_idx]*sgn>.999;inds=np.unique(mesh.faces[mask].ravel())
    if len(inds)<4:raise ValueError('Missing cube face '+node['name'])
    # Map the original UV at the cube's canonical upper-left and
    # lower-right corners; this retains flipped atlas coordinates.
    low,high=mesh.bounds
    corners={'east':([high[0],high[1],high[2]],[high[0],low[1],low[2]]),'west':([low[0],high[1],low[2]],[low[0],low[1],high[2]]),'up':([low[0],high[1],low[2]],[high[0],high[1],high[2]]),'down':([low[0],low[1],high[2]],[high[0],low[1],low[2]]),'south':([low[0],high[1],high[2]],[high[0],low[1],high[2]]),'north':([high[0],high[1],low[2]],[low[0],low[1],low[2]])}
    v0,v1=corners[face];pts=mesh.vertices[inds];j0=int(np.argmin(np.linalg.norm(pts-v0,axis=1)));j1=int(np.argmin(np.linalg.norm(pts-v1,axis=1)))
    uv0=uv[inds[j0]];uv1=uv[inds[j1]]
    outfaces[face]={'uv':[round(float(uv0[0]*16),6),round(float(uv0[1]*16),6),round(float(uv1[0]*16),6),round(float(uv1[1]*16),6)],'texture':texture}
   id=uid();el={'name':node.get('name',f'piece_{idx}'),'uuid':id,'type':'cube','box_uv':False,'from':[round(float(x),5) for x in lo],'to':[round(float(x),5) for x in hi],'origin':[round(float(x),5) for x in origin],'faces':outfaces,'export':True,'visibility':True}
   if not np.allclose(angles,0,atol=1e-6):el['rotation']=[round(float(x),5) for x in angles]
   elements.append(el);nodes[bone]['children'].append(id)
 for idx,node,t,mesh in other_meshes:
  pts=(trimesh.transform_points(mesh.vertices,t)+offset)*factor;vertices={str(i):[round(float(x),5) for x in p] for i,p in enumerate(pts)}
  texture=material_tex[gltf['meshes'][node['mesh']]['primitives'][0].get('material',0)]
  faces={str(i):{'vertices':[str(int(v)) for v in face],'uv':{str(int(v)):[round(float(x)*16,6) for x in mesh.visual.uv[v]] for v in face},'texture':texture} for i,face in enumerate(mesh.faces)}
  ident=uid();elements.append({'name':node.get('name','noncuboid'),'uuid':ident,'type':'mesh','origin':[0,0,0],'vertices':vertices,'faces':faces,'rotation':[0,0,0],'export':False,'visibility':True});nodes['body']['children'].append(ident)
 project={'meta':{'format_version':'5.0','model_format':'free','box_uv':False},'name':'Combina CL1000 importata','model_identifier':'horizon_combina_cl1000','resolution':{'width':16,'height':16},'elements':elements,'groups':groups,'outliner':roots,'textures':textures}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(project,separators=(',',':'))+'\n')
 print('Source width',width,'scale',factor,'cubes',len(elements)-len(other_meshes),'groups', {k:len(v) for k,v in members.items()},'non-cuboid preserved in Blockbench but excluded from item export',unsupported)
 print('UV rectangles retain atlas bounds but orientation and colors require in-game inspection.')
if __name__=='__main__':main()
