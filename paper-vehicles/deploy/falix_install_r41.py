#!/usr/bin/env python3
"""One-off installation to the explicitly authorized Falix test server.

Runs inside GitHub Actions with an ephemeral OIDC token. No server secrets are
written to the repository or logged. Aborts on existing vehicle JARs or version
mismatch; it never restarts or deletes anything.
"""
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
from pathlib import Path

BASE = 'https://client.falixnodes.net/api/v2'
SERVER = '3500167'
NAME = 'MrCrayfishVehiclePlugin.jar'

def request(url, *, method='GET', data=None, headers=None, json_response=True):
    try:
        req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
        with urllib.request.urlopen(req, timeout=60) as r:
            content = r.read()
        return json.loads(content) if json_response else content
    except urllib.error.HTTPError as e:
        sys.exit('Request failed: HTTP ' + str(e.code))
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        sys.exit('Request failed: ' + type(e).__name__)

def api(path, *, method='GET', data=None):
    headers = {'Authorization': 'Bearer ' + token}
    if data is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(data).encode()
    return request(BASE + path, method=method, data=data, headers=headers)

def valid_url(url):
    parts = urllib.parse.urlsplit(url)
    host = (parts.hostname or '').lower()
    if parts.scheme != 'https' or not (host.endswith('.falixserver.net') or host.endswith('.falixnodes.net')):
        sys.exit('Refusing unexpected Falix signed URL host')
    print('::add-mask::' + url, flush=True)
    return url

jar = Path(sys.argv[1]).read_bytes()
with zipfile.ZipFile(sys.argv[1]) as z:
    assert "api-version: '1.21.4'" in z.read('plugin.yml').decode()
    assert int.from_bytes(z.read('com/mrcrayfish/vehicle/paper/VehiclePlugin.class')[6:8], 'big') == 65
    assert re.search(r'(?m)^  url: ""$', z.read('config.yml').decode())
print('::notice title=Local JAR SHA-256::' + hashlib.sha256(jar).hexdigest())
audience = BASE
url = os.environ['ACTIONS_ID_TOKEN_REQUEST_URL'] + '&' + urllib.parse.urlencode({'audience': audience})
id_token = request(url, headers={'Authorization': 'bearer ' + os.environ['ACTIONS_ID_TOKEN_REQUEST_TOKEN']})['value']
print('::add-mask::' + id_token, flush=True)
form = urllib.parse.urlencode({'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange', 'subject_token_type': 'urn:ietf:params:oauth:token-type:id_token', 'connection': 'reg_541k4oqt2cDg61pRuQcRzOQie7', 'subject_token': id_token}).encode()
token = request(BASE + '/oauth2/token', method='POST', data=form)['access_token']
print('::add-mask::' + token, flush=True)
prefix = '/servers/' + SERVER
status = api(prefix + '/console/status')['data']
if status.get('status') != 'offline' or status.get('node_ready') is not True:
    sys.exit('Server is not confirmed offline and node-ready; refusing upload')
versions = api(prefix + '/files?directory=%2Fversions&limit=100')['data']
if not any(x.get('name') == '1.21.4' for x in versions):
    sys.exit('Paper 1.21.4 version directory not found; refusing upload')
listing = api(prefix + '/files?directory=%2Fplugins&limit=100')['data']
if any(isinstance(x.get('name'), str) and x['name'].lower().endswith('.jar') and ('vehicle' in x['name'].lower() or 'horizon' in x['name'].lower()) for x in listing):
    sys.exit('A vehicle plugin JAR already exists; refusing duplicate or overwrite')
response = api(prefix + '/files/upload', method='POST')
upload_url = valid_url(response['data']['url'])
separator = '&' if '?' in upload_url else '?'
upload_url += separator + urllib.parse.urlencode({'directory': '/plugins'})
print('::add-mask::' + upload_url, flush=True)
boundary = '----falix-' + uuid.uuid4().hex
body = (f'--{boundary}\r\nContent-Disposition: form-data; name="files"; filename="{NAME}"\r\nContent-Type: application/java-archive\r\n\r\n'.encode() + jar + f'\r\n--{boundary}--\r\n'.encode())
request(upload_url, method='POST', data=body, headers={'Content-Type': 'multipart/form-data; boundary=' + boundary}, json_response=False)
print('::notice title=Falix upload::Upload request succeeded; checking directory')
listing = api(prefix + '/files?directory=%2Fplugins&limit=100')['data']
entry = next((x for x in listing if x.get('name') == NAME), None)
if entry is None:
    sys.exit('Upload accepted but JAR not found in plugins directory')
size = entry.get('size')
if not isinstance(size, int) or size != len(jar):
    sys.exit(f'Upload accepted but remote size was not verified (remote={size}, local={len(jar)})')
print('::notice title=Falix verification::JAR present in plugins with matching byte size; no restart or hash verification')
