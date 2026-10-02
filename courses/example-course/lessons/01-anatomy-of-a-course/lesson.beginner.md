# Anatomy of a Course

A course is a folder of plain files. If you can make folders and edit text,
you can make a course. This lesson walks through the pieces, using the course
you are reading right now.

## The folder

```
courses/example-course/
  index.html          the page shell, identical in every course
  manifest.json       the table of contents
  lessons/
    01-anatomy-of-a-course/
      lesson.md       this text
      quiz.json       the questions below
```

Each lesson gets its own folder. The folder name is the lesson's `id`.

## Three kinds of file

- `index.html` is the page that loads everything. Every course has the same
  one, copied from `engine/course.html`. You never edit it.
- `manifest.json` is the table of contents: the course title and the list of
  lessons, in order.
- `lesson.md` is the lesson text, written in Markdown. `quiz.json` is an
  optional set of questions about it.

## Adding a lesson

Make a folder under `lessons/`, add one line for it in `manifest.json`, and
reload the page. It appears in the sidebar. There is nothing to build or
register.

## Stubs

A lesson you have planned but not written is a stub: it gets `"stub": true`
and an `outline` in the manifest. Lesson 3 of this course is one. It shows up
greyed out in the sidebar and does not count toward the progress label, which
reads "0 of 2 complete" rather than "0 of 3" before you finish anything.

Do not fill a lesson with filler text to make a course look finished. An
honest stub is more useful.

## Where your progress is saved

In this browser only. There are no accounts and nothing is sent anywhere.
The course's `slug` decides where progress is stored, so changing the slug
later resets everyone's progress. Choose it once.

## Levels

The Beginner, Intermediate and Advanced switch in the sidebar changes which
version of a lesson you read. This lesson has a beginner and an advanced
version; intermediate reads the standard text.
