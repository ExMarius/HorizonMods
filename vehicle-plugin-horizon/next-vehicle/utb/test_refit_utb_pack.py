import hashlib,io,json,unittest,zipfile
import refit_utb_pack as r
class RefitTest(unittest.TestCase):
    def test_only_utb_files_modified(self):
        files={'pack.mcmeta':json.dumps({'pack':{'pack_format':46}}).encode(),'unrelated':b'keep',r.CREAM:b'original cream'}
        files.update({p:b'old model' for p in r.MODELS})
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:
            for n,b in files.items():z.writestr(n,b)
        old=buf.getvalue();expected=hashlib.sha1(old).hexdigest();new=r.build(old,expected)
        with zipfile.ZipFile(io.BytesIO(new)) as z:
            self.assertEqual(z.read('unrelated'),b'keep');self.assertEqual(z.read('pack.mcmeta'),files['pack.mcmeta']);self.assertIn(r.AMBER,z.namelist())
            for n in r.MODELS:self.assertNotEqual(z.read(n),files[n])
        self.assertEqual(new,r.build(old,expected))
        with self.assertRaises(ValueError):r.build(old)
