# Engagement intake form

> Filled example (demo) for DEMO-ENG-2026-014. The requestor completes this before the scoping call. It captures logistics and baseline facts only, not objectives. The outcome-based objectives are drafted by the red team on the scoping call and recorded in the Scoping Document (the Phase 1 authorization gate). Scenario: a malicious insider reaching customer PII in the CRM datastore. Illustrative only; do not treat as a real engagement.

## Requestor

- **Engagement ID:** DEMO-ENG-2026-014
- **Requestor name / role / team:** M. Alvarez, Head of Customer Data Platform, Data Platform
- **Engagement sponsor (who can authorize and fund this):** M. Alvarez, Head of Customer Data Platform
- **Date submitted:** 2026-08-03

## Target

- **Target system / business unit:** CRM customer datastore and the CRM application tier (Customer Data Platform)
- **What prompted this request?** Sector reporting this quarter on rising financially motivated insider data theft, plus two disclosed peer breaches. The CRM PII path has not been tested against an insider with standing access.

## Timing

- **Desired start date:** 2026-08-12
- **Hard deadline and what drives it:** None; the request is intelligence-surfaced, not deadline-driven.
- **Known change freeze / high-volume period:** None in the requested window.

## Routing

- **Scheduled third-party TLPT cycle?** No; internally-initiated red team operation.
- **Compliance or contractual drivers:** None specific; general customer-PII protection obligations apply.

## Testing history

- **Penetration test:** Y, 2025-11, application-layer findings on the CRM web tier, remediated.
- **Internal red / purple team:** N, the insider-to-CRM PII path has not been exercised.
- **Third-party TLPT test:** N.

## Systemic relevance

- **Supports a designated CEF?** N.
- **Resolution / recovery plan dependency?** N.
- **FMI connectivity (SWIFT / RTGS / CHIPS / Fedwire / CCP / CSD)?** N.
- **Payment / clearing / settlement capability?** N.

## Sensitivity

- **Regulated customer data (PII / PCI / financial)?** Y, retail customer PII in the CRM datastore.
- **Production / revenue-critical infrastructure?** Y, the production CRM serves customer operations.
- **AI / ML components or agents?** N.
- **Third-party / vendor dependency in likely scope?** N.

## Contacts

- **Primary technical contact:** S. Bello, CRM Platform Engineering lead
- **Primary business contact:** M. Alvarez (as sponsor)
- **Asset owner:** Customer Data Platform (CRM datastore owner)

## Constraints (anything already known to be off-limits)

- **Off-limits systems, times, actions:** No changes to customer records; read and a minimal proof sample only. No availability impact to the production CRM.
- **Physical access to premises involved?** N.
- **Cross-border / data residency considerations:** Retrieve only a minimal PII proof sample; keep any retrieved sample within the engagement evidence store.
