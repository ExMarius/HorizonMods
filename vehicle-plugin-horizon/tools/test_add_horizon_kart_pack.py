import hashlib,io,json,unittest,zipfile
import add_horizon_kart_pack as kart
class KartPackTest(unittest.TestCase):
    def test_additions_preserve_all_existing_pack_entries(self):
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:z.writestr('pack.mcmeta','original');z.writestr('assets/daciapolice/models/item/body.json','do not touch')
        data=b.getvalue();out=kart.build(data,hashlib.sha1(data).hexdigest())
        with zipfile.ZipFile(io.BytesIO(out)) as z:
            self.assertEqual(z.read('pack.mcmeta'),b'original')
            self.assertEqual(z.read('assets/daciapolice/models/item/body.json'),b'do not touch')
            self.assertIsNone(z.testzip())
            for name in kart.PARTS:
                self.assertIn('assets/horizonvehicles/models/item/'+name+'_part_00.json',z.namelist())
        self.assertEqual(kart.build(data,hashlib.sha1(data).hexdigest()),out)
        with self.assertRaises(ValueError):kart.build(data)
    def test_refuses_to_overwrite_other_assets(self):
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:z.writestr('assets/horizonvehicles/models/item/go_kart_body_part_00.json','different')
        with self.assertRaises(ValueError):kart.build(b.getvalue(),hashlib.sha1(b.getvalue()).hexdigest())
