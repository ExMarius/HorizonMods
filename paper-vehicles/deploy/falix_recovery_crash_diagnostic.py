#!/usr/bin/env python3
import importlib.util,re
from pathlib import Path
spec=importlib.util.spec_from_file_location('f',Path(__file__).with_name('falix_auto_update.py'))
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);api=f.Falix(f.login())
f.notice('Server status',str(api.status()))
props={e['key']:str(e.get('value','')) for e in api.api('/properties') if isinstance(e,dict) and 'key' in e}
f.notice('Resource pack status',repr({k:props.get(k) for k in ('resource-pack','resource-pack-sha1','resource-pack-id','require-resource-pack')}))
config=api.download('/plugins/MrCrayfishVehiclePlugin/config.yml').decode('utf-8','replace')
m=re.search(r'(?ms)^resource-pack:[^\n]*\n((?:[ \t]+[^\n]*\n|\s*\n|\s*\#.*\n)*)',config)
f.notice('Plugin pack configuration',m.group(0).replace('%','%25') if m else 'not found')

for directory in ('/logs',):
    try:
        entries=[] if directory=='/logs' else api.api('/files?directory='+directory.replace('/','%2F')+'&limit=100')
        selected=[e for e in entries if isinstance(e,dict) and re.fullmatch(r'crash-[0-9_-]+-server\.txt',str(e.get('name','')))]
        selected=sorted(selected,key=lambda e:e['name'],reverse=True)[:2]
        paths=[directory+'/'+e['name'] for e in selected]
        if directory=='/logs':paths=['/logs/latest.log']
        for path in paths:
            text=api.download(path).decode('utf-8','replace').splitlines()
            relevant=[]
            for n,line in enumerate(text):
                if any(x in line for x in ('has stopped responding','Exception in server tick loop','Caused by:', 'Stacktrace:', 'Current Thread: Server thread', 'VehicleCollisionMover', 'LiveRecovery', 'LandVehicle.java', 'VehicleManager.java','recovery halted','Exception ticking world','OutOfMemoryError')):
                    relevant.extend(text[max(0,n-2):min(len(text),n+10)])
            relevant=[re.sub(r'\x1b\[[0-9;]*m','',s)[:350] for s in relevant[:100]]
            f.notice('Diagnostic '+path,' | '.join(relevant).replace('%','%25')[:60000] or 'No matching error lines')
    except BaseException as e:f.notice('Diagnostic read error',directory+' '+str(e))
