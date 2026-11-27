#!/usr/bin/env python3
"""Make verified server-side backups before a recovery-truck update.

If the server is running, first take a best-effort live backup, then request a
stop and take another authoritative backup only once it is offline. Never
install while live data can still change.
"""
import hashlib
import importlib.util
import io
import json
import os
import sys
import time
import urllib.parse
import zipfile
from pathlib import Path

spec=importlib.util.spec_from_file_location('falix',Path(__file__).with_name('falix_auto_update.py'))
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
ROOT='/plugins/MrCrayfishVehiclePlugin'
EXPECTED={'config.yml','dealer.yml','garages.yml','gas_pumps.yml','mechanics.yml','trailers.yml','vehicles.yml'}
EXPECTED_JAR='9b63797b49224a565c3807c5e492ad8c416fc4c02eacd7296cf9bb3788b793c2'
EXPECTED_PACK='136f003f9c56ee849881d41fb6697876353b5681'

def backup(api,pack,label,run):
    listing=api.api('/files?'+urllib.parse.urlencode({'directory':ROOT,'limit':100}))
    if len(listing)!=len(EXPECTED) or {x.get('name') for x in listing}!=EXPECTED or any(not x.get('is_file') or x.get('is_symlink') for x in listing):
        raise ValueError('plugin directory changed or includes unexpected entries; refusing incomplete backup')
    props={p['key']:str(p.get('value','')) for p in api.api('/properties') if 'key' in p}
    if props.get('resource-pack-sha1','').lower()!=EXPECTED_PACK or hashlib.sha1(pack).hexdigest()!=EXPECTED_PACK:
        raise ValueError('installed pack does not match backed up pack')
    jar=api.download('/plugins/'+f.NAME)
    if f.sha(jar)!=EXPECTED_JAR:raise ValueError('installed jar changed since audit')
    data={'plugin/MrCrayfishVehiclePlugin.jar':jar,'server.properties':api.download('/server.properties'),
          'old-resource-pack.zip':pack}
    for name in sorted(EXPECTED): data['plugin-data/'+name]=api.download(ROOT+'/'+name)
    # Fail if a data file changes during capture; an offline copy is still required.
    for name in sorted(EXPECTED):
        if api.download(ROOT+'/'+name)!=data['plugin-data/'+name]:raise ValueError('plugin data changed during backup; retry')
    if api.download('/plugins/'+f.NAME)!=jar or api.download('/server.properties')!=data['server.properties']:
        raise ValueError('server files changed during backup; retry')
    manifest={name:hashlib.sha256(content).hexdigest() for name,content in sorted(data.items())}
    data['manifest.sha256.json']=json.dumps(manifest,sort_keys=True,indent=2).encode()
    output=io.BytesIO()
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,content in sorted(data.items()):archive.writestr(name,content)
    payload=output.getvalue()
    if len(payload)>f.MAX_FILE:raise ValueError('backup exceeds upload limit')
    name=f'mcv-recovery-backup-{run}-{label}.zip.bak'
    api.upload('/',name,payload)
    if api.download('/'+name)!=payload:raise ValueError('backup verification failed')
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        if archive.testzip() or set(archive.namelist())!=set(data):raise ValueError('backup archive invalid')
        for path,content in data.items():
            if archive.read(path)!=content:raise ValueError('backup archive mismatch')
    f.notice('Verified backup', '/'+name+' SHA256='+f.sha(payload)+' ('+label+')')

def main():
    run=os.environ.get('GITHUB_RUN_ID','')
    if not run.isdecimal():raise ValueError('invalid run id')
    pack=Path(sys.argv[1]).read_bytes();api=f.Falix(f.login())
    state=api.status()
    if state not in ('running','offline'):raise ValueError('server transitioning; no installation')
    backup(api,pack,'live' if state=='running' else 'offline',run)
    if state=='running':
        f.notice('Stop request','Requesting stop before consistent offline backup and installation')
        api.api('/power',{'signal':'stop'},'POST')
        for _ in range(36):
            time.sleep(5)
            if api.status()=='offline':break
        else:raise ValueError('server did not stop; no installation performed')
        backup(api,pack,'offline',run)
    if api.status()!='offline':raise ValueError('server not offline; no installation')
    f.notice('Offline backup complete','Server offline; all audited plugin data, old JAR and old pack backed up')
if __name__=='__main__':main()
