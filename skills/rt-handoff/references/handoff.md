# Handoff and Closure detail

The Handoff and Closure record is the `#handoff` block (section 6). It routes each finding to the enterprise system that will own it, equips the retest team, confirms cleanup and decommission, and closes the red-team engagement tracker. The red team does not track remediation or run the retest; the enterprise systems are the record.

Entry criterion: findings established in `#report`. Cleanup and attacker-infrastructure state come from `#execution`.

## Route each finding to an enterprise system

Every finding in `#report` is entered into exactly one enterprise system, which then owns and tracks it:

- **`vulnerability-management`** for technical vulnerabilities (an exploitable weakness in a system, service, or configuration): finding `source` `attack-path` or `off-path`.
- **`control-tracking`** for control or process failures (a control that did not fire, a process gap).
- **`detection-engineering`** for a detection gap (finding `source` `detection-gap`): it goes to the SOC / detection-engineering function, never the asset owner.

For each finding record: the `finding_id` (from `#report`), the `enterprise_system`, the `entry_ref` (the record id in that system), and the `recommended_remediation` carried verbatim from the finding. The remediation is written to be actionable to the owner who receives it; it is not authored or revised here. **The enterprise system record is the source of truth for remediation status, not this artifact.**

## Equip the retest team

Hand the retest team the test cases and PoCs, scoped per finding, enough to retest that finding and not the whole tradecraft. Set `retest_handed_off` and record `test_case_ref`. The retest handoff is a standing red-team-to-retest exchange, not a stakeholder-facing call. The red team equips the retest; the retest team runs it.

## Confirm cleanup and decommission

From `#execution`:

- `target_cleanup_confirmed`: every Phase 4 `target_cleanup` item confirmed removed or handed to its owner.
- `attacker_infrastructure_decommissioned`: every `attacker_infrastructure` asset confirmed decommissioned. Where infrastructure persisted past execution for evidence or retest, the red team keeps operating it under safeguards until the retest team no longer needs it, then decommissions it. Accountability does not transfer while it is live.
- `evidence_disposition`: finalized per the records-retention standard.

## Close the tracker (gated)

`engagement_tracker_closed` is `true` only when **all** of these hold:

- `target_cleanup_confirmed` is `true`,
- `attacker_infrastructure_decommissioned` is `true`, and
- every finding has been entered into its enterprise system.

The tracker does not close while any attacker infrastructure remains live or any target-cleanup item is unconfirmed. Because the tracker is red-team-owned, enforcing this is the red team's discipline.

Common failure modes to avoid: closing the tracker while attacker infrastructure is still live; leaving a target-cleanup item unconfirmed; handing the retest team the whole tradecraft rather than the scoped test case; treating handoff as final closure when infrastructure persists for retest.

## Coverage note

`coverage_note` records slow-to-remediate or recurring gaps, fed back to the program review and the Phase-2 threat-informed backlog. It is a feedback signal, not a remediation commitment the red team owns.
