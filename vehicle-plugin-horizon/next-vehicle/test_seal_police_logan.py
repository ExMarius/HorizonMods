import hashlib,json,unittest
import custom_logan_body as c,repair_logan_body as r,final_logan_body as f,polish_logan_body as p,refit_police_logan as q,finish_police_logan as t,detail_police_logan as d,complete_police_logan as u,restore_police_wheels as v,seal_police_logan as s
from test_repair_logan_body import archive,overlaps
class SealTest(unittest.TestCase):
    def setUp(self):
        b=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}',**{n:'{"credit":"source"}' for n in c.PATHS},'other':'unchanged'})
        for fn in (c.build,r.repair,f.build,p.build,q.build,t.build,d.build,u.build,v.build):b=fn(b,hashlib.sha1(b).hexdigest())
        self.orig=b;self.before=c.readzip(b);self.result=s.build(b,hashlib.sha1(b).hexdigest());self.after=c.readzip(self.result)
        self.models=[json.loads(self.after[n]) for n in c.PATHS];self.e=self.models[0]['elements']
    def test_only_body_changed_phases_and_no_coplanar_fighting(self):
        self.assertEqual(set(self.before),set(self.after))
        for n in self.after:
            if n not in c.PATHS:self.assertEqual(self.before[n],self.after[n])
        self.assertEqual(self.result,s.build(self.orig,hashlib.sha1(self.orig).hexdigest()))
        with self.assertRaises(ValueError):s.build(self.orig)
        for m in self.models:
            self.assertEqual(len(m['elements']),256)
            self.assertFalse(overlaps(m['elements']))
            self.assertTrue(all(-16<=x<=32 for a in m['elements'] for k in ('from','to') for x in a[k]))
        for m in self.models[1:]:self.assertEqual(sum(a!=b for a,b in zip(self.e,m['elements'])),1)
    def test_underside_has_no_seat_faces(self):
        self.assertIn(c.cube([4.1,-.18,-2.2],[11.9,-.08,4.4],'trim'),self.e)
        self.assertFalse([a for a in self.e if a['faces'].get('down',{}).get('texture')=='#seat'])
    def test_rear_backrest_and_armrests_touch_without_stacking(self):
        for x0,x1 in ((-.55,2.5),(13.5,16.55)):
            candidates=[a for a in self.e if a['from']==[x0,6.,-5.3] and a['to']==[x1,8.6,-3.9]]
            self.assertEqual(len(candidates),1)
            self.assertEqual(candidates[0]['faces']['north']['texture'],'#seat')
        for x0,x1 in ((2.45,2.5),(13.5,13.55)):
            candidates=[a for a in self.e if a['from']==[x0,1.,-10.8] and a['to']==[x1,5.2,-2.9]]
            self.assertEqual(len(candidates),1)
    def test_rear_roof_has_no_structural_holes(self):
        def covered(x,y,z):
            return any(all(a['from'][k]-1e-9<=v<=a['to'][k]+1e-9 for k,v in enumerate((x,y,z))) for a in self.e if 'rotation' not in a)
        for x0,x1 in ((-.65,2.5),(13.5,16.65)):
            for i in range(127):
                x=x0+(x1-x0)*(i+.5)/127
                for j in range(83):
                    z=-11.1+8.2*(j+.5)/83
                    self.assertTrue(covered(x,5.3,z),f'wheelhouse roof gap: x={x}, z={z}')
    def test_front_liners_attach_and_avoid_wheel_model_changes(self):
        for x0,x1 in ((-.65,2.45),(13.55,16.65)):
            self.assertIn(c.cube([x0,5.2,19.25],[x1,5.44,28.65],'trim'),self.e)
            for a,b in ((19.,19.25),(28.65,28.85)):
                self.assertIn(c.cube([x0,1.35,a],[x1,5.2,b],'trim'),self.e)
        for path in v.NEW:self.assertEqual(self.before[path],self.after[path])
