#!/usr/bin/env python3
"""Blind answerability test for a course: can a reader get every quiz question right from the lesson alone?

    python3 scripts/quiz-coverage.py strip <slug> <outdir>      # answer-key-free copies of every quiz
    python3 scripts/quiz-coverage.py score <slug> <answers.json> # score a reviewer's blind answers

Workflow (see "Quiz coverage" and Build order in the course-builder skill):
  1. `strip` writes <outdir>/<lesson-id>/questions[.<level>].json holding only n, stem and options.
  2. A reviewer who sees ONLY a stripped file and the matching lesson text answers every question and
     writes answers.json shaped {"<lesson-id>" or "<lesson-id>.<level>": [{n, choice, support,
     needs_outside, confidence, note}, ...]}. `support` is an exact quote from the lesson, or the
     literal string NOT IN LESSON. `choice` is the 0-based option index. confidence is high|medium|low.
  3. `score` compares the choices to the real keys and flags: wrong answers, answers that needed outside
     knowledge, low or medium confidence, NOT IN LESSON, and supports that do not appear in the lesson
     text (a paraphrase or a computed number is a weak support). Exit status is 1 if anything is flagged.
Close each flag by adding the fact to the lesson (verified) or rewriting the question, then re-run.
"""
import glob, json, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def course_dir(slug):
    d = os.path.join(ROOT, "courses", slug)
    if not os.path.isdir(d):
        sys.exit(f"no such course: {slug}")
    return d


def lesson_text(cdir, lid, level):
    base = os.path.join(cdir, "lessons", lid)
    for name in ([f"lesson.{level}.md"] if level else []) + ["lesson.md"]:
        p = os.path.join(base, name)
        if os.path.exists(p):
            return open(p, encoding="utf-8").read()
    return ""


def quizzes(cdir):
    """Yield (key, lesson_id, level, path) for quiz.json and quiz.<level>.json of every lesson."""
    for p in sorted(glob.glob(os.path.join(cdir, "lessons", "*", "quiz*.json"))):
        lid = os.path.basename(os.path.dirname(p))
        m = re.fullmatch(r"quiz(?:\.([a-z0-9-]+))?\.json", os.path.basename(p))
        level = m.group(1) if m else None
        yield (f"{lid}.{level}" if level else lid), lid, level, p


def norm(s):
    s = re.sub(r"[`*_‘’“”\"']", "", s)
    s = s.replace("—", "-").replace("–", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


def strip(slug, outdir):
    cdir, n = course_dir(slug), 0
    for key, lid, level, p in quizzes(cdir):
        qs = json.load(open(p, encoding="utf-8"))["questions"]
        out = os.path.join(outdir, lid)
        os.makedirs(out, exist_ok=True)
        name = f"questions.{level}.json" if level else "questions.json"
        json.dump({"questions": [{"n": i + 1, "stem": q["stem"], "options": q["options"]} for i, q in enumerate(qs)]},
                  open(os.path.join(out, name), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        n += 1
    print(f"wrote {n} stripped quizzes under {outdir}")


def score(slug, answers_path):
    cdir = course_dir(slug)
    answers = json.load(open(answers_path, encoding="utf-8"))
    keys = {k: (lid, level, p) for k, lid, level, p in quizzes(cdir)}
    total = flagged = 0
    for key, items in answers.items():
        if key not in keys:
            sys.exit(f"answers refer to unknown quiz: {key}")
        lid, level, p = keys[key]
        qs = json.load(open(p, encoding="utf-8"))["questions"]
        if len(items) != len(qs):
            sys.exit(f"{key}: {len(items)} answers for {len(qs)} questions")
        text = norm(lesson_text(cdir, lid, level))
        for it in items:
            total += 1
            q, why = qs[it["n"] - 1], []
            if it["choice"] != q["correct_index"]:
                why.append("WRONG")
            if it.get("needs_outside"):
                why.append("needs outside knowledge")
            if it.get("confidence") != "high":
                why.append(f"confidence {it.get('confidence')}")
            sup = (it.get("support") or "").strip()
            if sup == "NOT IN LESSON":
                why.append("NOT IN LESSON")
            else:
                parts = [x for x in re.split(r"\s*(?:\.\.\.|…|\|)\s*", sup) if len(x.strip()) > 12] or [sup]
                if not any(norm(x) in text for x in parts):
                    why.append("support quote not found in lesson")
            if why:
                flagged += 1
                print(f"- {key} Q{it['n']}: {', '.join(why)} | {it.get('note', '')[:140]} | {q['stem'][:90]}")
    print(f"questions {total} | flagged {flagged}")
    sys.exit(1 if flagged else 0)


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "strip":
        strip(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 4 and sys.argv[1] == "score":
        score(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
