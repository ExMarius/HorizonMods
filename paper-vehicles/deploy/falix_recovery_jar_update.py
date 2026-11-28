#!/usr/bin/env python3
"""Replace only the recovery plugin JAR, after a verified offline backup."""
import importlib.util
import os
import sys
from pathlib import Path

spec=importlib.util.spec_from_file_location('backup',Path(__file__).with_name('falix_recovery_backup.py'))
backup=importlib.util.module_from_spec(spec);spec.loader.exec_module(backup)
f=backup.f
# Values audited on the running server immediately before preparing this update.
backup.EXPECTED_JAR='3af583848bdcd4d3332b8b986f993b0693af8616a6b08ae006437eb640eca38e'
backup.EXPECTED_PACK='cb74ea532786b8a81a0e096aef4a80541eb3e700'

def install(api, jar, oldpack, run):
    if not run.isdecimal():raise ValueError('Invalid run ID')
    if api.status()!='offline':raise ValueError('Server is not offline; no installation performed')
    # Full plugin folder, the current JAR, server.properties and installed pack.
    backup.backup(api,oldpack,'offline',run)
    if api.status()!='offline':raise ValueError('Server started after backup; no installation performed')
    old=api.download('/plugins/'+f.NAME)
    if f.sha(old)!=backup.EXPECTED_JAR:raise ValueError('Installed plugin changed; no installation performed')
    try:
        if api.status()!='offline':raise ValueError('Server started before upload')
        api.upload('/plugins',f.NAME,jar)
        if f.sha(api.download('/plugins/'+f.NAME))!=f.sha(jar):raise ValueError('Uploaded JAR checksum mismatch')
        if api.status()!='offline':raise ValueError('Server started during upload; inspect before use')
    except BaseException:
        try:
            if api.status()!='offline':raise ValueError('Server not offline; automatic rollback unsafe')
            api.upload('/plugins',f.NAME,old)
            if f.sha(api.download('/plugins/'+f.NAME))!=f.sha(old):raise ValueError('Rollback checksum mismatch')
            f.notice('Rollback','Previous JAR restored and verified')
        except BaseException:
            f.notice('Rollback warning','Could not verify rollback; keep server stopped and inspect files')
        raise
    f.notice('Installed','JAR verified SHA-256 '+f.sha(jar)+'; resource pack unchanged')

if __name__=='__main__':
    jar=f.verify_jar(Path(sys.argv[1]));pack=Path(sys.argv[2]).read_bytes()
    install(f.Falix(f.login()),jar,pack,os.environ.get('GITHUB_RUN_ID',''))
