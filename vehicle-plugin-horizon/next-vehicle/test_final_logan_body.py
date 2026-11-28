import hashlib,json,unittest
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f
from test_repair_logan_body import archive,overlaps
class FinalLoganTest(unittest.TestCase):
    def setUp(self):
        b=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}',**{n:'{"credit":"source"}' for n in c.PATHS},'other':'unchanged'})
        b=c.build(b,hashlib.sha1(b).hexdigest());self.old=r.repair(b,hashlib.sha1(b).hexdigest())
        self.new=f.build(self.old,hashlib.sha1(self.old).hexdigest())
        self.before=c.readzip(self.old);self.after=c.readzip(self.new)
        self.e=json.loads(self.after[c.MODEL])['elements']
    def test_only_three_models_modified_and_deterministic(self):
        self.assertEqual(set(self.before),set(self.after))
        for n in self.before:
            if n not in c.PATHS:self.assertEqual(self.before[n],self.after[n],n)
        self.assertEqual(self.new,f.build(self.old,hashlib.sha1(self.old).hexdigest()))
        with self.assertRaises(ValueError):f.build(self.old)
    def test_seats_and_floor(self):
        self.assertIn(c.cube([.55,1.7,-3.9],[15.45,3.7,1.5],'seat'),self.e)
        self.assertIn(c.cube([.58,3.7,-5.3],[15.42,8.6,-3.9],'seat'),self.e)
        self.assertIn(c.cube([-.65,1.35,-8.3],[16.65,1.7,17.35],'trim'),self.e)
        for lo,hi in ((1.27,6.73),(9.27,14.73)):
            self.assertIn(c.cube([lo,1.7,5.05],[hi,2.85,10.4],'seat'),self.e)
            self.assertIn(c.cube([lo,2.85,4.8],[hi,10.22,6.05],'seat'),self.e)
        self.assertIn(c.cube([.5,6,14.8],[15.5,8.45,17.7],'dash'),self.e)
        self.assertIn(c.cube([.35,1.7,13.5],[15.65,1.82,17.8],'dash'),self.e)
    def test_wheel_arch_unchanged_nose_shorter_and_no_coplanar_faces(self):
        old=json.loads(self.before[c.MODEL])['elements']
        # The four wheel-arch surrounds remain byte-for-byte unchanged.
        for x0,x1 in ((-1.86,-1.8),(17.8,17.86)):
            for z in (-6.95,23.95):
                for z0,z1,y0,y1 in ((z-2.2,z+2.2,5.18,5.48),(z-4.88,z-4.62,1.55,3.4),(z+4.62,z+4.88,1.55,3.4)):
                    e=c.cube([x0,y0,z0],[x1,y1,z1],'trim');self.assertIn(e,old);self.assertIn(e,self.e)
        self.assertIn(c.cube([-.65,8.37,29.27],[16.65,8.5,30.164],'body'),self.e)
        self.assertFalse(overlaps(self.e))
    def test_all_siren_phases_and_antenna(self):
        models=[json.loads(self.after[n]) for n in c.PATHS]
        antenna=c.cube([7.87,16.15,-1.8],[8.13,18.4,-1.54],'trim',{'axis':'x','angle':-22.5,'origin':[8,16.15,-1.7]})
        for model in models:self.assertIn(antenna,model['elements'])
        for m in models[1:]:self.assertEqual(sum(a!=b for a,b in zip(models[0]['elements'],m['elements'])),1)
