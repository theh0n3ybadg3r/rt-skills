# rt-adapt (Codex adapter)

Codex entrypoint for the `rt-adapt` skill. Read `SKILL.md` in this directory and follow its Procedure verbatim; the logic and guidance live in `SKILL.md` and `references/`, shared with the Claude Code path.

Codex-specific delta: mid-engagement, keep it fast and local. Do not fan out subagents or run external research; the only network call is the catalog fetch in `validate.py`.

If this file and `SKILL.md` ever disagree, `SKILL.md` and the shared `references/` win.
