#!/usr/bin/env python3
"""Check that every diagram in a lesson matches its spec.

    python3 scripts/check-diagrams.py                          # every course
    python3 scripts/check-diagrams.py authentication-protocols # one course
    python3 scripts/check-diagrams.py --fix                    # also rewrite drifted blocks from their specs

For each lesson file (lesson.md, lesson.beginner.md, lesson.advanced.md) and each
<!-- diagram:ID --> block in it, the spec is courses/<slug>/diagrams/ID.<level>.json
(falling back to ID.json for the intermediate file or an unvaried diagram). The
block must equal what the generator makes from that spec today, so a hand edit or
a changed spec that was never re-inserted shows up as drift. Also checks: markers
paired, an id appears once per file, a css prefix is used once per file, every spec
file is used by some lesson. Exits 1 on any problem.
"""
import glob, importlib.util, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mod = importlib.util.spec_from_file_location("diagram", os.path.join(ROOT, "scripts", "diagram.py"))
diagram = importlib.util.module_from_spec(mod)
mod.loader.exec_module(diagram)

BLOCK = re.compile(r"<!-- diagram:([\w-]+) -->.*?<!-- /diagram:\1 -->", re.S)
FIX = "--fix" in sys.argv
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
problems, used_specs, checked = [], set(), 0


def level_of(path):
    m = re.fullmatch(r"lesson(?:\.(beginner|advanced))?\.md", os.path.basename(path))
    return m.group(1) if m else None


for course in sorted(glob.glob(os.path.join(ROOT, "courses", "*"))):
    slug = os.path.basename(course)
    if ARGS and slug not in ARGS:
        continue
    for path in sorted(glob.glob(os.path.join(course, "lessons", "*", "lesson*.md"))):
        if not level_of(path) and os.path.basename(path) != "lesson.md":
            continue
        rel = os.path.relpath(path, ROOT)
        text = open(path, encoding="utf-8").read()
        opens, closes = len(re.findall(r"<!-- diagram:", text)), len(re.findall(r"<!-- /diagram:", text))
        if opens != closes or opens != len(BLOCK.findall(text)):
            problems.append(f"{rel}: unpaired or nested diagram markers")
        seen_ids, seen_prefixes = set(), set()
        for m in BLOCK.finditer(text):
            did, block = m.group(1), m.group(0)
            checked += 1
            if did in seen_ids:
                problems.append(f"{rel}: diagram id {did!r} appears twice")
            seen_ids.add(did)
            level = level_of(path)
            candidates = ([f"{did}.{level}.json"] if level else []) + [f"{did}.json"]
            spec_path = next((os.path.join(course, "diagrams", c) for c in candidates
                              if os.path.exists(os.path.join(course, "diagrams", c))), None)
            if not spec_path:
                problems.append(f"{rel}: no spec for diagram {did!r} (looked for {', '.join(candidates)} in diagrams/)")
                continue
            used_specs.add(spec_path)
            spec = json.load(open(spec_path, encoding="utf-8"))
            if spec["id"] != did:
                problems.append(f"{os.path.relpath(spec_path, ROOT)}: id {spec['id']!r} does not match its use as {did!r}")
            if spec["prefix"] in seen_prefixes:
                problems.append(f"{rel}: css prefix {spec['prefix']!r} used by two diagrams")
            seen_prefixes.add(spec["prefix"])
            try:
                fresh = diagram.build(spec)[0]
            except (AssertionError, KeyError) as e:
                problems.append(f"{os.path.relpath(spec_path, ROOT)}: does not build: {e!r}")
                continue
            if fresh != block and FIX:
                text = text.replace(block, fresh)
                open(path, "w", encoding="utf-8").write(text)
                print(f"fixed {rel}: {did}")
            elif fresh != block:
                problems.append(f"{rel}: diagram {did!r} differs from {os.path.relpath(spec_path, ROOT)}; re-run scripts/diagram.py --insert")
    for spec_path in sorted(glob.glob(os.path.join(course, "diagrams", "*.json"))):
        if spec_path not in used_specs and not (ARGS and slug not in ARGS):
            problems.append(f"{os.path.relpath(spec_path, ROOT)}: spec is not used by any lesson")

print(f"checked {checked} diagram blocks")
for p in problems:
    print("PROBLEM", p)
sys.exit(1 if problems else 0)
