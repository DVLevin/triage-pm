#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import secrets
import socket
from pathlib import Path

from triage.app import TriageApplication
from triage.server import create_server

ROOT = Path(__file__).resolve().parent


def access_token(data_dir: Path) -> str:
    data_dir.mkdir(parents=True, exist_ok=True)
    path = data_dir / "access-token"
    if path.exists():
        token = path.read_text().strip()
        if len(token) >= 32:
            return token
    token = secrets.token_urlsafe(32)
    path.write_text(token + "\n")
    os.chmod(path, 0o600)
    return token


def lan_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No packet is sent; this only asks the OS which interface it would route.
        sock.connect(("192.0.2.1", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local Triage KBOS review app")
    parser.add_argument("--config", default=str(ROOT / "config.local.json"))
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    parser.add_argument("--lan", action="store_true", help="Allow phone access on the local network with pairing-token auth")
    args = parser.parse_args()
    config_path = Path(args.config)
    if not config_path.exists():
        raise SystemExit("Copy config.example.json to config.local.json and set your project roots first.")
    config = json.loads(config_path.read_text())
    host = "0.0.0.0" if args.lan else (args.host or config.get("host", "127.0.0.1"))
    port = args.port or int(config.get("port", 8765))
    token = access_token(ROOT / "data")
    app = TriageApplication(config, ROOT / "data" / "triage.db")
    server = create_server(host, port, app, token, ROOT / "static")
    address = lan_ip() if args.lan else "127.0.0.1"
    print(f"Triage listening on {host}:{port}")
    print(f"Open: http://{address}:{port}/?pair={token}")
    print("Source KBOS is read-only. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        app.close()


if __name__ == "__main__":
    main()
