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

function renderSidebar(manifest, currentLessonId, progress) {
  const list = document.getElementById('lesson-list');
  list.innerHTML = '';
  manifest.lessons.forEach((lesson) => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = `?lesson=${lesson.id}`;
    const label = document.createElement('span');
    label.textContent = lesson.title;
    a.appendChild(label);
    if (lesson.id === currentLessonId) {
      a.classList.add('active');
      a.setAttribute('aria-current', 'page');
    }
    if (lesson.stub) a.classList.add('locked');

    const badge = document.createElement('span');
    badge.classList.add('badge');
    if (lesson.stub) {
      badge.classList.add('stub');
      badge.textContent = 'coming next';
    } else if (progress[lesson.id] && progress[lesson.id].completed) {
      badge.classList.add('done');
      badge.textContent = 'done';
    } else {
      badge.textContent = 'start';
    }
    a.appendChild(badge);
    li.appendChild(a);
    list.appendChild(li);
  });

  const done = manifest.lessons.filter((l) => !l.stub && progress[l.id] && progress[l.id].completed).length;
  const total = manifest.lessons.filter((l) => !l.stub).length;
  const pct = total ? Math.round((done / total) * 100) : 0;
  document.getElementById('progress-fill').style.width = pct + '%';
  document.getElementById('progress-label').textContent = `${done}/${total} lessons complete (${pct}%)`;
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
  try {
    const mdRes = await fetch(`./lessons/${lesson.id}/lesson.md`);
    if (!mdRes.ok) throw new Error(`HTTP ${mdRes.status}`);
    md = await mdRes.text();
  } catch (e) {
    if (token !== renderToken) return;
    article.innerHTML = `<h1>${esc(lesson.title)}</h1>`;
    showProblem(article, `Could not load lessons/${lesson.id}/lesson.md (${e.message}). Check that the folder name matches the id in manifest.json.`);
    return;
  }
  if (token !== renderToken) return;
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
