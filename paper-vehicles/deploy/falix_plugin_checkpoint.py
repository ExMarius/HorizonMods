#!/usr/bin/env python3
"""Read-only capture of plugin state plus a verified private server-side copy.

A live capture is not atomic, even if the double-read matches. The server is
never stopped or restarted. This is not a backup of worlds or other plugins.
"""
import hashlib
import importlib.util
import io
import json
import os
import urllib.parse
import zipfile
from pathlib import Path

spec = importlib.util.spec_from_file_location('falix', Path(__file__).with_name('falix_auto_update.py'))
f = importlib.util.module_from_spec(spec); spec.loader.exec_module(f)
ROOT = '/plugins/MrCrayfishVehiclePlugin'
PACK = Path(os.environ['CHECKPOINT_PACK'])


def list_files(api, root):
    result = []
    def visit(directory):
        entries = api.api('/files?' + urllib.parse.urlencode({'directory': directory, 'limit': 100}))
        if not isinstance(entries, list) or len(entries) >= 100:
            raise ValueError('Directory listing is incomplete or unexpectedly large')
        for entry in entries:
            name = entry.get('name')
            if not isinstance(name, str) or name in ('.', '..') or '/' in name or '\\' in name or entry.get('is_symlink'):
                raise ValueError('Unsafe or unknown plugin entry')
            path = directory + '/' + name
            if entry.get('is_file') is True:
                result.append(path)
            elif entry.get('is_directory') is True or entry.get('is_file') is False:
                visit(path)
            else:
                raise ValueError('Unrecognized plugin entry type')
    visit(root)
    return sorted(result)


def main():
    run = os.environ.get('GITHUB_RUN_ID', '')
    if not run.isdecimal(): raise ValueError('Invalid run ID')
    api = f.Falix(f.login())
    state = api.status()
    if state not in ('running', 'offline', 'sleeping'): raise ValueError('Server is transitioning')
    paths = list_files(api, ROOT)
    if not paths or ROOT + '/vehicles.yml' not in paths:
        raise ValueError('Plugin data directory not found or incomplete')
    pack = PACK.read_bytes()
    props = {x['key']: str(x.get('value', '')) for x in api.api('/properties') if isinstance(x, dict) and 'key' in x}
    if hashlib.sha1(pack).hexdigest() != props.get('resource-pack-sha1', '').lower():
        raise ValueError('Resource pack does not match active server configuration')
    paths += ['/plugins/' + f.NAME, '/server.properties']
    contents = {path: api.download(path) for path in paths}
    # Detect changed files/listings, but cannot guarantee an atomic live snapshot.
    for path, content in contents.items():
        if api.download(path) != content: raise ValueError('Server data changed during backup; no checkpoint written')
    if list_files(api, ROOT) != sorted(path for path in paths if path.startswith(ROOT + '/')):
        raise ValueError('Plugin directory changed during backup; no checkpoint written')
    payloads = {path.lstrip('/'): content for path, content in contents.items()}
    payloads['resource-pack/HorizonOffRoader-1.21.4.zip'] = pack
    info = {'source_commit': os.environ['GITHUB_SHA'], 'state': state,
            'consistency': 'live best effort' if state == 'running' else 'server state ' + state,
            'sha256': {path: hashlib.sha256(content).hexdigest() for path, content in sorted(payloads.items())}}
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
        for path, content in sorted(payloads.items()): z.writestr(path, content)
        z.writestr('checkpoint-info.json', json.dumps(info, indent=2, sort_keys=True))
    payload = output.getvalue()
    if len(payload) > f.MAX_FILE: raise ValueError('Backup is larger than the safe upload limit')
    name = 'mcv-plugin-checkpoint-' + run + '.zip.bak'
    api.upload('/', name, payload)
    if f.sha(api.download('/' + name)) != f.sha(payload): raise ValueError('Uploaded backup checksum mismatch')
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        if z.testzip() is not None: raise ValueError('Backup ZIP is corrupt')
        for path, content in payloads.items():
            if z.read(path) != content: raise ValueError('Backup contents mismatch')
    f.notice('Plugin checkpoint', '/' + name + ' SHA-256 ' + f.sha(payload)
             + '; ' + str(len(contents)) + ' files plus verified pack; state=' + state
             + '; live capture may not reflect unsaved in-memory changes')
    f.notice('Plugin JAR checksum', f.sha(contents['/plugins/' + f.NAME]))

if __name__ == '__main__': main()
