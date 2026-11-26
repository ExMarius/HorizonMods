import json, struct, unittest
from pathlib import Path
ROOT=Path(__file__).parent

class GalleryAssetsTest(unittest.TestCase):
    def test_real_gltf_models_reference_included_texture(self):
        for name in ('ambulance','firetruck','garbage-truck'):
            with self.subTest(name=name):
                data=(ROOT/'assets'/f'{name}.glb').read_bytes()
                magic,version,length=struct.unpack_from('<4sII',data)
                self.assertEqual((magic,version,length),(b'glTF',2,len(data)))
                size,kind=struct.unpack_from('<I4s',data,12)
                self.assertEqual(kind,b'JSON')
                scene=json.loads(data[20:20+size])
                self.assertTrue(scene['meshes'])
                for image in scene.get('images',[]):
                    if 'uri' in image: self.assertTrue((ROOT/'assets'/image['uri']).is_file())
    def test_license_included(self):
        text=(ROOT/'assets/License.txt').read_text()
        self.assertIn('Kenney',text)
        self.assertIn('CC0',text)

if __name__=='__main__': unittest.main()
