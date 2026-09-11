# Engagement Report structure

The Engagement Report is the human deliverable of Phase 5: a narrative of what happened and what detection did, not a severity-ranked vulnerability list. Write against systems, controls, and processes, never individuals. State detection failures plainly. rt-report renders it from the engagement artifact and the Blue Team Account; it adds no analysis beyond reconciling the record.

Front matter carries the engagement name / ID, engagement type (red team operation or purple team exercise), classification (confidential or higher), report version, prepared-by, peer-reviewed-by and date, and distribution. Peer review before distribution.

## The 10 sections

Each section draws from a named source in the artifact.

| # | Section | Draws from |
| --- | --- | --- |
| 1 | Executive summary | The whole report, written last: what was attempted, whether it worked, what it means, in plain language for the sponsor with the bottom line in the first two sentences. Also issued as the standalone Executive Summary. |
| 2 | Scope and objectives | `#scoping` (objectives as approved, success criteria, engagement type and why, out-of-scope a reader might assume was tested) and `#threat-profile` (the assumed threat actor). |
| 3 | Attack narrative | `#execution` (the path in sequence, techniques with taxonomy refs, supported by the Execution Record). For a purple team exercise, the validation record instead. |
| 4 | Objective outcomes | `#report.objective_outcomes` (per objective: achieved / partial / not-achieved vs the stated criterion, with an evidence ref). |
| 5 | Detection and response performance | `#report.detection_analysis` (the reconciliation of the Blue Team Account vs the Execution Record: what was detected, at what stage, response; where not detected, what should have caught it; coverage gap vs process gap). Attribute the Blue Team Account separately from the red team's assessment. |
| 6 | Findings | `#report.findings` where `source` is `attack-path` or `detection-gap` (each: description, role in the path, control or process gap, recommended remediation, suggested owner, material Y/N, control-domain mapping). |
| 7 | Vulnerabilities outside the attack path | `#report.findings` where `source` is `off-path` (discrete vulnerabilities found but not used, recorded so they are not lost, routed to per-application vulnerability management). |
| 8 | Cleanup status | `#execution.target_cleanup` and `attacker_infrastructure` (summary; any open item called out). |
| 9 | Deviations | `#execution.deviations` (any departure from the RoE with rationale and approver; if none, say so). |
| 10 | Limitations | `#report.limitations` (time, scope restrictions, intel/capability gaps, and any disclosure that affected the unaided-detection measure). |

## Appendices A-F

| Appendix | Content | Draws from |
| --- | --- | --- |
| A | Scoping Document ref | `#scoping` |
| B | Threat Profile Brief ref | `#threat-profile` |
| C | Evidence index | The engagement evidence store referenced by `#execution` |
| D | Execution Record ref | `#execution` |
| E | MITRE technique mapping | The ATT&CK / ATLAS / AADAPT techniques across `#threat-profile`, `#planning`, and `#execution` |
| F | Blue Team Account ref | The retained Blue Team Account deliverable (`#report.blue_team_account.ref`) |

## The Executive Summary

The standalone Executive Summary delivered to the Stakeholder is Section 1's content on its own: what was attempted, whether it worked, and what it means, in plain language with the bottom line first and no jargon. It carries what the Stakeholder will own. Write it last, after the body is settled.

## What the report is not

Not a penetration test report. A severity-ranked list with no narrative is a defined failure mode. The report is a narrative of what happened and what detection did. Off-path discrete vulnerabilities are recorded in Section 7 and routed, not scored as the engagement outcome.
