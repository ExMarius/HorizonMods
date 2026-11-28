#!/usr/bin/env python3
"""Install the authorized October 9 checkpoint after verifying backups."""
import importlib.util
import os
import sys
import urllib.parse
from pathlib import Path

spec = importlib.util.spec_from_file_location('falix', Path(__file__).with_name('falix_auto_update.py'))
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)
EXPECTED = '39d884e35e30444db14803900a2b843b7d1510340830bb8b506e09eaa1bfc5c5'
CURRENT = '13d25e3ffccb86e26a48cc63c9a7cf3f885e82abf8e20fa63cb0542036707e1a'

def main():
    run = os.environ.get('GITHUB_RUN_ID', '')
    if not run.isdecimal(): f.abort('Invalid run id')
    jar = f.verify_jar(Path(sys.argv[1]))
    if f.sha(jar) != EXPECTED: f.abort('October checkpoint hash mismatch')
    api = f.Falix(f.login())
    if f.sha(api.download('/plugins/' + f.NAME)) != CURRENT:
        f.abort('Current JAR changed; refusing to overwrite')
    names = {'config.yml', 'dealer.yml', 'gas_pumps.yml', 'mechanics.yml', 'trailers.yml', 'vehicles.yml'}
    entries = api.api('/files?' + urllib.parse.urlencode({'directory': '/plugins/MrCrayfishVehiclePlugin', 'limit': 100}))
    if {x.get('name') for x in entries if isinstance(x, dict)} != names:
        f.abort('Unexpected plugin files, manual backup required')
    paths = [('/plugins/MrCrayfishVehiclePlugin/' + name, name) for name in sorted(names)]
    paths.append(('/server.properties', 'server.properties'))
    for path, name in paths:
        data = api.download(path)
        backup = f'mcv-oct9-{run}-{name}.bak'
        api.upload('/', backup, data)
        if f.sha(api.download('/' + backup)) != f.sha(data): f.abort('Data backup verification failed; no JAR uploaded')
    f.notice('Backup', 'Six plugin data files and server.properties backed up and verified; pack configuration unchanged')
    f.deploy(api, jar, run)

if __name__ == '__main__': main()
