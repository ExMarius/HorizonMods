import hashlib,io,json,unittest,zipfile
from pathlib import Path
import prepare_police as p,style_police as s,rebuild_police as r,redesign_logan as d,custom_logan_body as c
ROOT=Path(__file__).resolve().parents[2]
def archive(files):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w') as z:
        for n,v in files.items():z.writestr(n,v)
    return b.getvalue()
class CustomBodyTest(unittest.TestCase):
    def makebase(self):
        base=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}','assets/other':'unchanged'})
        source=(ROOT/'paper-vehicles/transfer/vehicle-reference/vehicle-fara-mentiune.zip').read_bytes()
        def run(fn,data,*args):return fn(data,*args,hashlib.sha1(data).hexdigest())
        x=run(p.prepare,base,source);x=run(s.style,x);x=run(r.rebuild,x);return run(d.redesign,x)
    def test_body_preserves_pack_and_supports_siren(self):
        base=self.makebase(); result=c.build(base,hashlib.sha1(base).hexdigest());self.assertEqual(result,c.build(base,hashlib.sha1(base).hexdigest()))
        before=p.readzip(base);after=p.readzip(result)
        for name,data in before.items():
            if name not in c.PATHS:self.assertEqual(data,after[name],name)
        model=json.loads(after[c.MODEL]);e=model['elements']
        self.assertNotEqual(e,json.loads(before[c.MODEL])['elements'])
        self.assertGreater(len(e),100)
        for part in e:
            for key in ('from','to'):self.assertTrue(all(-16<=v<=32 for v in part[key]))
            for face in part['faces'].values():self.assertIn(face['texture'][1:],model['textures'])
        for name in model['textures'].values():
            namespace,ref=name.split(':');self.assertIn('assets/'+namespace+'/textures/'+ref+'.png',after)
        for i in (0,1):
            flash=json.loads(after[c.PATHS[i+1]]);self.assertEqual(len(e),len(flash['elements']))
            self.assertEqual(sum(a!=b for a,b in zip(e,flash['elements'])),1)
        with self.assertRaises(ValueError):c.build(base)
    def test_seats_windows_footwell_and_wheel_openings(self):
        e=c.body(-1)
        def has(lo,hi,texture):
            return any(x['from']==lo and x['to']==hi and all(f['texture']=='#'+texture for f in x['faces'].values()) for x in e)
        # Driver and passenger cushions are independent, centered on source x=12 and x=4.
        self.assertTrue(has([2.0,2.0,4.8],[6.6,3.75,10.2],'seat'))
        self.assertTrue(has([9.4,2.0,4.8],[14.0,3.75,10.2],'seat'))
        self.assertTrue(has([7.72,2.4,10.3],[8.28,4.1,10.9],'chrome'))
        for x in (10.1,11.35,12.6):
            self.assertTrue(any(q['from'][0]==x and q['from'][2]==13.4 and all(f['texture']=='#trim' for f in q['faces'].values()) for q in e))
        # At mid-height, no solid side-wall cuboid can occupy either open side window.
        for side in (-1.0,17.0):
            for z in (2.0,9.0):
                self.assertFalse(any('rotation' not in q and q['from'][0]<side<q['to'][0] and q['from'][1]<12<q['to'][1] and q['from'][2]<z<q['to'][2] for q in e))
        # At wheel centre height, no unrotated side panel fills either wheel centre.
        for side in (-1.4,17.4):
            for z in (-6.95,23.95):
                self.assertFalse(any('rotation' not in q and q['from'][0]<side<q['to'][0] and q['from'][1]<3<q['to'][1] and q['from'][2]<z<q['to'][2] for q in e))
