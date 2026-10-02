---
name: academy-of-things-course-importer
description: "Convert existing training material (a pasted transcript, an uploaded doc or PDF, notes, an old course export) into a course for the Academy of Things static course engine, preserving the source content rather than replacing it with newly-researched material. Trigger when asked to import, convert, or turn existing material into a course, or when source content is attached/pasted with a request for it to become training content."
---

# Academy of Things Course Importer

Converts material someone already has — a transcript, an old training deck's speaker notes, a doc, a PDF, a set of rough notes — into a course for the Academy of Things static course engine.

The defining difference from the companion `academy-of-things-course-builder` skill: this skill **preserves and restructures existing content** rather than researching and writing new content. A request for a fresh course on a subject with no source material belongs to the builder.

Works in any checkout of the Academy of Things repo (github.com/eldestar/academy-of-things) or a private courses repo built on the same engine. If `FORMAT.md` is present, read it first — it is the authoritative spec and wins over this file if the two disagree.

## When this triggers

Source material is provided or referenced — attached file, pasted text, a link to something already written — with a request for it to become a course, module, or training content. If someone is just naming a subject with nothing to import, redirect to `academy-of-things-course-builder`.

## Core principle: don't silently replace the source with your own knowledge

The whole point of importing is that the source is already trusted — someone's own writing, internal documentation, a specific reference meant to be preserved. Do not:

- Substitute your own explanation where the source said something different or more specific.
- Drop details, examples or caveats because they seem redundant. Condense structure and formatting, not substance.
- Add factual claims not present in the source, even ones you are confident are true, without marking them clearly — e.g. `> Note (not in original source):`.

Reorganising, splitting into lessons, fixing formatting and adding connective sentences is the actual conversion work and is expected. Quietly rewriting the substance is not.

## Process

1. **Read the full source first.** Do not start converting section 1 while section 4 is unread — scope and pacing will be misjudged.
2. **Use the lesson boundaries the source already has** — chapters, headers, topic shifts — rather than inventing a structure. If the source has none, propose a breakdown before writing files rather than guessing silently on a long document.
3. **Check for material that should not leave its original context.** Imported material often carries employer names, internal hostnames, vendor rates, customer names or named individuals. Flag anything like that and confirm before it lands in a course, especially one headed for a public repo.
4. **Flag gaps out loud.** If the source does not support a quiz question at the depth the format expects, say so rather than inventing questions. A shorter, honest quiz beats one padded from assumptions.
5. **Convert to the required layout.**

Scaffold with the script rather than hand-creating folders:

```bash
./scripts/new-course.sh <slug> "<Title>" "<Subtitle>"
```

```
courses/<slug>/
  index.html        copied verbatim from engine/course.html — never hand-edited
  manifest.json
  lessons/
    01-lesson-slug/
      lesson.md
      quiz.json
```

**The engine is shared, not copied.** `index.html` references `../../engine/`, and `app.js` and `style.css` exist once in `engine/`. Do not copy engine files into a course folder. For standalone distribution, `./scripts/package-course.sh <slug>` vendors them into a zip.

**manifest.json**

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

`slug` matches the folder name and namespaces saved progress. A source section too thin or unclear to convert properly gets `"stub": true` plus an `outline`, same as the builder — never pad it with invented content to avoid the stub label.

**lessons/&lt;id&gt;/lesson.md** — Markdown, converted with the source's structure and substance intact: headers, code blocks, callouts. If the source had images or diagrams that cannot be reproduced in text, say what is missing rather than dropping it silently: `> [Original included a diagram here — not reproduced; see source]`.

**lessons/&lt;id&gt;/quiz.json**

```json
{
  "pass_threshold_pct": 80,
  "passing_note": "4 of 5 correct to pass.",
  "questions": [
    {
      "stem": "Question grounded in something the source actually covers.",
      "options": ["A", "B", "C", "D"],
      "correct_index": 1,
      "explanation": "Explanation drawn from the source's own content, not outside knowledge."
    }
  ]
}
```

4 to 6 questions per lesson, each traceable to something the source said. `correct_index` is zero-based — verify every value; getting it wrong marks readers incorrect for the right answer and nothing warns you.

6. **Validate before finishing.** Confirm every `manifest.json` and `quiz.json` is valid JSON with every `correct_index` in range. Then run `python3 serve.py` from the repo root and confirm 200s for `/courses/<slug>/`, its manifest, and each lesson file. Click through and take a quiz.
7. **Report what didn't make it.** Summarise anything cut, simplified, flagged as a gap, or redacted. Do not let a course that looks complete quietly be missing pieces of the original.

## What NOT to do

- Don't research the subject independently and blend it in as if it came from the source. If outside context is genuinely needed for coherence, mark it and mention it in the handoff.
- Don't invent a different file layout — compatibility with `academy-of-things-course-builder` output is what keeps both skills useful.
- Don't copy `app.js` or `style.css` into a course folder.
- Don't silently drop a quiz rather than saying the source didn't support one.
