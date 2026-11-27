#!/usr/bin/env python3
import importlib.util,re
from pathlib import Path
spec=importlib.util.spec_from_file_location('f',Path(__file__).with_name('falix_auto_update.py'))
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);api=f.Falix(f.login())
# Emit the latest opt-in measurement before other notices: GitHub caps annotations
# per step and truncates individual messages. Compression preserves the samples.
try:
    import base64, gzip
    lines=api.download('/logs/latest.log').decode('utf-8','replace').splitlines()
    seat=[line.split('[SeatMeasure] ',1)[1] for line in lines if '[SeatMeasure] ' in line]
    starts=[i for i,line in enumerate(seat) if line.startswith('BEGIN ')]
    if starts:
        latest=seat[starts[-1]:]
        if not latest[-1].startswith('END'):
            f.notice('Seat measurement', 'Incomplete session')
        else:
            encoded=base64.b64encode(gzip.compress(('\n'.join(latest)).encode())).decode()
            chunks=[encoded[i:i+3000] for i in range(0,len(encoded),3000)]
            if len(chunks) > 9:
                f.notice('Seat measurement', 'Measurement too large to export safely in annotations')
            else:
                for i,chunk in enumerate(chunks,1):
                    f.notice(f'Seat measurement {i:02}/{len(chunks):02}',chunk)
    else:
        f.notice('Seat measurement', 'No completed measurement in latest.log')
except BaseException as e:
    f.notice('Seat measurement error',str(e))

# Check only for packet-library filenames; this does not prove the plugins loaded.
try:
    response=api.api('/files?directory=%2Fplugins&limit=100')
    entries=response.get('data', []) if isinstance(response,dict) else response
    names=[str(e.get('name','')).lower() for e in entries if isinstance(e,dict)]
    protocols=any(re.fullmatch(r'protocollib(?:[-_.].*)?\.jar',n) for n in names)
    events=any(re.fullmatch(r'packetevents(?:[-_.].*)?\.jar',n) for n in names)
    f.notice('Packet libraries', f'ProtocolLib jar={protocols}; PacketEvents jar={events}; listing count={len(names)}; enabled state not checked')
except BaseException as e:
    f.notice('Packet libraries', 'Directory lookup failed: '+str(e))

f.notice('Server status',str(api.status()))
props={e['key']:str(e.get('value','')) for e in api.api('/properties') if isinstance(e,dict) and 'key' in e}
f.notice('Resource pack status',repr({k:props.get(k) for k in ('resource-pack','resource-pack-sha1','resource-pack-id','require-resource-pack')}))
config=api.download('/plugins/MrCrayfishVehiclePlugin/config.yml').decode('utf-8','replace')
m=re.search(r'(?ms)^resource-pack:[^\n]*\n((?:[ \t]+[^\n]*\n|\s*\n|\s*\#.*\n)*)',config)
f.notice('Plugin pack configuration',repr(m.group(0)).replace('%','%25') if m else 'not found')

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

# Read-only timer diagnosis: do not print player names or vehicle data.
for key in ('pause-when-empty-seconds', 'simulation-distance', 'view-distance'):
    f.notice('Timer diagnostic property', key+'='+str(props.get(key, '(not present)')))
try:
    lines=api.download('/logs/latest.log').decode('utf-8','replace').splitlines()
    needles=('Pausing dedicated server', 'Server empty for', 'Unpausing dedicated server',
             'Recovery operations disabled', 'startup recovery deferred',
             'Could not atomically save vehicles.yml', 'Startup recovery:', '[CameraTest]')
    matches=[re.sub(r'\x1b\[[0-9;]*m','',line)[:400] for line in lines if any(n.lower() in line.lower() for n in needles)]
    f.notice('Timer diagnostic events', ' | '.join(matches[-20:]).replace('%','%25') or 'No matching events in latest.log')
except BaseException as e:
    f.notice('Timer diagnostic read error',str(e))
