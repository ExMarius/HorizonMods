#!/usr/bin/env python3
"""Install the matched Horizon JAR and pack on the authorized 1.21.4 server."""
import hashlib
import io
import importlib.util
import json
import os
import re
import sys
import time
import urllib.parse
import uuid
import zipfile
from pathlib import Path

spec = importlib.util.spec_from_file_location('falix', Path(__file__).with_name('falix_auto_update.py'))
f = importlib.util.module_from_spec(spec); spec.loader.exec_module(f)
OLD_JAR = '8d45843ea6664415e5027d5b957dead70ac1d290e5c8abd67bfb9d70acc5bf59'
OLD_PACK = 'd1b55da29e79f91f2299c40c3f7413656f349ff4'
OLD_CONFIG_SUFFIX = 'MrCrayfishVehiclePlugin-resource-pack-1.21.4-r39.zip'
NAMES = {'config.yml','dealer.yml','gas_pumps.yml','mechanics.yml','trailers.yml','vehicles.yml'}


def replace_pack(config, url, sha1):
    if '\n' in url or not re.fullmatch(r'https://github\.com/ExMarius/HorizonMods/releases/download/horizon-offroader-[0-9]+/HorizonOffRoader-1\.21\.4\.zip', url):
        raise ValueError('unexpected candidate URL')
    if not re.fullmatch(r'[0-9a-f]{40}', sha1): raise ValueError('invalid pack hash')
    text = config.decode('utf-8')
    section = re.search(r'(?ms)^resource-pack:[^\n]*\n((?:[ \t]+[^\n]*\n|\s*\n|\s*\#.*\n)*)', text)
    if not section: raise ValueError('missing pack section')
    body = section.group(1)
    for key, value in [('url', url), ('sha1', sha1)]:
        pattern = r'(?m)^  '+key+r':\s*([^\n]*)$'
        found = re.findall(pattern, body)
        if len(found) != 1: raise ValueError('ambiguous pack configuration')
        current = found[0].strip().strip('"\'')
        if current and not (key == 'url' and current.endswith(OLD_CONFIG_SUFFIX)
                            or key == 'sha1' and current.lower() == OLD_PACK):
            raise ValueError('unexpected plugin pack configuration')
        body = re.sub(pattern, lambda m: '  '+key+': '+json.dumps(value), body, count=1)
    return (text[:section.start(1)] + body + text[section.end(1):]).encode()


def properties(api):
    entries=api.api('/properties')
    return {e['key']:str(e.get('value','')) for e in entries if isinstance(e,dict) and 'key' in e}


def deploy(api, jar, pack, url, run):
    if not run.isdecimal(): raise ValueError('invalid run id')
    state=api.status()
    if state not in ('running','offline'): raise ValueError('server transitioning')
    versions=api.api('/files?directory=%2Fversions&limit=100')
    if not any(e.get('name')=='1.21.4' for e in versions): raise ValueError('wrong server version')
    oldjar=api.download('/plugins/'+f.NAME)
    if f.sha(oldjar)!=OLD_JAR: raise ValueError('selected JAR changed; refusing deploy')
    oldprops=properties(api)
    keys=['resource-pack','resource-pack-sha1','resource-pack-id','require-resource-pack']
    if any(k not in oldprops for k in keys) or oldprops['resource-pack-sha1'].lower()!=OLD_PACK:
        raise ValueError('server pack not expected r39')
    entries=api.api('/files?'+urllib.parse.urlencode({'directory':'/plugins/MrCrayfishVehiclePlugin','limit':100}))
    if {e.get('name') for e in entries if isinstance(e,dict)}!=NAMES: raise ValueError('unexpected plugin data files')
    backups={n:api.download('/plugins/MrCrayfishVehiclePlugin/'+n) for n in sorted(NAMES)}
    backup_props=api.download('/server.properties')
    pack_sha=hashlib.sha1(pack).hexdigest()
    newconfig=replace_pack(backups['config.yml'],url,pack_sha)
    with zipfile.ZipFile(io.BytesIO(pack)) as z:
        if json.loads(z.read('pack.mcmeta'))['pack']['pack_format'] != 46 or z.testzip(): raise ValueError('invalid pack')
        if 'assets/horizonvehicles/items/off_roader_body_part_00.json' not in z.namelist(): raise ValueError('missing Horizon models')
    for n, data in [('plugin.jar',oldjar),('server.properties',backup_props), *backups.items()]:
        name=f'mcv-before-horizon-{run}-{n}.bak'; api.upload('/',name,data)
        if f.sha(api.download('/'+name))!=f.sha(data): raise ValueError('backup verification failed')
    f.notice('Backup', 'Existing JAR, plugin data and server.properties backed up and verified')
    if f.sha(api.download('/plugins/'+f.NAME)) != OLD_JAR or api.download('/plugins/MrCrayfishVehiclePlugin/config.yml') != backups['config.yml']:
        raise ValueError('server files changed during backup; no installation performed')
    currentprops = properties(api)
    if any(currentprops.get(k,'').lower() != oldprops[k].lower() for k in keys):
        raise ValueError('server pack properties changed during backup; no installation performed')
    newprops={'resource-pack':url,'resource-pack-sha1':pack_sha,
              'resource-pack-id':str(uuid.uuid5(uuid.NAMESPACE_URL,url)),'require-resource-pack':'true'}
    changes_started=False
    try:
        changes_started=True
        api.upload('/plugins/MrCrayfishVehiclePlugin','config.yml',newconfig)
        if api.download('/plugins/MrCrayfishVehiclePlugin/config.yml')!=newconfig: raise ValueError('plugin config verification failed')
        api.api('/properties',{'properties':newprops},'PUT')
        if any(properties(api).get(k,'').lower()!=v.lower() for k,v in newprops.items()): raise ValueError('server properties verification failed')
        api.upload('/plugins', f.NAME, jar)
        if f.sha(api.download('/plugins/'+f.NAME))!=f.sha(jar): raise ValueError('JAR verification failed')
    except BaseException:
        if changes_started:
            try:
                api.upload('/plugins',f.NAME,oldjar)
                api.upload('/plugins/MrCrayfishVehiclePlugin','config.yml',backups['config.yml'])
                api.api('/properties',{'properties':{k:oldprops[k] for k in keys}},'PUT')
                if f.sha(api.download('/plugins/'+f.NAME))!=OLD_JAR or api.download('/plugins/MrCrayfishVehiclePlugin/config.yml')!=backups['config.yml'] or any(properties(api).get(k,'').lower()!=oldprops[k].lower() for k in keys):
                    raise RuntimeError('rollback could not be verified')
                f.notice('Rollback', 'Previous JAR, plugin config and pack properties restored and verified')
            except BaseException:
                print('::error::Automatic rollback failed; do not restart until server files are checked manually', flush=True)
        raise
    f.notice('Installed', 'JAR and matching pack settings verified; JAR SHA-256 '+f.sha(jar)+'; pack SHA-1 '+pack_sha)
    if state == 'offline':
        f.notice('Restart','Server offline; changes apply at next start'); return
    if api.status() != 'running': raise ValueError('server state changed; restart not requested')
    # Falix may require the user to verify in the panel. Keep the complete,
    # verified installation in place rather than rolling back on a 403 here.
    api.api('/power',{'signal':'restart'},'POST')
    f.notice('Restart','Restart accepted; waiting for state transition')
    transitioned=False
    for _ in range(36):
        time.sleep(5); current=api.status()
        if current in ('stopping','offline','starting'): transitioned=True
        if transitioned and current=='running':
            f.notice('Restart','Server running; check plugin log and visual behavior'); return
    raise ValueError('Restart not confirmed; check server panel')


def main():
    jar=f.verify_jar(Path(sys.argv[1])); pack=Path(sys.argv[2]).read_bytes(); url=sys.argv[3]
    deploy(f.Falix(f.login()),jar,pack,url,os.environ.get('GITHUB_RUN_ID',''))
if __name__=='__main__': main()
