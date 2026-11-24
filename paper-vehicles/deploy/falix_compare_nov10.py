#!/usr/bin/env python3
"""Back up plugin data and install the authorized 10 November 1.21.4 JAR."""
import hashlib
import importlib.util
import os
import re
import sys
import urllib.parse
from pathlib import Path

spec = importlib.util.spec_from_file_location('falix', Path(__file__).with_name('falix_auto_update.py'))
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)
EXPECTED = 'cdc946652883d728ed5413d97cbcc968f4cce0486772087c9da89da683fd54b3'
PACK_SHA1 = 'd1b55da29e79f91f2299c40c3f7413656f349ff4'

def main():
    run_id=os.environ.get('GITHUB_RUN_ID','')
    if not run_id.isdecimal(): f.abort('Invalid run id')
    jar=f.verify_jar(Path(sys.argv[1]))
    if hashlib.sha256(jar).hexdigest()!=EXPECTED: f.abort('Candidate JAR checksum mismatch')
    api=f.Falix(f.login())
    state=api.status()
    if state not in ('offline','running'): f.abort('Unexpected server state')
    entries=api.api('/files?'+urllib.parse.urlencode({'directory':'/plugins/MrCrayfishVehiclePlugin','limit':100}))
    names={x.get('name') for x in entries if isinstance(x,dict)}
    expected={'config.yml','dealer.yml','gas_pumps.yml','mechanics.yml','trailers.yml','vehicles.yml'}
    if names != expected: f.abort('Unexpected plugin data files; manual backup required')
    props=api.api('/properties')
    values={x.get('key'):str(x.get('value','')) for x in props if isinstance(x,dict)}
    if values.get('resource-pack-sha1','').lower()!=PACK_SHA1: f.abort('Server pack is not the expected r39; no deployment performed')
    for name in sorted(expected):
        data=api.download('/plugins/MrCrayfishVehiclePlugin/'+name)
        backup=f'mcv-compare-{run_id}-{name}.bak'
        api.upload('/', backup, data)
        if f.sha(api.download('/'+backup))!=f.sha(data): f.abort('Plugin data backup verification failed; JAR unchanged')
    properties=api.download('/server.properties')
    backup=f'mcv-compare-{run_id}-server.properties.bak'
    api.upload('/',backup,properties)
    if f.sha(api.download('/'+backup))!=f.sha(properties): f.abort('Properties backup verification failed; JAR unchanged')
    f.notice('Backup','Six plugin data files and server.properties backed up and verified; existing files remain untouched')
    f.deploy(api,jar,run_id)
if __name__=='__main__': main()
