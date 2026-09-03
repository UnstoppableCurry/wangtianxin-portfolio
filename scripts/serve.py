#!/usr/bin/env python3
"""Local preview server that serves dist/ under SITE_BASE, like GitHub Pages."""

from __future__ import annotations

import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1] / "dist"
SITE_BASE = os.environ.get("SITE_BASE", "/wangtianxin-portfolio").rstrip("/")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _rewrite_path(self) -> bool:
        parsed = urlparse(self.path)
        path = parsed.path or "/"
        extra = ""
        if parsed.query:
            extra = "?" + parsed.query
        if SITE_BASE:
            if path in ("/", ""):
                self.send_response(302)
                self.send_header("Location", SITE_BASE + "/" + extra)
                self.end_headers()
                return False
            prefix = SITE_BASE + "/"
            if path == SITE_BASE:
                self.send_response(302)
                self.send_header("Location", prefix + extra)
                self.end_headers()
                return False
            if path.startswith(prefix):
                stripped = path[len(SITE_BASE):] or "/"
                self.path = stripped + extra
                return True
        return True

    def do_GET(self):
        if self._rewrite_path():
            super().do_GET()

    def do_HEAD(self):
        if self._rewrite_path():
            super().do_HEAD()

    def send_error(self, code, message=None, explain=None):
        if code == 404 and (ROOT / "404.html").is_file():
            body = (ROOT / "404.html").read_bytes()
            self.send_response(404, "Not Found")
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().send_error(code, message, explain)


def main() -> None:
    port = int(os.environ.get("PORT", "4173"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    home = f"http://127.0.0.1:{port}{SITE_BASE or ''}/"
    print(f"serving {ROOT} on {home}")
    server.serve_forever()


if __name__ == "__main__":
    main()
