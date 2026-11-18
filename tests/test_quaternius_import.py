import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'content/assets/gokart'

class QuaterniusImport(unittest.TestCase):
    def test_source_hash_and_mesh_materials(self):
        glb = ROOT / 'third_party/quaternius/sports_car.glb'
        self.assertEqual(hashlib.sha256(glb.read_bytes()).hexdigest(),
                         'bbb1c718d2aaf5f4344e9fb2cd66d8332a998a515b09ddd4dfa14698d787124e')
        lines = (ASSETS / 'models/block/quaternius_sport.obj').read_text().splitlines()
        self.assertEqual(sum(line.startswith('f ') for line in lines), 1468)
        self.assertGreater(sum(line.startswith('v ') for line in lines), 2000)
        self.assertEqual({line.split()[1] for line in lines if line.startswith('usemtl ')},
                         {'white', 'windows', 'grey', 'headlights', 'taillights'})
        self.assertNotIn('wheel', ' '.join(line for line in lines if line.startswith('o ')).lower())

    def test_each_paint_variant_resolves_shared_mesh_and_textures(self):
        for i in range(16):
            model = json.loads((ASSETS / f'models/block/supercar_mesh_{i:02}.json').read_text())
            self.assertEqual(model['loader'], 'neoforge:obj')
            self.assertEqual(model['model'], 'gokart:models/block/quaternius_sport.obj')
            self.assertEqual(model['textures']['white'], f'gokart:block/sport_paint_{i:02}')
            for texture in model['textures'].values():
                path = texture.removeprefix('gokart:')
                self.assertTrue((ASSETS / f'textures/{path}.png').is_file(), texture)
        mtl = (ASSETS / 'models/block/quaternius_sport.mtl').read_text()
        for name in ('white', 'windows', 'grey', 'headlights', 'taillights'):
            self.assertIn(f'newmtl {name}\nmap_Kd #{name}\n', mtl)

if __name__ == '__main__':
    unittest.main()
