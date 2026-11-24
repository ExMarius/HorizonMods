#!/usr/bin/env python3
"""Install the opt-in 1.21.4 sync experiment over the verified November JAR."""
import importlib.util
import os
import urllib.parse
from pathlib import Path
import sys

spec=importlib.util.spec_from_file_location('falix', Path(__file__).with_name('falix_auto_update.py'))
f=importlib.util.module_from_spec(spec); spec.loader.exec_module(f)
BASELINE='cdc946652883d728ed5413d97cbcc968f4cce0486772087c9da89da683fd54b3'

def main():
    run=os.environ.get('GITHUB_RUN_ID','')
    if not run.isdecimal(): f.abort('Invalid run id')
    jar=f.verify_jar(Path(sys.argv[1])); api=f.Falix(f.login())
    old=api.download('/plugins/'+f.NAME)
    if f.sha(old)!=BASELINE: f.abort('Installed JAR does not match November release; no changes made')
    names={'config.yml','dealer.yml','gas_pumps.yml','mechanics.yml','trailers.yml','vehicles.yml'}
    listing=api.api('/files?'+urllib.parse.urlencode({'directory':'/plugins/MrCrayfishVehiclePlugin','limit':100}))
    if {x.get('name') for x in listing if isinstance(x,dict)} != names: f.abort('Unexpected plugin data; backup manually')
    for name in sorted(names):
        data=api.download('/plugins/MrCrayfishVehiclePlugin/'+name)
        backup=f'mcv-sync-{run}-{name}.bak'
        api.upload('/',backup,data)
        if f.sha(api.download('/'+backup))!=f.sha(data): f.abort('Data backup failed; JAR unchanged')
    f.notice('Backup','Plugin data backed up and verified before experiment')
    f.deploy(api,jar,run)
if __name__=='__main__': main()
