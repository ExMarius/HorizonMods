#!/usr/bin/env python3
"""Start a disposable offline Paper server, verify plugin load and stale-marker handling.

This is a server startup test, not a Minecraft-client, multiplayer or driving test.
Requires Java 21, network access to Paper and Mojang, and a built plugin JAR.
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

API = 'https://api.papermc.io/v2/projects/paper/versions/1.21.4'
HEADERS = {'User-Agent': 'HorizonVehiclesPaper-smoke/1.0 (https://github.com/ExMarius/HorizonMods)'}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=60) as response:
        return response.read()


def main(jar):
    jar = Path(jar).resolve()
    builds = json.loads(get(API + '/builds'))['builds']
    stable = [build for build in builds if build.get('channel') == 'default']
    build = max(stable or builds, key=lambda item: item['build'])
    name = build['downloads']['application']['name']
    url = API + f"/builds/{build['build']}/downloads/{name}"
    content = get(url)
    expected = build['downloads']['application']['sha256']
    if hashlib.sha256(content).hexdigest() != expected:
        raise RuntimeError('Paper server download checksum mismatch')
    with tempfile.TemporaryDirectory(prefix='horizon-paper-smoke-') as tmp:
        root = Path(tmp)
        (root / 'paper.jar').write_bytes(content)
        (root / 'eula.txt').write_text('eula=true\n')
        (root / 'server.properties').write_text('online-mode=false\nserver-port=0\nspawn-protection=0\nview-distance=3\nsimulation-distance=3\n')
        plugins = root / 'plugins'
        plugins.mkdir()
        shutil.copyfile(jar, plugins / 'HorizonVehiclesPaper-dev.jar')
        data = plugins / 'HorizonVehiclesPaper'
        data.mkdir()
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
                print(f'Paper 1.21.4 build {build["build"]}: plugin loaded, command responded, stale marker consumed.')
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
