/*
 * Tiny static course engine. No build step, no backend, no external binaries.
 * Only external dependency: marked.js (Markdown rendering), loaded from cdnjs.
 * Progress is stored client-side in localStorage, scoped per course slug.
 */

async function loadManifest() {
  const res = await fetch('./manifest.json');
  return res.json();
}

function progressKey(courseSlug) {
  return `academy-of-things:${courseSlug}:progress`;
}

function loadProgress(courseSlug) {
  try {
    return JSON.parse(localStorage.getItem(progressKey(courseSlug))) || {};
  } catch (e) {
    return {};
  }
}

function saveProgress(courseSlug, progress) {
  try {
    localStorage.setItem(progressKey(courseSlug), JSON.stringify(progress));
  } catch (e) {
    // storage blocked (private mode, quota): progress just won't persist
  }
}

function markComplete(courseSlug, lessonId) {
  const progress = loadProgress(courseSlug);
  if (progress[lessonId] && progress[lessonId].completed) return;
  progress[lessonId] = { completed: true, completedAt: new Date().toISOString() };
  saveProgress(courseSlug, progress);
}

// Author-supplied text (titles, stems, notes) is plain text, never HTML.
function esc(s) {
  const d = document.createElement('div');
  d.textContent = s == null ? '' : String(s);
  return d.innerHTML;
}

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
    // precedence: stub, then done, then current (open and unfinished), then todo
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

function renderQuiz(container, quiz, onPass) {
  if (!quiz || !quiz.questions || !quiz.questions.length) return;

  const wrap = document.createElement('div');
  wrap.className = 'quiz';
  const heading = document.createElement('h2');
  heading.textContent = 'Check your understanding';
  const note = document.createElement('p');
  note.className = 'passing-note';
  note.textContent = quiz.passing_note || 'Answer every question, then check your results.';
  wrap.append(heading, note);

  const answers = {};
  const groupName = 'q' + Math.random().toString(36).slice(2, 8);
  const qDivs = [];

  quiz.questions.forEach((q, qi) => {
    const qDiv = document.createElement('div');
    qDiv.className = 'question';
    qDiv.setAttribute('role', 'group');
    qDiv.setAttribute('aria-labelledby', `${groupName}-stem-${qi}`);
    const stem = document.createElement('p');
    stem.className = 'stem';
    stem.id = `${groupName}-stem-${qi}`;
    stem.textContent = `${qi + 1}. ${q.stem}`;
    qDiv.appendChild(stem);

    const optsDiv = document.createElement('div');
    optsDiv.className = 'options';
    q.options.forEach((opt, oi) => {
      const label = document.createElement('label');
      label.className = 'option';
      const input = document.createElement('input');
      input.type = 'radio';
      input.name = `${groupName}-${qi}`;
      input.addEventListener('change', () => {
        answers[qi] = oi;
        qDiv.classList.remove('unanswered');
      });
      const text = document.createElement('span');
      text.className = 'option-text';
      text.textContent = opt;
      const mark = document.createElement('span');
      mark.className = 'mark';
      mark.setAttribute('aria-hidden', 'true');
      label.append(input, text, mark);
      optsDiv.appendChild(label);
    });
    qDiv.appendChild(optsDiv);

    const expl = document.createElement('div');
    expl.className = 'explanation';
    expl.textContent = q.explanation || '';
    qDiv.appendChild(expl);

    qDivs.push(qDiv);
    wrap.appendChild(qDiv);
  });

  const checkBtn = document.createElement('button');
  checkBtn.className = 'primary';
  checkBtn.type = 'button';
  checkBtn.textContent = 'Check answers';
  const retryBtn = document.createElement('button');
  retryBtn.className = 'secondary';
  retryBtn.type = 'button';
  retryBtn.textContent = 'Try again';
  retryBtn.hidden = true;
  wrap.append(checkBtn, retryBtn);

  const resultDiv = document.createElement('div');
  resultDiv.setAttribute('role', 'status');
  wrap.appendChild(resultDiv);

  function setLocked(locked) {
    wrap.querySelectorAll('input').forEach((i) => { i.disabled = locked; });
  }

  checkBtn.addEventListener('click', () => {
    const missing = quiz.questions.map((_, qi) => qi).filter((qi) => answers[qi] === undefined);
    if (missing.length) {
      qDivs.forEach((d, qi) => d.classList.toggle('unanswered', missing.includes(qi)));
      resultDiv.innerHTML = '';
      const warn = document.createElement('div');
      warn.className = 'quiz-result fail';
      warn.textContent = `Answer every question first — ${missing.length} still blank.`;
      resultDiv.appendChild(warn);
      qDivs[missing[0]].scrollIntoView({ block: 'center' });
      return;
    }

    let correct = 0;
    quiz.questions.forEach((q, qi) => {
      const opts = qDivs[qi].querySelectorAll('.option');
      opts.forEach((o, oi) => {
        o.classList.remove('correct', 'incorrect');
        const mark = o.querySelector('.mark');
        mark.textContent = '';
        if (oi === q.correct_index) {
          o.classList.add('correct');
          mark.textContent = '✓ correct';
        } else if (answers[qi] === oi) {
          o.classList.add('incorrect');
          mark.textContent = '✗ your answer';
        }
      });
      qDivs[qi].querySelector('.explanation').classList.add('show');
      if (answers[qi] === q.correct_index) correct++;
    });

    const total = quiz.questions.length;
    const pct = Math.round((correct / total) * 100);
    const passThreshold = quiz.pass_threshold_pct || 80;
    const passed = pct >= passThreshold;

    resultDiv.innerHTML = '';
    const result = document.createElement('div');
    result.className = 'quiz-result ' + (passed ? 'pass' : 'fail');
    result.textContent = passed
      ? `Passed: ${correct}/${total} correct (${pct}%). Lesson marked complete.`
      : `${correct}/${total} correct (${pct}%) — below the ${passThreshold}% bar. Read the explanations, then try again.`;
    resultDiv.appendChild(result);

    setLocked(true);
    checkBtn.hidden = true;
    if (passed) {
      if (onPass) onPass();
    } else {
      retryBtn.hidden = false;
      retryBtn.focus();
    }
  });

  retryBtn.addEventListener('click', () => {
    Object.keys(answers).forEach((k) => delete answers[k]);
    wrap.querySelectorAll('input').forEach((i) => { i.checked = false; });
    wrap.querySelectorAll('.option').forEach((o) => {
      o.classList.remove('correct', 'incorrect');
      o.querySelector('.mark').textContent = '';
    });
    wrap.querySelectorAll('.explanation').forEach((e) => e.classList.remove('show'));
    resultDiv.innerHTML = '';
    setLocked(false);
    retryBtn.hidden = true;
    checkBtn.hidden = false;
    qDivs[0].scrollIntoView({ block: 'start' });
  });

  container.appendChild(wrap);
}

function showProblem(el, message) {
  const p = document.createElement('div');
  p.className = 'quiz-result fail';
  p.textContent = message;
  el.appendChild(p);
}

let renderToken = 0;

async function renderLesson(manifest, lessonId) {
  const token = ++renderToken; // a slower earlier render must not overwrite a newer one
  const lesson = manifest.lessons.find((l) => l.id === lessonId) || manifest.lessons[0];
  const progress = loadProgress(manifest.slug);
  renderSidebar(manifest, lesson.id, progress);

  document.title = `${lesson.title} — ${manifest.title}`;
  const article = document.getElementById('lesson-content');
  const quizContainer = document.getElementById('quiz-container');
  quizContainer.innerHTML = '';

  renderNav(manifest, lesson);

  if (lesson.stub) {
    article.innerHTML = `<h1>${esc(lesson.title)}</h1><blockquote>Not written yet — outline only. This section is planned next; see the repo README for the current build status.</blockquote>${lesson.outline ? marked.parse(lesson.outline) : ''}`;
    return;
  }

  let md;
  let usedVariant = false;
  try {
    const { res: mdRes, variant } = await fetchVariant(lesson.id, 'lesson', 'md', level);
    if (!mdRes.ok) throw new Error(`HTTP ${mdRes.status}`);
    md = await mdRes.text();
    usedVariant = variant;
  } catch (e) {
    if (token !== renderToken) return;
    article.innerHTML = `<h1>${esc(lesson.title)}</h1>`;
    showProblem(article, `Could not load lessons/${lesson.id}/lesson.md (${e.message}). Check that the folder name matches the id in manifest.json.`);
    return;
  }
  if (token !== renderToken) return;
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
    // network failure on an optional file: treat as no quiz
  }
  if (token !== renderToken) return;

  if (quiz && quiz.questions && quiz.questions.length) {
    renderQuiz(quizContainer, quiz, () => {
      markComplete(manifest.slug, lesson.id);
      renderSidebar(manifest, lesson.id, loadProgress(manifest.slug));
    });
  } else {
    // reading-only lesson: opening it counts as completing it (see FORMAT.md)
    markComplete(manifest.slug, lesson.id);
    renderSidebar(manifest, lesson.id, loadProgress(manifest.slug));
  }
}

function renderNav(manifest, lesson) {
  const idx = manifest.lessons.findIndex((l) => l.id === lesson.id);
  const prev = manifest.lessons[idx - 1];
  const next = manifest.lessons[idx + 1];
  const nav = document.getElementById('lesson-nav');
  nav.innerHTML = '';
  [[prev, '← ', ''], [next, '', ' →']].forEach(([target, before, after]) => {
    const a = document.createElement('a');
    if (target) {
      a.href = `?lesson=${target.id}`;
      a.textContent = before + target.title + after;
    } else {
      a.hidden = true;
    }
    nav.appendChild(a);
  });
}

async function initCourse() {
  initThemeSwitcher();
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

  async function go(e) {
    const a = e.target.closest('a');
    if (!a || a.hidden) return;
    e.preventDefault();
    const url = new URL(a.href);
    history.pushState({}, '', url);
    await renderLesson(manifest, url.searchParams.get('lesson'));
    window.scrollTo(0, 0);
  }
  document.getElementById('lesson-list').addEventListener('click', go);
  document.getElementById('lesson-nav').addEventListener('click', go);
}

initCourse();
