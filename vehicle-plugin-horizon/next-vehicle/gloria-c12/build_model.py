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
 # transmission discs, each an angular ring of raised bars
 for y,z,r in [(19,Z(2),3.1),(22,Z(11),4.0),(18,Z(20),2.3)]:
  for j in range(12):
   a=j*30;cube(body,'fulie segment', [x+min(0,side*.35),y+r-.45,z-.83],[x+max(0,side*.35),y+r+.35,z+.83], 'sasiu',[a,0,0],[x,y,z])
 # protective belt run
 box(body,'curea de transmisie',min(x+side*.5,x+side*.8),20.4,Z(2),max(x+side*.5,x+side*.8),21.25,Z(20),'negru')
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
# open grain bin, hollow interior and grain surface
box(body,'buncar podea',-12,29.5,Z(-6),12,30.5,Z(12),'rosu_inchis')
for x in (-12,11):box(body,'buncar perete lateral',x,30,Z(-6),x+1,48,Z(12),'rosu')
for z in (Z(-6),Z(12)-1):box(body,'buncar perete capat',-12,30,z,12,48,z+1,'rosu')
box(body,'grau in buncar',-10.9,43.4,Z(-6)+1.1,10.9,43.8,Z(12)-1.1,'grau')
for x in (-8,-3,2,7):
 for z in (-3,1,5,9):box(body,'granule grau',x,43.8,Z(z),x+1.3,44.05,Z(z)+1.4,'grau_lumina')
# rear engine enclosure and slatted intake
box(body,'compartiment motor',-12,25,Z(12),12,44,Z(28),'rosu')
for x in (-12.35,12):
 box(body,'rama grila motor',x,31,Z(17),x+.35,41,Z(26),'negru')
 for z in (17.5,19,20.5,22,23.5,25):box(body,'fanta ventilatie',x-.03,31.5,Z(z),x+.4,40.5,Z(z)+.6,'otel')
box(body,'esapament',8,44,Z(23),9.8,50,Z(23)+1.8,'negru');box(body,'capac esapament',7.8,50,Z(23)-.2,10,50.5,Z(23)+2,'sasiu')
for x in (-9,9):box(body,'bara scara spate',x,9,Z(28),x+.55,35,48,'otel')
for y in (10,14,18,22,26,30,34):box(body,'treapta scara spate',-9,y,46.7,9.55,y+.4,48,'metal')
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
# Inclined feeder as layered stepped plates, no multi-axis export claim.
for i in range(8):
 t=i/8; z=Z(-18)+t*(Z(-32)-Z(-18));yn=20+t*(7-20)
 box(header,'transportor treapta',-7,yn-2,z-3,7,yn+2,z+.1,'rosu_inchis')
for x in (-6,5):box(header,'cilindru hidraulic',x,8,Z(-29),x+1,15,Z(-22),'metal')
# trough rear wall, solid floor and end dividers
box(header,'podea heder',-33.6,1.5,Z(-42),33.6,2.4,Z(-32),'rosu_inchis')
box(header,'perete spate heder',-33.6,2.4,Z(-32)-1,33.6,12,Z(-32),'rosu')
for side in (-1,1):
 x=side*32;box(header,'cap lateral',x-1.4,2,Z(-42),x+1.4,10,Z(-32),'rosu')
 box(header,'despartitor lan',x-1.6,1.5,Z(-46),x+1.6,3,Z(-42),'rosu_lumina')
box(header,'bara taiere',-33,1,Z(-42)-.45,33,1.8,Z(-42)+.5,'metal')
for i in range(33):
 x=-32+i*2;box(header,'dinte taiere',x,1,Z(-42)-1.6,x+1.1,1.55,Z(-42),'crem')
box(header,'ax snec',-32,4.4,Z(-35)-1.4,32,6.6,Z(-35)+1.4,'otel')
for i in range(45):
 x=-31+i*1.4;a=i*33;cube(header,'spirala snec',[x,6.6,Z(-35)-.35],[x+.7,7.15,Z(-35)+.35],'metal',[a,0,0],[x,5.5,Z(-35)])
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
