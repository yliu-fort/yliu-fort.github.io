#!/usr/bin/env python3
"""Portrait tool: crop and adjust the home-page portrait in the browser.

    scripts/portrait.py [--port 4010] [--no-browser]

Starts a small server on 127.0.0.1 that serves scripts/portrait-tool.html.
The page does all image processing locally (nothing leaves your machine) and
posts the result back here, which writes

    assets/images/portrait.jpg        2:3 portrait, 900 x 1350
    assets/images/portrait.webp       same, when the browser can encode WebP
    assets/images/portrait-card.jpg   1200 x 630 link-preview image
    _data/portrait.yml                which files the site should use

"Remove portrait" in the page deletes those files and leaves the frame blank.
Re-encoding in the browser drops EXIF metadata such as GPS position.
Commit and push the changed files to publish.
"""
import argparse
import base64
import json
import re
import secrets
import sys
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL_PAGE = Path(__file__).resolve().parent / "portrait-tool.html"
IMAGES = ROOT / "assets" / "images"
DATA = ROOT / "_data" / "portrait.yml"
FILES = {
    "jpg": ("portrait.jpg", "image/jpeg"),
    "webp": ("portrait.webp", "image/webp"),
    "card": ("portrait-card.jpg", "image/jpeg"),
}
MAX_BODY = 40 * 1024 * 1024
TOKEN = secrets.token_urlsafe(24)

DATA_HEADER = (
    "# Home-page portrait. Written by scripts/portrait.py; edit with that tool.\n"
    "# An empty `image` leaves the frame on the home page blank.\n"
)


def read_state():
    state = {"image": "", "webp": "", "card": "", "alt": "", "version": 0}
    if DATA.exists():
        for line in DATA.read_text(encoding="utf-8").splitlines():
            m = re.match(r'^(\w+):\s*(.*)$', line)
            if m and m.group(1) in state:
                value = m.group(2).strip()
                if len(value) >= 2 and value[0] == value[-1] == '"':
                    value = json.loads(value)
                state[m.group(1)] = int(value) if m.group(1) == "version" and value.isdigit() else value
    return state


def write_state(state):
    lines = [DATA_HEADER.rstrip("\n")]
    for key in ("image", "webp", "card", "alt"):
        lines.append(f"{key}: {json.dumps(state.get(key, ''), ensure_ascii=False)}")
    lines.append(f"version: {int(state.get('version', 0))}")
    DATA.write_text("\n".join(lines) + "\n", encoding="utf-8")


def decode_data_url(value, mime):
    prefix = f"data:{mime};base64,"
    if not isinstance(value, str) or not value.startswith(prefix):
        raise ValueError(f"expected a {mime} data URL")
    return base64.b64decode(value[len(prefix):], validate=True)


class Handler(BaseHTTPRequestHandler):
    server_version = "PortraitTool/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("  " + fmt % args + "\n")

    def _send(self, status, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _host_ok(self):
        host = (self.headers.get("Host") or "").split(":")[0]
        return host in ("127.0.0.1", "localhost")

    def do_GET(self):
        if not self._host_ok():
            return self._send(403, {"error": "forbidden host"})
        path = self.path.split("?")[0]
        if path == "/":
            html = TOOL_PAGE.read_text(encoding="utf-8").replace("__TOKEN__", TOKEN)
            return self._send(200, html, "text/html; charset=utf-8")
        if path == "/api/state":
            state = read_state()
            state["exists"] = bool(state["image"]) and (IMAGES / FILES["jpg"][0]).exists()
            return self._send(200, state)
        if path == "/current.jpg":
            f = IMAGES / FILES["jpg"][0]
            if f.exists():
                return self._send(200, f.read_bytes(), "image/jpeg")
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        if not self._host_ok() or self.headers.get("X-Portrait-Token") != TOKEN:
            return self._send(403, {"error": "forbidden"})
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            return self._send(413, {"error": "body too large"})
        try:
            payload = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            return self._send(400, {"error": "invalid JSON"})

        path = self.path.split("?")[0]
        try:
            if path == "/api/save":
                return self._send(200, self.save(payload))
            if path == "/api/clear":
                return self._send(200, self.clear())
        except ValueError as exc:
            return self._send(400, {"error": str(exc)})
        return self._send(404, {"error": "not found"})

    def save(self, payload):
        blobs = {
            "jpg": decode_data_url(payload.get("jpg"), "image/jpeg"),
            "card": decode_data_url(payload.get("card"), "image/jpeg"),
        }
        if payload.get("webp"):
            blobs["webp"] = decode_data_url(payload["webp"], "image/webp")
        IMAGES.mkdir(parents=True, exist_ok=True)
        for key, (name, _) in FILES.items():
            target = IMAGES / name
            if key in blobs:
                target.write_bytes(blobs[key])
            elif target.exists():
                target.unlink()
        alt = str(payload.get("alt") or "").strip()[:300]
        state = {
            "image": "/assets/images/" + FILES["jpg"][0],
            "webp": "/assets/images/" + FILES["webp"][0] if "webp" in blobs else "",
            "card": "/assets/images/" + FILES["card"][0],
            "alt": alt,
            "version": int(time.time()),
        }
        write_state(state)
        written = [str((IMAGES / FILES[k][0]).relative_to(ROOT)) for k in blobs]
        sizes = {k: len(v) for k, v in blobs.items()}
        print(f"  saved {', '.join(written)} and _data/portrait.yml")
        return {"ok": True, "written": written + ["_data/portrait.yml"], "bytes": sizes}

    def clear(self):
        removed = []
        for name, _ in FILES.values():
            target = IMAGES / name
            if target.exists():
                target.unlink()
                removed.append(str(target.relative_to(ROOT)))
        write_state({"image": "", "webp": "", "card": "", "alt": "", "version": int(time.time())})
        print("  portrait removed; the home page frame is blank")
        return {"ok": True, "removed": removed}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--port", type=int, default=4010)
    parser.add_argument("--no-browser", action="store_true", help="do not open a browser window")
    args = parser.parse_args()

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://127.0.0.1:{args.port}/"
    print(f"Portrait tool running at {url}  (Ctrl-C to stop)")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
