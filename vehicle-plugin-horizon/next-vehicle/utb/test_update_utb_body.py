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
            fender=parts[side+' rear fender'];lip=parts[side+' fender lip']
            self.assertAlmostEqual(-10.0,fender['from'][2])
            self.assertGreaterEqual(lip['from'][2],fender['from'][2])
            self.assertLessEqual(lip['to'][2],fender['to'][2])
        self.assertLessEqual(parts['right mirror arm']['from'][1],parts['right mirror']['to'][1])
        self.assertGreaterEqual(parts['right mirror arm']['to'][1],parts['right mirror']['from'][1])
        self.assertLessEqual(parts['right mirror arm']['from'][2],parts['right mirror']['to'][2])
        self.assertGreaterEqual(parts['right mirror arm']['to'][2],parts['right mirror']['from'][2])
        rim=parts['exhaust rim']
        self.assertAlmostEqual(4.39,2*((rim['from'][0]+rim['to'][0])/2-8),places=2)
        self.assertAlmostEqual(37.2,8+2*(rim['to'][1]-8),places=2)
        self.assertAlmostEqual(4.2,2*((rim['from'][2]+rim['to'][2])/2-8),delta=0.01)
    def test_bumper_is_fixed_and_rear_bench_fits_between_wall_and_driver(self):
        m=json.loads(u.MODEL.read_text()); p={e['name']:e for e in m['elements']}
        bumper=p['front bumper']
        for side in ('left','right'):
            rail=p['front bumper '+side+' mounting rail']
            self.assertLessEqual(rail['from'][2],p['front chassis']['to'][2])
            self.assertGreaterEqual(rail['to'][2],bumper['from'][2])
        bench=p['rear bench cushion'];back=p['rear bench backrest'];driver=p['seat cushion']
        self.assertLess(bench['to'][2],driver['from'][2])
        self.assertLessEqual(back['to'][2],bench['from'][2]+0.3)
        self.assertGreater(bench['to'][0]-bench['from'][0],9.0)
        self.assertAlmostEqual(19.2,8+2*(bench['to'][1]-8),places=3)
        self.assertAlmostEqual(-26.5,2*((bench['from'][2]+bench['to'][2])/2-8),places=3)

    def test_treads_complete_and_rubber_bridges_inner_tread(self):
        import math
        for name in u.WHEELS:
            m=json.loads((u.ASSETS/(name+'.json')).read_text());parts={e['name']:e for e in m['elements']}
            self.assertEqual(32,sum(n.startswith('lug ') for n in parts))
            cores=[e for e in m['elements'] if e['name'].startswith('rubber core')]
            radius=10.75 if 'rear' in name else 5.25
            for i in range(360):
                angle=math.radians(i);y,z=radius*math.cos(angle),radius*math.sin(angle)
                def contains(e):
                    a=math.radians(e.get('rotation',{}).get('angle',0)); yy=y*math.cos(a)+z*math.sin(a);zz=-y*math.sin(a)+z*math.cos(a)
                    return e['from'][1]-8-1e-6 <= yy <= e['to'][1]-8+1e-6 and e['from'][2]-8-1e-6 <= zz <= e['to'][2]-8+1e-6
                self.assertTrue(any(contains(e) for e in cores),f'{name} inner tread gap at {i} degrees')

    def test_tractor_trailer_hitch_and_plate_geometry(self):
        tractor=json.loads(u.MODEL.read_text());trailer=json.loads((u.ASSETS/'tractor_trailer_body.json').read_text())
        u.validate(tractor);u.validate(trailer)
        t={e['name']:e for e in tractor['elements']};r={e['name']:e for e in trailer['elements']}
        # Preserve all five authored squares; the pin sits above the centre one.
        squares=[e for e in tractor['elements'] if e.get('name')=='PTO cap' and e['from'][1]==6.525]
        self.assertEqual(5,len(squares))
        centre=next(e for e in squares if e['from'][0] < 8 < e['to'][0])
        pin=t['rear hitch coupler pin'];coupler=r['coupler']
        self.assertAlmostEqual(centre['to'][1],pin['from'][1])
        for axis in (0,2):
            self.assertAlmostEqual((centre['from'][axis]+centre['to'][axis])/2,
                                   (pin['from'][axis]+pin['to'][axis])/2)
        self.assertNotIn('rear hitch central drawbar',t)
        self.assertNotIn('hitch block',t)
        # Physics hitch is centred on that square. With aligned roots the trailer
        # receiver overlaps the pin in X, Y and Z, including each body's origin.
        hitch_z=-34.45/16
        self.assertAlmostEqual(hitch_z,2*((centre['from'][2]+centre['to'][2])/2-8)/16)
        for axis in (0,):
            self.assertLessEqual(coupler['from'][axis],8)
            self.assertGreaterEqual(coupler['to'][axis],8)
        self.assertLessEqual(-1.75+2*(coupler['from'][2]-8)/16,0)
        self.assertGreaterEqual(-1.75+2*(coupler['to'][2]-8)/16,0)
        pin_bottom=0.5625+2*(pin['from'][1]-8)/16
        pin_top=0.5625+2*(pin['to'][1]-8)/16
        coupler_bottom=0.5+2*(coupler['from'][1]-8)/16
        coupler_top=0.5+2*(coupler['to'][1]-8)/16
        self.assertLessEqual(pin_bottom,coupler_top)
        self.assertGreaterEqual(pin_top,coupler_bottom)
        self.assertLessEqual(coupler['to'][0]-coupler['from'][0],0.6)
        for part in ('rear plate dark frame','rear plate white face'):
            self.assertIn(part,t);self.assertIn(part,r)
        for side in ('left','right'):
            for part in ('housing','red','amber'):self.assertIn(side+' rear lamp '+part,r)
        self.assertEqual('vehicle:item/utb_plate_tractor',tractor['textures']['plate_tractor'])
        self.assertEqual('vehicle:item/utb_plate_trailer',trailer['textures']['plate_trailer'])

    def test_narrow_front_axle_and_custom_steering(self):
        m=json.loads(u.MODEL.read_text()); parts={e['name']:e for e in m['elements']}
        axle=parts['front axle']
        self.assertAlmostEqual(-9.7708,2*(axle['from'][0]-8),places=3)
        self.assertAlmostEqual(9.7708,2*(axle['to'][0]-8),places=3)
        for side,center in [('left',-11.25),('right',11.25)]:
            knuckle=parts['front axle '+side+' steering knuckle']
            self.assertLessEqual(2*(knuckle['from'][0]-8)-0.1,center)
            self.assertGreaterEqual(2*(knuckle['to'][0]-8)+0.1,center)
        column=parts['steering column']
        self.assertAlmostEqual(24.0,8+2*(column['to'][1]-8),places=3)
        self.assertAlmostEqual(-9.4,2*(column['from'][2]-8),places=3)
        wheel=json.loads((u.ASSETS/'utb_steering_wheel.json').read_text());u.validate(wheel)
        self.assertEqual(8,sum(e['name'].startswith('rim ') for e in wheel['elements']))
        self.assertEqual(3,sum('spoke' in e['name'] for e in wheel['elements']))
        self.assertEqual(6.5,max(e['to'][0] for e in wheel['elements'])-min(e['from'][0] for e in wheel['elements']))
        for e in wheel['elements']:
            if 'rotation' in e:self.assertEqual([8,8,8],e['rotation']['origin'])

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
