import hashlib, io, json, unittest, zipfile
from pathlib import Path
import prepare_police,style_police,rebuild_police as r
ROOT=Path(__file__).resolve().parents[2]
def archive(files):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w') as z:
        for n,v in files.items():z.writestr(n,v)
    return b.getvalue()
class RebuildTest(unittest.TestCase):
    def test_targeted_rebuild(self):
        base=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}','assets/other/untouched':'original'})
        src=(ROOT/'paper-vehicles/transfer/vehicle-reference/vehicle-fara-mentiune.zip').read_bytes()
        initial=prepare_police.prepare(base,src,hashlib.sha1(base).hexdigest())
        styled=style_police.style(initial,hashlib.sha1(initial).hexdigest())
        result=r.rebuild(styled,hashlib.sha1(styled).hexdigest())
        self.assertEqual(result,r.rebuild(styled,hashlib.sha1(styled).hexdigest()))
        before=prepare_police.readzip(styled);out=prepare_police.readzip(result)
        changed={r.BODY, 'assets/daciapolice/models/item/body_flash_0.json','assets/daciapolice/models/item/body_flash_1.json'}
        for n,v in before.items():
            if n not in changed:self.assertEqual(v,out[n],n)
        old=json.loads(before[r.BODY]);new=json.loads(out[r.BODY]);removed=r.REAR_WINDOW_FILL | r.OLD_LIGHTBAR | r.OLD_POLICE_TEXT
        retained=[e for i,e in enumerate(old['elements'][:268]) if i not in removed]
        self.assertEqual(len(retained),216)
        for index,e in enumerate(old['elements'][:268]):
            if index in removed or index in r.SEATS:continue
            self.assertIn(e,new['elements'])
        for e in old['elements'][232:268]:self.assertNotIn(e,new['elements'])
        seats=[e for e in new['elements'] if e['faces'] and all(f['texture']=='#interior' for f in e['faces'].values())]
        self.assertEqual(len(seats),8)
        self.assertNotIn('#horizon_side',str(new['elements']));self.assertNotIn('#horizon_hood',str(new['elements']))
        for phase in (0,1):
            v=json.loads(out[f'assets/daciapolice/models/item/body_flash_{phase}.json'])
            self.assertEqual(len(v['elements']),len(new['elements']))
            changes=[i for i,(a,b) in enumerate(zip(new['elements'],v['elements'])) if a!=b]
            self.assertEqual(len(changes),1)
        with self.assertRaises(ValueError):r.rebuild(styled)
