#!/usr/bin/env python3
"""Serve this repo so courses can share one copy of the engine.

    python3 serve.py          # http://localhost:8000
    python3 serve.py 8080     # pick a port

Why this exists: courses reference ../../engine/, so the server has to be
rooted at the repo, not inside a course folder. Opening a course over
file:// will not work either -- the engine fetches manifest.json and lesson
files, which browsers block on file://.
"""
import http.server
import json
import pathlib
import socketserver
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
ROOT = pathlib.Path(__file__).parent.resolve()


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".md": "text/markdown; charset=utf-8",
        ".json": "application/json; charset=utf-8",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = landing_page().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, fmt, *args):
        pass  # keep the console readable


def landing_page():
    rows = []
    for slug, title, subtitle, written, total in course_rows():
        rows.append(
            f'<li><a href="/courses/{slug}/">{title}</a>'
            f'<div class="sub">{subtitle}</div>'
            f'<div class="meta">{written} of {total} lessons written</div></li>'
        )
    items = "\n".join(rows) or "<li>No courses found under <code>courses/*/manifest.json</code></li>"
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Academy of Things</title>
<link rel="stylesheet" href="/engine/style.css">
<style>
body{{max-width:46rem;margin:0 auto;padding:3rem 1.25rem}}
ul{{list-style:none;padding:0}}
li{{padding:1rem 0;border-bottom:1px solid var(--border,#2a2a2a)}}
li a{{font-size:1.1rem;font-weight:600;text-decoration:none}}
.sub{{color:var(--muted,#888);margin-top:.25rem}}
.meta{{color:var(--muted,#888);font-size:.8rem;margin-top:.35rem}}
</style></head>
<body><h1>Academy of Things</h1>
<p class="sub">Static courses — Markdown lessons and JSON quizzes, no backend.</p>
<ul>{items}</ul></body></html>"""


def course_rows():
    rows = []
    for manifest in sorted(ROOT.glob("courses/*/manifest.json")):
        try:
            data = json.loads(manifest.read_text())
        except json.JSONDecodeError:
            rows.append((manifest.parent.name, manifest.parent.name,
                         "manifest.json is not valid JSON", 0, 0))
            continue
        lessons = data.get("lessons", [])
        rows.append((
            manifest.parent.name,
            data.get("title", "untitled"),
            data.get("subtitle", ""),
            sum(1 for l in lessons if not l.get("stub")),
            len(lessons),
        ))
    return rows


if __name__ == "__main__":
    rows = course_rows()
    print(f"\n  Academy of Things — serving {ROOT}")
    print(f"\n    http://localhost:{PORT}/\n")
    for slug, title, _sub, written, total in rows:
        print(f"    http://localhost:{PORT}/courses/{slug}/")
        print(f"      {title}  ({written}/{total} lessons written)\n")
    if not rows:
        print("    No courses found under courses/*/manifest.json\n")
    print(f"  Ctrl-C to stop.\n")
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Stopped.\n")
