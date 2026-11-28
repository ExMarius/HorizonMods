#!/usr/bin/env python3
"""Replace only the gas-pump visuals in an existing 1.21.4 pack."""
import hashlib, io, json, sys, zipfile
from pathlib import Path
here = Path(__file__).resolve().parent
base, dest = map(Path, sys.argv[1:3])
if base.resolve() == dest.resolve() or dest.exists():
    raise SystemExit('Output must be a new file')
with zipfile.ZipFile(base) as z:
    if len(z.namelist()) != len(set(z.namelist())) or z.testzip():
        raise ValueError('Invalid base pack')
    files = {n: z.read(n) for n in z.namelist()}
if json.loads(files['pack.mcmeta'])['pack']['pack_format'] != 46:
    raise ValueError('Unexpected pack version')
changes = {
    'assets/vehicle/models/item/gas_pump_bottom.json': here / 'gas_pump_bottom.json',
    'assets/vehicle/models/item/gas_pump_top.json': here / 'gas_pump_top.json',
    'assets/vehicle/textures/item/nozzle.png': here.parent / 'assets/nozzle-red.png',
}
for key, source in changes.items():
    if key not in files:
        raise ValueError('Base pack missing ' + key)
    files[key] = source.read_bytes()
texture = 'assets/vehicle/textures/item/horizon_pump_red.png'
if texture in files:
    raise ValueError('Pump texture already present')
files[texture] = (here / 'pump.png').read_bytes()
with zipfile.ZipFile(dest, 'x', zipfile.ZIP_DEFLATED) as z:
    for name, data in sorted(files.items()):
        info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, data)
print('Pump pack SHA-1:', hashlib.sha1(dest.read_bytes()).hexdigest())
