import hashlib,io,json,unittest,zipfile
import add_modern_tractor_trailer_pack as p
class ModernPackTest(unittest.TestCase):
    def test_adds_only_trailer_and_restores_tractor(self):
        files={'pack.mcmeta':json.dumps({'pack':{'pack_format':46}}).encode(),'other':b'untouched',p.u.BODY:b'old tractor'}
        for path in (p.u.MODEL,p.u.ASSETS/'tractor_trailer_modern_body.json',p.u.ASSETS/'tractor_trailer_modern_front.json'):
            for ref in json.loads(path.read_bytes())['textures'].values():
                ns,tex=ref.split(':');entry=f'assets/{ns}/textures/{tex}.png'
                if entry not in p.NEW_TEXTURES:files[entry]=b'texture'
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:
            for n,v in files.items():z.writestr(n,v)
        raw=b.getvalue();result=p.build(raw,hashlib.sha1(raw).hexdigest())
        with zipfile.ZipFile(io.BytesIO(result)) as z:
            self.assertEqual(set(files)|{p.MODEL,p.ITEM,p.FRONT,p.FRONT_ITEM}|set(p.NEW_TEXTURES),set(z.namelist()))
            for name,value in files.items():self.assertEqual(z.read(name),p.u.MODEL.read_bytes() if name==p.u.BODY else value)
            self.assertEqual(z.read(p.MODEL),(p.u.ASSETS/'tractor_trailer_modern_body.json').read_bytes())
            for name,path in p.NEW_TEXTURES.items():self.assertEqual(z.read(name),path.read_bytes())
        with self.assertRaises(ValueError):p.build(raw)
    def test_approved_body_and_hitch_height(self):
        body=json.loads((p.u.ASSETS/'tractor_trailer_modern_body.json').read_text());front=json.loads((p.u.ASSETS/'tractor_trailer_modern_front.json').read_text());p.u.validate(body);p.u.validate(front)
        self.assertEqual(body,json.loads((p.u.ASSETS/'preview_rm5t/body.json').read_text()))
        parts={e['name']:e for e in front['elements']}
        self.assertIn('front axle',parts)
        eye=parts['tow eye left']
        eye_y=.5+2*((eye['from'][1]+eye['to'][1])/2-8)/16
        tractor_y=.5625+2*(6.975-8)/16
        self.assertAlmostEqual(eye_y,tractor_y,places=4)
        z=2*((eye['from'][2]+eye['to'][2])/2-8)/16
        self.assertAlmostEqual(z,1.835)
