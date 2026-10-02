# Academy of Things

Static course engine. `FORMAT.md` is the spec; this file is how to behave in
this repo. Read `FORMAT.md` and `AUTHORING.md` before writing a course.

## Layout rules

- A course is `courses/<slug>/` with `manifest.json`, `index.html` and
  `lessons/<id>/lesson.md` (+ optional `quiz.json`). Scaffold with
  `./scripts/new-course.sh`, never by hand. The old `training-<slug>/` layout
  is dead; do not recreate it.
- `index.html` is copied verbatim from `engine/course.html`. Never hand-edit
  it. If it differs from the engine copy, that is a bug.
- `app.js` and `style.css` live exactly once, in `engine/`. Never copy them
  into a course folder. The only place the engine is duplicated is the zip
  made by `./scripts/package-course.sh`.
- Do not touch `engine/` to make a course work. If the engine seems broken,
  say so and stop; a course should never need an engine change.

## Content rules

- `correct_index` in `quiz.json` is zero-based. Check every value by hand
  against its `options` array. A wrong index marks readers wrong for the right
  answer and nothing warns you.
- A lesson that is not written is `"stub": true` with an `outline`. Never pad
  a thin lesson with filler to avoid the stub label. A short honest course
  beats a padded one.
- Do not invent version numbers, dates, API details or pricing. If it was not
  verified this session, leave it out or flag it.
- Ask who the reader is and what level they are at before writing a course.

## Done means served

Nothing is done until `python3 serve.py` is running and the course has been
opened in a browser, every lesson clicked and every quiz taken. Reading the
files is not verification; a broken `quiz.json` renders no quiz and no error.

## Skills

`.claude/skills/` holds symlinks to `skills/`. Edit the copies in `skills/`;
never add real files under `.claude/skills/`.
