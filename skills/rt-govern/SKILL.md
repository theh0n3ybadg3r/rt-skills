---
name: rt-govern
description: >-
  Phase 1 (Intake and Scoping) gate for a red team engagement. Turns an intake request into an outcome-based Scoping Document: elicits the business impact from the stakeholder and validates it against the enterprise impact analysis, derives the crown-jewel targets, drafts measurable objectives, sets the data class and egress policy, records the provisional engagement type, and captures the Gate 1 sign-off (Stakeholder, Operations Lead, Assessment Lead, and the CISO). It authorizes what is tested; every other rt-* skill checks for a signed Scoping Document before acting.
---

# rt-govern

The Phase 1 human-in-command gate. It converts an intake request into the **Scoping Document**, the first authorization gate, which fixes the intent of each objective and approves what is tested and why. It does not analyze intelligence (that is `rt-intel`, Phase 2) and it executes nothing. Objective-based, not vulnerability-based: an objective is a business outcome with a measurable success criterion, never a technique, system, or vulnerability class.

Shared rules and schema:

- The `#scoping` block it writes: `skills/_shared/references/red-team-engagement-v3.md` (section 1). Operator summary: `references/scoping-record.md`.
- Objectives, crown jewels, and the differentiation test: `references/objectives.md`.
- Data classes and the egress policy: `references/data-classes.md`.
- The intake form the requestor fills: `templates/INTAKE.md`.

## Procedure

0. **Read the intake.** The requestor fills the intake form (`templates/INTAKE.md`, scaffolded by `make new-engagement`). Read the raw responses, not a summary; the free-text "what prompted this" field is diagnostic. Do not ask the requestor to define objectives.
1. **Triage and redirect.** Redirect work that is not a red team engagement: an enumeration / "test this system" request is a penetration test (redirect it to the penetration-test function); a scheduled third-party TLPT cycle goes to that program; application-security SDLC work goes to its function.
2. **Elicit and validate business impact.** Elicit the business impact from the stakeholder (the scoping call uses the stakeholder questionnaire). Cross-check it against the enterprise BIA / risk register where they exist, noting the absence as a gap to enterprise risk; validate CEF / FMI relevance against the enterprise view, since a business-line requestor is least likely to see systemic consequence. The impact is the stakeholder's, validated; it is not a red team product.
3. **Derive crown-jewel targets.** Map the validated business function to the actual technical asset (not a platform name), trace its identity, data, and integration dependencies, and identify any FMI connectivity. This translation is red team work.
4. **Split an AI/ML concern.** Where the target involves AI/ML, establish whether the concern is the AI's own behavior (ATLAS), the AI as a pivot into infrastructure (ATT&CK), or both, and scope them separately if both.
5. **Draft the objectives** (at most three). Each is an outcome (not a technique or system) with a measurable `success_criterion`, a `target_crown_jewel`, a `business_impact` that traces to the validated impact, its `systemic_relevance`, and a `detection_question`. Apply the differentiation test: if every finding would get the same "patch it" response, this is a penetration test, redirect it. The red team drafts; the Stakeholder confirms the objectives capture their concern but does not author them.
6. **Set the provisional engagement type** (`red-team-operation` | `purple-team-exercise`) with a rationale; it is confirmed in Phase 2. A red-to-purple downgrade names the narrower question it answers.
7. **Set the data class and egress policy** from `references/data-classes.md`: `data_class` is exactly `public-reference` or `engagement-sensitive`; `source_content` is `true` only for `public-reference`; `public_catalog_fetch` is always `true`.
8. **Peer review** by an operator not involved in drafting: each objective is an outcome, each success criterion measurable, each objective traces to a crown jewel and a validated impact.
9. **Record the Gate 1 sign-off.** The Scoping Document sign-off requires the Stakeholder, Operations Lead, Assessment Lead, and the CISO. The CISO may approve asynchronously, but the gate does not clear without the CISO's approval (non-exceptable).
10. **Write `#scoping`** to `engagements/<engagement-id>/engagement.md`, where `<engagement-id>` is the deterministic slug of `engagement_ref` defined in `red-team-engagement-v3.md`. Create the file if absent; write section 1 only; never modify other sections. Report the path so every later skill uses the same file.
11. **Hand off to `rt-verify` (target `scoping`)** for the independent peer review of the objectives (each is an outcome, measurable, and traces to a crown jewel and a validated business impact) before Phase 2 proceeds.

## Refusals and gate

- Refuse and write nothing if `engagement_ref` is empty or `data_class` is not one of the two literals.
- The Scoping Document is incomplete without at least one objective that is an outcome, has a measurable success criterion, and traces to a crown jewel and a validated business impact. A request with no articulable business impact is declined and redirected, not absorbed.
- The intent an objective locks at sign-off is not reopened later; Phase 2 enriches the approach, not the intent. A change to intent is a material change requiring stakeholder re-approval.
- Gate 1 clears only when all four approvers have signed. Downstream skills treat a missing or unsigned `#scoping` block as not authorized and stop.

## Scope and honesty

This gate is policy plus design, not a network sandbox. It records the declared terms and guarantees sensitive content never needs to egress; it cannot by itself stop a misbehaving tool from sending data, and with a hosted model the reasoning steps do send source content to the model provider. See `references/data-classes.md`. State this plainly if asked.
