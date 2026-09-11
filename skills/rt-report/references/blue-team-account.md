# Blue Team Account

The Blue Team Account is the SOC's own account of what it detected, unaided, during the engagement. It is completed by the SOC / blue team **before seeing the red team record**. Its validity depends entirely on being captured before disclosure. It is a standalone retained deliverable, attributed separately from the red team's assessment. rt-report records and references it; **rt-report does not write it**.

## Inputs the SOC receives

Only two: the time window (the dates) and the broad scope (the area in scope). **Never** the attack path, techniques, systems, or timestamps. Giving the SOC more than the window and broad scope changes what the account measures (see the exceptions).

## Capture order

Captured first, before any disclosure, from the SOC's own experience. The red team reconciles it against the Execution Record afterward, and that reconciliation is the Detection Analysis (`#report.detection_analysis`). Capturing the account after showing the SOC the execution record is a defined failure mode.

## Exception states

`blue_team_account.exception` records when the account measures something other than unaided detection:

- `none`: a true unaided measure over the full window.
- `disclosed-at`: testing was disclosed mid-engagement, so the account covers the pre-disclosure period only; the unaided measure ends at the disclosure.
- `non-blind`: the engagement was not truly blind, so this is a collaborative detection review, not an unaided measure.
- `limited-prompt`: the SOC needed more than the window and broad scope, so the result measures loggability (whether the activity was there to be found), not unaided detection.

`captured_before_disclosure` is `true` only when the account was completed before the SOC saw the engagement record.

## What the account contains

1. **What was observed**: over the period, what drew attention (alerts, anomalies, user reports), each with what, when, and source.
2. **What was investigated**: which observations were investigated, and the outcome of each.
3. **What was escalated**: what was escalated, to whom, and when.
4. **What was dismissed**: what was seen and closed, and on what basis. A dismissed true positive is a process finding.
5. **What was not seen**: anything the SOC would have expected to catch and did not, in retrospect but still before seeing the red team record.
6. **SOC narrative**: in the SOC's own words, how the period looked from the defensive side.

## How rt-report uses it

rt-report reconciles the account against the Execution Record to produce the Detection Analysis, distinguishing a coverage gap (nothing was watching) from a process gap (a control fired but the response failed). In `#report.blue_team_account` it records `captured_before_disclosure`, `exception`, the `account`, and the `ref` to the retained Blue Team Account deliverable. In the Engagement Report the account is Appendix F, and Section 5 attributes it separately from the red team's assessment.
