# Anatomy of a Course

You are reading a lesson, served by the engine, from a folder that looks
exactly like the one you will create. Open `courses/example-course/` beside
this page and the whole format should be obvious in about a minute.

## The folder

```
courses/example-course/
  index.html          copied verbatim from engine/course.html — never edited
  manifest.json       the table of contents
  lessons/
    01-anatomy-of-a-course/
      lesson.md       this file
      quiz.json       the questions below
```

There is no build step and no registry. The engine reads `manifest.json`,
then fetches `lessons/<id>/lesson.md` for whichever lesson you clicked. Add a
folder and an entry in the manifest and it appears in the sidebar.

<!-- diagram:course-folder -->
<div class="l01a-wrap" style="position:relative">
<input type="checkbox" id="l01a-pause" class="l01a-cb" /><label for="l01a-pause" class="l01a-btn"><span class="l01a-off">Pause animation</span><span class="l01a-on">Play animation</span></label>
<div class="l01a-box" style="overflow-x:auto">
<svg class="l01a-flow" viewBox="0 0 760 480" role="img" aria-labelledby="l01a-t l01a-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l01a-t">What the engine fetches for one lesson</title>
<desc id="l01a-d">The browser loads index.html, which loads engine/app.js. The engine then fetches manifest.json, the lesson's lesson.md, and its quiz.json from the course folder. A 404 on quiz.json means the lesson has no quiz. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l01a-flow{--ink:light-dark(#000000,#ffffff)}
.l01a-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l01a-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l01a-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01a-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01a-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l01a-front{stroke:var(--accent);stroke-width:2;fill:none}
.l01a-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l01a-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l01a-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01a-badt{fill:var(--ink)}
.l01a-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01a-badge{fill:var(--accent)}
.l01a-b-back{fill:var(--muted)}
.l01a-b-bad{fill:var(--bad)}
.l01a-b-good{fill:var(--good)}
.l01a-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01a-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l01a-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l01a-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l01a-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01a-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
.l01a-pk.l01a-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l01a-pk.l01a-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l01a-wrap{margin:20px 0}
@media (min-width:801px){.l01a-wrap{margin-left:-44px;margin-right:-44px}}
.l01a-g rect,.l01a-g line,.l01a-g path:not(.l01a-gl){opacity:.5;animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l01a-flow:hover .l01a-g rect,svg.l01a-flow:hover .l01a-g line,svg.l01a-flow:hover .l01a-g path:not(.l01a-gl),svg.l01a-flow:hover .l01a-pk{animation-play-state:paused}
.l01a-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l01a-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l01a-btn:hover{background:var(--hover)}
.l01a-cb:focus-visible + .l01a-btn{outline:2px solid var(--accent);outline-offset:2px}
.l01a-cb:checked + .l01a-btn .l01a-off,.l01a-cb:not(:checked) + .l01a-btn .l01a-on{display:none}
.l01a-cb:checked ~ .l01a-box .l01a-g rect,.l01a-cb:checked ~ .l01a-box .l01a-g line,.l01a-cb:checked ~ .l01a-box .l01a-g path:not(.l01a-gl),.l01a-cb:checked ~ .l01a-box .l01a-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l01a-g rect,.l01a-g line,.l01a-g path:not(.l01a-gl){animation:none;opacity:1}.l01a-pk{animation:none;display:none}.l01a-btn{display:none}}
@keyframes l01a-g0{0%{opacity:1}21.429%{opacity:1}21.439%,100%{opacity:.5}}
@keyframes l01a-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}17.143%{opacity:1;transform:translateX(236px)}21.429%{opacity:1;transform:translateX(236px)}21.439%,100%{opacity:0;transform:translateX(236px)}}
.l01a-g0 rect,.l01a-g0 line,.l01a-g0 path:not(.l01a-gl){animation-name:l01a-g0}.l01a-p0{animation-name:l01a-p0}
@keyframes l01a-g1{0%,21.419%{opacity:.5}21.429%{opacity:1}42.857%{opacity:1}42.867%,100%{opacity:.5}}
@keyframes l01a-p1{0%,21.419%{opacity:0;transform:translateX(0)}21.429%{opacity:1;transform:translateX(0)}38.571%{opacity:1;transform:translateX(236px)}42.857%{opacity:1;transform:translateX(236px)}42.867%,100%{opacity:0;transform:translateX(236px)}}
.l01a-g1 rect,.l01a-g1 line,.l01a-g1 path:not(.l01a-gl){animation-name:l01a-g1}.l01a-p1{animation-name:l01a-p1}
@keyframes l01a-g2{0%,42.847%{opacity:.5}42.857%{opacity:1}64.286%{opacity:1}64.296%,100%{opacity:.5}}
@keyframes l01a-p2{0%,42.847%{opacity:0;transform:translateX(0)}42.857%{opacity:1;transform:translateX(0)}60%{opacity:1;transform:translateX(236px)}64.286%{opacity:1;transform:translateX(236px)}64.296%,100%{opacity:0;transform:translateX(236px)}}
.l01a-g2 rect,.l01a-g2 line,.l01a-g2 path:not(.l01a-gl){animation-name:l01a-g2}.l01a-p2{animation-name:l01a-p2}
@keyframes l01a-g3{0%,64.276%{opacity:.5}64.286%{opacity:1}85.714%{opacity:1}85.724%,100%{opacity:.5}}
@keyframes l01a-p3{0%,64.276%{opacity:0;transform:translateX(0)}64.286%{opacity:1;transform:translateX(0)}81.429%{opacity:1;transform:translateX(236px)}85.714%{opacity:1;transform:translateX(236px)}85.724%,100%{opacity:0;transform:translateX(236px)}}
.l01a-g3 rect,.l01a-g3 line,.l01a-g3 path:not(.l01a-gl){animation-name:l01a-g3}.l01a-p3{animation-name:l01a-p3}
@keyframes l01a-g4{0%,85.704%{opacity:.5}85.714%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.l01a-g4 rect,.l01a-g4 line,.l01a-g4 path:not(.l01a-gl){animation-name:l01a-g4}
</style>
<defs>
<marker id="l01a-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l01a-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l01a-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l01a-life" x1="110" y1="72" x2="110" y2="428"/>
<line class="l01a-life" x1="380" y1="72" x2="380" y2="428"/>
<line class="l01a-life" x1="650" y1="72" x2="650" y2="428"/>
<rect class="l01a-box" x="20" y="10" width="180" height="62" rx="10"/><text class="l01a-ttl" x="110" y="36">Browser</text><text class="l01a-sub" x="110" y="56">index.html</text>
<rect class="l01a-box" x="290" y="10" width="180" height="62" rx="10"/><text class="l01a-ttl" x="380" y="36">Engine</text><text class="l01a-sub" x="380" y="56">engine/app.js</text>
<rect class="l01a-box" x="560" y="10" width="180" height="62" rx="10"/><text class="l01a-ttl" x="650" y="36">Course folder</text><text class="l01a-sub" x="650" y="56">served as files</text>
<g class="l01a-g l01a-g0">
<text class="l01a-main" x="245" y="108">index.html loads</text>
<text class="l01a-dim" x="245" y="124">../../engine/app.js</text>
<line class="l01a-front" x1="124" y1="138" x2="366" y2="138" marker-end="url(#l01a-m-front)"/>
<circle class="l01a-badge l01a-b-front" cx="110" cy="138" r="12"/><text class="l01a-bt" x="110" y="142.5">1</text>
</g>
<g class="l01a-g l01a-g1">
<text class="l01a-main" x="515" y="178">fetch manifest.json</text>
<line class="l01a-front" x1="394" y1="192" x2="636" y2="192" marker-end="url(#l01a-m-front)"/>
<circle class="l01a-badge l01a-b-front" cx="380" cy="192" r="12"/><text class="l01a-bt" x="380" y="196.5">2</text>
</g>
<g class="l01a-g l01a-g2">
<text class="l01a-main" x="515" y="232">fetch lessons/&lt;id>/lesson.md</text>
<line class="l01a-front" x1="394" y1="246" x2="636" y2="246" marker-end="url(#l01a-m-front)"/>
<circle class="l01a-badge l01a-b-front" cx="380" cy="246" r="12"/><text class="l01a-bt" x="380" y="250.5">3</text>
</g>
<g class="l01a-g l01a-g3">
<text class="l01a-main" x="515" y="286">fetch lessons/&lt;id>/quiz.json</text>
<line class="l01a-front" x1="394" y1="300" x2="636" y2="300" marker-end="url(#l01a-m-front)"/>
<circle class="l01a-badge l01a-b-front" cx="380" cy="300" r="12"/><text class="l01a-bt" x="380" y="304.5">4</text>
</g>
<g class="l01a-g l01a-g4">
<rect class="l01a-note" x="575" y="334" width="150" height="48" rx="8"/>
<text class="l01a-nt" x="650" y="355">A 404 on quiz.json</text>
<text class="l01a-nt" x="650" y="372">means no quiz</text>
</g>
<circle class="l01a-pk l01a-p0" cx="130" cy="138" r="5.5"/>
<circle class="l01a-pk l01a-p1" cx="400" cy="192" r="5.5"/>
<circle class="l01a-pk l01a-p2" cx="400" cy="246" r="5.5"/>
<circle class="l01a-pk l01a-p3" cx="400" cy="300" r="5.5"/>
<line class="l01a-front" x1="40" y1="456" x2="70" y2="456"/>
<text class="l01a-dim" x="78" y="460" style="text-anchor:start">normal event</text>
</svg>
</div>
</div>
<!-- /diagram:course-folder -->

## index.html is boilerplate

Every course has the same `index.html`, copied from `engine/course.html`. It
loads `../../engine/style.css` and `../../engine/app.js` — which is why the
server has to run from the repo root rather than inside a course folder.
Don't edit it per course; if you need a change, change the engine.

## manifest.json drives everything

The `lessons` array sets the order. The `id` must match the folder name. The
`slug` namespaces your saved progress in `localStorage`, so changing it later
resets the saved progress for everyone who has used the course.

## Stubs are first-class

Lesson 3 of this course is a stub. Look at the sidebar: it is greyed out, and
the progress label says "0 of 2 complete" rather than "0 of 3" — unwritten
lessons are excluded from the denominator rather than counted as incomplete
work.

This matters more than it looks. The alternative, when a generator runs out
of real material, is filler: three paragraphs restating the lesson title.
A stub with an honest outline tells the reader what is coming and tells the
author what to write next. Filler just wastes the reader's time and makes
them trust the rest of the course less.

## Levels are optional

This course declares `"levels"` in its manifest, which is why the sidebar has
a Beginner, Intermediate and Advanced switch. A lesson can ship
`lesson.<level>.md` for any level; where it does not, the engine falls back to
`lesson.md`. This lesson has a beginner and an advanced version, so
intermediate reads this file. Lesson 2 has only `lesson.md`, so it reads the
same at every level.

## What the engine does not do

No accounts, no server-side state, no completion reporting, no grading you
can audit. Progress lives in one browser's `localStorage`. If you need to
prove someone completed training, this is the wrong tool — it is built for
self-directed learning, not compliance.
