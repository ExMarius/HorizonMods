#!/usr/bin/env python3
"""Drive a real registered recovery rig using Paper and a disposable client."""
import hashlib,json,os,shutil,subprocess,sys,tempfile,time,urllib.request
from pathlib import Path
from recovery_log_check import assert_clean
API='https://fill.papermc.io/v3/projects/paper/versions/1.21.4/builds'
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Horizon-drive-probe/1.0 (https://github.com/ExMarius/HorizonMods)'}),timeout=90) as r:return r.read()
def main(jar,probe):
    build=max((b for b in json.loads(get(API)) if b.get('channel')=='STABLE'),key=lambda b:b['id'])
    download=build['downloads']['server:default'];paper=get(download['url'])
    if hashlib.sha256(paper).hexdigest()!=download['checksums']['sha256']:raise RuntimeError('Paper hash mismatch')
    with tempfile.TemporaryDirectory(prefix='recovery-drive-') as tmp:
        root=Path(tmp);(root/'paper.jar').write_bytes(paper);(root/'eula.txt').write_text('eula=true\n')
        (root/'server.properties').write_text('online-mode=false\ndifficulty=peaceful\nspawn-monsters=false\nserver-port=25579\nspawn-protection=0\ngenerate-structures=false\nview-distance=3\nsimulation-distance=3\nlevel-type=minecraft:flat\n')
        (root/'plugins').mkdir();shutil.copyfile(jar,root/'plugins/MrCrayfishVehiclePlugin.jar');shutil.copyfile(probe,root/'plugins/RecoveryDriveProbe.jar')
        log=root/'server.log'
        with log.open('w+') as out:
            proc=subprocess.Popen(['java','-Xms512M','-Xmx1G','-jar','paper.jar','--nogui'],cwd=root,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
            try:
                deadline=time.monotonic()+240
                while time.monotonic()<deadline:
                    time.sleep(2);out.flush();text=log.read_text(errors='replace')
                    if proc.poll() is not None:raise RuntimeError('server exited')
                    if 'Done (' in text and '[RecoveryDriveProbe] Enabling' in text:break
                else:raise RuntimeError('startup timeout')
                bot=subprocess.run(['node',str(Path(__file__).with_suffix('.cjs'))],capture_output=True,text=True,timeout=55)
                out.flush();text=log.read_text(errors='replace')
                if bot.returncode or any(s not in text for s in ('RECOVERY_FORWARD_OK','RECOVERY_TURN_OK')) or 'RECOVERY_PROBE_FAIL' in text:
                    raise RuntimeError('forward/steering check failed: '+(bot.stdout+bot.stderr)[-3000:])
                proc.stdin.write('stop\n');proc.stdin.flush();proc.wait(timeout=90);out.flush();assert_clean(log)
                print('Forward movement and turning checked on Paper; visual appearance not checked.')
            except Exception:
                out.flush();print('--- server log ---\n'+log.read_text(errors='replace')[-12000:],file=sys.stderr);raise
            finally:
                if proc.poll() is None:proc.kill();proc.wait()
if __name__=='__main__':main(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve())
