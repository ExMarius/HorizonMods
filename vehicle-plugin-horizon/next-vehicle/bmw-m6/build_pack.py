#!/usr/bin/env python3
"""Build a candidate pack with BMW M6 models, without changing existing entries."""
import argparse,hashlib,io,json,struct,subprocess,sys,tempfile,zipfile,zlib
from pathlib import Path
BASE=Path(__file__).parent
EXPECTED='bdd3a3ee9108990bbd7a3c5e343776af49792d27'
NAMES=('body','rear_left','rear_right','front_left','front_right')
def white_png():
 def chunk(kind,content):return struct.pack('>I',len(content))+kind+content+struct.pack('>I',zlib.crc32(kind+content)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b'\x00\xff\xff\xff\xff'))+chunk(b'IEND',b'')
def build(raw,expected=EXPECTED):
 if hashlib.sha1(raw).hexdigest()!=expected:raise ValueError('unexpected base pack SHA-1')
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  if z.testzip() or len(z.namelist())!=len(set(z.namelist())):raise ValueError('invalid ZIP')
  files={n:z.read(n) for n in z.namelist()}
 if json.loads(files['pack.mcmeta'])['pack']['pack_format']!=46:raise ValueError('wrong pack format')
 with tempfile.TemporaryDirectory() as tmp:
  subprocess.run([sys.executable,str(BASE/'convert_glb.py'),tmp],check=True)
  if json.loads((Path(tmp)/'conversion-issues.json').read_text()):raise ValueError('conversion errors')
  new={}
  for name in NAMES:
   model='bmw_m6_'+name;new[f'assets/vehicle/models/item/{model}.json']=(Path(tmp)/(name+'.json')).read_bytes()
   new[f'assets/vehicle/items/{model}.json']=json.dumps({'model':{'type':'minecraft:model','model':'vehicle:item/'+model}},separators=(',',':')).encode()
  b=(BASE/'assets/source.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);binary=b[20+n+8:]
  for i,image in enumerate(g['images']):
   v=g['bufferViews'][image['bufferView']];offset=v.get('byteOffset',0);new[f'assets/vehicle/textures/item/bmw_m6_texture_{i}.png']=binary[offset:offset+v['byteLength']]
  new['assets/vehicle/textures/item/bmw_m6_white.png']=white_png()
  new['credits/bmw-m6.txt']=(BASE/'ATTRIBUTION.md').read_bytes()
  if set(files)&set(new):raise ValueError('new asset already exists')
  files.update(new)
 out=io.BytesIO()
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in sorted(files.items()):
   info=zipfile.ZipInfo(n,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
 return out.getvalue()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('base',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
 if a.base.resolve()==a.output.resolve():p.error('output must differ')
 b=build(a.base.read_bytes());a.output.write_bytes(b);print('candidate SHA-1',hashlib.sha1(b).hexdigest())
