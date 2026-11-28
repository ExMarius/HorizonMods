import hashlib, io, json, unittest, zipfile
import pack

class CandidatePackTest(unittest.TestCase):
    def base(self, extra=None):
        b=io.BytesIO()
        with zipfile.ZipFile(b, 'w') as z:
            z.writestr('pack.mcmeta', json.dumps({'pack':{'pack_format':46}}))
            z.writestr('unchanged', b'original')
            if extra: z.writestr(extra, b'previous content')
        return b.getvalue()
    def test_additions_preserve_existing_and_have_valid_references(self):
        raw=self.base(); h=hashlib.sha1(raw).hexdigest()
        out=pack.build(raw,h)
        self.assertEqual(out,pack.build(raw,h))
        with zipfile.ZipFile(io.BytesIO(out)) as z:
            self.assertEqual(z.read('unchanged'), b'original')
            for part in pack.PARTS:
                name='gd32_'+part
                item=json.loads(z.read(f'assets/vehicle/items/{name}.json'))
                self.assertEqual(item['model']['model'],'vehicle:item/'+name)
                model=json.loads(z.read(f'assets/vehicle/models/item/{name}.json'))
                for ref in model['textures'].values():
                    namespace,path=ref.split(':')
                    self.assertIn(f'assets/{namespace}/textures/{path}.png',z.namelist())
    def test_wrong_hash_and_existing_model_are_rejected(self):
        raw=self.base()
        with self.assertRaises(ValueError): pack.build(raw,'0'*40)
        raw=self.base('assets/vehicle/models/item/gd32_body.json')
        with self.assertRaises(ValueError): pack.build(raw,hashlib.sha1(raw).hexdigest())

if __name__=='__main__': unittest.main()
