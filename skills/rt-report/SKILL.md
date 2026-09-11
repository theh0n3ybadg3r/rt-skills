---
name: rt-report
description: >-
  Phase 5 (Reporting) of the threat-informed red team methodology. It reconciles the Execution Record against the Blue Team Account (the SOC's own account, captured before any disclosure) to measure unaided detection, establishes findings that name systems, controls, and processes but never an individual, and records materiality as a human determination. Each finding carries a recommended remediation and a validated NIST CSF / NIST SP 800-53 control-domain mapping; material findings escalate to the CISO. It writes the Report as the #report block (section 5) and renders the human Engagement Report plus the Executive Summary. It assembles and records; it does not invent findings, severities, or detection conclusions.
---

# rt-report

Phase 5, Reporting. After execution concludes, this skill measures unaided detection, establishes findings, and produces the human-readable report. It reconciles the Execution Record against the Blue Team Account, records each finding with a recommended remediation and a control-domain mapping, and renders the Engagement Report and the Executive Summary. It writes the Report as the `#report` block (section 5).

rt-report **assembles and records; it does not invent**. Findings, severities, and detection conclusions come from the record and from the humans who own them. Materiality is a human determination (the Operations Lead). No individual is ever named as the cause of a failure. The Blue Team Account is captured before any disclosure. Control-domain ids are validated by the `validate` helper.

Shared assets:

- Artifact schema (`#report`, section 5): `skills/_shared/references/red-team-engagement-v3.md`. It consumes sections 1 (`#scoping`), 2 (`#threat-profile`), 3 (`#planning`), 4 (`#execution`), and any `#verification` block.
- Control-framework ID rules (`nist-csf`, `nist-800-53`): `skills/_shared/references/framework-mapping.md`.
- Deliverable structures: `references/engagement-report.md` (the Engagement Report's 10 sections and Appendices A-F) and `references/blue-team-account.md`.
- Optional machine exports (additive, not required): `references/machine-formats.md`.
- Writing standard for the deliverables (no AI tells): `skills/_shared/references/writing-style.md`.
- Bundled helpers this skill runs: `skills/_shared/scripts/validate.py` (control-domain id validation), `skills/_shared/scripts/check_doc_style.py` (deliverable style check), and `skills/_shared/scripts/pandoc_convert.py` (docx renderings; requires pandoc on PATH).

## Procedure

1. **Confirm the record is complete.** Read sections 1 (`#scoping`), 2 (`#threat-profile`), 3 (`#planning`), 4 (`#execution`), and any `#verification` block of `engagements/<engagement-id>/engagement.md`. Phase 5 needs a complete Execution Record and its evidence. If execution has not concluded, or the record or evidence is incomplete, stop and say what is missing; write nothing. Note `data_class` from `#scoping` and keep everything under it.

2. **Record the Blue Team Account, captured before disclosure.** The Blue Team Account is the SOC's own account of what it detected unaided. It is captured **first, before any disclosure**, from the SOC's own experience, with the SOC given only the time window and the broad scope, never the attack path, techniques, systems, or timestamps. It is a standalone retained deliverable that rt-report records and references; **rt-report does not invent it**. Populate `blue_team_account`:
   - `captured_before_disclosure`: `true` only when the account was completed before the SOC saw the engagement record.
   - `exception`: `none | disclosed-at | non-blind | limited-prompt`. `disclosed-at` means only the pre-disclosure period is an unaided measure; `non-blind` means a collaborative detection review, not an unaided measure; `limited-prompt` means the SOC needed more than the window and broad scope, so the account measures loggability, not unaided detection.
   - `account`: the SOC's own experience.
   - `ref`: the retained Blue Team Account deliverable. See `references/blue-team-account.md`.

3. **Reconcile the record into the Detection Analysis.** For each objective, reconcile the Execution Record against the Blue Team Account. **Unaided detection is the measure**, and a disclosure to stand down a response ends the unaided measurement from that point (see `#execution.disclosure_events`). Populate `detection_analysis` per objective with `objective_id`, `unaided_detected`, `stage` (where in the path it was detected), `gap_type` (`coverage` = nothing was watching, `process` = a control fired but the response failed, `none`), and `reconciliation` (execution record vs blue-team account, with the blue team's account **attributed separately** from the red team's assessment).

4. **Record the objective outcomes.** For each objective, populate `objective_outcomes` with `objective_id`, `outcome` (`achieved | partial | not-achieved`) against the stated success criterion, and an `evidence` reference.

5. **Establish findings.** Each finding is drawn from the record, not invented. Populate `findings`:
   - `id` (e.g. `F-1`), `source` (`attack-path | off-path | detection-gap`), and `objective_id` (or `null` for an off-path finding).
   - `description`: names the systems, controls, and processes involved and **never an individual** (non-attribution). State detection failures plainly.
   - `recommended_remediation`: written to be actionable to the owner who will receive it in the enterprise system.
   - `control_domain`: an array mapping to NIST CSF and/or NIST SP 800-53, each `{framework, id, name}` (`nist-csf | nist-800-53`), validated in step 7.
   - `severity`: **human-set**; rt-report records it, it does not score it.
   - `material` + `materiality_basis`: a **human determination by the Operations Lead**, which rt-report records, does not set.
   - `suggested_owner`. Distinguish a control/process finding from a discrete vulnerability. **Off-path vulnerabilities are recorded and routed, not scored as the engagement outcome** (`source: off-path`); they go to per-application vulnerability management in Phase 6.

6. **Record escalation and limitations.** Material findings escalate to the CISO: populate `escalation` with `{finding_id, escalated_to, date}` for each. Populate `limitations` with the time, scope, and intel/capability constraints, **including any disclosure effect on the unaided-detection measure**.

7. **Validate the control-domain ids.** Collect every `control_domain` entry as a JSON list of `{"id": ..., "framework": ..., "name": ...}`, write it to a scratch path **outside** `engagements/`, and run:

   ```bash
   python3 skills/_shared/scripts/validate.py --entries <tmp.json>
   ```

   Correct or drop any id the helper refutes, then delete the temp file. A control-domain id that cannot be confirmed is not presented as a validated mapping.

8. **Render the Engagement Report and the Executive Summary.** Following `references/engagement-report.md`, render the human documents in two formats each:
   - `<deliverable>.md`: markdown, the default working form.
   - `<deliverable>.html`: a self-contained HTML rendering (inline CSS, no external assets, ASCII-clean, light/dark aware). A reader can print it to PDF from any browser.

   The Engagement Report carries the fixed 10 sections (Executive summary, Scope and objectives, Attack narrative or the validation record for a purple team exercise, Objective outcomes, Detection and response performance, Findings, Vulnerabilities outside the attack path, Cleanup status, Deviations, Limitations) plus Appendices A-F (A Scoping Document, B Threat Profile Brief, C Evidence index, D Execution Record, E MITRE technique mapping, F Blue Team Account). Also produce the Executive Summary for the Stakeholder. Write to `engagements/<engagement-id>/deliverables/` using `engagement-report.{md,html}` and `executive-summary.{md,html}`. Do not modify the engagement artifact's own sections.

   Write the prose to the deliverable standard in `skills/_shared/references/writing-style.md`: plain professional analyst English, US English spelling, no em dashes, no jargon or unearned superlatives, no stock phrases, every statement bound to the artifact. Only present content the record supports; where a section has a gap, state it plainly rather than filling it.

9. **Check the deliverable prose for AI tells.** Run the style checker on the rendered human documents and revise anything it flags (an em dash, a jargon word, a stock phrase), keeping the meaning:

   ```bash
   python3 skills/_shared/scripts/check_doc_style.py engagements/<engagement-id>/deliverables/*.md engagements/<engagement-id>/deliverables/*.html
   ```

   It exits non-zero while any tell remains. The judgment tells it cannot catch (padding, vague claims) are still yours to remove per `writing-style.md`.

10. **Render editable docx (where pandoc is present).** After the markdown is finalized (style-checked and revised), render Word versions for readers who want them:

    ```bash
    python3 skills/_shared/scripts/pandoc_convert.py to-docx engagements/<engagement-id>/deliverables/*.md
    ```

    This writes each `<deliverable>.docx` beside its markdown. pandoc runs locally and makes no network calls; the docx files carry engagement content and follow the same handling as the `.md` and `.html`. If pandoc is not on PATH, the helper exits with an actionable message and the markdown and HTML remain the deliverables.

11. **Write `#report` (section 5).** Write only section 5; never modify another skill's block. Record `control_provenance` (the `nist-csf` and `nist-800-53` catalog versions), `blue_team_account`, `detection_analysis`, `objective_outcomes`, `findings`, `escalation`, and `limitations`. Hand off to `rt-verify` with target `report`.

12. **Optional machine formats (additive, not required).** The methodology mandates no machine-format deliverable. Where a downstream SIEM, threat-intel, or ML pipeline wants a structured export, `skills/_shared/scripts/export.py` produces JSON, a STIX 2.1 bundle, and ATT&CK Navigator layers. See `references/machine-formats.md`. `export.py` is being updated for the v3 schema and the real deliverable names in a later tooling pass, so do not rely on its current output shape here; the human Engagement Report and Executive Summary are the Phase 5 deliverables.

## Boundaries

- **Assemble and record; do not invent.** rt-report does not invent findings, severities, or detection conclusions. It reconciles the record and renders it. If a required section is missing or gated, say so in the document rather than filling the gap.
- **Unaided detection is the measure, captured before disclosure.** The Blue Team Account is captured first, from the SOC's own experience, before any disclosure. A disclosure to stand down a response ends the unaided measurement from that point, and that effect is recorded in `limitations`.
- **Non-attribution.** No individual is ever named as the cause of a failure. Findings name systems, controls, and processes.
- **Materiality is a human determination.** The Operations Lead sets `material` and `materiality_basis`; severity is human-set; rt-report records them, it does not set them. Material findings escalate to the CISO.
- **Control-domain ids are validated.** Every `nist-csf` / `nist-800-53` mapping is checked by the `validate` helper before it is presented as validated.
- Prose you author here follows the deliverable standard in `skills/_shared/references/writing-style.md`.
