# Engagement intake form

> The **requestor** completes this before the scoping call. It captures logistics and baseline facts only, not objectives. The outcome-based objectives are drafted by the red team on the scoping call and recorded in the Scoping Document (the Phase 1 authorization gate).
>
> To start: run `make new-engagement NAME=<engagement-id>` (copies this template to `engagements/<id>/intake.md`), fill it in, then run `/rt-govern engagements/<id>/intake.md`. `rt-govern` reads the raw answers, runs the scoping call, and drafts the Scoping Document.
>
> Do not paste sensitive source intelligence here; keep it in its own files and hand it to `rt-intel` in Phase 2.

## Requestor

- **Engagement ID:** <ENG-YYYY-nnn>
- **Requestor name / role / team:**
- **Engagement sponsor (who can authorize and fund this):**
- **Date submitted:**

## Target

- **Target system / business unit:** (name the actual system(s); "our AI platform" is not specific enough)
- **What prompted this request?** (free text: e.g. not tested in 18 months, a specific concern, a new launch, a peer incident)

## Timing

- **Desired start date:**
- **Hard deadline and what drives it:** (or none)
- **Known change freeze / high-volume period:** (or none)

## Routing

- **Scheduled third-party TLPT cycle?** (framework; routes to that program, or internally-initiated)
- **Compliance or contractual drivers:** (SOC2, PCI, audit finding, contractual; or none)

## Testing history

- **Penetration test:** (Y/N, date, findings summary)
- **Internal red / purple team:** (Y/N, date, objectives)
- **Third-party TLPT test:** (Y/N, date, framework)

## Systemic relevance

- **Supports a designated CEF?** (Y/N; which function)
- **Resolution / recovery plan dependency?** (Y/N)
- **FMI connectivity (SWIFT / RTGS / CHIPS / Fedwire / CCP / CSD)?** (Y/N; which)
- **Payment / clearing / settlement capability?** (Y/N)

## Sensitivity

- **Regulated customer data (PII / PCI / financial)?** (Y/N)
- **Production / revenue-critical infrastructure?** (Y/N)
- **AI / ML components or agents?** (Y/N)
- **Third-party / vendor dependency in likely scope?** (Y/N; name them)

## Contacts

- **Primary technical contact:** (architecture / ops)
- **Primary business contact:** (if different from sponsor)
- **Asset owner:** (if known)

## Constraints (anything already known to be off-limits)

- **Off-limits systems, times, actions:**
- **Physical access to premises involved?** (Y/N; if yes, requires legal authorization and adds lead time)
- **Cross-border / data residency considerations:** (or none)
