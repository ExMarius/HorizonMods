import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class MinibusPrototype(unittest.TestCase):
    def test_model_has_bounded_emissive_lamps_and_four_cushions(self):
        model = json.loads((ROOT / 'content/assets/gokart/models/block/prototype_minibus_body.json').read_text())
        parts = model['elements']
        seats = [e for e in parts if e['faces']['up']['texture'] == '#seat'
                 and e['from'][1] == 4.46]
        self.assertEqual(len(seats), 4)
        lights = [e for e in parts if e['faces']['up']['texture'] in ('#headlight', '#taillight')]
        self.assertEqual(len(lights), 4)
        self.assertTrue(all(e.get('light_emission') == 15 for e in lights))
        self.assertTrue(all(-16 <= c <= 32 for e in parts for key in ('from','to') for c in e[key]))
        self.assertIn('gokart:block/medical_glass', model['textures'].values())

    def test_prototype_is_not_exposed_as_a_finished_vehicle(self):
        runtime = (ROOT / 'mixins/gokart_native/runtime.rs').read_text()
        tab = json.loads((ROOT / 'content/data/gokart/horizon/creative_tab/vehicles.json').read_text())
        self.assertNotIn('gokart:block/prototype_minibus_body', runtime)
        self.assertNotIn('gokart:minibus', tab['items'])
        self.assertFalse((ROOT / 'content/data/gokart/recipe/minibus.json').exists())

if __name__ == '__main__':
    unittest.main()
