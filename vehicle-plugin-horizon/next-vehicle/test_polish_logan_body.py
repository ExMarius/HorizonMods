import hashlib,json,unittest
from pathlib import Path
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f,polish_logan_body as p
from test_repair_logan_body import archive,overlaps
ROOT=Path(__file__).resolve().parents[2]
class PolishTest(unittest.TestCase):
    def setUp(self):
        b=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}',**{n:'{"credit":"source"}' for n in c.PATHS},'other':'untouched'})
        for fn in (c.build,r.repair,f.build):b=fn(b,hashlib.sha1(b).hexdigest())
        self.before=c.readzip(b);self.output=p.build(b,hashlib.sha1(b).hexdigest());self.files=c.readzip(self.output)
        self.models=[json.loads(self.files[n]) for n in c.PATHS];self.e=self.models[0]['elements']
    def test_other_assets_and_siren_phases(self):
        self.assertEqual(set(self.before),set(self.files))
        for n in self.files:
            if n not in c.PATHS:self.assertEqual(self.before[n],self.files[n])
        for m in self.models[1:]:self.assertEqual(sum(a!=b for a,b in zip(self.e,m['elements'])),1)
        self.assertFalse(overlaps(self.e))
    def test_footwell_and_arch_joints(self):
        self.assertIn(c.cube([-.65,1.35,-8.3],[16.65,1.7,17.35],'trim'),self.e)
        self.assertIn(c.cube([-.65,1.699,17.35],[16.65,8.38,18.05],'dash'),self.e)
        self.assertIn(c.cube([2.4,0,-10.8],[13.6,1.0,27.5],'trim'),self.e)
        for x0,x1 in ((-1.8,-.65),(16.65,17.8)):
            for z0,z1 in ((-11.65,-2.3),(19.,28.85)):
                self.assertIn(c.cube([x0,5.17,z0],[x1,5.5,z1],'body'),self.e)
    def test_static_tire_fits_floor_bench_and_arch(self):
        # Transform source tire bounds into body model pixels. Static centers:
        # x=8 +/- (6.3+1.9+2.0); y=1.2/1.3; z=-6.95/23.95.
        wheel=json.loads((ROOT/'content/assets/gokart/models/block/wheel_sports.json').read_text())
        max_width=max(max(abs(a['from'][0]-8),abs(a['to'][0]-8)) for a in wheel['elements'])*.95
        inner=8-(6.3+1.9+2.0)+max_width
        self.assertLess(inner,.55) # rear bench begins at .55
        self.assertLess(inner,2.4) # chassis spine begins at 2.4
        radius=max(max(abs(a['from'][1]-8),abs(a['to'][1]-8),abs(a['from'][2]-8),abs(a['to'][2]-8)) for a in wheel['elements'])*.95
        self.assertLess(1.3+radius,5.17)
        for center,lo,hi in ((-6.95,-11.65,-2.3),(23.95,19,28.85)):
            self.assertGreaterEqual(center-radius,lo);self.assertLessEqual(center+radius,hi)
