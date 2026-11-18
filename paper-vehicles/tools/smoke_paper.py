#!/usr/bin/env python3
"""Start a disposable offline Paper server, verify plugin load and stale-marker handling.

This is a server startup test, not a Minecraft-client, multiplayer or driving test.
Requires Java 21, network access to Paper and Mojang, and a built plugin JAR.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

API = 'https://fill.papermc.io/v3/projects/paper/versions/1.21.4'
HEADERS = {'User-Agent': 'HorizonVehiclesPaper-smoke/1.0 (https://github.com/ExMarius/HorizonMods)'}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=60) as response:
        return response.read()


def main(jar):
    jar = Path(jar).resolve()
    builds = json.loads(get(API + '/builds'))
    stable = [build for build in builds if build.get('channel') == 'STABLE']
    build = max(stable or builds, key=lambda item: item['id'])
    download = build['downloads']['server:default']
    content = get(download['url'])
    expected = download['checksums']['sha256']
    if hashlib.sha256(content).hexdigest() != expected:
        raise RuntimeError('Paper server download checksum mismatch')
    with tempfile.TemporaryDirectory(prefix='horizon-paper-smoke-') as tmp:
        root = Path(tmp)
        (root / 'paper.jar').write_bytes(content)
        (root / 'eula.txt').write_text('eula=true\n')
        (root / 'start.sh').write_text('#!/bin/sh\necho restarted > restart.success\n')
        (root / 'start.sh').chmod(0o755)
        (root / 'server.properties').write_text('online-mode=false\nserver-port=25565\nspawn-protection=0\nview-distance=3\nsimulation-distance=3\n')
        plugins = root / 'plugins'
        plugins.mkdir()
        shutil.copyfile(jar, plugins / 'HorizonVehiclesPaper-dev.jar')
        if os.environ.get('FAKEPILOT_DEPS'):
            for dep in Path(os.environ['FAKEPILOT_DEPS']).glob('*.jar'):
                shutil.copyfile(dep, plugins / dep.name)
        data = plugins / 'HorizonVehiclesPaper'
        data.mkdir()
        (data / 'config.yml').write_text('experiments:\n  nested-boat-seat: true\n')
        marker = data / '.restart-request'
        marker.write_text(hashlib.sha256(jar.read_bytes()).hexdigest() + '\n')
        logpath = root / 'smoke.log'
        with logpath.open('w+') as log:
            proc = subprocess.Popen(['java', '-Xms512M', '-Xmx1G', '-jar', 'paper.jar', '--nogui'],
                                    cwd=root, stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT, text=True)
            try:
                deadline = time.monotonic() + 240
                while time.monotonic() < deadline:
                    time.sleep(2)
                    log.flush()
                    text = logpath.read_text(errors='replace')
                    if proc.poll() is not None:
                        raise RuntimeError('Paper exited before startup')
                    if 'Done (' in text and 'HorizonVehiclesPaper' in text:
                        break
                else:
                    raise RuntimeError('Paper startup timed out')
                proc.stdin.write('hvehicle list\n'); proc.stdin.flush()
                time.sleep(6)
                text = logpath.read_text(errors='replace')
                if 'Go-Kart: prototip experimental' not in text:
                    raise RuntimeError('Plugin command did not respond')
                if marker.exists():
                    raise RuntimeError('Restart watcher did not consume matching digest')
                if '[HorizonVehiclesPaper] Disabling' in text:
                    raise RuntimeError('Plugin disabled during startup')
                # Give the offline test player OP before login. The bot checks
                # boat mounting, steering and pack delivery, not visual fidelity.
                proc.stdin.write('op SmokeBot\n'); proc.stdin.flush()
                bot = Path(__file__).with_name('smoke_player.cjs').resolve()
                for variant in (('boat', 'raft', 'fake') if os.environ.get('FAKEPILOT_DEPS') else ('boat', 'raft')):
                    player_test = subprocess.run(['node', str(bot), variant], capture_output=True, text=True, timeout=60)
                    if player_test.returncode:
                        raise RuntimeError('Offline ' + variant + ' player failed: ' + (player_test.stdout + player_test.stderr)[-2000:])
                    print(player_test.stdout)
                    # Clean up the prior variant before reconnecting the same bot.
                    proc.stdin.write('kill @e[type=minecraft:interaction]\n'); proc.stdin.flush()
                    time.sleep(2)
                nested = Path(__file__).with_name('smoke_nested_boat.cjs').resolve()
                for vehicle in (() if os.environ.get('FAKEPILOT_DEPS') else ('oak_boat', 'bamboo_raft')):
                    nested_test = subprocess.run(['node', str(nested), vehicle], capture_output=True, text=True, timeout=40)
                    if nested_test.returncode:
                        raise RuntimeError('Nested ' + vehicle + ' experiment failed: ' + (nested_test.stdout + nested_test.stderr)[-2000:])
                    print(nested_test.stdout)
                two = Path(__file__).with_name('smoke_second_seat.cjs').resolve()
                two_test = subprocess.run(['node', str(two)], capture_output=True, text=True, timeout=45)
                if two_test.returncode:
                    raise RuntimeError('Second-seat experiment failed: ' + (two_test.stdout + two_test.stderr)[-2000:])
                print(two_test.stdout)
                # A different digest must issue the same restart command as the
                # upstream plugin. Our dummy start.sh records the invocation.
                marker.write_text('f' * 64 + '\n')
                deadline = time.monotonic() + 90
                while time.monotonic() < deadline and not (root / 'restart.success').exists():
                    time.sleep(1)
                if not (root / 'restart.success').exists():
                    raise RuntimeError('Restart command did not invoke the configured start script')
                text = logpath.read_text(errors='replace')
                if 'Update detected; requesting server restart' not in text:
                    raise RuntimeError('Restart watcher did not announce the update')
                print(f'Paper 1.21.4 build {build["id"]}: plugin loaded, offline client checked boat seat, steering and pack delivery, stale marker consumed and update triggered restart script.')
            except Exception:
                print(logpath.read_text(errors='replace')[-30000:], file=sys.stderr)
                raise
            finally:
                if proc.poll() is None:
                    proc.stdin.write('stop\n'); proc.stdin.flush()
                    try:
                        proc.wait(timeout=60)
                    except subprocess.TimeoutExpired:
                        proc.kill(); proc.wait()


if __name__ == '__main__':
    main(sys.argv[1])
