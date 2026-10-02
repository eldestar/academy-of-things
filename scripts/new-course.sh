#!/usr/bin/env bash
# Scaffold a new course.  Usage:
#   ./scripts/new-course.sh [--levels] <slug> "<Title>" "<Subtitle>"
# --levels adds beginner/intermediate/advanced levels. lesson.md is the
# fallback and the intermediate text; edit the lesson.beginner.md and
# lesson.advanced.md it creates, or delete them to show lesson.md there.
# A leftover placeholder is shown to readers as that level's lesson.
set -euo pipefail

LEVELS=0; ARGS=()
for a in "$@"; do
  if [ "$a" = "--levels" ]; then LEVELS=1; else ARGS+=("$a"); fi
done
set -- ${ARGS[@]+"${ARGS[@]}"}

if [ $# -lt 2 ]; then
  echo "usage: $0 [--levels] <slug> \"<Title>\" [\"<Subtitle>\"]" >&2
  exit 1
fi

SLUG="$1"; TITLE="$2"; SUBTITLE="${3:-}"
LEVELS_JSON=""
if [ "$LEVELS" = 1 ]; then
  LEVELS_JSON=$'\n  "levels": ["beginner", "intermediate", "advanced"],'
fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/courses/$SLUG"

if [ -e "$DEST" ]; then echo "error: $DEST already exists" >&2; exit 1; fi

mkdir -p "$DEST/lessons/01-first-lesson"
cp "$ROOT/engine/course.html" "$DEST/index.html"

cat > "$DEST/manifest.json" <<JSON
{
  "slug": "$SLUG",
  "title": "$TITLE",
  "subtitle": "$SUBTITLE",$LEVELS_JSON
  "lessons": [
    { "id": "01-first-lesson", "title": "1. First Lesson" },
    { "id": "02-second-lesson", "title": "2. Second Lesson", "stub": true,
      "outline": "## Coming next\n\n- Replace this outline with what the lesson will actually cover\n- Delete the stub flag once lesson.md exists" }
  ]
}
JSON

cat > "$DEST/lessons/01-first-lesson/lesson.md" <<'MD'
# First Lesson

Replace this with the lesson body. Plain Markdown; see ../../../FORMAT.md
for what the engine supports and ../../../AUTHORING.md for what makes a
lesson worth reading.
MD

if [ "$LEVELS" = 1 ]; then
  for lv in beginner advanced; do
    cat > "$DEST/lessons/01-first-lesson/lesson.$lv.md" <<MD
# First Lesson

Replace this with the $lv version. Keep the same facts as lesson.md and change
the depth. Delete this file to show lesson.md at the $lv level instead.
MD
  done
fi

cat > "$DEST/lessons/01-first-lesson/quiz.json" <<'JSON'
{
  "pass_threshold_pct": 80,
  "passing_note": "4 of 5 correct to pass.",
  "questions": [
    {
      "stem": "Replace this question.",
      "options": ["Wrong", "Right", "Also wrong"],
      "correct_index": 1,
      "explanation": "correct_index is zero-based. Say why the answer is right, not that it is right."
    }
  ]
}
JSON

echo "Created courses/$SLUG"
echo "Run:  python3 serve.py   then open http://localhost:8000/courses/$SLUG/"
if [ "$LEVELS" = 1 ]; then
  echo "Levels: lesson.md is the fallback and the intermediate text."
  echo "Write or delete lesson.beginner.md and lesson.advanced.md: a leftover placeholder is shown to readers as that level's lesson."
fi
