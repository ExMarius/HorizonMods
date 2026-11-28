#!/usr/bin/env python3
"""Merge adjacent identical cuboids in each Blockbench bone without changing their union.

This operates on the user's existing voxel reconstruction, not on a redrawn
combine. It does not guess hidden geometry or alter colors. To avoid UV changes
only elements whose six faces share the same unrotated UV/texture are merged.
"""
import argparse,collections,json,math,uuid
from pathlib import Path
FACES=('north','south','east','west','up','down')

def key(e):
 if e.get('type','cube')!='cube' or any(e.get('rotation',[0,0,0])):return None
 faces=e.get('faces',{});v=[faces.get(f) for f in FACES]
 if any(x is None or x!=v[0] for x in v):return None
 return (json.dumps(v[0],sort_keys=True,separators=(',',':')),e.get('export',True),e.get('visibility',True))

def merge_axis(boxes,axis):
 runs=collections.defaultdict(list)
 for lo,hi in boxes:
  other=[i for i in range(3) if i!=axis]
  runs[tuple((lo[i],hi[i]) for i in other)].append((lo[axis],hi[axis]))
 result=[]
 for fixed,segments in runs.items():
  segments.sort();start,end=segments[0]
  def emit(start,end):
   lo=[0]*3;hi=[0]*3;lo[axis]=start;hi[axis]=end
   for i,pair in zip((i for i in range(3) if i!=axis),fixed):lo[i],hi[i]=pair
   result.append((tuple(lo),tuple(hi)))
  for x,y in segments[1:]:
   if abs(x-end)<1e-7:end=y
   else:emit(start,end);start,end=x,y
  emit(start,end)
 return result

def optimize(source):
 p=json.loads(source.read_text());els={e['uuid']:e for e in p['elements']};out=[];seen=set();stats={}
 def visit(node):
  pending=collections.defaultdict(list);first={};keep=[];before=0
  for c in node['children']:
   if isinstance(c,dict):visit(c);keep.append(c);continue
   if c in seen:raise ValueError('Duplicate element reference')
   seen.add(c);e=els[c];before+=1;k=key(e)
   if k is None:out.append(e);keep.append(c);continue
   lo=tuple(round(float(x),7) for x in e['from']);hi=tuple(round(float(x),7) for x in e['to'])
   if not all(math.isfinite(x) for x in lo+hi) or any(a>=b for a,b in zip(lo,hi)):raise ValueError('Invalid cuboid')
   pending[k].append((lo,hi));first[k]=e
  after=len(keep)-sum(isinstance(c,dict) for c in keep)
  for k,boxes in pending.items():
   while True:
    old=len(boxes)
    for axis in (0,1,2):boxes=merge_axis(boxes,axis)
    if len(boxes)==old:break
   for lo,hi in boxes:
    e=first[k].copy();eid=str(uuid.uuid4());e.update({'uuid':eid,'from':list(lo),'to':list(hi),'origin':[(lo[i]+hi[i])/2 for i in range(3)]});out.append(e);keep.append(eid);after+=1
  node['children']=keep;stats[node['uuid']]={'before':before,'after':after}
 for n in p['outliner']:
  if not isinstance(n,dict):raise ValueError('Unsupported loose root element')
  visit(n)
 if seen!=set(els):raise ValueError('Some elements were not attached to a group')
 p['elements']=out;p['name']+=' - cuburi reunite';return p,stats

def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('source',type=Path);a.add_argument('output',type=Path);args=a.parse_args()
 if args.source.resolve()==args.output.resolve():a.error('Output must differ from source')
 project,stats=optimize(args.source);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(project,separators=(',',':'))+'\n');print(args.source.name,'before',sum(x['before'] for x in stats.values()),'after',len(project['elements']),'=>',args.output)
if __name__=='__main__':main()
