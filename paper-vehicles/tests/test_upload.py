import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('upload', ROOT / 'deploy/upload.py')
upload = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upload)


class FakeSftp:
    def __init__(self, existing=False, corrupt=False, atomic=True):
        self.files = {upload.TARGET: b'old jar'} if existing else {}
        self.corrupt = corrupt
        self.atomic = atomic
    def put(self, local, remote, confirm=True):
        self.files[remote] = b'corrupt' if self.corrupt else Path(local).read_bytes()
    def open(self, path, mode):
        return io.BytesIO(self.files[path])
    def stat(self, path):
        if path not in self.files:
            raise FileNotFoundError(path)
    def rename(self, old, new):
        if new in self.files:
            raise OSError('target exists')
        self.files[new] = self.files.pop(old)
    def posix_rename(self, old, new):
        if not self.atomic:
            raise OSError('atomic rename unsupported')
        self.files[new] = self.files.pop(old)
    def remove(self, path):
        if path not in self.files:
            raise FileNotFoundError(path)
        del self.files[path]


class UploadTests(unittest.TestCase):
    def test_verified_upload_first_install_and_atomic_upgrade(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'plugin.jar'
            path.write_bytes(b'new jar')
            for existing in (False, True):
                sftp = FakeSftp(existing=existing)
                upload.transfer(sftp, path)
                self.assertEqual(sftp.files, {upload.TARGET: b'new jar'})

    def test_checksum_failure_and_no_atomic_support_leave_existing_file_intact(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'plugin.jar'
            path.write_bytes(b'new jar')
            for sftp in (FakeSftp(existing=True, corrupt=True), FakeSftp(existing=True, atomic=False)):
                with self.assertRaises((ValueError, OSError)):
                    upload.transfer(sftp, path)
                self.assertEqual(sftp.files, {upload.TARGET: b'old jar'})

    def test_fingerprint_uses_sha256_wire_encoding(self):
        class Key:
            def asbytes(self): return b'example'
        self.assertEqual(upload.fingerprint(Key()), 'SHA256:UNhY4JhezH9gQYqvDMWrWH9CwlcKiECVqejMrND2VFw')

if __name__ == '__main__':
    unittest.main()
