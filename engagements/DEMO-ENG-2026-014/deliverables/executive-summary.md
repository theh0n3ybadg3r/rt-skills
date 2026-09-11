# Executive Summary: DEMO-ENG-2026-014

- **Engagement:** DEMO-ENG-2026-014, insider path to CRM customer PII
- **Engagement type:** Red team operation (SOC blind)
- **Classification:** Confidential
- **Prepared for:** Stakeholder (Head of Customer Data Platform)
- **Date:** 2026-08-28

> Demo deliverable. Illustrative only; do not treat as a real engagement.

A malicious insider could take the customer list and we would not have noticed. Over about eleven days a red team operator, starting from a standing engineering account, escalated privileges through an unpatched internal service, moved to the CRM application host, read customer records in bulk from the CRM datastore, and moved a minimal proof sample outside the approved data boundary. The objective was achieved.

One control fired. An EDR behavioral alert at the escalation step was investigated and dismissed in triage as a false positive within about 40 minutes. Everything after that was silent: the lateral movement, the bulk read, and the exfiltration produced nothing the SOC acted on.

What this means for the business: the crown-jewel customer PII in the CRM is reachable by an insider with standing access, and the current controls would not catch the path once the first alert is dismissed. In the wild this is a reportable breach of the retail customer PII set, with regulator notification and board attention.

The gaps are three: alert triage closed the one true positive without a second look; there is no monitoring of bulk reads at the CRM database tier; and the egress boundary neither inspected nor reviewed the outbound channel the data left over. Standing engineering access to the CRM also exceeded what the role needs, and one internal service was unpatched.

Next steps: the findings are handed to control tracking and vulnerability management with recommended remediations, the material findings are escalated to the CISO, and the red team will retest to confirm the fixes hold.
