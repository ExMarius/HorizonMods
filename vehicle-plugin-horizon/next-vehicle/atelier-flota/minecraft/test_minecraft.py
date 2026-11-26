import hashlib, io, json, struct, subprocess, tempfile, unittest, zipfile, zlib
from pathlib import Path
import build_pack
HERE=Path(__file__).resolve().parent
MODELS=('cab','flatbed','workshop','wheel','steering')

def base(extra=None):
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w') as z:
        z.writestr('pack.mcmeta',json.dumps({'pack':{'pack_format':46}}))
        z.writestr('original/file',b'existing data')
        if extra:z.writestr(extra,b'existing')
    return out.getvalue()

class ModelExportTest(unittest.TestCase):
    def test_generated_models_texture_references_and_vanilla_limits(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);subprocess.run(['node',str(HERE/'export.mjs'),str(out)],check=True,stdout=subprocess.DEVNULL)
            report=json.loads((out/'conversion-report.json').read_text());self.assertEqual(report['itemDisplayScale'],4)
            for name in MODELS:
                model='horizon_service_'+name
                obj=json.loads((out/'models/item'/f'{model}.json').read_text())
                item=json.loads((out/'items'/f'{model}.json').read_text())
                self.assertEqual(item['model']['model'],'vehicle:item/'+model)
                self.assertTrue(obj['elements'])
                for e in obj['elements']:
                    self.assertTrue(all(-16<=lo<hi<=32 for lo,hi in zip(e['from'],e['to'])),e['name'])
                    if 'rotation' in e:
                        self.assertIn(e['rotation']['angle'],(-45,-22.5,0,22.5,45))
                        self.assertTrue(all(-16<=n<=32 for n in e['rotation']['origin']))
                    self.assertEqual(set(e['faces']),{'north','south','east','west','up','down'})
                    for face in e['faces'].values(): self.assertIn(face['texture'][1:],obj['textures'])
                for texture in obj['textures'].values():
                    self.assertRegex(texture,r'^vehicle:item/[a-z0-9_]+$')
                    self.assertTrue((out/'textures'/f'{texture.split(":")[1]}.png').is_file(),texture)
            glass=(out/'textures/item/horizon_service_glass.png').read_bytes()
            self.assertEqual(glass[:8],bytes.fromhex('89504e470d0a1a0a'))
            self.assertTrue(any(r['vanillaDegrees']!=r['originalDegrees'] for r in report['rotationApproximations']))
    def test_checked_in_assets_match_authored_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            fresh=Path(tmp)
            subprocess.run(['node',str(HERE/'export.mjs'),str(fresh)],check=True,stdout=subprocess.DEVNULL)
            saved=HERE/'assets'
            paths={p.relative_to(fresh) for p in fresh.rglob('*') if p.is_file()}
            self.assertEqual(paths,{p.relative_to(saved) for p in saved.rglob('*') if p.is_file()})
            for path in paths:self.assertEqual((fresh/path).read_bytes(),(saved/path).read_bytes(),str(path))
    def test_glass_texture_contains_transparency(self):
        data=(HERE/'assets/textures/item/horizon_service_glass.png').read_bytes()
        offset=8;compressed=b''
        while offset<len(data):
            length=struct.unpack_from('>I',data,offset)[0];kind=data[offset+4:offset+8]
            if kind==b'IDAT':compressed+=data[offset+8:offset+8+length]
            offset+=12+length
        pixel=zlib.decompress(compressed)
        self.assertEqual(len(pixel),5)
        self.assertGreater(pixel[4],0);self.assertLess(pixel[4],255)
    def test_pack_is_deterministic_and_preserves_every_old_file(self):
        raw=base();sha=hashlib.sha1(raw).hexdigest();out=build_pack.build(raw,sha)
        self.assertEqual(out,build_pack.build(raw,sha))
        with zipfile.ZipFile(io.BytesIO(out)) as z:
            self.assertEqual(z.read('original/file'),b'existing data')
            for name in MODELS:
                self.assertIn('assets/vehicle/models/item/horizon_service_'+name+'.json',z.namelist())
                self.assertIn('assets/vehicle/items/horizon_service_'+name+'.json',z.namelist())
    def test_bad_hash_and_collisions_are_rejected(self):
        with self.assertRaises(ValueError):build_pack.build(base(),'0'*40)
        raw=base('assets/vehicle/items/horizon_service_cab.json')
        with self.assertRaises(ValueError):build_pack.build(raw,hashlib.sha1(raw).hexdigest())

if __name__=='__main__':unittest.main()
