#!/usr/bin/env python3
"""Check Paper console output for recovery/plugin failures, including stack traces.

Use the captured process output after exit, not logs/latest.log after a restart:
Paper overwrites latest.log on the next boot. This is a targeted check, not a
claim that unrelated server errors or all possible failures are detected.
"""
import re

PLUGIN = re.compile(r'com\.mrcrayfish\.vehicle\.|\[(?:MrCrayfishVehiclePlugin|RecoveryProbe)\]', re.I)
EXCEPTION = re.compile(r'\b(?:[\w.$]*(?:Exception|Error|Throwable))\b|Could not pass event|Exception in server tick loop|RECOVERY_PROBE_FAIL', re.I)
SEVERE = re.compile(r'\b(?:ERROR|SEVERE|FATAL)\b', re.I)
HEADER = re.compile(r'^\[\d\d:\d\d:\d\d\s')


def find_failures(text):
    lines = text.splitlines()
    matches = []
    for i, line in enumerate(lines):
        if 'RECOVERY_PROBE_FAIL' in line or 'Could not pass event' in line or 'Exception in server tick loop' in line:
            matches.append((i + 1, line))
        elif SEVERE.search(line) and PLUGIN.search(line):
            matches.append((i + 1, line))
        elif EXCEPTION.search(line):
            # An exception header often precedes its plugin stack frame. Stop at
            # the next regular log record to avoid correlating unrelated events.
            block = [line]
            for follow in lines[i + 1:i + 81]:
                if HEADER.match(follow):
                    break
                block.append(follow)
            if PLUGIN.search('\n'.join(block)):
                matches.append((i + 1, line))
    return matches


def assert_clean(path):
    failures = find_failures(path.read_text(errors='replace'))
    if failures:
        details = '\n'.join(f'{path.name}:{number}: {line}' for number, line in failures[:20])
        raise RuntimeError('Paper recovery/plugin log errors detected:\n' + details)
