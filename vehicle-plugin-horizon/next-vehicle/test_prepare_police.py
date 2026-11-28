import hashlib, importlib.util, io, json, unittest, zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('police',HERE/'prepare_police.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
SOURCE=(ROOT/'paper-vehicles/transfer/vehicle-reference/vehicle-fara-mentiune.zip').read_bytes()
def archive(d):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w') as z:
        for n,v in d.items():z.writestr(n,v)
    return b.getvalue()
class PolicePackTest(unittest.TestCase):
    def setUp(self):
        self.base=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}','assets/vehicle/items/existing.json':'unchanged'});self.sha=hashlib.sha1(self.base).hexdigest()
    def test_source_preserved_and_all_tints_resolve(self):
        result=m.prepare(self.base,SOURCE,self.sha);self.assertEqual(result,m.prepare(self.base,SOURCE,self.sha))
        out=m.readzip(result);src=m.readzip(SOURCE);model=json.loads(src[m.MODEL]);actual=json.loads(out['assets/daciapolice/models/item/body.json'])
        self.assertEqual(actual['elements'],model['elements']);self.assertEqual(actual['credit'],model['credit'])
        for slot,ref in model['textures'].items():
            name=ref.split(':',1)[1]
            self.assertEqual(out['assets/daciapolice/textures/item/'+name.replace('/','_')+'.png'],src['vehicle/textures/'+name+'.png'])
        self.assertEqual(out['assets/daciapolice/sounds/sirena_mono.ogg'],src[m.SOUND])
        item=json.loads(out['assets/daciapolice/items/body.json'])
        self.assertGreater(len(item['model']['tints']),max(f.get('tintindex',-1) for e in model['elements'] for f in e['faces'].values()))
        self.assertEqual(json.loads(out['dacia-logan-police-source-layout.json']),json.loads(src[m.CONFIG]))
        for n,v in m.readzip(self.base).items():self.assertEqual(out[n],v)
    def test_refuses_collision(self):
        b=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}','assets/daciapolice/items/body.json':'existing'})
        with self.assertRaises(ValueError):m.prepare(b,SOURCE,hashlib.sha1(b).hexdigest())
    def test_refuses_wrong_base(self):
        with self.assertRaises(ValueError):m.prepare(self.base,SOURCE)
if __name__=='__main__':unittest.main()
