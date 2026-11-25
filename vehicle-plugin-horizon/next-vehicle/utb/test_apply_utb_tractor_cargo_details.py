import hashlib,io,json,unittest,zipfile
import apply_tractor_cargo_details as p
class CargoPackTest(unittest.TestCase):
    def test_changes_two_models_and_adds_one_texture(self):
        files={'pack.mcmeta':json.dumps({'pack':{'pack_format':46}}).encode(),'other':b'untouched'}
        for name,path in p.MODELS.items():
            files[name]=b'old';m=json.loads(path.read_bytes())
            for ref in m['textures'].values():
                ns,tex=ref.split(':');entry=f'assets/{ns}/textures/{tex}.png'
                if entry!=p.BLUE:files[entry]=b'texture'
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:
            for n,v in files.items():z.writestr(n,v)
        data=b.getvalue();out=p.build(data,hashlib.sha1(data).hexdigest())
        with zipfile.ZipFile(io.BytesIO(out)) as z:
            self.assertEqual(set(files)|{p.BLUE},set(z.namelist()))
            for n,v in files.items():self.assertEqual(z.read(n),p.MODELS[n].read_bytes() if n in p.MODELS else v)
            self.assertEqual(z.read(p.BLUE),(p.u.ASSETS/'textures/plate_blue.png').read_bytes())
        with self.assertRaises(ValueError):p.build(data)
