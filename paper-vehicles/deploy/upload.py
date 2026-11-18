#!/usr/bin/env python3
"""Upload the development JAR only after authenticating a pinned SSH host key.

Requires environment variables: SFTP_USERNAME, SFTP_PASSWORD and
either SFTP_PRIVATE_KEY or SFTP_PASSWORD. Never prints credentials, runs remote
commands, or modifies worlds. After verification it requests a restart
through the plugin watcher, matching the original Paper plugin.
"""
import base64
import hashlib
import hmac
import io
import os
import socket
import sys
import uuid
from pathlib import Path

HOST = 'zara.hidencloud.com'
PORT = 2022
# Trust-on-first-use: observed via GitHub's SFTP host check, not verified by provider.
HOST_KEY_SHA256 = 'SHA256:phWPoAg3Zy1vnk1M1VJBUFGfvS/r0R+7pN8Al82o1IQ'
TARGET = 'plugins/HorizonVehiclesPaper-dev.jar'
DATA_DIR = 'plugins/HorizonVehiclesPaper'
RESTART_MARKER = DATA_DIR + '/.restart-request'
STAGE = 'configuration'


def fingerprint(key):
    digest = hashlib.sha256(key.asbytes()).digest()
    return 'SHA256:' + base64.b64encode(digest).decode('ascii').rstrip('=')


def transfer(sftp, local_path, target=TARGET):
    """Upload and verify a temporary file, then replace only our own JAR safely."""
    global STAGE
    local_path = Path(local_path)
    sha = hashlib.sha256(local_path.read_bytes()).digest()
    temporary = f'plugins/.horizonvehicles-upload-{uuid.uuid4().hex}.tmp'
    try:
        STAGE = 'upload_put'
        sftp.put(str(local_path), temporary, confirm=True)
        STAGE = 'upload_verify'
        remote_sha = hashlib.sha256()
        with sftp.open(temporary, 'rb') as remote:
            for chunk in iter(lambda: remote.read(1024 * 1024), b''):
                remote_sha.update(chunk)
        if not hmac.compare_digest(sha, remote_sha.digest()):
            raise ValueError('Uploaded file failed SHA-256 verification')
        STAGE = 'upload_target_stat'
        try:
            sftp.stat(target)
        except FileNotFoundError:
            STAGE = 'upload_install'
            sftp.rename(temporary, target)
        else:
            try:
                STAGE = 'upload_atomic_replace'
                sftp.posix_rename(temporary, target)
            except OSError:
                # Some SFTP hosts do not implement OpenSSH's posix-rename extension.
                # Keep the old plugin as a non-JAR backup and restore it on failure.
                # There is a brief gap between renames; no restart is performed here.
                backup = f'plugins/.horizonvehicles-backup-{uuid.uuid4().hex}.bak'
                STAGE = 'upload_backup'
                sftp.rename(target, backup)
                try:
                    STAGE = 'upload_install'
                    sftp.rename(temporary, target)
                except Exception:
                    try:
                        STAGE = 'upload_rollback'
                        sftp.rename(backup, target)
                    except Exception as rollback_error:
                        raise RuntimeError('Upload failed and rollback failed; backup is retained') from rollback_error
                    raise
    finally:
        try:
            sftp.remove(temporary)
        except OSError:
            pass


def request_restart(sftp, local_path):
    """Publish the new JAR digest only after transfer has succeeded."""
    global STAGE
    STAGE = 'restart_directory'
    try:
        sftp.stat(DATA_DIR)
    except FileNotFoundError:
        sftp.mkdir(DATA_DIR)
    digest = hashlib.sha256(Path(local_path).read_bytes()).hexdigest().encode('ascii') + b'\n'
    temporary = f'{DATA_DIR}/.restart-upload-{uuid.uuid4().hex}.tmp'
    try:
        STAGE = 'restart_marker_upload'
        sftp.putfo(io.BytesIO(digest), temporary, file_size=len(digest), confirm=True)
        with sftp.open(temporary, 'rb') as remote:
            if remote.read() != digest:
                raise ValueError('Restart marker verification failed')
        STAGE = 'restart_marker_install'
        try:
            sftp.stat(RESTART_MARKER)
        except FileNotFoundError:
            sftp.rename(temporary, RESTART_MARKER)
        else:
            try:
                sftp.posix_rename(temporary, RESTART_MARKER)
            except OSError:
                sftp.remove(RESTART_MARKER)
                sftp.rename(temporary, RESTART_MARKER)
    finally:
        try:
            sftp.remove(temporary)
        except OSError:
            pass

def main():
    import paramiko
    global STAGE
    STAGE = 'jar'
    if len(sys.argv) not in (2, 4):
        raise ValueError('Expected plugin JAR and optional two test dependency JARs')
    path = Path(sys.argv[1])
    if not path.is_file() or path.suffix != '.jar':
        raise ValueError('The plugin JAR was not found')
    dependencies = [Path(p) for p in sys.argv[2:]]
    if dependencies and ([p.name for p in dependencies] != ['CommandAPI-9.7.0.jar', 'fakeplayer-0.3.13.jar'] or any(not p.is_file() for p in dependencies)):
        raise ValueError('Unexpected or missing experimental dependency')
    username = os.environ.get('SFTP_USERNAME', '')
    password = os.environ.get('SFTP_PASSWORD', '')
    private_key = os.environ.get('SFTP_PRIVATE_KEY', '')
    expected = HOST_KEY_SHA256
    STAGE = 'username_missing'
    if not username:
        raise ValueError('SFTP username is missing')
    STAGE = 'credential_missing'
    if not private_key and not password:
        raise ValueError('SFTP credential is missing')
    STAGE = 'network'
    with socket.create_connection((HOST, PORT), timeout=20) as sock:
        transport = paramiko.Transport(sock)
        try:
            transport.start_client(timeout=20)
            # Compare the pinned, observed host key BEFORE sending credentials.
            STAGE = 'host_key'
            if not hmac.compare_digest(fingerprint(transport.get_remote_server_key()), expected):
                raise ValueError('SFTP host key fingerprint mismatch; upload stopped before authentication')
            STAGE = 'authentication'
            if private_key:
                key = paramiko.Ed25519Key.from_private_key(io.StringIO(private_key))
                transport.auth_publickey(username, key)
            else:
                transport.auth_password(username, password, fallback=False)
            if not transport.is_authenticated():
                raise ValueError('SFTP authentication failed')
            STAGE = 'upload'
            with paramiko.SFTPClient.from_transport(transport) as sftp:
                if dependencies:
                    STAGE = 'dependency_conflict_check'
                    existing = [n.lower() for n in sftp.listdir('plugins') if n.lower().endswith('.jar')]
                    for keyword, dep in zip(('commandapi', 'fakeplayer'), dependencies):
                        if any(keyword in n and n != dep.name.lower() for n in existing):
                            raise ValueError('A conflicting dependency already exists; refusing duplicate plugins')
                    for dep in dependencies:
                        transfer(sftp, dep, 'plugins/' + dep.name)
                transfer(sftp, path)
                request_restart(sftp, path)
        finally:
            transport.close()
    print('JAR verificat și cerere de restart publicată. Restartul necesită watcherul deja activ pe server.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        # Exceptions from network libraries may contain sensitive values.
        # GitHub surfaces this annotation through its API without exposing logs.
        # Only fixed stage labels and the exception class are reported.
        print(f'::error title=Livrare SFTP anulată::Etapă: {STAGE}; tip: {type(exc).__name__}', file=sys.stderr)
        sys.exit(1)
