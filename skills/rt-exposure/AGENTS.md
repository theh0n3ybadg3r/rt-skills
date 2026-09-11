# rt-exposure (Codex adapter)

Codex entrypoint for the `rt-exposure` skill. Read `SKILL.md` in this directory and follow its Procedure verbatim; the logic, artifact schema, mapping guidance, and verifier personas live in `SKILL.md` and `references/`, shared with the Claude Code path. The bundled helpers (`skills/_shared/scripts/validate.py` for technique-ID and control-ID validation, `skills/_shared/scripts/pandoc_convert.py` to convert a `.docx` source, and `skills/_shared/scripts/pdf_convert.py` to convert a `.pdf` source) are plain Python and run identically here; `pandoc_convert.py` requires pandoc on PATH and `pdf_convert.py` requires the pdfplumber package.

Independent verification: Claude Code dispatches the named `rt-exposure-verifier` agent once per target (`dissection`, then `controls`). Codex has no named-agent equivalent, so run each verifier as a fresh `spawn_agent` or a new session that never saw the producing reasoning, following the same two personas. Honor the model boundary in SKILL.md step 11: a different model is preferred, but on an `engagement-sensitive` run stay on the authorized boundary. See `skills/_shared/references/degradation.md`.

If this file and `SKILL.md` ever disagree, `SKILL.md` and the shared `references/` win.
