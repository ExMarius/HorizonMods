#!/usr/bin/env python3
"""Run disposable Paper + offline client; no visual or production-server changes."""
import hashlib, json, os, shutil, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
API='https://fill.papermc.io/v3/projects/paper/versions/1.21.4/builds'
HEADERS={'User-Agent':'tractor-trailer-smoke/1.0 (https://github.com/ExMarius/HorizonMods)'}
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS),timeout=90) as r: return r.read()
def main(jar):
    builds=json.loads(get(API)); stable=[b for b in builds if b.get('channel')=='STABLE']
    build=max(stable,key=lambda b:b['id']); download=build['downloads']['server:default']
    paper=get(download['url'])
    if hashlib.sha256(paper).hexdigest()!=download['checksums']['sha256']: raise RuntimeError('Paper hash mismatch')
    with tempfile.TemporaryDirectory(prefix='tractor-trailer-smoke-') as tmp:
        root=Path(tmp); (root/'paper.jar').write_bytes(paper); (root/'eula.txt').write_text('eula=true\n')
        (root/'server.properties').write_text('online-mode=false\ndifficulty=peaceful\nspawn-monsters=false\nserver-port=25568\nspawn-protection=0\nview-distance=3\nsimulation-distance=3\nlevel-type=minecraft:flat\nresource-pack=https://github.com/ExMarius/MrCrayfishVehicleMod/releases/download/paper-plugin/MrCrayfishVehiclePlugin-resource-pack-1.21.4-r39.zip\nresource-pack-sha1=d1b55da29e79f91f2299c40c3f7413656f349ff4\nrequire-resource-pack=false\n')
        (root/'plugins').mkdir(); shutil.copyfile(jar,root/'plugins/MrCrayfishVehiclePlugin.jar')
        log=root/'server.log'
        with log.open('w+') as out:
            proc=subprocess.Popen(['java','-Xms512M','-Xmx1G','-jar','paper.jar','--nogui'],cwd=root,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
            try:
                deadline=time.monotonic()+240
                while time.monotonic()<deadline:
                    time.sleep(2); out.flush(); text=log.read_text(errors='replace')
                    if proc.poll() is not None: raise RuntimeError('server exited before startup')
                    if 'Done (' in text and 'Vehicle plugin enabled.' in text: break
                else: raise RuntimeError('startup timeout')
                proc.stdin.write('op HorizonBot\n'); proc.stdin.flush(); time.sleep(2)
                bot=subprocess.run(['node',str(Path(__file__).with_suffix('.cjs'))],capture_output=True,text=True,timeout=125)
                if bot.returncode:
                    out.flush();lines=log.read_text(errors='replace').splitlines()
                    print('BOT DIAGNOSTIC:',bot.stdout,bot.stderr,flush=True)
                    print('KEY SERVER EVENTS:',*[line for line in lines if any(x in line for x in ('HorizonBot','UTB','vehicle','ERROR','Watchdog'))][-35:],sep='\n',flush=True)
                    for i,line in enumerate(lines):
                        if 'Current Thread: Server thread' in line:
                            print('SERVER THREAD:',*lines[i:i+25],sep='\n',flush=True);break
                    raise RuntimeError('bot failed: '+(bot.stdout+bot.stderr)[-2500:])
                print(bot.stdout,flush=True)
                proc.stdin.write('stop\n'); proc.stdin.flush(); proc.wait(timeout=90)
                out.flush(); text=log.read_text(errors='replace')
                data=(root/'plugins/MrCrayfishVehiclePlugin/vehicles.yml').read_text()
                garage=root/'plugins/MrCrayfishVehiclePlugin/garages.yml'
                garage_data=garage.read_text() if garage.exists() else ''
                if 'utb_650' not in data and 'utb_650' not in garage_data:
                    print('BOT DIAGNOSTIC:',bot.stdout,bot.stderr,flush=True)
                    print('Active data:',data,'Garage data:',garage_data,flush=True)
                    lines=text.splitlines()
                    print('MOUNT STATE:',*[line for line in lines if '[UTB dismount diagnostic]' in line],sep='\n',flush=True)
                    for i,line in enumerate(lines):
                        if 'Current Thread: Server thread' in line:
                            print('SERVER THREAD:',*lines[i:i+32],sep='\n',flush=True)
                            break
                    print('Relevant server lines:',*[line for line in lines if any(x in line.lower() for x in ('utb','vehicle','horizonbot','garaj','watchdog'))][:30],sep='\n',flush=True)
                    raise RuntimeError('vehicle missing from both active and garage persisted data')
                print('Persisted in '+('active vehicles' if 'utb_650' in data else 'garage'),flush=True)
                trailers=(root/'plugins/MrCrayfishVehiclePlugin/trailers.yml').read_text()
                if 'tractor_trailer' not in trailers or 'DIAMOND' not in trailers: raise RuntimeError('trailer or cargo missing from saved data')
                print('Trailer cargo persisted.',flush=True)
                if 'Could not pass event' in text or 'Exception in server tick loop' in text: raise RuntimeError('server reported event or tick failure')
                print('Vehicle save verified; restarting disposable server.',flush=True)
                proc=subprocess.Popen(['java','-Xms512M','-Xmx1G','-jar','paper.jar','--nogui'],cwd=root,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
                deadline=time.monotonic()+240
                start_at=len(text)
                while time.monotonic()<deadline:
                    time.sleep(2); out.flush(); newlog=log.read_text(errors='replace')[start_at:]
                    if proc.poll() is not None: raise RuntimeError('server exited during restart')
                    if 'Done (' in newlog and 'Loaded 1 trailer(s).' in newlog and ('vehicle(s);' in newlog or 'stored in garages.' in newlog): break
                else: raise RuntimeError('persisted vehicle did not load after restart')
                proc.stdin.write('stop\n'); proc.stdin.flush(); proc.wait(timeout=90)
                out.flush(); newlog=log.read_text(errors='replace')[start_at:]
                if 'Could not pass event' in newlog or 'Exception in server tick loop' in newlog: raise RuntimeError('server reported error after reload')
                if 'Loaded 1 trailer(s).' not in newlog: raise RuntimeError('trailer not loaded after restart')
                print('Saved vehicle and trailer loaded after clean restart.')
            except Exception:
                out.flush(); print('-----server log tail-----\n'+log.read_text(errors='replace')[-10000:],file=sys.stderr)
                raise
            finally:
                if proc.poll() is None: proc.kill(); proc.wait()
if __name__=='__main__': main(Path(sys.argv[1]).resolve())
