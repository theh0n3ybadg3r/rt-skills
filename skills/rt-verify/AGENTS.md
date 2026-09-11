# rt-verify (Codex adapter)

Codex entrypoint for the `rt-verify` skill. Read `SKILL.md` in this directory and follow its Procedure verbatim; the logic and the reviewer persona live in `SKILL.md` and `references/`, shared with the Claude Code path.

**Independence is mandatory, and procedural.** Start `rt-verify` in a _new_ Codex session / agent that has not seen the producer's reasoning; pass it only the artifact, the cited sources, and access to the `validate` helper. If you cannot spawn a separate context, follow the degradation fallback in `skills/_shared/references/degradation.md`; do not silently run it in the producer's context. (The Claude Code path names this fresh context: the `rt-engagement-verifier` agent. Codex has no equivalent named agent, so use `spawn_agent` or a new session.) Record `producer_model` / `verifier_model` / `boundary` per the model-diverse rule in `degradation.md`; on an `engagement-sensitive` run the fresh context stays on the same authorized model boundary.

If this file and `SKILL.md` ever disagree, `SKILL.md` + the shared `references/` win.
