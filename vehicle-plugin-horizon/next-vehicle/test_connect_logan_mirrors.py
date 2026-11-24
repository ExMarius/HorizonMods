import hashlib,json,math,unittest
from pathlib import Path
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f,polish_logan_body as p,refit_police_logan as q,finish_police_logan as t,detail_police_logan as d,complete_police_logan as u,restore_police_wheels as v,seal_police_logan as s,close_logan_wheelwells as w,connect_logan_mirrors as n
from test_repair_logan_body import archive,overlaps
ROOT=Path(__file__).resolve().parents[2]
class MirrorsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}',**{x:'{"credit":"source"}' for x in c.PATHS},'other':'untouched'})
        for fn in (c.build,r.repair,f.build,p.build,q.build,t.build,d.build,u.build,v.build,s.build,w.build):b=fn(b,hashlib.sha1(b).hexdigest())
        cls.orig=b;cls.before=c.readzip(b);cls.result=n.build(b,hashlib.sha1(b).hexdigest());cls.after=c.readzip(cls.result)
        cls.models=[json.loads(cls.after[x]) for x in c.PATHS];cls.e=cls.models[0]['elements']
    def test_resource_scope_and_all_siren_variants(self):
        self.assertEqual(set(self.before),set(self.after))
        for k in self.before:
            if k not in c.PATHS:self.assertEqual(self.before[k],self.after[k])
        self.assertEqual(self.result,n.build(self.orig,hashlib.sha1(self.orig).hexdigest()))
        with self.assertRaises(ValueError):n.build(self.orig)
        for m in self.models:
            self.assertFalse(overlaps(m['elements']))
            self.assertTrue(all(-16<=x<=32 for a in m['elements'] for k in ('from','to') for x in a[k]))
        for m in self.models[1:]:self.assertEqual(sum(a!=b for a,b in zip(self.e,m['elements'])),1)
    def test_dark_backing_hides_seats_outside_static_tire(self):
        wheel=json.loads((ROOT/'content/assets/gokart/models/block/wheel_sports.json').read_text())
        max_half_width=max(max(abs(a['from'][0]-8),abs(a['to'][0]-8)) for a in wheel['elements'])*.95
        edge=8-(6.3+1.9)+max_half_width
        self.assertLess(edge,2.46)
        for x0,x1 in ((2.46,2.49),(13.51,13.54)):
            self.assertIn(c.cube([x0,.9,-12.15],[x1,8.55,-2.4],'trim'),self.e)
        # Conservative 35-degree projection including rim width, tire radius
        # and steering offset. This is a bound, not a client render check.
        swept=8-6.3-1.9*math.cos(math.radians(35))+max_half_width*math.cos(math.radians(35))+4.1*math.sin(math.radians(35))
        self.assertLess(swept,4.72)
        for x0,x1 in ((4.72,4.75),(11.25,11.28)):
            self.assertIn(c.cube([x0,.9,18.5],[x1,8.55,29.35],'trim'),self.e)
    def test_wing_mirrors_connected_and_central_mirror_under_roof(self):
        self.assertIn(c.cube([-1.8,8.65,16.],[-.65,9.5,17.5],'trim'),self.e)
        self.assertIn(c.cube([16.65,8.65,16.],[17.8,9.5,17.5],'trim'),self.e)
        self.assertIn(c.cube([7.85,14.1,12.51],[8.15,15.2,12.9],'trim'),self.e)
        self.assertIn(c.cube([6.85,13.55,12.4],[9.15,14.15,12.8],'trim'),self.e)
        self.assertIn(c.cube([7.05,13.65,12.36],[8.95,14.05,12.39],'chrome'),self.e)
