import hashlib,io,json,unittest,zipfile
import add_tractor_trailer_pack as p
import update_utb_body as u
class PloughPackTest(unittest.TestCase):
    def test_add_only_plough_and_keep_every_existing_entry(self):
        files={'pack.mcmeta':json.dumps({'pack':{'pack_format':46}}).encode(),'other':b'untouched'}
        m=json.loads((u.ASSETS/'tractor_trailer_body.json').read_bytes())
        for ref in m['textures'].values():
            ns,tex=ref.split(':');files[f'assets/{ns}/textures/{tex}.png']=b'texture'
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:
            for n,v in files.items():z.writestr(n,v)
        data=b.getvalue();out=p.build(data,hashlib.sha1(data).hexdigest())
        with zipfile.ZipFile(io.BytesIO(out)) as z:
            self.assertEqual(set(files)|{p.MODEL,p.ITEM},set(z.namelist()))
            for n,v in files.items():self.assertEqual(z.read(n),v)
            self.assertEqual(json.loads(z.read(p.MODEL)),m)
        with self.assertRaises(ValueError):p.build(data)
