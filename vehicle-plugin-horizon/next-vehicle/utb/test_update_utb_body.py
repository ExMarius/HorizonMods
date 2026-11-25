import hashlib,io,json,unittest,zipfile
import update_utb_body as u

class UpdateUTBTest(unittest.TestCase):
    def test_authored_body_layout(self):
        m=json.loads(u.MODEL.read_text());u.validate(m)
        parts={e['name']:e for e in m['elements']}
        for name in ('cream roof','left rear fender','right rear fender','front grille','left headlamp lens','right headlamp lens','seat cushion','exhaust tube','left stair upper','left stair lower','left fuel tank','left amber signal','lower link left','lower link right','upper center link'):
            self.assertIn(name,parts)
        actual=lambda v:8+2*(v-8)
        self.assertAlmostEqual(44.0,actual(parts['cream roof']['to'][1]),places=3)
        self.assertAlmostEqual(16.8,actual(parts['cab floor']['to'][1]),places=3)
        self.assertAlmostEqual(20.8,actual(parts['seat cushion']['to'][1]),places=3)
        self.assertAlmostEqual(-15.8,actual((parts['seat cushion']['from'][2]+parts['seat cushion']['to'][2])/2)-8,places=3)
        self.assertAlmostEqual(28,2*(parts['hood top']['to'][2]-parts['hood top']['from'][2]),places=3)
        self.assertAlmostEqual(12.5,2*(parts['hood top']['to'][0]-parts['hood top']['from'][0]),places=3)
        self.assertGreater(actual(parts['left rear fender']['from'][1]),24.8)
        self.assertFalse(any('glass' in name for name in parts))
        self.assertEqual(10,sum('vent rib' in n for n in parts))
        self.assertIn('UTB analogue gauges',parts)
        self.assertIn('hydraulic lever',parts)
        decode_z=lambda v:2*(v-8)
        self.assertLessEqual(parts['left mirror arm']['from'][1],parts['left mirror']['to'][1])
        self.assertGreaterEqual(parts['left mirror arm']['to'][1],parts['left mirror']['from'][1])
        self.assertAlmostEqual(13.68,decode_z((parts['front axle']['from'][2]+parts['front axle']['to'][2])/2),places=3)
        self.assertAlmostEqual(-25.2,decode_z((parts['rear axle']['from'][2]+parts['rear axle']['to'][2])/2),places=3)
    def test_remodel_seat_mirror_fenders_and_exhaust_alignment(self):
        m=json.loads(u.MODEL.read_text()); parts={e['name']:e for e in m['elements']}
        cushion,back=parts['seat cushion'],parts['seat back']
        for name in ('seat back seam left','seat back seam right'):
            seam=parts[name]
            self.assertGreaterEqual(seam['from'][0],back['from'][0])
            self.assertLessEqual(seam['to'][0],back['to'][0])
            self.assertLess(abs(seam['from'][2]-back['to'][2]),0.03)
        for side in ('left','right'):
            self.assertEqual(-9.0,parts[side+' rear fender']['from'][2])
            self.assertEqual(-9.0,parts[side+' fender lip']['from'][2])
            self.assertEqual(-9.0,parts[side+' fender back']['from'][2])
        self.assertLessEqual(parts['right mirror arm']['from'][1],parts['right mirror']['to'][1])
        self.assertGreaterEqual(parts['right mirror arm']['to'][1],parts['right mirror']['from'][1])
        self.assertLessEqual(parts['right mirror arm']['from'][2],parts['right mirror']['to'][2])
        self.assertGreaterEqual(parts['right mirror arm']['to'][2],parts['right mirror']['from'][2])
        rim=parts['exhaust rim']
        self.assertAlmostEqual(4.39,2*((rim['from'][0]+rim['to'][0])/2-8),places=2)
        self.assertAlmostEqual(37.2,8+2*(rim['to'][1]-8),places=2)
        self.assertAlmostEqual(4.2,2*((rim['from'][2]+rim['to'][2])/2-8),delta=0.01)
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
