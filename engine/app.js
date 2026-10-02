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
  localStorage.setItem(progressKey(courseSlug), JSON.stringify(progress));
}

function markComplete(courseSlug, lessonId) {
  const progress = loadProgress(courseSlug);
  progress[lessonId] = { completed: true, completedAt: new Date().toISOString() };
  saveProgress(courseSlug, progress);
}

function renderSidebar(manifest, currentLessonId, progress) {
  const list = document.getElementById('lesson-list');
  list.innerHTML = '';
  manifest.lessons.forEach((lesson) => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = `?lesson=${lesson.id}`;
    a.textContent = lesson.title;
    if (lesson.id === currentLessonId) a.classList.add('active');
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
  wrap.innerHTML = `<h2>Check your understanding</h2><p style="color:var(--muted)">${quiz.passing_note || 'Answer every question, then check your results.'}</p>`;

  const answers = {};

  quiz.questions.forEach((q, qi) => {
    const qDiv = document.createElement('div');
    qDiv.className = 'question';
    qDiv.innerHTML = `<p class="stem">${qi + 1}. ${q.stem}</p>`;
    const optsDiv = document.createElement('div');
    optsDiv.className = 'options';

    q.options.forEach((opt, oi) => {
      const optDiv = document.createElement('div');
      optDiv.className = 'option';
      optDiv.textContent = opt;
      optDiv.dataset.index = oi;
      optDiv.addEventListener('click', () => {
        optsDiv.querySelectorAll('.option').forEach((o) => o.classList.remove('selected'));
        optDiv.classList.add('selected');
        answers[qi] = oi;
      });
      optsDiv.appendChild(optDiv);
    });

    qDiv.appendChild(optsDiv);

    const expl = document.createElement('div');
    expl.className = 'explanation';
    expl.textContent = q.explanation || '';
    qDiv.appendChild(expl);

    wrap.appendChild(qDiv);
  });

  const checkBtn = document.createElement('button');
  checkBtn.className = 'primary';
  checkBtn.textContent = 'Check answers';
  wrap.appendChild(checkBtn);

  const resultDiv = document.createElement('div');
  wrap.appendChild(resultDiv);

  checkBtn.addEventListener('click', () => {
    let correct = 0;
    const questionDivs = wrap.querySelectorAll('.question');
    quiz.questions.forEach((q, qi) => {
      const qDiv = questionDivs[qi];
      const opts = qDiv.querySelectorAll('.option');
      opts.forEach((o, oi) => {
        o.classList.remove('correct', 'incorrect');
        if (oi === q.correct_index) o.classList.add('correct');
        else if (answers[qi] === oi) o.classList.add('incorrect');
      });
      qDiv.querySelector('.explanation').classList.add('show');
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
      : `${correct}/${total} correct (${pct}%) — below the ${passThreshold}% bar. Review the explanations above and try again.`;
    resultDiv.appendChild(result);

    if (passed && onPass) onPass();
  });

  container.appendChild(wrap);
}

async function renderLesson(manifest, lessonId) {
  const lesson = manifest.lessons.find((l) => l.id === lessonId) || manifest.lessons[0];
  const progress = loadProgress(manifest.slug);
  renderSidebar(manifest, lesson.id, progress);

  document.title = `${lesson.title} — ${manifest.title}`;
  const article = document.getElementById('lesson-content');

  if (lesson.stub) {
    article.innerHTML = `<h1>${lesson.title}</h1><blockquote>Not written yet — outline only. This section is planned next; see the repo README for the current build status.</blockquote>${lesson.outline ? marked.parse(lesson.outline) : ''}`;
    document.getElementById('quiz-container').innerHTML = '';
    return;
  }

  const mdRes = await fetch(`./lessons/${lesson.id}/lesson.md`);
  const md = await mdRes.text();
  article.innerHTML = marked.parse(md);

  const quizContainer = document.getElementById('quiz-container');
  quizContainer.innerHTML = '';
  try {
    const quizRes = await fetch(`./lessons/${lesson.id}/quiz.json`);
    if (quizRes.ok) {
      const quiz = await quizRes.json();
      renderQuiz(quizContainer, quiz, () => {
        markComplete(manifest.slug, lesson.id);
        renderSidebar(manifest, lesson.id, loadProgress(manifest.slug));
      });
    }
  } catch (e) {
    // no quiz for this lesson — fine, some lessons are reading-only
  }

  const idx = manifest.lessons.findIndex((l) => l.id === lesson.id);
  const prev = manifest.lessons[idx - 1];
  const next = manifest.lessons[idx + 1];
  const nav = document.getElementById('lesson-nav');
  nav.innerHTML = `
    <a href="${prev ? '?lesson=' + prev.id : '#'}" style="visibility:${prev ? 'visible' : 'hidden'}">&larr; ${prev ? prev.title : ''}</a>
    <a href="${next ? '?lesson=' + next.id : '#'}" style="visibility:${next ? 'visible' : 'hidden'}">${next ? next.title : ''} &rarr;</a>
  `;
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

  document.getElementById('lesson-list').addEventListener('click', async (e) => {
    const a = e.target.closest('a');
    if (!a) return;
    e.preventDefault();
    const url = new URL(a.href);
    history.pushState({}, '', url);
    await renderLesson(manifest, url.searchParams.get('lesson'));
    window.scrollTo(0, 0);
  });

  document.getElementById('lesson-nav').addEventListener('click', async (e) => {
    const a = e.target.closest('a');
    if (!a || a.getAttribute('href') === '#') return;
    e.preventDefault();
    const url = new URL(a.href);
    history.pushState({}, '', url);
    await renderLesson(manifest, url.searchParams.get('lesson'));
    window.scrollTo(0, 0);
  });
}

initCourse();
