import hashlib,io,json,unittest,zipfile
from pathlib import Path
import custom_logan_body as c,repair_logan_body as r
ROOT=Path(__file__).resolve().parents[2]
def archive(files):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w') as z:
        for n,v in files.items():z.writestr(n,v)
    return b.getvalue()
def overlaps(elements):
    hits=[]
    for i,a in enumerate(elements):
        if 'rotation' in a:continue
        for b in elements[:i]:
            if 'rotation' in b:continue
            for ax in range(3):
                for side in ('from','to'):
                    if a[side][ax]==b[side][ax] and all(min(a['to'][k],b['to'][k])-max(a['from'][k],b['from'][k])>.03 for k in range(3) if k!=ax):hits.append((a,b,ax,side))
    return hits
class BodyRepairTest(unittest.TestCase):
    def setUp(self):
        self.base=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}',**{n:'{"credit":"source"}' for n in c.PATHS},'assets/other/other.json':'unchanged'})
        self.before=c.build(self.base,hashlib.sha1(self.base).hexdigest())
        self.result=r.repair(self.before,hashlib.sha1(self.before).hexdigest())
    def test_no_other_resources_changed_or_lost(self):
        before=c.readzip(self.before);after=c.readzip(self.result)
        self.assertEqual(set(before),set(after))
        for n in before:
            if n not in c.PATHS:self.assertEqual(before[n],after[n],n)
        self.assertEqual(self.result,r.repair(self.before,hashlib.sha1(self.before).hexdigest()))
        with self.assertRaises(ValueError):r.repair(self.before)
    def test_front_seats_match_horizon_size_and_source_anchors(self):
        model=json.loads(c.readzip(self.result)[c.MODEL]);e=model['elements']
        horizon=json.loads((ROOT/'content/assets/gokart/models/block/off_roader_body.json').read_text())
        cushion=horizon['elements'][189];back=horizon['elements'][190]
        for lo,hi,driver_x in ((1.27,6.73,4.0),(9.27,14.73,12.0)):
            seat=c.cube([lo,1.7,5.8],[hi,2.85,11.15],'seat');self.assertIn(seat,e)
            self.assertGreaterEqual(seat['from'][2],5.5)
            self.assertLess(lo,driver_x);self.assertGreater(hi,driver_x)
            self.assertLess(seat['from'][2],7.5);self.assertGreater(seat['to'][2],7.5)
            self.assertAlmostEqual((hi-lo)*1.7,(cushion['to'][0]-cushion['from'][0])*1.42,delta=.025)
            self.assertAlmostEqual((11.15-5.8)*1.7,(cushion['to'][2]-cushion['from'][2])*1.42,delta=.025)
            self.assertAlmostEqual((10.22-2.85)*1.7,(back['to'][1]-back['from'][1])*1.38,delta=.03)
            self.assertIn(c.cube([lo,2.85,5.55],[hi,10.22,6.8],'seat'),e)
    def test_floor_hood_siren_and_coplanar_regression(self):
        models=[json.loads(c.readzip(self.result)[n]) for n in c.PATHS]
        e=models[0]['elements'];self.assertIn(c.cube([-.65,1.35,-8.3],[16.65,1.7,17.35],'trim'),e)
        self.assertIn(c.cube([-.65,8.4,17.15],[16.65,9.0,25.05],'body'),e)
        for z0,z1,top in ((25.05,26.55,8.95),(26.55,28.05,8.80),(28.05,29.55,8.65),(29.55,31.04,8.50)):
            self.assertIn(c.cube([-.65,8.37,z0],[16.65,top,z1],'body'),e)
        self.assertGreater(len(overlaps(c.body(-1))),20)
        self.assertEqual(overlaps(e),[])
        for m in models[1:]:
            self.assertEqual(len(e),len(m['elements']))
            self.assertEqual(sum(a!=b for a,b in zip(e,m['elements'])),1)
