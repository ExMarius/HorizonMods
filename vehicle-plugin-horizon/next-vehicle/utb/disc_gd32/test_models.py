import json,subprocess,sys,tempfile,unittest
from pathlib import Path
BASE=Path(__file__).parent
class ModelTests(unittest.TestCase):
 def test_all_parts_use_valid_vanilla_bounds_and_rotations(self):
  with tempfile.TemporaryDirectory() as tmp:
   subprocess.run([sys.executable,str(BASE/'build_models.py'),tmp],check=True,stdout=subprocess.DEVNULL)
   for name in ('body','gang_frame','gang_front','gang_rear','wheel','axle','jack'):
    model=json.loads((Path(tmp)/f'gd32_{name}.json').read_text());self.assertTrue(model['elements'])
    for e in model['elements']:
     self.assertTrue(all(-16<=a<b<=32 for a,b in zip(e['from'],e['to'])),e['name'])
     if 'rotation' in e:
      self.assertIn(e['rotation']['axis'],('x','y','z'));self.assertIn(e['rotation']['angle'],(-45,-22.5,0,22.5,45));self.assertTrue(all(-16<=v<=32 for v in e['rotation']['origin']))
     self.assertEqual(set(e['faces']),{'up','down','north','south','east','west'})
     for face in e['faces'].values():self.assertIn(face['texture'][1:],model['textures'])
   for name in ('gang_front','gang_rear'):
    m=json.loads((Path(tmp)/f'gd32_{name}.json').read_text());self.assertEqual(len([e for e in m['elements'] if e['name'].startswith('disc_')]),32)
if __name__=='__main__':unittest.main()
