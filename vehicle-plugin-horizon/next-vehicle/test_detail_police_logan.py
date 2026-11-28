import hashlib,json,unittest
from pathlib import Path
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f,polish_logan_body as p,refit_police_logan as q,finish_police_logan as t,detail_police_logan as d
from test_repair_logan_body import archive,overlaps
ROOT=Path(__file__).resolve().parents[2]
class DetailTest(unittest.TestCase):
    def setUp(self):
        b=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}',**{n:'{"credit":"source"}' for n in c.PATHS},'other':'untouched'})
        for fn in (c.build,r.repair,f.build,p.build,q.build,t.build):b=fn(b,hashlib.sha1(b).hexdigest())
        self.orig=b;self.before=c.readzip(b);self.result=d.build(b,hashlib.sha1(b).hexdigest());self.after=c.readzip(self.result)
        self.models=[json.loads(self.after[n]) for n in c.PATHS];self.e=self.models[0]['elements']
    def test_only_body_changes_and_no_overlap(self):
        self.assertEqual(set(self.before),set(self.after))
        for n in self.after:
            if n not in c.PATHS:self.assertEqual(self.before[n],self.after[n])
        self.assertEqual(self.result,d.build(self.orig,hashlib.sha1(self.orig).hexdigest()))
        for m in self.models:
            self.assertFalse(overlaps(m['elements']))
            for x in m['elements']:
                self.assertTrue(all(-16<=v<=32 for k in ('from','to') for v in x[k]))
        for m in self.models[1:]:self.assertEqual(sum(a!=b for a,b in zip(self.e,m['elements'])),1)
    def test_pillars_follow_original_outlines_and_connect_floor(self):
        for x0,x1 in ((-.65,.35),(15.65,16.65)):
            self.assertIn(c.cube([x0,1.7,4.8],[x1,15.4,5.5],'trim'),self.e)
            self.assertIn(c.cube([x0,1.7,-1.9],[x1,15.2,-1.4],'body'),self.e)
        for x0,x1 in ((-.65,-.48),(16.48,16.65)):
            for z0,z1 in ((-2.3,-1.9),(-1.4,4.8),(5.5,17.3)):
                self.assertIn(c.cube([x0,1.7,z0],[x1,5.4,z1],'trim'),self.e)
    def test_grate_floor_roof_and_seat_contacts(self):
        for x in (2,4,6,8,10,12,14):
            self.assertIn(c.cube([x,1.95,4.5],[x+.14,14.95,4.65],'trim'),self.e)
        self.assertIn(c.cube([.38,1.7,4.47],[15.62,1.95,4.79],'trim'),self.e)
        self.assertIn(c.cube([.38,14.95,4.47],[15.62,15.2,4.79],'trim'),self.e)
        self.assertIn(c.cube([2.8,7.,4.79],[3.2,7.45,4.81],'trim'),self.e)
    def test_trunk_and_bench_wheel_wells(self):
        self.assertIn(c.cube([-1.45,8.75,-15.25],[17.45,9.2,-7.35],'body'),self.e)
        self.assertIn(c.cube([2.5,1,-10.8],[13.5,8.6,-10.6],'trim'),self.e)
        for x0,x1 in ((2.45,2.5),(13.5,13.55)):
            self.assertIn(c.cube([x0,1,-10.8],[x1,5.18,-2.9],'seat'),self.e)
        for x0,x1 in ((2.5,2.95),(13.05,13.5)):
            self.assertIn(c.cube([x0,3.7,-3.9],[x1,5.18,-3.0],'seat'),self.e)
        wheel=json.loads((ROOT/'content/assets/gokart/models/block/wheel_sports.json').read_text())
        width=max(max(abs(a['from'][0]-8),abs(a['to'][0]-8)) for a in wheel['elements'])*.95
        self.assertLess(8-(6.3+1.9)+width,2.45)
