# Execution Record fields

The Execution Record is the `#execution` block (section 4). Part 1 is the contemporaneous log; Part 2 is the cleanup at conclusion, populated from Part 1. It is a **live human record**: rt-adapt structures and appends it as the operator acts, append-only, and never rewrites a prior entry, reconstructs the log after the fact, or invents an action that was not taken. Reconstructing the log afterward is a defined failure mode.

Keep every timestamp in one timezone, log every action, and carry every introduced artifact to Part 2.

## Part 1: the live log

Each `log` entry:

```json
{
  "timestamp": "ISO-8601",
  "operator": "string",
  "objective_id": "string",
  "step": "string | null, the planning-pack step this action executes",
  "action": "string",
  "target": "string",
  "technique_id": "string | null",
  "framework": "attack | atlas | aadapt | null",
  "tooling": "string",
  "outcome": "success | blocked | detected",
  "state_change": "string | null",
  "artifact_introduced": "string | null, carried to Part 2 cleanup",
  "safeguard_state": "string | null, for a transaction-adjacent action",
  "adaptation": "string | null, the variant chosen (decision support only)"
}
```

- Every technique-bearing action carries a validatable `technique_id` + `framework`; a non-technique action sets both to `null`.
- Record `success` entries too, not only blocks and detections; the report needs the full path.
- `action` and `outcome` are fact (what happened); `adaptation` is the move the operator chose (decision support). Keep them distinct.

The other Part 1 sections, appended as events occur:

- `detection_observations`: `{ timestamp, observation, timing }`. What the blue team did and its timing relative to the action.
- `deconfliction_events`: strings recording a pause-and-consult on a suspected genuine incident, unintended impact, or a pre-existing compromise.
- `deviations`: `{ action, approver, rationale }`. Any action outside the RoE, approved before it is taken.
- `kill_switch`: `{ timestamp, invoked_by, reason }`.
- `disclosure_events`: `{ timestamp, decision_by, rationale, effect_on_unaided_measurement }`. A disclosure to stand down a response is a Operations Lead decision and ends the unaided-detection measurement from that point.

## Part 2: cleanup at conclusion

Populated from the log's introduced artifacts:

- `target_cleanup`: `{ artifact, removed, handed_to_owner }` for implants, accounts, persistence, and config changes. Reconciles against the planning pack B8 inventory; any artifact not confirmed removed becomes an open item at Phase 6.
- `attacker_infrastructure`: `{ asset, decommissioned, retained_for_retest, reason, owner, decommission_trigger }`. Decommissioned at conclusion, or retained for retest with a reason, owner, and trigger; while retained it stays under execution safeguards and the red team keeps operating it. Final decommission is confirmed at Phase 6.
- `recovered_secrets`: `{ type, system, rotation_owner_notified, rotation_confirmed }`. The secret **value is never recorded**; record only the type and system and flag rotation.

## Data handling

Keep the log in the local artifact under the run's data class. Do not put target-identifying secret values in it beyond what the engagement record already holds, and never record a recovered-secret value.
