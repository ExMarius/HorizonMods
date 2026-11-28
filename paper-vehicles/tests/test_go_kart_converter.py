import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]
ROOT = PAPER.parent
spec = importlib.util.spec_from_file_location('compile_go_kart', PAPER / 'tools/compile_go_kart.py')
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)


class GoKartConversion(unittest.TestCase):
    def test_all_source_cuboids_and_rotations_are_retained(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'kart.zip'
            result = converter.build_zip(path)
            with zipfile.ZipFile(path) as archive:
                names = set(archive.namelist())
                self.assertEqual(json.loads(archive.read('pack.mcmeta'))['pack']['pack_format'], 46)
                self.assertIn('LICENSE.txt', names)
                for name, parts in result['parts'].items():
                    source = json.loads((ROOT / 'content/assets/gokart/models/block' / (name + '.json')).read_text())
                    self.assertEqual(sum(p['element_count'] for p in parts), len(source['elements']))
                    expected_rotations = sorted((e['rotation']['axis'], e['rotation']['angle'], tuple(e['rotation']['origin']))
                        for e in source['elements'] if 'rotation' in e and e['rotation']['angle'] not in converter.LEGAL)
                    found_rotations = []
                    for part in parts:
                        model = part['item_model'].split(':')[1]
                        item = json.loads(archive.read('assets/horizonvehicles/items/' + model + '.json'))
                        self.assertEqual(item['model']['model'], 'horizonvehicles:item/' + model)
                        data = json.loads(archive.read('assets/horizonvehicles/models/item/' + model + '.json'))
                        self.assertEqual(len(data['elements']), part['element_count'])
                        for element in data['elements']:
                            self.assertTrue(all(-16 <= x <= 32 for field in ('from', 'to') for x in element[field]))
                            if 'rotation' in element:
                                self.assertIn(element['rotation']['angle'], converter.LEGAL)
                        if part['rotation']:
                            r = part['rotation']
                            found_rotations.extend([(r['axis'], r['angle'], tuple(r['origin']))] * part['element_count'])
                        for texture in data['textures'].values():
                            self.assertIn('assets/horizonvehicles/textures/item/' + texture.split('/')[-1] + '.png', names)
                    self.assertEqual(found_rotations and sorted(found_rotations), expected_rotations)
            second = Path(temp) / 'second.zip'
            converter.build_zip(second)
            self.assertEqual(path.read_bytes(), second.read_bytes())
            self.assertEqual(path.read_bytes(), (PAPER / 'public/go-kart.zip').read_bytes())

if __name__ == '__main__':
    unittest.main()
