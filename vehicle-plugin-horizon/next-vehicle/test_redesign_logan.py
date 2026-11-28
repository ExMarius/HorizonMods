import hashlib,io,json,unittest,zipfile
from pathlib import Path
import prepare_police as p, style_police as s, rebuild_police as r, redesign_logan as d
ROOT=Path(__file__).resolve().parents[2]
def archive(files):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w') as z:
        for n,v in files.items():z.writestr(n,v)
    return b.getvalue()
class RedesignTest(unittest.TestCase):
    def test_rebuild_preserves_other_resources_and_siren(self):
        base=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}','assets/other':'unchanged'})
        source=(ROOT/'paper-vehicles/transfer/vehicle-reference/vehicle-fara-mentiune.zip').read_bytes()
        def run(fn,data,*args):return fn(data,*args,hashlib.sha1(data).hexdigest())
        previous=run(p.prepare,base,source);previous=run(s.style,previous);previous=run(r.rebuild,previous)
        result=run(d.redesign,previous);self.assertEqual(result,run(d.redesign,previous))
        old=p.readzip(previous);new=p.readzip(result)
        changed={d.BODY,'assets/daciapolice/models/item/body_flash_0.json','assets/daciapolice/models/item/body_flash_1.json','assets/daciapolice/textures/item/logan_livery.png'}
        for name,data in old.items():
            if name not in changed:self.assertEqual(data,new[name],name)
        body=json.loads(new[d.BODY]);self.assertTrue(body['elements'])
        for e in body['elements']:
            for coord in ('from','to'):self.assertTrue(all(-16<=v<=32 for v in e[coord]))
        seats=[e for e in body['elements'] if e['faces'] and all(f['texture']=='#interior' for f in e['faces'].values())]
        self.assertEqual(len(seats),8)
        self.assertGreaterEqual(len(d.REPLACED),100)
        for i in (0,1):
            flash=json.loads(new[f'assets/daciapolice/models/item/body_flash_{i}.json'])
            self.assertEqual(len(flash['elements']),len(body['elements']))
            self.assertEqual(sum(a!=b for a,b in zip(body['elements'],flash['elements'])),1)
        self.assertIn('assets/daciapolice/sounds/sirena_mono.ogg',new)
        with self.assertRaises(ValueError):d.redesign(previous)
