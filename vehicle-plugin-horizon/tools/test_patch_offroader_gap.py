import hashlib, importlib.util, io, json, unittest, zipfile
from pathlib import Path
p=Path(__file__).with_name('patch_offroader_gap.py');s=importlib.util.spec_from_file_location('gap',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def pack(entries):
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w') as z:
        for n,d in entries.items():z.writestr(n,d)
    return out.getvalue()
class GapTest(unittest.TestCase):
    def test_only_cowl_geometry_changes(self):
        model={'elements':[{'from':[-2.55,9.8,14.35],'to':[18.55,13.5,16.4],'faces':{'north':{'uv':[0,0,16,16]}}}, {'from':[0,0,0],'to':[1,1,1]}]}
        base=pack({m.PATH:json.dumps(model),'unchanged':'existing'})
        result=m.patch(base,hashlib.sha1(base).hexdigest());self.assertEqual(result,m.patch(base,hashlib.sha1(base).hexdigest()))
        with zipfile.ZipFile(io.BytesIO(result)) as z:
            after=json.loads(z.read(m.PATH)); self.assertEqual(z.read('unchanged'),b'existing')
            self.assertEqual(after['elements'][0]['to'],[18.55,13.5,17.25]);self.assertEqual(after['elements'][0]['faces'],model['elements'][0]['faces']);self.assertEqual(after['elements'][1],model['elements'][1])
    def test_refuses_wrong_pack_or_wrong_geometry(self):
        with self.assertRaises(ValueError):m.patch(b'invalid')
        base=pack({m.PATH:'{"elements":[]}'})
        with self.assertRaises(ValueError):m.patch(base,hashlib.sha1(base).hexdigest())
if __name__=='__main__':unittest.main()
