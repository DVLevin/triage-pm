from __future__ import annotations

import hmac
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .app import TriageApplication
from .store import DuplicateDecision

STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/manifest.webmanifest": ("manifest.webmanifest", "application/manifest+json"),
    "/sw.js": ("sw.js", "text/javascript; charset=utf-8"),
    "/icon.svg": ("icon.svg", "image/svg+xml"),
    "/icon-192.png": ("icon-192.png", "image/png"),
    "/icon-512.png": ("icon-512.png", "image/png"),
}
CSP = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"


def create_server(host: str, port: int, app: TriageApplication, token: str, static_root: Path) -> ThreadingHTTPServer:
    class Handler(BaseHTTPRequestHandler):
        server_version = "TriageLocal/1.0"

        def log_message(self, format: str, *args: Any) -> None:
            # Suppress request-line logging: the initial pairing URL carries a token.
            return

        def _headers(self, status: int, content_type: str, length: int, api: bool = False) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(length))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", CSP)
            self.send_header("Cache-Control", "no-store" if api else "no-cache")
            self.end_headers()

        def _json(self, status: int, payload: Any) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self._headers(status, "application/json; charset=utf-8", len(body), api=True)
            self.wfile.write(body)

        def _authorized(self) -> bool:
            supplied = self.headers.get("Authorization", "").removeprefix("Bearer ")
            return bool(supplied) and hmac.compare_digest(supplied, token)

        def _read_json(self) -> dict[str, Any]:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                raise ValueError("Invalid content length")
            if length <= 0 or length > 65536:
                raise ValueError("JSON body must be between 1 and 65536 bytes")
            value = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(value, dict):
                raise ValueError("JSON object required")
            return value

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            if path == "/api/health":
                self._json(200, {"ok": True})
                return
            if path.startswith("/api/"):
                if not self._authorized():
                    self._json(401, {"error": "Pair this device with the local access token"})
                    return
                try:
                    if path == "/api/bootstrap":
                        self._json(200, {"projects": app.list_projects()})
                        return
                    parts = path.strip("/").split("/")
                    if len(parts) == 3 and parts[:2] == ["api", "project"]:
                        self._json(200, app.get_snapshot(parts[2]))
                        return
                    self._json(404, {"error": "Unknown API route"})
                except KeyError as exc:
                    self._json(404, {"error": str(exc)})
                except Exception as exc:
                    self._json(500, {"error": f"Snapshot failed: {type(exc).__name__}"})
                return
            if path not in STATIC_FILES:
                self._json(404, {"error": "Not found"})
                return
            filename, content_type = STATIC_FILES[path]
            try:
                body = (static_root / filename).read_bytes()
            except FileNotFoundError:
                self._json(404, {"error": "Application asset missing"})
                return
            self._headers(200, content_type, len(body))
            self.wfile.write(body)

        def do_POST(self) -> None:
            path = urlparse(self.path).path
            if not path.startswith("/api/"):
                self._json(404, {"error": "Not found"})
                return
            if not self._authorized():
                self._json(401, {"error": "Pair this device with the local access token"})
                return
            try:
                payload = self._read_json()
                if path == "/api/decisions":
                    self._json(201, {"decision": app.decide(payload)})
                    return
                if path == "/api/decisions/undo":
                    result = app.undo(str(payload.get("project_id") or ""))
                    self._json(200, {"decision": result, "undone": bool(result)})
                    return
                if path == "/api/comments":
                    result = app.comment(str(payload.get("project_id") or ""), str(payload.get("ticket_key") or ""), str(payload.get("body") or ""))
                    self._json(201, {"comment": result})
                    return
                parts = path.strip("/").split("/")
                if len(parts) == 4 and parts[:2] == ["api", "project"] and parts[3] == "refresh":
                    self._json(200, app.get_snapshot(parts[2], refresh=True))
                    return
                if len(parts) == 4 and parts[:2] == ["api", "project"] and parts[3] == "context":
                    self._json(200, app.apply_context(parts[2], payload.get("settings", {})))
                    return
                self._json(404, {"error": "Unknown API route"})
            except DuplicateDecision as exc:
                self._json(409, {"error": str(exc)})
            except KeyError as exc:
                self._json(404, {"error": str(exc)})
            except (ValueError, json.JSONDecodeError) as exc:
                self._json(422, {"error": str(exc)})
            except Exception as exc:
                self._json(500, {"error": f"Action failed: {type(exc).__name__}"})

    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    return server
