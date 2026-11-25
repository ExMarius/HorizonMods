import hashlib,io,json,unittest,zipfile
import fix_utb_modern_details_pack as p
class DetailPackTest(unittest.TestCase):
    def test_only_two_models_change(self):
        sources={p.MODEL:p.SOURCE,p.BODY:p.BODY_SOURCE}
        files={'pack.mcmeta':json.dumps({'pack':{'pack_format':46}}).encode(),'other':b'untouched',p.MODEL:b'old front',p.BODY:b'old body'}
        for path in sources.values():
            for ref in json.loads(path.read_bytes())['textures'].values():
                ns,tex=ref.split(':');files[f'assets/{ns}/textures/{tex}.png']=b'texture'
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:
            for n,v in files.items():z.writestr(n,v)
        raw=b.getvalue();result=p.build(raw,hashlib.sha1(raw).hexdigest())
        with zipfile.ZipFile(io.BytesIO(result)) as z:
            self.assertEqual(set(files),set(z.namelist()))
            for name,value in files.items():self.assertEqual(z.read(name),sources[name].read_bytes() if name in sources else value)
        with self.assertRaises(ValueError):p.build(raw)
    def test_rear_bumper_is_supported(self):
        m=json.loads(p.BODY_SOURCE.read_text());p.u.validate(m);e={x['name']:x for x in m['elements']}
        def overlaps(a,b):return all(a['from'][i] <= b['to'][i] and b['from'][i] <= a['to'][i] for i in range(3))
        for side,rail in [('left','main chassis -0.75'),('right','main chassis 0.65')]:
            bracket=e['rear bumper '+side+' chassis bracket'];self.assertTrue(overlaps(bracket,e['rear underrun bumper']));self.assertTrue(overlaps(bracket,e[rail]))
