import hashlib, importlib.util, io, json, unittest, zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('dacia',HERE/'prepare_dacia.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
SOURCE=(ROOT/'paper-vehicles/transfer/vehicle-reference/vehicle-fara-mentiune.zip').read_bytes()
def archive(entries):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w') as z:
        for name,data in entries.items():z.writestr(name,data)
    return b.getvalue()
class TestDacia(unittest.TestCase):
    def setUp(self):
        self.base=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}','assets/vehicle/items/existing.json':'existing'})
        self.hash=hashlib.sha1(self.base).hexdigest()
    def test_original_geometry_and_textures_preserved(self):
        out=d.prepare(self.base,SOURCE,self.hash); self.assertEqual(out,d.prepare(self.base,SOURCE,self.hash))
        pack=d.readzip(out); source=d.readzip(SOURCE)
        for name,content in d.readzip(self.base).items(): self.assertEqual(pack[name],content)
        model=json.loads(source[d.MODEL]); result=json.loads(pack['assets/daciavehicle/models/item/dacia_logan_body.json'])
        self.assertEqual(result['elements'],model['elements']); self.assertEqual(result['credit'],model['credit'])
        for slot,ref in model['textures'].items():
            path=ref.split(':',1)[1]
            self.assertEqual(pack['assets/daciavehicle/textures/item/'+path.replace('/','_')+'.png'],source['vehicle/textures/'+path+'.png'])
        self.assertEqual(json.loads(pack['dacia-logan-source-layout.json']),json.loads(source[d.CONFIG]))
    def test_rejects_wrong_hash(self):
        with self.assertRaises(ValueError):d.prepare(self.base,SOURCE)
    def test_rejects_collision(self):
        b=archive({'pack.mcmeta':'{"pack":{"pack_format":46}}','assets/daciavehicle/items/dacia_logan_body.json':'existing'})
        with self.assertRaises(ValueError):d.prepare(b,SOURCE,hashlib.sha1(b).hexdigest())
if __name__=='__main__':unittest.main()
