#!/usr/bin/env python3
"""Author an editable Gloria-inspired 1:1 Blockbench model, no plugin changes."""
import base64, json, math, struct, uuid, zlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'downloads'/'horizon-combina-moderna.bbmodel'
CORN='--corn' in sys.argv
OUT=ROOT/'downloads'/'horizon-combina-moderna-porumb.bbmodel' if CORN else BASE
# Reuse every texture entry and the named bone UUIDs already in the project.
previous=json.loads(BASE.read_text()) if BASE.exists() else None
old_named={g['name']:g['uuid'] for g in previous['groups'] if g['name'] in {'body','header_assembly','reel','intake_auger','unloading_auger','wheel_fl','wheel_fr','wheel_rl','wheel_rr','seat_driver','access_ladder','rear_steering_axle','cutter_bar'}} if previous else {}
uid=lambda: str(uuid.uuid4())
palette={'rosu':'d92b2b','rosu_inchis':'85221b','rosu_lumina':'e54b32','crem':'f2f4f7','sasiu':'22252a','cauciuc':'1e1e1e','cauciuc_lumina':'30302e','metal':'a9aaa4','otel':'6e7373','negru':'121516','chihlimbar':'ffa52a','sticla':'8bb5b5','grau':'cfae59','grau_lumina':'e2c675','far':'fff1bf','bord':'3c3e3b','verde':'d92b2b','verde_inchis':'35383c','gps':'d7d9d6'}
def png(rgb,alpha=255):
 raw=b'\0'+bytes.fromhex(rgb)+bytes([alpha])
 def chunk(tag,data):return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')
textures=[]
for i,(name,color) in enumerate(palette.items()):
 textures.append({'name':f'{name}_{color}.png','id':str(i),'uuid':uid(),'width':1,'height':1,'uv_width':16,'uv_height':16,'particle':False,'render_mode':'default','mode':'bitmap','saved':False,'source':'data:image/png;base64,'+base64.b64encode(png(color,110 if name=='sticla' else 255)).decode()})
if previous:
 if len(previous['textures']) != len(textures): raise ValueError('Existing texture count changed; refusing to overwrite')
 if [t['name'] for t in previous['textures']] != [t['name'] for t in textures]: raise ValueError('Existing texture order changed; refusing to overwrite')
 textures=previous['textures']
tex={n:i for i,n in enumerate(palette)}
elements=[];groups=[];roots=[]
def group(name,origin,parent=None):
 id=old_named.get(name) or uid();groups.append({'name':name,'uuid':id,'export':True,'locked':False,'origin':origin,'rotation':[0,0,0],'color':0,'visibility':True,'isOpen':True})
 node={'uuid':id,'isOpen':True,'children':[]};(roots if parent is None else parent['children']).append(node);return node

def cube(g,name,a,b,color,rot=None,origin=None):
 assert all(a[i]<b[i] for i in range(3)),(name,a,b)
 id=uid();e={'name':name,'box_uv':False,'from':[round(v,4) for v in a],'to':[round(v,4) for v in b],'autouv':0,'color':0,'origin':origin or [(a[i]+b[i])/2 for i in range(3)],'faces':{s:{'uv':[0,0,16,16],'texture':tex[color]} for s in ('north','south','east','west','up','down')},'type':'cube','uuid':id,'export':True,'visibility':True}
 if rot:e['rotation']=rot
 elements.append(e);g['children'].append(id)
def box(g,n,x1,y1,z1,x2,y2,z2,c):cube(g,n,[x1,y1,z1],[x2,y2,z2],c)
def beam_yz(g,n,x,width,y1,z1,y2,z2,thickness,c):
 # Rectangular beam aligned to endpoints in the YZ plane, one solid rotated cube.
 y,z=(y1+y2)/2,(z1+z2)/2;length=math.hypot(y2-y1,z2-z1);angle=math.degrees(math.atan2(-(y2-y1),z2-z1))
 cube(g,n,[x-width/2,y-thickness/2,z-length/2],[x+width/2,y+thickness/2,z+length/2],c,[angle,0,0],[x,y,z])
def beam_xy(g,n,x1,y1,x2,y2,z1,z2,thickness,c):
 x,y=(x1+x2)/2,(y1+y2)/2;length=math.hypot(x2-x1,y2-y1);angle=-math.degrees(math.atan2(x2-x1,y2-y1))
 cube(g,n,[x-thickness/2,y-length/2,z1],[x+thickness/2,y+length/2,z2],c,[0,0,angle],[x,y,(z1+z2)/2])

def wheel(name,x,y,z,r,width,count,parent=None):
 g=group(name,[x,y,z],parent);half=width/2;step=360/count
 # Fill the tyres and hubs with crossed rectangular cores behind the rings.
 box(g,'miez anvelopa',x-half,y-r*.72,z-r*.52,x+half,y+r*.72,z+r*.52,'cauciuc')
 box(g,'miez anvelopa',x-half,y-r*.52,z-r*.72,x+half,y+r*.52,z+r*.72,'cauciuc')
 for side in (-1,1):
  outer=x+side*(half+.09);lo,hi=sorted((outer,outer+side*.32))
  box(g,'disc janta',lo,y-r*.48,z-r*.33,hi,y+r*.48,z+r*.33,'crem')
  box(g,'disc janta',lo,y-r*.33,z-r*.48,hi,y+r*.33,z+r*.48,'crem')
 for i in range(count):
  angle=i*step
  cube(g,'anvelopa segment',[x-half,y+r-2.7,z-r*math.tan(math.pi/count)],[x+half,y+r,z+r*math.tan(math.pi/count)],'cauciuc',[angle,0,0],[x,y,z])
  # Explicit per-cube ring positions and angles, not just a rotated parent:
  # importers that flatten groups still see the profile around the wheel.
  theta=math.radians(angle);radial=r-.65;cy=y+radial*math.cos(theta);cz=z+radial*math.sin(theta)
  for side in (-1,1):
   cx=x+side*width*.23;cube(g,'crampon V',[cx-.95,cy-.25,cz-1.15],[cx+.95,cy+.25,cz+1.15],'cauciuc_lumina',[angle,0,side*16],[cx,cy,cz])
  for side in (-1,1):
   outside=x+side*(half+.09);lo,hi=sorted((outside,outside+side*.35))
   cube(g,'janta segment',[lo,y+r*.53-.65,z-r*.53*math.tan(math.pi/count)],[hi,y+r*.53+.3,z+r*.53*math.tan(math.pi/count)],'crem',[angle,0,0],[x,y,z])
 for side in (-1,1):
  outer=x+side*(half+.3);lo,hi=sorted((outer,outer+side*.65))
  box(g,'butuc rosu',lo,y-1.35,z-1.35,hi,y+1.35,z+1.35,'rosu')
  for dy,dz in ((2,0),(-2,0),(0,2),(0,-2)):box(g,'prezon',lo,y+dy-.2,z+dz-.2,hi,y+dy+.2,z+dz+.2,'metal')
 return g
def beam_xyz(g,n,p1,p2,thickness,c):
 # One short rotated cuboid joining consecutive points on the helix.
 dx,dy,dz=(p2[i]-p1[i] for i in range(3));length=math.sqrt(dx*dx+dy*dy+dz*dz)
 cx,cy,cz=((p1[i]+p2[i])/2 for i in range(3))
 yaw=math.degrees(math.atan2(-dz,math.hypot(dx,dy)));roll=math.degrees(math.atan2(dy,dx))
 cube(g,n,[cx-length/2,cy-thickness/2,cz-thickness/2],[cx+length/2,cy+thickness/2,cz+thickness/2],c,[0,yaw,roll],[cx,cy,cz])

# 8.20 m = 131.2 units, with the specified header/reel/auger pivots.
# Contradictory source Z range -52..32 is only 84 units; the sculpted
# body extends rearward and the crop dividers forward instead.
body=group('body',[0,0,0]);seat=group('seat_driver',[0,26,-18],body)
box(body,'cadru central',-13,11,-20,13,16,45,'sasiu')
box(body,'caroserie inferioara',-13,16,-20,13,29,44,'verde_inchis')
# White side shells with sloping shoulders and bright green bands.
for side in (-1,1):
 x=side*13
 box(body,'panou lateral alb',min(x,x+side*.9),25,-18,max(x,x+side*.9),38,43,'crem')
 box(body,'dunga verde',min(x+side*.9,x+side*1.25),29,-18,max(x+side*.9,x+side*1.25),33,43,'verde')
 beam_yz(body,'umăr aerodinamic',x+side*.4,1.4,38,-15,43,35,3.2,'crem')
 beam_yz(body,'profil capota verde',x+side*.8,1.1,38,32,29,44,2.6,'verde')
 box(body,'grila racire neagra',min(x+side*1.3,x+side*1.55),33,22,max(x+side*1.3,x+side*1.55),40,44,'negru')
 for y in (33.5,34.7,35.9,37.1,38.3,39.5):box(body,'lamela racire',min(x+side*1.56,x+side*1.72),y,22.5,max(x+side*1.56,x+side*1.72),y+.25,43.5,'otel')
 for z in (-2,10):box(body,'capac intretinere',min(x+side*1.3,x+side*1.5),20,z,max(x+side*1.3,x+side*1.5),24,z+7,'sasiu')
 # Exposed transmission under the side panel, small recessed pulleys.
 for y,z,r in ((19,-6,2.4),(20,2,3),(19,12,2.2)):
  lo,hi=sorted((x+side*1.6,x+side*2.5))
  for j in range(12):cube(body,'fulie transmisie',[lo,y+r-.5,z-.65],[hi,y+r,z+.65],'negru',[j*30,0,0],[x,y,z])
 beam_yz(body,'curea transmisie',x+side*2.6,.35,22, -6,22,12,.45,'negru')
# Sculpted rear cap with raised central engine cover, offset from the rear axle.
box(body,'capota motor',-10.5,30,17,10.5,44,36,'crem')
beam_yz(body,'capac spate inclinat',0,23,42,35,28,44,1.2,'crem')
# Rear axle: central oscillating pivot, rigid beam, steering knuckles and
# tie rods. Each rear wheel remains a separate child pivot for steering.
rear_axle=group('rear_steering_axle',[0,8.4,25],body)
box(rear_axle,'corp punte spate',-13,7,23.9,13,9.8,26.1,'sasiu')
box(rear_axle,'suport pivot central',-2.2,8.5,23.3,2.2,12,26.7,'metal')
box(rear_axle,'bolt central balans',-1.2,7.4,23,1.2,9.6,27,'negru')
box(rear_axle,'bara directie transversala',-11.5,6.3,21.8,11.5,6.85,22.4,'metal')
box(rear_axle,'cilindru directie',-3.5,6.65,21.4,2.5,7.65,22.8,'negru')
box(rear_axle,'tija cilindru directie',2.4,6.9,21.7,7.5,7.4,22.3,'metal')
for side in (-1,1):
 x=side*12.6
 box(rear_axle,'fuzeta port roata',x-.85,5.7,24.1,x+.85,11.8,25.9,'otel')
 box(rear_axle,'pivot vertical directie',x-.5,5.3,24.5,x+.5,12.2,25.5,'negru')
 box(rear_axle,'brat directie',x-.5,6.2,21.8,x+.5,7.2,24.6,'otel')
 box(rear_axle,'articulatie bara directie',x-.8,6.05,21.65,x+.8,7.35,22.55,'negru')
box(body,'protectie motor spate',-11,20,42,11,31,45,'sasiu')
# Rear straw chopper and two spreaders; decorative, not functional.
box(body,'tocator paie',-10,10,37,10,15.5,45,'sasiu')
for x in (-6,6):
 box(body,'disc tocator',x-3.6,9.5,39,x+3.6,10,45,'negru')
 for a in range(0,360,60):cube(body,'paleta tocator',[x-.25,9.3,38],[x+.25,10,45],'metal',[0,a,0],[x,9.6,42])
# Body reveals, service fasteners, reflective markers and rear lamps.
for side in (-1,1):
 x=side*14.0;lo,hi=sorted((x,x+side*.12))
 for z in (3,9,15,40):box(body,'separatie panou',lo,26,z,hi,38,z+.20,'otel')
 for z in (2,10):box(body,'maner capota',lo,24,z,hi,24.5,z+2,'negru')
 for z in (-8,41):box(body,'reflector lateral',lo,27,z,hi,28,z+1.5,'chihlimbar')
for x in (-9,7):
 box(body,'carcasa lampa spate',x,23,44.2,x+2.5,25.5,44.8,'negru')
 box(body,'lampa spate rosie',x+.25,23.3,44.8,x+2.25,25.2,44.95,'rosu')
# Curved/panoramic cab approximation: slender black frame + angled window panes.
box(body,'podea cabina',-10.5,28,-26,10.5,29,-10,'sasiu')
for side in (-1,1):
 x=side*9.4
 beam_yz(body,'stalp parbriz inclinat',x,.65,29,-27,49,-23,.65,'negru')
 box(body,'stalp spate cabina',x-.35,29,-10.5,x+.35,49,-9.8,'negru')
 box(body,'rama laterala inferioara',x-.35,30,-26,x+.35,30.6,-10,'negru')
 box(body,'rama laterala superioara',x-.35,47.8,-23,x+.35,48.5,-10,'negru')
box(body,'cadru parbriz jos',-9.5,29,-27,9.5,29.65,-26.4,'negru')
box(body,'cadru parbriz sus',-9.5,48.4,-23.2,9.5,49,-22.5,'negru')
beam_yz(body,'parbriz fumuriu',0,18.2,29.15,-26.95,48.85,-23.05,.22,'sticla')
for side in (-1,1):
 x=side*9.25
 box(body,'vitre laterale',x-.07,29.3,-23.1,x+.07,48.8,-10.5,'sticla')
box(body,'pavillon blanc',-11,49,-26,11,50.7,-9,'crem')
beam_yz(body,'bord avant toit',0,22,50.5,-26,48.8,-28,1,'crem')
for i in range(8):
 x=-8.75+i*2.5;box(body,'LED avant cadre',x,48.8,-28.15,x+1.7,49.7,-27.7,'negru');box(body,'LED avant lentille',x+.14,48.95,-28.25,x+1.56,49.55,-28.12,'far')
for x in (-9,8):
 box(body,'girofar soclu',x,50.7,-11.5,x+1.7,51.1,-9.8,'negru');box(body,'girofar portocaliu',x+.2,51.1,-11.3,x+1.5,53,-10,'chihlimbar')
box(body,'antena GPS',-.8,50.7,-16,.8,52.5,-14.4,'gps');box(body,'catarg GPS',-.15,52.5,-15.35,.15,58.4,-15.05,'sasiu')
# Seat origin is a plugin marker, physical cushion is higher than marker.
box(seat,'scaun perna',-2.6,29,-19.5,2.6,30.5,-15,'negru');box(seat,'scaun spatar',-2.6,30.5,-15.5,2.6,38,-14.4,'negru')
box(body,'coloana volan',-.4,30,-23,.4,36,-22.2,'otel')
for j in range(8):cube(body,'volan segment',[1.5,35,-23],[1.9,35.4,-22.5],'negru',[0,j*45,0],[0,35.2,-22.75])
box(body,'consola joystick',4,30,-20,8,33,-14,'sasiu');box(body,'joystick',5.7,33,-18,6.2,36,-17.5,'negru');box(body,'display bord',-4,34,-25,4,37,-24.6,'negru');box(body,'display aprins',-3.6,34.3,-25.08,3.6,36.7,-25.01,'gps')
for side in (-1,1):
 x=side*9.8;out=side*14.5;box(body,'brat oglinda',min(x,out),41,-24,max(x,out),41.5,-23.5,'otel');box(body,'oglinda',min(out-side*1,out+side*1),38,-24.5,max(out-side*1,out+side*1),43,-23.5,'negru')
box(body,'platforma acces',-17.5,22,-25,-10,23,-11,'sasiu')
ladder=group('access_ladder',[-16,22,-18],body)
groups[-1]['rotation']=[-12,0,0]
for z in (-22,-14):box(ladder,'montant scara',-17,4,z,-16.4,22,z+.6,'otel')
for y in (5,8,11,14,17,20):box(ladder,'treapta scara',-17.2,y,-22,-16.2,y+.4,-13.4,'metal')
for z in (-24,-12):box(body,'balustrada acces',-17.4,23,z,-16.9,32,z+.5,'sasiu')
box(body,'mana curenta acces',-17.4,31.5,-24,-16.9,32,-11.5,'sasiu')
# Open flared hopper; grain is an independent visible surface.
box(body,'buncar podea',-8,33,-8,8,34,14,'sasiu')
# Matched short slices follow the same taper on all four walls. Their
# edges overlap slightly to avoid cracks; no end wall extends past the sides.
for i in range(11):
 y1=34+2*i;y2=y1+2.08;t0=i/11;t1=(i+1)/11;tm=(t0+t1)/2
 xmid=8+5*tm;front=-6-2*tm;back=12+2*tm
 for side in (-1,1):
  x=side*xmid
  box(body,'oblon buncar',x-.55,y1,front-.55,x+.55,y2,back+.55,'crem')
 for label,z in [('avant',front),('arriere',back)]:
  box(body,'buncar paroi '+label,-xmid-.12,y1,z-.55,xmid+.12,y2,z+.55,'crem')
for side in (-1,1):
 box(body,'bord verde buncar',min(side*12.5,side*13.5),55.5,-8,max(side*12.5,side*13.5),56.4,14,'verde')
box(body,'suprafata grau',-11.3,50,-7,11.3,50.4,13,'grau')
for x in (-9,-5,-1,3,7):
 for z in (-5,0,5,10):box(body,'grau detalii',x,50.4,z,x+1.1,50.65,z+1,'grau_lumina')
box(body,'snec umplere buncar',-.65,51,-6,.65,52.4,12,'metal')
# Exhaust and rear access ladder.
box(body,'protectie esapament',8,44,29,10.2,51,31.2,'metal');box(body,'esapament',8.45,51,29.45,9.75,56,30.75,'negru')
for x in (-8,8):box(body,'montant scara spate',x,10,45,x+.5,36,46,'otel')
for y in (11,15,19,23,27,31,35):box(body,'treapta spate',-8,y,45,8.5,y+.4,46,'metal')
# Exact wheel diameters, 14-section front wheels; rear axle moved back to
# preserve convincing proportions within the corrected total length.
wheel('wheel_fl',-18,14,-12,14,8,14);wheel('wheel_fr',18,14,-12,14,8,14)
wheel('wheel_rl',-14,8.4,25,8.4,4.8,10,rear_axle);wheel('wheel_rr',14,8.4,25,8.4,4.8,10,rear_axle)
auger=group('unloading_auger',[-13,44,0]);box(auger,'cot baza',-14.6,42.4,-1.6,-11.4,45.6,1.6,'verde');box(auger,'tub descarcare',-14.6,42.4,0,-11.4,45.6,44,'crem');box(auger,'manson flexibil',-14.8,42.2,34,-11.2,45.8,36,'negru');box(auger,'lampa descarcare',-14.8,41.2,31,-11.2,42.4,33,'far')
# Fixed feeder hinge supports on the machine remain anchored to the body.
for side in (-1,1):
 x=side*7.6
 box(body,'placa prindere heder',x-.8,18.2,-21.2,x+.8,23.8,-18.8,'sasiu')
 box(body,'bolt pivot heder',x-1.05,20.1,-20.9,x+1.05,21.9,-19.1,'metal')
# Whole feeder and header rotate around the same hinge; the rear wall sits
# across the feeder mouth, not floating in front of it.
header=group('header_assembly',[0,21,-20]);beam_yz(header,'feeder neted',0,15,8,-40,21,-20,5,'sasiu')
for x in (-7.6,7.6):
 beam_yz(header,'bara feeder',x,.65,8,-40,21,-20,.7,'metal')
 beam_yz(header,'cilindru hidraulic corp',x,1.8,7,-37,11,-30,1.8,'negru')
 beam_yz(header,'cilindru hidraulic tija',x,.7,11,-30,17,-23,.7,'metal')
if not CORN:
 # Cutter and reel are on the FRONT (-Z), auger behind them toward +Z.
 # A continuous, deeper trough links the cutting bar to the feeder mouth.
 box(header,'jgheab fund',-38.4,1.2,-64,38.4,2.2,-39,'sasiu')
 box(header,'jgheab perete',-38.4,2.2,-40,38.4,11,-39,'rosu')
 box(header,'rama cuplare heder inferioara',-8,5.5,-40.4,8,7,-38.6,'otel')
 for x in (-8,7):box(header,'rama cuplare laterala',x,7,-40.4,x+1,12,-38.6,'sasiu')
 box(header,'rama cuplare heder superioara',-8,11,-40.4,8,12,-38.6,'otel')
 for side in (-1,1):
  x=side*36.8;box(header,'capac lateral heder',x-1.6,2,-64,x+1.6,10,-39,'rosu')
  for k in range(8):
   z1=-70+6*k/8;z2=-70+6*(k+1)/8;w=.16+1.44*(k+1)/8
   box(header,'despartitor conic',x-w,1.2,z1,x+w,1.8+1.5*(k+1)/8,z2,'rosu')
  beam_yz(header,'protectie cromata',x,.4,1.75,-69,3,-64,.4,'metal')
  # Pivot bracket and two fixed support/hydraulic arms terminate at the axle.
  beam_yz(header,'brat rabator',x-side*1.8,1.25,9,-40,11,-57.5,1.2,'rosu')
  beam_yz(header,'cilindru rabator corp',x-side*1.8,1.0,5.5,-41,8.0,-50,1.0,'negru')
  beam_yz(header,'cilindru rabator tija',x-side*1.8,.55,8,-50,11,-57.5,.55,'metal')
  box(header,'lagar rabator',x-side*1.8-.8,10.2,-58.3,x-side*1.8+.8,11.8,-56.7,'negru')
 cutter=group('cutter_bar',[0,1.2,-64],header);box(cutter,'bara taiere',-37.5,0,-64.5,37.5,.8,-63.6,'metal')
 for i in range(38):
  x=-37+i*2;box(cutter,'dinte taiere',x,0,-65.7,x+1.1,.5,-64,'crem')
 # Polygonal auger drum plus continuous helical flighting from both ends.
 # Left and right spirals have opposite handedness to lead toward the centre.
 intake=group('intake_auger',[0,6.5,-47.5],header)
 box(intake,'tambur snec miez',-36.9,5.2,-49.0,36.9,7.8,-46.0,'metal')
 box(intake,'tambur snec miez',-36.9,4.9,-48.65,36.9,8.1,-46.35,'metal')
 for j in range(12):
  angle=j*30;cube(intake,'tambur octogonal',[-36.9,8.0,-47.95],[36.9,8.35,-47.05],'metal',[angle,0,0],[0,6.5,-47.5])
 for side in (-1,1):
  for i in range(68):
   u1=i/68;u2=(i+1)/68
   def helix(u):
    x=side*(35.8-u*32.8);angle=side*u*math.pi*8
    return [x,6.5+2.25*math.cos(angle),-47.5+2.25*math.sin(angle)]
   beam_xyz(intake,'spirala continua snec',helix(u1),helix(u2),.42,'otel')
 for x in (-4.5,-2.5,-.5,1.5,3.5):
  box(intake,'deget alimentare snec',x,8.1,-47.8,x+.45,10,-47.2,'negru')
 for x in (-37,36.5):box(intake,'flansa snec',x,4.4,-49.6,x+.5,8.6,-45.4,'sasiu')
 # Lower and advance the reel to just behind the cutter, in front of the auger.
 reel=group('reel',[0,11,-57.5],header);box(reel,'ax rabator',-37,10.6,-57.9,37,11.4,-57.1,'otel')
 for j in range(6):
  angle=j*60
  for x in (-34,-11,11,34):cube(reel,'stea rabator',[x-.35,11,-57.85],[x+.35,20.3,-57.15],'metal',[angle,0,0],[x,11,-57.5])
  cube(reel,'bara rabator',[-37,19.9,-57.8],[37,20.5,-57.2],'sasiu',[angle,0,0],[0,11,-57.5])
  for x in range(-36,37,3):
   cube(reel,'gheara rabator',[x-.12,18.0,-57.65],[x+.12,20.1,-57.35],'metal',[angle,0,0],[0,11,-57.5])
   cube(reel,'varf gheara',[x-.14,17.7,-57.95],[x+.14,18.15,-57.35],'metal',[angle,0,0],[0,11,-57.5])
else:
 # Independent corn header at the same feeder hinge; no crop logic implied.
 # Eight crop lanes and nine tapered dividers, following the supplied GLB.
 box(header,'cadru heder porumb',-38.4,2,-48,38.4,5,-39,'sasiu')
 box(header,'spate heder porumb',-38.4,5,-41,38.4,11,-39,'rosu')
 box(header,'cuplaj heder porumb jos',-8,5.5,-40.4,8,7,-38.6,'otel')
 for x in (-8,7):box(header,'cuplaj heder porumb lateral',x,7,-40.4,x+1,12,-38.6,'sasiu')
 box(header,'cuplaj heder porumb sus',-8,11,-40.4,8,12,-38.6,'otel')
 for side in (-1,1):
  x=side*37.2
  box(header,'carcasa laterala porumb',x-1.2,2,-57,x+1.2,10,-39,'rosu')
 # Each snout narrows toward the front. The stepped silhouette is editable
 # with Blockbench cubes and is an approximation, not the source GLB mesh.
 for lane in range(9):
  x=-35.2+lane*8.8
  for i in range(12):
   t=(i+.5)/12;z1=-70+i*2;z2=z1+2.04
   width=.18+3.35*t;height=.55+3.8*t
   box(header,'separator porumb',x-width,1.0,z1,x+width,1.0+height,z2,'rosu')
  beam_yz(header,'muchie separator',x,.18,1.55,-69.6,5.05,-46,.18,'rosu_lumina')
 for lane in range(8):
  x=-30.8+lane*8.8
  box(header,'canal alimentare porumb',x-1.8,3.1,-56,x+1.8,3.65,-42,'negru')
  for side in (-1,1):
   for j in range(6):
    z=-55+j*2.1
    box(header,'lant alimentare porumb',x+side*1.25-.3,3.65,z,x+side*1.25+.3,4.05,z+1.05,'metal')
 # Empty placeholders maintain the common rig names while avoiding a cereal reel.
 group('cutter_bar',[0,1.2,-64],header)
 group('intake_auger',[0,6.5,-47.5],header)
 group('reel',[0,11,-57.5],header)
project={'meta':{'format_version':'5.0','model_format':'free','box_uv':False},'name':'Horizon Combina Moderna Porumb' if CORN else 'Horizon Combina Moderna 1-1','model_identifier':'horizon_combina_moderna_porumb' if CORN else 'horizon_combina_moderna','visible_box':[8,8,0],'resolution':{'width':16,'height':16},'elements':elements,'groups':groups,'outliner':roots,'textures':textures}
OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(project,separators=(',',':'))+'\n');print('Wrote',OUT,'elements',len(elements),'groups',len(groups))
