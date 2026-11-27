#!/usr/bin/env python3
"""Back up and replace the approved recovery cab on the authorized test server."""
import hashlib, importlib.util, io, json, os, sys, uuid, zipfile
from pathlib import Path
spec=importlib.util.spec_from_file_location('i',Path(__file__).with_name('falix_install_horizon.py'))
i=importlib.util.module_from_spec(spec);spec.loader.exec_module(i);f=i.f
OLD_JAR='fdbe986f14610bb23dfe3bef8b41d4251ce8add4f28c005d2f12381a41231129'
OLD_PACK='f9a1979f20b1103bb6be770afa5bc1d5a9284a60'
OLD_URL='https://github.com/ExMarius/HorizonMods/releases/download/horizon-offroader-46055037372/HorizonOffRoader-1.21.4.zip'
CONFIG='/plugins/MrCrayfishVehiclePlugin/config.yml'
KEYS=('resource-pack','resource-pack-sha1','resource-pack-id','require-resource-pack')
i.OLD_PACK=OLD_PACK;i.OLD_CONFIG_SUFFIX=OLD_URL

def normalize(key,value):
    return value.replace('\\','') if key == 'resource-pack' else value

def current(api):
    state=api.status()
    if state not in ('running','offline','sleeping'):raise ValueError('Server transitioning; refusing update')
    jar=api.download('/plugins/'+f.NAME);config=api.download(CONFIG);props=i.properties(api)
    if f.sha(jar)!=OLD_JAR:raise ValueError('Installed JAR differs; refusing update')
    if any(k not in props for k in KEYS) or props['resource-pack-sha1'].lower()!=OLD_PACK or normalize('resource-pack',props['resource-pack'])!=OLD_URL:
        raise ValueError('Installed resource pack differs; refusing update')
    return jar,config,{k:props[k] for k in KEYS}

def backup(api,oldpack,run):
    if hashlib.sha1(oldpack).hexdigest()!=OLD_PACK:raise ValueError('Old resource pack does not match server')
    jar,config,props=current(api);properties=api.download('/server.properties')
    data=io.BytesIO()
    with zipfile.ZipFile(data,'w',zipfile.ZIP_DEFLATED) as z:
        for name,content in [('MrCrayfishVehiclePlugin.jar',jar),('config.yml',config),('server.properties',properties),('HorizonOffRoader-1.21.4.zip',oldpack)]:z.writestr(name,content)
        z.writestr('backup-info.json',json.dumps({'previous_jar_sha256':OLD_JAR,'previous_pack_sha1':OLD_PACK,'previous_pack_url':OLD_URL,'properties_api':props,'previous_live_sources_commit':'e40e067ac7dbdb009340df6f80c068204a328545'},indent=2))
    content=data.getvalue();name='mcv-before-new-recovery-cab-'+run+'.zip.bak'
    api.upload('/',name,content)
    if f.sha(api.download('/'+name))!=f.sha(content):raise ValueError('Backup checksum mismatch; installation refused')
    Path('/tmp/recovery-cab-backup.sha').write_text(f.sha(content))
    f.notice('Backup','/'+name+' SHA-256 '+f.sha(content))

def install(api,jar,newpack,url,run):
    name='mcv-before-new-recovery-cab-'+run+'.zip.bak'
    backed=api.download('/'+name)
    if f.sha(backed)!=Path('/tmp/recovery-cab-backup.sha').read_text().strip():raise ValueError('Verified backup missing or changed')
    oldjar,oldconfig,oldprops=current(api)
    with zipfile.ZipFile(io.BytesIO(backed)) as z:
        if z.read('MrCrayfishVehiclePlugin.jar')!=oldjar or z.read('config.yml')!=oldconfig:raise ValueError('Server changed since backup')
        recorded=json.loads(z.read('backup-info.json'))
        if recorded['properties_api']!=oldprops:raise ValueError('Pack configuration changed since backup')
    newsha=hashlib.sha1(newpack).hexdigest();newconfig=i.replace_pack(oldconfig,url,newsha)
    newprops={'resource-pack':url,'resource-pack-sha1':newsha,'resource-pack-id':str(uuid.uuid5(uuid.NAMESPACE_URL,url)),'require-resource-pack':'true'}
    try:
        api.upload('/plugins/MrCrayfishVehiclePlugin','config.yml',newconfig)
        if api.download(CONFIG)!=newconfig:raise ValueError('Plugin config upload mismatch')
        api.api('/properties',{'properties':newprops},'PUT')
        if any(normalize(k,i.properties(api).get(k,'')).lower()!=normalize(k,v).lower() for k,v in newprops.items()):raise ValueError('Pack properties mismatch')
        api.upload('/plugins',f.NAME,jar)
        if f.sha(api.download('/plugins/'+f.NAME))!=f.sha(jar):raise ValueError('JAR upload mismatch')
    except BaseException:
        try:
            api.upload('/plugins',f.NAME,oldjar);api.upload('/plugins/MrCrayfishVehiclePlugin','config.yml',oldconfig)
            api.api('/properties',{'properties':{k:normalize(k,v) for k,v in oldprops.items()}},'PUT')
            if f.sha(api.download('/plugins/'+f.NAME))!=OLD_JAR or api.download(CONFIG)!=oldconfig or any(normalize(k,i.properties(api).get(k,''))!=normalize(k,oldprops[k]) for k in KEYS):raise ValueError('Rollback mismatch')
            f.notice('Rollback','Previous plugin, config and pack settings restored')
        except BaseException:print('::error::Rollback not verified. Inspect files before restarting.',flush=True)
        raise
    f.notice('Installed','JAR SHA-256 '+f.sha(jar)+'; resource pack SHA-1 '+newsha+'; restart required')

if __name__=='__main__':
    run=os.environ.get('GITHUB_RUN_ID','')
    if not run.isdecimal():raise ValueError('Invalid run ID')
    api=f.Falix(f.login())
    if sys.argv[1]=='backup':backup(api,Path(sys.argv[2]).read_bytes(),run)
    elif sys.argv[1]=='install':install(api,f.verify_jar(Path(sys.argv[2])),Path(sys.argv[3]).read_bytes(),sys.argv[4],run)
    else:raise ValueError('Unknown action')
