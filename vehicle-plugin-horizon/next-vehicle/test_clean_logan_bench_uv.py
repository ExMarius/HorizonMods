import unittest
import custom_logan_body as c, repair_logan_body as r, final_logan_body as f, polish_logan_body as p, refit_police_logan as q, finish_police_logan as t, detail_police_logan as d, complete_police_logan as u, restore_police_wheels as v, seal_police_logan as s, close_logan_wheelwells as w, connect_logan_mirrors as m, clean_logan_bench_uv as clean

class BenchUVTest(unittest.TestCase):
    def test_only_seat_extension_uv_changes(self):
        for phase in (-1,0,1):
            before={'elements':c.body(phase),'textures':c.TEX}
            for fn in (r.repair_model,f.refine_model,p.polish,q.refit,t.finish,d.detail,u.complete,v.body,s.seal,w.close,m.connect):before=fn(before,phase)
            after=clean.clean(before)
            self.assertEqual(before['textures'],after['textures'])
            changed=0
            for a,b in zip(before['elements'],after['elements']):
                self.assertEqual(a['from'],b['from']);self.assertEqual(a['to'],b['to'])
                if a!=b:
                    changed+=1
                    self.assertLess(a['from'][2],0);self.assertNotIn(tuple(a['from']),clean.KEEP)
                    for face in b['faces'].values():
                        if face['texture']=='#seat':self.assertEqual(face['uv'],[3,0,13,16])
            self.assertEqual(changed,12)
