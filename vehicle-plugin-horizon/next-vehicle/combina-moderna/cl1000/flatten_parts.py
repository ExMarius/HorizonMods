#!/usr/bin/env python3
"""Flatten imported Blockbench cube groups into provisional vehicle bones.

Uses the user's saved Blockbench project (not the GLB), applying each ancestor
rotation to each cube before assigning body/header/wheel groups. Bone mapping
and scale are provisional; no server files or resource packs are installed.
"""
import argparse,copy,itertools,json,math,uuid,warnings
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation

def uid():return str(uuid.uuid4())
def rot(a):return Rotation.from_euler('xyz',a,degrees=True).as_matrix()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('source',type=Path);ap.add_argument('output',type=Path);ap.add_argument('--width',type=float,default=4.8);a=ap.parse_args()
 if a.source.resolve()==a.output.resolve():ap.error('input and output must differ')
 p=json.loads(a.source.read_text());groups={g['uuid']:g for g in p.get('groups',[])};elements={e['uuid']:e for e in p.get('elements',[])};data=[];seen=set()
 names={'wheel1_20':'wheel_fr','wheel2_38':'wheel_fl','wheel3_75':'wheel_rr','wheel4_93':'wheel_rl','pipe_301':'unloading_auger','SEAT_331':'seat_driver','rullo_481':'reel','SPIKES_423':'header_assembly','SPIKES2_378':'header_assembly'}
 def walk(node,R,t,parent_origin,classification=None):
  if isinstance(node,str):
   e=elements[node];seen.add(node)
   if e.get('type')!='cube':raise ValueError('Only cubes are supported')
   if not e.get('export',True) or not e.get('visibility',True):return
   origin=np.asarray(e.get('origin',[0,0,0]),dtype=float);lo=np.asarray(e['from'],dtype=float);hi=np.asarray(e['to'],dtype=float)
   ew=t+R@(origin-parent_origin);re=R@rot(e.get('rotation',[0,0,0]));corners=np.array([ew+re@(np.array(c)-origin) for c in itertools.product(*zip(lo,hi))]);center=(corners.min(axis=0)+corners.max(axis=0))/2
   bone=classification or ('header_assembly' if center[2]<-32 and center[1]<35.2 else 'body')
   data.append({'element':e,'origin':origin,'lo':lo,'hi':hi,'ew':ew,'rotation':re,'corners':corners,'bone':bone});return
  info=groups[node['uuid']];origin=np.asarray(info.get('origin',[0,0,0]),dtype=float);gg=R@rot(info.get('rotation',[0,0,0]));tt=t+R@(origin-parent_origin);newclass=names.get(info.get('name'),classification)
  if info.get('visibility',True):
   for c in node.get('children',[]):walk(c,gg,tt,origin,newclass)
 for node in p.get('outliner',[]):walk(node,np.eye(3),np.zeros(3),np.zeros(3))
 if not data:raise ValueError('No visible cubes')
 if seen!=set(elements):raise ValueError('Some elements not reachable from visible outliner')
 allpoints=np.vstack([d['corners'] for d in data]);low=allpoints.min(axis=0);high=allpoints.max(axis=0);f=a.width*16/(high[0]-low[0]);offset=np.array([-(low[0]+high[0])/2,-low[1],0]);
 if not math.isfinite(f) or f<=0:raise ValueError('invalid width')
 for d in data:
  d['ew']=(d['ew']+offset)*f;d['corners']=(d['corners']+offset)*f;d['lo']=(d['lo']-d['origin'])*f;d['hi']=(d['hi']-d['origin'])*f
 def center(bone,fallback):
  pts=[d['corners'] for d in data if d['bone']==bone]
  if not pts:return fallback
  v=np.vstack(pts);return ((v.min(axis=0)+v.max(axis=0))/2).tolist()
 # Estimated hinge and outlet from original geometry; verified only by client.
 definitions=[('body',[0,0,0],None),('header_assembly',((np.array([0,20.8,-28.8])+offset)*f).tolist(),'body'),('reel',center('reel',[0,8,-50]),'header_assembly'),('intake_auger',center('header_assembly',[0,8,-40]),'header_assembly'),('unloading_auger',((np.array([-21.92,76.8,28.8])+offset)*f).tolist(),'body')]
 for n in ('wheel_fl','wheel_fr','wheel_rl','wheel_rr','seat_driver'):definitions.append((n,center(n,[0,0,0]),'body'))
 groups=[];roots=[];nodes={};out=[]
 for n,origin,parent in definitions:
  ident=uid();groups.append({'name':n,'uuid':ident,'origin':[round(float(x),5) for x in origin],'rotation':[0,0,0],'export':True,'visibility':True});nodes[n]={'uuid':ident,'children':[]};(roots if parent is None else nodes[parent]['children']).append(nodes[n])
 for d in data:
  e=copy.deepcopy(d['element']);e['from']=[round(float(x),5) for x in d['ew']+d['lo']];e['to']=[round(float(x),5) for x in d['ew']+d['hi']];e['origin']=[round(float(x),5) for x in d['ew']]
  with warnings.catch_warnings():warnings.simplefilter('ignore');angles=Rotation.from_matrix(d['rotation']).as_euler('xyz',degrees=True)
  e['rotation']=[round(float(x),5) if abs(x)>1e-6 else 0 for x in angles];out.append(e);nodes[d['bone']]['children'].append(e['uuid'])
 p.update({'name':p.get('name','CL1000')+' - grupuri pentru vehicul','elements':out,'groups':groups,'outliner':roots});a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(p,separators=(',',':'))+'\n')
 print('Cuburi',len(out),'scara',round(f,5),'limite blocuri',((high-low)*f/16).round(3).tolist());print('grupuri',{n:sum(d['bone']==n for d in data) for n,_,_ in definitions})
if __name__=='__main__':main()
