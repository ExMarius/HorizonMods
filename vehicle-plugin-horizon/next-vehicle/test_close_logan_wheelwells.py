import hashlib,json,unittest
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f,polish_logan_body as p,refit_police_logan as q,finish_police_logan as t,detail_police_logan as d,complete_police_logan as u,restore_police_wheels as v,seal_police_logan as s,close_logan_wheelwells as z
from test_repair_logan_body import archive,overlaps
class CloseWellsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}',**{n:'{"credit":"source"}' for n in c.PATHS},'other':'untouched'})
        for fn in (c.build,r.repair,f.build,p.build,q.build,t.build,d.build,u.build,v.build,s.build):b=fn(b,hashlib.sha1(b).hexdigest())
        cls.orig=b;cls.before=c.readzip(b);cls.result=z.build(b,hashlib.sha1(b).hexdigest());cls.after=c.readzip(cls.result)
        cls.models=[json.loads(cls.after[n]) for n in c.PATHS];cls.e=cls.models[0]['elements']
    def test_body_only_sirens_and_coplanar(self):
        self.assertEqual(set(self.before),set(self.after))
        for n in self.after:
            if n not in c.PATHS:self.assertEqual(self.before[n],self.after[n])
        self.assertEqual(self.result,z.build(self.orig,hashlib.sha1(self.orig).hexdigest()))
        for model in self.models:
            self.assertEqual(len(model['elements']),256);self.assertFalse(overlaps(model['elements']))
        for model in self.models[1:]:self.assertEqual(sum(a!=b for a,b in zip(self.e,model['elements'])),1)
    def test_backing_is_dark_and_fills_whole_opening(self):
        for x0,x1 in ((2.45,2.5),(13.5,13.55)):
            for z0,z1 in ((-11.65,-2.9),(19.,28.85)):
                self.assertIn(c.cube([x0,1.,z0],[x1,5.2,z1],'trim'),self.e)
        # Sample the entire inner face behind each wheel, including the
        # previously open ends. Ignore rotated pieces to make this conservative.
        for x in (2.475,13.525):
            for z0,z1 in ((-11.65,-2.3),(19.,28.85)):
                for i in range(94):
                    zz=z0+(z1-z0)*(i+.5)/94
                    for y in (1.8,2.5,3.5,4.5,5.1):
                        self.assertTrue(any('rotation' not in a and all(a['from'][k]-1e-8<=v<=a['to'][k]+1e-8 for k,v in enumerate((x,y,zz))) for a in self.e),f'backing gap x={x},y={y},z={zz}')
