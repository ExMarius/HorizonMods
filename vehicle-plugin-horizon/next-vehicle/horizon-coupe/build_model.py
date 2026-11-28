#!/usr/bin/env python3
"""Original box-model sport coupe, authored in vanilla item model coordinates.

At scale 2 each model pixel is 1/8 block. Y=8 is ground. Body is 2 blocks
wide, 4 blocks long; front is +Z. Four independently animated wheels.
"""
import json,sys
from pathlib import Path
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent/'generated'
OUT.mkdir(parents=True,exist_ok=True)
textures={k:'vehicle:item/horizon_coupe_'+k for k in ('red','darkred','black','rubber','silver','rim','lamp','tail','amber','seat','white')}
def cuboid(name,lo,hi,tex,rot=None):
 e={'name':name,'from':list(lo),'to':list(hi),'faces':{f:{'uv':[0,0,16,16],'texture':'#'+tex} for f in ('north','south','east','west','up','down')}}
 if rot:e['rotation']=rot
 assert all(-16<=x<=32 for x in lo+hi) and all(a<b for a,b in zip(lo,hi))
 return e
body=[]
def box(name,lo,hi,texture,rotation=None):body.append(cuboid(name,lo,hi,texture,rotation))
def r(axis,angle,origin):return {'axis':axis,'angle':angle,'origin':origin}
# Engine bay, central floor, sill panels and fenders: wheel wells left open.
box('floor',(1,10,-7),(15,11,23),'black')
box('nose front panel',(0,11,22),(16,16,24),'red')
box('rear panel',(0,11,-8),(16,16,-6),'red')
box('hood',(0.5,15,9),(15.5,16.1,22),'red')
box('hood raised center',(3,16.1,10),(13,16.45,21),'red')
box('rear deck',(0.5,15,-6),(15.5,16.1,-1),'red')
for side in (0,1):
 x0,x1=(0,1.2) if side==0 else (14.8,16)
 for name,z0,z1 in [('front end',20,22),('door',-1.2,8),('rear end',-6,-4.5)]:box(f'{name} side {side}',(x0,10,z0),(x1,15,z1),'red')
 for z in (-4.5,8):box(f'wheel arch upper {side} {z}',(x0,13.7,z),(x1,15,z+12),'red') if z==8 else box(f'wheel arch upper {side} {z}',(x0,13.7,z),(x1,15,z+3.3),'red')
 box(f'door upper {side}',(x0,15,-1),(x1,16,9),'red')
 box(f'side molding {side}',(x0-.04,13,-1),(x1+.04,13.3,9),'black')
 box(f'rocker {side}',(x0,9.5,-1),(x1,10.3,8),'darkred')
 box(f'handle {side}',(x0-.08,15.1,1),(x1+.08,15.4,2.1),'silver')
 # Door/window pillars: open windows allow player visibility.
 box(f'A pillar {side}',(x0+.15,16,7.2),(x1-.15,20.8,8),'red',r('x',-22.5,[8,16,7.2]))
 box(f'B pillar {side}',(x0+.15,16,1.7),(x1-.15,21,2.3),'black')
 box(f'C pillar {side}',(x0+.15,16,-2),(x1-.15,20.8,-1.2),'red',r('x',22.5,[8,16,-1.2]))
 box(f'window sill {side}',(x0,16,-1),(x1,16.25,7.2),'silver')
 box(f'mirror stem {side}',(x0-.4,16,6.5),(x1+.4,16.45,7.2),'black')
 box(f'mirror {side}',(x0-.55,16.35,6.25),(x1+.55,17.1,7.35),'black')
box('roof',(1,20.4,-1.7),(15,21.1,6.7),'red')
box('windscreen top frame',(1,20.1,6.5),(15,20.5,7),'black')
box('windscreen bottom frame',(1,16,7.6),(15,16.3,8.1),'black')
box('rear glass top frame',(1,20.1,-1.8),(15,20.5,-1.3),'black')
box('dashboard',(1.2,15.6,6.5),(14.8,16.5,8.2),'black')
box('instrument binnacle',(9.2,16.4,6.9),(12.8,16.8,7.7),'black')
box('centre console',(7,11.2,0),(9,14.4,7),'black')
box('gear shifter',(7.7,14.2,2.6),(8.3,15.4,3.2),'silver')
for x in (3.5,9.5):
 box('front seat cushion '+str(x),(x,11,2.7),(x+3,12.3,5.7),'seat')
 box('front seat back '+str(x),(x,12,2.6),(x+3,16.7,3.5),'seat')
 box('front headrest '+str(x),(x+.5,16.5,2.5),(x+2.5,17.8,3.4),'seat')
 box('rear seat cushion '+str(x),(x,11,-3.2),(x+3,12.3,-.5),'seat')
 box('rear seat back '+str(x),(x,12,-3.3),(x+3,15.8,-2.5),'seat')
# Steering ring, dashboard and external sport trim.
for name,lo,hi in [('top',(9.3,17.5,5.3),(12.7,17.8,5.7)),('bottom',(9.3,14.5,5.3),(12.7,14.8,5.7)),('left',(9.1,14.8,5.3),(9.4,17.5,5.7)),('right',(12.6,14.8,5.3),(12.9,17.5,5.7)),('hub',(10.6,15.5,5.2),(11.4,16.6,5.8))]:box('steering '+name,lo,hi,'black')
box('front fascia',(0,11.2,23.9),(16,15.1,24.15),'black')
for i,x in enumerate((1.3,3.6,10.1,12.4)):
 box('lamp bezel '+str(i),(x,12.2,24.1),(x+2.1,14.4,24.3),'silver')
 box('headlamp '+str(i),(x+.25,12.45,24.29),(x+1.85,14.15,24.4),'lamp')
for x in (6.1,8.1):
 box('front grille frame '+str(x),(x,12.0,24.15),(x+1.8,14.8,24.36),'silver')
 box('front grille '+str(x),(x+.2,12.2,24.35),(x+1.6,14.6,24.45),'black')
box('front bumper',(-.3,10.5,24),(16.3,11.35,24.75),'black')
box('front bumper trim',(-.3,11,24.72),(16.3,11.17,24.82),'silver')
box('rear bumper',(-.3,10.5,-8.7),(16.3,11.35,-8),'black')
for x in (1,11):
 box('tail lamp '+str(x),(x,12.6,-8.2),(x+4,14.3,-7.95),'tail')
 box('rear indicator '+str(x),(x,12.65,-8.23),(x+1,14.25,-8.19),'amber')
box('rear plate',(6,12.3,-8.25),(10,13.6,-8.15),'white')
for x in (1,14):box('spoiler mount '+str(x),(x,16,-7.3),(x+1,17.1,-6.6),'black')
box('rear wing',(0,17,-7.6),(16,17.5,-5.8),'darkred')
# Tire pivot centered at model (8,8,8). Square-edged 12-segment appearance.
w=[]
def wheel(name,lo,hi,texture,rot=None):w.append(cuboid(name,lo,hi,texture,rot))
wheel('tire central',(6.7,5.8,5.8),(9.3,10.2,10.2),'rubber')
for a in (-1,1):
 wheel('tire vertical '+str(a),(6.7,7.1,5.2 if a<0 else 10.2),(9.3,8.9,5.8 if a<0 else 10.8),'rubber')
 wheel('tire horizontal '+str(a),(6.7,5.2 if a<0 else 10.2,7.1),(9.3,5.8 if a<0 else 10.8,8.9),'rubber')
for side in (-1,1):
 x0,x1=(6.55,6.7) if side<0 else (9.3,9.45)
 wheel('rim '+str(side),(x0,6.4,6.4),(x1,9.6,9.6),'rim')
 wheel('hub '+str(side),(x0-.03,7.6,7.6),(x1+.03,8.4,8.4),'silver')
 for dz in (-1,1):wheel('rim slit '+str(side)+' '+str(dz),(x0-.02,7.75,8+dz*.95-.25),(x1+.02,8.25,8+dz*.95+.25),'black')
for name,e in [('body',body),('wheel',w)]:
 (OUT/(name+'.json')).write_text(json.dumps({'textures':textures,'elements':e},indent=2)+'\n')
print('original coupe:',len(body),'body parts,',len(w),'wheel parts; width 2, length 4, height 1.64 blocks at scale 2')
