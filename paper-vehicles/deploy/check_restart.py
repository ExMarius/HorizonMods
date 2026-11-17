#!/usr/bin/env python3
"""Report whether the restart marker remains, without displaying credentials or logs."""
import hmac
import io
import os
import socket
import sys
import paramiko
import upload


def main():
    username = os.environ.get('SFTP_USERNAME', '')
    password = os.environ.get('SFTP_PASSWORD', '')
    key = os.environ.get('SFTP_PRIVATE_KEY', '')
    if not username or not (password or key):
        raise ValueError('credentials missing')
    with socket.create_connection((upload.HOST, upload.PORT), timeout=20) as sock:
        transport = paramiko.Transport(sock)
        try:
            transport.start_client(timeout=20)
            if not hmac.compare_digest(upload.fingerprint(transport.get_remote_server_key()), upload.HOST_KEY_SHA256):
                raise ValueError('host key changed')
            if key:
                transport.auth_publickey(username, paramiko.Ed25519Key.from_private_key(io.StringIO(key)))
            else:
                transport.auth_password(username, password, fallback=False)
            with paramiko.SFTPClient.from_transport(transport) as sftp:
                try:
                    sftp.stat(upload.RESTART_MARKER)
                except FileNotFoundError:
                    print('::notice title=Restart marker::Marker absent; this alone does not prove that the server restarted.')
                else:
                    print('::notice title=Restart marker::Marker pending; the new watcher may not be active yet.')
                try:
                    with sftp.open('logs/latest.log', 'rb') as log:
                        log.seek(0, 2)
                        log.seek(max(0, log.tell() - 1024 * 1024))
                        recent = log.read().decode('utf-8', errors='replace')
                    enabled = recent.rfind('Enabling MrCrayfishVehiclePlugin')
                    disabled = recent.rfind('Disabling MrCrayfishVehiclePlugin')
                    print('::notice title=Legacy plugin::' + ('Enabled in current log.' if enabled >= 0 and enabled > disabled else 'No active legacy-plugin enable found in current log.'))
                except OSError:
                    print('::notice title=Legacy plugin::Current log could not be inspected.')
        finally:
            transport.close()


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'::error title=Restart status unavailable::Type: {type(exc).__name__}', file=sys.stderr)
        sys.exit(1)
