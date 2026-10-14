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
`lessons/<id>/quiz.json` (for a selected level it tries the level's file
first; see Levels below). Both paths are relative to the course folder, and
nothing in the engine ties the course folder's name to the manifest `slug`.
Only the lesson `id` has to match its folder.

A stub is never fetched. Its `outline` from the manifest is rendered instead,
so a stub needs no folder at all.

## Failure behaviour

- A missing `lesson.md` shows the title and a message naming the path that
  failed to load.
- A missing `quiz.json` (a 404) means no quiz. That is normal and silent.
  Any other failure to load it shows a message and the lesson is not marked
  complete.
- A `quiz.json` that exists but is not valid JSON shows a message naming the
  file and the parse error. The lesson text still renders, but the lesson
  cannot be completed until the file is fixed.

## State

Progress is one `localStorage` key per course: `academy-of-things:<slug>:progress`. It
holds an object keyed by lesson id, each with a `completed` flag and a
timestamp. A lesson with no quiz is marked complete as soon as it opens. A
lesson with a quiz is marked complete only when the reader passes it, and
failed attempts are not recorded. The slug is the only namespace for progress, so renaming
it orphans every reader's saved progress.

## Levels

This course declares `levels` in its manifest. For the selected level the
engine tries `lesson.<level>.md` and `quiz.<level>.json` first and falls back
to `lesson.md` and `quiz.json`, each independently. You can fork the text
without forking the quiz, or the reverse. Progress is per lesson, not per
level. This lesson has a beginner and an advanced version; intermediate falls
back to `lesson.md`.

<!-- diagram:course-folder -->
<div class="l01a-wrap" style="position:relative">
<input type="checkbox" id="l01a-pause" class="l01a-cb" /><label for="l01a-pause" class="l01a-btn"><span class="l01a-off">Pause animation</span><span class="l01a-on">Play animation</span></label>
<div class="l01a-box" style="overflow-x:auto">
<svg class="l01a-flow" viewBox="0 0 760 344" role="img" aria-labelledby="l01a-t l01a-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l01a-t">How a level picks its lesson file</title>
<desc id="l01a-d">For the selected level the engine tries lesson.level.md first. If that is not found it tries lesson.md, and if that is also missing it shows the title and the path that failed to load. The quiz resolves the same way, independently. The diagram highlights each path in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
@keyframes l01a-h0{0%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:0}}
.l01a-h0{animation-name:l01a-h0}
@keyframes l01a-h1{0%,33.323%{opacity:0}33.333%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:0}}
.l01a-h1{animation-name:l01a-h1}
@keyframes l01a-h2{0%,66.657%{opacity:0}66.667%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l01a-h2{animation-name:l01a-h2}
</style>
<defs>
<marker id="l01a-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l01a-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l01a-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<path class="l01a-edge" d="M380,89 L380,118 L216,118 L216,144" marker-end="url(#l01a-m-front)"/>
<text class="l01a-dimL" x="223" y="134">lesson.&lt;level>.md found</text>
<path class="l01a-edge" d="M380,89 L380,118 L443,118 L443,144" marker-end="url(#l01a-m-front)"/>
<text class="l01a-dimL" x="450" y="134">not found</text>
<path class="l01a-edge" d="M443,178 L443,207 L354,207 L354,233" marker-end="url(#l01a-m-front)"/>
<text class="l01a-dimL" x="361" y="223">found</text>
<path class="l01a-edge" d="M443,178 L443,207 L518,207 L518,233" marker-end="url(#l01a-m-front)"/>
<text class="l01a-dimL" x="525" y="223">not found</text>
<rect class="l01a-note-good" x="161" y="147" width="110" height="31" rx="8"/><text class="l01a-nt" x="216" y="168">Render it</text>
<rect class="l01a-note-good" x="287" y="236" width="134" height="31" rx="8"/><text class="l01a-nt" x="354" y="257">Render lesson.md</text>
<rect class="l01a-note-bad" x="437" y="236" width="162" height="48" rx="8"/><text class="l01a-nt" x="518" y="257">Show the title and</text><text class="l01a-nt" x="518" y="274">the path that failed</text>
<rect class="l01a-box" x="386" y="147" width="114" height="31" rx="8"/><text class="l01a-main" x="443" y="168">Try lesson.md</text>
<rect class="l01a-box" x="292" y="24" width="175" height="65" rx="8"/><text class="l01a-main" x="380" y="45">Reader selects a level</text><text class="l01a-nt" x="380" y="62">Text and quiz resolve</text><text class="l01a-nt" x="380" y="79">independently</text>
<g class="l01a-h l01a-h0">
<path class="l01a-hle" d="M380,89 L380,118 L216,118 L216,144" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-hl" x="292" y="24" width="175" height="65" rx="8"/>
<rect class="l01a-hl" x="161" y="147" width="110" height="31" rx="8"/>
</g>
<g class="l01a-h l01a-h1">
<path class="l01a-hle" d="M380,89 L380,118 L443,118 L443,144" marker-end="url(#l01a-m-front)"/>
<path class="l01a-hle" d="M443,178 L443,207 L354,207 L354,233" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-hl" x="292" y="24" width="175" height="65" rx="8"/>
<rect class="l01a-hl" x="386" y="147" width="114" height="31" rx="8"/>
<rect class="l01a-hl" x="287" y="236" width="134" height="31" rx="8"/>
</g>
<g class="l01a-h l01a-h2">
<path class="l01a-hle" d="M380,89 L380,118 L443,118 L443,144" marker-end="url(#l01a-m-front)"/>
<path class="l01a-hle" d="M443,178 L443,207 L518,207 L518,233" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-hl" x="292" y="24" width="175" height="65" rx="8"/>
<rect class="l01a-hl" x="386" y="147" width="114" height="31" rx="8"/>
<rect class="l01a-hl" x="437" y="236" width="162" height="48" rx="8"/>
</g>
<line class="l01a-front" x1="40" y1="320" x2="70" y2="320"/>
<text class="l01a-dim" x="78" y="324" style="text-anchor:start">the path being traced</text>
<rect class="l01a-note-good" x="246" y="312" width="22" height="16" rx="4"/>
<text class="l01a-dim" x="276" y="324" style="text-anchor:start">fine</text>
<rect class="l01a-note-bad" x="335" y="312" width="22" height="16" rx="4"/>
<text class="l01a-dim" x="365" y="324" style="text-anchor:start">the problem</text>
</svg>
</div>
</div>
<!-- /diagram:course-folder -->

## What it does not do

No accounts, no server-side state, no completion reporting. If you need
audit-grade proof that someone finished training, this is the wrong tool.
