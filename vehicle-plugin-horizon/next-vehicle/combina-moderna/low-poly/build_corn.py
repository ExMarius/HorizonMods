#!/usr/bin/env python3
"""Build an editable, articulated low-poly combine inspired by the supplied GLB.
Blockbench free format. Not a vanilla resource pack or plugin implementation.
"""
import base64,json,math,struct,uuid,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'downloads/horizon-combina-glb-porumb-lowpoly.bbmodel'
uid=lambda:str(uuid.uuid4())
COLORS={'rosu':'8b1e1e','rosu_umbra':'601414','rosu_lumina':'a52b25','negru':'1e2024','negru_adanc':'111315','gri':'8b9091','otel':'595e60','far':'ffdb78','sticla':'708b8c','janta':'999b97','sol':'383b3c'}
def png(color,alpha):
 def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b'\x00'+bytes.fromhex(color)+bytes([alpha])))+chunk(b'IEND',b'')
textures=[]
for i,(n,c) in enumerate(COLORS.items()):textures.append({'name':n+'_'+c+'.png','id':str(i),'uuid':uid(),'width':1,'height':1,'uv_width':16,'uv_height':16,'particle':False,'render_mode':'default','mode':'bitmap','saved':False,'source':'data:image/png;base64,'+base64.b64encode(png(c,112 if n=='sticla' else 255)).decode()})
tex={name:i for i,name in enumerate(COLORS)}
elements=[];groups=[];roots=[]
def group(name,origin,parent=None):
 id=uid();groups.append({'name':name,'uuid':id,'origin':origin,'rotation':[0,0,0],'export':True,'visibility':True,'isOpen':True});n={'uuid':id,'children':[]};(roots if parent is None else parent['children']).append(n);return n
def cube(g,name,a,b,color,rotation=None,origin=None):
 assert all(a[i]<b[i] for i in range(3)),(name,a,b)
 assert not rotation or all(v in (0,-45,-22.5,22.5,45) for v in rotation),(name,rotation)
 ident=uid();e={'name':name,'uuid':ident,'type':'cube','from':a,'to':b,'origin':origin or [(a[i]+b[i])/2 for i in range(3)],'faces':{f:{'uv':[0,0,16,16],'texture':tex[color]} for f in ('north','south','east','west','up','down')},'box_uv':False,'export':True,'visibility':True}
 if rotation:e['rotation']=rotation
 elements.append(e);g['children'].append(ident)
def box(g,n,x1,y1,z1,x2,y2,z2,c,rot=None,origin=None):cube(g,n,[x1,y1,z1],[x2,y2,z2],c,rot,origin)
body=group('body',[0,0,0]);seat=group('seat_driver',[0,29,-13],body)
# Compact main body: 43 px wide, faceted rather than voxel-stepped.
box(body,'sasiu',-20,11,-19,20,16,38,'negru')
box(body,'corp inferior',-20.5,16,-18,20.5,29,37,'rosu')
box(body,'capac lateral stanga',-21.5,22,-16,-20.5,39,35,'rosu')
box(body,'capac lateral dreapta',20.5,22,-16,21.5,39,35,'rosu')
box(body,'spate capota',-19,24,34,19,41,39,'rosu_umbra')
box(body,'capota motor',-16,33,15,16,43,36,'rosu')
box(body,'acoperire superioara',-17,42,12,17,44,34,'negru')
for side in (-1,1):
 x=side*20.5
 box(body,'umăr caroserie',x-.6,36,2,x+.6,40,32,'rosu_lumina',[0,0,side*22.5])
 for y in (26,28,30,32):box(body,'fanta ventilatie',min(x,x+side*.8),y,22,max(x,x+side*.8),y+.5,35,'negru')
 box(body,'treapta acces',-23 if side<0 else 21,17,-19,-21 if side<0 else 23,18,-10,'otel')
# Layered service panels and subtle red edge accents, in the style of UTB.
for side in (-1,1):
 x=side*21.5;lo,hi=sorted((x,x+side*.2))
 for z in (-12,7,19,31):box(body,'rost caroserie',lo,23,z,hi,36,z+.25,'rosu_umbra')
 for z in (-10,17):box(body,'maner capac',lo,25,z,hi,25.6,z+3,'negru_adanc')
 box(body,'prag lateral',min(x,x+side*.35),19,-16,max(x,x+side*.35),20,34,'negru')
 box(body,'aparatoare roata fata',min(side*20,side*26.4),22,-20,max(side*20,side*26.4),23,-1,'rosu_umbra')
 box(body,'aparatoare roata spate',min(side*18,side*22.8),14,17,max(side*18,side*22.8),15,31,'rosu_umbra')
# Ladder with individual rungs and handrail, outside the cab.
for z in (-18,-9):box(body,'montant scara',-23,5,z,-22.4,28,z+.55,'otel')
for y in (7,11,15,19,23,27):box(body,'treapta scara',-23.15,y,-18,-22.2,y+.45,-8.45,'gri')
box(body,'mana curenta',-23,28,-18,-22.4,36,-17.4,'negru')
# Open-top hopper, connected walls, clear dark outline as the GLB.
box(body,'buncar fund',-15,43,1,15,44,30,'negru_adanc')
for x in (-17,15):box(body,'buncar lateral',x,44,1,x+2,51,30,'negru')
for z in (1,28):box(body,'buncar perete',-15,44,z,15,51,z+2,'negru')
box(body,'buncar margine stanga',-17.5,50.5,.5,-14.5,51.5,30.5,'otel')
box(body,'buncar margine dreapta',14.5,50.5,.5,17.5,51.5,30.5,'otel')
# Cabin is open inside, with transparent panes and 23-unit clear height.
box(body,'podea cabina',-12,28,-24,12,29,-4,'negru')
box(body,'acoperis cabina',-13,52,-25,13,54,-3,'negru')
for x in (-11.8,11.0):
 for z in (-23.8,-5.5):box(body,'stalp cabina',x,29,z,x+.8,52,z+.8,'negru')
 box(body,'rama cabina sus',x,50.5,-23,x+.8,51.2,-5,'negru')
 box(body,'geam lateral fumuriu',x+.12,29.5,-22.9,x+.68,50.5,-5.6,'sticla')
box(body,'parbriz fumuriu',-10.8,29.5,-23.75,10.8,50.5,-23.55,'sticla')
box(body,'geam spate',-10.8,29.5,-5.4,10.8,50.5,-5.2,'sticla')
box(body,'bara sub parbriz',-11,29,-24,11,30,-23,'negru')
box(body,'perna scaun',-2.7,29,-14.5,2.7,30.4,-9.3,'negru')
box(seat,'spatar scaun',-2.7,30.4,-10,2.7,37,-8.8,'negru')
box(body,'coloana volan',-.35,29.5,-20,.35,34,-19.3,'gri')
box(body,'volan sus',-2,34,-20,2,34.5,-19.4,'negru')
box(body,'volan jos',-2,32,-20,2,32.5,-19.4,'negru')
for x in (-2,1.5):box(body,'volan lateral',x,32,-20,x+.5,34.5,-19.4,'negru')
box(body,'bord',-8,30,-22.8,8,32,-21,'negru')
# Interior/dashboard and exterior mirrors, avoiding a solid cab wall.
box(body,'panou bord',-5,32,-22.7,5,34.2,-22.35,'negru_adanc')
for x in (-3,0,3):box(body,'indicator bord',x-.55,32.6,-22.78,x+.55,33.6,-22.7,'far')
for side in (-1,1):
 x=side*12;outer=side*16
 box(body,'brat oglinda',min(x,outer),43,-23,max(x,outer),43.5,-22.5,'otel')
 box(body,'oglinda carcasa',outer-1.3,41,-23.7,outer+1.3,46,-22.4,'negru_adanc')
 box(body,'oglinda sticla',outer-1,41.4,-23.85,outer+1,45.6,-23.7,'gri')
box(body,'stergator',-7,31,-24.15,3,31.3,-23.9,'negru_adanc')
# Exhaust at the rear of the machine and bumper finishing.
box(body,'esapament baza',13,40,24,15.4,49,26.4,'otel')
box(body,'esapament varf',13.4,49,24.4,15,53,26,'negru_adanc')
box(body,'bara protectie spate',-19,15,38.5,19,17,40,'negru')
# Projector clusters on the front, dark housings with yellow lenses.
for side in (-1,1):
 x=side*15
 box(body,'carcasa proiectoare',x-4,44,-25,x+4,48,-23,'negru_adanc')
 for dx in (-2,2):
  box(body,'far galben',x+dx-1.15,44.8,-25.25,x+dx+1.15,47.2,-24.95,'far')
box(body,'grila frontala',-14,24,-19.5,14,28,-18,'negru')
for x in (-12,-6,0,6,12):box(body,'grila insertie',x-.5,24,-19.65,x+.5,28,-19.5,'gri')
for x in (-15,12):box(body,'lampa spate',x,25,39,x+3,27,39.4,'far')
# Rear outlet folds from the hopper-side elbow.
unload=group('unloading_auger',[-16,47,7],body)
box(unload,'cot descarcare',-18,45,5,-14,49,9,'negru')
box(unload,'tub descarcare rosu',-17.4,45.7,8,-14.6,48.5,33,'rosu')
box(unload,'gura descarcare',-18,44.8,32,-14,49.2,35,'negru_adanc')
# Four independently rotating wheels; front radius 11, rear radius 7.
def wheel(name,x,y,z,r,width):
 g=group(name,[x,y,z],body);h=width/2
 # Octagonal cross-section: two central cores plus bevels on all four corners.
 box(g,'anvelopa miez vertical',x-h,y-r,z-r*.62,x+h,y+r,z+r*.62,'negru_adanc')
 box(g,'anvelopa miez transversal',x-h,y-r*.62,z-r,x+h,y+r*.62,z+r,'negru_adanc')
 for sy in (-1,1):
  for sz in (-1,1):
   cy=y+sy*r*.65;cz=z+sz*r*.65
   box(g,'umăr rotunjit anvelopa',x-h,cy-r*.13,cz-r*.34,x+h,cy+r*.13,cz+r*.34,'negru_adanc',[sy*sz*45,0,0],[x,cy,cz])
 # Readable heavy-duty tread bands with legal element rotations.
 for sy in (-1,1):
  for strip in (-1,1):
   xx=x+strip*width*.22
   box(g,'crampon profil',xx-width*.17,y+sy*(r*.8-.4)-.32,z-r*.47,xx+width*.17,y+sy*(r*.8-.4)+.32,z+r*.47,'negru',[sy*strip*22.5,0,0],[xx,y+sy*(r*.8-.4),z])
 for sz in (-1,1):
  box(g,'crampon lateral',x-h+.1,y-r*.43,z+sz*(r-.35)-.28,x+h-.1,y+r*.43,z+sz*(r-.35)+.28,'negru')
 for side in (-1,1):
  l,u=sorted([x+side*h,x+side*(h+.25)])
  box(g,'janta centrala',l,y-r*.43,z-r*.43,u,y+r*.43,z+r*.43,'janta')
  box(g,'janta diagonala',l,y-r*.31,z-r*.31,u,y+r*.31,z+r*.31,'janta',[45,0,0],[x,y,z])
  l,u=sorted([x+side*(h+.25),x+side*(h+.55)])
  box(g,'butuc',l,y-r*.16,z-r*.16,u,y+r*.16,z+r*.16,'negru')
  for dy,dz in ((.29,0),(-.29,0),(0,.29),(0,-.29)):
   box(g,'prezon roata',l,y+dy*r-.23,z+dz*r-.23,u,y+dy*r+.23,z+dz*r+.23,'otel')
 return g
wheel('wheel_fl',-23,11,-10,11,7);wheel('wheel_fr',23,11,-10,11,7)
wheel('wheel_rl',-20,7,24,7,4.5);wheel('wheel_rr',20,7,24,7,4.5)
# Articulated feeder at user-specified hinge, plus 72-unit corn header.
header=group('header_assembly',[0,20,-18],body)
box(header,'gat alimentare',-9,11,-33,9,19,-18,'negru')
box(header,'gat alimentare panou',-8,17,-33,8,19,-18,'rosu')
box(header,'jgheab heder',-36,3,-48,36,7,-32,'negru')
box(header,'perete heder',-36,7,-34,36,12,-32,'rosu')
for x in (-36,34):box(header,'obraz heder',x,3,-49,x+2,12,-32,'rosu')
# Seven tapered covers; four cuboids each. The top is a single smooth tilted
# panel; the two lower panels and tip form a taper, not a staircase.
for i in range(7):
 x=(i-3)*10
 box(header,'cioc baza',x-3.4,2,-53,x+3.4,4.8,-42,'rosu')
 box(header,'cioc fata',x-2.3,1.4,-62,x+2.3,3.6,-52,'rosu')
 box(header,'cioc varf',x-.9,.8,-68,x+.9,2.2,-61,'rosu_lumina')
 box(header,'capota inclinata cioc',x-2.3,3.5,-60,x+2.3,4.2,-44,'rosu_lumina',[-22.5,0,0],[x,3.85,-52])
for i in range(6):
 x=(i-2.5)*10
 box(header,'canal alimentare',x-1,4,-55,x+1,4.6,-39,'negru_adanc')
 box(header,'lant alimentare',x-.4,4.6,-51,x+.4,4.9,-39,'gri')
# Grey feed auger, centred in its own group and oriented along X.
intake=group('intake_auger',[0,8,-39],header)
box(intake,'ax melc',-34,7,-40,34,9,-38,'gri')
box(intake,'tambur melc',-33,6.2,-40.3,33,9.8,-37.7,'gri')
box(intake,'tambur diagonal',-33,6.2,-40.3,33,9.8,-37.7,'gri',[45,0,0],[0,8,-39])
for x in (-28,-21,-14,-7,0,7,14,21,28):box(intake,'nervura melc',x-.35,5.7,-39.8,x+.35,10.3,-38.2,'otel',[22.5,0,0],[x,8,-39])
# Empty compatibility marker: the corn header has no cereal reel.
group('reel',[0,8,-39],header)
assert len(elements)<300,len(elements)
project={'meta':{'format_version':'5.0','model_format':'free','box_uv':False},'name':'Horizon Combina GLB Porumb low poly','model_identifier':'horizon_combina_glb_porumb','resolution':{'width':16,'height':16},'elements':elements,'groups':groups,'outliner':roots,'textures':textures}
OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(project,separators=(',',':'))+'\n');print('Generated',OUT,len(elements),'elements',len(groups),'groups')
