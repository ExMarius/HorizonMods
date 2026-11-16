"""Sample the visible side of the generated fenders for pinholes above the arch."""
import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def covers_side(element, x, y, z):
    lo, hi = element['from'], element['to']
    if not lo[0] <= x + 8 <= hi[0]:
        return False
    z += 8
    rotation = element.get('rotation')
    if rotation:
        if rotation['axis'] != 'x':
            return False
        angle = math.radians(-rotation['angle'])
        c, s = math.cos(angle), math.sin(angle)
        _, oy, oz = rotation['origin']
        dy, dz = y - oy, z - oz
        y, z = oy + c * dy - s * dz, oz + s * dy + c * dz
    return lo[1] - 1e-5 <= y <= hi[1] + 1e-5 and lo[2] - 1e-5 <= z <= hi[2] + 1e-5


class ArchCoverage(unittest.TestCase):
    def test_exterior_panel_above_arch(self):
        cases = [
            ('police_car', 13.8, 12.20, 8.75, 10.9, 2.15, 3.2, 38),
            ('police_car', -13.8, 12.20, 8.75, 11.05, 2.15, 3.2, 38),
            ('off_roader', 14.5, 12.10, 10.05, 12.55, 2.45, 3.35, 35),
            ('off_roader', -14.5, 12.10, 10.05, 12.8, 2.45, 3.35, 35),
        ]
        for name, cz, x, crown, top, half, length, angle in cases:
            model = ROOT / f'content/assets/gokart/models/block/{name}_body.json'
            elements = json.loads(model.read_text())['elements']
            rad = math.radians(angle)
            for i in range(101):
                dz = (half + length * math.cos(rad)) * i / 100
                low = crown - max(0, dz - half) * math.tan(rad)
                for sign in (-1, 1):
                    z = cz + sign * dz
                    for j in range(1, 31):
                        y = low + (top - low) * j / 30
                        for side_x in (-x, x):
                            self.assertTrue(any(covers_side(e, side_x, y, z) for e in elements),
                                            f'{name} at axle {cz}: hole at ({side_x}, {y}, {z})')


if __name__ == '__main__':
    unittest.main()
