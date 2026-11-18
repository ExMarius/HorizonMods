#!/usr/bin/env python3
"""Inspect official Minecraft 1.21.4 client bytecode, without redistributing it.

Run with Java 21 and access to Mojang's version manifest. Mojang's published
client mappings provide names; javap shows actual implementation, not just API
signatures. This is a static audit, not proof of in-game visuals.
"""
import hashlib
import json
import re
import subprocess
import tempfile
import urllib.request
from pathlib import Path

MANIFEST = 'https://piston-meta.mojang.com/mc/game/version_manifest_v2.json'
WANTED = {
    'net.minecraft.world.entity.vehicle.AbstractBoat': {'tick', 'controlBoat', 'clampRotation', 'getControllingPassenger', 'positionRider'},
    'net.minecraft.client.player.LocalPlayer': {'rideTick', 'sendPosition', 'sendChanges'},
    'net.minecraft.world.entity.Entity': {'addPassenger', 'isControlledByLocalInstance', 'getRootVehicle', 'getControlledVehicle'},
}


def download(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'HorizonVehicles-audit/1.0'}), timeout=120) as response:
        return response.read()


def checked(item):
    data = download(item['url'])
    if hashlib.sha1(data).hexdigest() != item['sha1']:
        raise ValueError('Mojang download did not match manifest SHA-1')
    return data


def parse_mappings(data):
    current = None
    classes = {}
    methods = {}
    for line in data.splitlines():
        match = re.match(r'^([^ ]+) -> ([^:]+):$', line)
        if match:
            current = match.group(1)
            if current in WANTED:
                classes[current] = match.group(2)
                methods[current] = {}
            continue
        if current not in WANTED:
            continue
        match = re.match(r'^\s+(?:\d+:\d+:)?\S+ ([\w$<>]+)\([^)]*\)(?::\d+:\d+)? -> (\S+)$', line)
        if match and match.group(1) in WANTED[current]:
            methods[current].setdefault(match.group(1), set()).add(match.group(2))
    return classes, methods


def main():
    manifest = json.loads(download(MANIFEST))
    version_url = next(v['url'] for v in manifest['versions'] if v['id'] == '1.21.4')
    version = json.loads(download(version_url))
    mapping = checked(version['downloads']['client_mappings']).decode('utf-8')
    classes, methods = parse_mappings(mapping)
    if set(classes) != set(WANTED):
        raise RuntimeError('Expected mapped classes missing: ' + str(set(WANTED) - set(classes)))
    with tempfile.TemporaryDirectory(prefix='hv-vanilla-audit-') as tmp:
        jar = Path(tmp) / 'client.jar'
        jar.write_bytes(checked(version['downloads']['client']))
        for source, obfuscated in classes.items():
            text = subprocess.check_output(['javap', '-classpath', str(jar), '-p', '-c', obfuscated], text=True)
            print('\n## ' + source + ' (' + obfuscated + ')')
            for name, mapped_names in methods[source].items():
                found = False
                for obf_name in mapped_names:
                    # javap signatures start with two spaces; instruction lines do not.
                    sig = re.compile(r'^  (?:public|protected|private).*\b' + re.escape(obf_name) + r'\([^;]*\);$', re.M)
                    for m in sig.finditer(text):
                        end = re.search(r'^  (?:public|protected|private|static).*\);$', text[m.end():], re.M)
                        block = text[m.start():m.end() + (end.start() if end else len(text))]
                        print('\n### ' + name + ' -> ' + obf_name + '\n' + block[:12000])
                        found = True
                if not found:
                    print('\n### ' + name + ': mapped method not found in javap output')


if __name__ == '__main__':
    main()
