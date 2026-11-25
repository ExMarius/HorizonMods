import hashlib,io,json,unittest,zipfile
import update_utb_body as u

class UpdateUTBTest(unittest.TestCase):
    def test_authored_body_layout(self):
        m=json.loads(u.MODEL.read_text());u.validate(m)
        parts={e['name']:e for e in m['elements']}
        self.assertEqual(len(parts),len(m['elements']))
        for name in ('cream roof','left rear fender','right rear fender','front grille','left headlamp lens','right headlamp lens','seat cushion','exhaust tube','left stair upper','left stair lower','left fuel tank','left amber signal','lower link left','lower link right','upper center link'):
            self.assertIn(name,parts)
        actual=lambda v:8+2*(v-8)
        self.assertAlmostEqual(44.0,actual(parts['cream roof']['to'][1]),places=3)
        self.assertAlmostEqual(16.8,actual(parts['cab floor']['to'][1]),places=3)
        self.assertAlmostEqual(20.8,actual(parts['seat cushion']['to'][1]),places=3)
        self.assertAlmostEqual(-25.2,actual((parts['seat cushion']['from'][2]+parts['seat cushion']['to'][2])/2)-8,places=3)
        self.assertAlmostEqual(28,2*(parts['hood top']['to'][2]-parts['hood top']['from'][2]),places=3)
        self.assertAlmostEqual(12.5,2*(parts['hood top']['to'][0]-parts['hood top']['from'][0]),places=3)
        self.assertGreater(actual(parts['left rear fender']['from'][1]),24.8)
        self.assertFalse(any('glass' in name for name in parts))
        self.assertEqual(10,sum('vent rib' in n for n in parts))
    def test_wheel_dimensions_pivots_and_segments(self):
        for model,diameter,width in [('utb_650_wheel_front',13.8,3.5),('utb_650_wheel_rear',24.8,6.7)]:
            m=json.loads((u.ASSETS/(model+'.json')).read_text());u.validate(m)
            parts={e['name']:e for e in m['elements']}
            self.assertEqual(16,sum(n.startswith('tread arc ') for n in parts))
            self.assertEqual(10,sum(n.startswith('stud ') for n in parts))
            for e in m['elements']:
                if 'rotation' in e:self.assertEqual([8,8,8],e['rotation']['origin'])
            a=parts['tread arc horizontal 1'];b=parts['tread arc horizontal -1']
            self.assertAlmostEqual(diameter,a['to'][1]-b['from'][1],places=2)
            self.assertAlmostEqual(width,a['to'][0]-a['from'][0],places=2)
    def test_only_body_changes_and_assets_added(self):
        old=io.BytesIO()
        with zipfile.ZipFile(old,'w') as z:
            z.writestr('pack.mcmeta',json.dumps({'pack':{'pack_format':46}}));z.writestr(u.BODY,'old');z.writestr('vehicles/other','unchanged')
        data=old.getvalue();expected=hashlib.sha1(data).hexdigest();result=u.build(data,expected)
        with zipfile.ZipFile(io.BytesIO(result)) as z:
            self.assertEqual(z.read('vehicles/other'),b'unchanged');self.assertEqual(json.loads(z.read(u.BODY)),json.loads(u.MODEL.read_text()))
            for name in u.WHEELS:self.assertIn('assets/vehicle/items/'+name+'.json',z.namelist())
            for name in u.TEXTURES:self.assertIn('assets/vehicle/textures/item/utb_'+name+'.png',z.namelist())
        self.assertEqual(result,u.build(data,expected))
        with self.assertRaises(ValueError):u.build(data)
