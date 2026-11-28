import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
BASE=Path(__file__).parent
class ConversionTest(unittest.TestCase):
 def test_conversion_is_deterministic_and_keeps_groups(self):
  with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
   for path in [a,b]:subprocess.run([sys.executable,str(BASE/'convert_glb.py'),path],check=True,stdout=subprocess.DEVNULL)
   names=['body','rear_left','front_left','rear_right','front_right'];all_names=[]
   for name in names:
    path=Path(a)/(name+'.json'); self.assertEqual(path.read_bytes(),(Path(b)/(name+'.json')).read_bytes())
    model=json.loads(path.read_text())
    for e in model['elements']:
     all_names.append(e['name']);self.assertTrue(e['faces'])
     for k in ('from','to'):
      self.assertTrue(all(-16<=v<=32 for v in e[k]))
     self.assertTrue(all(x<=y for x,y in zip(e['from'],e['to'])))
     for face in e['faces'].values():self.assertIn(face['texture'][1:],model['textures'])
     if 'rotation' in e:
      self.assertIn(e['rotation']['axis'],('x','y','z'));self.assertIn(e['rotation']['angle'],(-45,-22.5,22.5,45))
   self.assertEqual(len(all_names),280);self.assertEqual(len(set(all_names)),280)
   self.assertEqual(json.loads((Path(a)/'conversion-issues.json').read_text()),[])
 def test_source_is_unchanged(self):
  self.assertEqual(hashlib.sha256((BASE/'assets/source.glb').read_bytes()).hexdigest(),'33845ab8f06efd961a54f916c0d94cee13192ff375eb641d2a928b6d2b47443a')
if __name__=='__main__':unittest.main()
