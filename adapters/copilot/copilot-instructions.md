# Academy of Things

Courses live in `courses/<slug>/` as Markdown lessons plus JSON quizzes.
Read `FORMAT.md` (layout and schema) and `AUTHORING.md` (what makes a lesson
worth reading) before creating or editing one.

- Scaffold with `./scripts/new-course.sh <slug> "<Title>" "<Subtitle>"`.
- Never edit a course's `index.html` — it is copied from `engine/course.html`.
- `correct_index` is zero-based; verify every value.
- Unwritten lessons are `"stub": true` with an `outline`, never filler.
- Verify with `python3 serve.py` and click through before calling it done.
