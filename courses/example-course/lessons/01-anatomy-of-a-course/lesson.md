# Anatomy of a Course

You are reading a lesson, served by the engine, from a folder that looks
exactly like the one you will create. Open `courses/example-course/` beside
this page and the whole format should be obvious in about a minute.

## The folder

```
courses/example-course/
  index.html          copied verbatim from engine/course.html — never edited
  manifest.json       the table of contents
  lessons/
    01-anatomy-of-a-course/
      lesson.md       this file
      quiz.json       the questions below
```

There is no build step and no registry. The engine reads `manifest.json`,
then fetches `lessons/<id>/lesson.md` for whichever lesson you clicked. Add a
folder and an entry in the manifest and it appears in the sidebar.

## index.html is boilerplate

Every course has the same `index.html`, copied from `engine/course.html`. It
loads `../../engine/style.css` and `../../engine/app.js` — which is why the
server has to run from the repo root rather than inside a course folder.
Don't edit it per course; if you need a change, change the engine.

## manifest.json drives everything

The `lessons` array sets the order. The `id` must match the folder name. The
`slug` namespaces your saved progress in `localStorage`, so changing it later
resets the saved progress for everyone who has used the course.

## Stubs are first-class

Lesson 3 of this course is a stub. Look at the sidebar: it is greyed out, and
the progress label says "0 of 2 complete" rather than "0 of 3" — unwritten
lessons are excluded from the denominator rather than counted as incomplete
work.

This matters more than it looks. The alternative, when a generator runs out
of real material, is filler: three paragraphs restating the lesson title.
A stub with an honest outline tells the reader what is coming and tells the
author what to write next. Filler just wastes the reader's time and makes
them trust the rest of the course less.

## What the engine does not do

No accounts, no server-side state, no completion reporting, no grading you
can audit. Progress lives in one browser's `localStorage`. If you need to
prove someone completed training, this is the wrong tool — it is built for
self-directed learning, not compliance.
