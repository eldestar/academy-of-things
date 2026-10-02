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

## quiz.json

Optional. Omit the file and the lesson simply has no quiz.

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
complete when you click through it.

## State

Progress lives in the browser's `localStorage` under
`academy-of-things:<slug>:progress`. Nothing is sent anywhere, there is no
account, and clearing site data resets it. Two people using the same course
on the same machine share the same progress.

## Constraints worth knowing

- **Must be served over HTTP.** The engine `fetch`es `manifest.json` and the
  lesson files; browsers block that on `file://`. Use `serve.py`.
- **Served from the repo root**, because a course references
  `../../engine/`. `scripts/package-course.sh` produces a standalone copy
  with the engine vendored in, for handing a single course to someone.
- **One external dependency**: marked.js from cdnjs, for Markdown rendering.
  Everything else is hand-written HTML, CSS and JS in `engine/`.
