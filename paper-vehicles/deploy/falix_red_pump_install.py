#!/usr/bin/env python3
"""Install a pump-only pack while retaining and verifying the current JAR."""
import hashlib, importlib.util, os, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location('cab', Path(__file__).with_name('falix_recovery_cab_install.py'))
cab = importlib.util.module_from_spec(spec); spec.loader.exec_module(cab)
old, new = (Path(p).read_bytes() for p in sys.argv[2:4])
url = sys.argv[4] if len(sys.argv) > 4 else ''
cab.OLD_JAR = '888c780b292c852e13ba84478a361f7e71dbcd4d8ac012d32ba50660a7a8f8d1'
cab.OLD_PACK = hashlib.sha1(old).hexdigest()
cab.OLD_URL = 'https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-46057404122/HorizonOffRoader-1.21.4.zip'
cab.i.OLD_PACK = cab.OLD_PACK
cab.i.OLD_CONFIG_SUFFIX = cab.OLD_URL
run = os.environ['GITHUB_RUN_ID']
if not run.isdecimal(): raise ValueError('Invalid run ID')
api = cab.f.Falix(cab.f.login())
if sys.argv[1] == 'backup':
    cab.backup(api, old, run)
elif sys.argv[1] == 'install':
    jar = api.download('/plugins/' + cab.f.NAME)
    if cab.f.sha(jar) != cab.OLD_JAR: raise ValueError('Installed JAR differs')
    cab.install(api, jar, new, url, run)
else:
    raise ValueError('Unknown action')
