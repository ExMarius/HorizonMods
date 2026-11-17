import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'content/assets/gokart'

class MinibusPrototype(unittest.TestCase):
    def test_imported_model_and_texture_references(self):
        model = json.loads((ASSETS / 'models/block/prototype_minibus_body.json').read_text())
        self.assertEqual(model['loader'], 'neoforge:obj')
        self.assertTrue(model['flip_v'])
        self.assertEqual(model['model'], 'gokart:models/block/prototype_city_bus.obj')
        obj = (ASSETS / 'models/block/prototype_city_bus.obj').read_text()
        self.assertIn('mtllib prototype_city_bus.mtl', obj)
        self.assertIn('usemtl bus', obj)
        self.assertGreater(sum(line.startswith('f ') for line in obj.splitlines()), 100)
        self.assertEqual((ASSETS / 'textures/block/prototype_city_bus.png').read_bytes(),
                         (ROOT / 'third_party/city_vehicles/yellow_bus.png').read_bytes())

    def test_prototype_is_not_exposed_as_a_finished_vehicle(self):
        runtime = (ROOT / 'mixins/gokart_native/runtime.rs').read_text()
        tab = json.loads((ROOT / 'content/data/gokart/horizon/creative_tab/vehicles.json').read_text())
        self.assertNotIn('gokart:block/prototype_minibus_body', runtime)
        self.assertNotIn('gokart:minibus', tab['items'])
        self.assertFalse((ROOT / 'content/data/gokart/recipe/minibus.json').exists())

if __name__ == '__main__':
    unittest.main()
