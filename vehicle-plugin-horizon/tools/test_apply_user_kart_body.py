import hashlib,io,json,unittest,zipfile
import apply_user_kart_body as patch
class UserKartTest(unittest.TestCase):
    def test_only_four_models_change_to_user_geometry(self):
        old,_=patch.models(None);new,_=patch.models(patch.USER);out=io.BytesIO()
        with zipfile.ZipFile(out,'w') as z:
            for name,model in old.items():z.writestr(name,json.dumps(model))
            z.writestr('dacia','unchanged');z.writestr('pack.mcmeta','unchanged')
        data=out.getvalue();result=patch.build(data,hashlib.sha1(data).hexdigest())
        with zipfile.ZipFile(io.BytesIO(result)) as z:
            self.assertIsNone(z.testzip());self.assertEqual(z.read('dacia'),b'unchanged');self.assertEqual(z.read('pack.mcmeta'),b'unchanged')
            for name,model in new.items():self.assertEqual(json.loads(z.read(name)),model)
        self.assertEqual(result,patch.build(data,hashlib.sha1(data).hexdigest()))
        with self.assertRaises(ValueError):patch.build(data)
    def test_fails_before_install_if_old_model_was_changed(self):
        old,_=patch.models(None);first=next(iter(old));old[first]['elements'][0]['from'][0]+=1;out=io.BytesIO()
        with zipfile.ZipFile(out,'w') as z:
            for name,model in old.items():z.writestr(name,json.dumps(model))
        with self.assertRaises(ValueError):patch.build(out.getvalue(),hashlib.sha1(out.getvalue()).hexdigest())
