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
    def test_undesired_side_hangers_and_jack_removed(self):
        m=json.loads(p.SOURCE.read_text());p.u.validate(m); e={x['name']:x for x in m['elements']}
        for name in ('left drawbar-to-axle hanger','right drawbar-to-axle hanger','drawbar support','drawbar support foot'):
            self.assertNotIn(name,e)
        def overlaps(a,b):return all(a['from'][i] <= b['to'][i] and b['from'][i] <= a['to'][i] for i in range(3))
        self.assertTrue(overlaps(e['front axle'],e['front axle kingpin support']))
        for color in ('rubber','hyd'):
            sections=[e[color+' hose connected section '+str(i)] for i in range(4)]
            self.assertTrue(overlaps(sections[0],e[color+' axle hose fitting']))
            self.assertTrue(overlaps(e[color+' axle hose fitting'],e['front axle']))
            for a,b in zip(sections,sections[1:]):self.assertTrue(overlaps(a,b))
            self.assertTrue(overlaps(sections[-1],e[color+' front hose fitting']))
            self.assertTrue(overlaps(e[color+' front hose fitting'],e['tow eye back']))
