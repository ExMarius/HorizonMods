import hashlib,io,json,unittest,zipfile
import restore_tractor_bar_pack as p
class RestoreBarPackTest(unittest.TestCase):
    def test_only_tractor_model_changes(self):
        files={'pack.mcmeta':json.dumps({'pack':{'pack_format':46}}).encode(),'other':b'untouched'}
        for name,path in p.MODELS.items():
            files[name]=b'old'
            for ref in json.loads(path.read_bytes())['textures'].values():
                ns,tex=ref.split(':');files[f'assets/{ns}/textures/{tex}.png']=b'texture'
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:
            for n,v in files.items():z.writestr(n,v)
        raw=b.getvalue();result=p.build(raw,hashlib.sha1(raw).hexdigest())
        with zipfile.ZipFile(io.BytesIO(result)) as z:
            self.assertEqual(set(files),set(z.namelist()))
            for name,value in files.items():self.assertEqual(z.read(name),p.MODELS[name].read_bytes() if name in p.MODELS else value)
        with self.assertRaises(ValueError):p.build(raw)
