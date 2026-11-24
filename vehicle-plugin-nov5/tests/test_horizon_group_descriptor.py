import io
import json
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class DescriptorTest(unittest.TestCase):
    def test_descriptor_matches_transfer_and_all_groups_have_models(self):
        transfer = ROOT / 'paper-vehicles/transfer/off-roader/horizon-off-roader-transfer.zip'
        descriptor = ROOT / 'vehicle-plugin-horizon/paper-plugin/src/main/resources/horizon/off_roader_parts.json'
        with zipfile.ZipFile(transfer) as outer:
            with zipfile.ZipFile(io.BytesIO(outer.read('paper-resource-pack.zip'))) as pack:
                self.assertEqual(json.loads(descriptor.read_bytes()), json.loads(pack.read('go_kart_parts.json')))
                groups = json.loads(descriptor.read_bytes())['parts']
                self.assertEqual(sum(g['element_count'] for g in groups['off_roader_body']), 197)
                # The mechanic switches between these two grouped wheel models
                # without respawning displays; their pivots must be identical.
                for a, b in zip(groups['wheel_standard'], groups['wheel_sports'], strict=True):
                    self.assertEqual(a['rotation'], b['rotation'])
                for part in groups.values():
                    for group in part:
                        namespace, name = group['item_model'].split(':')
                        self.assertIn(f'assets/{namespace}/items/{name}.json', pack.namelist())
                        self.assertIn(f'assets/{namespace}/models/item/{name}.json', pack.namelist())
                        if group['rotation'] is not None:
                            self.assertIn(group['rotation']['axis'], ('x', 'y', 'z'))
                            self.assertEqual(len(group['rotation']['origin']), 3)

if __name__ == '__main__': unittest.main()
