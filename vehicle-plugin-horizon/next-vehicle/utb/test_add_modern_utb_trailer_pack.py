import hashlib,io,json,unittest,zipfile
import add_modern_tractor_trailer_pack as p
class ModernPackTest(unittest.TestCase):
    def test_adds_only_trailer_and_restores_tractor(self):
        files={'pack.mcmeta':json.dumps({'pack':{'pack_format':46}}).encode(),'other':b'untouched',p.u.BODY:b'old tractor'}
        for path in (p.u.MODEL,p.u.ASSETS/'tractor_trailer_modern_body.json'):
            for ref in json.loads(path.read_bytes())['textures'].values():
                ns,tex=ref.split(':');files[f'assets/{ns}/textures/{tex}.png']=b'texture'
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:
            for n,v in files.items():z.writestr(n,v)
        raw=b.getvalue();result=p.build(raw,hashlib.sha1(raw).hexdigest())
        with zipfile.ZipFile(io.BytesIO(result)) as z:
            self.assertEqual(set(files)|{p.MODEL,p.ITEM},set(z.namelist()))
            for name,value in files.items():self.assertEqual(z.read(name),p.u.MODEL.read_bytes() if name==p.u.BODY else value)
            self.assertEqual(z.read(p.MODEL),(p.u.ASSETS/'tractor_trailer_modern_body.json').read_bytes())
        with self.assertRaises(ValueError):p.build(raw)
    def test_model_has_tandem_axles_and_correct_hitch(self):
        m=json.loads((p.u.ASSETS/'tractor_trailer_modern_body.json').read_text());p.u.validate(m)
        names={e['name']:e for e in m['elements']}
        self.assertEqual(2,sum(n.startswith('tandem axle') for n in names))
        coupler=names['drawbar coupling']
        self.assertLessEqual(-2.75+2*(coupler['from'][2]-8)/16,0)
        self.assertGreaterEqual(-2.75+2*(coupler['to'][2]-8)/16,0)
        for n in ('left rear red lens','right rear red lens','plate face'):self.assertIn(n,names)
