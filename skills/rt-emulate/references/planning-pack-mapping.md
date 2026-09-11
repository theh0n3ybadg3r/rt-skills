# Mapping `#planning` to the Engagement Planning Pack

The Engagement Planning Pack has three parts: attack path (A), infrastructure (B), procurement (C). It is peer-reviewed together with the Rules of Engagement. `rt-emulate` authors only the machine-readable Part A into the `#planning` section and references the rest; the human deliverables are written by the people who own them. `rt-report` renders the formal document from these inputs.

## What `#planning` maps to

| `#planning` field | Planning Pack element |
| --- | --- |
| `attack_paths[].steps` (technique, action, detection risk, branch, assumption) | Part A: A2 path steps and A5 assumptions register |
| `attack_paths[].steps[].detects_what` | Part A: A4 detection questions carried to reporting |
| `attack_paths[].terminal_action` | Part A: A3 terminal action and evidence to capture |
| `attack_paths[].live_execution_safeguard` / `safeguard_verified` | Part A: A3 safeguard confirmation (transaction-adjacent) |
| `human_owned.infrastructure_plan_ref` | Part B, including the B8 teardown inventory |
| `human_owned.procurement_plan_ref` | Part C |
| `human_owned.rules_of_engagement_ref` | Signed RoE |
| `authorizations.legal` / `authorizations.third_party` | Legal authorization letter / written vendor authorization |
| `gate2_sign_off` | RoE sign-off (Gate 2) |

## What is human-owned (referenced, not authored here)

- **Part B, attack infrastructure.** C2, redirectors, domains and their aging lead times, phishing infrastructure, payload testing against the target EDR stack, and hardware. Section **B8 is the authoritative teardown inventory**: every asset stood up is recorded there, and Phase 4 cleanup and Phase 6 decommission reconcile against it. `#planning` references it by `infrastructure_plan_ref`; it does not reproduce it.
- **Part C, procurement and logistics.** Completed only where spend outside the annual budget is needed; lead time gates the window. Referenced by `procurement_plan_ref`.
- **Rules of Engagement.** Carries the execution authorization, the **Control Group membership**, and the SOC-blind status. There is no separate Control Group Terms of Reference. Referenced by `rules_of_engagement_ref`.
- **Legal and third-party authorizations.** The legal authorization letter for physical operations, and written third-party authorization for any vendor system in the path. Referenced by `authorizations.legal` and `authorizations.third_party`.

What this skill guarantees is that each attack-path step is a validated technique tied to an objective, actor-consistent or justified from tradecraft, with a detection question for the reporting phase and a branch if blocked. The infrastructure, procurement, RoE, and authorizations are the humans' to produce and sign; the Gate 2 sign-off recorded here is the gate that authorizes execution.
