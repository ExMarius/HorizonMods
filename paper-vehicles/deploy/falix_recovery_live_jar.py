#!/usr/bin/env python3
"""One-time restore of verified checkpoint JAR; never restores player data."""
import importlib.util
import io
import zipfile
from pathlib import Path

spec = importlib.util.spec_from_file_location('falix', Path(__file__).with_name('falix_auto_update.py'))
f = importlib.util.module_from_spec(spec); spec.loader.exec_module(f)
api = f.Falix(f.login())
if api.status() not in ('running', 'offline', 'sleeping'):
    raise ValueError('Server transitioning; restore refused')
backup = api.download('/mcv-plugin-checkpoint-46074236579.zip.bak')
if f.sha(backup) != '1147c3f285b73dd2e9b25a195e01b9051e15d35172419e21965bc6d6a9d29191':
    raise ValueError('Checkpoint checksum mismatch; restore refused')
with zipfile.ZipFile(io.BytesIO(backup)) as archive:
    jar = archive.read('plugins/' + f.NAME)
if f.sha(jar) != '27342358346aea9e2b67d4e8ecc3ce99b75fdccb52efc6629f0f84261d980b2b':
    raise ValueError('Checkpoint JAR checksum mismatch; restore refused')
old = api.download('/plugins/' + f.NAME)
if f.sha(old) != '65cf8139aac3f7dd03cffbf159d719248f265adf5481542e4cd4780cee8e3e5f':
    raise ValueError('Installed JAR differs from expected; restore refused')
try:
    api.upload('/plugins', f.NAME, jar)
    if f.sha(api.download('/plugins/' + f.NAME)) != f.sha(jar):
        raise ValueError('Restored JAR verification failed')
except BaseException:
    try:
        api.upload('/plugins', f.NAME, old)
        if f.sha(api.download('/plugins/' + f.NAME)) != f.sha(old):
            raise ValueError('Rollback verification failed')
        f.notice('Rollback', 'Previous JAR restored and verified')
    except BaseException:
        print('::error::Rollback not verified; inspect before restart', flush=True)
    raise
f.notice('Checkpoint JAR restored', 'SHA-256 ' + f.sha(jar) + '; player data and properties unchanged; manual restart required')
