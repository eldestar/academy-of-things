---
name: academy-of-things-course-builder
description: "Generate a new self-contained training course (lessons + quizzes) for this repo's static course engine from a typed-in subject. Trigger when asked to build/create/generate a new training course, module, or lesson series for the academy, or a request like 'add a course on X' or 'make a training series for Y.'"
---

# Academy of Things Course Builder

Generates a new course for this repo: a self-contained static training site with Markdown lessons and JSON-driven quizzes, no backend, no build step, one CDN dependency (marked.js). This skill's job is to research a subject and produce a complete, correctly-formatted course folder that drops straight into this repo and runs immediately.

## When this triggers

Someone says things like "add a course on X," "build a training series for Y," "generate a module on Z for the academy," or otherwise asks for new training content for this specific tool (not a generic request to "explain X," which should just be answered directly in chat).

## Before building anything

1. Confirm two things if not already clear: the subject/scope, and roughly how many lessons are wanted (3-6 is typical; more than that should be split into two courses).
2. Research the subject properly before writing lesson content -- use web search/fetch for anything factual, current, or technical. Never write a lesson from assumed/stale knowledge on a fast-moving topic (tool versions, current best practices, pricing, etc.) without checking.
3. Plan the lesson sequence before writing any files: each lesson should teach one coherent chunk, build on the previous one, and end with something the learner can point to as evidence of understanding (not just "read this").

## Exact file format (load-bearing -- the engine will not render course content that doesn't match this exactly)

A course lives in its own top-level folder, named `training-<kebab-case-slug>/`, with this structure:

```
training-<slug>/
  index.html          <- copy verbatim from an existing course folder, do not hand-edit
  style.css             <- copy verbatim from shared/course-engine/style.css (or an existing training-* folder)
  app.js                 <- copy verbatim from shared/course-engine/app.js (or an existing training-* folder)
  manifest.json
  lessons/
    01-first-lesson-slug/
      lesson.md
      quiz.json
    02-second-lesson-slug/
      lesson.md
      quiz.json
```

**Why index.html/style.css/app.js are copied, not written fresh:** the engine intentionally has no build step, and each course folder is self-contained so a plain `python3 -m http.server` run from inside that folder works without path-traversal issues (a bug already hit and fixed once in this repo -- don't reintroduce it). Always copy these three files byte-for-byte; never hand-author them for a new course.

### manifest.json

```json
{
  "slug": "kebab-case-slug",
  "title": "Human-Readable Course Title",
  "subtitle": "One-line description of what this course covers and for whom",
  "lessons": [
    { "id": "01-lesson-slug", "title": "1. Lesson Title" },
    { "id": "02-lesson-slug", "title": "2. Lesson Title" },
    { "id": "03-lesson-slug", "title": "3. Not Written Yet", "stub": true,
      "outline": "## Coming next\n\n- bullet point of what this will cover\n- another bullet point" }
  ]
}
```

- `slug` must match the folder name minus `training-`.
- Lesson `id` values must exactly match their subfolder names under `lessons/`.
- A lesson not yet fully written gets `"stub": true` plus a short `outline` field (markdown) describing what it will cover -- the engine renders this honestly as "not written yet." Never mark a lesson non-stub unless lesson.md and quiz.json both actually exist and are complete. Do not work around this by writing thin/filler content just to avoid the stub label.

### lessons/<id>/lesson.md

Plain Markdown, rendered via marked.js. Match the style of existing lessons in this repo:
- `# Title` as the single H1 at the top.
- `## Section` headers (aim for 4-7 sections).
- Real code blocks wherever the subject involves code/config.
- A `> blockquote` for callouts/warnings/caveats.
- End with a forward pointer to the next lesson, or a concrete "your task" section for hands-on material.
- Length: roughly 50-90 lines of Markdown is the established range.
- Never fabricate technical specifics (exact API syntax, current tool versions, pricing) not verified via research this session -- flag uncertainty explicitly rather than guessing.

### lessons/<id>/quiz.json

```json
{
  "pass_threshold_pct": 80,
  "passing_note": "4 of 5 correct to pass.",
  "questions": [
    {
      "stem": "The question text.",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_index": 1,
      "explanation": "Why this answer is correct -- shown to the learner after they check their answers."
    }
  ]
}
```

- 4-6 questions per lesson.
- `correct_index` is 0-based into `options`.
- Every question needs a real `explanation`, not a one-liner restating the answer.
- Favor scenario-style questions ("a user reports X, what's the likely cause") over pure definition recall.
- Validate the JSON is syntactically correct and every `correct_index` is in range before considering a lesson done -- a broken quiz.json silently fails in the engine (no quiz section renders, no error shown).

## Build order

1. Create the course folder, copy the three engine files in first.
2. Write `manifest.json` with the full intended lesson list, marking not-yet-written lessons `stub: true` with outlines.
3. Write lessons one at a time, each with lesson.md + quiz.json, validating JSON as you go.
4. Update the top-level repo README's course table if one exists.
5. Actually test it: start a local server in the new course folder and curl every referenced file path (index.html, style.css, app.js, manifest.json, each lesson.md/quiz.json) to confirm 200s before calling it done.

## What NOT to do

- Don't invent a different file layout "because it's cleaner" -- consistency across courses is what keeps this tool maintainable.
- Don't write filler lessons to hit a lesson-count target.
- Don't add external dependencies beyond marked.js without flagging it first and explaining why.
