import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('compile_city_bus', ROOT / 'tools/compile_city_bus.py')
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)


class BusConverterTest(unittest.TestCase):
    def test_bus_pack_geometry_texture_and_license(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'city-bus.zip'
            descriptor = converter.build_zip(path)
            self.assertEqual(descriptor['body']['source_faces'], 379)
            self.assertEqual(descriptor['body']['skipped_degenerate_faces'], 32)
            self.assertEqual(descriptor['wheel']['source_faces'], 64)
            self.assertEqual(descriptor['wheel']['skipped_degenerate_faces'], 0)
            self.assertLessEqual(len(descriptor['body']['parts']), 40)
            self.assertLessEqual(len(descriptor['wheel']['parts']), 25)
            with zipfile.ZipFile(path) as archive:
                names = set(archive.namelist())
                self.assertIn('LICENSE-city-bus.txt', names)
                self.assertIn('city_bus_parts.json', names)
                self.assertEqual(json.loads(archive.read('pack.mcmeta'))['pack']['pack_format'], 46)
                for mesh in ('body', 'wheel'):
                    for part in descriptor[mesh]['parts']:
                        model = part['item_model'].split(':')[1]
                        self.assertIn('assets/horizonvehicles/items/' + model + '.json', names)
                        data = json.loads(archive.read('assets/horizonvehicles/models/item/' + model + '.json'))
                        for element in data['elements']:
                            self.assertTrue(all(-16 <= value <= 32 for value in element['from'] + element['to']))
                            for face in element['faces'].values():
                                texture = data['textures'][face['texture'][1:]].split('/')[-1]
                                self.assertIn('assets/horizonvehicles/textures/item/' + texture + '.png', names)
            second = Path(temp) / 'second.zip'
            converter.build_zip(second)
            self.assertEqual(path.read_bytes(), second.read_bytes())

if __name__ == '__main__':
    unittest.main()
