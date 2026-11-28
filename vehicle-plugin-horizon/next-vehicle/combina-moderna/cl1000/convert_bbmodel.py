#!/usr/bin/env python3
"""Convert axis-aligned box meshes in a Blockbench project into editable cubes.

Retains the input groups, rotations, pivots and embedded textures. Each mesh
must have eight axis-aligned corners and twelve triangular faces forming six
rectangles; unsupported data is rejected, not silently approximated. UV bounds
are reconstructed from the original face vertices and may still need visual
verification in Blockbench/Minecraft.
"""
import argparse,copy,json,math
from collections import defaultdict
from pathlib import Path

FACE_INFO={('x',1):'east',('x',0):'west',('y',1):'up',('y',0):'down',('z',1):'south',('z',0):'north'}
def close(a,b):return abs(a-b)<1e-5

def convert(e):
 if e.get('type')!='mesh':raise ValueError('Not a mesh: '+e.get('name','?'))
 vertices=e.get('vertices',{});v=list(vertices.values())
 if len(v)!=8 or any(len(p)!=3 or not all(math.isfinite(float(x)) for x in p) for p in v):raise ValueError('Mesh is not an eight-corner box: '+e.get('name','?'))
 lo=[min(p[i] for p in v) for i in range(3)];hi=[max(p[i] for p in v) for i in range(3)]
 if any(close(lo[i],hi[i]) for i in range(3)) or any(not (close(p[i],lo[i]) or close(p[i],hi[i])) for p in v for i in range(3)):raise ValueError('Mesh is not axis-aligned: '+e.get('name','?'))
 sides=defaultdict(list)
 for face in e.get('faces',{}).values():
  ids=face.get('vertices',[])
  if len(ids)!=3 or any(i not in vertices for i in ids):raise ValueError('Not a triangle: '+e.get('name','?'))
  points=[vertices[i] for i in ids];matches=[(axis,flag) for axis in range(3) for flag,bound in enumerate((lo[axis],hi[axis])) if all(close(p[axis],bound) for p in points)]
  if len(matches)!=1:raise ValueError('Triangle is not on a box face: '+e.get('name','?'))
  axis,flag=matches[0];sides[FACE_INFO[('xyz'[axis],flag)]].append(face)
 if len(sides)!=6 or any(len(f)!=2 for f in sides.values()):raise ValueError('Missing box faces: '+e.get('name','?'))
 corners={'east':([hi[0],hi[1],hi[2]],[hi[0],lo[1],lo[2]]),'west':([lo[0],hi[1],lo[2]],[lo[0],lo[1],hi[2]]),'up':([lo[0],hi[1],lo[2]],[hi[0],hi[1],hi[2]]),'down':([lo[0],lo[1],hi[2]],[hi[0],lo[1],lo[2]]),'south':([lo[0],hi[1],hi[2]],[hi[0],lo[1],hi[2]]),'north':([hi[0],hi[1],lo[2]],[lo[0],lo[1],lo[2]])}
 outfaces={}
 for name,triangles in sides.items():
  if triangles[0].get('texture')!=triangles[1].get('texture'):raise ValueError('Different textures on one cube face: '+e.get('name','?'))
  uv={}
  for face in triangles:
   for ident in face['vertices']:
    if ident not in face.get('uv',{}):raise ValueError('Missing UV')
    point=tuple(round(float(x),5) for x in vertices[ident]);coordinate=face['uv'][ident]
    if point in uv and any(not close(a,b) for a,b in zip(uv[point],coordinate)):raise ValueError('UV seam within a face')
    uv[point]=coordinate
  p0,p1=(tuple(round(float(x),5) for x in p) for p in corners[name])
  if p0 not in uv or p1 not in uv:raise ValueError('Missing UV corner')
  outfaces[name]={'uv':[float(x) for x in uv[p0]+uv[p1]],'texture':triangles[0].get('texture')}
 origin=e.get('origin',[0,0,0]);result=copy.deepcopy(e)
 for k in ('vertices','shading'):result.pop(k,None)
 result.update({'type':'cube','box_uv':False,'from':[origin[i]+lo[i] for i in range(3)],'to':[origin[i]+hi[i] for i in range(3)],'faces':outfaces})
 return result

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('source',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args()
 if a.source.resolve()==a.output.resolve():ap.error('Output must differ')
 p=json.loads(a.source.read_text());elements=p.get('elements',[]);p['elements']=[convert(e) for e in elements];p['name']=p.get('name','model')+' cuburi'
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(p,separators=(',',':'))+'\n');print('Converted',len(elements),'mesh boxes to cubes; retained',len(p.get('groups',[])),'groups and',len(p.get('textures',[])),'textures:',a.output)
if __name__=='__main__':main()
