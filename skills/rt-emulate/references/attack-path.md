# The attack path (Planning Pack Part A)

Part A of the Engagement Planning Pack is one attack path per objective: a hypothesized sequence a capable, actor-consistent operator would follow from initial access to the objective's success criterion. It is a hypothesis, not a script. Build it with the adversary mindset in `skills/_shared/references/adversary-mindset.md`: reason from the objective backward, chain preconditions to postconditions, stay faithful to the assigned actor's documented tradecraft, and reason about what the defender would see at each step. Everything here is design and decision support bounded by the Rules of Engagement; the skill executes nothing.

Repeat the whole structure per objective.

## Steps

An ordered list. Each step:

- **`technique_id` + `framework`** (`attack` | `atlas` | `aadapt`). Choose the taxonomy by target type per the selection rule in `framework-mapping.md`, not by whatever a source cited. The id must validate.
- **`actor_consistent`.** True when the technique is in `#threat-profile` for this objective's assigned actor. A step whose technique is not in `#threat-profile` is allowed only when justified from the actor's documented tradecraft; record the justification. An off-profile step with no basis is a defect.
- **`action`.** Concretely what the operator does at this step, at a level a red teamer can execute (tooling and method), without being a copy-paste exploit.
- **`detection_risk`** (`high` | `medium` | `low`). The operator's honest read of how likely this step is to be seen.
- **`detects_what`.** What control would detect this step and at what stage. This is the detection question carried to reporting, so name the telemetry or control, not a vague "monitoring".
- **`branch_if_blocked`.** The alternative if the step is blocked or detected. A path with no branch is under-planned: a real operation adapts, so the plan anticipates the block.
- **`assumption`** (or `null`). What the step assumes to be true (a reachable host, a harvested credential, an unpatched service). Marked assumptions form the pack's assumptions register: each has an impact if false and a branch.

## Terminal action

`terminal_action` is the action that satisfies the objective's `success_criterion` from `#scoping`. It is the point of the path; the steps exist to reach it. State the evidence the operator captures to demonstrate the outcome.

## Live-execution safeguard (transaction-adjacent objectives)

Where an objective is transaction-adjacent (payment, clearing, settlement, or any path that could move value or state that matters), set:

- **`live_execution_safeguard`**: the control that bounds live execution so the demonstration cannot cause real harm (a value ceiling, a sandboxed rail, a hold-and-confirm step).
- **`safeguard_verified`**: `true` only when the safeguard has been technically verified with the asset owner, not merely written down. A documented-but-unverified safeguard does not satisfy Gate 2.

For an objective that is not transaction-adjacent, both are `null`.
