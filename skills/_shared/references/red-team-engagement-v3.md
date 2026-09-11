# red-team-engagement/v3: shared engagement artifact schema

The engagement artifact is one markdown file the `rt-*` skills hand off over. Each skill writes or replaces **only its own `#section` block**, in numbered order, and never modifies another skill's block. Every section carries a fenced `json` block with the machine-readable spine so the `validate` helper and `rt-verify` can parse it; a rendered human summary may accompany it. `rt-report` renders the formal deliverables from these sections.

This schema conforms to a threat-informed, intelligence-led red team methodology: a capability-building and control-validation function, not an independent assurance function. Engagements are **objective-based**, not flag- or vulnerability-based: an objective is a business outcome with a measurable success criterion, never a technique, system name, or vulnerability class.

The lifecycle is **six phases and begins at intake**. Business impact is elicited from the stakeholder at intake and cross-checked against the enterprise business-impact analysis; the red team does not produce that analysis, and where it is missing that is a gap raised to enterprise risk. There is no standing business-impact-mapping section.

Two authorization gates govern the run: **Gate 1** is the Scoping Document sign-off (section 1), approving _what_ is tested; **Gate 2** is the Rules of Engagement sign-off (section 3), approving _how_ it runs and authorizing execution. Both require the same four approvers (Stakeholder, Operations Lead, Assessment Lead, and the CISO). The CISO is a required approver at both gates and may approve asynchronously: the gate meeting may proceed without the CISO present, but the CISO's approval is recorded before the engagement advances, and the gate does not clear without it. The gates do not include the CRO or any board committee.

Filename: `engagements/<engagement-id>/engagement.md`. The `<engagement-id>` is a deterministic slug of `engagement_ref`: if it is a URL or file path take its last segment, then lowercase, keep `[a-z0-9-]`, and collapse every other run of characters to a single `-`. `rt-govern` reports the resulting path; every later skill uses it or re-derives it by this same rule.

Sections, in order: 1. Scoping Document (`rt-govern`, Phase 1), 2. Threat Profile (`rt-intel`, Phase 2), 3. Planning Pack (`rt-emulate`, Phase 3), 4. Execution Record (`rt-adapt`, Phase 4), 5. Report (`rt-report`, Phase 5), 6. Handoff and Closure (`rt-handoff`, Phase 6), 7. Verification (`rt-verify`, cross-cutting). A run only fills the sections for the phases it uses.

Frameworks: offensive `attack` / `atlas` / `aadapt` for technique mapping in Phases 2-3 (apply the target-type selection rule in `framework-mapping.md`: `atlas` when the AI system itself is the subject of the test, `aadapt` for payment / clearing / settlement infrastructure, `attack` otherwise); defensive `nist-csf` + `nist-800-53` for the control-domain mapping in Phase 5. See `framework-mapping.md` for ID rules.

---

## 1. Scoping Document (written by `rt-govern`)

The Phase 1 Scoping Document: the scope, objectives, provisional engagement type, and Gate 1 sign-off. It fixes the **intent** of each objective. No downstream skill acts without this block present; it is the first authorization.

```json
{
  "schema": "red-team-engagement/v3#scoping",
  "engagement_ref": "string, engagement name or id (scope reference)",
  "engagement_type": "red-team-operation | purple-team-exercise (provisional at Phase 1)",
  "engagement_type_rationale": "string, why this type (a red->purple downgrade names the narrower question)",
  "stakeholder": "string",
  "red_team_lead": "string",
  "peer_reviewed_by": "string, operator not involved in drafting",
  "data_class": "public-reference | engagement-sensitive",
  "egress_permitted": { "source_content": false, "public_catalog_fetch": true },
  "scoping_summary": {
    "business_impact": "string, elicited from the stakeholder",
    "business_impact_validated": false,
    "crown_jewels": ["string, crown-jewel asset (from the enterprise view)"],
    "in_scope": ["string"],
    "out_of_scope": ["string"],
    "third_party_systems_in_path": ["string"],
    "physical_operations": false,
    "constraints": [
      "string, cross-border / data-residency / change-freeze / other"
    ]
  },
  "backlog": {
    "source": "stakeholder-request | intelligence-surfaced",
    "prioritization_rationale": "string, per the prioritization factors"
  },
  "objectives": [
    {
      "id": "string, e.g. OBJ-1",
      "outcome": "string, the intent: a business outcome (NOT a technique, system, or vulnerability class)",
      "success_criterion": "string, measurable",
      "target_crown_jewel": "string, from scoping_summary.crown_jewels",
      "business_impact": "string, consequence if achieved in the wild",
      "systemic_relevance": "none | cef | fmi | payment-settlement",
      "detection_question": "string, the 'would we detect it unaided' question",
      "constraints": "string | null, objective-specific constraints"
    }
  ],
  "gate1_sign_off": {
    "stakeholder": "string | null",
    "operations_lead": "string | null",
    "assessment_lead": "string | null",
    "ciso": "string | null, required approver (may approve asynchronously)"
  }
}
```

Rules:

- `engagement_ref` required and non-empty, and `data_class` one of the two literals, else refuse and write nothing.
- At least one objective, each an outcome (not a technique / system / vulnerability), with a measurable `success_criterion` and a `target_crown_jewel` that appears in `scoping_summary.crown_jewels`. `business_impact_validated` is `true` only when the impact was cross-checked against the enterprise BIA / risk register; an objective whose impact cannot be validated does not proceed.
- The objective `outcome` (intent) is locked once Gate 1 is signed; Phase 2 may enrich the approach but a change to intent is a material change requiring stakeholder re-approval.
- `engagement_type` is provisional here and confirmed in Phase 2.
- `egress_permitted.public_catalog_fetch` is always `true`; `egress_permitted.source_content` is `true` only when `data_class == public-reference`. The hosted-model honest limit lives in `data-classes.md`.
- **Gate 1 (non-exceptable):** all four `gate1_sign_off` approvers present (Stakeholder, Operations Lead, Assessment Lead, and the CISO) before the engagement proceeds past scoping. The CISO may approve asynchronously, but the gate does not clear without it.
- A run whose artifact has no `#scoping` block is unauthorized; downstream skills stop.

## 2. Threat Profile (written by `rt-intel`)

The Phase 2 threat profile brief: a companion to the signed Scoping Document (not an edit to it). It establishes the intelligence-justified actor per objective and maps the techniques, enriching the **approach** without changing the signed intent.

```json
{
  "schema": "red-team-engagement/v3#threat-profile",
  "sources": ["string, CTI / advisory / GTL identifiers"],
  "catalog_provenance": {
    "attack": "string, version",
    "atlas": "string, version",
    "aadapt": "string, version"
  },
  "engagement_type_confirmed": "red-team-operation | purple-team-exercise",
  "actors": [
    {
      "objective_id": "string, the objective this actor is selected for",
      "name": "string, actor class or named group",
      "intelligence_basis": {
        "quote": "verbatim string from a source",
        "locator": "string, section/page/line",
        "recency": "string"
      },
      "motivation": "string, the actor's motivation in this scenario",
      "capability": "string",
      "sophistication": "string",
      "opsec_posture": "string, persistent-covert | fast-noisy | ..."
    }
  ],
  "techniques": [
    {
      "id": "string, e.g. T1566.001 / AML.T0051 / <aadapt-id>",
      "framework": "attack | atlas | aadapt",
      "name": "string, technique name as extracted",
      "objective_id": "string",
      "sourced": "intelligence | inference",
      "citations": [
        { "quote": "verbatim string from the source", "locator": "string" }
      ],
      "script_verdict": "confirmed | refuted | unverifiable, from the validate helper",
      "script_reason": "string"
    }
  ],
  "excluded_techniques": [
    {
      "id": "string",
      "framework": "attack | atlas | aadapt",
      "reason": "string, why deliberately excluded"
    }
  ],
  "intelligence_gaps": [
    "string, gaps and assumptions carried forward to the report's limitations"
  ],
  "implications_for_planning": {
    "initial_access_approach": "string, implied initial access",
    "infrastructure_implied": "string, feeds planning pack Part B",
    "specialist_capability_implied": "string, feeds Part C procurement",
    "opsec_constraints": "string, constraints the engagement must observe"
  }
}
```

Rules:

- This section enriches the approach; it does not edit the signed objectives. If intelligence contradicts an objective's intent, that is a material change requiring explicit stakeholder re-approval, not a silent edit.
- Every actor is selected for an `objective_id` and carries an `intelligence_basis` with a verbatim `quote` + `locator`. An actor asserted without an intelligence basis is refused; where no credible actor exists, raise it rather than assume one.
- Every technique carries `id`, `framework`, `name`, an `objective_id`, at least one citation whose `quote` is a verbatim substring of a cited source, and `sourced`. A mapping proposed by inference sets `sourced: "inference"` and is never presented as authoritative.
- Choose the taxonomy by target type (the `framework-mapping.md` selection rule), not by whatever a source happens to cite. Technique breadth is not a goal.
- `engagement_type_confirmed` records the confirmed (or revised) engagement-type decision. `script_verdict` is the deterministic ID/name check; `rt-verify` sets the final verdict.

## 3. Planning Pack (written by `rt-emulate`)

The Phase 3 engagement planning pack Part A: a hypothesized attack path per objective, plus Gate 2 (the RoE sign-off that authorizes execution). Parts B (infrastructure and teardown), C (procurement), the Rules of Engagement (which now carries the Control Group membership and SOC-blind status, with no separate Control Group ToR), the safeguard verification, and the legal / third-party authorizations are **human-owned** artifacts this section references but does not author. `rt-emulate` is design and decision support and executes nothing.

```json
{
  "schema": "red-team-engagement/v3#planning",
  "attack_paths": [
    {
      "objective_id": "string",
      "steps": [
        {
          "step": 1,
          "technique_id": "string",
          "framework": "attack | atlas | aadapt",
          "actor_consistent": true,
          "action": "string, what the operator does (executable, not a copy-paste exploit)",
          "detection_risk": "high | medium | low",
          "detects_what": "string, what would detect it and at what stage (feeds the report)",
          "branch_if_blocked": "string, the alternative (a path with no alternative is under-planned)",
          "assumption": "string | null"
        }
      ],
      "terminal_action": "string, the action that satisfies the success criterion",
      "live_execution_safeguard": "string | null, required for a transaction-adjacent objective",
      "safeguard_verified": "boolean | null, technically verified with the asset owner (null when n/a)"
    }
  ],
  "gate2_sign_off": {
    "stakeholder": "string | null",
    "operations_lead": "string | null",
    "assessment_lead": "string | null",
    "ciso": "string | null, required approver (may approve asynchronously)",
    "legal": "string | null, signer required only where physical operations are in scope"
  },
  "authorizations": {
    "legal": "string | null, authorization-letter reference where physical operations are in scope",
    "third_party": "string | null, written authorization where an attack path touches vendor systems"
  },
  "human_owned": {
    "infrastructure_plan_ref": "string | null, planning pack Part B incl. the B8 teardown inventory",
    "procurement_plan_ref": "string | null, Part C",
    "rules_of_engagement_ref": "string | null, signed RoE: carries execution authorization, the Control Group membership, and the SOC-blind status (there is no separate Control Group ToR)"
  }
}
```

Rules:

- Every step's `technique_id` validates against the `validate` helper and is `actor_consistent`; a step whose technique is not in `#threat-profile` must be justified from the actor's documented tradecraft. Each path carries at least one `branch_if_blocked` and marks its assumptions.
- **Gate 2 (non-exceptable):** all four `gate2_sign_off` approvers present (Stakeholder, Operations Lead, Assessment Lead, and the CISO, who may approve asynchronously but without whom the gate does not clear), plus the `legal` signer where physical operations are in scope; `authorizations.legal` present where `#scoping.scoping_summary.physical_operations` is true; `authorizations.third_party` present where `third_party_systems_in_path` is non-empty; `safeguard_verified == true` for every path carrying a `live_execution_safeguard`. A documented-but-unverified safeguard does not satisfy the gate.
- The B8 infrastructure inventory (human, referenced by `infrastructure_plan_ref`) is the authoritative teardown list that Phase 4 cleanup and Phase 6 decommission reconcile against.

## 4. Execution Record (written by `rt-adapt`)

The Phase 4 execution record: a contemporaneous log and the target-environment cleanup. The log is a **live human record**: `rt-adapt` structures and appends entries and proposes adaptations as decision support, and never fabricates or reconstructs the record. Append-only; never rewrite prior entries.

```json
{
  "schema": "red-team-engagement/v3#execution",
  "entry_criteria_confirmed": {
    "timestamp": "ISO-8601",
    "roe_signed": true,
    "safeguards_active": true,
    "soc_blind": true,
    "c2_separated": true
  },
  "log": [
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
      "artifact_introduced": "string | null, carried to cleanup",
      "safeguard_state": "string | null, for a transaction-adjacent action",
      "adaptation": "string | null, variant proposed (decision support only)"
    }
  ],
  "detection_observations": [
    { "timestamp": "ISO-8601", "observation": "string", "timing": "string" }
  ],
  "deconfliction_events": ["string"],
  "deviations": [
    { "action": "string", "approver": "string", "rationale": "string" }
  ],
  "kill_switch": [
    { "timestamp": "ISO-8601", "invoked_by": "string", "reason": "string" }
  ],
  "disclosure_events": [
    {
      "timestamp": "ISO-8601",
      "decision_by": "string, a Operations Lead decision",
      "rationale": "string",
      "effect_on_unaided_measurement": "string, the unaided measure ends from this point"
    }
  ],
  "target_cleanup": [
    {
      "artifact": "string",
      "removed": true,
      "handed_to_owner": "string | null"
    }
  ],
  "attacker_infrastructure": [
    {
      "asset": "string",
      "decommissioned": false,
      "retained_for_retest": false,
      "reason": "string | null, why retained (when retained_for_retest)",
      "owner": "string | null, who owns it while retained",
      "decommission_trigger": "string | null"
    }
  ],
  "recovered_secrets": [
    {
      "type": "string, credential / key / token / ... (the value itself is never recorded)",
      "system": "string",
      "rotation_owner_notified": false,
      "rotation_confirmed": false
    }
  ]
}
```

Rules:

- `entry_criteria_confirmed` must all be true before the first action (the Gate 2 conditions, confirmed live: RoE signed, safeguards active at start, SOC blind for a red team operation, C2 separated).
- Every log action that used a technique carries a validatable `technique_id` + `framework`. Record `success` entries too; the report needs the full path.
- `target_cleanup` (implants, accounts, persistence, config changes) is completed at conclusion and reconciles against the planning pack B8 inventory; any artifact not confirmed removed becomes an open item at Phase 6.
- `attacker_infrastructure` may be decommissioned at conclusion, or retained for retest (`retained_for_retest: true`) with a recorded `decommission_trigger`; while live it stays under execution safeguards and the red team continues to operate it. Its final decommission is confirmed at Phase 6.
- `disclosure_events` records any disclosure to stand down a response: it is a Operations Lead decision, recorded, and ends the unaided-detection measurement from that point.
- Recovered credential and secret values are NOT retained: `recovered_secrets` records the type and system and flags rotation, never the value.

## 5. Report (written by `rt-report`)

The Phase 5 reporting: the Blue Team Account, the Detection Analysis, findings, and materiality. `rt-report` assembles the report; it does not invent findings, severities, or detection conclusions.

```json
{
  "schema": "red-team-engagement/v3#report",
  "control_provenance": {
    "nist-csf": "string, version",
    "nist-800-53": "string, version"
  },
  "blue_team_account": {
    "captured_before_disclosure": true,
    "exception": "none | disclosed-at | non-blind | limited-prompt",
    "account": "string, the SOC's own experience (inputs: time window + broad scope only)",
    "ref": "string, standalone retained Blue Team Account deliverable"
  },
  "detection_analysis": [
    {
      "objective_id": "string",
      "unaided_detected": true,
      "stage": "string, where in the path it was detected",
      "gap_type": "coverage | process | none",
      "reconciliation": "string, execution record vs blue-team account (attributed separately)"
    }
  ],
  "objective_outcomes": [
    {
      "objective_id": "string",
      "outcome": "achieved | partial | not-achieved",
      "evidence": "string"
    }
  ],
  "findings": [
    {
      "id": "string, e.g. F-1",
      "source": "attack-path | off-path | detection-gap",
      "objective_id": "string | null",
      "description": "string, names systems/controls/processes, never an individual",
      "recommended_remediation": "string",
      "control_domain": [
        {
          "framework": "nist-csf | nist-800-53",
          "id": "string",
          "name": "string"
        }
      ],
      "severity": "string, human-set",
      "material": true,
      "materiality_basis": "string",
      "suggested_owner": "string"
    }
  ],
  "escalation": [
    {
      "finding_id": "string",
      "escalated_to": "string, CISO for material findings",
      "date": "ISO-8601"
    }
  ],
  "limitations": [
    "string, incl. any disclosure effect on the unaided-detection measure"
  ]
}
```

Rules:

- **Unaided detection is the measure.** The `blue_team_account` is captured first, from the SOC's own experience, **before any disclosure**; reconciling it against the execution record is the `detection_analysis`, with the blue team's account attributed separately. A disclosure to stand down a response ends the unaided-detection measurement from that point.
- `blue_team_account.exception` records when the account measures something other than unaided detection: `disclosed-at` (only the pre-disclosure period is an unaided measure), `non-blind` (a collaborative detection review, not an unaided measure), or `limited-prompt` (the SOC needed more than the window and broad scope, so it measures loggability, not unaided detection).
- **Non-attribution:** no individual is ever named as the cause of a failure. Findings name systems, controls, and processes.
- **Materiality is a human determination** (the Operations Lead); `rt-report` records `material` + `materiality_basis`, it does not set them. Material findings escalate to the CISO.
- Each finding carries a `recommended_remediation` and, where useful, a `control_domain` mapping (`nist-csf` and/or `nist-800-53`; the `validate` helper checks the ids). Off-path vulnerabilities are recorded and routed, not scored as the engagement outcome.

## 6. Handoff and Closure (written by `rt-handoff`)

The Phase 6 handoff: route each finding into the enterprise system that will own it, equip the retest function, confirm cleanup and decommission, and close the red-team engagement tracker. The red team does **not** track remediation status or run the retest; the enterprise systems are the record.

```json
{
  "schema": "red-team-engagement/v3#handoff",
  "findings": [
    {
      "finding_id": "string, from #report",
      "enterprise_system": "vulnerability-management | control-tracking | detection-engineering",
      "entry_ref": "string, the record id in that enterprise system",
      "recommended_remediation": "string, carried from #report",
      "retest_handed_off": false,
      "test_case_ref": "string | null, test cases / PoCs handed to the retest team"
    }
  ],
  "closure": {
    "target_cleanup_confirmed": false,
    "attacker_infrastructure_decommissioned": false,
    "evidence_disposition": "string",
    "engagement_tracker_closed": false
  },
  "coverage_note": "string, slow-to-remediate or recurring gaps noted for the program review / Phase-2 backlog"
}
```

Rules:

- Every finding is entered into the correct enterprise system with its `recommended_remediation`; the enterprise system record is the source of truth for remediation status, not this artifact. Route by finding `source`: a technical vulnerability (`attack-path` or `off-path`) to `vulnerability-management`, a control or process failure to `control-tracking`, and a `detection-gap` to `detection-engineering` (the SOC / detection-engineering function), never to the asset owner.
- Test cases and PoCs are handed to the retest team, scoped per finding.
- The engagement tracker does not close while any attacker infrastructure remains live or any cleanup item is unconfirmed: `engagement_tracker_closed` is `true` only when `target_cleanup_confirmed` and `attacker_infrastructure_decommissioned` are both `true` and every finding has been entered.

## 7. Verification (written by `rt-verify`)

Independent re-check of a section. Section 7 holds **one `#verification` block per `target`** (`scoping`, `threat-profile`, `planning`, or `report`), appended, never overwriting another target's block. Sets the release gate for that target.

```json
{
  "schema": "red-team-engagement/v3#verification",
  "target": "scoping | threat-profile | planning | report",
  "producer_model": "string",
  "verifier_model": "string",
  "boundary": "string, see degradation.md",
  "catalog_provenance": {
    "attack": "string, version",
    "atlas": "string, version",
    "aadapt": "string, version"
  },
  "ready": false,
  "verdicts": [
    {
      "id": "string, matches a reviewed item id (objective / technique / step / finding)",
      "verdict": "confirmed | refuted | unverifiable",
      "reason": "string",
      "checks": { "note": "per-target checks; see below" }
    }
  ]
}
```

Review objects per target (QA peer review):

- `scoping`: each objective is an outcome (not a technique), the `success_criterion` is measurable, it traces to a `target_crown_jewel` and a validated `business_impact`, and its systemic relevance is recorded.
- `threat-profile`: each technique's `id_name` validates, a citation resolves, the quote supports the mapping, the actor's `intelligence_basis` is real (not plausible-sounding), and inferred mappings are marked.
- `planning`: each step's technique validates and is actor-consistent or justified from tradecraft; the path carries a branch; a safeguard is specified and verified for any transaction-adjacent objective.
- `report`: the narrative is supported by the execution record and evidence, the blue-team account was captured before disclosure, no individual is named, and each finding traces to the record.

Gate rule (fail-closed), computed by the `validate` helper's gate mode, never hand-typed:

- An item is `confirmed` only when its deterministic `id_name` check is `confirmed` (where it has one) AND its citations resolve AND the persona judgment for that target is `yes`.
- Any `refuted` or `unverifiable` item, or an empty verdict set, means `ready: false`. An empty set must never vacuously pass.
- Catalog unreachable means `id_name == unverifiable`, so the item is `unverifiable` and the artifact is gated. Never passed silently.
- `ready: true` only when there is at least one verdict and every verdict is `confirmed`.

Independence here is **procedural**, not organizational: the red team and the tested function share a reporting line, so the guarantee is a separate drafter, a fresh verifying context that never saw the producer's reasoning, and a report the tested function cannot edit (its own account is captured separately as the Blue Team Account). See `degradation.md`.
