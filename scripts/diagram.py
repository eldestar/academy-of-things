#!/usr/bin/env python3
"""Generate an animated diagram block (inline SVG) for a lesson.

    python3 scripts/diagram.py spec.json                       # print the block
    python3 scripts/diagram.py spec.json --insert lesson.md --after "## Heading"
    python3 scripts/diagram.py spec.json --insert lesson.md --before "1. First list item"
    python3 scripts/diagram.py spec.json --insert a.md b.md --after "## Heading"

The block is raw HTML (inline SVG plus a <style>) that the engine renders as-is.
It uses the engine's CSS variables, so it follows light and dark mode, steps
through the story with a spotlight (and a travelling dot on arrows), pauses on
hover and from a keyboard-operable "Pause animation" control, shows everything
statically under prefers-reduced-motion, and scrolls inside its own box on
narrow screens. No scripts. --insert is idempotent: re-running replaces the
block between its <!-- diagram:ID --> markers. A lesson's level files take
their own spec: diagrams/<id>.beginner.json, diagrams/<id>.json (intermediate),
diagrams/<id>.advanced.json, so each level can show a different diagram.

Common spec fields:
  kind    sequence (default) | anatomy | flow | stages | matrix
  id      marker id, unique per lesson file (the same id may repeat across levels)
  prefix  short css prefix, unique per diagram within a lesson file
  title, desc (screen-reader text), duration (seconds per loop, default 18)
  legend  optional overrides for the legend words

kind sequence: who talks to whom, in order.
  lanes:  [{id, title, sub, hot?}]            2 to 4, left to right
  steps:  [{type: "arrow", from, to, label: [line, ...], badge?, tone?: front|back|bad, with_previous?}
           {type: "note",  under, lines: [line, ...], badge?, tone?: plain|good|bad, with_previous?}]
  legend keys: front, back, bad, good

kind anatomy: a nested structure; callouts say what reads or checks each part.
  root:   {title, sub?, hot?, check?: [line, ...], tone?: plain|good|bad, children?: [node, ...]}
          Nodes with `check` get a numbered callout and one animation step, in tree order.
  legend keys: plain, good, bad

kind flow: a decision tree walked from the top; one animation step per leaf.
  root:   {lines: [line, ...], tone?: plain|good|bad, children?: [{edge: "label", node: {...}}, ...]}
          Up to 6 leaves. Leaves are the conclusions.
  legend keys: front, plain, good, bad

kind stages: states or phases in a row, with the transitions between neighbours.
  stages: [{title, sub?, lines?: [line, ...], tone?: plain|good|bad, hot?, badge?}]   2 to 4
  links:  [{from: i, to: i+1 or i-1, label?: [line, ...], tone?: front|back|bad}]     0-based; default: forward arrows
  legend keys: front, back, bad, good

kind matrix: rows compared across columns, one animation step per row.
  columns: [{title, sub?}]                                  1 to 4
  rows:    [{title, sub?, cells: [{mark?: good|partial|bad, text?: [line, ...]}, ...]}]   up to 7
  legend keys: good, partial, bad
"""
import argparse, json, re
import xml.dom.minidom as minidom

W = 760
FONT = '-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif'
LO = ".45"
WORD = {  # estimated px per character at the diagram's text sizes
    "label": 6.6, "note": 6.6, "small": 6.2, "title": 7.2,
}


def pct(x):
    return f"{x:.3f}".rstrip("0").rstrip(".")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def fit(lines, width, what, per=None):
    per = per or WORD["small"]
    for t in lines:
        assert len(t) * per <= width, f"{what}: line too long for {width:.0f}px: {t!r}"


def badge(P, cx, cy, text, tone="front"):
    return (f'<circle class="{P}-badge {P}-b-{tone}" cx="{cx:.0f}" cy="{cy:.0f}" r="12"/>'
            f'<text class="{P}-bt" x="{cx:.0f}" y="{cy + 4.5:.1f}">{esc(text)}</text>')


def glyph(P, kind, cx, cy, r=10):
    fill = {"good": "good", "bad": "bad", "partial": "muted"}[kind]
    s = r * 0.42
    mark = {"good": f"M{cx - s:.1f},{cy:.1f} L{cx - s / 3:.1f},{cy + s * .8:.1f} L{cx + s:.1f},{cy - s * .8:.1f}",
            "bad": f"M{cx - s * .8:.1f},{cy - s * .8:.1f} L{cx + s * .8:.1f},{cy + s * .8:.1f} M{cx + s * .8:.1f},{cy - s * .8:.1f} L{cx - s * .8:.1f},{cy + s * .8:.1f}",
            "partial": f"M{cx - s:.1f},{cy:.1f} L{cx + s:.1f},{cy:.1f}"}[kind]
    return (f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r}" style="fill:var(--{fill})"/>'
            f'<path d="{mark}" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>')


def words_for(spec, defaults):
    return {**defaults, **spec.get("legend", {})}


def label_parts(P, lines, xc, base, tone="front"):
    out = []
    for j, text in enumerate(lines):
        cls = f"{P}-main" if j == 0 else f"{P}-dim"
        if tone == "bad" and j == 0:
            cls += f" {P}-badt"
        out.append(f'<text class="{cls}" x="{xc:.0f}" y="{base + 16 * j}">{esc(text)}</text>')
    return out


# ---------------------------------------------------------------- sequence

def layout_sequence(spec, P):
    lanes = spec["lanes"]
    assert 2 <= len(lanes) <= 4, "2 to 4 lanes"
    step_x = (W - 220) / (len(lanes) - 1)
    lx = {l["id"]: 110 + i * step_x for i, l in enumerate(lanes)}
    box_w = min(180, step_x - 20)
    for l in lanes:
        fit([l["title"]], box_w - 12, f'lane {l["title"]!r} title', WORD["title"])
        fit([l.get("sub", "")], box_w - 2, f'lane {l["title"]!r} sub', 5.9)

    slots = []
    cursor, last_arrow = 96, None  # last_arrow: (y, to_x)
    used = {"front"}

    for st in spec["steps"]:
        newslot = not st.get("with_previous")
        if newslot:
            slots.append({"dim": [], "hl": [], "dot": None})
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
            parts = label_parts(P, st["label"], (x0 + x1) / 2, y - 14 - 16 * (n - 1), tone)
            parts.append(f'<line class="{P}-{tone}" x1="{x0:.0f}" y1="{y}" x2="{x1:.0f}" y2="{y}" marker-end="url(#{P}-{marker})"/>')
            if st.get("badge"):
                parts.append(badge(P, fx, y, st["badge"], tone))
            slots[k]["dim"].append("\n".join(parts))
            slots[k]["dot"] = (x0 + (6 if right else -6), x1 - x0 - (6 if right else -6), y, tone)
            used.add(tone)
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
                parts.append(badge(P, x, y + h / 2, st["badge"], tone))
            slots[k]["dim"].append("\n".join(parts))
            if tone in ("good", "bad"):
                used.add("note-" + tone)
            cursor = max(cursor, y + h + 22)

    H = int(cursor + 76)
    static = [f'<line class="{P}-life" x1="{lx[l["id"]]:.0f}" y1="72" x2="{lx[l["id"]]:.0f}" y2="{H - 52}"/>' for l in lanes]
    for l in lanes:
        x = lx[l["id"]]
        kind = "hot" if l.get("hot") else "box"
        static.append(f'<rect class="{P}-{kind}" x="{x - box_w / 2:.0f}" y="10" width="{box_w:.0f}" height="62" rx="10"/>'
                      f'<text class="{P}-ttl" x="{x:.0f}" y="36">{esc(l["title"])}</text>'
                      f'<text class="{P}-sub" x="{x:.0f}" y="56">{esc(l.get("sub", ""))}</text>')

    words = words_for(spec, {"front": "normal event", "back": "server to server", "bad": "failure mode",
                             "good": "what your handler must do"})
    legend = [("front", words["front"])]
    if "back" in used: legend.append(("back", words["back"]))
    if "bad" in used: legend.append(("bad", words["bad"]))
    if "note-bad" in used and "bad" not in used: legend.append(("note-bad", words["bad"]))
    if "note-good" in used: legend.append(("note-good", words["good"]))
    return {"H": H, "static": static, "slots": slots, "legend": legend}


# ----------------------------------------------------------------- anatomy

def layout_anatomy(spec, P):
    TX, TW = 14, 440          # nested boxes
    CX, CW = 484, 262         # callout column
    PAD, GAP = 12, 8
    static, order = [], []

    def place(n, x, y, w):
        head = 46 if n.get("sub") else 32
        idx = len(static)
        static.append(None)
        if n.get("check"):
            order.append(n)
        cy = y + head
        kids = n.get("children", [])
        for kid in kids:
            cy += place(kid, x + PAD, cy, w - 2 * PAD) + GAP
        h = (cy - GAP + PAD - y) if kids else head
        n["_box"] = (x, y, w, h)
        cls = f"{P}-hot" if n.get("hot") else (f"{P}-box" if x == TX else f"{P}-nest")
        t = f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="9"/>'
        t += f'<text class="{P}-ttlL" x="{x + 14}" y="{y + 21}">{esc(n["title"])}</text>'
        if n.get("sub"):
            t += f'<text class="{P}-subL" x="{x + 14}" y="{y + 38}">{esc(n["sub"])}</text>'
            fit([n["sub"]], w - 28, f'anatomy node {n["title"]!r} sub')
        static[idx] = t
        return h

    total = place(spec["root"], TX, 16, TW)
    assert order, "anatomy needs at least one node with `check`"
    slots, bottom, used = [], 0, set()
    for i, n in enumerate(order):
        bx, by, bw, bh = n["_box"]
        lines = n["check"]
        fit(lines, CW - 24, f'anatomy callout for {n["title"]!r}')
        h = 14 + 17 * len(lines)
        top = max(by + 17 - h / 2, bottom + 10)
        bottom = top + h
        mid, ny = top + h / 2, by + 17
        ex = 462 + (i % 4) * 4
        tone = n.get("tone", "plain")
        used.add(tone)
        cls = {"plain": "note", "good": "note-good", "bad": "note-bad"}[tone]
        dim = [f'<path class="{P}-conn" d="M{bx + bw},{ny:.0f} L{ex},{ny:.0f} L{ex},{mid:.0f} L{CX - 14},{mid:.0f}" marker-end="url(#{P}-m-front)"/>',
               f'<rect class="{P}-{cls}" x="{CX}" y="{top:.0f}" width="{CW}" height="{h}" rx="8"/>']
        dim += [f'<text class="{P}-nt" x="{CX + CW / 2:.0f}" y="{top + 21 + 17 * j:.0f}">{esc(t)}</text>' for j, t in enumerate(lines)]
        dim.append(badge(P, CX, mid, str(i + 1), tone if tone != "plain" else "front"))
        hl = [f'<rect class="{P}-hl" x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="9"/>']
        slots.append({"dim": ["\n".join(dim)], "hl": hl, "dot": None})
    H = int(max(16 + total, bottom) + 58)
    words = words_for(spec, {"plain": "what it carries", "good": "what is checked", "bad": "where it goes wrong"})
    legend = []
    if "plain" in used and len(used) > 1: legend.append(("note", words["plain"]))
    if "good" in used: legend.append(("note-good", words["good"]))
    if "bad" in used: legend.append(("note-bad", words["bad"]))
    return {"H": H, "static": static, "slots": slots, "legend": legend}


# -------------------------------------------------------------------- flow

def layout_flow(spec, P):
    GAPX, VGAP = 16, 58
    leaves = []

    def prep(n):
        lines = n["lines"]
        n["_w"] = max(110, int(max(len(t) for t in lines) * 6.8 + 26))
        n["_h"] = 14 + 17 * len(lines)
        kids = n.get("children", [])
        for c in kids:
            prep(c["node"])
        if kids:
            n["_sw"] = max(n["_w"], sum(c["node"]["_sw"] for c in kids) + GAPX * (len(kids) - 1))
        else:
            n["_sw"] = n["_w"]
            leaves.append(n)

    root = spec["root"]
    prep(root)
    assert 2 <= len(leaves) <= 6, "flow needs 2 to 6 leaves"
    TW = root["_sw"]
    Wd = max(W, int(TW + 28))
    assert Wd <= 940, f"flow tree too wide ({TW:.0f}px): shorten lines or drop a branch"
    levels = {}

    def depth_h(n, d=0):
        levels[d] = max(levels.get(d, 0), n["_h"])
        for c in n.get("children", []):
            depth_h(c["node"], d + 1)

    depth_h(root)
    ys, y = {}, 24
    for d in sorted(levels):
        ys[d] = y
        y += levels[d] + VGAP

    def place(n, left, d):
        n["_y"], n["_d"] = ys[d], d
        n["_cx"] = left + n["_sw"] / 2
        kids = n.get("children", [])
        if kids:
            span = sum(c["node"]["_sw"] for c in kids) + GAPX * (len(kids) - 1)
            x = left + (n["_sw"] - span) / 2
            for c in kids:
                place(c["node"], x, d + 1)
                x += c["node"]["_sw"] + GAPX

    place(root, 0, 0)  # measure first: an edge label right of the last drop may overhang the tree
    over = 0

    def overhang(n):
        nonlocal over
        for c in n.get("children", []):
            if c.get("edge"):
                over = max(over, c["node"]["_cx"] + 7 + len(c["edge"]) * 5.9 - TW)
            overhang(c["node"])

    overhang(root)
    Wd = max(Wd, int(TW + 2 * (over + 12)))
    assert Wd <= 940, f"flow tree too wide ({Wd}px with its edge labels): shorten lines or drop a branch"
    place(root, (Wd - TW) / 2, 0)
    edges, nodes, used = [], [], set()

    def edge_path(p, c):
        pb, ct = p["_y"] + p["_h"], c["_y"] - 3
        px, cx, ym = p["_cx"], c["_cx"], p["_y"] + p["_h"] + VGAP / 2
        d = f"M{px:.0f},{pb} L{px:.0f},{ct}" if abs(px - cx) < 1 else f"M{px:.0f},{pb} L{px:.0f},{ym:.0f} L{cx:.0f},{ym:.0f} L{cx:.0f},{ct}"
        return d, pb, ct, px, cx, ym

    def draw(n):
        for c in n.get("children", []):
            ch = c["node"]
            d, pb, ct, px, cx, ym = edge_path(n, ch)
            edges.append(f'<path class="{P}-edge" d="{d}" marker-end="url(#{P}-m-front)"/>')
            if c.get("edge"):  # label sits right of its own child's drop line, clear of the siblings' labels
                kids = n["children"]
                k = kids.index(c)
                if k + 1 < len(kids):
                    room = kids[k + 1]["node"]["_cx"] - cx - 14
                    assert len(c["edge"]) * 5.9 <= room, f'flow edge label too long for {room:.0f}px: {c["edge"]!r}'
                y = (pb + ct) / 2 + 4 if len(kids) == 1 else ct - 10
                edges.append(f'<text class="{P}-dimL" x="{cx + 7:.0f}" y="{y:.0f}">{esc(c["edge"])}</text>')
            draw(ch)
        kids = n.get("children", [])
        tone = n.get("tone", "plain")
        if kids:
            cls = f"{P}-box"
        else:
            cls = {"plain": "note", "good": "note-good", "bad": "note-bad"}[tone]
            cls = f"{P}-{cls}"
            used.add(tone)
        x = n["_cx"] - n["_w"] / 2
        t = f'<rect class="{cls}" x="{x:.0f}" y="{n["_y"]}" width="{n["_w"]}" height="{n["_h"]}" rx="8"/>'
        for j, line in enumerate(n["lines"]):
            klass = f"{P}-main" if (kids and j == 0) else f"{P}-nt"
            t += f'<text class="{klass}" x="{n["_cx"]:.0f}" y="{n["_y"] + 21 + 17 * j}">{esc(line)}</text>'
        nodes.append(t)

    draw(root)
    slots = []
    for leaf in leaves:
        path = []

        def find(n, acc):
            if n is leaf:
                path.extend(acc + [n])
                return True
            return any(find(c["node"], acc + [n]) for c in n.get("children", []))

        find(root, [])
        hl = []
        for a, b in zip(path, path[1:]):
            hl.append(f'<path class="{P}-hle" d="{edge_path(a, b)[0]}" marker-end="url(#{P}-m-front)"/>')
        for n in path:
            hl.append(f'<rect class="{P}-hl" x="{n["_cx"] - n["_w"] / 2:.0f}" y="{n["_y"]}" width="{n["_w"]}" height="{n["_h"]}" rx="8"/>')
        slots.append({"dim": [], "hl": hl, "dot": None})
    H = int(y - VGAP + 60)
    words = words_for(spec, {"front": "the path being traced", "plain": "conclusion", "good": "fine", "bad": "the problem"})
    legend = [("front", words["front"])]
    if "plain" in used and len(used) > 1: legend.append(("note", words["plain"]))
    if "good" in used: legend.append(("note-good", words["good"]))
    if "bad" in used: legend.append(("note-bad", words["bad"]))
    return {"H": H, "W": Wd, "static": edges + nodes, "slots": slots, "legend": legend}


# ------------------------------------------------------------------ stages

def layout_stages(spec, P):
    st = spec["stages"]
    n = len(st)
    assert 2 <= n <= 4, "2 to 4 stages"
    G = {2: 150, 3: 110, 4: 80}[n]
    bw = min(220, (W - 28 - (n - 1) * G) / n)
    x0 = (W - (n * bw + (n - 1) * G)) / 2
    top = 40
    maxl = max(len(s.get("lines", [])) for s in st)
    bh = 62 + (14 + 17 * maxl if maxl else 0)
    xs = [x0 + i * (bw + G) for i in range(n)]
    links = spec.get("links") or [{"from": i, "to": i + 1} for i in range(n - 1)]
    for lk in links:
        assert abs(lk["from"] - lk["to"]) == 1, "links connect neighbouring stages"
    used, slots, bottom = {"front"}, [], top + bh
    for i, s in enumerate(st):
        fit([s["title"]], bw - 12, f'stage {i} title', WORD["title"])
        tone = s.get("tone", "plain")
        cls = f"{P}-hot" if s.get("hot") else {"plain": f"{P}-box", "good": f"{P}-note-good", "bad": f"{P}-note-bad"}[tone]
        if tone in ("good", "bad"): used.add("note-" + tone)
        cx = xs[i] + bw / 2
        parts = [f'<rect class="{cls}" x="{xs[i]:.0f}" y="{top}" width="{bw:.0f}" height="{bh}" rx="10"/>',
                 f'<text class="{P}-ttl" x="{cx:.0f}" y="{top + 27}">{esc(s["title"])}</text>']
        if s.get("sub"):
            fit([s["sub"]], bw - 16, f'stage {i} sub')
            parts.append(f'<text class="{P}-sub" x="{cx:.0f}" y="{top + 47}">{esc(s["sub"])}</text>')
        fit(s.get("lines", []), bw - 16, f'stage {i} lines')
        for j, t in enumerate(s.get("lines", [])):
            parts.append(f'<text class="{P}-nt" x="{cx:.0f}" y="{top + 62 + 14 + 17 * j - 2}">{esc(t)}</text>')
        if s.get("badge"):
            parts.append(badge(P, xs[i], top, s["badge"]))
        dot = None
        for lk in links:
            if min(lk["from"], lk["to"]) != i:  # each link between i and i+1 belongs to stage i's slot
                continue
            fwd = lk["to"] > lk["from"]
            tone2 = lk.get("tone", "front")
            used.add(tone2)
            lo, hi = xs[i] + bw + 8, xs[i + 1] - 8
            y = top + 30 if fwd else top + 54
            a, b = (lo, hi) if fwd else (hi, lo)
            lab = lk.get("label", [])
            fit(lab, G - 6, "stage link label")
            base = (y - 6 - 16 * (len(lab) - 1)) if fwd else (y + 18)
            parts += label_parts(P, lab, (lo + hi) / 2, base, tone2)
            marker = {"front": "m-front", "back": "m-back", "bad": "m-bad"}[tone2]
            parts.append(f'<line class="{P}-{tone2}" x1="{a:.0f}" y1="{y}" x2="{b:.0f}" y2="{y}" marker-end="url(#{P}-{marker})"/>')
            bottom = max(bottom, base + 16 * len(lab) if not fwd else y)
            if dot is None or fwd:
                d = 6 if fwd else -6
                dot = (a + d, b - a - d, y, tone2)
        slots.append({"dim": ["\n".join(parts)], "hl": [], "dot": dot})
    H = int(bottom + 60)
    words = words_for(spec, {"front": "transition", "back": "server to server", "bad": "bad transition",
                             "good": "safe state", "bad_state": "state to avoid"})
    legend = [("front", words["front"])]
    if "back" in used: legend.append(("back", words["back"]))
    if "bad" in used: legend.append(("bad", words["bad"]))
    if "note-good" in used: legend.append(("note-good", words["good"]))
    if "note-bad" in used: legend.append(("note-bad", words["bad_state"]))
    return {"H": H, "static": [], "slots": slots, "legend": legend}


# ------------------------------------------------------------------ matrix

def layout_matrix(spec, P):
    cols, rows = spec["columns"], spec["rows"]
    assert 1 <= len(cols) <= 4 and 1 <= len(rows) <= 7, "matrix: 1 to 4 columns, up to 7 rows"
    RH = 216
    cw = (W - 14 - (RH + 20)) / len(cols)
    cxs = [RH + 20 + cw * i + cw / 2 for i in range(len(cols))]
    static = []
    for c, cx in zip(cols, cxs):
        fit([c["title"]], cw - 16, f'matrix column {c["title"]!r}', WORD["title"])
        static.append(f'<rect class="{P}-box" x="{cx - cw / 2 + 4:.0f}" y="10" width="{cw - 8:.0f}" height="62" rx="10"/>'
                      f'<text class="{P}-ttl" x="{cx:.0f}" y="36">{esc(c["title"])}</text>'
                      f'<text class="{P}-sub" x="{cx:.0f}" y="56">{esc(c.get("sub", ""))}</text>')
        if c.get("sub"): fit([c["sub"]], cw - 24, "matrix column sub")
    slots, y, used = [], 86, set()
    for r in rows:
        assert len(r["cells"]) == len(cols), f'matrix row {r["title"]!r}: one cell per column'
        maxl = max(len(c.get("text", [])) for c in r["cells"])
        rh = 22 + 26 + 15 * maxl + 8 if maxl else 56
        parts = [f'<rect class="{P}-row" x="10" y="{y}" width="{W - 20}" height="{rh}" rx="8"/>',
                 f'<text class="{P}-ttlL" x="24" y="{y + 26}">{esc(r["title"])}</text>']
        fit([r["title"]], RH - 20, f'matrix row {r["title"]!r}', 7.0)
        if r.get("sub"):
            fit([r["sub"]], RH - 20, "matrix row sub")
            parts.append(f'<text class="{P}-subL" x="24" y="{y + 44}">{esc(r["sub"])}</text>')
        for cell, cx in zip(r["cells"], cxs):
            if cell.get("mark"):
                used.add(cell["mark"])
                parts.append(glyph(P, cell["mark"], cx, y + 22))
            fit(cell.get("text", []), cw - 14, "matrix cell")
            for j, t in enumerate(cell.get("text", [])):
                parts.append(f'<text class="{P}-nt" x="{cx:.0f}" y="{y + 48 + 15 * j}">{esc(t)}</text>')
        slots.append({"dim": ["\n".join(parts)], "hl": [], "dot": None})
        y += rh + 8
    words = words_for(spec, {"good": "stops it", "partial": "partly", "bad": "does not stop it"})
    legend = [("mark-" + k, words[k]) for k in ("good", "partial", "bad") if k in used]
    return {"H": int(y + 44), "static": static, "slots": slots, "legend": legend}


LAYOUTS = {"sequence": layout_sequence, "anatomy": layout_anatomy, "flow": layout_flow,
           "stages": layout_stages, "matrix": layout_matrix}
NOUN = {"sequence": "step", "anatomy": "part", "flow": "path", "stages": "stage", "matrix": "row"}


# ------------------------------------------------------------------- shell

def kf(name, i, N, lo):
    s, e = i / N * 100, (i + 1) / N * 100
    if i == 0:
        return f"@keyframes {name}{{0%{{opacity:1}}{pct(e)}%{{opacity:1}}{pct(e + .01)}%,100%{{opacity:{lo}}}}}"
    return f"@keyframes {name}{{0%,{pct(s - .01)}%{{opacity:{lo}}}{pct(s)}%{{opacity:1}}{pct(e)}%{{opacity:1}}{pct(e + .01)}%,100%{{opacity:{lo}}}}}"


def build(spec):
    P = spec["prefix"]
    dur = spec.get("duration", 18)
    kind = spec.get("kind", "sequence")
    assert kind in LAYOUTS, f"unknown kind {kind!r}; one of {', '.join(LAYOUTS)}"
    L = LAYOUTS[kind](spec, P)
    slots, H, Wd = L["slots"], L["H"], L.get("W", W)
    N = len(slots)
    has_hl = any(s["hl"] for s in slots)
    anim = f".{P}-g,.{P}-pk" + (f",.{P}-h" if has_hl else "")

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
.{P}-nt{{fill:var(--body);font:12.5px {FONT};text-anchor:middle}}"""]
    if kind != "sequence":
        css.append(f""".{P}-nest{{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}}
.{P}-row{{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}}
.{P}-ttlL{{fill:var(--text);font:600 14px {FONT};text-anchor:start}}
.{P}-subL{{fill:var(--muted);font:12px {FONT};text-anchor:start}}
.{P}-dimL{{fill:var(--muted);font:12px {FONT};text-anchor:start}}
.{P}-dimR{{fill:var(--muted);font:12px {FONT};text-anchor:end}}
.{P}-conn{{stroke:var(--accent);stroke-width:1.5;fill:none}}
.{P}-edge{{stroke:var(--border-strong);stroke-width:1.75;fill:none}}
.{P}-hl{{fill:none;stroke:var(--accent);stroke-width:3}}
.{P}-hle{{stroke:var(--accent);stroke-width:3;fill:none}}""")
    css.append(f""".{P}-pk{{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:{dur}s;animation-timing-function:linear;animation-iteration-count:infinite}}
.{P}-pk.{P}-pkback{{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}}
.{P}-pk.{P}-pkbad{{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}}
.{P}-g{{opacity:{LO};animation-duration:{dur}s;animation-timing-function:linear;animation-iteration-count:infinite}}""")
    if has_hl:
        css.append(f".{P}-h{{opacity:0;animation-duration:{dur}s;animation-timing-function:linear;animation-iteration-count:infinite}}")
    hover = f"svg.{P}-flow:hover .{P}-g,svg.{P}-flow:hover .{P}-pk" + (f",svg.{P}-flow:hover .{P}-h" if has_hl else "")
    paused = ",".join(f".{P}-cb:checked ~ .{P}-box {sel}" for sel in anim.split(","))
    css.append(f"""{hover}{{animation-play-state:paused}}
.{P}-cb{{position:absolute;opacity:0;width:1px;height:1px;margin:0}}
.{P}-btn{{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px {FONT};cursor:pointer;user-select:none}}
.{P}-btn:hover{{background:var(--hover)}}
.{P}-cb:focus-visible + .{P}-btn{{outline:2px solid var(--accent);outline-offset:2px}}
.{P}-cb:checked + .{P}-btn .{P}-off,.{P}-cb:not(:checked) + .{P}-btn .{P}-on{{display:none}}
{paused}{{animation-play-state:paused}}
@media (prefers-reduced-motion:reduce){{.{P}-g{{animation:none;opacity:1}}.{P}-pk{{animation:none;display:none}}{f".{P}-h{{animation:none;opacity:0}}" if has_hl else ""}.{P}-btn{{display:none}}}}""")
    for i, s in enumerate(slots):
        rule = ""
        if s["dim"]:
            css.append(kf(f"{P}-g{i}", i, N, LO))
            rule += f".{P}-g{i}{{animation-name:{P}-g{i}}}"
        if s["dot"]:
            sx, ex = i / N * 100, (i + 1) / N * 100
            dx = s["dot"][1]
            css.append(f"@keyframes {P}-p{i}{{0%,{pct(sx - .01)}%{{opacity:0;transform:translateX(0)}}{pct(sx)}%{{opacity:1;transform:translateX(0)}}{pct(ex)}%{{opacity:1;transform:translateX({dx:.0f}px)}}{pct(ex + .01)}%,100%{{opacity:0;transform:translateX({dx:.0f}px)}}}}")
            rule += f".{P}-p{i}{{animation-name:{P}-p{i}}}"
        if s["hl"]:
            css.append(kf(f"{P}-h{i}", i, N, "0"))
            rule += f".{P}-h{i}{{animation-name:{P}-h{i}}}"
        css.append(rule)
    css.append("</style>")

    body = ["<defs>"]
    for name, var in (("front", "accent"), ("back", "muted"), ("bad", "bad")):
        body.append(f'<marker id="{P}-m-{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--{var})"/></marker>')
    body.append("</defs>")
    body += L["static"]
    for i, s in enumerate(slots):
        if s["dim"]:
            body.append(f'<g class="{P}-g {P}-g{i}">\n' + "\n".join(s["dim"]) + "\n</g>")
    for i, s in enumerate(slots):
        if s["hl"]:
            body.append(f'<g class="{P}-h {P}-h{i}">\n' + "\n".join(s["hl"]) + "\n</g>")
    for i, s in enumerate(slots):
        if s["dot"]:
            x0, dx, y, tone = s["dot"]
            extra = "" if tone == "front" else f" {P}-pk{tone}"
            body.append(f'<circle class="{P}-pk {P}-p{i}{extra}" cx="{x0:.0f}" cy="{y}" r="5.5"/>')

    rows, x = [[]], 40
    for lk, text in L["legend"]:
        lead = 30 if lk.startswith("note") else 24 if lk.startswith("mark") else 38
        w = lead + int(len(text) * 6.4)
        if rows[-1] and x + w > Wd - 24:
            rows.append([])
            x = 40
        rows[-1].append((lk, text, x, lead))
        x += w + 34
    base_y = H - 24
    H += 22 * (len(rows) - 1)
    for r, row in enumerate(rows):
        ly = base_y + 22 * r
        for lk, text, x, lead in row:
            if lk.startswith("note"):
                body.append(f'<rect class="{P}-{lk}" x="{x}" y="{ly - 8}" width="22" height="16" rx="4"/>')
            elif lk.startswith("mark"):
                body.append(glyph(P, lk[5:], x + 8, ly, 8))
            else:
                body.append(f'<line class="{P}-{lk}" x1="{x}" y1="{ly}" x2="{x + 30}" y2="{ly}"/>')
            body.append(f'<text class="{P}-dim" x="{x + lead}" y="{ly + 4}" style="text-anchor:start">{esc(text)}</text>')

    desc = re.sub(r"\s*The diagram highlights each .*$", "", spec["desc"].strip(), flags=re.S)  # the generator adds its own sentence
    noun = NOUN[kind]
    # A real checkbox styled as a button: keyboard operable (Tab, Space) with no script, so a
    # keyboard user can pause moving content (WCAG 2.2.2). Hover still pauses as well.
    svg = (
        '<div style="position:relative;margin:20px 0">\n'
        f'<input type="checkbox" id="{P}-pause" class="{P}-cb" />'
        f'<label for="{P}-pause" class="{P}-btn"><span class="{P}-off">Pause animation</span><span class="{P}-on">Play animation</span></label>\n'
        f'<div class="{P}-box" style="overflow-x:auto">\n'
        f'<svg class="{P}-flow" viewBox="0 0 {Wd} {H}" role="img" aria-labelledby="{P}-t {P}-d" '
        'style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">\n'
        f'<title id="{P}-t">{esc(spec["title"])}</title>\n'
        f'<desc id="{P}-d">{esc(desc)} The diagram highlights each {noun} in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>\n'
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
