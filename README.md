# Red Team Operating Model: Skills

An AI-assisted, human-led operating model that turns threat intelligence into objective-based, independently verified red team engagements. It implements a threat-informed red team methodology as composable **Skills** for Claude Code and Codex, with MITRE adversary emulation as the bridge from intelligence to an executable plan.

The program is a threat-informed, intelligence-led red team methodology: a capability-building and control-validation function, not an independent assurance function. Engagements are **objective-based, not flag- or vulnerability-based**: an objective is a business outcome with a measurable success criterion, never a technique, system name, or vulnerability class.

You invoke each phase as a slash command (`/rt-govern`, `/rt-intel`, ...). The skills are markdown instructions the coding agent follows; the bundled code is small stdlib Python helpers the agent runs (technique-ID validation, the release gate, deliverable style checks, and document conversion). Converting documents uses two extra tools: **pandoc** (a system binary, for `.docx` sources in and `.docx` deliverables out) and **pdfplumber** (a pip package, for `.pdf` sources in). Both are optional prerequisites; everything else needs only Python. There is no program to operate.

## Install (no plugin needed)

These are plain files, not a plugin or marketplace, so there is nothing to publish or register. Claude Code auto-discovers skills from a skills directory; one `make` target symlinks them there so the `/rt-*` commands appear:

```bash
make install-skills                 # links skills/rt-* into ./.claude/skills (this repo)
# make install-skills SCOPE=personal  # links into ~/.claude/skills instead
# make uninstall-skills               # remove the links
make install-agents                 # links agents/rt-* into ./.claude/agents (the verifiers)
make new-engagement NAME=ENG-2026-020  # scaffold an engagement intake from the template
```

`make install-agents` installs the sub-agents that the skills dispatch for their independent-context passes under Claude Code: `rt-engagement-verifier` (for `rt-verify`) and `rt-exposure-verifier` (for `rt-exposure`). Codex uses a fresh session instead, so it needs no agent install. Like the skills links, they live under the gitignored `.claude/`, so re-run it per machine.

Claude Code picks the skills up live (no restart), and both explicit `/rt-govern` and automatic description-matched invocation work. Run the agent from the repo root so the skills' shared paths resolve. Two lower-effort paths need no install at all: ask the agent to "read and follow `skills/rt-intel/SKILL.md`", or, on Codex, rely on the shipped `AGENTS.md` adapters. See `docs/runbook.md` for the full guide.

To give the agent the always-on operating context (the guardrails and pipeline, in force before any skill fires), place the operating-context files at the project root:

```bash
make install-agent-context DEST=.   # copies templates/CLAUDE.md + templates/AGENTS.md (refuses to clobber)
```

`templates/CLAUDE.md` (Claude Code) and `templates/AGENTS.md` (Codex) carry the human-led guardrails: run `/rt-govern` first, no autonomous offensive execution, data-class egress limits, fail-closed independent verification, and treating ingested CTI as untrusted data. They are operating context for an engagement project, distinct from any coding-style `CLAUDE.md` you keep for development.

## The eight skills

Six phase skills run the engagement lifecycle in order; `rt-verify` is cross-cutting; `rt-exposure` is standalone.

| Skill | Phase | What it produces |
| --- | --- | --- |
| `/rt-govern` | 1. Intake and Scoping | The **Scoping Document** and the Gate 1 sign-off (what is tested) |
| `/rt-intel` | 2. Threat Intelligence and Objective Design | The **Threat Profile Brief** (actor and techniques per objective) |
| `/rt-emulate` | 3. Attack Planning | The **Engagement Planning Pack** Part A and the Gate 2 (Rules of Engagement) sign-off |
| `/rt-adapt` | 4. Execution and Live Testing | The **Execution Record** (contemporaneous log, decision support only) |
| `/rt-report` | 5. Reporting | The **Engagement Report** + Executive Summary + the **Blue Team Account** and Detection Analysis |
| `/rt-handoff` | 6. Handoff and Closure | Findings routed into the enterprise systems; the engagement tracker closed |
| `/rt-verify` | cross-cutting | Independent-context reviewer that gates a phase output fail-closed |
| `/rt-exposure` | standalone | Vulnerability subject-matter expertise, outside the engagement lifecycle |

## The lifecycle and its two gates

The six phase skills write to one shared engagement artifact, `engagements/<id>/engagement.md` (schema `red-team-engagement/v3`). Each phase writes only its own section, in order, and never edits another's:

```
Phase 1  rt-govern   Intake and Scoping           -> #scoping         [Gate 1: what is tested]
Phase 2  rt-intel    Threat Intel & Objective Design -> #threat-profile
Phase 3  rt-emulate  Attack Planning              -> #planning        [Gate 2: Rules of Engagement, authorizes execution]
Phase 4  rt-adapt    Execution and Live Testing   -> #execution
Phase 5  rt-report   Reporting                    -> #report
Phase 6  rt-handoff  Handoff and Closure          -> #handoff

  cross-cutting  rt-verify    independent verifier, fail-closed -> #verification
                              (targets: scoping, threat-profile, planning, report)
  standalone     rt-exposure  vulnerability SME (its own exposure artifact, no engagement gate)
```

**Two authorization gates** govern the run, each signed by the same four approvers: the Stakeholder, the Operations Lead, the Assessment Lead, and the **CISO**. The CISO is a required approver and may approve asynchronously, but no gate clears without it.

- **Gate 1** is the Scoping Document sign-off (Phase 1). It approves _what_ is tested. No downstream skill acts without a signed `#scoping` block.
- **Gate 2** is the Rules of Engagement sign-off (Phase 3). It approves _how_ the engagement runs and authorizes execution.

Business impact is elicited from the stakeholder and validated against the enterprise business-impact analysis; the red team does not produce that analysis, and there is no business-impact-mapping phase. Material findings escalate to the CISO.

## A typical engagement

One run, start to finish. The `rt-verify` gates are the load-bearing part: nothing generative is trusted until an independent context confirms it, and the gate is fail-closed, so an unreachable catalog or an unresolved item halts the run rather than passing.

1. **Intake and Scoping.** `make new-engagement NAME=<id>` stamps `engagements/<id>/intake.md` from the template; fill in the scope, crown jewels, data class, and intel sources. Then `/rt-govern engagements/<id>/intake.md` elicits and validates the business impact, drafts measurable objectives, and records the **Gate 1** sign-off in the Scoping Document. Nothing downstream runs without it.
2. `/rt-verify` (target scoping), **in a fresh context**, confirms each objective is an outcome with a measurable success criterion. Resolve anything refuted, then re-run until the gate is `ready`.
3. **Threat Intelligence and Objective Design.** `/rt-intel` selects an intelligence-justified actor per objective and maps that actor's ATT&CK/ATLAS/AADAPT techniques with verbatim citations, then writes the Threat Profile Brief. It enriches the approach; it does not change the signed intent.
4. `/rt-verify` (target threat-profile) re-derives each mapping and gates fail-closed.
5. **Attack Planning.** `/rt-emulate` turns the signed objectives and the Threat Profile into the Engagement Planning Pack Part A (a hypothesized attack path per objective) and records the **Gate 2** Rules of Engagement sign-off that authorizes execution. It references, but does not author, the human-owned infrastructure, procurement, and legal artifacts.
6. `/rt-verify` (target planning) gates the plan the same way.
7. **Execution and Live Testing (human-led).** `/rt-adapt` structures and appends the contemporaneous log, and proposes ranked, validated variant options when a technique is blocked or detected. The operator decides and executes; the tool proposes and records, and never fabricates the log.
8. **Reporting.** `/rt-report` reconciles the Execution Record against the Blue Team Account (the SOC's own account, captured before any disclosure) to measure unaided detection, establishes findings that name systems, controls, and processes but never an individual, maps each to a NIST CSF / NIST SP 800-53 control domain, and renders the Engagement Report and Executive Summary. Materiality is a human determination; material findings escalate to the CISO.
9. `/rt-verify` (target report) confirms each finding traces to the record and that the Blue Team Account was captured before disclosure.
10. **Handoff and Closure.** `/rt-handoff` routes each finding into the enterprise system that will own it (technical vulnerabilities to vulnerability management, control or process failures to control tracking), hands the retest team its test cases, confirms cleanup and attacker-infrastructure decommission, and closes the engagement tracker. The enterprise systems, not this artifact, own remediation status.

The step-by-step operator guide is `docs/runbook.md`, and `docs/cross-provider-verification.html` covers running the verify pass on a separate provider (for example Codex on a GPT model) for cross-vendor independence. Worked examples ship under `engagements/DEMO-ENG-2026-014/` (a full engagement on the `red-team-engagement/v3` schema) and `exposures/DEMO-CVE-2026-0001/` (a standalone exposure assessment).

## Standalone: vulnerability exposure (`/rt-exposure`)

Aside from a full engagement, the red team is often asked for subject-matter expertise on a newly disclosed vulnerability: dissect it, judge whether we are exposed, and say what compensating controls limit that exposure. `/rt-exposure` (alias `rt-vuln`) does exactly that, standalone. It does not require an `rt-govern` authorization or touch the engagement artifact; it reads the advisory/CVE files you give it and writes its own assessment under `exposures/<vuln-id>/exposure.md`.

- **Dissects** the weakness (CWE), affected surface, exploitation path (mapped to ATT&CK/ATLAS/AADAPT), and severity signals (CVSS/EPSS/KEV), each grounded in a verbatim quote from a source.
- **Assesses exposure** against your critical functions and assets.
- **Proposes compensating controls**, each mapped to a **NIST CSF** and/or **NIST SP 800-53** control domain, with an explicit "limits exposure by ..." claim and a stated residual risk.
- **Gates on two independent verifiers.** One re-checks the dissection (claims cited, IDs valid); one re-checks the controls (each genuinely counters the identified technique, no overclaim, residual risk stated). Both run in fresh contexts and, where the data class permits, on a different model than the producer, for uncorrelated errors. The assessment is ready only when both gate fail-closed.

Input is advisory/CVE files (md/html/pdf/txt, converted locally like `rt-intel`), one assessment per run, no live fetch. See `skills/rt-exposure/SKILL.md`.

## Frameworks and trust

Technique mappings are validated against three MITRE offensive frameworks so nothing invented slips through:

- **ATT&CK Enterprise** and **ATLAS** (AI/ML systems): fetched live from MITRE, always current.
- **AADAPT** (digital-asset / payment tech): vendored and version-pinned (no live endpoint). Directly relevant to financial-sector custody and payments.

The taxonomy is chosen by target type: ATLAS when the AI system itself is the subject of the test, AADAPT for payment / clearing / settlement infrastructure, ATT&CK otherwise. OWASP is referenced as a vocabulary for naming a web/application vulnerability class in a finding, but an OWASP-driven scope is a penetration test and is redirected to that function, not run here.

For the control-domain mapping in reporting (`rt-report`) and in exposure assessments (`rt-exposure`), control IDs are validated the same way against **NIST CSF 2.0** and **NIST SP 800-53 Rev 5** (both vendored). The split that makes verification trustworthy: the agent does the reading and judgment (which techniques an advisory describes, whether a quote supports a mapping, whether a control counters the exposure); the deterministic `validate` helper checks everything checkable (does the ID exist, does the name match, is the gate satisfied). Wrong or invented IDs are caught by code, not trusted to the model.

The trust floor, in force throughout:

- **Verbatim-quote contract:** no quote, no claim. Every actor and technique citation is a verbatim substring of a cited source.
- **Deterministic ID validation** by `validate.py`: only a real technique or control ID whose name matches its catalog is confirmed.
- **Fail-closed independent verification:** `rt-verify` runs in a fresh context that never saw the producer's reasoning, and an unreachable catalog gates the run rather than passing unverified data.
- **Human-in-command:** no autonomous offensive execution; the operator decides and executes, the skills propose and record.
- **Data-class egress** with the honest hosted-model limit (see below).

## Layout

```
skills/
  _shared/references/   red-team-engagement-v3.md (artifact schema), framework-mapping.md,
                        adversary-mindset.md, writing-style.md, degradation.md
  _shared/scripts/      validate.py (validation + release gate), export.py (optional machine-format renderer),
                        check_doc_style.py (deliverable style check), pandoc_convert.py (docx conversion),
                        pdf_convert.py (pdf conversion), ingest_common.py (shared ingest helpers),
                        sync_aadapt.py + aadapt-catalog.json, sync_nist80053.py + nist-800-53-catalog.json,
                        sync_csf.py + nist-csf-catalog.json (+ tests)
  rt-govern/            SKILL.md + AGENTS.md + references/   (Phase 1)
  rt-intel/             SKILL.md + AGENTS.md + references/   (Phase 2)
  rt-emulate/           SKILL.md + AGENTS.md + references/   (Phase 3)
  rt-adapt/             SKILL.md + AGENTS.md + references/   (Phase 4)
  rt-report/            SKILL.md + AGENTS.md + references/   (Phase 5)
  rt-handoff/           SKILL.md + AGENTS.md + references/   (Phase 6)
  rt-verify/            SKILL.md + AGENTS.md + references/personas/  (cross-cutting)
  rt-exposure/          SKILL.md + AGENTS.md + references/personas/ (standalone vulnerability SME)
agents/                 rt-engagement-verifier.md (rt-verify's verifier), rt-exposure-verifier.md
                        (rt-exposure's verifier); the sub-agents dispatched under Claude Code
engagements/            per-engagement artifacts (gitignored runtime data; a tracked worked example)
exposures/              per-vulnerability assessments from rt-exposure (gitignored runtime data)
templates/              INTAKE.md (engagement brief) + CLAUDE.md + AGENTS.md (operating context)
MAINTENANCE.md          how the catalogs stay current
```

Logic lives in portable `references/*.md`; `SKILL.md` (Claude Code) and `AGENTS.md` (Codex) are thin adapters over the same references. See `skills/_shared/references/degradation.md`.

## Deliverables

The Phase 5 deliverables are the human **Engagement Report** and the **Executive Summary**, with the **Blue Team Account** captured and retained separately. Each is produced human-ready:

- **Markdown**, the default working form.
- A **self-contained HTML** rendering (inline CSS, no external assets, light/dark aware; print it to PDF from any browser).
- An editable **docx** rendered with pandoc.

Machine formats are **optional and additive**, not mandated by the methodology. Where a downstream SIEM, threat-intel, or ML pipeline wants a structured export, `export.py` produces JSON, a STIX 2.1 bundle, and ATT&CK Navigator layers from the already-validated artifact. `export.py` is being updated for the v3 schema in a later tooling pass, so do not rely on its current output shape. See `skills/rt-report/references/machine-formats.md`.

## Run the checks

```bash
make test          # helper unit tests (offline; docx/pdf round-trips skip when pandoc/pdfplumber are absent)
make check-docs    # flag AI-written tells in the docs and deliverables
make format        # prettier --write on markdown

cd skills/_shared/scripts

# Validate technique or control mappings against catalog data (a JSON list of {id, framework, name})
python3 validate.py --entries entries.json

# The deterministic release gate over verification verdicts (fail-closed)
python3 validate.py --gate verification.json --expect-ids ids.json

# Catalog freshness (versions + AADAPT staleness)
python3 validate.py --catalog-info
```

## Maintenance

ATT&CK and ATLAS self-update (fetched live, cached 24h). The vendored catalogs are re-synced when their sources ship a new version: AADAPT with `sync_aadapt.py`, NIST SP 800-53 with `sync_nist80053.py`, and NIST CSF with `sync_csf.py` (all under `skills/_shared/scripts/`). See `MAINTENANCE.md`.

## Honest limitations

- With a hosted model, the reasoning steps send source content to the model provider; the data-class controls mean "no egress beyond the authorized model host", not "nothing leaves the machine". For a hard guarantee, run a local model.
- Live validation depends on reaching MITRE; an outage or air-gap gates the run (fail-closed) rather than passing unverified data.
- `rt-verify`'s independence is procedural, enforced by running it in a fresh context that never saw the producer's reasoning, not by attestation. The red team and the tested function share a reporting line; the Blue Team Account is captured separately so the tested function's own account is not edited by the red team.
