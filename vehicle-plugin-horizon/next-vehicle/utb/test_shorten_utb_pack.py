import hashlib,io,json,unittest,zipfile
import shorten_utb_pack as p
import update_utb_body as u
class ShortenTest(unittest.TestCase):
    def test_only_body_replaced_and_gauges_added(self):
        model=json.loads(u.MODEL.read_text())
        files={'pack.mcmeta':json.dumps({'pack':{'pack_format':46}}).encode(),u.BODY:b'old body','unrelated':b'unchanged'}
        for ref in model['textures'].values():
            ns,path=ref.split(':');name=f'assets/{ns}/textures/{path}.png'
            if name!=p.GAUGES:files[name]=b'existing texture'
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:
            for n,b in files.items():z.writestr(n,b)
        old=buf.getvalue();sha=hashlib.sha1(old).hexdigest();new=p.build(old,sha)
        with zipfile.ZipFile(io.BytesIO(new)) as z:
            self.assertEqual(set(z.namelist()),set(files)|{p.GAUGES})
            for n,b in files.items():
                if n!=u.BODY:self.assertEqual(z.read(n),b,n)
            self.assertEqual(json.loads(z.read(u.BODY)),model)
        self.assertEqual(new,p.build(old,sha))
        with self.assertRaises(ValueError):p.build(old)
