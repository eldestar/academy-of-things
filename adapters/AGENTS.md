# Academy of Things — agent instructions

Append this to your project's `AGENTS.md` (Codex and most agent CLIs read it),
or point your agent at this file.

## What this repo is

A static course engine. A course is a folder of Markdown lessons and JSON
quizzes under `courses/<slug>/`. No build step, no backend, no framework.

## Before writing a course

Read `FORMAT.md` for the file layout and schema, and `AUTHORING.md` for what
separates a course people finish from one they close.

## Rules

- Scaffold with `./scripts/new-course.sh <slug> "<Title>" "<Subtitle>"` rather
  than hand-creating folders.
- Never edit a course's `index.html`. It is copied verbatim from
  `engine/course.html`. Engine changes go in `engine/`.
- `correct_index` in `quiz.json` is zero-based. Verify every value.
- Mark unwritten lessons `"stub": true` with an `outline`. Do not pad a course
  with filler to make it look complete.
- Do not invent version numbers, dates, pricing or API details. Flag anything
  unverified inline.
- Verify your work: run `python3 serve.py`, open the course, click through
  every lesson, and take every quiz before reporting it done.
