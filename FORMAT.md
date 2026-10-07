# Course format

A course is a folder. Nothing is compiled, generated or registered. If the
folder is shaped like this, the engine renders it.

```
courses/<slug>/
  index.html                  copied verbatim from engine/course.html
  manifest.json               the course's table of contents
  lessons/
    01-first-lesson/
      lesson.md               the lesson body (Markdown)
      quiz.json               optional
      lesson.beginner.md      optional, one per level (see Levels)
      quiz.advanced.json      optional, one per level
    02-second-lesson/
      lesson.md
      quiz.json
```

Lesson folder names are the lesson `id`. Prefix them with a zero-padded
number so they sort correctly on disk; the engine orders by the `lessons`
array in `manifest.json`, not by filename.

## manifest.json

```json
{
  "slug": "identity-protocols",
  "title": "Identity Protocols Deep Dive",
  "subtitle": "SAML, OIDC, OAuth 2.0, and SCIM — architect-level, not just configure-level",
  "lessons": [
    { "id": "01-saml", "title": "1. SAML" },
    { "id": "02-oidc-oauth2", "title": "2. OIDC & OAuth 2.0" },
    { "id": "03-scim", "title": "3. SCIM", "stub": true,
      "outline": "## Coming next\n\n- What SCIM is for\n- Where it breaks" }
  ]
}
```

| Field | Required | Notes |
| --- | --- | --- |
| `slug` | yes | Namespaces the browser's saved progress. Keep it stable — changing it resets everyone's progress. |
| `title` | yes | Shown in the sidebar and on the landing page. |
| `subtitle` | no | One line under the title. |
| `levels` | no | Array of level slugs (lowercase letters, digits, hyphens), in display order. The first is the default. Adds a level switcher. Omit it and the course has no levels. Duplicates and malformed entries are ignored. See [Levels](#levels). |
| `lessons[].id` | yes | Must match the folder name under `lessons/`. |
| `lessons[].title` | yes | Sidebar label. Number it yourself if you want numbers shown. |
| `lessons[].stub` | no | `true` means outlined but not written. Renders the `outline` instead of looking for `lesson.md`, greys the sidebar entry, and excludes it from the progress denominator. |
| `lessons[].outline` | no | Markdown shown in place of a stub lesson. Say what the lesson will cover. |

**Stubs are a feature, not a gap.** A lesson that isn't written is marked
`"stub": true` and shown as unwritten. Do not pad a thin lesson out with
filler to make a course look finished — an honest stub is more useful than
three paragraphs of generated throat-clearing.

## lesson.md

Plain Markdown, rendered by marked.js. Start with a single `#` heading.
Fenced code blocks, tables, and lists all work. There is no front matter and
no templating — what you write is what renders.

Raw HTML passes through: the engine does not sanitize lesson text, and scripts
do not run. That is what lets a lesson carry an inline SVG diagram. Diagrams
are inline, not `<img>` files, on purpose: an SVG loaded as an image cannot see
the page's CSS variables, so it would not follow light and dark mode. Generate
them with `scripts/diagram.py` rather than hand-writing the markup (kinds:
sequence, anatomy, flow, stages, matrix); the generator's specs live beside the
course in `courses/<slug>/diagrams/`, one per level (`<id>.beginner.json`,
`<id>.json` for intermediate, `<id>.advanced.json`), ignored by the engine and
not shipped by `package-course.sh`. `scripts/check-diagrams.py` verifies every
diagram still matches its spec. A diagram must not
be the only place a fact appears.

## quiz.json

Optional. Omit the file and the lesson simply has no quiz. The engine reads
"missing" as a 404 from the server; any other failure to load the file shows a
message and the lesson is not marked complete.

```json
{
  "pass_threshold_pct": 80,
  "passing_note": "4 of 5 correct to pass.",
  "questions": [
    {
      "stem": "In SAML terminology, what is Okta's role?",
      "options": ["Service Provider", "Identity Provider", "Principal", "ACS"],
      "correct_index": 1,
      "explanation": "Okta authenticates the user and issues the signed assertion."
    }
  ]
}
```

| Field | Required | Notes |
| --- | --- | --- |
| `pass_threshold_pct` | no | Defaults to 80. |
| `passing_note` | no | Shown above the questions. Spell out the arithmetic ("4 of 5 correct to pass") so the bar is obvious. |
| `questions[].stem` | yes | The question. |
| `questions[].options` | yes | Plain strings. Three or four is the useful range. |
| `questions[].correct_index` | yes | **Zero-based.** The most common authoring bug is off-by-one here. |
| `questions[].explanation` | yes in practice | Revealed after checking answers, for right and wrong alike. This is where the teaching actually happens — write it even when the answer looks obvious. |

Passing a quiz marks the lesson complete. A lesson with no quiz is marked
complete as soon as it is opened. The reader must answer every question
before checking; after checking, a failed attempt can be retried.

## Levels

Optional. Add `"levels"` to the manifest and the sidebar gets a segmented
switcher:

```json
"levels": ["beginner", "intermediate", "advanced"]
```

For each lesson the engine looks for a file named after the selected level
and falls back to the plain file:

| Selected level | Lesson body | Quiz |
| --- | --- | --- |
| `beginner` | `lesson.beginner.md`, else `lesson.md` | `quiz.beginner.json`, else `quiz.json` |
| `advanced` | `lesson.advanced.md`, else `lesson.md` | `quiz.advanced.json`, else `quiz.json` |

The two fallbacks are independent: you can fork a lesson's text without
forking its quiz, or the reverse. `lesson.md` and `quiz.json` are therefore the
standard version and the fallback for every level that has no file of its own.
Stub lessons render their `outline` at every level.

Give every lesson that has a `quiz.<level>.json` a plain `quiz.json` too.
Without it the other levels have no quiz, and a lesson with no quiz is marked
complete as soon as it opens.

A `quiz.<level>.json` that is not valid JSON shows an error naming the file and does not fall back to `quiz.json`; that lesson cannot be completed at that level until the file is fixed.

When the lesson body fell back to `lesson.md`, the engine shows one line under
the title: `No <level> version of this lesson; showing the standard text.` A
lesson that only ever has `lesson.md` reads that way at every level, which is
fine and honest. Do not copy the same text into every level file.

Progress is per lesson, not per level: passing a lesson's quiz at any level
marks it complete everywhere. Switching level re-renders the open lesson and
discards any quiz answers not yet checked.

A missing level file is detected from a 404 response, so the server has to
return a real 404 for it (`serve.py` does). A host that answers every unknown
path with 200 and an HTML page will break the fallback, and one that answers
with another error status (a 403 for missing files, say) shows a load error
instead of falling back.

Each lesson open at a level asks for the level file first, so the browser's
developer console shows one failed-request (404) line per missing variant. That
is expected, not an error in your course.

## State

Everything lives in the browser's `localStorage`. Nothing is sent anywhere,
there is no account, and clearing site data resets it. Two people using the
same course on the same machine share the same state.

| Key | Holds |
| --- | --- |
| `academy-of-things:<slug>:progress` | Completed lessons for one course. |
| `academy-of-things:<slug>:level` | The selected level for one course. `?level=<level>` seeds it once and is then removed from the URL; values the manifest does not declare are ignored. A stored value the manifest no longer declares falls back to the first level. |
| `academy-of-things:theme` | `light` or `dark`. Absent means follow the system. One key for every course. |

## Constraints worth knowing

- **Must be served over HTTP.** The engine `fetch`es `manifest.json` and the
  lesson files; browsers block that on `file://`. Use `serve.py`.
- **Served from the repo root**, because a course references
  `../../engine/`. `scripts/package-course.sh` produces a standalone copy
  with the engine vendored in, for handing a single course to someone.
- **One external dependency**: marked.js from cdnjs, for Markdown rendering.
  Everything else is hand-written HTML, CSS and JS in `engine/`.
- **Modern browser.** Colors use `light-dark()`, `color-mix()` and `:has()`
  (Baseline 2024 and later). Older browsers are not supported.
