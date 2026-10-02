# Course levels, restyle and theming: design

Status: approved by Ben 2026-10-01. Branch `claude/academy-levels-feature-48682d`.

## Goal

Let one course serve Beginner, Intermediate and Advanced readers, and bring the
engine UI up to a minimal, Linear-like standard with light, dark and system
themes. Reader is a working professional. Desktop first, responsive on mobile.
No framework, no build step; marked.js stays the only external dependency.

Visual research: Mobbin was unavailable (account has no paid plan) and 21st.dev
is not configured, so the UI direction comes from sketches Ben chose from, not
from third-party references. No product's branding or assets are used.

## Format changes (author-facing)

`manifest.json` gains an optional field:

```json
"levels": ["beginner", "intermediate", "advanced"]
```

- Absent: the course behaves exactly as today and no switcher renders.
- Present: each entry is a lowercase slug (`[a-z0-9-]+`). Order is display
  order and the first entry is the default level.

Per lesson folder, optional level variants:

```
lessons/01-x/
  lesson.md                 fallback for every level
  lesson.beginner.md        used at that level when present
  quiz.json                 fallback
  quiz.advanced.json        used at that level when present
```

- Lesson body and quiz fall back to `lesson.md` and `quiz.json` independently.
  Falling back is decided by a non-OK response, the same way a missing
  `quiz.json` is treated today.
- A lesson whose body fell back to `lesson.md` shows one line under the title:
  "No <level> version of this lesson; showing the standard text." The engine
  cannot know whether other levels differ without probing them, so the note
  states only what is true for the level being read. For a lesson that has
  only `lesson.md` it reads the same at every level. Stub lessons and courses
  without `levels` never show it. A quiz-only fallback shows nothing.
- Progress stays per lesson, not per level. Completing a lesson at any level
  marks it complete.

## Level state

Resolution order, first valid wins:

1. `?level=` in the URL
2. `localStorage` key `academy-of-things:<slug>:level`
3. `levels[0]`

Any value not in `manifest.levels` is ignored, which also keeps user input out
of fetched paths. A valid `?level=` is saved to storage. Changing level
re-renders the current lesson in place with no history entry. Lesson links stay
`?lesson=<id>`; the level lives in storage, so navigation never drops it.
Storage access is wrapped in try/catch like progress; on failure the level
lives in memory for the page.

## Theme state

- One universal key for every course: `academy-of-things:theme`, values
  `light`, `dark`, or absent meaning system. It is deliberately not namespaced
  by course slug, so the choice follows the reader across courses.
- Applied as `data-theme="light|dark"` on `<html>`. No attribute means system.
- A tiny inline script in `<head>` of `course.html` sets the attribute before
  first paint, to avoid a flash of the wrong theme. It validates the stored
  value and ignores anything else.
- Control: a three-segment System / Light / Dark control in the sidebar footer.
- The landing page in `serve.py` has its own styles and is out of scope. It can
  read the same key later.

## No hardcoded colors

- Every color is a CSS custom property declared once in the token block at the
  top of `style.css`, using `light-dark(<light>, <dark>)` with
  `color-scheme: light dark` on `:root`, `light` under `[data-theme="light"]`,
  `dark` under `[data-theme="dark"]`. One definition per token, no duplicated
  dark set. `light-dark()` is Baseline 2024; older browsers are unsupported and
  that is accepted.
- Outside the token block, `style.css` contains no color literals (hex, rgb,
  hsl, named colors other than `transparent` and `currentColor`). `app.js`
  contains none either. Verified by grep as part of "done".
- Tokens cover: page, panel, raised, hover, border, border-strong, text, muted,
  accent, accent-strong, good, good-bg, bad, bad-bg, code-bg, and focus ring.
  Existing hardcoded values (`#1f232c`, `#d3d6dc`, `#14171d` and similar) are
  replaced by tokens.

## UI

Shared helper `segmented(container, name, label, options, value, onChange)` renders a
control from real radio inputs inside labels, so keyboard and screen-reader
behaviour is native. Used for the level switcher and the theme control.

- Level switcher: top of the sidebar, under the course title. Hidden without
  `levels`. Labels are the level slugs, capitalized by CSS.
- Sidebar progress: one green segment per written lesson, plus "N of M
  complete" text. Stubs are excluded from segments and from the denominator, as
  today.
- Lesson rows: leading status icon drawn in CSS, with visually-hidden status
  text. States: done (check), current (filled dot, row tinted and bordered),
  not started (empty ring), stub (dashed ring, muted text). The old text badges
  go away.
- Quiz: answer rows get a tint and a 3px left border for correct (green) and
  incorrect (red), with a check or cross mark. Explanation sits under each
  question and shows for right and wrong alike. An unanswered question at
  check time gets a danger border. Behaviour is unchanged: answer every
  question, check, retry on fail, pass marks the lesson complete.
- Mobile (max-width 800px): sidebar stacks above content as today; segmented
  controls stay full width.

## Engine edits (kept small)

| File | Change |
| --- | --- |
| `engine/app.js` | Level and theme resolution, fallback fetch, `segmented()`, sidebar and quiz markup, the "no <level> version" note inserted after the lesson h1. |
| `engine/course.html` | Head script for theme; sidebar containers for the level switcher and theme control. |
| `engine/style.css` | Token block with light/dark, component restyle. Everything else reuses existing selectors. |

After the engine copy changes, `engine/course.html` is re-copied verbatim to
`courses/example-course/index.html` and `courses/okta-workflows/index.html`
and checked with `diff`. `okta-workflows` receives only that identical
`index.html`; its manifest and lessons are untouched, and it must still work
with no `levels`.

## Other deliverables

- `courses/example-course`: add `levels`, `lesson.beginner.md` and
  `lesson.advanced.md` for lesson 1, and `quiz.advanced.json` for lesson 1.
  Lesson 2 stays single-version to exercise the "No <level> version" note. Content is
  about the course format itself, so every claim is checkable in this repo.
- `FORMAT.md`: document `levels`, variant files, fallback, state keys, theme.
- `scripts/new-course.sh`: optional levels flag that writes `levels` and
  variant stubs; default output unchanged.
- `skills/academy-of-things-course-builder/SKILL.md`: teach levels, variant
  files and the fallback rule. Edited in `skills/`, never under
  `.claude/skills/`.
- `scripts/package-course.sh`: check that standalone zips still work with the
  new engine; change only if broken.

## Verification ("done means served")

No test framework is added. Run `python3 serve.py <free port>` (not 8000,
which oMLX owns; never kill unknown PIDs), then in a browser:

1. `example-course`: switch every level, click every lesson, take every quiz,
   including pass and fail paths. Confirm the "No <level> version" note on lesson 2
   at every level, and on lesson 1 at intermediate only.
2. Reload and open with `?level=advanced` and with an invalid level; confirm
   persistence and the ignore rule.
3. Theme: System, Light, Dark; reload with each; confirm no flash and that the
   key is shared by both courses. Toggle the OS theme while on System.
4. `okta-workflows`: no switcher, behaves as before, themed.
5. Mobile width: sidebar, controls and quiz usable.
6. `grep` confirms no color literals outside the token block.
7. `diff` confirms every `courses/*/index.html` equals `engine/course.html`.

## Out of scope

Per-level progress, level-specific lesson order or titles, a new landing page,
animation, and any change to `okta-workflows` content.
