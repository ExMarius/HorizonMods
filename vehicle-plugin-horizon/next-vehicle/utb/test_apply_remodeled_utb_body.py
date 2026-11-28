import hashlib,io,json,unittest,zipfile
import apply_remodeled_utb_body as p
import update_utb_body as u

class UserBodyTest(unittest.TestCase):
    def test_preserves_other_entries_and_exact_user_model(self):
        model=json.loads(u.MODEL.read_bytes())
        files={'pack.mcmeta':json.dumps({'pack':{'pack_format':46}}).encode(),u.BODY:b'old', 'other':b'keep'}
        for ref in model['textures'].values():
            ns,path=ref.split(':');files[f'assets/{ns}/textures/{path}.png']=b'texture'
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:
            for name,data in files.items():z.writestr(name,data)
        old=buf.getvalue();result=p.build(old,hashlib.sha1(old).hexdigest())
        with zipfile.ZipFile(io.BytesIO(result)) as z:
            self.assertEqual(set(z.namelist()),set(files))
            for name,data in files.items():self.assertEqual(z.read(name),u.MODEL.read_bytes() if name==u.BODY else data)
        with self.assertRaises(ValueError):p.build(old)
