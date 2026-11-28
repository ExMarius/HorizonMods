import json,subprocess,sys,tempfile,unittest
from pathlib import Path
BASE=Path(__file__).parent
class ModelTest(unittest.TestCase):
 def test_geometry_and_parts(self):
  with tempfile.TemporaryDirectory() as tmp:
   subprocess.run([sys.executable,str(BASE/'build_model.py'),tmp],check=True)
   body=json.loads((Path(tmp)/'body.json').read_text());wheel=json.loads((Path(tmp)/'wheel.json').read_text())
   self.assertGreaterEqual(len(body['elements']),60);self.assertGreaterEqual(len(wheel['elements']),10)
   for model in (body,wheel):
    for e in model['elements']:
     self.assertTrue(all(-16<=x<=32 for key in ('from','to') for x in e[key]));self.assertTrue(all(x<y for x,y in zip(e['from'],e['to'])))
     self.assertEqual(set(e['faces']),{'north','south','east','west','up','down'})
     self.assertTrue(all(f['texture'][1:] in model['textures'] for f in e['faces'].values()))
   self.assertTrue(any(x['name']=='roof' for x in body['elements']))
   self.assertTrue(any(x['name']=='steering hub' for x in body['elements']))
   self.assertTrue(any(x['name']=='tire central' for x in wheel['elements']))
if __name__=='__main__':unittest.main()
