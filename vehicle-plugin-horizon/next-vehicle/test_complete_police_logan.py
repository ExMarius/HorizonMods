import hashlib,json,math,unittest
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f,polish_logan_body as p,refit_police_logan as q,finish_police_logan as t,detail_police_logan as d,complete_police_logan as z
from test_repair_logan_body import archive,overlaps
class CompleteTest(unittest.TestCase):
    def setUp(self):
        b=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}',**{n:'{"credit":"source"}' for n in c.PATHS},'other':'untouched'})
        for fn in (c.build,r.repair,f.build,p.build,q.build,t.build,d.build):b=fn(b,hashlib.sha1(b).hexdigest())
        self.original=b;self.before=c.readzip(b);self.result=z.build(b,hashlib.sha1(b).hexdigest());self.after=c.readzip(self.result)
        self.models=[json.loads(self.after[n]) for n in c.PATHS];self.e=self.models[0]['elements']
    def test_safe_deterministic_pack_and_sirens(self):
        self.assertEqual(set(self.before),set(self.after))
        for n in self.after:
            if n not in c.PATHS:self.assertEqual(self.after[n],self.before[n],n)
        self.assertEqual(self.result,z.build(self.original,hashlib.sha1(self.original).hexdigest()))
        with self.assertRaises(ValueError):z.build(self.original)
        for m in self.models:
            self.assertFalse(overlaps(m['elements']))
            for part in m['elements']:
                self.assertTrue(all(-16<=v<=32 for k in ('from','to') for v in part[k]))
        for m in self.models[1:]:self.assertEqual(sum(a!=b for a,b in zip(self.e,m['elements'])),1)
    def test_rear_lower_joins_and_upper_backrest(self):
        for x0,x1 in ((-.55,2.45),(13.55,16.55)):
            self.assertIn(c.cube([x0,3.7,-3.0],[x1,5.17,-1.89],'seat'),self.e)
            self.assertIn(c.cube([x0,5.17,-8.3],[x1,6.,-3.0],'trim'),self.e)
        for x0,x1 in ((-.55,2.5),(13.5,16.55)):
            self.assertIn(c.cube([x0,6.18,-5.3],[x1,8.6,-3.9],'seat'),self.e)
        self.assertIn(c.cube([2.5,3.7,-5.3],[13.5,8.6,-3.9],'seat'),self.e)
    def test_arch_filled_outside_rotating_tire_envelope(self):
        for x0,x1 in ((-1.8,-.65),(16.65,17.8)):
            for center in (-6.95,23.95):
                for a,b,y in ((-4.65,-3.85,4.28),(-3.85,-3.1,4.88),(-3.1,-2.2,4.88),(2.2,3.1,4.88),(3.1,3.85,4.88),(3.85,4.65,4.28)):
                    self.assertIn(c.cube([x0,y,round(center+a,5)],[x1,5.17,round(center+b,5)],'body'),self.e)
                    self.assertGreater(math.hypot(min(abs(a),abs(b)),y-1.3),4.1)
    def test_underside_complete_and_loose_hook_removed(self):
        self.assertNotIn(c.cube([7.2,-.24,-15.7],[8.8,0,-10.75],'trim'),self.e)
        self.assertIn(c.cube([2.5,-.08,-10.8],[13.5,1.,27.5],'trim'),self.e)
        self.assertIn(c.cube([-1.5,0,-15.3],[17.5,1.35,-11.1],'trim'),self.e)
        self.assertIn(c.cube([2.5,0,-11.1],[13.5,1.,-10.8],'trim'),self.e)
        self.assertIn(c.cube([2.5,0,27.5],[13.5,1.,29.0],'trim'),self.e)
        for x0,x1 in ((-1.6,2.5),(13.5,17.6)):
            self.assertIn(c.cube([x0,0,-2.3],[x1,.9,17.5],'trim'),self.e)
