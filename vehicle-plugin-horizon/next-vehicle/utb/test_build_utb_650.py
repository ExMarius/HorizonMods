import hashlib,io,json,unittest,zipfile
from pathlib import Path
import build_utb_650 as u
ROOT=Path(__file__).resolve().parents[3]
class UTBTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with zipfile.ZipFile(ROOT/'paper-vehicles/transfer/vehicle-reference/vehicle-fara-mentiune.zip') as z:
            cls.old=json.loads(z.read('vehicle/models/vehicle/tractor_body.json'))
    def test_model_retains_driving_layout_and_has_open_cab(self):
        m=u.model(self.old);self.assertGreater(len(m['elements']),80)
        self.assertEqual(m['elements'][0],self.old['elements'][0])
        self.assertEqual(m['textures']['color'],'minecraft:block/red_concrete')
        self.assertIn(u.box([.55,31.,-11.9],[15.45,32.,2.2],'utb_red'),m['elements'])
        self.assertIn(u.box([3.4,8.,28.05],[12.6,17.5,28.3],'utb_dark'),m['elements'])
        self.assertEqual(sum(1 for e in m['elements'] if any(f['texture']=='#utb_glass' for f in e['faces'].values())),6)
    def test_pack_additions_never_overwrite_existing(self):
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:
            z.writestr('pack.mcmeta',json.dumps({'pack':{'pack_format':46}}));z.writestr(u.BASE,json.dumps(self.old));z.writestr('dacia','unchanged')
        data=b.getvalue();out=u.build(data,hashlib.sha1(data).hexdigest())
        with zipfile.ZipFile(io.BytesIO(out)) as z:
            self.assertEqual(z.read('dacia'),b'unchanged');self.assertEqual(json.loads(z.read(u.BASE)),self.old)
            self.assertIn(u.ITEM,z.namelist());self.assertIn(u.BODY,z.namelist());self.assertIsNone(z.testzip())
        self.assertEqual(out,u.build(data,hashlib.sha1(data).hexdigest()))
        with self.assertRaises(ValueError):u.build(data)
