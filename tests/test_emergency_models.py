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
            for zstep in range(65, 187):
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

    def test_patient_floor_and_equipment_support(self):
        for name in ('ambulance', 'smurd'):
            elements = json.loads((ROOT / f'content/assets/gokart/models/block/{name}_body.json').read_text())['elements']
            floors = [e for e in elements if e['faces']['up']['texture'] == '#medical_floor']
            # Generator shifts x and z by eight. The entire centre aisle is
            # solid and meets the forward floor and rear wheelhouse liners.
            for x in (-6.39, -4.0, 0.0, 4.0, 6.39):
                for z in (-21.20, -18.0, -13.8, -8.60, -8.50, -5.0):
                    self.assertTrue(any(e['from'][0] <= x + 8 <= e['to'][0] and
                                        e['from'][2] <= z + 8 <= e['to'][2] and
                                        abs(e['to'][1] - 4.36) < 0.001 for e in floors),
                                    (name, x, z))
            # The bag and oxygen cylinder rest completely on the raised shelf,
            # not floating over its outside edge.
            shelf = next(e for e in floors if e['from'][0] == 14.96 and e['to'][0] == 16.19)
            bag = next(e for e in elements if e['faces']['up']['texture'] == '#medical_red' and
                       e['from'][1] == 8.57)
            cylinder = next(e for e in elements if e['faces']['up']['texture'] == '#medical_white' and
                            e['from'][1] == 8.57)
            for item in (bag, cylinder):
                for axis in (0, 2):
                    self.assertLessEqual(shelf['from'][axis], item['from'][axis])
                    self.assertGreaterEqual(shelf['to'][axis], item['to'][axis])
                self.assertAlmostEqual(item['from'][1] - shelf['to'][1], 0.02)

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
            self.assertLess(20.0 - 15.25, 5.0)
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
            self.assertEqual(len(corners), 16)
            for side in (-1, 1):
                strips = sorted((e for e in corners if (e['from'][0] > 8) == (side > 0)),
                                key=lambda e: e['from'][2])
                self.assertEqual(len(strips), 8)
                for a, b in zip(strips, strips[1:]):
                    self.assertLessEqual(b['from'][2] - a['to'][2], 0.011)
                    self.assertGreater(a['to'][1], b['to'][1])
                for e in strips:
                    self.assertLessEqual(e['to'][0] - e['from'][0], 0.081)
                    # Rear surface of the -30 degree A-pillar: verify the
                    # front upper corner of each window stays behind it.
                    y = e['to'][1]
                    pillar_rear_z = 15.25 - 0.25 / math.cos(math.radians(30)) - (y - 11.05) * math.tan(math.radians(30))
                    self.assertLessEqual(e['to'][2] - 8, pillar_rear_z - 0.09)
            main = [e for e in elements if e['faces']['east']['texture'] == '#glass' and
                    e['from'][1] == 11.86 and e['to'][1] == 21.70]
            self.assertEqual(len(main), 2)
            for e in main:
                pillar_rear_z = 15.25 - 0.25 / math.cos(math.radians(30)) - (e['to'][1] - 11.05) * math.tan(math.radians(30))
                self.assertLess(e['to'][2] - 8, pillar_rear_z)
                self.assertLessEqual(e['to'][0] - e['from'][0], 0.081)
            self.assertEqual(sum(e['faces']['up']['texture'] == '#medical_mattress' for e in elements), 1)
            self.assertTrue(any(e['faces']['up']['texture'] == '#medical_red' for e in elements))

    def test_roof_crown_front_lights_and_door_markings(self):
        for name in ('ambulance', 'smurd'):
            model = json.loads((ROOT / f'content/assets/gokart/models/block/{name}_body.json').read_text())
            elements = model['elements']
            for x in (-12, -10.25, 0, 10.25, 12):
                for z in (-20, -8, 0, 5):
                    self.assertTrue(any(covers_side(e, x, 22.3, z) for e in elements), (name, x, z))
            self.assertEqual(sum(e['faces']['south']['texture'] == '#van_lamp' and e['from'][2] > 26 for e in elements), 2)
            for tex, side in (('#door_mark', 'east'), ('#door_mark_reverse', 'west')):
                self.assertEqual(sum(e['faces'][side]['texture'] == tex for e in elements), 1)
            self.assertEqual(model['textures']['glass'], 'gokart:block/medical_glass')
            self.assertEqual(model['textures']['van_lamp'], 'gokart:block/medical_headlamp')

    def test_emergency_wheel_openings_clear_tires_with_limited_gap(self):
        # World-space wheel radius 4 texels * 1.36 scale; body is non-uniformly scaled.
        radius = 4 * 1.36 / 16
        for name in ('ambulance', 'smurd'):
            elements = json.loads((ROOT / f'content/assets/gokart/models/block/{name}_body.json').read_text())['elements']
            for axle in (-13.8, 11.0):
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

    def test_fire_engine_content_and_windows(self):
        model = json.loads((ROOT / 'content/assets/gokart/models/block/fire_truck_body.json').read_text())
        elements = model['elements']
        self.assertGreaterEqual(sum(e['faces']['east']['texture'] == '#shutter' for e in elements), 4)
        self.assertGreaterEqual(sum(e['faces']['up']['texture'] == '#chrome' and
                                    e['from'][1] > 23 for e in elements), 9)
        self.assertTrue((ROOT / 'content/assets/gokart/textures/item/fire_truck.png').is_file())
        self.assertTrue((ROOT / 'content/data/gokart/recipe/fire_truck.json').is_file())
        for texture in model['textures'].values():
            namespace, path = texture.split(':', 1)
            self.assertTrue((ROOT / 'content/assets' / namespace / 'textures' / (path + '.png')).is_file(), texture)
        # Cab has no solid shell occupying the window/windscreen centres.
        for e in elements:
            if e.get('rotation') or e['faces']['up']['texture'] != '#red':
                continue
            for point in ((20.1, 17, 14.0), (-4.1, 17, 14.0), (8.0, 17, 26.6)):
                self.assertFalse(all(e['from'][i] < point[i] < e['to'][i] for i in range(3)))

    def test_fire_cab_is_hollow_and_seats_rest_on_floor(self):
        elements = json.loads((ROOT / 'content/assets/gokart/models/block/fire_truck_body.json').read_text())['elements']
        floors = [e for e in elements if e['faces']['up']['texture'] == '#floor']
        self.assertEqual(len(floors), 1)
        floor = floors[0]
        seats = [e for e in elements if e['faces']['up']['texture'] == '#seat' and abs(e['from'][1] - 4.42) < 0.001]
        self.assertEqual(len(seats), 2)
        for seat in seats:
            self.assertLess(abs(seat['from'][1] - floor['to'][1]), 0.03)
            for axis in (0, 2):
                self.assertGreater(seat['from'][axis], floor['from'][axis])
                self.assertLess(seat['to'][axis], floor['to'][axis])
            point = [(seat['from'][0]+seat['to'][0])/2, 7.0, (seat['from'][2]+seat['to'][2])/2]
            self.assertFalse(any(e['faces']['up']['texture'] == '#red' and not e.get('rotation') and
                                 all(e['from'][i] < point[i] < e['to'][i] for i in range(3)) for e in elements))

    def test_static_blue_beacons_have_expected_bounds_and_uv(self):
        for name, key, y0, y1, z0, z1 in (('ambulance', '#siren_blue', 23.67, 24.6, -2.75, -0.85),
                                           ('smurd', '#siren_blue', 23.67, 24.6, -2.75, -0.85),
                                           ('fire_truck', '#blue', 23.07, 24.0, 8.05, 9.95)):
            model = json.loads((ROOT / f'content/assets/gokart/models/block/{name}_body.json').read_text())
            self.assertEqual(model['textures'][key[1:]], 'gokart:block/emergency_blue_lens')
            lenses = [e for e in model['elements'] if e['faces']['up']['texture'] == key and
                      abs(e['from'][1]-y0) < 0.001 and abs(e['to'][1]-y1) < 0.001]
            self.assertEqual(len(lenses), 2)
            for lens in lenses:
                self.assertAlmostEqual(lens['to'][0]-lens['from'][0], 5.8)
                self.assertAlmostEqual(lens['from'][2]-8, z0)
                self.assertAlmostEqual(lens['to'][2]-8, z1)
                self.assertEqual(lens['faces']['up']['uv'], [0.0, 0.0, 16.0, 16.0])

    def test_attendant_seat_faces_stretcher_without_overlap(self):
        for name in ('ambulance', 'smurd'):
            elements = json.loads((ROOT / f'content/assets/gokart/models/block/{name}_body.json').read_text())['elements']
            mattress = next(e for e in elements if e['faces']['up']['texture'] == '#medical_mattress')
            seat = [e for e in elements if e['faces']['up']['texture'] == '#attendant']
            self.assertEqual(len(seat), 3)  # seat cushion, back and headrest
            cushion = min(seat, key=lambda e: e['from'][1])
            back = max(seat, key=lambda e: e['to'][1])
            self.assertGreater(cushion['from'][0], mattress['to'][0])
            self.assertLess(cushion['from'][2], mattress['to'][2])
            self.assertGreater(cushion['to'][2], mattress['from'][2])
            self.assertGreater(back['to'][1], cushion['to'][1] + 5)

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
