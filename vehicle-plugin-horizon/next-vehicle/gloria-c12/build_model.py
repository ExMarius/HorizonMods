#!/usr/bin/env python3
"""Author an editable Gloria-inspired 1:1 Blockbench model, no plugin changes."""
import base64, json, math, struct, uuid, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'downloads'/'horizon-gloria-c12.bbmodel'
uid=lambda: str(uuid.uuid4())
palette={'rosu':'c83228','rosu_inchis':'85221b','rosu_lumina':'e54b32','crem':'f0ece1','sasiu':'262626','cauciuc':'1e1e1e','cauciuc_lumina':'30302e','metal':'a9aaa4','otel':'6e7373','negru':'121516','chihlimbar':'ffa52a','sticla':'8bb5b5','grau':'cfae59','grau_lumina':'e2c675','far':'fff1bf','bord':'3c3e3b'}
def png(rgb):
 raw=b'\0'+bytes.fromhex(rgb)+b'\xff'
 def chunk(tag,data):return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')
textures=[]
for i,(name,color) in enumerate(palette.items()):
 textures.append({'name':f'{name}_{color}.png','id':str(i),'uuid':uid(),'width':1,'height':1,'uv_width':16,'uv_height':16,'particle':False,'render_mode':'default','mode':'bitmap','saved':False,'source':'data:image/png;base64,'+base64.b64encode(png(color)).decode()})
tex={n:i for i,n in enumerate(palette)}
elements=[];groups=[];roots=[]
def group(name,origin,parent=None):
 id=uid();groups.append({'name':name,'uuid':id,'export':True,'locked':False,'origin':origin,'rotation':[0,0,0],'color':0,'visibility':True,'isOpen':True})
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
# Longitudinal coordinates: user's original Z scaled by 1.6; 121.6/16=7.60m.
def Z(z):return z*1.6
body=group('body',[0,0,0]);seat=group('seat_driver',[-3,26,Z(-15)],body)
# chassis, flanks and upper side panels; cab volume remains open above the deck
box(body,'cadru inferior',-13,10,Z(-18),13,14,Z(28),'sasiu')
box(body,'corp masina',-13,14,Z(-18),13,28,Z(28),'rosu')
box(body,'platforma podea cabina',-12.6,27.8,Z(-22),9.5,29,Z(-8),'sasiu')
for side in (-1,1):
 x=side*13
 for y in (16,19,22,25):box(body,'nervura laterala',min(x,x+side*.38),y,Z(-3),max(x,x+side*.38),y+.45,Z(27),'rosu_inchis')
 for z in (1,9,17):
  box(body,'capac vizitare',min(x,x+side*.32),20,Z(z),max(x,x+side*.32),25,Z(z+5),'rosu_inchis')
  box(body,'capac interior',min(x+side*.32,x+side*.44),20.5,Z(z+.3),max(x+side*.32,x+side*.44),24.5,Z(z+4.7),'rosu')
 # Cream contrast strip interrupted only by raised mechanical covers.
 box(body,'banda crem laterala',min(x+side*.48,x+side*.58),26,Z(-18),max(x+side*.48,x+side*.58),28,Z(28),'crem')
 # Five thick raised pulleys per side, with metal faces and dark hubs.
 pulley=[(19,Z(-2),2.7),(21,Z(4),3.6),(19.3,Z(10),2.25),(22.0,Z(16),3.0),(19,Z(23),2.4)]
 px=x+side*1.0;lo,hi=sorted((x+side*.35,x+side*1.85))
 for y,z,r in pulley:
  box(body,'disc fulie',lo,y-r*.65,z-r*.46,hi,y+r*.65,z+r*.46,'otel')
  box(body,'disc fulie',lo,y-r*.46,z-r*.65,hi,y+r*.46,z+r*.65,'otel')
  for j in range(12):
   angle=j*30;cube(body,'coroana fulie',[lo,y+r-.5,z-r*math.tan(math.pi/12)],[hi,y+r-.05,z+r*math.tan(math.pi/12)],'metal',[angle,0,0],[px,y,z])
  box(body,'butuc fulie',lo,y-.65,z-.65,hi,y+.65,z+.65,'negru')
 # Connecting upper and lower belt runs, physically separate from body panels.
 belt_x=x+side*1.96
 for (y1,z1,r1),(y2,z2,r2) in zip(pulley,pulley[1:]):
  beam_yz(body,'curea sus',belt_x,.45,y1+r1,z1,y2+r2,z2,.38,'negru')
  beam_yz(body,'curea jos',belt_x,.45,y1-r1,z1,y2-r2,z2,.38,'negru')
 # Partial safety guard: a rail and two short anchored ends, not a solid cover.
 gx=x+side*2.25
 beam_yz(body,'aparatoare curea',gx,.3,26,Z(-3),27,Z(24),.45,'otel')
 for z in (Z(-3),Z(24)):box(body,'suport aparatoare',min(x,gx),23,z-.3,max(x,gx),26,z+.3,'otel')
# cab, structural frame only: actual openings (not opaque window blocks)
for x in (-10,8.6):
 for z in (Z(-22),Z(-8)-.8):box(body,'stalp cabina',x,29,z,x+1,46,z+.8,'negru')
 for y in (29,36.2,45.5):box(body,'rama laterala cabina',x,y,Z(-22),x+1,y+.7,Z(-8),'negru')
for y in (29,45.3):box(body,'rama parbriz',-10,y,Z(-22),9.6,y+.8,Z(-22)+.8,'negru')
box(body,'rama centrala parbriz',-.7,30,Z(-22),.1,45.3,Z(-22)+.75,'negru')
box(body,'acoperis cabina',-11,46,Z(-22)-1,10.5,47.5,Z(-8)+1,'crem')
box(body,'margine plafon',-11,45.7,Z(-22)-1,10.5,46,Z(-8)+1,'sasiu')
for x in (-7,5):
 box(body,'proiector carcasa',x,44.7,Z(-22)-1.4,x+3,46,Z(-22)-.6,'negru')
 box(body,'proiector lentila',x+.2,44.9,Z(-22)-1.55,x+2.8,45.8,Z(-22)-1.35,'far')
box(body,'girofar soclu',7,47.5,Z(-10),9,48,Z(-10)+2,'sasiu');box(body,'girofar portocaliu',7.15,48,Z(-10)+.15,8.85,52,Z(-10)+1.85,'chihlimbar')
# Driver seat pivot at declared location. Cushion and back visible above floor.
box(seat,'perna scaun',-5.7,29,Z(-15)-2,-.3,30.5,Z(-15)+2,'negru')
box(seat,'spatar scaun',-5.7,30.5,Z(-15)+1.5,-.3,36,Z(-15)+2.4,'negru')
box(body,'panou bord',-6.5,33,Z(-21),2,35.2,Z(-19),'bord')
box(body,'coloana volan',-3.4,30.5,Z(-19),-2.6,35.4,Z(-19)+.8,'otel')
for j in range(8):
 a=j*45;cube(body,'volan inel',[-3.2+1.7,35,Z(-19)-.2],[-3.2+2.1,35.45,Z(-19)+.2],'negru',[0,a,0],[-3.2,35.2,Z(-19)])
box(body,'maneta',2.8,30,Z(-15),3.1,34,Z(-15)+.3,'otel');box(body,'maneta cap',2.5,34,Z(-15)-.2,3.4,34.9,Z(-15)+.6,'negru')
# left boarding platform and ladder
box(body,'platforma acces',-17.4,23,Z(-19),-12.9,24,Z(-11),'sasiu')
for z in (Z(-19),Z(-12)):box(body,'montant scara',-17.1,6,z,-16.45,24,z+.65,'otel')
for y in (7,10.5,14,17.5,21):box(body,'treapta',-17.3,y,Z(-19),-16.2,y+.45,Z(-11.5),'metal')
# Large mirrors on long metal arms, black windscreen wiper and access rails.
for side in (-1,1):
 x=side*10; outer=side*15.5
 box(body,'brat oglinda',min(x,outer),40,Z(-22)+.3,max(x,outer),40.55,Z(-22)+.8,'otel')
 box(body,'oglinda cadru',min(outer-side*1.0,outer+side*1.0),38,Z(-22)-.35,max(outer-side*1.0,outer+side*1.0),43,Z(-22)+.35,'negru')
 box(body,'oglinda sticla',min(outer-side*.75,outer+side*.75),38.3,Z(-22)-.42,max(outer-side*.75,outer+side*.75),42.7,Z(-22)-.34,'metal')
beam_xy(body,'stergator',-6,31,4.5,38,Z(-22)-.17,Z(-22)+.15,.38,'negru')
for z in (Z(-19),Z(-11.5)):
 box(body,'montant balustrada acces',-17.2,24,z,-16.7,32,z+.5,'otel')
box(body,'mana curenta acces',-17.2,31.5,Z(-19),-16.7,32,Z(-11),'metal')
# Open-top cream grain hopper: slanted panels flare out from base to lip.
box(body,'buncar podea',-8.5,29.5,Z(-6)+2,8.5,30.5,Z(12)-2,'rosu_inchis')
for side in (-1,1):
 beam_xy(body,'buncar perete evazat',side*8.5,30,side*12,48,Z(-6),Z(12),.9,'crem')
 box(body,'bordura rosie buncar',min(side*11.5,side*12.5),47.5,Z(-6),max(side*11.5,side*12.5),48.3,Z(12),'rosu')
# End panels tilt outward too, leaving an unobstructed top and gold surface.
beam_yz(body,'buncar fata',0,24,30,Z(-6)+2,48,Z(-6),.85,'crem')
beam_yz(body,'buncar spate',0,24,30,Z(12)-2,48,Z(12),.85,'crem')
for z in (Z(-6)-.2,Z(12)-.5):box(body,'bordura rosie capat',-12.5,47.5,z,12.5,48.3,z+.7,'rosu')
box(body,'grau in buncar',-10.8,43.4,Z(-6)+1.4,10.8,43.8,Z(12)-1.4,'grau')
for x in (-8,-3,2,7):
 for z in (-3,1,5,9):box(body,'granule grau',x,43.8,Z(z),x+1.3,44.05,Z(z)+1.4,'grau_lumina')
# Engine and rear separators: horizontal lower body with a pitched rear hood.
box(body,'motor baza',-12,25,Z(12),12,35,Z(25),'rosu')
box(body,'capac motor central ridicat',-9,35,Z(12),9,43,Z(22),'rosu')
beam_yz(body,'capota spate inclinata',0,24,40,Z(22),28,Z(28),1.2,'rosu')
for side in (-1,1):
 x=side*12
 box(body,'rama grila motor',min(x,x+side*.35),29,Z(14),max(x,x+side*.35),35,Z(22),'negru')
 for z in (14.5,16,17.5,19,20.5):box(body,'lamela radiator',min(x+side*.36,x+side*.5),29.5,Z(z),max(x+side*.36,x+side*.5),34.5,Z(z)+.55,'otel')
box(body,'esapament vertical',8,43,Z(18),9.8,49,Z(18)+1.8,'negru')
box(body,'cot esapament',8,49,Z(18)-1.2,9.8,50.5,Z(18)+1.8,'sasiu')
for x in (-9,9):box(body,'bara scara spate',x,9,Z(28),x+.55,39,48,'otel')
for y in (10,14,18,22,26,30,34,38):box(body,'treapta scara spate',-9,y,46.7,9.55,y+.4,48,'metal')
for x in (-9,9):box(body,'balustrada spate',x,39,46.5,x+.55,46,47.1,'metal')
box(body,'mana curenta spate',-9,45.5,46.5,9.55,46.05,47.1,'metal')
box(body,'punte spate',-14,6,Z(21)-1.2,14,8,Z(21)+1.2,'sasiu')
# wheels: polygon tread rings and smaller segmented cream rims; wheel group pivot is axle.
def wheel(name,x,y,z,r,width,count):
 g=group(name,[x,y,z]);half=width/2;step=360/count
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
  tread=group('crampoane_'+str(i),[x,y,z],g)
  groups[-1]['rotation']=[angle,0,0]
  for side in (-1,1):
   a=x+side*width*.23;cube(tread,'crampon V',[a-.95,y+r-.9,z-1.15],[a+.95,y+r-.4,z+1.15],'cauciuc_lumina',[0,0,side*16],[a,y+r-.65,z])
  for side in (-1,1):
   outside=x+side*(half+.09);lo,hi=sorted((outside,outside+side*.35))
   cube(g,'janta segment',[lo,y+r*.53-.65,z-r*.53*math.tan(math.pi/count)],[hi,y+r*.53+.3,z+r*.53*math.tan(math.pi/count)],'crem',[angle,0,0],[x,y,z])
 for side in (-1,1):
  outer=x+side*(half+.3);lo,hi=sorted((outer,outer+side*.65))
  box(g,'butuc rosu',lo,y-1.35,z-1.35,hi,y+1.35,z+1.35,'rosu')
  for dy,dz in ((2,0),(-2,0),(0,2),(0,-2)):box(g,'prezon',lo,y+dy-.2,z+dz-.2,hi,y+dy+.2,z+dz+.2,'metal')
 return g
wheel('wheel_fl',-17,12.4,Z(-10),12.4,6.5,12);wheel('wheel_fr',17,12.4,Z(-10),12.4,6.5,12)
wheel('wheel_rl',-13,6.8,Z(21),6.8,3.8,10);wheel('wheel_rr',13,6.8,Z(21),6.8,3.8,10)
# swivel auger pivot; folded rearwards along +Z
auger=group('unloading_auger',[-12,38,Z(2)])
box(auger,'cot baza',-13.6,36.4,Z(2)-1.6,-10.4,39.6,Z(2)+1.6,'rosu')
box(auger,'tub descarcare',-13.6,36.4,Z(2),-10.4,39.6,Z(2)+38,'crem')
box(auger,'manson de capat',-13.7,36.3,Z(2)+36,-10.3,39.7,Z(2)+38,'negru')
# header: exact adjusted hinge; reel nested under header with its own axis
header=group('header_assembly',[0,20,Z(-18)])
# Continuous, solid feeder housing from hinge to header: no stepped slices.
beam_yz(header,'gat transportor neted',0,14,7,Z(-32),20,Z(-18),5,'rosu_inchis')
for x in (-7.3,7.3):
 beam_yz(header,'sina laterala transportor',x,.6,7,Z(-32),20,Z(-18),.65,'metal')
 # Thick black barrel and a silver piston rod, both inside the articulated header.
 beam_yz(header,'cilindru hidraulic corp',x,1.6,6.0,Z(-30),10.5,Z(-25),1.6,'negru')
 beam_yz(header,'cilindru hidraulic tija',x,.72,10.2,Z(-25.3),16,Z(-20),.72,'metal')
 for y,z in [(6,Z(-30)),(16,Z(-20))]:box(header,'articulatie cilindru',x-.9,y-.9,z-.8,x+.9,y+.9,z+.8,'otel')
# trough rear wall, solid floor and end dividers
box(header,'podea heder',-33.6,1.5,Z(-42),33.6,2.4,Z(-32),'rosu_inchis')
box(header,'perete spate heder',-33.6,2.4,Z(-32)-1,33.6,12,Z(-32),'rosu')
for side in (-1,1):
 x=side*32;box(header,'cap lateral',x-1.4,2,Z(-42),x+1.4,10,Z(-32),'crem')
 # Six progressively narrower sections approximate a tapered crop divider.
 for k in range(6):
  z1=Z(-46)+(Z(-42)-Z(-46))*k/6;z2=Z(-46)+(Z(-42)-Z(-46))*(k+1)/6
  w=.25+1.35*(k+1)/6;box(header,'torpila conica',x-w,1.5,z1,x+w,2.4+1.1*(k+1)/6,z2,'crem')
box(header,'bara taiere',-33,1,Z(-42)-.45,33,1.8,Z(-42)+.5,'metal')
for i in range(33):
 x=-32+i*2;box(header,'dinte taiere',x,1,Z(-42)-1.6,x+1.1,1.55,Z(-42),'crem')
box(header,'snec miez',-32,3.8,Z(-35)-1.8,32,7.2,Z(-35)+1.8,'metal')
for i in range(45):
 x=-31+i*1.4;a=i*33;cube(header,'spirala snec',[x,6.6,Z(-35)-.35],[x+.7,7.15,Z(-35)+.35],'metal',[a,0,0],[x,5.5,Z(-35)])
# Fixed side arms belong to the header, not to the rotating reel.
for x in (-30,30):
 beam_yz(header,'brat rabator rosu',x,1.2,9,Z(-32),12,Z(-39),1.2,'rosu')
 beam_yz(header,'sprijin rabator metalic',x,.65,5.5,Z(-32),12,Z(-39),.65,'metal')
 box(header,'lagar ax rabator',x-.9,11.1,Z(-39)-.9,x+.9,12.9,Z(-39)+.9,'sasiu')
reel=group('reel',[0,12,Z(-39)],header)
box(reel,'ax rabator',-32.5,11.6,Z(-39)-.4,32.5,12.4,Z(-39)+.4,'sasiu')
for j in range(6):
 a=j*60
 for x in (-30,0,30):cube(reel,'brat stea',[x-.35,12,Z(-39)-.35],[x+.35,18,Z(-39)+.35],'metal',[a,0,0],[x,12,Z(-39)])
 cube(reel,'bara rabator',[-32.5,17.6,Z(-39)-.3],[32.5,18.2,Z(-39)+.3],'sasiu',[a,0,0],[0,12,Z(-39)])
 for x in range(-30,31,3):cube(reel,'deget rabator',[x-.12,15.6,Z(-39)-.12],[x+.12,17.8,Z(-39)+.12],'metal',[a,0,0],[0,12,Z(-39)])
project={'meta':{'format_version':'5.0','model_format':'free','box_uv':False},'name':'Horizon Gloria C12 1-1','model_identifier':'horizon_gloria_c12','visible_box':[8,8,0],'resolution':{'width':16,'height':16},'elements':elements,'groups':groups,'outliner':roots,'textures':textures}
OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(project,separators=(',',':'))+'\n')
print('Wrote',OUT,'elements',len(elements),'groups',len(groups))
