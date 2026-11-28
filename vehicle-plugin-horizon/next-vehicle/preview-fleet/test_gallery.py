import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
ASSETS=ROOT/'content/assets/gokart'

class GalleryAssetsTest(unittest.TestCase):
    def test_project_models_and_textures_exist(self):
        for name in ('ambulance_body','smurd_body','fire_truck_body','wheel_standard'):
            with self.subTest(name=name):
                model=json.loads((ASSETS/'models/block'/f'{name}.json').read_text())
                self.assertTrue(model['elements'])
                for element in model['elements']:
                    for face in element['faces'].values():
                        self.assertIn(face['texture'][1:],model['textures'])
                for ref in model['textures'].values():
                    self.assertTrue(ref.startswith('gokart:block/'))
                    self.assertTrue((ASSETS/'textures/block'/(ref.split('/')[-1]+'.png')).is_file(),ref)
    def test_medical_models_include_windows_and_interior_material(self):
        for name in ('ambulance_body','smurd_body'):
            model=json.loads((ASSETS/'models/block'/f'{name}.json').read_text())
            self.assertIn('glass',model['textures'])
            self.assertIn('medical_mattress',model['textures'])

if __name__=='__main__': unittest.main()
