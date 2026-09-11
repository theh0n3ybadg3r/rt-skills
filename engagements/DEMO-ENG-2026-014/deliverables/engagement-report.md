# Engagement Report: DEMO-ENG-2026-014

- **Engagement:** DEMO-ENG-2026-014, insider path to CRM customer PII
- **Engagement type:** Red team operation (SOC blind)
- **Classification:** Confidential
- **Report version:** 1.0
- **Prepared by:** J. Rivera (Red Team Lead)
- **Peer-reviewed by:** K. Sato
- **Date:** 2026-08-28
- **Distribution:** Stakeholder (Head of Customer Data Platform), Operations Lead, Assessment Lead, CISO

> Demo deliverable. Illustrative only; do not treat as a real engagement.

## 1. Executive summary

A malicious insider could take the customer list and we would not have noticed. Over about eleven days a red team operator, starting from a standing engineering account, escalated privileges through an unpatched internal service, moved to the CRM application host, read customer records in bulk from the CRM datastore, and moved a minimal proof sample outside the approved data boundary. The objective was achieved.

One control fired. An EDR behavioral alert at the escalation step was investigated and dismissed in triage as a false positive within about 40 minutes. Everything after that was silent: the lateral movement, the bulk read, and the exfiltration produced nothing the SOC acted on. The gaps are alert triage, database-tier monitoring of the CRM, and egress inspection at the boundary. The findings are handed to control tracking and vulnerability management with recommended remediations, and we will retest to confirm the fixes.

## 2. Scope and objectives

The engagement was authorized under a signed Scoping Document (Gate 1) and a signed Rules of Engagement (Gate 2), each approved by the Stakeholder, the Operations Lead, the Assessment Lead, and the CISO.

- **Objective (OBJ-1):** a malicious insider reaches and exfiltrates customer PII from the CRM datastore without being detected.
- **Success criterion:** a minimal customer PII proof sample retrieved from the CRM datastore and moved outside the approved data boundary, confirmed by record count and content, with no access or egress alert acted on after the initial access step.
- **Crown jewel:** the CRM customer datastore.
- **Engagement type:** red team operation, because the open question was whether an end-to-end insider path would be detected unaided, not a collaborative walk-through.
- **Assumed actor:** a financially motivated malicious insider (engineering) with standing access, selected from sector intelligence on insider data theft. The actor uses legitimate tools and sanctioned pathways rather than custom malware, and works patiently across days.
- **Out of scope (a reader might assume it was tested):** any change to customer records, availability impact to the production CRM, and the customer-facing web front end beyond the CRM application tier. The engagement retrieved a minimal proof sample only.

## 3. Attack narrative

The path followed five steps, each a validated ATT&CK technique consistent with the assumed insider.

1. **Valid accounts (T1078).** The operator authenticated to the internal remote-access path using the standing engineering account, within its normal access pattern. Outcome: success.
2. **Exploitation for privilege escalation (T1068).** The operator exploited an unpatched internal service to escalate toward the CRM application tier. Outcome: detected. An EDR behavioral alert fired here.
3. **Remote services (T1021).** Using the escalated access, the operator moved to the CRM application host over a sanctioned remote service, without new tooling. Outcome: success.
4. **Data from information repositories (T1213).** The operator queried the CRM datastore for a bulk set of customer records and reduced the result to a minimal proof sample. Outcome: success.
5. **Exfiltration over C2 channel (T1041).** The operator moved the minimal proof sample outside the approved data boundary over an allowed outbound channel. Outcome: success, satisfying the OBJ-1 success criterion.

The path ran from 2026-08-12 to 2026-08-22.

## 4. Objective outcomes

| Objective | Outcome | Evidence |
| --- | --- | --- |
| OBJ-1: insider reaches and exfiltrates CRM PII undetected | Achieved | A minimal customer PII proof sample was confirmed outside the approved data boundary by record count and content (Execution Record 2026-08-22, evidence index). |

## 5. Detection and response performance

The Blue Team Account is the SOC's own account, captured before any disclosure, with the SOC given only the time window and the broad engineering-to-datastore scope. It is attributed to the SOC and stated here separately from the red team's assessment.

**Blue Team Account (SOC, attributed separately).** One EDR behavioral alert on an internal service on day 3 drew attention and was investigated, then closed as a false positive within about 40 minutes. Nothing else over the period was escalated. The lateral movement over the sanctioned remote service, the bulk read from the CRM datastore, and the outbound transfer were not seen.

**Red team assessment (reconciliation).** The Execution Record places the escalation at 2026-08-14, matching the dismissed EDR alert in the SOC account. One control fired, at the escalation step, and was dismissed in triage. Every later stage was unseen. Detection at the escalation step was unaided but the response failed at triage, which is a process gap rather than a coverage gap. The absence of any signal at the database read and at the egress boundary are coverage gaps: nothing was watching those stages.

## 6. Findings

Each finding names systems, controls, and processes, never an individual. Materiality is a determination of the Operations Lead, recorded here. Material findings were escalated to the CISO on 2026-08-26.

### FND-1: the one alert that fired was dismissed in triage (detection gap, process)

The EDR behavioral alert at the escalation step was closed as a false positive within about 40 minutes. Triage had no secondary-review gate for a behavioral alert on an internal service, so a true positive was closed and the rest of the path proceeded unseen. Role in the path: the single opportunity to stop the operation. Recommended remediation: add a secondary-review gate before a behavioral alert on an internal service can be closed as a false positive, and feed dismissed behavioral alerts into a periodic review. Control domain: NIST CSF DE.AE (Adverse Event Analysis), NIST CSF RS.AN (Incident Analysis). Severity: high. Material: yes. Suggested owner: SOC / detection engineering.

### FND-2: standing engineering access to the CRM exceeded least privilege (attack path)

The standing engineering account held access to the CRM datastore beyond what the role required, which let the insider path reach and read customer records once positioned. Role in the path: the precondition for the read. Recommended remediation: constrain standing engineering access to the CRM datastore to least privilege, and review and recertify entitlements to the CRM customer records. Control domain: NIST CSF PR.AA (Identity Management, Authentication, and Access Control), NIST SP 800-53 AC-6 (Least Privilege). Severity: high. Material: yes. Suggested owner: IAM / access governance.

### FND-3: no database-tier monitoring of the CRM datastore (detection gap, coverage)

There was no database-tier monitoring of the CRM datastore, so the bulk read of customer records produced no alert. Role in the path: the step that turned access into data. Recommended remediation: add database-tier monitoring and alerting on bulk or unusual reads of the CRM customer records, tuned to the normal query profile. Control domain: NIST CSF DE.CM (Continuous Monitoring), NIST SP 800-53 SI-4 (System Monitoring). Severity: high. Material: yes. Suggested owner: detection engineering / data platform.

### FND-4: exfiltration over an allowed channel crossed the boundary undetected (detection gap, coverage)

The minimal PII proof sample left over an allowed outbound channel with no boundary inspection and no review of the egress records, so the exfiltration was not detected. Role in the path: the step where the data left. Recommended remediation: apply boundary inspection or data-loss detection to the allowed outbound channels that cross the approved data boundary, and add periodic review of egress records for customer data. Control domain: NIST SP 800-53 SC-7 (Boundary Protection), NIST SP 800-53 AU-6 (Audit Record Review, Analysis, and Reporting). Severity: high. Material: yes. Suggested owner: network security / SOC.

### FND-5: an unpatched internal service permitted the escalation (attack path, discrete vulnerability)

An unpatched internal service permitted the privilege escalation at the escalation step. This is a discrete technical vulnerability in one internal service, distinct from the detection and access-control gaps, and the escalation was a failure to enforce the account's approved access. Role in the path: the escalation mechanism. Recommended remediation: patch the internal service to remediate the escalation vulnerability, and confirm the fix through the service's normal patch pipeline. Control domain: NIST SP 800-53 AC-3 (Access Enforcement). Severity: medium. Material: no. Suggested owner: platform engineering / vulnerability management. Routed to vulnerability management.

## 7. Vulnerabilities outside the attack path

None recorded. Every finding in this engagement lay on the attack path or was a detection gap on it; no discrete off-path vulnerability was found and set aside.

## 8. Cleanup status

The two engagement artifacts introduced on the target, the temporary local account used for the escalation and the staged proof-sample file on the CRM application host, were removed at conclusion. The only attacker infrastructure was the operator remote-access session, with no external domains; it was decommissioned at execution close. No open cleanup item remains.

## 9. Deviations

None. The engagement ran within the signed Rules of Engagement, with no departure requiring an approver's rationale.

## 10. Limitations

- The threat intelligence is a mock sector-level brief, not attribution to a named group; the assumed actor is an insider class.
- By scope, the engagement retrieved a minimal PII proof sample only, so it demonstrates the path rather than the full data volume an insider could take.
- No disclosure to stand down a response occurred, so the unaided-detection measure covers the full window.

## Appendix A: Scoping Document

See section 1 (`#scoping`) of `engagement.md`. OBJ-1 as approved, with the success criterion, crown jewel, and Gate 1 sign-off.

## Appendix B: Threat Profile Brief

See section 2 (`#threat-profile`) of `engagement.md`. The malicious insider actor and the five techniques, each with a verbatim citation to the source brief.

## Appendix C: Evidence index

The engagement evidence store referenced by the Execution Record, including the confirmation of the minimal PII proof sample outside the boundary (2026-08-22).

## Appendix D: Execution Record

See section 4 (`#execution`) of `engagement.md`. The contemporaneous log, detection observation, cleanup, attacker infrastructure, and recovered-secret record.

## Appendix E: MITRE technique mapping

| Step | Technique                             | ID    | Framework |
| ---- | ------------------------------------- | ----- | --------- |
| 1    | Valid Accounts                        | T1078 | ATT&CK    |
| 2    | Exploitation for Privilege Escalation | T1068 | ATT&CK    |
| 3    | Remote Services                       | T1021 | ATT&CK    |
| 4    | Data from Information Repositories    | T1213 | ATT&CK    |
| 5    | Exfiltration Over C2 Channel          | T1041 | ATT&CK    |

Excluded from the profile: zero-day exploitation of a public-facing service (T1190) and noisy domain-wide credential attacks (T1110), both inconsistent with this insider.

## Appendix F: Blue Team Account

The retained Blue Team Account deliverable, `Blue Team Account / DEMO-ENG-2026-014`, captured before disclosure. Summarized in section 5.
