#!/usr/bin/env python3
"""Read and back up the selected server build; never changes the active files."""
import importlib.util
import os
import sys
import urllib.parse
import zipfile
from io import BytesIO
from pathlib import Path
spec = importlib.util.spec_from_file_location('falix', Path(__file__).with_name('falix_auto_update.py'))
f = importlib.util.module_from_spec(spec); spec.loader.exec_module(f)
JAR_SHA = '8d45843ea6664415e5027d5b957dead70ac1d290e5c8abd67bfb9d70acc5bf59'

def main():
    run = os.environ.get('GITHUB_RUN_ID', '')
    if not run.isdecimal(): f.abort('Invalid run id')
    api = f.Falix(f.login())
    live = api.download('/plugins/' + f.NAME)
    if f.sha(live) != JAR_SHA: f.abort('Server JAR differs from selected build; no backup written')
    local = Path(sys.argv[1]).read_bytes()
    with zipfile.ZipFile(BytesIO(live)) as a, zipfile.ZipFile(BytesIO(local)) as b:
        ac = {n: a.read(n) for n in a.namelist() if n.endswith('.class')}
        bc = {n: b.read(n) for n in b.namelist() if n.endswith('.class')}
        if ac != bc: f.abort('Source bytecode does not match selected build; no backup written')
        f.notice('Baseline', f'All {len(ac)} compiled classes match selected live JAR')
    names = {'config.yml','dealer.yml','gas_pumps.yml','mechanics.yml','trailers.yml','vehicles.yml'}
    entries = api.api('/files?' + urllib.parse.urlencode({'directory':'/plugins/MrCrayfishVehiclePlugin','limit':100}))
    if {x.get('name') for x in entries if isinstance(x,dict)} != names: f.abort('Unexpected plugin data files; manual backup required')
    files = [('/plugins/' + f.NAME, 'plugin.jar.bak', live), ('/server.properties', 'server.properties.bak', None)]
    files += [('/plugins/MrCrayfishVehiclePlugin/'+n, n+'.bak', None) for n in sorted(names)]
    for path, name, data in files:
        if data is None: data = api.download(path)
        backup = f'mcv-good-{run}-{name}'
        api.upload('/', backup, data)
        if f.sha(api.download('/'+backup)) != f.sha(data): f.abort('Backup verification failed')
    f.notice('Backup', f'Verified JAR, six plugin files and server.properties with prefix mcv-good-{run}-; live snapshot not atomic')

if __name__ == '__main__': main()
