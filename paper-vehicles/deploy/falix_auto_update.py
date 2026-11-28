#!/usr/bin/env python3
"""Update one authorized server, verify backup/upload, then request a restart."""
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
from pathlib import Path

BASE = 'https://client.falixnodes.net/api/v2'
SERVER = '/servers/3500167'
NAME = 'MrCrayfishVehiclePlugin.jar'
MAX_FILE = 20 * 1024 * 1024

def notice(title, message):
    print(f'::notice title={title}::{message}', flush=True)

def abort(message):
    print('::error title=Falix update::' + message, flush=True)
    raise SystemExit(1)

def call(url, data=None, headers=None, method=None, binary=False):
    try:
        request = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read(MAX_FILE + 1)
        if len(raw) > MAX_FILE:
            abort('Response exceeds safety limit')
        return raw if binary else json.loads(raw)
    except urllib.error.HTTPError as exc:
        try:
            code = json.load(exc).get('error', {}).get('code', 'unknown')
        except Exception:
            code = 'unknown'
        if not isinstance(code, str) or not re.fullmatch(r'[a-z_]{1,80}', code):
            code = 'unknown'
        abort(f'HTTP {exc.code}, {code}; if verification is required, start/restart in Falix panel')
    except (urllib.error.URLError, TimeoutError, ValueError):
        abort('Network or response error')

def login():
    url = os.environ['ACTIONS_ID_TOKEN_REQUEST_URL'] + '&' + urllib.parse.urlencode({'audience': BASE})
    jwt = call(url, headers={'Authorization': 'bearer ' + os.environ['ACTIONS_ID_TOKEN_REQUEST_TOKEN']})['value']
    print('::add-mask::' + jwt, flush=True)
    form = urllib.parse.urlencode({'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange', 'subject_token_type': 'urn:ietf:params:oauth:token-type:id_token', 'connection': 'reg_541k4oqt2cDg61pRuQcRzOQie7', 'subject_token': jwt}).encode()
    token = call(BASE + '/oauth2/token', data=form)['access_token']
    print('::add-mask::' + token, flush=True)
    return token

class Falix:
    def __init__(self, token): self.token = token
    def api(self, path, data=None, method=None):
        headers = {'Authorization': 'Bearer ' + self.token}
        if data is not None:
            headers['Content-Type'] = 'application/json'
            data = json.dumps(data).encode()
        return call(BASE + SERVER + path, data=data, headers=headers, method=method)['data']
    def signed(self, url):
        parsed = urllib.parse.urlsplit(url)
        host = (parsed.hostname or '').lower()
        if parsed.scheme != 'https' or not (host.endswith('.falixserver.net') or host.endswith('.falixnodes.net')):
            abort('Unexpected signed URL host')
        print('::add-mask::' + url, flush=True)
        return url
    def download(self, path):
        signed = self.signed(self.api('/files/download', {'path': path}, 'POST')['url'])
        return call(signed, binary=True)
    def upload(self, directory, name, content):
        url = self.signed(self.api('/files/upload', method='POST')['url'])
        url += ('&' if '?' in url else '?') + urllib.parse.urlencode({'directory': directory})
        print('::add-mask::' + url, flush=True)
        boundary = '----falix-' + uuid.uuid4().hex
        body = (f'--{boundary}\r\nContent-Disposition: form-data; name="files"; filename="{name}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode() + content + f'\r\n--{boundary}--\r\n'.encode())
        call(url, data=body, headers={'Content-Type': 'multipart/form-data; boundary=' + boundary}, method='POST', binary=True)
    def status(self): return self.api('/console/status').get('status')

def sha(data): return hashlib.sha256(data).hexdigest()

def verify_jar(path):
    content = path.read_bytes()
    if len(content) > MAX_FILE: abort('Plugin JAR too large')
    with zipfile.ZipFile(path) as z:
        if "api-version: '1.21.4'" not in z.read('plugin.yml').decode(): abort('Wrong Paper API version')
        if int.from_bytes(z.read('com/mrcrayfish/vehicle/paper/VehiclePlugin.class')[6:8], 'big') != 65: abort('Wrong Java version')
    return content

def deploy(api, jar, run_id):
    state = api.status()
    if state not in ('running', 'offline'): abort('Server is transitioning; no upload performed')
    versions = api.api('/files?directory=%2Fversions&limit=100')
    if not any(x.get('name') == '1.21.4' for x in versions): abort('Server version is not confirmed 1.21.4')
    old = api.download('/plugins/' + NAME)
    backup = f'mcv-backup-{run_id}.jar.bak'
    api.upload('/', backup, old)
    if sha(api.download('/' + backup)) != sha(old): abort('Backup checksum mismatch; old plugin was not overwritten')
    notice('Falix backup', 'Previous JAR backed up and verified: ' + backup)
    api.upload('/plugins', NAME, jar)
    if sha(api.download('/plugins/' + NAME)) != sha(jar): abort('Uploaded JAR checksum mismatch; restart was not requested; verified backup remains on server')
    notice('Falix upload', 'Uploaded JAR SHA-256 verified: ' + sha(jar))
    if state == 'offline':
        notice('Falix restart', 'Server offline: update applies at next start; no automatic start requested')
        return
    if api.status() != 'running': abort('Server state changed after upload; no restart requested')
    api.api('/power', {'signal': 'restart'}, 'POST')
    notice('Falix restart', 'Restart request accepted; checking state transition')
    transitioned = False
    for _ in range(36):
        time.sleep(5)
        current = api.status()
        if current in ('stopping', 'offline', 'starting'): transitioned = True
        if current == 'running' and transitioned:
            notice('Falix restart', 'Server returned to running after restart; verify plugin startup in console')
            return
    abort('Restart accepted but complete restart could not be verified; check Falix panel')

if __name__ == '__main__':
    run_id = os.environ.get('GITHUB_RUN_ID', '')
    if not run_id.isdecimal(): abort('Invalid GitHub run ID')
    deploy(Falix(login()), verify_jar(Path(sys.argv[1])), run_id)
