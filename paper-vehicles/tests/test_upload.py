import importlib.util
import io
import hashlib
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
        self.directories = set()
    def put(self, local, remote, confirm=True):
        self.files[remote] = b'corrupt' if self.corrupt else Path(local).read_bytes()
    def putfo(self, source, remote, file_size=0, confirm=True):
        self.files[remote] = source.read()
    def mkdir(self, path):
        self.directories.add(path)
    def open(self, path, mode):
        return io.BytesIO(self.files[path])
    def stat(self, path):
        if path not in self.files and path not in self.directories:
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
            sftp = FakeSftp(existing=True, corrupt=True)
            with self.assertRaises(ValueError):
                upload.transfer(sftp, path)
            self.assertEqual(sftp.files, {upload.TARGET: b'old jar'})

            sftp = FakeSftp(existing=True, atomic=False)
            upload.transfer(sftp, path)
            self.assertEqual(sftp.files[upload.TARGET], b'new jar')
            backups = [data for name, data in sftp.files.items() if name.endswith('.bak')]
            self.assertEqual(backups, [b'old jar'])

            class FailInstall(FakeSftp):
                def rename(self, old, new):
                    if old.endswith('.tmp'):
                        raise OSError('install failed')
                    super().rename(old, new)
            sftp = FailInstall(existing=True, atomic=False)
            with self.assertRaises(OSError):
                upload.transfer(sftp, path)
            self.assertEqual(sftp.files, {upload.TARGET: b'old jar'})

    def test_restart_marker_is_digest_of_verified_jar(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'plugin.jar'
            path.write_bytes(b'new jar')
            for atomic in (True, False):
                sftp = FakeSftp(atomic=atomic)
                upload.transfer(sftp, path)
                upload.request_restart(sftp, path)
                self.assertEqual(sftp.files[upload.RESTART_MARKER],
                                 hashlib.sha256(b'new jar').hexdigest().encode() + b'\n')
                upload.request_restart(sftp, path)
                self.assertEqual(sftp.files[upload.RESTART_MARKER],
                                 hashlib.sha256(b'new jar').hexdigest().encode() + b'\n')
                self.assertFalse(any(name.endswith('.tmp') for name in sftp.files))

    def test_fingerprint_uses_sha256_wire_encoding(self):
        class Key:
            def asbytes(self): return b'example'
        self.assertEqual(upload.fingerprint(Key()), 'SHA256:UNhY4JhezH9gQYqvDMWrWH9CwlcKiECVqejMrND2VFw')

if __name__ == '__main__':
    unittest.main()
