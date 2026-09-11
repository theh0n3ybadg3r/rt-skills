# Objectives, crown jewels, and the differentiation test

The Scoping Document is objective-based. An **objective** is a business outcome a threat actor would achieve, with a measurable success criterion. It is never a technique, a system name, or a vulnerability class. The test: can you write one sentence stating what, if observed, means the objective was achieved? If not, it is not yet an objective.

Each objective records:

- `outcome`: the business outcome (the intent). Locked at Gate 1; not reopened later.
- `success_criterion`: the observable, measurable condition that means it was met.
- `target_crown_jewel`: the specific asset (name / owner), not a platform name.
- `business_impact`: the consequence if achieved in the wild, tracing to the validated impact summary. An objective with no traceable impact does not proceed.
- `systemic_relevance`: `cef` | `fmi` | `payment-settlement` in the path, or `none`.
- `detection_question`: what should catch this, and at what stage. It becomes the detection analysis in reporting.

**Crown jewels** come from the enterprise impact view, not invented by the red team: map the business function to the real technical asset, trace identity / data / integration dependencies, and note FMI connectivity. Business impact is the stakeholder's, validated against the enterprise BIA / risk register; deriving the crown-jewel target from it is red team work, the impact itself is not.

**Differentiation test.** If every finding the engagement could produce would get the same "patch it" response, the request is a penetration test; redirect it. A red team engagement asks a "would we know" question about an end-to-end outcome, not "does this one control work."

Keep to at most three objectives; a focused set beats shallow breadth. `rt-verify` (target `scoping`) later checks that each objective is an outcome, is measurable, and traces to a crown jewel and a validated impact.
