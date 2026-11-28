#!/usr/bin/env python3
"""Experimental GLB-to-vanilla cube conversion. Requires visual validation.
Source: BMW M6 1988 Custom by Sprint, CC BY 4.0. See ATTRIBUTION.md.
"""
import json, math, struct, sys
from pathlib import Path
BASE=Path(__file__).parent
SRC=BASE/'assets/source.glb'
OUTPUT=Path(sys.argv[1]) if len(sys.argv)>1 else BASE/'generated'
OUTPUT.mkdir(parents=True,exist_ok=True)
b=SRC.read_bytes(); length,kind=struct.unpack_from('<II',b,12)
if b[:4]!=b'glTF' or kind!=0x4e4f534a: raise ValueError('Not GLB 2')
g=json.loads(b[20:20+length]); off=20+length; n,kind=struct.unpack_from('<II',b,off); blob=b[off+8:off+8+n]
if kind!=0x004e4942:raise ValueError('Missing binary chunk')
def acc(idx):
 a=g['accessors'][idx]; v=g['bufferViews'][a['bufferView']]; typ=a['type']; ct=a['componentType']; cols={'VEC3':3,'VEC2':2,'SCALAR':1}[typ]; fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[ct];size=struct.calcsize('<'+fmt)*cols;stride=v.get('byteStride',size);start=v.get('byteOffset',0)+a.get('byteOffset',0)
 return [struct.unpack_from('<'+fmt*cols,blob,start+i*stride) for i in range(a['count'])]
def rounded(x):return round(x,5)
# Source groups 186-278 were identified spatially, but require visual review.
def wheel(n):
 for low,hi,name,center in ((187,209,'rear_left',(.109375,.15625,-.1875)),(210,232,'front_left',(.109375,.15625,1.125)),(233,255,'front_right',(.890625,.15625,1.125)),(256,278,'rear_right',(.890625,.15625,-.1875))):
  if low<=n<=hi:return name,center
 return 'body',(.5,0,.5)
D={'body':[],'rear_left':[],'front_left':[],'rear_right':[],'front_right':[]}; issues=[]
tex={'0':'vehicle:item/bmw_m6_texture_0','1':'vehicle:item/bmw_m6_texture_1','white':'vehicle:item/bmw_m6_white'}
N=g['nodes'];parents=N[3]['children']
for index in parents:
 node=N[index];name=node.get('name','');suffix=name.rsplit('_',1)[-1]; number=int(suffix) if suffix.isdigit() else -1; key,center=wheel(number); m=node.get('matrix',[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]);
 # GLTF group matrices are column-major and only rotate around a single axis.
 axis=None;ang=0
 if abs(m[1])>1e-5: axis='z';ang=math.degrees(math.atan2(m[1],m[0]))
 elif abs(m[2])>1e-5:axis='y';ang=math.degrees(math.atan2(m[8],m[0]))
 elif abs(m[6])>1e-5:axis='x';ang=math.degrees(math.atan2(m[6],m[5]))
 if axis:
  angle=round(ang/22.5)*22.5
  if abs(angle-ang)>1e-3 or abs(angle)>45:issues.append(f'{name}: unsupported rotation {ang}');continue
 else:angle=0
 trans=[m[12+i] for i in range(3)]
 primitives=[]
 for child in node.get('children',[]):
  if 'mesh' not in N[child]:continue
  for pr in g['meshes'][N[child]['mesh']]['primitives']:
   positions=acc(pr['attributes']['POSITION']); normals=acc(pr['attributes']['NORMAL']);uv=acc(pr['attributes']['TEXCOORD_0']) if 'TEXCOORD_0' in pr['attributes'] else [(0,0)]*len(positions)
   primitives.append((pr,positions,normals,uv))
 if not primitives:continue
 pts=[p for _,pos,_,_ in primitives for p in pos];mins=[min(p[i] for p in pts) for i in range(3)];maxs=[max(p[i] for p in pts) for i in range(3)]
 origin=[8+(trans[i]-center[i])*16 for i in range(3)]
 element={'name':name,'from':[rounded(origin[i]+mins[i]*16) for i in range(3)],'to':[rounded(origin[i]+maxs[i]*16) for i in range(3)],'faces':{}}
 if angle:element['rotation']={'angle':angle,'axis':axis,'origin':[rounded(x) for x in origin]}
 for pr,positions,normals,uv in primitives:
  mat=pr.get('material',0);matdef=g['materials'][mat].get('pbrMetallicRoughness',{}); ti=matdef.get('baseColorTexture',{}).get('index');texture='white' if ti is None else str(g['textures'][ti]['source'])
  byface={}
  for i,normal in enumerate(normals):
   axis_i=max(range(3),key=lambda x:abs(normal[x]));
   if abs(normal[axis_i])<.999: issues.append(f'{name}: non-cardinal normal');continue
   face={(0,1):'east',(0,-1):'west',(1,1):'up',(1,-1):'down',(2,1):'south',(2,-1):'north'}[(axis_i,1 if normal[axis_i]>0 else -1)]
   byface.setdefault(face,[]).append(uv[i])
  for face,coords in byface.items():
   us=[v[0]*16 for v in coords];vs=[v[1]*16 for v in coords]
   if face in element['faces']:issues.append(f'{name}: duplicate face {face}')
   element['faces'][face]={'uv':[rounded(min(us)),rounded(min(vs)),rounded(max(us)),rounded(max(vs))],'texture':'#'+texture}
 if any(x < -16.00001 or x > 32.00001 for a in ('from','to') for x in element[a]):issues.append(name+': out of vanilla bounds')
 D[key].append(element)
for key,els in D.items():
 (OUTPUT/(key+'.json')).write_text(json.dumps({'credit':'Adapted from BMW M6 1988 Custom by Sprint, CC BY 4.0','textures':tex,'elements':els},indent=2)+'\n')
(OUTPUT/'conversion-issues.json').write_text(json.dumps(issues,indent=2)+'\n')
print('model elements', {k:len(v) for k,v in D.items()});print('issues',len(issues));print('\n'.join(issues[:20]));print('WARNING: UV orientation and wheel group membership require client-side visual verification')
