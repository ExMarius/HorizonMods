import copy
import importlib.util
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('off_roader_transfer', PAPER / 'tools/build_off_roader_transfer.py')
transfer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transfer)

class OffRoaderTransferTest(unittest.TestCase):
    def test_pack_retains_all_elements_and_rotation_data(self):
        with tempfile.TemporaryDirectory() as temp:
            first, second = Path(temp) / 'one.zip', Path(temp) / 'two.zip'
            desc = transfer.build(first)
            transfer.build(second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(first.read_bytes(), (PAPER / 'transfer/off-roader/horizon-off-roader-transfer.zip').read_bytes())
            with zipfile.ZipFile(first) as bundle:
                with zipfile.ZipFile(io.BytesIO(bundle.read('paper-resource-pack.zip'))) as pack:
                    self.assertEqual(json.loads(pack.read('pack.mcmeta'))['pack']['pack_format'], 46)
                    for name, groups in desc['parts'].items():
                        source = json.loads(bundle.read(f'source/models/{name}.json'))
                        expected = []
                        for element in source['elements']:
                            element = copy.deepcopy(element)
                            element.pop('light_emission', None)
                            expected.append(json.dumps(element, sort_keys=True))
                        actual = []
                        for group in groups:
                            model = group['item_model'].split(':')[1]
                            item = json.loads(pack.read(f'assets/horizonvehicles/items/{model}.json'))
                            self.assertEqual(item['model']['model'], f'horizonvehicles:item/{model}')
                            data = json.loads(pack.read(f'assets/horizonvehicles/models/item/{model}.json'))
                            for texture in data['textures'].values():
                                self.assertIn('assets/horizonvehicles/textures/item/' + texture.split('/')[-1] + '.png', pack.namelist())
                            for element in data['elements']:
                                self.assertTrue(all(-16 <= x <= 32 for field in ('from', 'to') for x in element[field]))
                                if group['rotation']:
                                    self.assertNotIn('rotation', element)
                                    element['rotation'] = group['rotation']
                                actual.append(json.dumps(element, sort_keys=True))
                        self.assertCountEqual(actual, expected)
            self.assertEqual(sum(g['element_count'] for g in desc['parts']['off_roader_body']), 197)

if __name__ == '__main__':
    unittest.main()
