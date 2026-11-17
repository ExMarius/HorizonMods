#!/usr/bin/env python3
"""Upload the development JAR only after authenticating a pinned SSH host key.

Requires environment variables: SFTP_USERNAME, SFTP_PASSWORD and
SFTP_HOST_KEY_SHA256. Never prints credentials. Does not run remote commands,
restart the server, modify worlds, or remove an existing plugin.
"""
import base64
import hashlib
import hmac
import os
import socket
import sys
import uuid
from pathlib import Path

HOST = 'zara.hidencloud.com'
PORT = 2022
TARGET = 'plugins/HorizonVehiclesPaper-dev.jar'
STAGE = 'configuration'


def fingerprint(key):
    digest = hashlib.sha256(key.asbytes()).digest()
    return 'SHA256:' + base64.b64encode(digest).decode('ascii').rstrip('=')


def transfer(sftp, local_path):
    """Upload and verify a temporary file, then replace only our own JAR safely."""
    local_path = Path(local_path)
    sha = hashlib.sha256(local_path.read_bytes()).digest()
    temporary = f'plugins/.horizonvehicles-upload-{uuid.uuid4().hex}.tmp'
    try:
        sftp.put(str(local_path), temporary, confirm=True)
        remote_sha = hashlib.sha256()
        with sftp.open(temporary, 'rb') as remote:
            for chunk in iter(lambda: remote.read(1024 * 1024), b''):
                remote_sha.update(chunk)
        if not hmac.compare_digest(sha, remote_sha.digest()):
            raise ValueError('Uploaded file failed SHA-256 verification')
        try:
            sftp.stat(TARGET)
        except FileNotFoundError:
            sftp.rename(temporary, TARGET)
        else:
            # Never delete the old JAR first: if atomic overwrite is unsupported,
            # fail safely and leave the previous file untouched.
            sftp.posix_rename(temporary, TARGET)
    finally:
        try:
            sftp.remove(temporary)
        except OSError:
            pass


def main():
    import paramiko
    global STAGE
    STAGE = 'jar'
    if len(sys.argv) != 2:
        raise ValueError('Expected one JAR path')
    path = Path(sys.argv[1])
    if not path.is_file() or path.suffix != '.jar':
        raise ValueError('The plugin JAR was not found')
    username = os.environ.get('SFTP_USERNAME', '')
    password = os.environ.get('SFTP_PASSWORD', '')
    expected = os.environ.get('SFTP_HOST_KEY_SHA256', '').strip()
    STAGE = 'username_missing'
    if not username:
        raise ValueError('SFTP username is missing')
    STAGE = 'password_missing'
    if not password:
        raise ValueError('SFTP password is missing')
    STAGE = 'fingerprint_missing_or_invalid'
    if not expected.startswith('SHA256:'):
        raise ValueError('SFTP host fingerprint is missing or invalid')
    STAGE = 'network'
    with socket.create_connection((HOST, PORT), timeout=20) as sock:
        transport = paramiko.Transport(sock)
        try:
            transport.start_client(timeout=20)
            # Verify independently obtained host key BEFORE sending credentials.
            STAGE = 'host_key'
            if not hmac.compare_digest(fingerprint(transport.get_remote_server_key()), expected):
                raise ValueError('SFTP host key fingerprint mismatch; upload stopped before authentication')
            STAGE = 'authentication'
            transport.auth_password(username, password, fallback=False)
            if not transport.is_authenticated():
                raise ValueError('SFTP authentication failed')
            STAGE = 'upload'
            with paramiko.SFTPClient.from_transport(transport) as sftp:
                transfer(sftp, path)
        finally:
            transport.close()
    print('JAR încărcat și verificat. Serverul NU a fost repornit.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        # Exceptions from network libraries may contain sensitive values.
        # GitHub surfaces this annotation through its API without exposing logs.
        # Only fixed stage labels and the exception class are reported.
        print(f'::error title=Livrare SFTP anulată::Etapă: {STAGE}; tip: {type(exc).__name__}', file=sys.stderr)
        sys.exit(1)
