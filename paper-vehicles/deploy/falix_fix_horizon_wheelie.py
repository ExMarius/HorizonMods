#!/usr/bin/env python3
"""Install wheelie fix only over the confirmed Horizon release and pack."""
import importlib.util, os, sys, urllib.parse
from pathlib import Path
spec=importlib.util.spec_from_file_location('falix', Path(__file__).with_name('falix_auto_update.py'))
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
JAR_SHA='3d45d95a43ccd4875dd019510b70d8a5124f18aa257d3db98b41469c848d596f'
PACK_SHA='ca0413462ebbbc2fde1b8c2f1cfaf43620709661'
NAMES={'config.yml','dealer.yml','gas_pumps.yml','mechanics.yml','trailers.yml','vehicles.yml'}
def main():
    run=os.environ.get('GITHUB_RUN_ID','')
    if not run.isdecimal(): f.abort('Invalid run id')
    jar=f.verify_jar(Path(sys.argv[1])); api=f.Falix(f.login())
    if f.sha(api.download('/plugins/'+f.NAME))!=JAR_SHA: f.abort('Installed JAR differs from expected Horizon release')
    props={v['key']:str(v.get('value','')) for v in api.api('/properties') if isinstance(v,dict) and 'key' in v}
    if props.get('resource-pack-sha1','').lower()!=PACK_SHA: f.abort('Server pack differs from Horizon release')
    listing=api.api('/files?'+urllib.parse.urlencode({'directory':'/plugins/MrCrayfishVehiclePlugin','limit':100}))
    if {x.get('name') for x in listing if isinstance(x,dict)}!=NAMES: f.abort('Unexpected plugin files')
    for n in sorted(NAMES):
        data=api.download('/plugins/MrCrayfishVehiclePlugin/'+n); backup=f'mcv-wheelie-{run}-{n}.bak'
        api.upload('/',backup,data)
        if f.sha(api.download('/'+backup))!=f.sha(data): f.abort('Data backup verification failed')
    f.notice('Backup','Six plugin data files backed up and verified; pack unchanged')
    if f.sha(api.download('/plugins/'+f.NAME))!=JAR_SHA: f.abort('JAR changed during backup')
    f.deploy(api,jar,run)
if __name__=='__main__': main()
