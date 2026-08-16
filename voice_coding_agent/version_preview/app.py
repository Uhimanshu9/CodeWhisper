"""Dependency-free HTTP server for the visual version-control dashboard."""

from __future__ import annotations

import json
import mimetypes
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict
from urllib.parse import unquote, urlparse

from .service import VersionPreviewError, VersionPreviewService


STATIC_DIR = Path(__file__).resolve().parent / "static"


class VersionPreviewHandler(BaseHTTPRequestHandler):
    service = VersionPreviewService()

    def log_message(self, format: str, *args: Any) -> None:
        print("[version-preview] " + (format % args))

    def _send_json(self, payload: Any, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_error_json(self, message: str, status: int = HTTPStatus.BAD_REQUEST) -> None:
        self._send_json({"error": message}, status)

    def _read_body(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 32_768:
            raise VersionPreviewError("Request body is too large.")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as error:
            raise VersionPreviewError("Request body must be JSON.") from error
        if not isinstance(value, dict):
            raise VersionPreviewError("Request body must be a JSON object.")
        return value

    def _serve_static(self, path: str) -> None:
        requested = "index.html" if path in ("/", "/index.html") else path.lstrip("/")
        candidate = (STATIC_DIR / requested).resolve()
        if STATIC_DIR not in candidate.parents and candidate != STATIC_DIR:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if not candidate.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        body = candidate.read_bytes()
        content_type = mimetypes.guess_type(str(candidate))[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = unquote(urlparse(self.path).path)
        try:
            if path == "/api/project":
                self._send_json(self.service.project_info())
            elif path == "/api/versions":
                self._send_json({"versions": self.service.versions()})
            elif path == "/api/traces":
                self._send_json({"events": self.service.recent_events()})
            elif path.startswith("/api/previews/") and path.endswith("/logs"):
                preview_id = path.split("/")[3]
                self._send_json(self.service.preview_logs(preview_id))
            elif path.startswith("/api/previews/"):
                preview_id = path.split("/")[3]
                self._send_json(self.service.preview(preview_id))
            else:
                self._serve_static(path)
        except VersionPreviewError as error:
            self._send_error_json(str(error))
        except Exception as error:  # Keep the UI usable when a host tool fails unexpectedly.
            self._send_error_json(f"Unexpected server error: {error}", HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:  # noqa: N802
        path = unquote(urlparse(self.path).path)
        try:
            body = self._read_body()
            if path == "/api/checkpoints":
                result = self.service.create_checkpoint(
                    str(body.get("message", "")), str(body.get("prompt", ""))
                )
            elif path.startswith("/api/versions/") and path.endswith("/branch"):
                commit_sha = path.split("/")[3]
                result = self.service.branch_from_version(commit_sha, body.get("branch_name"))
            elif path.startswith("/api/versions/") and path.endswith("/preview"):
                commit_sha = path.split("/")[3]
                result = self.service.preview_version(commit_sha)
            elif path.startswith("/api/previews/") and path.endswith("/stop"):
                preview_id = path.split("/")[3]
                result = self.service.stop_preview(preview_id)
            else:
                self._send_error_json("Unknown endpoint.", HTTPStatus.NOT_FOUND)
                return
            self._send_json(result, HTTPStatus.CREATED)
        except VersionPreviewError as error:
            self._send_error_json(str(error))
        except Exception as error:
            self._send_error_json(f"Unexpected server error: {error}", HTTPStatus.INTERNAL_SERVER_ERROR)


def main() -> None:
    host = os.getenv("VERSION_PREVIEW_HOST", "127.0.0.1")
    port = int(os.getenv("VERSION_PREVIEW_PORT", "4090"))
    server = ThreadingHTTPServer((host, port), VersionPreviewHandler)
    print(f"Version Preview UI: http://{host}:{port}")
    print("Press Ctrl-C to stop the dashboard.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nVersion Preview UI stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
