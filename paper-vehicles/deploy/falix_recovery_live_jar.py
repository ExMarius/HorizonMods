#!/usr/bin/env python3
"""Upload recovery JAR to the test server; user restarts in Falix."""
import importlib.util,sys
from pathlib import Path
spec=importlib.util.spec_from_file_location('falix',Path(__file__).with_name('falix_auto_update.py'))
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
jar=f.verify_jar(Path(sys.argv[1]));api=f.Falix(f.login())
if api.status() not in ('running','offline','sleeping'):raise ValueError('Server transitioning; upload refused')
old=api.download('/plugins/'+f.NAME)
if f.sha(old)!='90aa3a1b62448fa736994d365a2e543fbd97dfcd05f20683ddfc29b61502eeb8':raise ValueError('Installed JAR differs from expected; upload refused')
try:
    api.upload('/plugins',f.NAME,jar)
    if f.sha(api.download('/plugins/'+f.NAME))!=f.sha(jar):raise ValueError('Uploaded JAR checksum mismatch')
except BaseException:
    try:
        api.upload('/plugins',f.NAME,old)
        if f.sha(api.download('/plugins/'+f.NAME))!=f.sha(old):raise ValueError('Rollback mismatch')
        f.notice('Rollback','Previous JAR restored')
    except BaseException:print('::error::Rollback not verified; inspect before restart',flush=True)
    raise
f.notice('Installed','JAR SHA-256 '+f.sha(jar)+'; user must restart the server')
