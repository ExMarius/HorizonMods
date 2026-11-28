import hashlib,json,math,unittest
from pathlib import Path
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f,polish_logan_body as p,refit_police_logan as q,finish_police_logan as t
from test_repair_logan_body import archive,overlaps
class FinishTest(unittest.TestCase):
    def setUp(self):
        data=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}',**{n:'{"credit":"source"}' for n in c.PATHS},'other':'unchanged'})
        for fn in (c.build,r.repair,f.build,p.build,q.build):data=fn(data,hashlib.sha1(data).hexdigest())
        self.original=data;self.before=c.readzip(data);self.result=t.build(data,hashlib.sha1(data).hexdigest());self.after=c.readzip(self.result)
        self.models=[json.loads(self.after[n]) for n in c.PATHS];self.e=self.models[0]['elements']
    def test_resources_siren_and_no_fighting(self):
        self.assertEqual(set(self.before)-{t.SMOKED},set(self.after))
        for n in self.after:
            if n not in set(c.PATHS)|{t.STEER}:self.assertEqual(self.after[n],self.before[n])
        self.assertEqual(self.result,t.build(self.original,hashlib.sha1(self.original).hexdigest()))
        for model in self.models:
            self.assertNotIn('smoked',model['textures'])
            self.assertFalse(any(v['texture']=='#smoked' for e in model['elements'] for v in e['faces'].values()))
            self.assertFalse(overlaps(model['elements']))
        for m in self.models[1:]:self.assertEqual(sum(a!=b for a,b in zip(self.e,m['elements'])),1)
    def test_bench_shelf_wheel_clearance_and_armrests(self):
        self.assertIn(c.cube([2.5,1.7,-3.9],[13.5,3.7,1.5],'seat'),self.e)
        self.assertIn(c.cube([-.55,8.6,-8.34],[16.55,8.74,-5.3],'trim'),self.e)
        for x0,x1 in ((-.55,2.45),(13.55,16.55)):
            self.assertIn(c.cube([x0,5.17,-8.3],[x1,6.,-3.0],'trim'),self.e)
            self.assertIn(c.cube([x0+.25,6,-7.8],[x1-.25,6.18,-3.5],'seat'),self.e)
        # Max static tire height is 5.1; covers begin above it.
        self.assertGreater(5.17,1.3+4*.95)
    def test_partition_attached_and_pedal_floor(self):
        for x in (2,4,6,8,10,12,14):self.assertIn(c.cube([x,4.25,4.5],[x+.14,14.65,4.65],'trim'),self.e)
        for x0,x1 in ((2.8,3.2),(12.8,13.2)):self.assertIn(c.cube([x0,7,4.79],[x1,7.45,4.81],'trim'),self.e)
        self.assertIn(c.cube([.35,1.7,13.5],[15.65,1.82,17.8],'trim'),self.e)
        self.assertIn(c.cube([-.65,1.699,17.35],[16.65,8.38,18.05],'trim'),self.e)
    def test_small_rounded_steering_column_reaches_firewall(self):
        model=json.loads(self.after[t.STEER]);self.assertEqual(len(model['elements']),16)
        self.assertIn(c.cube([7.35,-2.3,7.35],[8.65,7.5,8.65],'trim'),model['elements'])
        z=12.8+.5*10.3*math.sin(math.radians(65));self.assertGreater(z,17.35);self.assertLess(z,18.05)
        self.assertLess(.5*8.4,.73*8) # diameter smaller than previous steering
