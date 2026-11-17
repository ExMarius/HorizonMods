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

    def test_glass_is_above_doors_and_clear_of_seats(self):
        def overlaps(a, b):
            return all(min(a['to'][i], b['to'][i]) - max(a['from'][i], b['from'][i]) > 0.001 for i in range(3))
        for name in CARS:
            model = json.loads((ROOT / f'assets/gokart/models/block/{name}_body.json').read_text())
            elements = model['elements']
            glass = [e for e in elements if e['faces']['up']['texture'] == '#glass']
            seats = [e for e in elements if e['faces']['up']['texture'] == '#seat']
            self.assertGreaterEqual(len(glass), 4, name)
            self.assertTrue(all(e['from'][1] > 10.2 for e in glass), name)
            for pane in glass:
                for seat in seats:
                    self.assertFalse(overlaps(pane, seat), name)

if __name__ == '__main__':
    unittest.main()
