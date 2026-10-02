# Adapters

The course format is the real interface — plain folders, Markdown and JSON.
Any assistant that can write files can write a course. These are shortcuts,
not requirements.

| File | For |
| --- | --- |
| `PROMPT.md` | Any chat assistant, no setup. Paste `FORMAT.md`, then this, then your subject. |
| `AGENTS.md` | Codex and agent CLIs that read `AGENTS.md`. |
| `cursor/academy-of-things.mdc` | Cursor. Copy into `.cursor/rules/`. |
| `copilot/copilot-instructions.md` | GitHub Copilot. Copy into `.github/`. |
| `claude/` | See `INSTALL.md` — Claude gets the two full skills in `skills/`. |

Claude is the only one that gets the skills, because skills are a Claude
feature. Everything else gets the same instructions as plain context, which
works nearly as well since the format is simple enough to hold in a prompt.
