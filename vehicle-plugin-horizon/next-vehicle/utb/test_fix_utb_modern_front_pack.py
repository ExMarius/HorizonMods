import hashlib,io,json,unittest,zipfile
import fix_utb_modern_front_pack as p
class FrontPackTest(unittest.TestCase):
    def test_only_front_model_changes(self):
        files={'pack.mcmeta':json.dumps({'pack':{'pack_format':46}}).encode(),'other':b'untouched',p.MODEL:b'old'}
        for ref in json.loads(p.SOURCE.read_bytes())['textures'].values():
            ns,tex=ref.split(':');files[f'assets/{ns}/textures/{tex}.png']=b'texture'
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:
            for n,v in files.items():z.writestr(n,v)
        raw=b.getvalue();result=p.build(raw,hashlib.sha1(raw).hexdigest())
        with zipfile.ZipFile(io.BytesIO(result)) as z:
            self.assertEqual(set(files),set(z.namelist()))
            for name,value in files.items():self.assertEqual(z.read(name),p.SOURCE.read_bytes() if name==p.MODEL else value)
        with self.assertRaises(ValueError):p.build(raw)
    def test_axle_hangers_touch_axle_and_drawbar(self):
        m=json.loads(p.SOURCE.read_text());p.u.validate(m); e={x['name']:x for x in m['elements']};axis=e['front axle'];pin=e['front axle kingpin support']
        def overlaps(a,b):return all(a['from'][i] <= b['to'][i] and b['from'][i] <= a['to'][i] for i in range(3))
        self.assertTrue(overlaps(axis,pin))
        self.assertTrue(overlaps(pin,e['turntable lower 0']))
        for side in ('left','right'):
            h=e[side+' drawbar-to-axle hanger'];self.assertTrue(overlaps(axis,h));self.assertLess(h['from'][2],12.1);self.assertGreater(h['to'][2],12.1)
