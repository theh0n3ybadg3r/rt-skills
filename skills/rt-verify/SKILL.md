---
name: rt-verify
description: >-
  Independent-context reviewer for one section of the engagement artifact. Re-derives every reviewed item (a scoping objective, a threat-profile technique or actor, a planning step, or a report finding) from the artifact, the cited sources, and live catalog data (never the producer's reasoning), judges whether each objective is an outcome, each quote supports its mapping, each step is actor-consistent, and each finding traces to the record, and gates the artifact fail-closed via the validate helper. Cross-cutting; it writes the #verification block (section 7).
---

# rt-verify

The trust gate. It catches wrong, unsupported, or unverifiable output before it is trusted, so it must **run in a fresh context**: a separate subagent (Claude Code) or a separate invocation (Codex). Under Claude Code, dispatch the `rt-engagement-verifier` agent (install it with `make install-agents`); it re-derives the target's review objects in its own context and returns the composed `#verification` block, which this skill then writes and gates. Under Codex, use a fresh `spawn_agent` or a new session. See `skills/_shared/references/degradation.md` for the fallback when no subagent primitive exists. Never run `rt-verify` in the context that produced the output; a generator grading its own work is the failure mode this skill prevents.

Independence here is **procedural, not organizational**: the red team and the tested function share a reporting line, so the guarantee is a separate drafter, a fresh verifying context that never saw the producer's reasoning, and a report the tested function cannot edit (its own account is captured separately as the Blue Team Account). See `degradation.md`.

Shared assets:

- Artifact schema (section 7, `#verification`): `skills/_shared/references/red-team-engagement-v3.md`.
- ID rules and name matching for the offensive frameworks (`attack`/`atlas`/`aadapt`) and the control frameworks: `skills/_shared/references/framework-mapping.md`.
- The one bundled validation helper: `skills/_shared/scripts/validate.py` (deterministic id/name validation and the fail-closed ready gate).
- The reviewer persona covering all four targets: `references/personas/review.md`.
- Writing standard for any prose that reaches a reader: `skills/_shared/references/writing-style.md`.

**Pick the target.** `rt-verify` reviews one section per run: `target` is one of `scoping` (Scoping Document, section 1), `threat-profile` (Threat Profile Brief, section 2), `planning` (Planning Pack, section 3), or `report` (Engagement Report, section 5). You did not produce the section; treat every item as a claim to check. Adopt the persona in `references/personas/review.md`, which states the per-target checks and the adversarial-skeptic default.

Temp files: write any temp JSON the helper needs to a scratch path **outside** `engagements/` (so engagement content never lands in the artifact tree), and delete it after. Each temp entry is `{"id": <id>, "framework": <attack|atlas|aadapt>, "name": <official name, optional>}`; the helper also accepts `technique_id` in place of `id`.

## A. Re-derive the review objects (per target)

Re-derive each item; never reuse the producer's `script_verdict`. The per-target review objects and their checks are in `references/personas/review.md`. In summary:

- `scoping`: for each objective, that it is an outcome (not a technique), its `success_criterion` is measurable, it traces to a `target_crown_jewel` in `scoping_summary.crown_jewels` and to a validated `business_impact`, and its `systemic_relevance` is recorded. (No deterministic `id_name`; the judgment is the whole check.)
- `threat-profile`: for each technique, run `id_name`, confirm each citation `quote` resolves verbatim at its locator, judge whether the quote supports _this_ technique (`yes`/`no`/`unclear`), and confirm an inferred mapping is marked `sourced: "inference"`; for each actor, confirm the `intelligence_basis` quote resolves and is real, not plausible-sounding.
- `planning`: for each step, run `id_name`, confirm the step is `actor_consistent` or justified from documented tradecraft, confirm the path carries a `branch_if_blocked`, and for a transaction-adjacent objective confirm a `live_execution_safeguard` is specified and `safeguard_verified == true`.
- `report`: for each finding, confirm the narrative is supported by the execution record and evidence, it traces to the log, and it names no individual (and where the finding carries a `control_domain` mapping, run `id_name` on that control id); plus the report-level check that the `blue_team_account` was `captured_before_disclosure` (or its `exception` honestly records what else it measures).

**Deterministic `id_name`** (where the item has an id): write the item(s) as a JSON list and run `python3 skills/_shared/scripts/validate.py --entries <tmp.json> --refresh`. `--refresh` forces a fresh catalog fetch so verification never reuses the producer's cache. Take the verdict.

**Combine (fail-closed), per item:** an item is `confirmed` only when its deterministic `id_name` is `confirmed` (where it has one) AND its required citations resolve AND every persona judgment for the target is `yes`. `id_name == unverifiable` (catalog unreachable) -> **unverifiable**; `id_name == refuted` -> **refuted**; a required quote that does not resolve -> **unverifiable**; any persona judgment that is not `yes` -> **refuted**; otherwise -> **confirmed**.

## B. Write and gate

This skill (the invoking context), not the verifier agent, owns the write and the gate. When the `rt-engagement-verifier` agent returns a composed `#verification` block, take its verdicts as-is and do this section.

Write one verdict per reviewed item into a `#verification` block carrying the `target`. **Section 7 holds one block per target**: append a new block, and never overwrite another target's block (each target's gate result is needed later, for example by `rt-report`). Record `catalog_provenance` (the catalog versions used, from `python3 skills/_shared/scripts/validate.py --catalog-info`) in the block for the audit trail, and record `producer_model` / `verifier_model` / `boundary` per section C.

Do not hand-type `ready`. Write an ids file listing every reviewed item id, then compute the gate: `python3 skills/_shared/scripts/validate.py --gate <the #verification block> --expect-ids <ids.json>`. It returns `ready` only when there is at least one verdict, every verdict is `confirmed`, and the verdicts cover every expected id (so dropping a failing item cannot vacuously pass). Any `refuted`/`unverifiable` item, a missing item, or an empty set means `ready: false`; catalog unreachable makes `id_name` unverifiable, so the item is unverifiable and the artifact is gated. Never mark ready to keep moving.

Report the gate result plus a one-line reason per non-confirmed item.

## C. Model-diverse verification

Record `producer_model`, `verifier_model`, and `boundary` in the block, per the model-diverse rule in `degradation.md`:

- Run the verifier on a different model tier than the producer where the data class allows, for uncorrelated errors.
- The fresh context still receives the source, so on an `engagement-sensitive` run it stays on the **same authorized model boundary** (a different vendor/host egresses source content across an unauthorized boundary and is a blocker, not a fallback). On a `public-reference` run, cross-model and cross-vendor verification is permitted and preferred for independence.
- If the harness cannot pin a per-agent model and producer and verifier collide on the same model, that is a logged reduced-independence note (`boundary: same-model-reduced-independence`), not a failure: a separate fresh context still satisfies the fail-closed gate.
