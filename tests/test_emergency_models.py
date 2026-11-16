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

    def test_patient_compartment_has_real_window_openings_and_stretcher(self):
        for name in ('ambulance', 'smurd'):
            model = json.loads((ROOT / f'content/assets/gokart/models/block/{name}_body.json').read_text())
            elements = model['elements']
            # No solid shell/livery at the centre of either side or rear window.
            for e in elements:
                if e.get('rotation'):
                    continue
                lo, hi = e['from'], e['to']
                tex = {face['texture'] for face in e['faces'].values()}
                if tex.isdisjoint({'#shell', '#livery', '#livery_reverse'}):
                    continue
                for x, y, z in ((20.0, 15.0, 0.0), (-4.0, 15.0, 0.0),
                                (4.0, 15.0, -13.7), (12.0, 15.0, -13.7)):
                    self.assertFalse(lo[0] < x < hi[0] and lo[1] < y < hi[1] and lo[2] < z < hi[2],
                                     (name, 'solid wall blocks window', x, y, z))
            mattresses = [e for e in elements if e['faces']['up']['texture'] == '#medical_mattress']
            self.assertEqual(len(mattresses), 1)
            mattress = mattresses[0]
            self.assertGreater(mattress['to'][2] - mattress['from'][2], 16)
            # In the middle of the stretcher space there must be no old solid carbon core.
            self.assertFalse(any(e['faces']['up']['texture'] == '#carbon' and
                                 e['from'][0] < 7 < e['to'][0] and e['from'][1] < 7 < e['to'][1] and
                                 e['from'][2] < -4 < e['to'][2] for e in elements))

    def test_emergency_markings_and_opposite_side_uvs_are_present(self):
        for name in ('ambulance', 'smurd'):
            model = json.loads((ROOT / f'content/assets/gokart/models/block/{name}_body.json').read_text())
            self.assertIn('rear_livery', model['textures'])
            self.assertIn('livery_reverse', model['textures'])
            self.assertEqual(sum(e['faces']['west']['texture'] == '#livery_reverse' for e in model['elements']), 4)
            for texture in model['textures'].values():
                namespace, path = texture.split(':', 1)
                self.assertTrue((ROOT / 'content/assets' / namespace / 'textures' / (path + '.png')).is_file(), texture)


if __name__ == '__main__':
    unittest.main()
