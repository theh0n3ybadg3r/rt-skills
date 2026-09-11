---
name: rt-emulate
description: >-
  Phase 3 (Attack Planning) of the threat-informed red team methodology. Turns a signed Scoping Document and the Phase 2 Threat Profile into the Engagement Planning Pack Part A: a hypothesized attack path per objective, each step a validated ATT&CK/ATLAS/AADAPT technique that is actor-consistent, with detection risk, a branch if blocked, and a marked assumption. It references (does not author) the human-owned infrastructure plan, procurement plan, signed Rules of Engagement, and legal/third-party authorizations, records the Gate 2 (RoE) sign-off, validates every technique id, and hands off to rt-verify. Design and decision support only; it executes nothing.
---

# rt-emulate

Phase 3, Attack Planning. It turns the signed objectives and the Threat Profile into the Engagement Planning Pack Part A, the hypothesized attack path per objective, and records the Gate 2 sign-off that authorizes execution. The attack path is a planning hypothesis, not an execution script. This skill designs and supports the decision; it executes nothing and never touches a target.

Shared assets:

- Artifact schema (`#planning`, section 3): `skills/_shared/references/red-team-engagement-v3.md`. It consumes section 1 (`#scoping`) and section 2 (`#threat-profile`).
- Framework ID rules and the taxonomy-selection rule: `skills/_shared/references/framework-mapping.md`.
- The one bundled helper: `skills/_shared/scripts/validate.py`.
- Guidance: `references/attack-path.md` (the Part A step structure), `references/planning-pack-mapping.md` (how `#planning` maps to the Engagement Planning Pack and what is human-owned), `references/ctid-library.md` (an optional aid for building the already-selected actor's tradecraft into a path).

## Procedure

1. **Check the inputs.** Read sections 1 (`#scoping`) and 2 (`#threat-profile`) of `engagements/<engagement-id>/engagement.md`. Both must be present, and the `#scoping` `gate1_sign_off` must be complete (all four approvers, Gate 1 cleared). If either section is missing, or Gate 1 is not signed, stop and tell the operator which is missing; write nothing. Note `data_class`: on an `engagement-sensitive` run keep source content local (the `validate` helper fetches only the public catalog and sends nothing about the engagement).

2. **Build the attack path per objective (Part A).** For each objective in `#scoping`, construct an ordered `steps` list. Each step (see `references/attack-path.md`) carries:
   - `technique_id` + `framework` (`attack` | `atlas` | `aadapt`, chosen by the target-type rule in `framework-mapping.md`), a real technique validated in step 5.
   - `actor_consistent`: true when the technique is in `#threat-profile` for this objective's actor. A step whose technique is not in `#threat-profile` must be justified from the actor's documented tradecraft; an unjustified off-profile step is a defect.
   - `action`: what the operator does, at a level a red teamer can execute, not a copy-paste exploit.
   - `detection_risk`: `high` | `medium` | `low`.
   - `detects_what`: what would detect this step and at what stage. This feeds the report's detection question, so make it concrete.
   - `branch_if_blocked`: the alternative if the step is blocked or detected. A path with no alternative is under-planned.
   - `assumption`: what the step assumes, or `null`. Marked assumptions carry to the pack's assumptions register.

   Then set `terminal_action` (the action that satisfies the objective's `success_criterion`). For a transaction-adjacent objective (payment, clearing, settlement, or any path that could move value), set `live_execution_safeguard` (the safeguard that bounds live execution) and `safeguard_verified` (true only when it has been technically verified with the asset owner, not merely documented).

3. **Reference the human-owned artifacts; do not author them.** Record references in `human_owned` and `authorizations`. These are human deliverables this section points at:
   - `infrastructure_plan_ref`: Planning Pack Part B (C2, redirectors, domains and aging, phishing infrastructure, payload testing, hardware), including the **B8 teardown inventory**, the authoritative list Phase 4 cleanup and Phase 6 decommission reconcile against.
   - `procurement_plan_ref`: Part C, where procurement outside the annual budget is needed.
   - `rules_of_engagement_ref`: the signed Rules of Engagement. The RoE carries execution authorization, the Control Group membership, and the SOC-blind status. There is no separate Control Group Terms of Reference.
   - `authorizations.legal`: the legal authorization-letter reference, required where `#scoping.scoping_summary.physical_operations` is true.
   - `authorizations.third_party`: the written third-party authorization, required where any path touches a system in `#scoping.scoping_summary.third_party_systems_in_path`.

4. **Record and check Gate 2 (RoE sign-off).** Populate `gate2_sign_off` from the recorded human sign-off. Gate 2 is non-exceptable. It clears only when all of these hold; report any that do not, and do not present the plan as execution-ready while any is unmet:
   - all four approvers present: `stakeholder`, `operations_lead`, `assessment_lead`, and `ciso` (the CISO may approve asynchronously, but the gate does not clear without the CISO);
   - `gate2_sign_off.legal` present where physical operations are in scope;
   - `authorizations.legal` present where `physical_operations` is true;
   - `authorizations.third_party` present where `third_party_systems_in_path` is non-empty;
   - `safeguard_verified == true` for every path that carries a `live_execution_safeguard`. A documented-but-unverified safeguard does not satisfy the gate.

5. **Validate every step's technique id.** Collect each step's technique across all paths as a JSON list of `{"technique_id": ..., "framework": ..., "name": ...}` (the helper accepts `technique_id`) and write it to a scratch path **outside** `engagements/`. Run `python3 skills/_shared/scripts/validate.py --entries <tmp.json>`, fix or drop any refuted id (correct the id/name, or drop the step and re-plan its branch), then delete the temp file. A step whose id cannot be confirmed does not go into the path.

6. **Write `#planning` (section 3) and hand off.** Write only section 3; never modify another skill's block. See `references/planning-pack-mapping.md` for how the section maps to the Engagement Planning Pack Parts A/B/C and the RoE. Report per-objective step counts, which Gate 2 conditions are met or outstanding, and hand off to `rt-verify` (target `planning`).

## Boundaries

- **Executes nothing.** rt-emulate is design and decision support for a human operator. It plans a path and records decisions; the human operator decides and executes under the signed RoE.
- **Every step validates and is actor-consistent.** Each `technique_id` passes the `validate` helper and is either in `#threat-profile` or justified from the actor's documented tradecraft. Each path carries at least one `branch_if_blocked` and marks its assumptions.
- **The Gate 2 safety gates are non-exceptable.** The four approvers, the legal and third-party authorizations where they apply, and a verified safeguard for every transaction-adjacent path are conditions of the gate, not preferences.
- **The B8 inventory is the authoritative teardown list.** It is human-owned (Part B) and referenced here; Phase 4 cleanup reconciles against it. This section references it, it does not reproduce it.
- Build the path with the adversary mindset in `skills/_shared/references/adversary-mindset.md` (reason from the objective backward, faithful to documented tradecraft, bounded by the RoE). Prose you author here is written to the deliverable standard in `skills/_shared/references/writing-style.md`.
