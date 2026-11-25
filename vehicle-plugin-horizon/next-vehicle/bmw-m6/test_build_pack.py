import hashlib,io,json,unittest,zipfile
import build_pack as b
class PackTest(unittest.TestCase):
 def test_preserves_existing_and_adds_only_bmw(self):
  out=io.BytesIO()
  original={'pack.mcmeta':json.dumps({'pack':{'pack_format':46}}).encode(),'existing':b'unchanged'}
  with zipfile.ZipFile(out,'w') as z:
   for name,value in original.items():z.writestr(name,value)
  raw=out.getvalue(); result=b.build(raw,hashlib.sha1(raw).hexdigest())
  with zipfile.ZipFile(io.BytesIO(result)) as z:
   self.assertIsNone(z.testzip()); self.assertEqual(len(z.namelist()),len(original)+14)
   for n,v in original.items():self.assertEqual(z.read(n),v)
   for n in b.NAMES:
    self.assertTrue(json.loads(z.read('assets/vehicle/models/item/bmw_m6_'+n+'.json'))['elements'])
   self.assertIn(b'Sprint',z.read('credits/bmw-m6.txt'))
  with self.assertRaises(ValueError):b.build(raw)
