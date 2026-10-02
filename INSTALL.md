# Install

Two separate things, and you may only want the first:

1. **Running courses** needs nothing but Python 3. No install step.
2. **Generating courses with an AI tool** is optional — the format is plain
   files, so you can write a course by hand with no assistant at all.

## 1. Run it

```bash
git clone https://github.com/eldestar/academy-of-things.git
cd academy-of-things
python3 serve.py
```

Open http://localhost:8000. Start with **Example Course** — it teaches the
format by being written in it.

`file://` will not work. The engine fetches `manifest.json` and lesson files,
which browsers block on local files. That is the only reason `serve.py`
exists.

Progress lives in your browser's `localStorage`. Nothing leaves your machine,
there are no accounts, and clearing site data resets it.

## 2. Wire up an AI tool

Pick the row that matches what you use. All of them do the same job: give the
assistant the format spec and the authoring rules.

### Any assistant, no setup

Open `adapters/PROMPT.md` and follow the two-paste instruction at the top.
This works in any chat interface and is the right starting point if you are
not sure.

### Claude

The two skills in `skills/` are the fullest version — they carry the complete
authoring rules and trigger on their own in conversation.

- **Claude Code**: copy both skill folders into your personal skills
  directory (commonly `~/.claude/skills/`), or into `.claude/skills/` inside
  a project to scope them to it.
- **Claude desktop / claude.ai**: add them wherever your plan surfaces custom
  skills.

Paths and availability differ by surface and plan, so check Anthropic's
current docs if a skill does not appear. Either way the skills assume this
repo is checked out — they write into `courses/`.

### Codex and other agent CLIs

Append `adapters/AGENTS.md` to your project's `AGENTS.md`.

### Cursor

```bash
mkdir -p .cursor/rules && cp adapters/cursor/academy-of-things.mdc .cursor/rules/
```

### GitHub Copilot

```bash
mkdir -p .github && cp adapters/copilot/copilot-instructions.md .github/
```

## 3. Make a course

```bash
./scripts/new-course.sh okta-basics "Okta Basics" "For a new IT hire"
python3 serve.py
```

Or ask your assistant: *"add a course on <subject> to the academy."*

See `FORMAT.md` for the schema and `AUTHORING.md` for what makes a course
worth finishing.

## 4. Share a single course

```bash
./scripts/package-course.sh okta-basics
# -> dist/okta-basics.zip
```

That zip stands alone: the engine is vendored in, and it runs with
`python3 serve.py` from inside the unzipped folder. Hand it to someone who
has never seen this repo, or drop one you were given into `courses/` and it
appears next time you start the server.
