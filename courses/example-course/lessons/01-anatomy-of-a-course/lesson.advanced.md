# Anatomy of a Course

You have built a course before, or you are about to build several. This
lesson is the mechanism: what the engine fetches, in what order, and what it
keeps.

## The folder

```
courses/example-course/
  index.html          copied verbatim from engine/course.html — never edited
  manifest.json       the table of contents
  lessons/
    01-anatomy-of-a-course/
      lesson.md       the standard text (and the intermediate level's)
      lesson.beginner.md
      lesson.advanced.md
      quiz.json
      quiz.advanced.json
```

## What the engine reads

On load the engine fetches `./manifest.json`, then renders the lesson named by
`?lesson=<id>`, or the first lesson when the parameter is missing or unknown.
For that lesson it fetches `lessons/<id>/lesson.md` and then
`lessons/<id>/quiz.json` (for a selected level it tries the level's file
first; see Levels below). Both paths are relative to the course folder, and
nothing in the engine ties the course folder's name to the manifest `slug`.
Only the lesson `id` has to match its folder.

A stub is never fetched. Its `outline` from the manifest is rendered instead,
so a stub needs no folder at all.

## Failure behaviour

- A missing `lesson.md` shows the title and a message naming the path that
  failed to load.
- A missing `quiz.json` means no quiz. That is normal and silent.
- A `quiz.json` that exists but is not valid JSON shows a message naming the
  file and the parse error. The lesson text still renders, but the lesson
  cannot be completed until the file is fixed.

## State

Progress is one `localStorage` key per course: `academy-of-things:<slug>:progress`. It
holds an object keyed by lesson id, each with a `completed` flag and a
timestamp. A lesson with no quiz is marked complete as soon as it opens. A
lesson with a quiz is marked complete only when the reader passes it, and
failed attempts are not recorded. The slug is the only namespace for progress, so renaming
it orphans every reader's saved progress.

## Levels

This course declares `levels` in its manifest. For the selected level the
engine tries `lesson.<level>.md` and `quiz.<level>.json` first and falls back
to `lesson.md` and `quiz.json`, each independently. You can fork the text
without forking the quiz, or the reverse. Progress is per lesson, not per
level. This lesson has a beginner and an advanced version; intermediate falls
back to `lesson.md`.

## What it does not do

No accounts, no server-side state, no completion reporting. If you need
audit-grade proof that someone finished training, this is the wrong tool.
