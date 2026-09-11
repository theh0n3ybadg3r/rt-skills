# MOCK CTI brief: malicious insider data theft in financial services

> MOCK SOURCE, FOR THE DEMO ENGAGEMENT ONLY. This is a fabricated intelligence brief written to illustrate the verbatim-citation contract in DEMO-ENG-2026-014. It is not real threat intelligence and must not be treated as such. Reference id: MOCK-CTI-INSIDER-2026. Recency: Q3 2026 (mock).

## Actor and motivation

Financially motivated malicious insiders in financial services increasingly monetize customer data by reselling it to third parties. These insiders are typically competent engineers who hold standing access and rely on legitimate tools rather than custom malware, keeping their operational footprint low. Their opsec is patient and covert: they work within their normal access patterns and across days rather than in a single noisy burst.

## Observed tradecraft

They begin from valid accounts they already hold rather than phishing for new credentials. Where their standing role is insufficient, they exploit an unpatched internal service to escalate privileges. They move to target systems over sanctioned remote services rather than deploying new tooling. Once positioned, they collect bulk records directly from information repositories such as CRM datastores. They exfiltrate the data over an allowed outbound channel that blends with normal traffic.

## What they avoid

They avoid zero-day exploitation and noisy domain-wide credential attacks, which draw attention and are inconsistent with a low-profile insider who is trying to stay within expected behavior.
