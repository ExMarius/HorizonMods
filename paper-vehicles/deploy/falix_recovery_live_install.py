#!/usr/bin/env python3
"""Install a matching recovery JAR and pack on the authorized live test server."""
import hashlib, importlib.util, os, sys, uuid
from pathlib import Path
spec=importlib.util.spec_from_file_location('installer',Path(__file__).with_name('falix_install_horizon.py'))
i=importlib.util.module_from_spec(spec);spec.loader.exec_module(i)
f=i.f
i.OLD_PACK='cb74ea532786b8a81a0e096aef4a80541eb3e700'
i.OLD_CONFIG_SUFFIX='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-46003712699/HorizonOffRoader-1.21.4.zip'
OLD_JAR='33d1ad383981811aaa94188a4168787926a23bfc259983051365dbb74e4bbc1e'

def main():
    jar=f.verify_jar(Path(sys.argv[1])); pack=Path(sys.argv[2]).read_bytes(); url=sys.argv[3]
    api=f.Falix(f.login()); state=api.status()
    if state not in ('running','offline'):raise ValueError('Server transitioning; no installation performed')
    oldjar=api.download('/plugins/'+f.NAME)
    if f.sha(oldjar)!=OLD_JAR:raise ValueError('Installed JAR differs from expected; no installation performed')
    path='/plugins/MrCrayfishVehiclePlugin';oldconfig=api.download(path+'/config.yml')
    oldprops=i.properties(api);keys=['resource-pack','resource-pack-sha1','resource-pack-id','require-resource-pack']
    if any(k not in oldprops for k in keys) or oldprops['resource-pack-sha1'].lower()!=i.OLD_PACK:
        raise ValueError('Installed pack differs from expected; no installation performed')
    packsha=hashlib.sha1(pack).hexdigest();newconfig=i.replace_pack(oldconfig,url,packsha)
    newprops={'resource-pack':url,'resource-pack-sha1':packsha,'resource-pack-id':str(uuid.uuid5(uuid.NAMESPACE_URL,url)),'require-resource-pack':'true'}
    try:
        if api.download(path+'/config.yml')!=oldconfig or any(i.properties(api).get(k)!=oldprops[k] for k in keys):
            raise ValueError('Configuration changed before upload')
        api.upload(path,'config.yml',newconfig)
        if api.download(path+'/config.yml')!=newconfig:raise ValueError('Plugin config upload mismatch')
        api.api('/properties',{'properties':newprops},'PUT')
        if any(i.properties(api).get(k,'').lower()!=v.lower() for k,v in newprops.items()):raise ValueError('Pack properties mismatch')
        api.upload('/plugins',f.NAME,jar)
        if f.sha(api.download('/plugins/'+f.NAME))!=f.sha(jar):raise ValueError('JAR upload mismatch')
    except BaseException:
        try:
            api.upload('/plugins',f.NAME,oldjar);api.upload(path,'config.yml',oldconfig)
            api.api('/properties',{'properties':{k:oldprops[k] for k in keys}},'PUT')
            if f.sha(api.download('/plugins/'+f.NAME))!=OLD_JAR or api.download(path+'/config.yml')!=oldconfig or any(i.properties(api).get(k)!=oldprops[k] for k in keys):
                raise ValueError('Rollback not verified')
            f.notice('Rollback','Previous files and pack configuration restored')
        except BaseException:
            print('::error::Rollback not verified; inspect files before restart',flush=True)
        raise
    f.notice('Installed','JAR SHA-256 '+f.sha(jar)+'; pack SHA-1 '+packsha)
    if state=='running':
        if api.status()!='running':raise ValueError('Server state changed; restart not requested')
        api.api('/power',{'signal':'restart'},'POST')
        f.notice('Restart','Restart requested; confirm startup in Falix')
    else:f.notice('Restart','Server offline; changes apply at next start')
if __name__=='__main__':main()
