#!/usr/bin/env python3
"""Generate candidate item-model parts for GD-3.2 (not installed).

Item models are authored at half the 16 units/block reference dimensions;
ItemDisplay scale 2 restores the requested size. Coordinate origin is 8,8,8.
Rotating gangs, wheels and the jack are deliberately separate models.
This is a vanilla-cuboid approximation; visually compare it to preview.html.
"""
import json,struct,sys,zlib
from pathlib import Path
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('generated')
OUT.mkdir(parents=True,exist_ok=True)
COLORS={'blue':'1e6bb8','darkblue':'174c83','dark':'262626','steel':'c8d0d8','rubber':'1e1e1e','cream':'e6dcc5','weight':'3a3a3a'}
TEXTURES={n:'vehicle:item/gd32_'+n for n in COLORS}
def png(rgb):
 def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b'\0'+bytes.fromhex(rgb)+b'\xff'))+chunk(b'IEND',b'')
def coord(x):return round(8+x/2,5)
def part(name,lo,hi,material,rotation=None):
 e={'name':name,'from':[coord(x) for x in lo],'to':[coord(x) for x in hi],
    'faces':{f:{'uv':[0,0,16,16],'texture':'#'+material} for f in ('north','south','east','west','up','down')}}
 if rotation:
  axis,angle,origin=rotation;e['rotation']={'axis':axis,'angle':angle,'origin':[coord(x) for x in origin]}
 for lo_,hi_ in zip(e['from'],e['to']):
  if lo_<-16 or hi_>32 or lo_>=hi_:raise ValueError('invalid bounds '+name)
 return e
D={k:[] for k in ('body','gang_frame','gang_front','gang_rear','wheel','jack')}
def add(model,name,lo,hi,mat,rot=None):D[model].append(part(name,lo,hi,mat,rot))
# Main frame is authored about its actual ground root.
for x in (-5,5):add('body','longitudinal rail '+str(x),(x-1.25,10,-20),(x+1.25,12.5,12),'blue')
for z in (-20,-3,12):add('body','crossmember '+str(z),(-10,10,z-1.25),(10,12.5,z+1.25),'blue')
# Approximate the drawbar angle with the nearest vanilla 22.5° element rotation.
for side in (-1,1):
 x=side*3.5
 add('body','drawbar arm '+str(side),(x-.85,10.15,-35),(x+.85,11.85,-19),'blue',('y',side*22.5,(x,11,-27)))
add('body','coupler plate',(-1.7,9.8,-36.6),(1.7,11.2,-33.7),'darkblue')
# Eye uses 4 small connected elements with an open center.
for x in (-1.2,1.2):add('body','coupler eye side '+str(x),(x-.3,10.05,-37),(x+.3,10.95,-35),'dark')
for z in (-37,-35):add('body','coupler eye end '+str(z),(-1.2,10.05,z-.3),(1.2,10.95,z+.3),'dark')
for side in (-1,1):
 x=side*12
 add('body','weight tray '+str(side),(x-4,12.5,-21),(x+4,14.5,-15),'darkblue')
 for i in (-1,0,1):add('body','counterweight '+str((side,i)),(x+i*2.35-1.05,14.5,-20.5),(x+i*2.35+1.05,16.3,-15.5),'weight')
# Frame for each gang is rendered at its own 18° world yaw.
add('gang_frame','carrier',(-11.5,8.5,-1),(11.5,10.5,1),'blue')
for i,x in enumerate((-8.4,0,8.4)):
 add('gang_frame','bearing '+str(i),(x-.425,4.2,-.55),(x+.425,8.5,.55),'dark')
for i in range(8):
 x=(i-3.5)*2.8
 add('gang_frame','scraper hanger '+str(i),(x+.26,4.5,-.275),(x+.46,9.5,.275),'dark')
 add('gang_frame','scraper blade '+str(i),(x+.26,1.7,-.35),(x+.46,4.5,.85),'steel')
# Each blade is an octagonal-looking union of strips. Rotations remain valid
# vanilla (0 or ±45°); all pieces share the axle pivot for animation.
for model in ('gang_front','gang_rear'):
 add(model,'gang shaft',(-11.5,-.5,-.5),(11.5,.5,.5),'dark')
 for i in range(8):
  x=(i-3.5)*2.8
  for n,lo,hi,rot in [
   ('vertical',(-.2,-4.1,-1.65),(.2,4.1,1.65),None),
   ('horizontal',(-.2,-1.65,-4.1),(.2,1.65,4.1),None),
   ('diagonal_a',(-.2,-4.1,-1.65),(.2,4.1,1.65),('x',45,(x,0,0))),
   ('diagonal_b',(-.2,-4.1,-1.65),(.2,4.1,1.65),('x',-45,(x,0,0)))]:
   lo=(lo[0]+x,lo[1],lo[2]);hi=(hi[0]+x,hi[1],hi[2]);add(model,f'disc_{i}_{n}',lo,hi,'steel',rot)
  add(model,'disc hub '+str(i),(x-.32,-.72,-.72),(x+.32,.72,.72),'dark')
# A common wheel is symmetric, so one asset serves both sides without mirroring.
for i in range(4):
 if i == 2:
  add('wheel','tire segment '+str(i),(-1.75,-2.1,-5.4),(1.75,2.1,5.4),'rubber')
 else:
  angle={0:0,1:45,3:-45}[i]
  add('wheel','tire segment '+str(i),(-1.75,-5.4,-2.1),(1.75,5.4,2.1),'rubber',('x',angle,(0,0,0)) if angle else None)
for x in (-1.76,1.76):
 add('wheel','rim '+str(x),(x-.08,-3.1,-3.1),(x+.08,3.1,3.1),'cream')
 add('wheel','hub '+str(x),(x-.18,-.8,-.8),(x+.18,.8,.8),'dark')
# Stand is rendered only when uncoupled, as a discrete display.
add('jack','jack pole',(-.45,0,-.45),(.45,9,.45),'dark')
add('jack','jack foot',(-1.4,0,-1.2),(1.4,.7,1.2),'dark')
for name,parts in D.items():
 (OUT/('gd32_'+name+'.json')).write_text(json.dumps({'textures':TEXTURES,'elements':parts},indent=2)+'\n')
for name,rgb in COLORS.items():(OUT/('gd32_'+name+'.png')).write_bytes(png(rgb))
print('GD-3.2 candidate models:',{k:len(v) for k,v in D.items()})
