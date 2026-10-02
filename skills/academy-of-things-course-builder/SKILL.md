---
name: academy-of-things-course-builder
description: "Generate a new self-contained training course (lessons + quizzes) for the Academy of Things static course engine from a typed-in subject. Trigger when asked to build/create/generate a new training course, module, or lesson series, or a request like 'add a course on X' or 'make a training series for Y.'"
---

# Academy of Things Course Builder

Generates a new course for Academy of Things: a static training site with Markdown lessons and JSON-driven quizzes, no backend, no build step, one CDN dependency (marked.js). This skill researches a subject and produces a complete, correctly-formatted course folder that drops into `courses/` and runs immediately.

Works in any checkout of the Academy of Things repo (github.com/eldestar/academy-of-things) or a private courses repo built on the same engine. If `FORMAT.md` is present, read it first — it is the authoritative spec and wins over this file if the two ever disagree.

## When this triggers

Someone says things like "add a course on X," "build a training series for Y," "generate a module on Z for the academy," or otherwise asks for new training content for this tool — not a generic request to "explain X," which should just be answered directly in chat.

If the request comes with source material to convert (a transcript, a doc, notes), that belongs to `academy-of-things-course-importer` instead.

## Before building anything

1. **Ask who the reader is and what level they are at**, unless it is already clear. A course for someone who has run the technology for five years is a different course from an introduction, and guessing wrong wastes the whole thing. Also confirm scope and rough lesson count — 4 to 8 is the useful range; more than that should be two courses.
2. **Research the subject properly** before writing lesson content. Use web search and fetch for anything factual, current, or technical. Never write a lesson from stale knowledge on a fast-moving topic — tool versions, current best practices, provider names, pricing.
3. **Reconcile what you fetched.** When two pages disagree (a limit quoted two ways, a default that differs by page), do not pick one silently. State both in the lesson, or say the figure should be confirmed in the reader's own environment. Record the date the facts were checked in the first lesson, because limits and tier numbers rot.
4. **Plan the lesson sequence before writing files.** Each lesson teaches one coherent chunk, builds on the previous one, and ends with something the learner can point to as evidence of understanding.

## File layout

Scaffold with the script rather than hand-creating folders:

```bash
./scripts/new-course.sh <slug> "<Title>" "<Subtitle>"
```

That produces a placeholder `01-first-lesson` folder and a manifest with one real and one stub entry. Rename or delete the placeholder lesson folder and rewrite the manifest to match your plan, or the course ships with a lesson called "First Lesson". It produces:

```
courses/<slug>/
  index.html        copied verbatim from engine/course.html — never hand-edited
  manifest.json
  lessons/
    01-first-lesson/
      lesson.md
      quiz.json
    02-second-lesson/
      lesson.md
      quiz.json
```

**The engine is shared, not copied.** `index.html` references `../../engine/`, and there is exactly one copy of `app.js` and `style.css` in `engine/`. Do not copy engine files into a course folder — that was the old layout and it caused drift. If a course needs to stand alone for distribution, `./scripts/package-course.sh <slug>` vendors the engine into a zip; that is the only place duplication is correct.

### manifest.json

```json
{
  "slug": "kebab-case-slug",
  "title": "Human-Readable Course Title",
  "subtitle": "One line: what this covers and for whom",
  "lessons": [
    { "id": "01-lesson-slug", "title": "1. Lesson Title" },
    { "id": "02-lesson-slug", "title": "2. Lesson Title" },
    { "id": "03-lesson-slug", "title": "3. Not Written Yet", "stub": true,
      "outline": "## Coming next\n\n- what this will cover\n- another bullet" }
  ]
}
```

- `slug` matches the folder name under `courses/`, and namespaces saved progress in `localStorage`. Pick one you can live with — changing it later resets every reader's progress.
- Lesson `id` values must exactly match their subfolder names under `lessons/`.
- A lesson not yet fully written gets `"stub": true` plus an `outline`. The engine renders it honestly as unwritten, greys it in the sidebar, and excludes it from the progress denominator. Never mark a lesson non-stub unless `lesson.md` exists and is complete, and never write thin filler to avoid the stub label.

### lessons/&lt;id&gt;/lesson.md

Plain Markdown, rendered via marked.js.

- `# Title` as the single H1 at the top.
- `## Section` headers; 4 to 7 sections is the established range.
- Real code blocks wherever the subject involves code or config.
- A `> blockquote` for callouts, warnings and caveats.
- End with a forward pointer to the next lesson, or a concrete "your task" section for hands-on material.
- Roughly 50 to 90 lines of Markdown.
- **Teach the failure modes**, not just the happy path. The thing that breaks at 2am is the thing worth writing down; the happy path is already in the vendor's docs.
- Never fabricate technical specifics — API syntax, version numbers, release dates, pricing — that were not verified by research this session. Flag uncertainty explicitly rather than guessing.
- This includes UI details: exact menu paths, button and card names, and claims that a feature does *not* exist. A claim of absence ("there is no built-in X") needs a source as much as a claim of presence. If research did not confirm a name or an absence, describe the idea generically ("a chat action such as a send-message card") or say it was not verified. After drafting, grep your own lessons for product names, menu paths and "no ..." claims and check each against what you actually fetched.

### lessons/&lt;id&gt;/quiz.json

```json
{
  "pass_threshold_pct": 80,
  "passing_note": "4 of 5 correct to pass.",
  "questions": [
    {
      "stem": "The question text.",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_index": 1,
      "explanation": "Why this answer is correct — shown after the reader checks their answers."
    }
  ]
}
```

- 4 to 6 questions per lesson.
- **Vary where the right answer sits.** Drafts drift towards one position (usually index 1), and readers learn to guess by position. Spread `correct_index` across all positions within a quiz, and re-read each question after reordering, since distractors that referred to each other by position or order stop making sense.
- **`correct_index` is zero-based.** This is the single most common authoring bug, and it is invisible until someone is marked wrong for the right answer. Verify every value.
- Favour scenario questions ("a user reports X, what is the likely cause") over definition recall. If a question can be answered by string-matching the lesson text, rewrite it.
- Distractors must be plausible to someone who half-understands the material. No joke options — each implausible distractor is one the reader eliminates for free.
- Every question needs a real `explanation` giving the mechanism. Explanations render for right and wrong answers alike and are the highest-attention moment in the course. Never write "Correct!".
- Validate the JSON and every `correct_index` before calling a lesson done. A broken `quiz.json` fails silently — no quiz renders and no error shows.

## Build order

1. Scaffold with `./scripts/new-course.sh`.
2. Write `manifest.json` with the full intended lesson list, marking unwritten lessons `"stub": true` with outlines.
3. Write lessons one at a time, each with `lesson.md` and `quiz.json`, validating JSON as you go.
4. Update the repo README's course list only if it has one. Most checkouts do not; do not create one.
5. **Actually test it.** Run `python3 serve.py` from the repo root, then confirm 200s for `/courses/<slug>/`, its `manifest.json`, and every `lesson.md` and `quiz.json`. Click through the lessons and take the quizzes before reporting it done.

   - If port 8000 is already taken, use another: `python3 serve.py 8137`. A 404 on `/engine/app.js` means you are talking to some other server, not this repo. Check what owns the port with `lsof -nP -iTCP:8000 -sTCP:LISTEN` and `ps -o command -p <pid>`. Never kill a process you did not start.
   - Check the quizzes against your intent, not against `correct_index`: for each question, find the option whose text you meant to be right, click it, and confirm the engine scores it correct. That catches an answer key and a reshuffled option list drifting apart.
   - Clear the test progress afterwards (`localStorage.removeItem('academy-of-things:<slug>:progress')`) so the first real reader does not see lessons already marked complete.

## What NOT to do

- Don't invent a different file layout "because it's cleaner" — consistency across courses is what keeps this maintainable.
- Don't copy `app.js` or `style.css` into a course folder.
- Don't write filler lessons to hit a lesson-count target. A short, true course beats a padded one.
- Don't add external dependencies beyond marked.js without flagging it first and explaining why.
