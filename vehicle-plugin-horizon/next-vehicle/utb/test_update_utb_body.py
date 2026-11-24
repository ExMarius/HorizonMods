import hashlib,io,json,math,unittest,zipfile
import update_utb_body as u

class UpdateUTBTest(unittest.TestCase):
    def test_authored_model_and_dimensions(self):
        m=json.loads(u.MODEL.read_text());u.validate(m)
        parts={e['name']:e for e in m['elements']}
        self.assertEqual(len(parts),len(m['elements']))
        for name in ('cream roof','left rear fender','right rear fender','front grille','left headlamp lens','right headlamp lens','seat cushion','exhaust tube'):
            self.assertIn(name,parts)
        actual=lambda value:8+2*(value-8)
        zmin=min(actual(e['from'][2])-8 for e in m['elements']);zmax=max(actual(e['to'][2])-8 for e in m['elements'])
        self.assertAlmostEqual(65.6,zmax-zmin,places=3)
        self.assertAlmostEqual(40.8,actual(parts['cream roof']['to'][1]),places=3)
        self.assertAlmostEqual(26.4,2*(parts['hood top']['to'][2]-parts['hood top']['from'][2]),places=3)
        self.assertAlmostEqual(10.9,2*(parts['hood top']['to'][0]-parts['hood top']['from'][0]),places=3)
        self.assertGreater(actual(parts['left rear fender']['from'][1]),23.2)
        self.assertFalse(any('glass' in name for name in parts))
    def test_wheel_dimensions_pivots_and_segments(self):
        for model,diameter,width in [('utb_650_wheel_front',13.12,3.04),('utb_650_wheel_rear',23.2,6.08)]:
            m=json.loads((u.ASSETS/(model+'.json')).read_text());u.validate(m)
            parts={e['name']:e for e in m['elements']}
            self.assertEqual(8,sum(n.startswith('tire ') and n not in ('tire centre vertical','tire centre horizontal') for n in parts))
            for e in m['elements']:
                if 'rotation' in e:self.assertEqual([8,8,8],e['rotation']['origin'])
            self.assertAlmostEqual(diameter,parts['tire top']['to'][1]-parts['tire bottom']['from'][1],places=2)
            self.assertAlmostEqual(width,parts['tire top']['to'][0]-parts['tire top']['from'][0],places=2)
    def test_only_body_changes_and_assets_added(self):
        old=io.BytesIO()
        with zipfile.ZipFile(old,'w') as z:
            z.writestr('pack.mcmeta',json.dumps({'pack':{'pack_format':46}}));z.writestr(u.BODY,'old');z.writestr('vehicles/other','unchanged')
        data=old.getvalue();expected=hashlib.sha1(data).hexdigest();result=u.build(data,expected)
        with zipfile.ZipFile(io.BytesIO(result)) as z:
            self.assertEqual(z.read('vehicles/other'),b'unchanged');self.assertEqual(json.loads(z.read(u.BODY)),json.loads(u.MODEL.read_text()))
            for name in u.WHEELS:self.assertIn('assets/vehicle/items/'+name+'.json',z.namelist())
            for name in u.TEXTURES:self.assertIn('assets/vehicle/textures/utb/'+name+'.png',z.namelist())
        self.assertEqual(result,u.build(data,expected))
        with self.assertRaises(ValueError):u.build(data)
