---
name: rt-handoff
description: >-
  Phase 6 (Handoff and Closure) of the threat-informed red team methodology. With findings established in the report, it routes each finding into the enterprise system that will own it (technical vulnerabilities to vulnerability management, control or process failures to control tracking), records the entry reference and carries the recommended remediation from the report, equips the retest team with test cases and PoCs scoped per finding, confirms target cleanup and attacker-infrastructure decommission, sets the evidence disposition, and closes the red-team engagement tracker. It writes the Handoff and Closure record as the #handoff block (section 6). The red team hands findings off and does not own remediation status or run the retest; the enterprise systems are the record.
---

# rt-handoff

Phase 6, Handoff and Closure. Once the report holds the findings, this skill routes each finding to the enterprise system that will own it, hands the retest team what it needs, confirms the engagement is cleaned up and decommissioned, and closes the red-team engagement tracker. It writes the Handoff and Closure record as the `#handoff` block (section 6). This is the closing phase; there is no downstream `rt-*` skill.

The red team does **not** track remediation to closure and does **not** run the retest. The enterprise system record is the source of truth for remediation status. Findings are handed off with the remediation the report already recommends; nothing is invented here.

Shared assets:

- Artifact schema (`#handoff`, section 6): `skills/_shared/references/red-team-engagement-v3.md`. It consumes section 5 (`#report`, the findings) and section 4 (`#execution`, cleanup and attacker-infrastructure state).
- Guidance: `references/handoff.md` (the routing rule, the retest handoff, and the tracker-close conditions).

## Procedure

1. **Confirm the entry criterion.** Read section 5 (`#report`) and section 4 (`#execution`) of `engagements/<engagement-id>/engagement.md`. `#report` must be present with its findings; this phase requires findings established in the report. If `#report` is missing or has no findings, stop and tell the operator; write nothing.

2. **Route each finding to the enterprise system that will own it.** For every finding in `#report`, add a `findings` entry: carry the `finding_id` and set `enterprise_system`. Technical vulnerabilities go to `vulnerability-management`; control or process failures go to `control-tracking`; a detection gap goes to `detection-engineering` (the SOC / detection-engineering function), not the asset owner. Record the `entry_ref` (the record id in that enterprise system) and carry the `recommended_remediation` verbatim from the finding in `#report`. Do not author a new remediation here.

3. **Equip the retest function.** For each finding, hand the retest team the test cases and PoCs scoped to that finding (enough to retest it, not the whole tradecraft). Set `retest_handed_off` and record `test_case_ref`. The red team equips the retest; it does not run it.

4. **Confirm cleanup and decommission.** From `#execution`, set `closure.target_cleanup_confirmed` (every Phase 4 target-cleanup item confirmed removed or handed to its owner) and `closure.attacker_infrastructure_decommissioned` (every attacker-infrastructure asset confirmed decommissioned, including anything retained for retest once its trigger fires). Record `evidence_disposition` (per the records-retention standard).

5. **Close the tracker, gated.** Set `closure.engagement_tracker_closed` to `true` **only** when `target_cleanup_confirmed` and `attacker_infrastructure_decommissioned` are both `true` and every finding has been entered into its enterprise system. The tracker does not close while any attacker infrastructure remains live or any cleanup item is unconfirmed. If either is not met, leave it `false` and name what is still open.

6. **Record the coverage note.** In `coverage_note`, feed slow-to-remediate or recurring gaps back to the program review and the Phase-2 threat-informed backlog.

7. **Write `#handoff` (section 6).** Write only section 6; never modify another skill's block. This is the closing phase; there is no handoff to a downstream `rt-*` skill.

## Boundaries

- **The enterprise systems are the record.** The red team hands findings off and does not own remediation status or retest tracking; the vulnerability-management or control-tracking record is the source of truth for a finding's remediation, not this artifact.
- **Remediation is carried, never invented.** Each finding is routed with the `recommended_remediation` from `#report`; this phase does not author or revise remediation.
- **Closure is gated.** The engagement tracker cannot close while any cleanup item is unconfirmed or any attacker infrastructure is still live; `engagement_tracker_closed` is `true` only when both are confirmed and every finding is entered.
- **Requires findings.** No handoff without a `#report` that holds findings; if it is missing, write nothing.
- Prose you author here follows the deliverable standard in `skills/_shared/references/writing-style.md`.
