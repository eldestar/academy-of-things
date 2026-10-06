#!/usr/bin/env python3
"""Generate an animated sequence-diagram SVG block for a lesson.

    python3 scripts/sequence-diagram.py spec.json                       # print the block
    python3 scripts/sequence-diagram.py spec.json --insert lesson.md --after "## Heading"
    python3 scripts/sequence-diagram.py spec.json --insert lesson.md --before "1. First list item"
    python3 scripts/sequence-diagram.py spec.json --insert a.md b.md c.md --after "## Heading"

The block is raw HTML (inline SVG plus a <style>) that the engine renders as-is.
It uses the engine's CSS variables, so it follows light and dark mode, steps
through the story with a spotlight and a travelling dot, pauses on hover, shows
every step statically under prefers-reduced-motion, and scrolls inside its own
box on narrow screens. No scripts. --insert is idempotent: re-running replaces
the block between its <!-- diagram:ID --> markers. Pass several files (for
example a lesson's level variants) to keep every copy identical.

Spec (JSON):
  id, prefix (unique short css prefix), title, desc (screen-reader text), duration (s, default 18)
  legend (optional): override the legend words, keys front, back, bad, good
  lanes:  [{id, title, sub, hot?}]            2 to 4 lanes, left to right
  steps:  [{type: "arrow", from, to, label: [line, ...], badge?, tone?: front|back|bad, with_previous?}
           {type: "note",  under, lines: [line, ...], badge?, tone?: plain|good|bad, with_previous?}]
Each step without with_previous is one animation slot. Layout is automatic.
"""
import argparse, json, re, sys
import xml.dom.minidom as minidom

W = 760
FONT = '-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif'


def pct(x):
    return f"{x:.3f}".rstrip("0").rstrip(".")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def build(spec):
    P = spec["prefix"]
    dur = spec.get("duration", 18)
    lanes = spec["lanes"]
    assert 2 <= len(lanes) <= 4, "2 to 4 lanes"
    step_x = (W - 220) / (len(lanes) - 1)
    lx = {l["id"]: 110 + i * step_x for i, l in enumerate(lanes)}
    box_w = min(180, step_x - 20)

    slots, dots = [], {}          # slots: list of svg-part lists; dots: slot -> (x0, dx, y, tone)
    cursor, last_arrow = 96, None  # last_arrow: (y, to_x)
    used_tones = {"front"}

    for st in spec["steps"]:
        newslot = not st.get("with_previous")
        if newslot:
            slots.append([])
        k = len(slots) - 1
        tone = st.get("tone", "front" if st["type"] == "arrow" else "plain")
        if st["type"] == "arrow":
            fx, tx = lx[st["from"]], lx[st["to"]]
            n = len(st["label"])
            y = cursor + 16 * n + 10   # a with_previous arrow shares the slot but gets its own row
            right = tx > fx
            x0 = fx + 14 if right else fx - 14
            x1 = tx - 14 if right else tx + 14
            marker = {"front": "m-front", "back": "m-back", "bad": "m-bad"}[tone]
            parts = []
            base = y - 14 - 16 * (n - 1)
            for j, text in enumerate(st["label"]):
                cls = f"{P}-main" if j == 0 else f"{P}-dim"
                if tone == "bad" and j == 0:
                    cls += f" {P}-badt"
                parts.append(f'<text class="{cls}" x="{(x0 + x1) / 2:.0f}" y="{base + 16 * j}">{esc(text)}</text>')
            parts.append(f'<line class="{P}-{tone}" x1="{x0:.0f}" y1="{y}" x2="{x1:.0f}" y2="{y}" marker-end="url(#{P}-{marker})"/>')
            if st.get("badge"):
                parts.append(f'<circle class="{P}-badge {P}-b-{tone}" cx="{fx:.0f}" cy="{y}" r="12"/>'
                             f'<text class="{P}-bt" x="{fx:.0f}" y="{y + 4.5}">{esc(st["badge"])}</text>')
            slots[k].append("\n".join(parts))
            dots[k] = (x0 + (6 if right else -6), x1 - x0 - (6 if right else -6), y, tone)
            used_tones.add(tone)
            last_arrow = (y, tx)
            cursor = max(cursor, y + 28)
        else:
            lines = st["lines"]
            w = max(150, int(max(len(t) for t in lines) * 6.6 + 30))
            h = 14 + 17 * len(lines)
            cx = lx[st["under"]]
            x = min(max(cx - w / 2, 10), W - 10 - w)
            y = (last_arrow[0] + 18) if (not newslot and last_arrow) else cursor + 6
            cls = {"plain": "note", "good": "note-good", "bad": "note-bad"}[tone]
            parts = [f'<rect class="{P}-{cls}" x="{x:.0f}" y="{y}" width="{w}" height="{h}" rx="8"/>']
            for j, t in enumerate(lines):
                parts.append(f'<text class="{P}-nt" x="{x + w / 2:.0f}" y="{y + 21 + 17 * j}">{esc(t)}</text>')
            if st.get("badge"):
                parts.append(f'<circle class="{P}-badge {P}-b-{tone}" cx="{x:.0f}" cy="{y + h / 2:.0f}" r="12"/>'
                             f'<text class="{P}-bt" x="{x:.0f}" y="{y + h / 2 + 4.5:.1f}">{esc(st["badge"])}</text>')
            slots[k].append("\n".join(parts))
            if tone in ("good", "bad"):
                used_tones.add("note-" + tone)
            cursor = max(cursor, y + h + 22)

    N = len(slots)
    H = int(cursor + 76)

    css = [f"""<style>
.{P}-box{{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}}
.{P}-hot{{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}}
.{P}-ttl{{fill:var(--text);font:600 15px {FONT};text-anchor:middle}}
.{P}-sub{{fill:var(--muted);font:12px {FONT};text-anchor:middle}}
.{P}-life{{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}}
.{P}-front{{stroke:var(--accent);stroke-width:2;fill:none}}
.{P}-back{{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}}
.{P}-bad{{stroke:var(--bad);stroke-width:2;fill:none}}
.{P}-main{{fill:var(--text);font:600 13px {FONT};text-anchor:middle}}
.{P}-badt{{fill:var(--bad-text)}}
.{P}-dim{{fill:var(--muted);font:12px {FONT};text-anchor:middle}}
.{P}-badge{{fill:var(--accent)}}
.{P}-b-back{{fill:var(--muted)}}
.{P}-b-bad{{fill:var(--bad)}}
.{P}-b-good{{fill:var(--good)}}
.{P}-bt{{fill:var(--on-accent);font:700 12px {FONT};text-anchor:middle}}
.{P}-note{{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}}
.{P}-note-good{{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}}
.{P}-note-bad{{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}}
.{P}-nt{{fill:var(--body);font:12.5px {FONT};text-anchor:middle}}
.{P}-pk{{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:{dur}s;animation-timing-function:linear;animation-iteration-count:infinite}}
.{P}-pk.{P}-pkback{{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}}
.{P}-pk.{P}-pkbad{{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}}
.{P}-g{{opacity:.45;animation-duration:{dur}s;animation-timing-function:linear;animation-iteration-count:infinite}}
svg.{P}-flow:hover .{P}-g,svg.{P}-flow:hover .{P}-pk{{animation-play-state:paused}}
.{P}-cb{{position:absolute;opacity:0;width:1px;height:1px;margin:0}}
.{P}-btn{{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px {FONT};cursor:pointer;user-select:none}}
.{P}-btn:hover{{background:var(--hover)}}
.{P}-cb:focus-visible + .{P}-btn{{outline:2px solid var(--accent);outline-offset:2px}}
.{P}-cb:checked + .{P}-btn .{P}-off,.{P}-cb:not(:checked) + .{P}-btn .{P}-on{{display:none}}
.{P}-cb:checked ~ .{P}-box .{P}-g,.{P}-cb:checked ~ .{P}-box .{P}-pk{{animation-play-state:paused}}
@media (prefers-reduced-motion:reduce){{.{P}-g{{animation:none;opacity:1}}.{P}-pk{{animation:none;display:none}}.{P}-btn{{display:none}}}}"""]
    for i in range(N):
        s, e = i / N * 100, (i + 1) / N * 100
        if i == 0:
            css.append(f"@keyframes {P}-g{i}{{0%{{opacity:1}}{pct(e)}%{{opacity:1}}{pct(e + .01)}%,100%{{opacity:.45}}}}")
        else:
            css.append(f"@keyframes {P}-g{i}{{0%,{pct(s - .01)}%{{opacity:.45}}{pct(s)}%{{opacity:1}}{pct(e)}%{{opacity:1}}{pct(e + .01)}%,100%{{opacity:.45}}}}")
        rule = f".{P}-g{i}{{animation-name:{P}-g{i}}}"
        if i in dots:
            dx = dots[i][1]
            css.append(f"@keyframes {P}-p{i}{{0%,{pct(s - .01)}%{{opacity:0;transform:translateX(0)}}{pct(s)}%{{opacity:1;transform:translateX(0)}}{pct(e)}%{{opacity:1;transform:translateX({dx:.0f}px)}}{pct(e + .01)}%,100%{{opacity:0;transform:translateX({dx:.0f}px)}}}}")
            rule += f".{P}-p{i}{{animation-name:{P}-p{i}}}"
        css.append(rule)
    css.append("</style>")

    body = ["<defs>"]
    for name, var in (("front", "accent"), ("back", "muted"), ("bad", "bad")):
        body.append(f'<marker id="{P}-m-{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--{var})"/></marker>')
    body.append("</defs>")
    for l in lanes:
        body.append(f'<line class="{P}-life" x1="{lx[l["id"]]:.0f}" y1="72" x2="{lx[l["id"]]:.0f}" y2="{H - 52}"/>')
    for l in lanes:
        x = lx[l["id"]]
        kind = "hot" if l.get("hot") else "box"
        body.append(f'<rect class="{P}-{kind}" x="{x - box_w / 2:.0f}" y="10" width="{box_w:.0f}" height="62" rx="10"/>'
                    f'<text class="{P}-ttl" x="{x:.0f}" y="36">{esc(l["title"])}</text>'
                    f'<text class="{P}-sub" x="{x:.0f}" y="56">{esc(l.get("sub", ""))}</text>')
    for i, parts in enumerate(slots):
        body.append(f'<g class="{P}-g {P}-g{i}">\n' + "\n".join(parts) + "\n</g>")
    for i, (x0, dx, y, tone) in dots.items():
        extra = "" if tone == "front" else f" {P}-pk{tone}"
        body.append(f'<circle class="{P}-pk {P}-p{i}{extra}" cx="{x0:.0f}" cy="{y}" r="5.5"/>')

    words = {"front": "normal event", "back": "server to server", "bad": "failure mode",
             "good": "what your handler must do", **spec.get("legend", {})}
    legend = [("front", words["front"])]
    if "back" in used_tones: legend.append(("back", words["back"]))
    if "bad" in used_tones: legend.append(("bad", words["bad"]))
    if "note-good" in used_tones: legend.append(("note-good", words["good"]))
    ly, x = H - 24, 40
    for kind, text in legend:
        if kind.startswith("note"):
            body.append(f'<rect class="{P}-{kind}" x="{x}" y="{ly - 8}" width="22" height="16" rx="4"/>')
            tx = x + 30
        else:
            body.append(f'<line class="{P}-{kind}" x1="{x}" y1="{ly}" x2="{x + 30}" y2="{ly}"/>')
            tx = x + 38
        body.append(f'<text class="{P}-dim" x="{tx}" y="{ly + 4}" style="text-anchor:start">{esc(text)}</text>')
        x = tx + int(len(text) * 6.4) + 34

    # A real checkbox styled as a button: keyboard operable (Tab, Space) with no script, so a
    # keyboard user can pause moving content (WCAG 2.2.2). Hover still pauses as well.
    svg = (
        '<div style="position:relative;margin:20px 0">\n'
        f'<input type="checkbox" id="{P}-pause" class="{P}-cb" />'
        f'<label for="{P}-pause" class="{P}-btn"><span class="{P}-off">Pause animation</span><span class="{P}-on">Play animation</span></label>\n'
        f'<div class="{P}-box" style="overflow-x:auto">\n'
        f'<svg class="{P}-flow" viewBox="0 0 {W} {H}" role="img" aria-labelledby="{P}-t {P}-d" '
        'style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">\n'
        f'<title id="{P}-t">{esc(spec["title"])}</title>\n'
        f'<desc id="{P}-d">{esc(spec["desc"])} The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>\n'
        + "\n".join(css) + "\n" + "\n".join(body) + "\n</svg>\n</div>\n</div>"
    )
    minidom.parseString(svg)
    assert not re.search(r"\n[ \t]*\n", svg), "blank line would end the HTML block early"
    return f'<!-- diagram:{spec["id"]} -->\n{svg}\n<!-- /diagram:{spec["id"]} -->', N


def insert(path, block, spec_id, after, caption, before=None):
    t = open(path, encoding="utf-8").read()
    pat = re.compile(rf"<!-- diagram:{re.escape(spec_id)} -->.*?<!-- /diagram:{re.escape(spec_id)} -->", re.S)
    if pat.search(t):
        t = pat.sub(lambda m: block, t, count=1)
    elif before:
        at = re.search(rf"^{re.escape(before)}", t, re.M)
        assert at, f"line not found in {path}: {before}"
        tail = f"\n\n{caption}" if caption else ""
        t = t[:at.start()] + block + tail + "\n\n" + t[at.start():]
    else:
        assert after, "--after or --before is required for the first insert"
        line = re.search(rf"^{re.escape(after)}[ \t]*$", t, re.M)
        assert line, f"heading not found in {path}: {after}"
        tail = f"\n\n{caption}" if caption else ""
        t = t[:line.end()] + "\n\n" + block + tail + t[line.end():]
    open(path, "w", encoding="utf-8").write(t)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--insert", nargs="+", metavar="FILE")
    ap.add_argument("--after", help="exact heading line to insert under, e.g. '## The flow'")
    ap.add_argument("--before", help="insert before the first line starting with this text instead (e.g. a numbered list)")
    ap.add_argument("--caption", help="one paragraph placed right after the diagram")
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8"))
    block, n = build(spec)
    if not a.insert:
        print(block)
        return
    for f in a.insert:
        insert(f, block, spec["id"], a.after, a.caption, a.before)
        print(f"inserted {spec['id']} ({n} steps) into {f}")


if __name__ == "__main__":
    main()
