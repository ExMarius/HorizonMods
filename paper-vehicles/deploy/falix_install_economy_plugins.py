#!/usr/bin/env python3
"""Install requested Vault + EssentialsX core without overwriting existing plugins."""
import importlib.util, re, sys, urllib.parse, zipfile
from pathlib import Path
spec=importlib.util.spec_from_file_location('falix',Path(__file__).with_name('falix_auto_update.py'))
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
files=[(Path(sys.argv[1]),'EssentialsX-2.22.0.jar','Essentials'),(Path(sys.argv[2]),'Vault-1.7.3.jar','Vault')]
for path,_,name in files:
    with zipfile.ZipFile(path) as z:
        yml=z.read('plugin.yml').decode('utf8')
        if not re.search(r'(?m)^name:\s*["\']?'+re.escape(name)+r'["\']?\s*$',yml):
            raise ValueError('Unexpected plugin identity: '+name)
api=f.Falix(f.login())
if api.status() not in ('running','offline','sleeping'):raise ValueError('Server transitioning')
entries=api.api('/files?'+urllib.parse.urlencode({'directory':'/plugins','limit':1000}))
names=[str(e.get('name','')) for e in entries if isinstance(e,dict)]
# Do not silently add a competing economy provider or a second copy.
if any(re.match(r'(?i)^(cmi|cmi-injector|the?new?economy|craftconomy|iconomy|essentialsx?economy)(?:[-_.].*)?\.jar$',n) for n in names):
    raise ValueError('Another possible economy provider is installed; inspect before installing EssentialsX')
for path,filename,plugin in files:
    pattern=r'(?i)^vault(?:[-_.].*)?\.jar$' if plugin=='Vault' else r'(?i)^essentials(?:x)?(?:[-_.]?[0-9].*)?\.jar$'
    matches=[n for n in names if re.match(pattern,n)]
    if matches:
        f.notice(plugin, 'Already present; left unchanged: '+', '.join(matches));continue
    content=path.read_bytes()
    if len(content)>f.MAX_FILE:raise ValueError('Plugin too large')
    api.upload('/plugins',filename,content)
    if f.sha(api.download('/plugins/'+filename))!=f.sha(content):raise ValueError('Upload verification failed: '+plugin)
    f.notice(plugin,'Installed '+filename+' SHA-256 '+f.sha(content)+'; restart required')
