import hashlib,io,json,unittest,zipfile
import apply_utb_bench as p
class FrontHitchTest(unittest.TestCase):
    def test_only_three_models_replaced(self):
        files={'pack.mcmeta':json.dumps({'pack':{'pack_format':46}}).encode(),'other':b'keep'}
        for name,path in p.MODELS.items():
            files[name]=b'old';m=json.loads(path.read_bytes())
            for ref in m['textures'].values():
                ns,tex=ref.split(':');files[f'assets/{ns}/textures/{tex}.png']=b'texture'
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:
            for n,v in files.items():z.writestr(n,v)
        data=b.getvalue();out=p.build(data,hashlib.sha1(data).hexdigest())
        with zipfile.ZipFile(io.BytesIO(out)) as z:
            self.assertEqual(set(files),set(z.namelist()))
            for n,v in files.items():self.assertEqual(z.read(n),p.MODELS[n].read_bytes() if n in p.MODELS else v)
        with self.assertRaises(ValueError):p.build(data)
