---
name: rt-adapt
description: >-
  Phase 4 (Execution and Live Testing) of the threat-informed red team methodology. Under a signed Scoping Document and a signed Rules of Engagement (Gate 2), it confirms the entry criteria, structures and appends the contemporaneous engagement log as decision support, and proposes ranked ATT&CK/ATLAS/AADAPT variant options when a technique is blocked or detected. The human operator decides and executes; rt-adapt executes nothing and never fabricates the log. It records detection observations, deconfliction, deviations, disclosures, target cleanup, attacker infrastructure, and recovered secrets (never the value), and writes the Execution Record as the #execution block (section 4). Fast and local-only for OPSEC and latency.
---

# rt-adapt

Phase 4, Execution and Live Testing. During live execution against the target, this skill structures the contemporaneous engagement log, proposes a next move when a technique is blocked or detected, and records the target cleanup at conclusion. It writes the Execution Record as the `#execution` block (section 4). The human operator stays on the trigger: rt-adapt proposes and records, the operator decides and executes. It executes nothing.

The log is a **live human record**. rt-adapt structures it and appends entries as they happen; it never fabricates, reconstructs, or back-fills a log after the fact.

Shared assets:

- Artifact schema (`#execution`, section 4): `skills/_shared/references/red-team-engagement-v3.md`. It consumes section 1 (`#scoping`, Gate 1) and section 3 (`#planning`, Gate 2).
- Framework ID rules: `skills/_shared/references/framework-mapping.md`.
- The one bundled helper: `skills/_shared/scripts/validate.py`.
- Guidance: `references/refinement.md` (the ranked-variant decision-support method), `references/execution-record.md` (the Part 1 log fields, Part 2 cleanup, and the append-only / no-fabrication rule).

## Procedure

1. **Confirm the entry gate before the first action.** Read sections 1 (`#scoping`) and 3 (`#planning`) of `engagements/<engagement-id>/engagement.md`. Both must be present with a signed `#scoping` (Gate 1, all four approvers) and a `#planning` whose `gate2_sign_off` carries all four approvers, including the CISO (Gate 2, the RoE sign-off that authorizes execution). A `#planning` missing any Gate 2 approver is not authorized; stop. Then confirm `entry_criteria_confirmed` all true, live: `roe_signed` (Gate 2 cleared), `safeguards_active` at start, `soc_blind` (this is a red team operation), and `c2_separated`. If any input is missing or any entry criterion is not met, stop and tell the operator which; write nothing. Note `data_class`: mid-engagement is typically `engagement-sensitive`, so keep everything local (the only external call is the catalog fetch in step 4).

2. **Append log entries as the operator acts (append-only).** For each action the operator reports, append one entry to `log` with `timestamp`, `operator`, `objective_id`, `step` (the planning-pack step this executes, or `null`), `action`, `target`, `tooling`, `outcome` (`success` | `blocked` | `detected`), and, where they apply, `state_change`, `artifact_introduced` (carried to cleanup in step 5), and `safeguard_state` (for a transaction-adjacent action). Every technique-bearing action carries a validatable `technique_id` + `framework` (`attack` | `atlas` | `aadapt`); a non-technique action sets both to `null`. Record `success` entries too, the report needs the full path. Never rewrite a prior entry. You structure and append what the operator reports; you never invent an action that was not taken.

3. **Propose a ranked adaptation when a technique is blocked or detected (decision support).** Following `references/refinement.md`, offer a short ranked list of variant options for the same objective: a sibling sub-technique first, then an alternative technique for the same objective, then an OPSEC change to the same technique. Each option is a real ATT&CK/ATLAS/AADAPT `technique_id` + `framework`, validated in step 4, with one line on why it may evade the observed control and an OPSEC note. The human operator decides and executes; rt-adapt never executes. Record the chosen move in the `adaptation` field of the log entry for the blocked or detected action.

4. **Validate every proposed technique or variant id.** Collect the ids as a JSON list of `{"technique_id": ..., "framework": ..., "name": ...}`, write it to a scratch path **outside** `engagements/`, and run `python3 skills/_shared/scripts/validate.py --entries <tmp.json>`. Drop any refuted id (never offer it), then delete the temp file. An id that cannot be confirmed is not proposed and does not go into the log.

5. **Record the live-execution events as they occur.** Append to their sections:
   - `detection_observations`: what the blue team did and the timing relative to the action. Detection is data to record, not a reason to abandon; continue if the RoE and objective allow.
   - `deconfliction_events`: a pause-and-consult on a suspected genuine incident, unintended impact, or a discovery of a pre-existing compromise.
   - `deviations`: any action outside the RoE, each with the `approver` and the `rationale`, approved before it is taken.
   - `kill_switch`: any invocation, with `invoked_by` and `reason`.
   - `disclosure_events`: any disclosure made to stand down a blue-team response. This is a Operations Lead decision (`decision_by`), recorded with its `rationale`, and it ends the unaided-detection measurement from that point (`effect_on_unaided_measurement`).

6. **Complete the cleanup and infrastructure record at conclusion.** From the log's introduced artifacts, populate:
   - `target_cleanup`: implants, accounts, persistence, and config changes, each `removed` or `handed_to_owner`. This reconciles against the planning pack **B8 inventory** (referenced by `#planning.human_owned.infrastructure_plan_ref`); any artifact not confirmed removed becomes an open item at Phase 6.
   - `attacker_infrastructure`: each asset either `decommissioned` at conclusion or `retained_for_retest` with a `reason`, an `owner`, and a `decommission_trigger`. While retained it stays under execution safeguards and the red team continues to operate it; its final decommission is confirmed at Phase 6.
   - `recovered_secrets`: the `type` and `system` and the rotation flags (`rotation_owner_notified`, `rotation_confirmed`). The secret **value is never recorded**.

7. **Write `#execution` (section 4).** Write only section 4; never modify another skill's block. It feeds Phase 5 reporting (`rt-report`), which reconciles it against the separately captured Blue Team Account. rt-adapt does **not** hand to `rt-verify`; the report is what gets verified.

## Boundaries

- **No autonomous execution, ever.** rt-adapt proposes and records; the human operator decides and executes under the signed RoE.
- **The log is a contemporaneous human record; never fabricate it.** rt-adapt structures and appends what the operator reports, append-only, and never reconstructs or back-fills the log after the fact. Reconstructing the log after the fact is a defined failure mode.
- **The entry gate is a precondition.** No entry until a signed `#scoping` (Gate 1) and `#planning` (Gate 2) are present and `entry_criteria_confirmed` is all true. If not met, write nothing.
- **Recovered-secret values are never retained**: record the type and system and flag rotation, never the value.
- **Fast and local.** Do not fan out subagents or run external research mid-engagement; the only network call is catalog validation.
- Reason about the next move with the adversary mindset in `skills/_shared/references/adversary-mindset.md` (how the emulated actor would get past the observed control), bounded by the RoE. Prose you author here follows the deliverable standard in `skills/_shared/references/writing-style.md`.
