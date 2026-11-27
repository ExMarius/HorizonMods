#!/usr/bin/env python3
"""Disposable Paper paired-garage quit and restart probe."""
import hashlib,json,os,shutil,subprocess,sys,tempfile,time,urllib.request
from pathlib import Path
from recovery_log_check import assert_clean
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
        (root/'server.properties').write_text('online-mode=false\ndifficulty=peaceful\nspawn-monsters=false\nserver-port=25578\nspawn-protection=0\ngenerate-structures=false\nview-distance=3\nsimulation-distance=3\nlevel-type=minecraft:flat\n')
        (root/'plugins').mkdir();shutil.copyfile(jar,root/'plugins/MrCrayfishVehiclePlugin.jar');shutil.copyfile(probe,root/'plugins/RecoveryProbe.jar')
        log=root/'server.log'
        with log.open('w+') as out:
            proc=subprocess.Popen(['java','-Dhorizon.recovery.commandcrash=true','-Dhorizon.recovery.fallbacktest='+str(os.getenv('RECOVERY_FALLBACK_TEST')=='1').lower(),'-Dhorizon.recovery.retrytest='+str(os.getenv('RECOVERY_RETRY_TEST')=='1').lower(),'-Dhorizon.recovery.pairtest=true','-Dhorizon.recovery.drivetest='+str(os.getenv('RECOVERY_PAIR_DRIVE')=='1' or os.getenv('RECOVERY_MID_RESTART')=='1').lower(),'-Dhorizon.recovery.restarttest='+str(os.getenv('RECOVERY_MID_RESTART')=='1').lower(),'-Xms512M','-Xmx1G','-jar','paper.jar','--nogui'],cwd=root,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
            try:
                deadline=time.monotonic()+240
                while time.monotonic()<deadline:
                    time.sleep(2);out.flush();text=log.read_text(errors='replace')
                    if proc.poll() is not None:raise RuntimeError('server exited')
                    if 'Done (' in text and '[RecoveryProbe] Enabling' in text:break
                else:raise RuntimeError('startup timeout')
                bot=subprocess.Popen(['node',str(Path(__file__).with_name('smoke_recovery_pair.cjs'))],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                deadline=time.monotonic()+75
                while time.monotonic()<deadline:
                    time.sleep(1);out.flush();text=log.read_text(errors='replace')
                    if 'RECOVERY_PROBE_FAIL' in text:raise RuntimeError('live command failed before crash')
                    if proc.poll() is not None or bot.poll() is not None:raise RuntimeError('server or client exited before crash')
                    if 'RECOVERY_LIVE_COMMAND_CRASH_READY' in text:break
                else:raise RuntimeError('live command crash point not reached')
                # Kill Paper while both players are connected and loading is in progress.
                proc.kill();proc.wait(timeout=90)
                bot.terminate();bot.wait(timeout=15)
                if proc.returncode != -9:raise RuntimeError('server was not killed by SIGKILL')
                out.flush(); assert_clean(log)  # Include shutdown or SIGKILL output.
                restartlog=root/'server-restart.log'
                with restartlog.open('w+') as restarted:
                    proc=subprocess.Popen(['java','-Dhorizon.recovery.fallbacktest='+str(os.getenv('RECOVERY_FALLBACK_TEST')=='1').lower(),'-Dhorizon.recovery.retrytest='+str(os.getenv('RECOVERY_RETRY_TEST')=='1').lower(),'-Dhorizon.recovery.pairtest=true','-Dhorizon.recovery.drivetest='+str(os.getenv('RECOVERY_PAIR_DRIVE')=='1' or os.getenv('RECOVERY_MID_RESTART')=='1').lower(),'-Dhorizon.recovery.restarttest='+str(os.getenv('RECOVERY_MID_RESTART')=='1').lower(),'-Xms512M','-Xmx1G','-jar','paper.jar','--nogui'],cwd=root,stdin=subprocess.PIPE,stdout=restarted,stderr=subprocess.STDOUT,text=True)
                    deadline=time.monotonic()+240
                    while time.monotonic()<deadline:
                        time.sleep(2);restarted.flush(); restarttext=restartlog.read_text(errors='replace')
                        if proc.poll() is not None:raise RuntimeError('restart exited: '+restarttext[-4000:])
                        if 'Done (' in restarttext and '[RecoveryProbe] Enabling' in restarttext:break
                    else:raise RuntimeError('restart startup timeout')
                    env={**os.environ,'RECOVERY_PAIR_RESTART':'1'}
                    bot=subprocess.run(['node',str(Path(__file__).with_name('smoke_recovery_pair.cjs'))],capture_output=True,text=True,timeout=30,env=env)
                    restarted.flush();restarttext=restartlog.read_text(errors='replace')
                    if 'recovered' not in restarttext.lower() and 'RECOVERY_PAIR_RESTART_OK' not in restarttext:raise RuntimeError('no recovery evidence after live crash')
                    if bot.returncode or any('RECOVERY_PAIR_RESTART_OK '+n not in restarttext for n in ('RecoveryOwnerBot','RecoveryProbeBot')) or 'RECOVERY_PROBE_FAIL' in restarttext:
                        raise RuntimeError('restart garage verification failed: '+(restarttext+bot.stdout+bot.stderr)[-5000:])
                    proc.stdin.write('stop\n');proc.stdin.flush();proc.wait(timeout=90)
                    restarted.flush(); assert_clean(restartlog)
                print('Disposable Paper: SIGKILL during live command loading; both owners recovered their vehicle IDs after restart.')
            except Exception:
                out.flush();print('--- server log ---\n'+log.read_text(errors='replace')[-12000:],file=sys.stderr);raise
            finally:
                if proc.poll() is None:proc.kill();proc.wait()
if __name__=='__main__':main(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve())
