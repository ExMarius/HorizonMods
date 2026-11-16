"""Geometry and texture regressions for the emergency vans."""
import json
import unittest
from pathlib import Path

from test_wheel_arch_coverage import covers_side

ROOT = Path(__file__).resolve().parents[1]


class EmergencyModels(unittest.TestCase):
    def test_body_panels_cover_arch_backing_without_protruding_above_hood(self):
        for name in ('ambulance', 'smurd'):
            model = json.loads((ROOT / f'content/assets/gokart/models/block/{name}_body.json').read_text())
            elements = model['elements']
            # In the front wheel zone, the hood edge must be continuous and flat.
            for zstep in range(95, 215):
                z = zstep / 10
                for side in (-1, 1):
                    self.assertTrue(any(covers_side(e, side * 12.20, 11.70, z) for e in elements), (name, z))
                    self.assertFalse(any(covers_side(e, side * 12.20, 11.90, z) for e in elements), (name, z))

    def test_emergency_markings_and_opposite_side_uvs_are_present(self):
        for name in ('ambulance', 'smurd'):
            model = json.loads((ROOT / f'content/assets/gokart/models/block/{name}_body.json').read_text())
            self.assertIn('rear_livery', model['textures'])
            self.assertIn('livery_reverse', model['textures'])
            self.assertEqual(sum(e['faces']['west']['texture'] == '#livery_reverse' for e in model['elements']), 1)
            for texture in model['textures'].values():
                namespace, path = texture.split(':', 1)
                self.assertTrue((ROOT / 'content/assets' / namespace / 'textures' / (path + '.png')).is_file(), texture)


if __name__ == '__main__':
    unittest.main()
