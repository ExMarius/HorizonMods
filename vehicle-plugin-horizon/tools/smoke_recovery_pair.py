#!/usr/bin/env python3
"""Disposable Paper paired-garage quit and restart probe."""
import hashlib,json,os,shutil,subprocess,sys,tempfile,time,urllib.request
from pathlib import Path
API='https://fill.papermc.io/v3/projects/paper/versions/1.21.4/builds'
HEADERS={'User-Agent':'Horizon-recovery-probe/1.0 (https://github.com/ExMarius/HorizonMods)'}
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS),timeout=90) as r:return r.read()
def main(jar,probe):
    builds=json.loads(get(API));build=max((b for b in builds if b.get('channel')=='STABLE'),key=lambda b:b['id'])
    download=build['downloads']['server:default'];paper=get(download['url'])
    if hashlib.sha256(paper).hexdigest()!=download['checksums']['sha256']:raise RuntimeError('Paper hash mismatch')
    with tempfile.TemporaryDirectory(prefix='recovery-probe-') as tmp:
        root=Path(tmp);(root/'paper.jar').write_bytes(paper);(root/'eula.txt').write_text('eula=true\n')
        (root/'server.properties').write_text('online-mode=false\ndifficulty=peaceful\nspawn-monsters=false\nserver-port=25578\nspawn-protection=0\nview-distance=3\nsimulation-distance=3\nlevel-type=minecraft:flat\n')
        (root/'plugins').mkdir();shutil.copyfile(jar,root/'plugins/MrCrayfishVehiclePlugin.jar');shutil.copyfile(probe,root/'plugins/RecoveryProbe.jar')
        log=root/'server.log'
        with log.open('w+') as out:
            proc=subprocess.Popen(['java','-Dhorizon.recovery.pairtest=true','-Xms512M','-Xmx1G','-jar','paper.jar','--nogui'],cwd=root,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
            try:
                deadline=time.monotonic()+240
                while time.monotonic()<deadline:
                    time.sleep(2);out.flush();text=log.read_text(errors='replace')
                    if proc.poll() is not None:raise RuntimeError('server exited')
                    if 'Done (' in text and '[RecoveryProbe] Enabling' in text:break
                else:raise RuntimeError('startup timeout')
                bot=subprocess.run(['node',str(Path(__file__).with_suffix('.cjs'))],capture_output=True,text=True,timeout=50)
                if bot.returncode:raise RuntimeError('bot failed: '+(bot.stdout+bot.stderr)[-2000:])
                out.flush();text=log.read_text(errors='replace')
                if 'RECOVERY_PAIR_QUIT_OK' not in text or 'RECOVERY_PROBE_FAIL' in text:raise RuntimeError('pair owner-quit test failed')
                if 'Could not pass event' in text or 'Exception in server tick loop' in text:raise RuntimeError('server reported event/tick error')
                proc.stdin.write('stop\n');proc.stdin.flush();proc.wait(timeout=90)
                restartlog=root/'server-restart.log'
                with restartlog.open('w+') as restarted:
                    proc=subprocess.Popen(['java','-Dhorizon.recovery.pairtest=true','-Xms512M','-Xmx1G','-jar','paper.jar','--nogui'],cwd=root,stdin=subprocess.PIPE,stdout=restarted,stderr=subprocess.STDOUT,text=True)
                    deadline=time.monotonic()+240
                    while time.monotonic()<deadline:
                        time.sleep(2);restarted.flush(); restarttext=restartlog.read_text(errors='replace')
                        if proc.poll() is not None:raise RuntimeError('restart exited: '+restarttext[-4000:])
                        if 'Done (' in restarttext and '[RecoveryProbe] Enabling' in restarttext:break
                    else:raise RuntimeError('restart startup timeout')
                    env={**os.environ,'RECOVERY_PAIR_RESTART':'1'}
                    bot=subprocess.run(['node',str(Path(__file__).with_suffix('.cjs'))],capture_output=True,text=True,timeout=30,env=env)
                    restarted.flush();restarttext=restartlog.read_text(errors='replace')
                    if bot.returncode or any('RECOVERY_PAIR_RESTART_OK '+n not in restarttext for n in ('RecoveryOwnerBot','RecoveryProbeBot')) or 'RECOVERY_PROBE_FAIL' in restarttext:
                        raise RuntimeError('restart garage verification failed: '+(restarttext+bot.stdout+bot.stderr)[-5000:])
                    proc.stdin.write('stop\n');proc.stdin.flush();proc.wait(timeout=90)
                print('Disposable owner quit during loading returned both to owners garages; graceful restart verified.')
            except Exception:
                out.flush();print('--- server log ---\n'+log.read_text(errors='replace')[-12000:],file=sys.stderr);raise
            finally:
                if proc.poll() is None:proc.kill();proc.wait()
if __name__=='__main__':main(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve())
