import hashlib,io,json,unittest,zipfile
import build_pack as b
class PackTest(unittest.TestCase):
 def test_replace_only_old_coupe_assets(self):
  files={'pack.mcmeta':json.dumps({'pack':{'pack_format':46}}).encode(),'other-model':b'untouched'}|{k:b'old' for k in b.OLD};raw=io.BytesIO()
  with zipfile.ZipFile(raw,'w') as z:
   for n,v in files.items():z.writestr(n,v)
  data=raw.getvalue();out=b.build(data,hashlib.sha1(data).hexdigest())
  with zipfile.ZipFile(io.BytesIO(out)) as z:
   self.assertIsNone(z.testzip());self.assertTrue(b.OLD.isdisjoint(z.namelist()));self.assertEqual(z.read('other-model'),b'untouched')
   self.assertEqual(len(set(z.namelist())-set(files)),15)
   for m in ('body','wheel'):self.assertGreater(len(json.loads(z.read(f'assets/vehicle/models/item/horizon_coupe_{m}.json'))['elements']),10)
  with self.assertRaises(ValueError):b.build(data)
