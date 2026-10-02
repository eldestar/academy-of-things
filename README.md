# Academy of Things

Small, honest training courses that run from a folder. Markdown lessons, JSON
quizzes, one 300-line engine, no backend, no build step, no account.

```bash
git clone https://github.com/eldestar/academy-of-things.git
cd academy-of-things && python3 serve.py
```

Open http://localhost:8000 and start with **Example Course**, which teaches
the format by being written in it.

## Why this exists

It started as a way to close a specific skills gap before a job interview —
Terraform and identity protocols — and the quickest honest thing to build was
a folder of lessons and a hundred lines of JavaScript. It turned out that was
the whole product. Most internal training tooling is a platform when what was
actually needed was a folder, a quiz, and somewhere to track that you finished.

So the design holds a line: **no filler**. A lesson that has not been written
is marked as a stub and shown as unwritten, in the sidebar and in the progress
bar. It is never padded out to look complete. That one rule is what makes a
course trustworthy, and both generation skills enforce it.

## What is here

| Path | What it is |
| --- | --- |
| `engine/` | The whole engine: `app.js`, `style.css`, and `course.html`. One copy, shared by every course. |
| `courses/` | Courses. Ships with `example-course`. Drop more in and they appear. |
| `skills/` | Two Claude skills — one generates a course from a subject, one converts material you already have. |
| `adapters/` | The same instructions for Cursor, Copilot, Codex, or any chat assistant. |
| `scripts/` | `new-course.sh` scaffolds one, `package-course.sh` zips one up to share. |
| `serve.py` | Local static server. The only runtime dependency is Python 3. |
| `FORMAT.md` | The course format — the actual interface. |
| `AUTHORING.md` | What separates a course people finish from one they close. |
| `INSTALL.md` | Running it, and wiring it to whichever AI tool you use. |

## Using it with an AI tool

The format is plain folders, Markdown and JSON, so any assistant that can
write files can write a course. Claude gets the two full skills in `skills/`;
everything else gets the same rules as plain context from `adapters/`. If you
use something not listed, paste `FORMAT.md` and `adapters/PROMPT.md` into any
chat window and it will work.

You can also ignore all of it and write the files yourself. That is the point
of keeping the format this small.

## Sharing one course

```bash
./scripts/package-course.sh example-course   # -> dist/example-course.zip
```

The zip is self-contained — engine vendored in, runs with `python3 serve.py`
from inside the folder. Hand it to someone who has never seen this repo.
Going the other way, a course zip you were given unzips straight into
`courses/`.

## What it deliberately does not do

No accounts, no server, no completion reporting, no SCORM, no LMS. Progress is
one browser's `localStorage`. If you need to prove to an auditor that someone
completed training, this is the wrong tool — it is built for self-directed
learning, not compliance.

## Contributing

Course contributions are welcome, especially ones that teach the failure modes
of something you have actually operated. Read `AUTHORING.md` first. A short,
honest course with three real lessons is worth more than a padded ten.

## License

MIT — see [LICENSE](LICENSE).
