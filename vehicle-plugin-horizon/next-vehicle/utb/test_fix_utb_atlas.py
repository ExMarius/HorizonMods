import copy,hashlib,io,json,unittest,zipfile
import fix_utb_atlas as f
import update_utb_body as u

class AtlasTest(unittest.TestCase):
    def test_only_three_models_and_new_atlas_textures(self):
        files={'pack.mcmeta':json.dumps({'pack':{'pack_format':46}}).encode(),'other':b'unchanged'}
        for path,filename in zip(f.MODELS,('utb_650_body.json',)+tuple(n+'.json' for n in u.WHEELS)):
            model=json.loads((u.ASSETS/filename).read_text())
            model['textures']={k:v.replace('vehicle:item/utb_','vehicle:utb/') for k,v in model['textures'].items()}
            files[path]=json.dumps(model).encode()
        for n in u.TEXTURES:files[f'assets/vehicle/textures/utb/{n}.png']=(u.ASSETS/'textures'/(n+'.png')).read_bytes()
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:
            for n,v in files.items():z.writestr(n,v)
        old=buf.getvalue(); new=f.build(old,hashlib.sha1(old).hexdigest())
        with zipfile.ZipFile(io.BytesIO(new)) as z:
            for n,v in files.items():
                if n not in f.MODELS:self.assertEqual(z.read(n),v,n)
            for path in f.MODELS:
                before=json.loads(files[path]);after=json.loads(z.read(path))
                for n in after['textures']:
                    self.assertEqual(after['textures'][n],f'vehicle:item/utb_{n}')
                    self.assertEqual(z.read(f'assets/vehicle/textures/item/utb_{n}.png'),files[f'assets/vehicle/textures/utb/{n}.png'])
                after['textures']=before['textures'];self.assertEqual(after,before)
        self.assertEqual(new,f.build(old,hashlib.sha1(old).hexdigest()))
        with self.assertRaises(ValueError):f.build(old)
