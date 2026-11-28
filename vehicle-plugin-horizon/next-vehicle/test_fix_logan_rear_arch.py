import hashlib,json,unittest
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f,polish_logan_body as p,refit_police_logan as q,finish_police_logan as t,detail_police_logan as d,complete_police_logan as u,restore_police_wheels as v,seal_police_logan as s,close_logan_wheelwells as w,fix_logan_rear_arch as z
from test_repair_logan_body import archive,overlaps
class RearArchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}',**{x:'{"credit":"source"}' for x in c.PATHS},'other':'untouched'})
        for fn in (c.build,r.repair,f.build,p.build,q.build,t.build,d.build,u.build,v.build,s.build,w.build):b=fn(b,hashlib.sha1(b).hexdigest())
        cls.before=c.readzip(b);cls.result=z.build(b,hashlib.sha1(b).hexdigest());cls.after=c.readzip(cls.result)
        cls.models=[json.loads(cls.after[x]) for x in c.PATHS];cls.e=cls.models[0]['elements']
    def test_scope_phases_no_coplanar_conflicts(self):
        self.assertEqual(set(self.before),set(self.after))
        for k in self.before:
            if k not in c.PATHS:self.assertEqual(self.before[k],self.after[k])
        for m in self.models:
            self.assertFalse(overlaps(m['elements']))
            self.assertTrue(all(-16<=v<=32 for a in m['elements'] for k in ('from','to') for v in a[k]))
        for m in self.models[1:]:self.assertEqual(sum(a!=b for a,b in zip(self.e,m['elements'])),1)
    def test_rear_opening_is_centered_on_restored_wheel(self):
        for x0,x1 in ((-1.8,-.65),(16.65,17.8)):
            self.assertIn(c.cube([x0,1.35,-15.3],[x1,5.5,-12.65],'body'),self.e)
            self.assertIn(c.cube([x0,1.35,-3.3],[x1,5.5,19.0],'body'),self.e)
            self.assertAlmostEqual((-12.65 + -3.3)/2,-7.975)
        for x0,x1 in ((-1.86,-1.8),(17.8,17.86)):
            self.assertIn(c.cube([x0,5.18,-10.15],[x1,5.48,-5.75],'trim'),self.e)
    def test_rear_wall_and_underside_are_beyond_tire_sweep(self):
        self.assertLess(-12.1,-7.95-4.1)
        self.assertIn(c.cube([-1.5,0,-15.3],[17.5,1.35,-12.1],'trim'),self.e)
        for x0,x1 in ((-.65,2.45),(13.55,16.65)):
            self.assertIn(c.cube([x0,1.35,-12.65],[x1,5.2,-12.4],'trim'),self.e)
        for x0,x1 in ((2.46,2.49),(13.51,13.54)):
            self.assertIn(c.cube([x0,.9,-13.15],[x1,8.55,-2.4],'trim'),self.e)
    def test_mirror_mounts_are_preserved(self):
        self.assertIn(c.cube([-1.8,8.65,16.],[-.65,9.5,17.5],'trim'),self.e)
        self.assertIn(c.cube([7.85,14.1,12.51],[8.15,15.2,12.9],'trim'),self.e)
