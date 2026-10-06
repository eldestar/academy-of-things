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

   Also decide whether the course needs levels. Add them only when the audience genuinely spans levels and you can write the lessons at more than one depth. A single-level course is simpler and often better. If levels are wanted, scaffold with `--levels` and write `lesson.md` as the standard text (the intermediate one when using the default levels).
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

With levels:

```bash
./scripts/new-course.sh --levels <slug> "<Title>" "<Subtitle>"
```

That adds `"levels": ["beginner", "intermediate", "advanced"]` to the manifest and creates `lesson.beginner.md` and `lesson.advanced.md` placeholders beside `lesson.md`. Write each one or delete it: a leftover placeholder is served to readers as that level's lesson.

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
- `levels` (optional) is an array of level slugs, lowercase letters, digits and hyphens. The first is the default. Leave it out for a single-level course.

### lessons/&lt;id&gt;/lesson.md

Plain Markdown, rendered via marked.js.

- `# Title` as the single H1 at the top.
- `## Section` headers; 4 to 7 sections is the established range.
- Real code blocks wherever the subject involves code or config.
- A `> blockquote` for callouts, warnings and caveats.
- End with a forward pointer to the next lesson, or a concrete "your task" section for hands-on material.
- Roughly 50 to 90 lines of Markdown, not counting diagram blocks (see Diagrams).
- **Teach the facts the quiz asks about.** Every number, name, default, limit, ordering and distinction that a quiz question turns on must be stated in the lesson text. A question the reader can only answer by elimination, or by knowing something the lesson never said, is a defect in the lesson, not the reader. See "Quiz coverage" below.
- **Teach the failure modes**, not just the happy path. The thing that breaks at 2am is the thing worth writing down; the happy path is already in the vendor's docs.
- Never fabricate technical specifics — API syntax, version numbers, release dates, pricing — that were not verified by research this session. Flag uncertainty explicitly rather than guessing.
- This includes UI details: exact menu paths, button and card names, and claims that a feature does *not* exist. A claim of absence ("there is no built-in X") needs a source as much as a claim of presence. If research did not confirm a name or an absence, describe the idea generically ("a chat action such as a send-message card") or say it was not verified. After drafting, grep your own lessons for product names, menu paths and "no ..." claims and check each against what you actually fetched.

### Diagrams

Add a diagram only when a flow, lifecycle or state change is hard to hold in your head from prose: a protocol handshake, a provisioning and deprovisioning sequence, a pipeline with an approval gate, a failure that crosses systems. A diagram earns its place by showing something the paragraph cannot: the order, who talks to whom, which hops go through the browser and which are server to server, where the failure enters. Do not add one to decorate a lesson. Two or three per lesson at most, and most lessons need none.

The engine does not sanitize lesson text, so raw HTML and inline SVG render inside Markdown; scripts do not run. Use `scripts/sequence-diagram.py`, which turns a small JSON spec into an animated sequence diagram and inserts it into one or more lesson files:

```bash
python3 scripts/sequence-diagram.py spec.json --insert courses/<slug>/lessons/<id>/lesson.md --after "## Section heading" --caption "One sentence tying the numbers to the text."
```

Keep each diagram's spec in the course as `courses/<slug>/diagrams/<id>.json` (the engine ignores it and `package-course.sh` does not ship it), so the diagram can be edited and regenerated later. `courses/workos-product-training/diagrams/` holds two complete worked specs: `saml-sp-initiated.json` (browser hops plus a server-to-server exchange) and `scim-lifecycle.json` (a failure mode and a fix). The output uses the engine's CSS variables (light and dark mode), tours the steps with a spotlight and a travelling dot, pauses on hover and through a keyboard-operable "Pause animation" control (moving content must be pausable without a mouse), shows every step statically under `prefers-reduced-motion`, scrolls inside its own box on narrow screens, and carries a title and description for screen readers. Re-running with the same spec replaces the block between its `<!-- diagram:ID -->` markers, so edit the spec, not the generated markup.

- Every label must be a fact the lesson already states and has verified. A diagram is not a place to introduce new claims. Use the lesson's own names (event names, endpoints) and keep the numbers in the diagram matching the numbered text.
- Pass all of a lesson's level files to one `--insert` so every copy is identical. The engine has no include mechanism, and a level file replaces the whole lesson, so the block is duplicated per level by design.
- Diagrams do not replace the text. The paragraph still has to carry the facts a quiz needs, because a reader on a screen reader, with reduced motion, or skimming past it must not lose them.
- Check it rendered: view the lesson in dark and light, at a narrow width, confirm the steps advance in order and hover pauses, and check the browser console is clean. State in your report anything you could not test, for example the real reduced-motion setting.
- Other diagram shapes (state machines, layered architecture) have no generator yet. Hand-write them in the same style (inline SVG, theme variables, a title and desc, no scripts), keep them small, and say in the report that they are hand-built.

### Quiz coverage: the lesson must contain the answers

A quiz tests what the lesson taught. For every question, before you call a lesson done:

1. Write down the deciding fact(s): what makes the right option right, and what rules out each distractor.
2. Find each fact in the lesson body. A fact that appears only in the quiz explanation does not count: the reader meets the explanation after answering. If a fact is missing, add it to the lesson, verified from a source, or rewrite the question.
3. Facts the reader is assumed to know from outside the course (state this in the reader framing, for example "you have run Okta for years") may be left out. Anything product-specific, numeric, default-valued or behavioural may not.
4. Run the blind test in Build order. An answer the test-taker reaches by elimination, with no supporting sentence, is a gap.

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
- **Do not let length give the answer away.** Drafts make the right option the longest, because it carries the qualification and the distractors are quick to write. Across a quiz the correct option should be the single longest in at most about one question in four, and not systematically the shortest either. Write distractors as specific and as long as the right answer, and trim bloated right answers. Check it by counting, not by feel.
- **`correct_index` is zero-based.** This is the single most common authoring bug, and it is invisible until someone is marked wrong for the right answer. Verify every value.
- Favour scenario questions ("a user reports X, what is the likely cause") over definition recall. If a question can be answered by string-matching the lesson text, rewrite it.
- Distractors must be plausible to someone who half-understands the material. No joke options — each implausible distractor is one the reader eliminates for free.
- Every question needs a real `explanation` giving the mechanism. Explanations render for right and wrong answers alike and are the highest-attention moment in the course. Never write "Correct!".
- An invalid `quiz.json` renders no quiz and shows an error naming the file; a valid file with no `questions` renders nothing at all. Validate the JSON and every `correct_index` before calling a lesson done.

### Level variants

- `lesson.<level>.md` and `quiz.<level>.json` replace `lesson.md` and `quiz.json` at that level. A missing variant falls back to the plain file, independently for text and quiz.
- Give every lesson that has a `quiz.<level>.json` a plain `quiz.json` too. Without it the other levels have no quiz, and a lesson with no quiz is marked complete as soon as it opens.
- `?level=<level>` in the URL only seeds the reader's saved choice once and is then removed; levels the manifest does not declare are ignored.
- A level's quiz may ask only what that level's lesson text teaches. Run the blind answerability test per level variant (`scripts/quiz-coverage.py` handles `quiz.<level>.json`), because an advanced question can quietly depend on a fact only the advanced text contains.
- Same facts, different depth. A beginner version defines terms and slows down; an advanced version covers mechanism and failure modes. Never let a level file contradict `lesson.md`.
- Do not copy `lesson.md` into every level file. A lesson with only `lesson.md` is valid; the reader sees a one-line note that no version exists for their level.
- Progress is per lesson. Passing at any level completes the lesson, so keep pass thresholds comparable across a lesson's quizzes.
- Stubs ignore levels.

## Build order

1. Scaffold with `./scripts/new-course.sh`.
2. Write `manifest.json` with the full intended lesson list, marking unwritten lessons `"stub": true` with outlines.
3. Write lessons one at a time, each with `lesson.md` and `quiz.json`, validating JSON as you go. Draft the quiz from the lesson's fact list, not from imagination, so each question has its deciding facts on the page (see Quiz coverage).
4. **Blind answerability test.** For each quiz (every level variant too), make a copy of its questions with `correct_index` and `explanation` removed. Have a reviewer who sees only that copy and the matching lesson text answer every question. For each answer they must quote the supporting sentence from the lesson, or say `NOT IN LESSON` and mark that they relied on outside knowledge or guessed. Then check three things: the answers match your key; every quoted support really appears in the lesson (a paraphrase or a computed number is a weak support); and no answer was flagged as needing outside knowledge or low confidence. Close each gap by adding the fact to the lesson (verified) or rewriting the question, and re-run the test on what changed. The helper does the mechanical half: `python3 scripts/quiz-coverage.py strip <slug> <outdir>` writes the key-free copies (every level variant too) and `python3 scripts/quiz-coverage.py score <slug> <answers.json>` does the comparison and the quote check; its docstring gives the answers format. When using subagents, use a fresh agent for this and forbid it from opening `quiz.json` or other lessons; the author of the lesson cannot judge this. A blind pass that gets everything right is not proof: also have a second reviewer list, per question, the deciding facts and where the lesson states each, because a test-taker can pass by elimination.
5. Update the repo README's course list only if it has one. Most checkouts do not; do not create one.
6. **Actually test it.** Run `python3 serve.py` from the repo root, then confirm 200s for `/courses/<slug>/`, its `manifest.json`, and every `lesson.md` and `quiz.json`. Click through the lessons and take the quizzes before reporting it done.

   - If port 8000 is already taken, use another: `python3 serve.py 8137`. A 404 on `/engine/app.js` means you are talking to some other server, not this repo. Check what owns the port with `lsof -nP -iTCP:8000 -sTCP:LISTEN` and `ps -o command -p <pid>`. Never kill a process you did not start.
   - Check the quizzes against your intent, not against `correct_index`: for each question, find the option whose text you meant to be right, click it, and confirm the engine scores it correct. That catches an answer key and a reshuffled option list drifting apart.
   - Clear the test progress afterwards (`localStorage.removeItem('academy-of-things:<slug>:progress')`) so the first real reader does not see lessons already marked complete.
   - With levels, switch through every level on every lesson and take each quiz variant. Confirm the `No <level> version of this lesson` note appears only where a variant is genuinely absent. Confirm no placeholder text ("Replace this with the ...") remains in any level file.

## What NOT to do

- Don't invent a different file layout "because it's cleaner" — consistency across courses is what keeps this maintainable.
- Don't copy `app.js` or `style.css` into a course folder.
- Don't write filler lessons to hit a lesson-count target. A short, true course beats a padded one.
- Don't add external dependencies beyond marked.js without flagging it first and explaining why.
