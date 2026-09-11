# Scoping Document record (the `#scoping` block)

`rt-govern` writes one `#scoping` block to section 1 of the engagement artifact. The canonical schema and rules are in `skills/_shared/references/red-team-engagement-v3.md`; this is the operator-facing summary.

Example (engagement-sensitive run):

```json
{
  "schema": "red-team-engagement/v3#scoping",
  "engagement_ref": "ENG-2026-014",
  "engagement_type": "red-team-operation",
  "engagement_type_rationale": "an open question about whether unaided detection would catch insider PII exfiltration",
  "stakeholder": "j.rivera (Head of Retail Payments)",
  "red_team_lead": "a.okafor",
  "peer_reviewed_by": "s.lindqvist",
  "data_class": "engagement-sensitive",
  "egress_permitted": { "source_content": false, "public_catalog_fetch": true },
  "scoping_summary": {
    "business_impact": "loss of customer PII from the CRM datastore; regulatory and trust impact",
    "business_impact_validated": true,
    "crown_jewels": ["CRM customer datastore (owner: CRM platform team)"],
    "in_scope": ["corporate identity plane", "CRM application tier"],
    "out_of_scope": ["payment-authorization production path"],
    "third_party_systems_in_path": [],
    "physical_operations": false,
    "constraints": [
      "no production customer-data exfiltration beyond a minimal proof sample"
    ]
  },
  "backlog": {
    "source": "stakeholder-request",
    "prioritization_rationale": "high business impact; CRM datastore never tested"
  },
  "objectives": [
    {
      "id": "OBJ-1",
      "outcome": "a malicious insider reaches and exfiltrates customer PII from the CRM datastore",
      "success_criterion": "a minimal proof sample of PII is retrieved from the CRM datastore",
      "target_crown_jewel": "CRM customer datastore",
      "business_impact": "loss of customer PII (regulatory and trust)",
      "systemic_relevance": "none",
      "detection_question": "would the SOC detect bulk read and egress from the CRM datastore, unaided?",
      "constraints": "minimal proof sample only"
    }
  ],
  "gate1_sign_off": {
    "stakeholder": "j.rivera",
    "operations_lead": "m.chen",
    "assessment_lead": "d.abara",
    "ciso": "r.mensah"
  }
}
```

Rules:

- Write the record only when `engagement_ref` is non-empty and `data_class` is one of the two literals.
- `public_catalog_fetch` is always `true`; `source_content` is `true` only for `public-reference`.
- At least one objective that is an outcome, is measurable, and traces to a crown jewel and a validated business impact, else the Scoping Document is incomplete.
- **Gate 1 (non-exceptable):** the four sign-off approvers (Stakeholder, Operations Lead, Assessment Lead, CISO) are all present; the CISO may approve asynchronously, but the gate does not clear without it. The CRO and board committees are not in the chain.
- Do not modify other sections; each skill owns its own.
- A run whose artifact has no signed `#scoping` block is not authorized; downstream skills stop.
