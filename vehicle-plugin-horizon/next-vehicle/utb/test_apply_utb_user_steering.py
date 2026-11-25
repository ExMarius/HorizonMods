import hashlib,io,json,unittest,zipfile
import apply_utb_user_steering as p
import update_utb_body as u
class SteeringPackTest(unittest.TestCase):
    def test_only_body_replaced_and_steering_added(self):
        files={'pack.mcmeta':json.dumps({'pack':{'pack_format':46}}).encode(),'other':b'untouched',u.BODY:b'old body'}
        for path in (u.MODEL,u.ASSETS/'utb_steering_wheel.json'):
            for ref in json.loads(path.read_bytes())['textures'].values():
                ns,tex=ref.split(':');files[f'assets/{ns}/textures/{tex}.png']=b'texture'
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:
            for n,v in files.items():z.writestr(n,v)
        data=b.getvalue();out=p.build(data,hashlib.sha1(data).hexdigest())
        with zipfile.ZipFile(io.BytesIO(out)) as z:
            self.assertEqual(set(files)|{p.MODEL,p.ITEM},set(z.namelist()))
            for n,v in files.items():self.assertEqual(z.read(n),u.MODEL.read_bytes() if n==u.BODY else v)
            self.assertEqual(z.read(p.MODEL),(u.ASSETS/'utb_steering_wheel.json').read_bytes())
        with self.assertRaises(ValueError):p.build(data)
