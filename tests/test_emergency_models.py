"""Geometry and texture regressions for the emergency vans."""
import json
import math
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

    def test_raked_pillars_reach_roof_and_vans_have_distinct_fronts(self):
        grilles = []
        for name in ('ambulance', 'smurd'):
            model = json.loads((ROOT / f'content/assets/gokart/models/block/{name}_body.json').read_text())
            grilles.append(model['textures']['van_grille'])
            pillars = [e for e in model['elements'] if e.get('rotation', {}).get('angle') == -30.0
                       and e['faces']['up']['texture'] == '#shell']
            self.assertEqual(len(pillars), 2)
            # Forward-set windshield gives a van-like short nose, rather than
            # the long pickup hood seen in the previous model.
            self.assertTrue(all(abs(e['rotation']['origin'][2] - 23.25) < 0.01 for e in pillars))
            self.assertLess(22.8 - 15.25, 8.0)
            for e in pillars:
                r = e['rotation']
                angle = math.radians(r['angle'])
                oy, oz = r['origin'][1:]
                y, z = e['to'][1], e['to'][2]
                top_y = oy + math.cos(angle) * (y - oy) - math.sin(angle) * (z - oz)
                top_z = oz + math.sin(angle) * (y - oy) + math.cos(angle) * (z - oz)
                self.assertGreaterEqual(top_y, 22.02)
                self.assertLessEqual(top_z, 18.0)  # front edge of the roof, in model coordinates
            windows = [e for e in model['elements'] if e['faces']['east']['texture'] == '#glass'
                       and e['from'][0] > 20 and e['from'][1] > 13]
            self.assertTrue(any(e['to'][2] - e['from'][2] > 9 for e in windows))
        self.assertNotEqual(*grilles)

    def test_cab_taper_and_medical_equipment_are_present(self):
        for name in ('ambulance', 'smurd'):
            model = json.loads((ROOT / f'content/assets/gokart/models/block/{name}_body.json').read_text())
            elements = model['elements']
            corners = [e for e in elements if e['faces']['east']['texture'] == '#corner_glass']
            self.assertEqual(len(corners), 10)
            for side in (-1, 1):
                strips = sorted((e for e in corners if (e['from'][0] > 8) == (side > 0)),
                                key=lambda e: e['from'][2])
                self.assertEqual(len(strips), 5)
                for a, b in zip(strips, strips[1:]):
                    self.assertLessEqual(b['from'][2] - a['to'][2], 0.011)
                    self.assertGreater(a['to'][1], b['to'][1])
            self.assertEqual(sum(e['faces']['up']['texture'] == '#medical_mattress' for e in elements), 1)
            self.assertTrue(any(e['faces']['up']['texture'] == '#medical_red' for e in elements))

    def test_roof_crown_front_lights_and_door_markings(self):
        for name in ('ambulance', 'smurd'):
            model = json.loads((ROOT / f'content/assets/gokart/models/block/{name}_body.json').read_text())
            elements = model['elements']
            for x in (-12, -10.25, 0, 10.25, 12):
                for z in (-20, -8, 0, 5):
                    self.assertTrue(any(covers_side(e, x, 22.3, z) for e in elements), (name, x, z))
            self.assertEqual(sum(e['faces']['south']['texture'] == '#van_lamp' and e['from'][2] > 29 for e in elements), 2)
            for tex, side in (('#door_mark', 'east'), ('#door_mark_reverse', 'west')):
                self.assertEqual(sum(e['faces'][side]['texture'] == tex for e in elements), 1)
            self.assertEqual(model['textures']['glass'], 'gokart:block/medical_glass')
            self.assertEqual(model['textures']['van_lamp'], 'gokart:block/medical_headlamp')

    def test_emergency_wheel_openings_clear_tires_with_limited_gap(self):
        # World-space wheel radius 4 texels * 1.36 scale; body is non-uniformly scaled.
        radius = 4 * 1.36 / 16
        for name in ('ambulance', 'smurd'):
            elements = json.loads((ROOT / f'content/assets/gokart/models/block/{name}_body.json').read_text())['elements']
            for axle in (-13.8, 13.8):
                for side in (-1, 1):
                    for angle in range(0, 181, 5):
                        a = math.radians(angle)
                        y = (radius + radius * math.sin(a)) * 16 / 1.45
                        z = axle + radius * math.cos(a) * 16 / 1.65
                        self.assertFalse(any(covers_side(e, side * 12.20, y, z) and
                                             e['faces']['east']['texture'] in ('#shell', '#frame')
                                             for e in elements), (name, axle, side, angle))
                    # Crown should sit close to, but above, the top of the tyre.
                    tyre_top = 2 * radius * 16 / 1.45
                    self.assertLess(7.85 - tyre_top, 0.5)
                    self.assertGreater(7.85 - tyre_top, 0)
                    # The arch ends are near the tyre, not the previous huge opening.
                    arch_half_width = 1.15 + 3.1 * math.cos(math.radians(38))
                    self.assertLess(arch_half_width - radius * 16 / 1.65, 0.4)

    def test_emergency_markings_and_opposite_side_uvs_are_present(self):
        for name in ('ambulance', 'smurd'):
            model = json.loads((ROOT / f'content/assets/gokart/models/block/{name}_body.json').read_text())
            self.assertIn('rear_livery', model['textures'])
            self.assertIn('livery_reverse', model['textures'])
            self.assertEqual(sum(e['faces']['west']['texture'] == '#side_sign_reverse' for e in model['elements']), 1)
            self.assertEqual(sum(e['faces']['east']['texture'] == '#side_sign' for e in model['elements']), 1)
            for texture in model['textures'].values():
                namespace, path = texture.split(':', 1)
                self.assertTrue((ROOT / 'content/assets' / namespace / 'textures' / (path + '.png')).is_file(), texture)


if __name__ == '__main__':
    unittest.main()
