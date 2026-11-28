#!/usr/bin/env python3
"""Enable the existing 1.21.4 vehicle pack on one authorized Falix server."""
import hashlib
import importlib.util
import sys
import time
import urllib.request
import uuid
import zipfile
from pathlib import Path

p = Path(__file__).with_name('falix_auto_update.py')
spec = importlib.util.spec_from_file_location('falix', p)
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)
URL = 'https://github.com/ExMarius/MrCrayfishVehicleMod/releases/download/paper-plugin/MrCrayfishVehiclePlugin-resource-pack-1.21.4-r39.zip'
SHA1 = 'd1b55da29e79f91f2299c40c3f7413656f349ff4'
SHA256 = 'f1d0b35cb54c8c8a0f6bfb323183d3448c528ada52919bfd94bcf2df7167f7ea'

def properties(api):
    result = api.api('/properties')
    if not isinstance(result, list): f.abort('Unexpected properties response')
    return {x['key']: str(x.get('value', '')) for x in result if isinstance(x,dict) and isinstance(x.get('key'), str)}

def main():
    path=Path(sys.argv[1]); data=path.read_bytes()
    if hashlib.sha256(data).hexdigest() != SHA256 or hashlib.sha1(data).hexdigest() != SHA1:
        f.abort('Public pack checksum mismatch; no change made')
    with zipfile.ZipFile(path) as z:
        import json
        if json.loads(z.read('pack.mcmeta'))['pack']['pack_format'] != 46 or z.testzip() is not None:
            f.abort('Pack format or ZIP invalid')
    f.notice('Resource pack', 'Public release downloaded and SHA-1/SHA-256 verified; format 46')
    api=f.Falix(f.login())
    versions=api.api('/files?directory=%2Fversions&limit=100')
    if not any(x.get('name')=='1.21.4' for x in versions): f.abort('Server is not confirmed as 1.21.4')
    old=properties(api)
    if old.get('resource-pack','').strip() not in ('', URL): f.abort('Another pack is configured; refusing to overwrite it')
    values={'resource-pack':URL,'resource-pack-sha1':SHA1,'resource-pack-id':str(uuid.uuid5(uuid.NAMESPACE_URL, URL)), 'require-resource-pack':'true'}
    api.api('/properties', {'properties':values}, 'PUT')
    current=properties(api)
    if any(current.get(k,'').lower() != v.lower() for k,v in values.items()): f.abort('Pack properties could not be verified after write; no restart requested')
    f.notice('Resource pack', 'Server properties updated and verified; pack is offered on login')
    state=api.status()
    if state=='offline':
        f.notice('Restart', 'Server offline; changes take effect on next start')
        return
    if state!='running': f.abort('Server transitioning; pack saved but restart not requested')
    api.api('/power', {'signal':'restart'}, 'POST')
    f.notice('Restart', 'Falix accepted restart; waiting for transition')
    transitioned=False
    for _ in range(36):
        time.sleep(5); current=api.status()
        if current in ('stopping','starting','offline'): transitioned=True
        if current=='running' and transitioned:
            f.notice('Restart', 'Server running after restart; client must rejoin to test pack')
            return
    f.abort('Restart accepted but not confirmed; check Falix panel')
if __name__=='__main__': main()
