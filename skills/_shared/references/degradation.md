# Cross-platform degradation rules

The skills are authored once (portable `references/*.md` + stdlib Python) and run on Claude Code and Codex. Where a platform lacks a capability, degrade as follows, never silently drop a guarantee.

## Independent verification (load-bearing, KTD4)

A verifier must not see the producer's reasoning. This applies to `rt-verify` (over the engagement artifact) and to `rt-exposure`'s two verifiers (over a standalone exposure assessment).

1. **Preferred:** dispatch it as a fresh subagent/worker with its own context, passing only the artifact, the source advisory, and script access. Under Claude Code this is the `rt-engagement-verifier` agent (for `rt-verify`) or the `rt-exposure-verifier` agent (for `rt-exposure`, dispatched once per target), installed with `make install-agents`; under Codex it is `spawn_agent`.
2. **Fallback (no subagent primitive):** run the verifier as a separate top-level invocation in a new session, explicitly instructed to ignore any prior producing discussion.
3. **Never** run production and verification in one continuous context. If a platform truly cannot provide a second context, stop and report it as a blocker, do not run both sides in one context and call it verified. Disclose any degradation in one line.
4. **Respect the data class when choosing the verify context.** The fresh context still receives the source, so on an `engagement-sensitive` run it must stay on the **same authorized model boundary**. Do not fall back to a different vendor/host (e.g. Codex when the run was authorized on Claude, or vice versa), that egresses source content across an unauthorized boundary; treat a different-host-only second context as a blocker for engagement-sensitive input. On a `public-reference` run (the common case for `rt-exposure`, which reads public CVEs and advisories) source-content egress is permitted, so cross-model and cross-vendor verification is allowed and is preferred for independence: `rt-exposure` runs its verifiers on a different model than the producer where it can, and records `producer_model` / `verifier_model` / `boundary` in each verification block. A same-model collision is a logged reduced-independence note, not a failure; two independent fresh contexts still satisfy the fail-closed gate.

## Model tiering

- Cheap/extraction tier: reading sources and resolving quotes (mechanical).
- Mid tier: technique extraction and mapping in `rt-intel`.
- Capable tier: the `rt-verify` semantic "quote supports mapping" judgment.
- **No per-agent model selection?** Run everything on the inherited session model. Cost control then comes from the deterministic-script split (KTD2), not from tiering.

## The one helper

The `validate` helper (`skills/_shared/scripts/validate.py`) is stdlib-only Python 3 and runs identically on both platforms. It is the only bundled validation code the skills run: id and name validation against the offensive frameworks (ATT&CK / ATLAS / AADAPT) and the defensive control frameworks (NIST CSF / NIST 800-53) used for control-domain mapping, plus the deterministic ready-gate (`--gate`). Everything else, including reading and quoting sources, is done by the agent following the skill instructions. (The document converters `pandoc_convert.py` / `pdf_convert.py` are separate ingest helpers, not validation code.)

## Devin

Deferred. The markdown + Python core ports without change; only a Devin-specific entrypoint (equivalent to `AGENTS.md`) would be added later.
