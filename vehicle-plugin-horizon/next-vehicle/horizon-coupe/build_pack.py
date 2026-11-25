#!/usr/bin/env python3
"""Replace the rejected converted BMW assets with original Horizon coupe assets."""
import argparse,hashlib,io,json,struct,subprocess,sys,tempfile,zipfile,zlib
from pathlib import Path
BASE=Path(__file__).parent
EXPECTED='7b2ff0a429667b6e28bb560d01672aeb724acdaf'
COLORS={'red':'b42427','darkred':'77191c','black':'22272a','rubber':'151819','silver':'9faeb0','rim':'bec4c1','lamp':'eee8bf','tail':'b31e22','amber':'d78a29','seat':'493834','white':'e9eae0'}
OLD={f'assets/vehicle/{p}/bmw_m6_{n}.json' for p in ('models/item','items') for n in ('body','rear_left','rear_right','front_left','front_right')} | {f'assets/vehicle/textures/item/bmw_m6_{n}.png' for n in ('texture_0','texture_1','white')} | {'credits/bmw-m6.txt'}
def png(rgb):
 def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b'\x00'+bytes.fromhex(rgb)+b'\xff'))+chunk(b'IEND',b'')
def build(raw,expected=EXPECTED):
 if hashlib.sha1(raw).hexdigest()!=expected:raise ValueError('unexpected deployed pack')
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  if z.testzip() or len(z.namelist())!=len(set(z.namelist())):raise ValueError('invalid zip')
  files={n:z.read(n) for n in z.namelist()}
 if json.loads(files['pack.mcmeta'])['pack']['pack_format']!=46 or not OLD.issubset(files):raise ValueError('not expected pack')
 with tempfile.TemporaryDirectory() as tmp:
  subprocess.run([sys.executable,str(BASE/'build_model.py'),tmp],check=True)
  new={}
  for name in ('body','wheel'):
   model='horizon_coupe_'+name;new[f'assets/vehicle/models/item/{model}.json']=(Path(tmp)/(name+'.json')).read_bytes();new[f'assets/vehicle/items/{model}.json']=json.dumps({'model':{'type':'minecraft:model','model':'vehicle:item/'+model}},separators=(',',':')).encode()
  for name,color in COLORS.items():new[f'assets/vehicle/textures/item/horizon_coupe_{name}.png']=png(color)
  if set(new)&set(files):raise ValueError('new asset already exists')
  for n in OLD:del files[n]
  files.update(new)
 out=io.BytesIO()
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in sorted(files.items()):
   entry=zipfile.ZipInfo(n,(1980,1,1,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED;z.writestr(entry,b)
 return out.getvalue()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('base',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
 if a.base.resolve()==a.output.resolve():p.error('output must differ')
 out=build(a.base.read_bytes());a.output.write_bytes(out);print('SHA-1',hashlib.sha1(out).hexdigest())
