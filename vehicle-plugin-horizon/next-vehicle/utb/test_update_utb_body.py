import hashlib,io,json,unittest,zipfile
import update_utb_body as u

class UpdateUTBTest(unittest.TestCase):
    def test_authored_model_and_layout(self):
        m=json.loads(u.MODEL.read_text());u.validate(m)
        parts={e['name']:e for e in m['elements']}
        self.assertEqual(len(parts),len(m['elements']))
        for name in ('roof','left rear fender','right rear fender','grille dark face','left lamp lens','right lamp lens','seat cushion','exhaust pipe'):
            self.assertIn(name,parts)
        # World coordinates restored by scale correction around model origin 8.
        actual=lambda value:8+2*(value-8)
        self.assertGreater(actual(parts['roof']['from'][1]),39)
        self.assertGreater(actual(parts['left rear fender']['from'][1]),20)
        self.assertLess(actual(parts['seat cushion']['to'][1]),16)
        self.assertFalse(any('glass' in name for name in parts))
    def test_only_body_changes(self):
        old=io.BytesIO()
        with zipfile.ZipFile(old,'w') as z:
            z.writestr('pack.mcmeta',json.dumps({'pack':{'pack_format':46}}));z.writestr(u.BODY,'old');z.writestr('vehicles/other','unchanged')
        data=old.getvalue();expected=hashlib.sha1(data).hexdigest();result=u.build(data,expected)
        with zipfile.ZipFile(io.BytesIO(result)) as z:
            self.assertEqual(z.read('vehicles/other'),b'unchanged');self.assertEqual(json.loads(z.read(u.BODY)),json.loads(u.MODEL.read_text()))
        self.assertEqual(result,u.build(data,expected))
        with self.assertRaises(ValueError):u.build(data)
