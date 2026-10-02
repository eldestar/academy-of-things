---
name: academy-of-things-course-importer
description: "Convert existing training material (a pasted transcript, an uploaded doc or PDF, notes, an old course export) into a course for this repo's static course engine, preserving the source content rather than replacing it with newly-researched material. Trigger when asked to import, convert, or turn existing material into a course for the academy, or when source content is attached/pasted with a request for it to become training content."
---

# Academy of Things Course Importer

Converts material someone already has -- a transcript, an old training deck's speaker notes, a doc, a PDF, a set of rough notes -- into a course for this repo's static course engine. The defining difference from the companion `academy-of-things-course-builder` skill: this skill's job is to **preserve and restructure existing content**, not to research and write new content from scratch. A request for a fresh course on a subject with no source material belongs to the builder skill, not this one.

## When this triggers

Source material is provided or referenced (attached file, pasted text, a link to something already written) with a request for it to become a course, module, or training content in this tool. If someone's just naming a subject with nothing to import, redirect to `academy-of-things-course-builder` instead.

## Core principle: don't silently replace the source with your own knowledge

The whole point of importing is that the source material is already trusted -- it might be someone's own writing, internal documentation, or a specific reference meant to be preserved. Do not:
- Substitute your own explanation of the subject where the source said something different or more specific.
- Drop details, examples, or caveats from the source because they seem redundant -- condense structure and formatting, not substance.
- Add new factual claims not present in the source, even ones you're confident are true, without clearly marking them as an addition (e.g., a `> Note (not in original source):` callout).

It's fine and expected to reorganize, split into lessons, fix formatting, and add connective sentences -- that's the actual conversion work. It is not fine to quietly rewrite the substance.

## Process

1. **Get the full source material first.** Read the whole thing before planning the lesson split -- don't start converting section 1 while section 4 is still unread, scope and pacing will be misjudged.
2. **Identify the natural lesson boundaries** the source already has (chapters, headers, topic shifts) rather than inventing an arbitrary structure. If the source has no clear structure, propose a lesson breakdown before writing files rather than guessing silently on a long or ambiguous document.
3. **Flag gaps out loud.** If the source material doesn't cleanly support a quiz question at the depth this engine's quizzes expect, say so rather than inventing quiz content not grounded in the source -- a shorter, honest quiz beats a padded one built from assumptions.
4. **Convert to the exact file format required by the engine** (identical to the builder skill's format, reproduced here so this skill is self-contained):

```
training-<kebab-case-slug>/
  index.html          <- copy verbatim from shared/course-engine/ or an existing training-* folder
  style.css             <- copy verbatim, same source
  app.js                 <- copy verbatim, same source
  manifest.json
  lessons/
    01-lesson-slug/
      lesson.md
      quiz.json
```

**manifest.json:**
```json
{
  "slug": "kebab-case-slug",
  "title": "Course Title (from or closely derived from the source)",
  "subtitle": "One-line description",
  "lessons": [
    { "id": "01-lesson-slug", "title": "1. Lesson Title" }
  ]
}
```
A source section too thin or unclear to convert properly yet gets `"stub": true` plus an `outline` field, same as the builder skill -- never pad it out with invented content just to avoid marking it a stub.

**lessons/<id>/lesson.md:** Markdown, converted from the source with its structure and substance intact -- headers, code blocks, callouts as appropriate. If the source had images/diagrams that can't be reproduced in text, note what's missing rather than silently dropping it (e.g., `> [Original included a diagram here -- not reproduced; see source]`).

**lessons/<id>/quiz.json:**
```json
{
  "pass_threshold_pct": 80,
  "passing_note": "4 of 5 correct to pass.",
  "questions": [
    {
      "stem": "Question grounded in something the source material actually covers.",
      "options": ["A", "B", "C", "D"],
      "correct_index": 1,
      "explanation": "Explanation referencing the source's own content, not outside knowledge."
    }
  ]
}
```
4-6 questions per lesson, each traceable back to something the source material actually said.

5. **Validate before finishing:** confirm every manifest.json and quiz.json is syntactically valid JSON with every `correct_index` in range, then start a local server in the new course folder and curl each referenced file path to confirm everything resolves -- this exact class of broken-relative-path bug has happened before in this repo.
6. **Report what didn't make it.** If anything from the source was cut, simplified, or flagged as a gap, summarize that plainly when handing back the result -- don't let a "looks complete" course quietly be missing pieces of the original.

## What NOT to do

- Don't research the subject independently and blend that in as if it came from the source -- if outside context is genuinely needed for coherence, add it as a clearly marked note and mention it in the handoff summary.
- Don't invent a different file layout -- consistency with `academy-of-things-course-builder`'s format is what keeps both skills producing compatible output.
- Don't silently drop a quiz for a lesson rather than saying the source didn't support one.
