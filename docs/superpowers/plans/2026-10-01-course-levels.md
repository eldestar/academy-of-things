# Course Levels, Restyle and Theming Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add optional Beginner/Intermediate/Advanced levels to the course engine, restyle the sidebar and quiz, and add light/dark/system theming with every color defined once as a token.

**Architecture:** Vanilla JS and CSS in `engine/`, shared by every course. Levels resolve from `?level=`, then `localStorage`, then the first declared level, and select `lesson.<level>.md` / `quiz.<level>.json` with fallback to the plain files. Theme is a `data-theme` attribute on `<html>` set from one universal `localStorage` key; colors come from `light-dark()` tokens.

**Tech Stack:** HTML, CSS (`light-dark()`, `color-mix()`, `:has()`), vanilla JS, marked.js (unchanged), bash, `python3 serve.py`.

**Spec:** `docs/superpowers/specs/2026-10-01-course-levels-design.md`

**Working directory for every command:** `/Users/BenjaminMac/dev/projects/academy-of-things/.claude/worktrees/academy-levels-feature-48682d` (a git worktree; never `cd` to the main checkout). Branch `claude/academy-levels-feature-48682d`.

## How testing works here

There is no test framework and none is added (repo rule: "Done means served"). A "test" is a check run in the browser against `python3 serve.py`: a `javascript_tool` snippet with an expected result, or a screenshot. Each task writes the check first, runs it to see it fail, implements, and runs it again to see it pass.

Server: port **8137** (not 8000; oMLX owns it; never kill a process you did not start). Start it with `Bash` `run_in_background` and stop it with `TaskStop` at the end. Browser: the built-in browser tools (`mcp__Claude_Browser__*`). Clear test state between checks with `localStorage.clear()` in the page.

Browser cache: `serve.py` sends only `Last-Modified`, so the browser can serve a stale `app.js` or `style.css` after an edit. Before each check, reload with a cache bust (for example `await Promise.all(['app.js','style.css'].map(f => fetch('/engine/'+f, {cache: 'reload'})))` then `location.reload()`), and confirm the change is live.

Commit rule for every task: `git add` the listed files, run `gitleaks protect --staged`, then commit with the trailer line shown. Never commit if gitleaks reports a finding.

## File structure

| File | Responsibility | Tasks |
| --- | --- | --- |
| `engine/style.css` | Token block, theme, all component styles | 1, 2, 3 |
| `engine/course.html` | Page shell: head theme script, sidebar containers | 1, 2, 5 |
| `engine/app.js` | Behaviour: theme, levels, sidebar render, quiz render | 1, 2, 5 |
| `courses/*/index.html` | Verbatim copies of `engine/course.html` | 1, 2, 5 |
| `courses/example-course/**` | Level test fixtures and updated prose | 2, 4 |
| `scripts/new-course.sh` | `--levels` scaffolding | 6 |
| `FORMAT.md`, `skills/academy-of-things-course-builder/SKILL.md` | Documentation | 7 |
| `docs/superpowers/specs/...` | Spec amendments found while planning | 0 |

Not touched: `engine/`-external files beyond the list, `courses/okta-workflows/` except its `index.html` copy, `AUTHORING.md`, `serve.py`, `.claude/skills/`.

Re-copy helper used in several tasks (run from the repo root):

```bash
for c in courses/*/; do cp engine/course.html "${c}index.html"; done
for c in courses/*/; do diff -q engine/course.html "${c}index.html" && echo "match: $c"; done
```

---

### Task 0: Amend the spec for three details found while planning

Planning surfaced three places where the spec's wording does not hold up. Fix the spec first so spec and plan agree.

1. "Same content at every level" is false on a lesson that has beginner and advanced files when the reader is at intermediate (it falls back to `lesson.md`, which differs from the other two). The engine cannot know without probing every level, so the note states only what is true for the level being read.
2. The note is inserted by JS after the lesson's `<h1>`, so `course.html` needs no note slot.
3. `segmented()` takes an accessible group label.

**Files:**
- Modify: `docs/superpowers/specs/2026-10-01-course-levels-design.md`

- [ ] **Step 1: Edit the note wording**

Replace

```
- A lesson whose body fell back to `lesson.md` shows one line under the title:
  "Same content at every level." Stub lessons and courses without `levels`
  never show it. A quiz-only fallback shows nothing.
```

with

```
- A lesson whose body fell back to `lesson.md` shows one line under the title:
  "No <level> version of this lesson; showing the standard text." The engine
  cannot know whether other levels differ without probing them, so the note
  states only what is true for the level being read. For a lesson that has
  only `lesson.md` it reads the same at every level. Stub lessons and courses
  without `levels` never show it. A quiz-only fallback shows nothing.
```

- [ ] **Step 2: Edit the helper signature, engine table and verification wording**

Replace `segmented(container, name, options, value, onChange)` with `segmented(container, name, label, options, value, onChange)`.

Replace `Head script for theme; sidebar containers for switcher, note slot and theme control.` with `Head script for theme; sidebar containers for the level switcher and theme control.`

Replace `Level and theme resolution, fallback fetch, `segmented()`, sidebar and quiz markup, "same content" note.` with `Level and theme resolution, fallback fetch, `segmented()`, sidebar and quiz markup, the "no <level> version" note inserted after the lesson h1.`

Replace

```
Confirm the "same content" note on lesson 2
   and its absence on lesson 1 at levels that have a variant.
```

with

```
Confirm the "No <level> version" note on lesson 2
   at every level, and on lesson 1 at intermediate only.
```

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/specs/2026-10-01-course-levels-design.md docs/superpowers/plans/2026-10-01-course-levels.md
gitleaks protect --staged
git commit -m "Docs: amend levels spec (note wording, helper signature) and add plan" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 1: Theme tokens, light/dark/system, theme switcher

Converts every color in `style.css` to a token, adds the theme control, adds the shared `segmented()` helper. Visual design of lessons and quizzes is unchanged in this task.

**Files:**
- Modify: `engine/style.css` (replace whole file)
- Modify: `engine/course.html` (replace whole file)
- Modify: `engine/app.js` (insert helpers before `renderSidebar`; call in `initCourse`)
- Modify: `courses/example-course/index.html`, `courses/okta-workflows/index.html` (re-copy)

- [ ] **Step 1: Baseline and server**

```bash
lsof -nP -iTCP:8137 -sTCP:LISTEN || echo "8137 free"
for c in courses/*/; do diff -q engine/course.html "${c}index.html" && echo "baseline match: $c"; done
```

Expected: `8137 free`, and `baseline match:` for both courses. If either differs, stop and report; that is an existing bug, not part of this task.

Start the server with `Bash` `run_in_background`: `python3 serve.py 8137`. Open `http://localhost:8137/courses/okta-workflows/` in the built-in browser.

- [ ] **Step 2: Write the failing check**

Run in the page with `javascript_tool`:

```js
!!document.querySelector('#theme-switcher input[value=dark]')
```

Expected now: `false` (FAIL: no theme control exists).

- [ ] **Step 3: Replace `engine/style.css`**

Write the whole file:

```css
:root {
  color-scheme: light dark;
  --bg:            light-dark(#ffffff, #0f1115);
  --panel:         light-dark(#f7f8fa, #171a21);
  --raised:        light-dark(#ffffff, #1c2029);
  --hover:         light-dark(#eceef3, #1f232c);
  --border:        light-dark(#e1e4ea, #2a2e38);
  --border-strong: light-dark(#c4c9d4, #3d4352);
  --text:          light-dark(#1b1f27, #e6e8ec);
  --body:          light-dark(#2f3542, #d3d6dc);
  --muted:         light-dark(#5b6472, #9aa1ad);
  --accent:        light-dark(#2f6fb5, #4a90d9);
  --on-accent:     light-dark(#ffffff, #0f1115);
  --good:          light-dark(#1f8a4c, #2e9e5b);
  --good-text:     light-dark(#17703d, #5fd08c);
  --good-bg:       light-dark(#e6f4ec, #14261c);
  --bad:           light-dark(#c4423e, #d9534f);
  --bad-text:      light-dark(#b0332f, #ff8a86);
  --bad-bg:        light-dark(#fbeceb, #2b1717);
  --code-bg:       light-dark(#f1f3f6, #11141a);
}
:root[data-theme="light"] { color-scheme: light; }
:root[data-theme="dark"] { color-scheme: dark; }
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}
a { color: var(--accent); }
a:focus-visible, button:focus-visible, .option:focus-within {
  outline: 2px solid var(--accent); outline-offset: 2px;
}
.sr-only {
  position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0;
  overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0;
}
.layout { display: grid; grid-template-columns: 280px 1fr; min-height: 100vh; }
.sidebar {
  background: var(--panel);
  border-right: 1px solid var(--border);
  padding: 24px 16px;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
.sidebar .home { align-self: flex-start; display: inline-block; font-size: 12px; margin-bottom: 14px; text-decoration: none; color: var(--muted); }
.sidebar .home:hover { color: var(--text); }
.sidebar .course-title { font-size: 16px; font-weight: 700; margin: 0 0 4px; }
.sidebar .subtitle { color: var(--muted); font-size: 12px; margin-bottom: 20px; }
.segmented { display: flex; gap: 2px; padding: 2px; margin: 0 0 16px; background: var(--bg); border: 1px solid var(--border); border-radius: 8px; }
.segmented[hidden] { display: none; }
.segmented label { position: relative; flex: 1; text-align: center; padding: 5px 4px; border-radius: 6px; font-size: 12px; color: var(--muted); cursor: pointer; text-transform: capitalize; }
.segmented label:hover { color: var(--text); }
.segmented label:has(input:checked) { background: var(--raised); color: var(--text); box-shadow: inset 0 0 0 1px var(--border-strong); }
.segmented label:has(input:focus-visible) { outline: 2px solid var(--accent); outline-offset: 2px; }
.segmented input { position: absolute; inset: 0; margin: 0; opacity: 0; cursor: pointer; }
.sidebar-foot { margin-top: auto; padding-top: 16px; }
.sidebar-foot .segmented { margin: 0; }
.lesson-list { list-style: none; padding: 0; margin: 0; }
.lesson-list li a {
  display: flex; justify-content: space-between; gap: 8px;
  padding: 10px 12px; border-radius: 6px; color: var(--text);
  text-decoration: none; font-size: 14px; margin-bottom: 2px;
}
.lesson-list li a:hover { background: var(--hover); }
.lesson-list li a.active { background: var(--accent); color: var(--on-accent); }
.lesson-list li a.active .badge { background: var(--hover); color: var(--text); }
.lesson-list li a.locked { color: var(--muted); }
.badge { flex-shrink: 0; align-self: flex-start; white-space: nowrap; font-size: 11px; padding: 1px 6px; border-radius: 10px; background: var(--border); color: var(--muted); }
.badge.done { background: var(--good); color: var(--on-accent); }
.badge.stub { background: transparent; border: 1px dashed var(--muted); }
main { padding: 40px 56px; max-width: 820px; min-width: 0; }
.progress-label { font-size: 12px; color: var(--muted); margin-bottom: 16px; }
.progress-bar-outer { background: var(--border); border-radius: 8px; height: 8px; margin: 8px 0 20px; overflow: hidden; }
.progress-bar-inner { background: var(--accent); height: 100%; transition: width 0.3s ease; }
article h1 { font-size: 28px; margin-top: 0; }
article h2 { font-size: 20px; margin-top: 32px; border-bottom: 1px solid var(--border); padding-bottom: 6px; }
article h3 { font-size: 16px; margin-top: 24px; }
article p, article li { color: var(--body); }
article code { background: var(--code-bg); padding: 2px 6px; border-radius: 4px; font-size: 13px; }
article table { border-collapse: collapse; display: block; overflow-x: auto; margin: 16px 0; }
article th, article td { border: 1px solid var(--border); padding: 6px 12px; text-align: left; vertical-align: top; }
article pre { background: var(--code-bg); border: 1px solid var(--border); border-radius: 8px; padding: 16px; overflow-x: auto; }
article pre code { background: none; padding: 0; }
article blockquote {
  border-left: 3px solid var(--accent); margin: 16px 0; padding: 4px 16px;
  color: var(--muted); background: var(--panel); border-radius: 0 6px 6px 0;
}
.quiz { margin-top: 40px; border-top: 2px solid var(--border); padding-top: 24px; }
.quiz h2 { border: none; }
.passing-note { color: var(--muted); }
.question { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 18px 20px; margin-bottom: 16px; }
.question .stem { font-weight: 600; margin: 0 0 10px; }
.question.unanswered { border-color: var(--bad); }
.options { display: flex; flex-direction: column; gap: 8px; }
.option { display: flex; align-items: center; gap: 10px; padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px; cursor: pointer; }
.option:hover { border-color: var(--accent); }
.option:has(input:checked) { border-color: var(--accent); background: color-mix(in srgb, var(--accent) 12%, transparent); }
.option input:disabled { opacity: 1; }
.option input { accent-color: var(--accent); flex-shrink: 0; }
.option-text { flex: 1; }
.mark { font-size: 12px; font-weight: 600; white-space: nowrap; }
.option.correct .mark { color: var(--good-text); }
.option.incorrect .mark { color: var(--bad-text); }
.options .option.correct { border-color: var(--good); background: color-mix(in srgb, var(--good) 12%, transparent); }
.options .option.incorrect { border-color: var(--bad); background: color-mix(in srgb, var(--bad) 12%, transparent); }
.explanation { margin-top: 10px; font-size: 13px; color: var(--muted); display: none; }
.explanation.show { display: block; }
.quiz-result { margin-top: 20px; padding: 16px 20px; border-radius: 8px; background: var(--panel); border: 1px solid var(--border); }
.quiz-result.pass { border-color: var(--good); }
.quiz-result.fail { border-color: var(--bad); }
button.primary { background: var(--accent); color: var(--on-accent); border: none; padding: 10px 18px; border-radius: 6px; font-size: 14px; cursor: pointer; margin-top: 16px; }
button.primary:hover { opacity: 0.9; }
button.secondary { background: transparent; border: 1px solid var(--border); color: var(--text); padding: 10px 18px; border-radius: 6px; cursor: pointer; margin-top: 16px; margin-left: 8px; }
footer.nav { display: flex; justify-content: space-between; margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--border); }
footer.nav a { text-decoration: none; font-size: 14px; }
footer.nav a[hidden] { display: block; visibility: hidden; }

@media (max-width: 800px) {
  .layout { grid-template-columns: 1fr; }
  .sidebar { position: static; height: auto; border-right: none; border-bottom: 1px solid var(--border); padding: 16px; }
  .lesson-list { max-height: 35vh; overflow-y: auto; }
  main { padding: 24px 16px; }
  footer.nav { flex-direction: column; gap: 12px; }
  footer.nav a[hidden] { display: none; }
}
```

- [ ] **Step 4: Replace `engine/course.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="light dark">
<title>Course</title>
<script>
/* Apply the saved theme before first paint. One key for every course; keep in sync with THEME_KEY in app.js. */
try {
  var t = localStorage.getItem('academy-of-things:theme');
  if (t === 'light' || t === 'dark') document.documentElement.dataset.theme = t;
} catch (e) {}
</script>
<link rel="stylesheet" href="../../engine/style.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script>
</head>
<body>
<div class="layout">
  <aside class="sidebar">
    <a class="home" href="../../">&larr; All courses</a>
    <p class="course-title" id="course-title">Loading…</p>
    <div class="subtitle" id="course-subtitle"></div>
    <div class="progress-bar-outer"><div class="progress-bar-inner" id="progress-fill" style="width:0%"></div></div>
    <div id="progress-label" class="progress-label"></div>
    <nav aria-label="Lessons"><ul class="lesson-list" id="lesson-list"></ul></nav>
    <div class="sidebar-foot"><div id="theme-switcher"></div></div>
  </aside>
  <main>
    <article id="lesson-content"></article>
    <div id="quiz-container"></div>
    <footer class="nav" id="lesson-nav"></footer>
  </main>
</div>
<script src="../../engine/app.js"></script>
</body>
</html>
```

- [ ] **Step 5: Add helpers to `engine/app.js`**

Insert immediately before `function renderSidebar(`:

```js
// One theme choice for every course, so it is deliberately not namespaced by
// slug. The inline script in course.html reads the same key before first paint.
const THEME_KEY = 'academy-of-things:theme';

function storageGet(key) {
  try {
    return localStorage.getItem(key);
  } catch (e) {
    return null;
  }
}

function storageSet(key, value) {
  try {
    if (value == null) localStorage.removeItem(key);
    else localStorage.setItem(key, value);
  } catch (e) {
    // storage blocked (private mode, quota): the choice just won't persist
  }
}

// Radio group styled as a segmented control; native radios give keyboard and
// screen-reader behaviour for free. Option values double as visible labels.
function segmented(container, name, label, options, value, onChange) {
  container.innerHTML = '';
  container.classList.add('segmented');
  container.setAttribute('role', 'radiogroup');
  container.setAttribute('aria-label', label);
  options.forEach((opt) => {
    const lab = document.createElement('label');
    const input = document.createElement('input');
    input.type = 'radio';
    input.name = name;
    input.value = opt;
    input.checked = opt === value;
    input.addEventListener('change', () => onChange(opt));
    const text = document.createElement('span');
    text.textContent = opt;
    lab.append(input, text);
    container.appendChild(lab);
  });
}

function initThemeSwitcher() {
  const current = document.documentElement.dataset.theme || 'system';
  segmented(document.getElementById('theme-switcher'), 'theme', 'Theme', ['system', 'light', 'dark'], current, (theme) => {
    if (theme === 'system') delete document.documentElement.dataset.theme;
    else document.documentElement.dataset.theme = theme;
    storageSet(THEME_KEY, theme === 'system' ? null : theme);
  });
}

```

Then in `initCourse`, make the first line `initThemeSwitcher();` (before `const manifest = await loadManifest();`), so the theme control works even if the manifest fails to load.

- [ ] **Step 6: Re-copy `course.html` to every course**

Run the re-copy helper from the top of this plan. Expected: `match:` for both courses.

- [ ] **Step 7: Run the check to see it pass**

Reload `http://localhost:8137/courses/okta-workflows/`, run in the page:

```js
localStorage.clear();
const out = {};
out.hasSwitcher = !!document.querySelector('#theme-switcher input[value=dark]');
document.querySelector('#theme-switcher input[value=dark]').click();
out.darkAttr = document.documentElement.dataset.theme;
out.darkBg = getComputedStyle(document.body).backgroundColor;
out.darkKey = localStorage.getItem('academy-of-things:theme');
document.querySelector('#theme-switcher input[value=light]').click();
out.lightBg = getComputedStyle(document.body).backgroundColor;
document.querySelector('#theme-switcher input[value=system]').click();
out.sysAttr = document.documentElement.dataset.theme ?? null;
out.sysKey = localStorage.getItem('academy-of-things:theme');
out
```

Expected: `hasSwitcher: true`, `darkAttr: "dark"`, `darkBg: "rgb(15, 17, 21)"`, `darkKey: "dark"`, `lightBg: "rgb(255, 255, 255)"`, `sysAttr: null`, `sysKey: null`.

Persistence and first paint: click Dark, reload, run `document.documentElement.dataset.theme` (expect `"dark"`). Then click System, reload, and with the browser's `resize_window` `colorScheme: "dark"` run `getComputedStyle(document.body).backgroundColor` (expect `rgb(15, 17, 21)`), then `colorScheme: "light"` (expect `rgb(255, 255, 255)`).

Take one screenshot in each theme and look at them: text readable, sidebar/panel distinct from page, active lesson row visible, no unstyled leftovers.

- [ ] **Step 8: No color literals outside the token block**

```bash
awk '/^:root \{/{t=1} t&&/^\}/{t=0; next} !t' engine/style.css | grep -nE '#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(|(^|[^-a-z])(white|black|red|green|blue|gray|grey)([^-a-z]|$)' || echo "clean: no literals outside token block"
grep -nE '#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(' engine/app.js engine/course.html || echo "clean: none in app.js or course.html"
```

Expected: both `clean:` lines. Note `course.html` has none because the head script uses no colors.

- [ ] **Step 9: Commit**

```bash
git add engine/style.css engine/course.html engine/app.js courses/example-course/index.html courses/okta-workflows/index.html
gitleaks protect --staged
git commit -m "Engine: color tokens, light/dark/system theme and theme switcher" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Sidebar status icons and segmented progress

**Files:**
- Modify: `engine/app.js` (`renderSidebar`)
- Modify: `engine/course.html` (progress markup)
- Modify: `engine/style.css` (lesson rows, progress)
- Modify: `courses/example-course/lessons/01-anatomy-of-a-course/lesson.md` (stale "progress bar" wording)
- Modify: `courses/*/index.html` (re-copy)

- [ ] **Step 1: Write the failing check**

Open `http://localhost:8137/courses/example-course/`, run:

```js
localStorage.setItem('academy-of-things:example-course:progress', JSON.stringify({'01-anatomy-of-a-course': {completed: true}}));
location.reload();
```

then after load:

```js
({
  segments: document.querySelectorAll('#progress-segments span').length,
  doneSegments: document.querySelectorAll('#progress-segments span.done').length,
  label: document.getElementById('progress-label').textContent,
  icons: document.querySelectorAll('#lesson-list .status').length
})
```

Expected after implementation: `{segments: 2, doneSegments: 1, label: "1 of 2 complete", icons: 3}`. Now it errors or returns zeros (FAIL).

- [ ] **Step 2: Replace `renderSidebar` in `engine/app.js`**

Replace the whole function with:

```js
const STATUS_TEXT = { stub: 'coming next', done: 'completed', current: 'in progress', todo: 'not started' };

function renderSidebar(manifest, currentLessonId, progress) {
  const list = document.getElementById('lesson-list');
  list.innerHTML = '';
  const isDone = (l) => !!(progress[l.id] && progress[l.id].completed);

  manifest.lessons.forEach((lesson) => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = `?lesson=${lesson.id}`;
    const current = lesson.id === currentLessonId;
    let state = 'todo';
    if (lesson.stub) state = 'stub';
    else if (isDone(lesson)) state = 'done';
    else if (current) state = 'current';
    a.classList.add('is-' + state);
    if (current) {
      a.classList.add('active');
      a.setAttribute('aria-current', 'page');
    }

    const icon = document.createElement('span');
    icon.className = 'status';
    icon.setAttribute('aria-hidden', 'true');
    const title = document.createElement('span');
    title.textContent = lesson.title;
    const status = document.createElement('span');
    status.className = 'sr-only';
    status.textContent = ` (${STATUS_TEXT[state]})`;
    a.append(icon, title, status);
    li.appendChild(a);
    list.appendChild(li);
  });

  const written = manifest.lessons.filter((l) => !l.stub);
  const done = written.filter(isDone).length;
  const segments = document.getElementById('progress-segments');
  segments.innerHTML = '';
  written.forEach((l) => {
    const s = document.createElement('span');
    if (isDone(l)) s.className = 'done';
    segments.appendChild(s);
  });
  document.getElementById('progress-label').textContent = `${done} of ${written.length} complete`;
}
```

- [ ] **Step 3: Update `engine/course.html`**

Replace

```html
    <div class="progress-bar-outer"><div class="progress-bar-inner" id="progress-fill" style="width:0%"></div></div>
```

with

```html
    <div class="progress-segments" id="progress-segments" aria-hidden="true"></div>
```

Then run the re-copy helper. Expected: `match:` for both courses.

- [ ] **Step 4: Update `engine/style.css`**

Replace this block (exact text from Task 1):

```css
.lesson-list li a {
  display: flex; justify-content: space-between; gap: 8px;
  padding: 10px 12px; border-radius: 6px; color: var(--text);
  text-decoration: none; font-size: 14px; margin-bottom: 2px;
}
.lesson-list li a:hover { background: var(--hover); }
.lesson-list li a.active { background: var(--accent); color: var(--on-accent); }
.lesson-list li a.active .badge { background: var(--hover); color: var(--text); }
.lesson-list li a.locked { color: var(--muted); }
.badge { flex-shrink: 0; align-self: flex-start; white-space: nowrap; font-size: 11px; padding: 1px 6px; border-radius: 10px; background: var(--border); color: var(--muted); }
.badge.done { background: var(--good); color: var(--on-accent); }
.badge.stub { background: transparent; border: 1px dashed var(--muted); }
```

with:

```css
.lesson-list li a {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 8px 10px; border-radius: 6px; color: var(--text);
  text-decoration: none; font-size: 14px; line-height: 1.4; margin-bottom: 2px;
}
.lesson-list li a:hover { background: var(--hover); }
.lesson-list li a.active { background: var(--raised); box-shadow: inset 0 0 0 1px var(--border-strong); }
.lesson-list li a.is-stub { color: var(--muted); }
.status { position: relative; flex: none; width: 14px; height: 14px; margin-top: 2px; border: 1.5px solid var(--border-strong); border-radius: 50%; }
.is-stub .status { border-style: dashed; }
.is-current .status { border-color: var(--text); }
.is-current .status::after { content: ''; position: absolute; inset: 2.5px; border-radius: 50%; background: var(--text); }
.is-done .status { border-color: var(--good); background: var(--good); }
.is-done .status::after { content: ''; position: absolute; left: 3px; top: 0.5px; width: 3.5px; height: 6.5px; border: solid var(--on-accent); border-width: 0 1.5px 1.5px 0; transform: rotate(45deg); }
```

Replace these three lines:

```css
.progress-label { font-size: 12px; color: var(--muted); margin-bottom: 16px; }
.progress-bar-outer { background: var(--border); border-radius: 8px; height: 8px; margin: 8px 0 20px; overflow: hidden; }
.progress-bar-inner { background: var(--accent); height: 100%; transition: width 0.3s ease; }
```

with:

```css
.progress-segments { display: flex; gap: 2px; margin: 4px 0 8px; }
.progress-segments span { flex: 1; height: 3px; border-radius: 2px; background: var(--border-strong); }
.progress-segments span.done { background: var(--good); }
.progress-label { font-size: 12px; color: var(--muted); margin-bottom: 16px; }
```

- [ ] **Step 5: Fix the stale prose in the example lesson**

In `courses/example-course/lessons/01-anatomy-of-a-course/lesson.md`, replace

```
the progress bar says "0/2" rather than "0/3" — unwritten lessons are
excluded from the denominator rather than counted as incomplete work.
```

with

```
the progress label says "0 of 2 complete" rather than "0 of 3" — unwritten
lessons are excluded from the denominator rather than counted as incomplete
work.
```

- [ ] **Step 6: Run the check to see it pass**

Reload `http://localhost:8137/courses/example-course/` (progress from Step 1 is still set) and run the Step 1 second snippet. Expected: `{segments: 2, doneSegments: 1, label: "1 of 2 complete", icons: 3}`.

Screenshot in light and dark. Look at: lesson 1 shows a green check with its row tinted and outlined (it is both done and active); lesson 2 shows an empty ring; lesson 3 shows a dashed ring and muted text; the check mark is centered in its circle. If the check or dot is visibly off-center, adjust `left`/`top` by 0.5px steps and re-look; do not move on until it is centered. Then `localStorage.clear()` and reload: lesson 1 shows the filled-dot "current" state, label `0 of 2 complete`.

Also open `courses/okta-workflows/`: seven written lessons give seven segments, one stub icon, label `0 of 7 complete`.

- [ ] **Step 7: Re-run the literal check from Task 1 Step 8**

Expected: both `clean:` lines.

- [ ] **Step 8: Commit**

```bash
git add engine/app.js engine/course.html engine/style.css courses/example-course/index.html courses/okta-workflows/index.html courses/example-course/lessons/01-anatomy-of-a-course/lesson.md
gitleaks protect --staged
git commit -m "Engine: sidebar status icons and segmented progress" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Quiz states

CSS only. `renderQuiz` already adds `.correct`, `.incorrect`, `.unanswered`, the `✓ correct` / `✗ your answer` marks and the per-question explanation.

**Files:**
- Modify: `engine/style.css`

- [ ] **Step 1: Write the failing check**

Open `http://localhost:8137/courses/example-course/?lesson=01-anatomy-of-a-course`, `localStorage.clear()`, reload. Choose the first option of every question (this makes at least one wrong), click **Check answers**, then run:

```js
const right = document.querySelector('.options .option.correct');
const wrong = document.querySelector('.options .option.incorrect');
({
  rightBar: getComputedStyle(right).boxShadow,
  wrongBar: getComputedStyle(wrong).boxShadow,
  explanationBg: getComputedStyle(document.querySelector('.explanation.show')).backgroundColor
})
```

Expected after implementation: `rightBar` and `wrongBar` contain `inset` and `3px`; `explanationBg` equals the page background (`rgb(255, 255, 255)` in light, `rgb(15, 17, 21)` in dark). Now `rightBar` and `wrongBar` are `"none"` (FAIL).

- [ ] **Step 2: Update `engine/style.css`**

Replace

```css
.options .option.correct { border-color: var(--good); background: color-mix(in srgb, var(--good) 12%, transparent); }
.options .option.incorrect { border-color: var(--bad); background: color-mix(in srgb, var(--bad) 12%, transparent); }
.explanation { margin-top: 10px; font-size: 13px; color: var(--muted); display: none; }
```

with

```css
.options .option.correct { border-color: var(--good); background: var(--good-bg); box-shadow: inset 3px 0 0 var(--good); }
.options .option.incorrect { border-color: var(--bad); background: var(--bad-bg); box-shadow: inset 3px 0 0 var(--bad); }
.explanation { margin-top: 10px; padding: 8px 12px; border-radius: 6px; background: var(--bg); font-size: 13px; color: var(--muted); display: none; }
```

- [ ] **Step 3: Run the check to see it pass, in both themes**

Reload, redo the Step 1 clicks, run the snippet. Expected values as above. Switch the theme control to Dark and Light and screenshot the checked quiz each time. Look at: correct row green-tinted with a left bar, wrong row red-tinted with a left bar, `✓ correct` / `✗ your answer` marks readable, explanation block visible under each question, a question with no answer (reload, answer only some, click Check) gets a red border and the message `Answer every question first — N still blank.`

Pass path: reload, pick the right option for every question (Q1 option 2, Q2 option 2, Q3 option 3, Q4 option 2; numbering is 1-based here), click Check. Expected: `Passed: 4/4 correct (100%). Lesson marked complete.` and the sidebar shows the lesson done. Fail path: wrong answers show `Try again`, which clears the tints and explanations.

- [ ] **Step 4: Literal check and commit**

Re-run the Task 1 Step 8 check (expect both `clean:` lines), then:

```bash
git add engine/style.css
gitleaks protect --staged
git commit -m "Engine: quiz states with tinted rows, accent bar and explanation block" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Level fixtures in example-course (before the engine supports them)

Data first, so the next task has something to fail against. All content describes this repo's own format and engine, so every claim is checkable in `FORMAT.md` and `engine/app.js`.

**Files:**
- Modify: `courses/example-course/manifest.json`
- Modify: `courses/example-course/lessons/01-anatomy-of-a-course/lesson.md`
- Create: `courses/example-course/lessons/01-anatomy-of-a-course/lesson.beginner.md`
- Create: `courses/example-course/lessons/01-anatomy-of-a-course/lesson.advanced.md`
- Create: `courses/example-course/lessons/01-anatomy-of-a-course/quiz.advanced.json`

- [ ] **Step 1: Add `levels` to the manifest**

In `courses/example-course/manifest.json`, replace

```json
  "subtitle": "A working course that teaches the course format by being one",
```

with

```json
  "subtitle": "A working course that teaches the course format by being one",
  "levels": ["beginner", "intermediate", "advanced"],
```

- [ ] **Step 2: Add a Levels section to the base lesson (this is the intermediate text)**

In `lesson.md`, insert before the line `## What the engine does not do`:

```markdown
## Levels are optional

This course declares `"levels"` in its manifest, which is why the sidebar has
a Beginner, Intermediate and Advanced switch. A lesson can ship
`lesson.<level>.md` for any level; where it does not, the engine falls back to
`lesson.md`. This lesson has a beginner and an advanced version, so
intermediate reads this file. Lesson 2 has only `lesson.md`, so it reads the
same at every level.

```

- [ ] **Step 3: Create `lesson.beginner.md`**

```markdown
# Anatomy of a Course

A course is a folder of plain files. If you can make folders and edit text,
you can make a course. This lesson walks through the pieces, using the course
you are reading right now.

## The folder

```
courses/example-course/
  index.html          the page shell, identical in every course
  manifest.json       the table of contents
  lessons/
    01-anatomy-of-a-course/
      lesson.md       this text
      quiz.json       the questions below
```

Each lesson gets its own folder. The folder name is the lesson's `id`.

## Three kinds of file

- `index.html` is the page that loads everything. Every course has the same
  one, copied from `engine/course.html`. You never edit it.
- `manifest.json` is the table of contents: the course title and the list of
  lessons, in order.
- `lesson.md` is the lesson text, written in Markdown. `quiz.json` is an
  optional set of questions about it.

## Adding a lesson

Make a folder under `lessons/`, add one line for it in `manifest.json`, and
reload the page. It appears in the sidebar. There is nothing to build or
register.

## Stubs

A lesson you have planned but not written is a stub: it gets `"stub": true`
and an `outline` in the manifest. Lesson 3 of this course is one. It shows up
greyed out in the sidebar and does not count toward the progress label, which
reads "0 of 2 complete" rather than "0 of 3" before you finish anything.

Do not fill a lesson with filler text to make a course look finished. An
honest stub is more useful.

## Where your progress is saved

In this browser only. There are no accounts and nothing is sent anywhere.
The course's `slug` decides where progress is stored, so changing the slug
later resets everyone's progress. Choose it once.

## Levels

The Beginner, Intermediate and Advanced switch in the sidebar changes which
version of a lesson you read. This lesson has a beginner and an advanced
version; intermediate reads the standard text.
```

- [ ] **Step 4: Create `lesson.advanced.md`**

```markdown
# Anatomy of a Course

You have built a course before, or you are about to build several. This
lesson is the mechanism: what the engine fetches, in what order, and what it
keeps.

## The folder

```
courses/example-course/
  index.html          copied verbatim from engine/course.html — never edited
  manifest.json       the table of contents
  lessons/
    01-anatomy-of-a-course/
      lesson.md       the standard text (and the intermediate level's)
      lesson.beginner.md
      lesson.advanced.md
      quiz.json
      quiz.advanced.json
```

## What the engine reads

On load the engine fetches `./manifest.json`, then renders the lesson named by
`?lesson=<id>`, or the first lesson when the parameter is missing or unknown.
For that lesson it fetches `lessons/<id>/lesson.md` and then
`lessons/<id>/quiz.json`. Both paths are relative to the course folder, and
nothing in the engine ties the course folder's name to the manifest `slug`.
Only the lesson `id` has to match its folder.

A stub is never fetched. Its `outline` from the manifest is rendered instead,
so a stub needs no folder at all.

## Failure behaviour

- A missing `lesson.md` shows the title and a message naming the path that
  failed to load.
- A missing `quiz.json` means no quiz. That is normal and silent.
- A `quiz.json` that exists but is not valid JSON shows a message naming the
  file and the parse error. The lesson text still renders.

## State

One `localStorage` key per course: `academy-of-things:<slug>:progress`. It
holds an object keyed by lesson id, each with a `completed` flag and a
timestamp. A lesson with no quiz is marked complete as soon as it opens. A
lesson with a quiz is marked complete only when the reader passes it, and
failed attempts are not recorded. The slug is the only namespace, so renaming
it orphans every reader's saved progress.

## Levels

This course declares `levels` in its manifest. For the selected level the
engine tries `lesson.<level>.md` and `quiz.<level>.json` first and falls back
to `lesson.md` and `quiz.json`, each independently. You can fork the text
without forking the quiz, or the reverse. Progress is per lesson, not per
level. This lesson has a beginner and an advanced version; intermediate falls
back to `lesson.md`.

## What it does not do

No accounts, no server-side state, no completion reporting. If you need
audit-grade proof that someone finished training, this is the wrong tool.
```

- [ ] **Step 5: Create `quiz.advanced.json`**

`correct_index` values are zero-based: 1, 3, 0, 2. Verified against each `options` array below.

```json
{
  "pass_threshold_pct": 75,
  "passing_note": "3 of 4 correct to pass.",
  "questions": [
    {
      "stem": "A lesson folder contains lesson.md and no quiz.json. What happens when a reader opens the lesson?",
      "options": [
        "An empty quiz renders and can never be passed",
        "The lesson is marked complete as soon as it opens",
        "The lesson refuses to render until a quiz exists",
        "The lesson is marked complete once the reader scrolls to the end"
      ],
      "correct_index": 1,
      "explanation": "A missing quiz.json simply means no quiz, and a lesson with no quiz counts as complete on open. The engine does not track scrolling, and nothing requires a quiz to exist."
    },
    {
      "stem": "A manifest entry has \"stub\": true and its lessons/<id>/ folder does not exist. What does the reader see?",
      "options": [
        "A could-not-load error naming the missing lesson.md",
        "An empty page, because the fetch for lesson.md fails",
        "A 404 page from the server",
        "The outline text from the manifest, rendered as Markdown"
      ],
      "correct_index": 3,
      "explanation": "Stubs return before any fetch. The engine renders the manifest's outline in place of lesson.md, so a stub needs no folder. That is also why a stub cannot have a quiz."
    },
    {
      "stem": "quiz.json is present but contains a trailing comma, so it is invalid JSON. What does the reader see?",
      "options": [
        "No quiz, plus a message naming the file and the parse error; the lesson text still renders",
        "No quiz and no message of any kind",
        "The whole lesson fails to load",
        "A quiz with zero questions that passes immediately"
      ],
      "correct_index": 0,
      "explanation": "The engine reports a parse failure on the page instead of swallowing it, and keeps the lesson body. A missing quiz.json is silent because that is a normal state; a present but broken one is an authoring bug worth surfacing."
    },
    {
      "stem": "A reader passes this lesson's quiz at Advanced, then switches to Beginner. What does the sidebar show for the lesson?",
      "options": [
        "Not started, because progress is tracked separately per level",
        "In progress until they also pass the Beginner quiz",
        "Done, because progress is stored per lesson, not per level",
        "Done only at Advanced; the check disappears at other levels"
      ],
      "correct_index": 2,
      "explanation": "Progress is keyed on lesson id alone. Levels change which text and quiz a reader sees, not what counts as finished, so a pass at any level completes the lesson for all of them."
    }
  ]
}
```

- [ ] **Step 6: Validate fixtures and run the failing check**

```bash
python3 - <<'PY'
import json, pathlib
root = pathlib.Path("courses/example-course")
m = json.loads((root / "manifest.json").read_text())
assert m["levels"] == ["beginner", "intermediate", "advanced"], m["levels"]
q = json.loads((root / "lessons/01-anatomy-of-a-course/quiz.advanced.json").read_text())
assert [x["correct_index"] for x in q["questions"]] == [1, 3, 0, 2]
for x in q["questions"]:
    assert 0 <= x["correct_index"] < len(x["options"]), x["stem"]
print("fixtures ok")
PY
```

Expected: `fixtures ok`.

Failing check: open `http://localhost:8137/courses/example-course/?lesson=01-anatomy-of-a-course&level=advanced` and run `!!document.getElementById('level-switcher')`. Expected now: `false` (FAIL: the engine does not know levels yet). Also confirm the page still renders normally (levels is ignored, base text shows).

- [ ] **Step 7: Commit**

```bash
git add courses/example-course
gitleaks protect --staged
git commit -m "Example course: level variants for lesson 1 (data only)" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Levels in the engine

**Files:**
- Modify: `engine/app.js`
- Modify: `engine/course.html` (switcher container)
- Modify: `engine/style.css` (note style)
- Modify: `courses/*/index.html` (re-copy)

- [ ] **Step 1: Level helpers in `engine/app.js`**

Insert immediately after `initThemeSwitcher` (before `STATUS_TEXT`):

```js
const LEVEL_RE = /^[a-z0-9-]+$/;
let level = null; // selected level slug, or null when the course declares none

function levelKey(courseSlug) {
  return `academy-of-things:${courseSlug}:level`;
}

// Keep only well-formed slugs: the level ends up in a fetched file name.
function normalizeLevels(manifest) {
  const raw = manifest.levels;
  if (raw === undefined) {
    manifest.levels = [];
    return;
  }
  manifest.levels = Array.isArray(raw) ? raw.filter((l) => typeof l === 'string' && LEVEL_RE.test(l)) : [];
  if (!Array.isArray(raw) || manifest.levels.length !== raw.length) {
    console.warn('manifest.json: ignored invalid "levels" entries (use lowercase letters, digits and hyphens)');
  }
}

// ?level= wins, then storage, then the first declared level.
// Anything the manifest does not declare is ignored.
function resolveLevel(manifest, search) {
  const levels = manifest.levels;
  if (!levels.length) return null;
  const fromUrl = new URLSearchParams(search).get('level');
  if (levels.includes(fromUrl)) {
    storageSet(levelKey(manifest.slug), fromUrl);
    return fromUrl;
  }
  const stored = storageGet(levelKey(manifest.slug));
  return levels.includes(stored) ? stored : levels[0];
}

// Try lesson.<level>.md (or quiz.<level>.json) first, then the plain file.
// `variant` says which one answered; `path` is the last path tried.
async function fetchVariant(lessonId, base, ext, lvl) {
  if (lvl) {
    const res = await fetch(`./lessons/${lessonId}/${base}.${lvl}.${ext}`);
    if (res.ok) return { res, variant: true, path: `lessons/${lessonId}/${base}.${lvl}.${ext}` };
  }
  const path = `lessons/${lessonId}/${base}.${ext}`;
  return { res: await fetch(`./${path}`), variant: false, path };
}

function initLevelSwitcher(manifest, onChange) {
  if (!manifest.levels.length) return;
  const el = document.getElementById('level-switcher');
  el.hidden = false;
  segmented(el, 'level', 'Reading level', manifest.levels, level, onChange);
}

function currentLessonId(manifest) {
  return new URLSearchParams(location.search).get('lesson') || manifest.lessons[0].id;
}

```

- [ ] **Step 2: Use the fallback fetch in `renderLesson`**

Replace the lesson-body fetch block

```js
  let md;
  try {
    const mdRes = await fetch(`./lessons/${lesson.id}/lesson.md`);
    if (!mdRes.ok) throw new Error(`HTTP ${mdRes.status}`);
    md = await mdRes.text();
  } catch (e) {
```

with

```js
  let md;
  let usedVariant = false;
  try {
    const { res: mdRes, variant } = await fetchVariant(lesson.id, 'lesson', 'md', level);
    if (!mdRes.ok) throw new Error(`HTTP ${mdRes.status}`);
    md = await mdRes.text();
    usedVariant = variant;
  } catch (e) {
```

Replace

```js
  article.innerHTML = marked.parse(md);

  let quiz = null;
  try {
    const quizRes = await fetch(`./lessons/${lesson.id}/quiz.json`);
    if (quizRes.ok) {
      try {
        quiz = await quizRes.json();
      } catch (e) {
        if (token === renderToken) showProblem(quizContainer, `lessons/${lesson.id}/quiz.json is not valid JSON (${e.message}), so this lesson has no quiz.`);
        return;
      }
    }
  } catch (e) {
```

with

```js
  article.innerHTML = marked.parse(md);
  if (level && !usedVariant) {
    const note = document.createElement('p');
    note.className = 'level-note';
    note.textContent = `No ${level} version of this lesson; showing the standard text.`;
    const h1 = article.querySelector('h1');
    if (h1) h1.after(note);
    else article.prepend(note);
  }

  let quiz = null;
  try {
    const { res: quizRes, path: quizPath } = await fetchVariant(lesson.id, 'quiz', 'json', level);
    if (quizRes.ok) {
      try {
        quiz = await quizRes.json();
      } catch (e) {
        if (token === renderToken) showProblem(quizContainer, `${quizPath} is not valid JSON (${e.message}), so this lesson has no quiz.`);
        return;
      }
    }
  } catch (e) {
```

- [ ] **Step 3: Wire `initCourse`**

Replace

```js
  const manifest = await loadManifest();
  document.getElementById('course-title').textContent = manifest.title;
  document.getElementById('course-subtitle').textContent = manifest.subtitle || '';

  const params = new URLSearchParams(location.search);
  const lessonId = params.get('lesson') || manifest.lessons[0].id;
  await renderLesson(manifest, lessonId);

  window.addEventListener('popstate', async () => {
    const p = new URLSearchParams(location.search);
    await renderLesson(manifest, p.get('lesson') || manifest.lessons[0].id);
  });
```

with

```js
  const manifest = await loadManifest();
  document.getElementById('course-title').textContent = manifest.title;
  document.getElementById('course-subtitle').textContent = manifest.subtitle || '';

  normalizeLevels(manifest);
  level = resolveLevel(manifest, location.search);
  initLevelSwitcher(manifest, async (value) => {
    level = value;
    storageSet(levelKey(manifest.slug), value);
    await renderLesson(manifest, currentLessonId(manifest));
  });

  await renderLesson(manifest, currentLessonId(manifest));

  window.addEventListener('popstate', async () => {
    await renderLesson(manifest, currentLessonId(manifest));
  });
```

- [ ] **Step 4: Switcher container and note style**

In `engine/course.html`, insert between the subtitle and the progress segments:

```html
    <div id="level-switcher" hidden></div>
```

In `engine/style.css`, add after the `article h3` rule:

```css
.level-note { margin: 0 0 20px; font-size: 13px; color: var(--muted); }
```

Run the re-copy helper. Expected: `match:` for both courses.

- [ ] **Step 5: Run the checks to see them pass**

Each check starts from `localStorage.clear()`. URL base: `http://localhost:8137/courses/example-course/`.

1. Default level. Load `?lesson=01-anatomy-of-a-course`:

```js
({
  visible: !document.getElementById('level-switcher').hidden,
  levels: [...document.querySelectorAll('#level-switcher input')].map((i) => i.value),
  checked: document.querySelector('#level-switcher input:checked').value,
  hasBeginnerText: document.getElementById('lesson-content').textContent.includes('Three kinds of file'),
  note: document.querySelector('.level-note')?.textContent ?? null,
  firstStem: document.querySelector('.quiz .stem')?.textContent
})
```

Expected: `visible: true`, `levels: ["beginner","intermediate","advanced"]`, `checked: "beginner"`, `hasBeginnerText: true`, `note: null`, `firstStem` starting `1. What has to match between manifest.json` (beginner has no quiz variant, so the plain quiz shows: independent fallback).

2. Switch to advanced:

```js
const before = history.length;
document.querySelector('#level-switcher input[value=advanced]').click();
await new Promise((r) => setTimeout(r, 600));
({
  key: localStorage.getItem('academy-of-things:example-course:level'),
  hasAdvancedText: document.getElementById('lesson-content').textContent.includes('What the engine reads'),
  note: document.querySelector('.level-note')?.textContent ?? null,
  firstStem: document.querySelector('.quiz .stem')?.textContent,
  questions: document.querySelectorAll('.question').length,
  historyAdded: history.length - before,
  url: location.search
})
```

Expected: `key: "advanced"`, `hasAdvancedText: true`, `note: null`, `firstStem` starting `1. A lesson folder contains lesson.md and no quiz.json`, `questions: 4`, `historyAdded: 0`, `url: "?lesson=01-anatomy-of-a-course"`.

3. Intermediate falls back with a note:

```js
document.querySelector('#level-switcher input[value=intermediate]').click();
await new Promise((r) => setTimeout(r, 600));
({
  note: document.querySelector('.level-note')?.textContent,
  noteAfterH1: document.querySelector('#lesson-content h1').nextElementSibling.className,
  hasLevelsSection: document.getElementById('lesson-content').textContent.includes('Levels are optional')
})
```

Expected: `note: "No intermediate version of this lesson; showing the standard text."`, `noteAfterH1: "level-note"`, `hasLevelsSection: true`.

4. Lesson 2 shows the note at every level and lesson 3 (stub) never does. For each of the three radios, click it, wait, and navigate by clicking the sidebar link `a[href="?lesson=02-writing-quizzes"]`; read `.level-note` text each time. Expected: `No beginner version of this lesson; showing the standard text.` / `No intermediate ...` / `No advanced ...`. Then click `a[href="?lesson=03-distribution"]`; expected `document.querySelector('.level-note')` is `null`.

5. Persistence and URL override. Reload `?lesson=01-anatomy-of-a-course`: the checked radio is the stored one. Load `?lesson=01-anatomy-of-a-course&level=beginner`: checked is `beginner` and the key is now `beginner`. Load `...&level=bogus` and `...&level=../../x`: the checked radio is unchanged and the key is unchanged.

6. Progress is per lesson. Set level to advanced, pass the advanced quiz (correct options 1-based: 2, 4, 1, 3), confirm the sidebar shows lesson 1 done, switch to beginner and intermediate: still done, and the label stays `1 of 2 complete`.

7. A course without levels. Open `http://localhost:8137/courses/okta-workflows/` after `localStorage.clear()`:

```js
({
  hidden: document.getElementById('level-switcher').hidden,
  note: document.querySelector('.level-note'),
  title: document.querySelector('#lesson-content h1')?.textContent,
  themeSwitcher: !!document.querySelector('#theme-switcher input')
})
```

Expected: `hidden: true`, `note: null`, a lesson title, `themeSwitcher: true`. Click through every okta lesson and take at least one quiz; behaviour is as before.

8. Console: `read_console_messages` with `onlyErrors: true` on both courses. Expected: no errors (the 404s for missing `lesson.<level>.md` / `quiz.<level>.json` are network entries, not console errors, and are expected).

Take screenshots of the example course at each level in light and dark.

- [ ] **Step 6: Literal check and commit**

Re-run the Task 1 Step 8 check (expect both `clean:` lines), then:

```bash
git add engine/app.js engine/course.html engine/style.css courses/example-course/index.html courses/okta-workflows/index.html
gitleaks protect --staged
git commit -m "Engine: course levels with per-lesson variants and fallback" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 6: `new-course.sh --levels`

**Files:**
- Modify: `scripts/new-course.sh`

- [ ] **Step 1: Write the failing check**

```bash
./scripts/new-course.sh --levels tmp-levels "Tmp" "Sub"; echo "exit=$?"
```

Expected now: an error such as `error: ...` or a course named `--levels` created (FAIL). If a stray `courses/--levels` directory appears, remove it with `rm -rf -- courses/--levels` (it is your own mistake output) and continue.

- [ ] **Step 2: Replace the argument parsing**

Replace

```bash
if [ $# -lt 2 ]; then
  echo "usage: $0 <slug> \"<Title>\" [\"<Subtitle>\"]" >&2
  exit 1
fi

SLUG="$1"; TITLE="$2"; SUBTITLE="${3:-}"
```

with

```bash
LEVELS=0; ARGS=()
for a in "$@"; do
  if [ "$a" = "--levels" ]; then LEVELS=1; else ARGS+=("$a"); fi
done
set -- ${ARGS[@]+"${ARGS[@]}"}

if [ $# -lt 2 ]; then
  echo "usage: $0 [--levels] <slug> \"<Title>\" [\"<Subtitle>\"]" >&2
  exit 1
fi

SLUG="$1"; TITLE="$2"; SUBTITLE="${3:-}"
LEVELS_JSON=""
if [ "$LEVELS" = 1 ]; then
  LEVELS_JSON=$'\n  "levels": ["beginner", "intermediate", "advanced"],'
fi
```

Also update the header comment: replace `#   ./scripts/new-course.sh <slug> "<Title>" "<Subtitle>"` with

```bash
#   ./scripts/new-course.sh [--levels] <slug> "<Title>" "<Subtitle>"
# --levels adds beginner/intermediate/advanced levels. lesson.md is the
# fallback and the intermediate text; edit the lesson.beginner.md and
# lesson.advanced.md it creates, or delete them to show lesson.md there.
```

- [ ] **Step 3: Use the variable in the manifest and write the variants**

In the manifest heredoc, replace the line

```
  "subtitle": "$SUBTITLE",
```

with

```
  "subtitle": "$SUBTITLE",$LEVELS_JSON
```

After the `lesson.md` heredoc (the block ending with a line `MD`), add:

```bash
if [ "$LEVELS" = 1 ]; then
  for lv in beginner advanced; do
    cat > "$DEST/lessons/01-first-lesson/lesson.$lv.md" <<MD
# First Lesson

Replace this with the $lv version. Keep the same facts as lesson.md and change
the depth. Delete this file to show lesson.md at the $lv level instead.
MD
  done
fi
```

At the end, after the final `echo "Run: ..."` line, add:

```bash
if [ "$LEVELS" = 1 ]; then
  echo "Levels: lesson.md is the fallback and the intermediate text."
fi
```

- [ ] **Step 4: Run the checks to see them pass**

```bash
./scripts/new-course.sh --levels tmp-levels "Tmp" "Sub" && ./scripts/new-course.sh tmp-plain "Tmp"
python3 - <<'PY'
import json
a = json.load(open("courses/tmp-levels/manifest.json"))
b = json.load(open("courses/tmp-plain/manifest.json"))
assert a["levels"] == ["beginner", "intermediate", "advanced"], a
assert "levels" not in b, b
print("manifests ok")
PY
ls courses/tmp-levels/lessons/01-first-lesson courses/tmp-plain/lessons/01-first-lesson
diff -q engine/course.html courses/tmp-levels/index.html && diff -q engine/course.html courses/tmp-plain/index.html && echo "index.html matches"
```

Expected: `manifests ok`; `tmp-levels` lists `lesson.advanced.md lesson.beginner.md lesson.md quiz.json`; `tmp-plain` lists `lesson.md quiz.json`; `index.html matches`. In the browser, open `http://localhost:8137/courses/tmp-levels/`: the switcher shows, switching to Beginner shows the beginner placeholder text and to Intermediate shows the note. Open `courses/tmp-plain/`: no switcher.

- [ ] **Step 5: Remove the two throwaway courses (created in this task, never committed) and commit**

```bash
rm -rf courses/tmp-levels courses/tmp-plain
git status --short
git add scripts/new-course.sh
gitleaks protect --staged
git commit -m "Scaffold: new-course.sh --levels" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

Expected `git status --short` before the add: only `M scripts/new-course.sh`.

---

### Task 7: Documentation (FORMAT.md and the builder skill)

`AUTHORING.md` is outside the approved scope; it is left alone and flagged in the final report.

**Files:**
- Modify: `FORMAT.md`
- Modify: `skills/academy-of-things-course-builder/SKILL.md`

- [ ] **Step 1: FORMAT.md — layout, manifest, levels, state**

In the layout tree, replace

```
    01-first-lesson/
      lesson.md               the lesson body (Markdown)
      quiz.json               optional
```

with

```
    01-first-lesson/
      lesson.md               the lesson body (Markdown)
      quiz.json               optional
      lesson.beginner.md      optional, one per level (see Levels)
      quiz.advanced.json      optional, one per level
```

In the manifest field table, add a row after the `subtitle` row:

```
| `levels` | no | Array of level slugs (lowercase letters, digits, hyphens), in display order. The first is the default. Adds a level switcher. Omit it and the course has no levels. See [Levels](#levels). |
```

Add this section before `## State`:

````markdown
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

When the lesson body fell back to `lesson.md`, the engine shows one line under
the title: "No <level> version of this lesson; showing the standard text." A
lesson that only ever has `lesson.md` reads that way at every level, which is
fine and honest. Do not copy the same text into every level file.

Progress is per lesson, not per level: passing a lesson's quiz at any level
marks it complete everywhere. Switching level re-renders the open lesson and
discards any quiz answers not yet checked.

A missing level file is detected from a non-OK response, so the server has to
return a real 404 for it (`serve.py` does). A host that answers every unknown
path with 200 and an HTML page will break the fallback.
````

In `## State`, replace the opening paragraph

```
Progress lives in the browser's `localStorage` under
`academy-of-things:<slug>:progress`. Nothing is sent anywhere, there is no
account, and clearing site data resets it. Two people using the same course
on the same machine share the same progress.
```

with

```
Everything lives in the browser's `localStorage`. Nothing is sent anywhere,
there is no account, and clearing site data resets it. Two people using the
same course on the same machine share the same state.

| Key | Holds |
| --- | --- |
| `academy-of-things:<slug>:progress` | Completed lessons for one course. |
| `academy-of-things:<slug>:level` | The selected level for one course. Also settable once with `?level=<level>`; values the manifest does not declare are ignored. |
| `academy-of-things:theme` | `light` or `dark`. Absent means follow the system. One key for every course. |
```

In `## Constraints worth knowing`, add a bullet:

```
- **Modern browser.** Colors use `light-dark()`, `color-mix()` and `:has()`
  (Baseline 2024 and later). Older browsers are not supported.
```

- [ ] **Step 2: SKILL.md — teach levels**

In `skills/academy-of-things-course-builder/SKILL.md`, under `## Before building anything`, add a step after step 1:

```
   Also decide whether the course needs levels. Add them only when the audience genuinely spans levels and you can write the lessons at more than one depth. A single-level course is simpler and often better. If levels are wanted, scaffold with `--levels` and write `lesson.md` as the standard (intermediate) text.
```

In `## File layout`, after the scaffold command block, add:

````
With levels:

```bash
./scripts/new-course.sh --levels <slug> "<Title>" "<Subtitle>"
```

That adds `"levels": ["beginner", "intermediate", "advanced"]` to the manifest and creates `lesson.beginner.md` and `lesson.advanced.md` placeholders beside `lesson.md`.
````

After the `### manifest.json` field bullets, add:

```
- `levels` (optional) is an array of level slugs, lowercase letters, digits and hyphens. The first is the default. Leave it out for a single-level course.
```

After the `### lessons/<id>/quiz.json` bullets, add a new subsection:

```
### Level variants

- `lesson.<level>.md` and `quiz.<level>.json` replace `lesson.md` and `quiz.json` at that level. A missing variant falls back to the plain file, independently for text and quiz.
- Same facts, different depth. A beginner version defines terms and slows down; an advanced version covers mechanism and failure modes. Never let a level file contradict `lesson.md`.
- Do not copy `lesson.md` into every level file. A lesson with only `lesson.md` is valid; the reader sees a one-line note that no version exists for their level.
- Progress is per lesson. Passing at any level completes the lesson, so keep pass thresholds comparable across a lesson's quizzes.
- Stubs ignore levels.
```

In `## Build order`, step 5, add after the first sentence's list item sub-bullets:

```
   - With levels, switch through every level on every lesson and take each quiz variant. Confirm the "No <level> version" note appears only where a variant is genuinely absent.
```

- [ ] **Step 3: Check the docs against the engine**

```bash
grep -n "levels" FORMAT.md | head -20
grep -n "levels" skills/academy-of-things-course-builder/SKILL.md | head -20
ls -la .claude/skills/
```

Expected: both greps list the new text; `.claude/skills/` contains only symlinks (no regular files). Reread the new FORMAT.md Levels section once against `engine/app.js` (`fetchVariant`, `resolveLevel`, the note text) and fix any mismatch.

- [ ] **Step 4: Commit**

```bash
git add FORMAT.md skills/academy-of-things-course-builder/SKILL.md
gitleaks protect --staged
git commit -m "Docs: document levels, theme and state keys in FORMAT.md and the builder skill" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 8: Packaged zips still work

`scripts/package-course.sh` rewrites `../../engine/` and deletes the line containing `class="home"`. The new head script and containers must survive that.

**Files:**
- Modify only if broken: `scripts/package-course.sh`

- [ ] **Step 1: Package and inspect**

```bash
./scripts/package-course.sh example-course
rm -rf "$TMPDIR/pkg-check" 2>/dev/null; mkdir -p "$TMPDIR/pkg-check"
unzip -q dist/example-course.zip -d "$TMPDIR/pkg-check"
grep -c '\.\./\.\./engine/' "$TMPDIR/pkg-check/example-course/index.html" || true
grep -c 'class="home"' "$TMPDIR/pkg-check/example-course/index.html" || true
grep -c 'academy-of-things:theme' "$TMPDIR/pkg-check/example-course/index.html"
grep -c 'id="level-switcher"' "$TMPDIR/pkg-check/example-course/index.html"
ls "$TMPDIR/pkg-check/example-course"
git check-ignore dist && echo "dist ignored" || echo "dist NOT ignored"
```

Expected: `0`, `0`, `1`, `1`; the listing includes `index.html app.js style.css manifest.json lessons serve.py README.md`; `dist ignored`. If `dist NOT ignored`, do not commit `dist/`; delete `dist/example-course.zip` after the check.

- [ ] **Step 2: Run the standalone copy**

Start `cd "$TMPDIR/pkg-check/example-course" && python3 serve.py 8138` with `Bash` `run_in_background` (own server, own port). Open `http://localhost:8138/` and run the Task 5 checks 1 to 3 and the Task 1 theme check. Expected: identical results (switcher present, levels work, theme control works). Stop that server with `TaskStop`.

- [ ] **Step 3: Commit only if something needed fixing**

If the script needed a change, fix it, re-run Step 1 and 2, and commit:

```bash
git add scripts/package-course.sh
gitleaks protect --staged
git commit -m "Packaging: keep levels and theme working in standalone zips" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

If nothing was broken, no commit; note "package-course.sh needed no change" in the final report. Clean up: `rm -rf "$TMPDIR/pkg-check" dist/example-course.zip` (own artifacts).

---

### Task 9: Full verification pass (done means served)

Run on the committed state. Nothing here should require a code change; if it does, fix it in a new commit and rerun the affected checks.

- [ ] **Step 1: Mechanical checks**

```bash
for c in courses/*/; do diff -q engine/course.html "${c}index.html" && echo "match: $c"; done
awk '/^:root \{/{t=1} t&&/^\}/{t=0; next} !t' engine/style.css | grep -nE '#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(|(^|[^-a-z])(white|black|red|green|blue|gray|grey)([^-a-z]|$)' || echo "clean: no literals outside token block"
grep -nE '#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(' engine/app.js engine/course.html || echo "clean: none in app.js or course.html"
ls -la .claude/skills/ && git status --short
```

Expected: `match:` for each course, both `clean:` lines, only symlinks under `.claude/skills/`, empty `git status`.

- [ ] **Step 2: example-course, desktop, light and dark**

With the server on 8137 and `localStorage.clear()`:

1. Every level (beginner, intermediate, advanced) on every lesson (1, 2, 3 stub): the right text, the note only where a variant is absent, nothing on the stub.
2. Take every quiz: lesson 1 at beginner (plain quiz), intermediate (plain quiz), advanced (advanced quiz); lesson 2. For each, run a fail path (wrong answers, `Try again` resets) and a pass path.
3. Answer-key check per the skill: for each question, click the option whose text you meant to be right and confirm the engine scores it correct.
4. Reload with each of `?level=advanced`, `?level=beginner`, `?level=bogus`. Confirm persistence and the ignore rule.
5. Theme: System, Light, Dark; reload on each (no flash: `document.documentElement.dataset.theme` is already set at `DOMContentLoaded`); confirm both courses share the key; with System selected, emulate OS dark and light via `resize_window` `colorScheme` and confirm the page follows.

- [ ] **Step 3: okta-workflows**

No switcher, themed, all seven lessons open, take two quizzes including a pass. Confirm its `manifest.json` and lessons are unchanged: `git diff main --stat -- courses/okta-workflows` shows only `index.html`.

- [ ] **Step 4: Mobile and landing page**

`resize_window` preset `mobile` (375px): reload `example-course`, check the sidebar stacks above the lesson, the three-segment level control fits without clipping `Intermediate`, the theme control is reachable, the quiz is usable, and there is no horizontal page scroll (`document.documentElement.scrollWidth <= window.innerWidth`). Reset with preset `desktop`.

Open `http://localhost:8137/` (the `serve.py` landing page loads `engine/style.css`). Confirm it is legible in light and dark. It is out of scope to restyle; if it is unreadable, report it rather than patching `serve.py`.

- [ ] **Step 5: Clean up and report**

In the page: `localStorage.clear()`. Stop the 8137 server with `TaskStop`. Then:

```bash
git status --short
git log --oneline main..HEAD
```

Expected: empty status; the commit list matches Tasks 0 to 8. Final report to Ben: what changed in `engine/` (file by file), the three deviations from the spec (note wording, no note slot, `segmented` label), that `AUTHORING.md` was not touched and what to add, that the `serve.py` landing page now follows the system theme, and the browser-support note. Offer `superpowers:finishing-a-development-branch`.

---

## Self-review

**Spec coverage.** Format (`levels`, variants, independent fallback, note, per-lesson progress): Tasks 4, 5. Level state (`?level=`, storage, default, ignore invalid, in-place re-render, storage failure): Task 5 (`resolveLevel`, `storageGet/Set`, module-level `level`). Theme (universal key, `data-theme`, head script, control): Task 1. No hardcoded colors (tokens, `light-dark()`, grep): Task 1 and re-run in Tasks 2, 3, 5, 9. UI (segmented helper, switcher, progress segments, status icons, quiz states, mobile): Tasks 1, 2, 3, 5, 9. Engine edits and re-copy: Tasks 1, 2, 5, 9. Other deliverables (example-course, FORMAT.md, new-course.sh, skill, package check): Tasks 4, 7, 6, 7, 8. Verification list: Task 9. The three spec amendments are Task 0.

**Placeholders.** None: every code step carries the code; every check names its expected value.

**Consistency.** `segmented(container, name, label, options, value, onChange)` is defined in Task 1 and used with that signature in Tasks 1 and 5. `storageGet`/`storageSet` (Task 1) are used in Task 5. `fetchVariant` returns `{ res, variant, path }` and both call sites destructure those names. `level` is the single module variable read by `renderLesson`. CSS class names (`status`, `is-*`, `progress-segments`, `level-note`, `sidebar-foot`, `sr-only`, `segmented`) match between `app.js`, `course.html` and `style.css`. Element ids (`theme-switcher`, `level-switcher`, `progress-segments`, `progress-label`) match across files. `STATUS_TEXT` keys match the `state` values.
