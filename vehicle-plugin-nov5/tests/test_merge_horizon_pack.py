import hashlib
import importlib.util
import io
import json
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('merge_pack', ROOT / 'vehicle-plugin-nov5/tools/merge_horizon_pack.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
TRANSFER = ROOT / 'paper-vehicles/transfer/off-roader/horizon-off-roader-transfer.zip'

def archive(entries):
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w') as z:
        for k, v in entries.items(): z.writestr(k, v)
    return b.getvalue()

class MergeTest(unittest.TestCase):
    def setUp(self):
        self.base = archive({'pack.mcmeta': json.dumps({'pack': {'pack_format': 46, 'description': 'original'}}),
                             'assets/vehicle/items/off_roader.json': 'original', 'LICENSE.txt': 'original license'})
        self.sha = hashlib.sha256(self.base).hexdigest()
        self.transfer = TRANSFER.read_bytes()

    def test_preserves_every_base_entry_and_adds_horizon_namespace(self):
        out = m.merge(self.base, self.transfer, self.sha)
        self.assertEqual(out, m.merge(self.base, self.transfer, self.sha))
        result = m.files(out)
        for name, data in m.files(self.base).items(): self.assertEqual(result[name], data)
        self.assertIn('assets/horizonvehicles/items/off_roader_body_part_00.json', result)
        self.assertIn('horizon-off-roader-LICENSE.txt', result)
        body = json.loads(result['assets/horizonvehicles/models/item/off_roader_body_part_00.json'])
        self.assertTrue(all(face['tintindex'] == 0 for element in body['elements'] for face in element['faces'].values()))
        item = json.loads(result['assets/horizonvehicles/items/off_roader_body_part_00.json'])
        self.assertEqual(item['model']['tints'][0]['type'], 'minecraft:dye')
        wheel = json.loads(result['assets/horizonvehicles/models/item/wheel_sports_part_00.json'])
        self.assertTrue(all('tintindex' not in face for e in wheel['elements'] for face in e['faces'].values()))

    def test_refuses_unexpected_base(self):
        with self.assertRaises(ValueError): m.merge(self.base, self.transfer)

    def test_refuses_conflicting_asset(self):
        files = m.files(self.base)
        files['assets/horizonvehicles/items/off_roader_body_part_00.json'] = b'existing'
        base = archive(files)
        with self.assertRaises(ValueError): m.merge(base, self.transfer, hashlib.sha256(base).hexdigest())

    def test_refuses_non_1214(self):
        base = archive({'pack.mcmeta': '{"pack":{"pack_format": 75}}'})
        with self.assertRaises(ValueError): m.merge(base, self.transfer, hashlib.sha256(base).hexdigest())

if __name__ == '__main__': unittest.main()
