import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('falix_auto_update', Path(__file__).resolve().parents[1] / 'deploy/falix_auto_update.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class FakeFalix:
    def __init__(self, state='running', corrupt_backup=False, corrupt_jar=False):
        self.state = state
        self.files = {'/plugins/' + m.NAME: b'original'}
        self.events = []
        self.corrupt_backup = corrupt_backup
        self.corrupt_jar = corrupt_jar
    def status(self):
        self.events.append('status')
        return self.state
    def api(self, path, data=None, method=None):
        self.events.append(path)
        if path.startswith('/files?'): return [{'name': '1.21.4'}]
        if path == '/power': self.state = 'starting'; return {}
        raise AssertionError(path)
    def download(self, path):
        self.events.append('download:' + path)
        data = self.files[path]
        if (path.endswith('.bak') and self.corrupt_backup) or (path == '/plugins/' + m.NAME and data != b'original' and self.corrupt_jar): return b'corrupt'
        return data
    def upload(self, directory, name, content):
        self.events.append('upload:' + name)
        self.files[directory.rstrip('/') + '/' + name] = content

class UpdateTests(unittest.TestCase):
    def test_backup_failure_does_not_overwrite_or_restart(self):
        api = FakeFalix(corrupt_backup=True)
        with self.assertRaises(SystemExit): m.deploy(api, b'new', '123')
        self.assertEqual(api.files['/plugins/' + m.NAME], b'original')
        self.assertNotIn('/power', api.events)
    def test_upload_mismatch_does_not_restart(self):
        api = FakeFalix(corrupt_jar=True)
        with self.assertRaises(SystemExit): m.deploy(api, b'new', '123')
        self.assertEqual(api.files['/mcv-backup-123.jar.bak'], b'original')
        self.assertNotIn('/power', api.events)
    def test_offline_update_never_starts_server(self):
        api = FakeFalix(state='offline')
        m.deploy(api, b'new', '123')
        self.assertEqual(api.files['/plugins/' + m.NAME], b'new')
        self.assertNotIn('/power', api.events)
    def test_restart_only_after_verified_upload(self):
        api = FakeFalix()
        states = iter(['running', 'running', 'starting', 'running'])
        api.status = lambda: next(states)
        with patch.object(m.time, 'sleep'):
            m.deploy(api, b'new', '123')
        self.assertGreater(api.events.index('/power'), api.events.index('download:/plugins/' + m.NAME, api.events.index('upload:' + m.NAME)))

if __name__ == '__main__': unittest.main()
