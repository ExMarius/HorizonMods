#!/usr/bin/env python3
"""Report blockers to blindly copying Horizon model JSON into vanilla Paper packs.

This is a conservative inventory, not a complete Minecraft resource-pack validator.
It never copies, rewrites, or claims to port the referenced assets.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / 'paper-vehicles/src/main/java/ro/exmarius/horizonvehicles/VehicleCatalog.java'
ASSETS = ROOT / 'content/assets/gokart'
VALID_ANGLES = {-45, -22.5, 0, 22.5, 45}


def audit():
    entries = re.findall(r'new Entry\("([a-z_]+)", "[^"]+", "([a-z_]+)"\)', CATALOG.read_text())
    if not entries:
        raise ValueError('No vehicle entries found')
    result = []
    for name, model in entries:
        data = json.loads((ASSETS / 'models/block' / (model + '.json')).read_text())
        elements = data.get('elements', [])
        unsupported_angles = sorted({e['rotation']['angle'] for e in elements
                                     if 'rotation' in e and e['rotation']['angle'] not in VALID_ANGLES})
        outside_bounds = sum(any(n < -16 or n > 32 for key in ('from', 'to') for n in e[key])
                             for e in elements)
        missing_textures = []
        for texture in data.get('textures', {}).values():
            if texture.startswith('gokart:block/'):
                path = ASSETS / 'textures/block' / (texture.split('/')[-1] + '.png')
                if not path.exists():
                    missing_textures.append(texture)
        result.append({'vehicle': name, 'model': model,
                       'loader': data.get('loader', 'vanilla_elements'),
                       'elements': len(elements), 'unsupported_angles': unsupported_angles,
                       'elements_outside_vanilla_bounds': outside_bounds,
                       'missing_textures': missing_textures,
                       'has_horizon_light_emission': any('light_emission' in e for e in elements)})
    return result


if __name__ == '__main__':
    print(json.dumps(audit(), ensure_ascii=False, indent=2))
