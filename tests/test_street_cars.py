import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'content'
CARS = ('street_coupe', 'muscle_car', 'supercar', 'city_suv', 'taxi')

class StreetCars(unittest.TestCase):
    def test_assets_and_recipes(self):
        creative = json.loads((ROOT / 'data/gokart/horizon/creative_tab/vehicles.json').read_text())
        for name in CARS:
            with self.subTest(name=name):
                self.assertIn('gokart:' + name, creative['items'])
                model = json.loads((ROOT / f'assets/gokart/models/block/{name}_body.json').read_text())
                self.assertGreater(len(model['elements']), 25)
                self.assertNotIn('siren_red', model['textures'])
                recipe = json.loads((ROOT / f'data/gokart/recipe/{name}.json').read_text())
                self.assertEqual(recipe['result']['id'], 'gokart:' + name)
                self.assertTrue((ROOT / f'assets/gokart/textures/item/{name}.png').is_file())
                for lang in ('en_us', 'ro_ro'):
                    translations = json.loads((ROOT / f'assets/gokart/lang/{lang}.json').read_text())
                    self.assertIn('item.gokart.' + name, translations)

if __name__ == '__main__':
    unittest.main()
