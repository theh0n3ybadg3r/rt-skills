# Compensating control mapping

Goal: for each identified exposure, a compensating control that genuinely reduces it, anchored to a control-domain mapping (NIST CSF and/or NIST SP 800-53), with an honest statement of what it does and what it leaves behind.

A compensating control here is any measure that limits exposure to the identified vulnerability short of the vendor fix: a mitigation, a detection, a configuration change, a segmentation or access restriction. The point is to tell a defender what they can do now and how much it helps.

## What to capture per control

### The control-domain anchor

- **control_domain** (an array of `{framework, id, name}`): the control domains the measure realizes. `framework` is `nist-csf` or `nist-800-53`. This mirrors the engagement report's finding `control_domain` (the program pairs NIST CSF with NIST SP 800-53 as the control-domain frameworks), so an exposure assessment speaks the same control language as a report finding.
  - NIST SP 800-53 Rev 5 gives the audit-facing control, e.g. `SC-7` Boundary Protection, `SI-4` System Monitoring, `SI-2` Flaw Remediation.
  - NIST CSF 2.0 gives the Category the control lands in, e.g. `PR.IR` Technology Infrastructure Resilience, `DE.CM` Continuous Monitoring, `PR.PS` Platform Security.
  - Prefer a pair (one 800-53 control and one CSF Category) so the control is placed both in the audit catalog and in the CSF domain. One framework alone is acceptable when only one credibly applies; the compliance intent is folded into this mapping, so there is no separate compliance field.
- Use the official title for each id so the `validate` helper confirms the name (both CSF and 800-53 are name-checked, fail-closed, with no `Parent: Child` tolerance).

### The claim and the honesty

- **counters_technique_ids**: the technique ids from `#vulnerability.techniques` this control addresses. A control that maps to no identified technique is not a compensating control for this vulnerability.
- **limits_exposure_by**: the causal reduction, specific to this exposure. "Inbound traffic filtering blocks the unauthenticated request path to the vulnerable endpoint from untrusted networks" is a real reduction; "improves security posture" is not.
- **residual_risk**: what exposure remains after the control. Every control leaves something (an authenticated attacker, an internal path, a detection lag, a bypass). A control that claims to eliminate the risk entirely is an overclaim the control-adequacy verifier refutes. If a control genuinely closes the exposure, the residual is the operational cost or the coverage gap, stated plainly.

## Judging "counters this technique" honestly

The control-adequacy verifier decides `counters_technique` as a semantic judgment: does this control credibly limit the identified exposure for the technique it claims to counter? There is no map lookup. State the causal mechanism in `limits_exposure_by` so the judgment can be made on the merits.

- A clear, correct mechanism reads as `yes` (e.g. boundary protection counters exploitation of an internet-facing endpoint from untrusted networks).
- A control offered against a behavior it does not touch reads as `no` (e.g. continuous monitoring offered as if it prevented the initial code execution).
- A control whose mechanism is not clearly argued reads as `unclear`, treated as a fail. Do not assert a link you cannot explain; explain the mechanism.

## Discipline

- **A control-domain anchor, always.** A control with no `control_domain` entry is incomplete.
- **Official names for the frameworks.** A wrong CSF Category name or NIST 800-53 control name is refuted by the `validate` helper.
- **No vacuous residual risk.** "Minimal residual risk" with no specifics reads as an overclaim; name the remaining exposure.
- **Prefer controls the org can actually apply.** Where `#scope.affected_assets` or `critical_functions` are known, favor controls that fit that environment over generic best practice.
