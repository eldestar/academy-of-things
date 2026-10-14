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
      lesson.md       the standard text
      lesson.beginner.md  this text
      quiz.json       the questions below
```

Each lesson gets its own folder. The folder name is the lesson's `id`.

<!-- diagram:course-folder -->
<div class="l01a-wrap" style="position:relative">
<input type="checkbox" id="l01a-pause" class="l01a-cb" /><label for="l01a-pause" class="l01a-btn"><span class="l01a-off">Pause animation</span><span class="l01a-on">Play animation</span></label>
<div class="l01a-box" style="overflow-x:auto">
<svg class="l01a-flow" viewBox="0 0 760 456" role="img" aria-labelledby="l01a-t l01a-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l01a-t">A course is a folder</title>
<desc id="l01a-d">The files in a course folder: index.html, manifest.json, and a lessons folder with one folder per lesson, each holding lesson.md and an optional quiz.json. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
.l01a-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l01a-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l01a-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l01a-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l01a-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l01a-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l01a-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l01a-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l01a-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l01a-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l01a-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l01a-pk.l01a-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l01a-pk.l01a-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l01a-wrap{margin:20px 0}
@media (min-width:801px){.l01a-wrap{margin-left:-44px;margin-right:-44px}}
.l01a-g rect,.l01a-g line,.l01a-g path:not(.l01a-gl){opacity:.5;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l01a-h{opacity:0;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l01a-flow:hover .l01a-g rect,svg.l01a-flow:hover .l01a-g line,svg.l01a-flow:hover .l01a-g path:not(.l01a-gl),svg.l01a-flow:hover .l01a-pk,svg.l01a-flow:hover .l01a-h{animation-play-state:paused}
.l01a-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l01a-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l01a-btn:hover{background:var(--hover)}
.l01a-cb:focus-visible + .l01a-btn{outline:2px solid var(--accent);outline-offset:2px}
.l01a-cb:checked + .l01a-btn .l01a-off,.l01a-cb:not(:checked) + .l01a-btn .l01a-on{display:none}
.l01a-cb:checked ~ .l01a-box .l01a-g rect,.l01a-cb:checked ~ .l01a-box .l01a-g line,.l01a-cb:checked ~ .l01a-box .l01a-g path:not(.l01a-gl),.l01a-cb:checked ~ .l01a-box .l01a-pk,.l01a-cb:checked ~ .l01a-box .l01a-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l01a-g rect,.l01a-g line,.l01a-g path:not(.l01a-gl){animation:none;opacity:1}.l01a-pk{animation:none;display:none}.l01a-h{animation:none;opacity:0}.l01a-btn{display:none}}
@keyframes l01a-g0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:.5}}
@keyframes l01a-h0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:0}}
.l01a-g0 rect,.l01a-g0 line,.l01a-g0 path:not(.l01a-gl){animation-name:l01a-g0}.l01a-h0{animation-name:l01a-h0}
@keyframes l01a-g1{0%,24.99%{opacity:.5}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.5}}
@keyframes l01a-h1{0%,24.99%{opacity:0}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:0}}
.l01a-g1 rect,.l01a-g1 line,.l01a-g1 path:not(.l01a-gl){animation-name:l01a-g1}.l01a-h1{animation-name:l01a-h1}
@keyframes l01a-g2{0%,49.99%{opacity:.5}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:.5}}
@keyframes l01a-h2{0%,49.99%{opacity:0}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:0}}
.l01a-g2 rect,.l01a-g2 line,.l01a-g2 path:not(.l01a-gl){animation-name:l01a-g2}.l01a-h2{animation-name:l01a-h2}
@keyframes l01a-g3{0%,74.99%{opacity:.5}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
@keyframes l01a-h3{0%,74.99%{opacity:0}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l01a-g3 rect,.l01a-g3 line,.l01a-g3 path:not(.l01a-gl){animation-name:l01a-g3}.l01a-h3{animation-name:l01a-h3}
</style>
<defs>
<marker id="l01a-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l01a-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l01a-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l01a-box" x="14" y="16" width="440" height="382" rx="9"/><text class="l01a-ttlL" x="28" y="37">example-course/</text><text class="l01a-subL" x="28" y="54">one folder per course</text>
<rect class="l01a-nest" x="26" y="62" width="416" height="46" rx="9"/><text class="l01a-ttlL" x="40" y="83">index.html</text><text class="l01a-subL" x="40" y="100">the page shell</text>
<rect class="l01a-nest" x="26" y="116" width="416" height="46" rx="9"/><text class="l01a-ttlL" x="40" y="137">manifest.json</text><text class="l01a-subL" x="40" y="154">table of contents</text>
<rect class="l01a-nest" x="26" y="170" width="416" height="216" rx="9"/><text class="l01a-ttlL" x="40" y="191">lessons/</text><text class="l01a-subL" x="40" y="208">one folder per lesson</text>
<rect class="l01a-nest" x="38" y="216" width="392" height="158" rx="9"/><text class="l01a-ttlL" x="52" y="237">01-anatomy-of-a-course/</text><text class="l01a-subL" x="52" y="254">folder name is the lesson id</text>
<rect class="l01a-nest" x="50" y="262" width="368" height="46" rx="9"/><text class="l01a-ttlL" x="64" y="283">lesson.md</text><text class="l01a-subL" x="64" y="300">the text</text>
<rect class="l01a-nest" x="50" y="316" width="368" height="46" rx="9"/><text class="l01a-ttlL" x="64" y="337">quiz.json</text><text class="l01a-subL" x="64" y="354">the questions</text>
<g class="l01a-g l01a-g0">
<path class="l01a-conn" d="M442,79 L462,79 L462,79 L470,79" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note" x="484" y="55" width="262" height="48" rx="8"/>
<text class="l01a-nt" x="615" y="76">Same in every course</text>
<text class="l01a-nt" x="615" y="93">You never edit it</text>
<circle class="l01a-badge l01a-b-front" cx="484" cy="79" r="12"/><text class="l01a-bt" x="484" y="83.5">1</text>
</g>
<g class="l01a-g l01a-g1">
<path class="l01a-conn" d="M442,133 L466,133 L466,137 L470,137" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note" x="484" y="113" width="262" height="48" rx="8"/>
<text class="l01a-nt" x="615" y="134">Course title and lesson list</text>
<text class="l01a-nt" x="615" y="151">Lessons appear in this order</text>
<circle class="l01a-badge l01a-b-front" cx="484" cy="137" r="12"/><text class="l01a-bt" x="484" y="141.5">2</text>
</g>
<g class="l01a-g l01a-g2">
<path class="l01a-conn" d="M418,279 L470,279 L470,279 L470,279" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note" x="484" y="264" width="262" height="31" rx="8"/>
<text class="l01a-nt" x="615" y="284">Written in Markdown</text>
<circle class="l01a-badge l01a-b-front" cx="484" cy="279" r="12"/><text class="l01a-bt" x="484" y="283.5">3</text>
</g>
<g class="l01a-g l01a-g3">
<path class="l01a-conn" d="M418,333 L474,333 L474,333 L470,333" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note" x="484" y="309" width="262" height="48" rx="8"/>
<text class="l01a-nt" x="615" y="330">Optional</text>
<text class="l01a-nt" x="615" y="347">No file means no quiz</text>
<circle class="l01a-badge l01a-b-front" cx="484" cy="333" r="12"/><text class="l01a-bt" x="484" y="337.5">4</text>
</g>
<g class="l01a-h l01a-h0">
<rect class="l01a-hl" x="26" y="62" width="416" height="46" rx="9"/>
</g>
<g class="l01a-h l01a-h1">
<rect class="l01a-hl" x="26" y="116" width="416" height="46" rx="9"/>
</g>
<g class="l01a-h l01a-h2">
<rect class="l01a-hl" x="50" y="262" width="368" height="46" rx="9"/>
</g>
<g class="l01a-h l01a-h3">
<rect class="l01a-hl" x="50" y="316" width="368" height="46" rx="9"/>
</g>
</svg>
</div>
</div>
<!-- /diagram:course-folder -->

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
