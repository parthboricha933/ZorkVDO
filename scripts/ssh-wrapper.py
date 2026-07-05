#!/usr/bin/env python3
"""SSH wrapper for git using paramiko.

Git invokes this via GIT_SSH_COMMAND. It receives args like:
  git@github.com "git-receive-pack 'user/repo.git'"

This script uses paramiko to establish the SSH connection and pipes
stdin/stdout/stderr bidirectionally.
"""
import sys
import os
import paramiko
import threading
import select

def main():
    args = sys.argv[1:]

    # Strip -o options that git might pass
    filtered = []
    i = 0
    while i < len(args):
        if args[i] == "-o" and i + 1 < len(args):
            i += 2
            continue
        if args[i] == "-p" and i + 1 < len(args):
            i += 2
            continue
        filtered.append(args[i])
        i += 1

    if len(filtered) < 1:
        sys.stderr.write("Usage: ssh-wrapper host [command]\n")
        sys.exit(1)

    host = filtered[0]
    command = " ".join(filtered[1:]) if len(filtered) > 1 else None

    key_path = os.path.expanduser("~/.ssh/id_ed25519")
    private_key = paramiko.Ed25519Key.from_private_key_file(key_path)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname="github.com",
            username="git",
            pkey=private_key,
            port=22,
            timeout=30,
            allow_agent=False,
            look_for_keys=False,
        )
    except Exception as e:
        sys.stderr.write(f"SSH connection failed: {e}\n")
        sys.exit(1)

    if command:
        transport = client.get_transport()
        chan = transport.open_session()
        chan.exec_command(command)

        def pipe_stdin():
            try:
                while True:
                    data = sys.stdin.buffer.read1(4096)
                    if not data:
                        chan.shutdown_write()
                        break
                    chan.sendall(data)
            except Exception:
                pass

        stdin_thread = threading.Thread(target=pipe_stdin, daemon=True)
        stdin_thread.start()

        while True:
            r, _, _ = select.select([chan], [], [], 0.1)
            if chan.recv_ready():
                data = chan.recv(4096)
                if data:
                    sys.stdout.buffer.write(data)
                    sys.stdout.buffer.flush()
            if chan.recv_stderr_ready():
                data = chan.recv_stderr(4096)
                if data:
                    sys.stderr.buffer.write(data)
                    sys.stderr.buffer.flush()
            if chan.exit_status_ready() and not chan.recv_ready() and not chan.recv_stderr_ready():
                break

        exit_code = chan.recv_exit_status()
        stdin_thread.join(timeout=1)
        client.close()
        sys.exit(exit_code)
    else:
        client.close()
        sys.exit(0)

if __name__ == "__main__":
    main()
