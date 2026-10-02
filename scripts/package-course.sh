#!/usr/bin/env bash
# Package one course as a standalone zip with the engine vendored in, so it
# runs on its own without this repo.  Usage:
#   ./scripts/package-course.sh <slug>
# Produces dist/<slug>.zip
set -euo pipefail

if [ $# -lt 1 ]; then echo "usage: $0 <slug>" >&2; exit 1; fi

SLUG="$1"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/courses/$SLUG"
[ -d "$SRC" ] || { echo "error: no course at courses/$SLUG" >&2; exit 1; }

STAGE="$(mktemp -d)"; trap 'rm -rf "$STAGE"' EXIT
OUT="$STAGE/$SLUG"
mkdir -p "$OUT"

cp -R "$SRC/manifest.json" "$SRC/lessons" "$OUT/"
cp "$ROOT/engine/app.js" "$ROOT/engine/style.css" "$OUT/"
cp "$ROOT/serve.py" "$OUT/"

# standalone: engine sits beside the course, not two levels up
# (and drop the "All courses" link: there is no course list to go back to)
sed -e 's#\.\./\.\./engine/#./#g' -e '/class="home"/d' "$ROOT/engine/course.html" > "$OUT/index.html"

# serve.py expects courses/<slug>/ and serves a course list at "/"; in a
# standalone bundle the course is the root, so serve index.html there instead
python3 - "$OUT/serve.py" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1])
t = p.read_text()
for old, new in [('ROOT.glob("courses/*/manifest.json")', 'ROOT.glob("manifest.json")'),
                 ('self.path in ("/", "/index.html")', 'False')]:
    assert old in t, old
    t = t.replace(old, new)
p.write_text(t)
PY

cat > "$OUT/README.md" <<MD
# $SLUG

A standalone Academy of Things course. No install, no build step.

\`\`\`bash
python3 serve.py
# open http://localhost:8000
\`\`\`

Progress is saved in your browser only. Nothing is sent anywhere.

Format and authoring docs: https://github.com/eldestar/academy-of-things
MD

mkdir -p "$ROOT/dist"
(cd "$STAGE" && zip -qr "$ROOT/dist/$SLUG.zip" "$SLUG")
echo "Wrote dist/$SLUG.zip"
