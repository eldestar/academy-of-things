# Universal prompt

Works in any assistant — no skills, plugins or config. Paste the contents of
`FORMAT.md`, then this, then your subject.

---

You are generating a course for the Academy of Things static course engine.
The format spec is above. Follow it exactly.

Produce a complete course folder. For each file, give me the full path and
its full contents in a fenced code block, so I can save them directly:

```
courses/<slug>/manifest.json
courses/<slug>/lessons/01-<id>/lesson.md
courses/<slug>/lessons/01-<id>/quiz.json
...
```

Do not generate `index.html` — it is copied verbatim from `engine/course.html`.

Rules:

1. **Ask me who the reader is and what level they are at** before writing
   anything, unless I have already said. A course for someone who has run
   the technology for five years is a different course from an introduction,
   and guessing wrong wastes the whole thing.
2. **Four to eight lessons.** More than that, split it into two courses.
3. **Write what you actually know.** Mark anything you are unsure of as a
   stub with an outline instead of writing it. Never invent version numbers,
   release dates, pricing, or API details — if a fact matters and you cannot
   verify it, leave it out or flag it inline for me to check.
4. **Teach failure modes**, not just the happy path. The thing that breaks at
   2am is the thing worth writing down.
5. **Quizzes test judgment, not recall.** Four to six questions per lesson.
   `correct_index` is zero-based — double-check every one. Distractors must be
   plausible to someone who half-understands the material; no joke options.
   Explanations explain the mechanism, never just "Correct!".
6. **Stubs over filler.** If you run out of real material, mark the remaining
   lessons `"stub": true` with honest outlines. A short, true course beats a
   padded one.

My subject:
