# Red Team Skills: User Guide and Runbook

How to operate the eight-skill red team operating model end to end: take an intake request through six phases to a verified Engagement Report, then hand the findings to the enterprise systems that own them. The program implements a threat-informed, intelligence-led red team methodology: a capability-building and control-validation function, not an independent assurance function. Engagements are **objective-based**, not flag- or vulnerability-based. Technique mappings validate against ATT&CK, ATLAS, and AADAPT; control-domain mappings against NIST CSF and NIST SP 800-53.

For the design, see `docs/architecture.html`. For the why, see `docs/product-overview.html`. To run the verify pass on a separate model provider (Codex on a GPT model) for cross-vendor independence, see `docs/cross-provider-verification.html`.

## Prerequisites

- Python 3.9 or newer on PATH. The bundled Python helpers are stdlib only, so the core pipeline needs no `pip install`.
- `pandoc` on PATH, for document conversion: reading `.docx` intel sources, and rendering the human deliverables (plus the intake and engagement artifact) to `.docx`. Install it from `https://pandoc.org/installing.html`.
- `pdfplumber` (a pip package) for reading `.pdf` intel sources: `pip install -r requirements.txt`.
- Both converters are optional. Without them the rest of the pipeline still runs: a missing pandoc stops the docx steps with a clear message, and a missing pdfplumber makes `rt-intel` fall back to reading PDFs natively (with less reliable quotes and locators).
- Network access to `raw.githubusercontent.com` and `api.github.com` for live ATT&CK and ATLAS validation. Catalogs are cached under `~/.cache/red-team-skills/catalogs/`. AADAPT, NIST CSF, and NIST SP 800-53 are vendored, so they need no network.

## Install (no plugin)

The skills are plain files, not a plugin or marketplace, so there is nothing to publish or register. Both Claude Code and Codex discover skills from a directory of `SKILL.md` folders; `make` targets symlink these there. Claude Code registers `/rt-*` slash commands from `.claude/skills`; Codex scans `.agents/skills` and invokes the same skills as `$rt-*`:

```bash
make install-skills                    # links skills/rt-* into ./.claude/skills (Claude Code)
make install-skills SCOPE=personal     # links into ~/.claude/skills instead
make uninstall-skills                  # remove the links
make list-skills                       # show what is installed
make install-codex-skills              # links skills/rt-* into ./.agents/skills (Codex)
make install-codex-skills SCOPE=personal # links into ~/.agents/skills instead
make uninstall-codex-skills            # remove the links
make list-codex-skills                 # show what is installed
make install-agents                    # links agents/rt-* into ./.claude/agents (the verifiers)
make list-agents                       # show installed agents
make new-engagement NAME=ENG-2026-020  # scaffold an engagement intake from the template
make render-docx ENG=<id>              # render an engagement's deliverables + intake + engagement to docx (needs pandoc)
```

Claude Code picks the skills up live (no restart); both explicit `/rt-govern` and automatic description-matched invocation then work. On Codex, `make install-codex-skills` symlinks the same skills into `.agents/skills` (Codex scans it from the working directory up to the repo root and follows the links); restart Codex if they do not appear, then invoke a skill with a `$` mention (`$rt-govern`) or browse with `/skills`. There is no `/rt-govern` slash command in Codex, and Codex custom prompts (`~/.codex/prompts`) are deprecated. Both install dirs are gitignored, so `make install-skills` and `make install-codex-skills` are per-checkout steps. Run the agent from the repo root so each skill's shared paths (`skills/_shared/...`) resolve.

`make install-agents` symlinks the verifier sub-agents (also under the gitignored `.claude/`, so it is a per-checkout step too): `rt-engagement-verifier` (dispatched by `rt-verify`) and `rt-exposure-verifier` (dispatched by `rt-exposure`). Each skill dispatches its verifier under Claude Code to get the independent context its trust gate requires; Codex has no equivalent named agent and uses a fresh `spawn_agent` or session instead, so it needs no agent install.

Give the agent the always-on operating context (guardrails and pipeline, in force before any skill fires) by placing the operating-context files at the project root:

```bash
make install-agent-context DEST=.   # copies templates/CLAUDE.md + templates/AGENTS.md (refuses to clobber)
```

`templates/CLAUDE.md` (Claude Code) and `templates/AGENTS.md` (Codex) carry the human-led guardrails (run `rt-govern` first, no autonomous offensive execution, data-class egress limits, fail-closed independent verification, ingested CTI treated as untrusted data). They are operating context for an engagement project, separate from any coding-style `CLAUDE.md` you keep for development.

If you cannot or do not want to install even that:

- Ask the agent directly: "read and follow `skills/rt-intel/SKILL.md` and run its Procedure". No discovery step, works anywhere in the repo on Claude Code or Codex.
- The per-skill `AGENTS.md` files are directory operating-context pointers, not slash commands. Codex invocation comes from the skills being under `.agents/skills` (above); if you prefer not to use the make target, drop or commit the skill folders under `.agents/skills` yourself.

Either way the bundled Python helpers run under plain `python3` regardless of how a skill is invoked; only document conversion additionally needs pandoc (docx) or pdfplumber (pdf).

## The six phases and two gates

The engagement lifecycle begins at intake and runs six phases, each phase to one skill:

| Phase | Skill | Produces |
| --- | --- | --- |
| 1. Intake and Scoping | `rt-govern` | The Scoping Document and the Gate 1 sign-off |
| 2. Threat Intelligence and Objective Design | `rt-intel` | The Threat Profile Brief |
| 3. Attack Planning | `rt-emulate` | The Engagement Planning Pack Part A and the Gate 2 sign-off |
| 4. Execution and Live Testing | `rt-adapt` | The Execution Record |
| 5. Reporting | `rt-report` | The Engagement Report, Executive Summary, and Blue Team Account |
| 6. Handoff and Closure | `rt-handoff` | Findings routed to the enterprise systems; the tracker closed |

`rt-verify` is cross-cutting (it gates a phase output fail-closed) and `rt-exposure` is standalone (vulnerability SME, outside the lifecycle).

**Two authorization gates** govern the run, each signed by the same four approvers: the Stakeholder, the Operations Lead, the Assessment Lead, and the CISO. The CISO is a required approver and may approve asynchronously, but no gate clears without it.

- **Gate 1** is the Scoping Document sign-off (Phase 1). It approves _what_ is tested.
- **Gate 2** is the Rules of Engagement sign-off (Phase 3). It approves _how_ the engagement runs and authorizes execution.

## Typical engagement (end to end)

The arc of one engagement. The verify gates are the point: no generated artifact is trusted until an independent context confirms it, and the gate is fail-closed, so an unreachable catalog or an unresolved item halts rather than passes. That independent context can run on a different model provider for uncorrelated-error independence; see `docs/cross-provider-verification.html` (and mind the data-class rule).

1. **Intake and Scoping.** `make new-engagement NAME=<id>`, edit `engagements/<id>/intake.md`, then `/rt-govern engagements/<id>/intake.md` -> the Scoping Document with the **Gate 1** sign-off. Nothing downstream runs without it.
2. `/rt-verify` target scoping, in a fresh session -> gate. Resolve any refuted item, re-run until `ready: true`.
3. **Threat Intelligence and Objective Design.** `/rt-intel` -> the Threat Profile Brief (an intelligence-justified actor and cited techniques per objective).
4. `/rt-verify` target threat-profile -> gate.
5. **Attack Planning.** `/rt-emulate` -> the Engagement Planning Pack Part A (an attack path per objective) and the **Gate 2** Rules of Engagement sign-off that authorizes execution.
6. `/rt-verify` target planning -> gate the plan.
7. **Execution and Live Testing (human-led).** `/rt-adapt` proposes validated variants and appends the contemporaneous log as techniques are blocked or detected. The operator acts; the tool proposes and records, and never fabricates the log.
8. **Reporting.** `/rt-report` reconciles the Execution Record against the Blue Team Account (captured before disclosure), records findings with NIST CSF / NIST SP 800-53 control-domain mappings, and renders the Engagement Report and Executive Summary. Material findings escalate to the CISO.
9. `/rt-verify` target report -> gate the findings and the detection account.
10. **Handoff and Closure.** `/rt-handoff` routes each finding to vulnerability management, control tracking, or detection engineering, hands the retest team its test cases, confirms cleanup and decommission, and closes the engagement tracker.

Worked examples ship under `engagements/DEMO-ENG-2026-014/` (a full engagement on the `red-team-engagement/v3` schema) and `exposures/DEMO-CVE-2026-0001/` (a standalone exposure assessment). The per-skill detail follows.

## Layout

```
skills/
  _shared/scripts/    validate.py (validation + release gate), export.py (optional machine-format rendering),
                      check_doc_style.py (style check), pandoc_convert.py (docx conversion),
                      pdf_convert.py (pdf conversion), ingest_common.py (shared ingest helpers),
                      sync_aadapt.py, sync_nist80053.py, sync_csf.py + the vendored catalogs
  _shared/references/ red-team-engagement-v3.md (artifact schema), framework-mapping.md, degradation.md
  rt-govern/  rt-intel/  rt-emulate/  rt-adapt/  rt-report/  rt-handoff/   (the six phase skills)
  rt-verify/            cross-cutting verifier (SKILL.md + AGENTS.md + references/personas/)
  rt-exposure/          standalone vulnerability SME (SKILL.md + AGENTS.md + references/personas/)
agents/               rt-engagement-verifier.md, rt-exposure-verifier.md (the sub-agents dispatched under Claude Code)
engagements/          per-engagement artifacts (a tracked worked example)
exposures/            per-vulnerability assessments from rt-exposure (a tracked worked example)
```

The skills are markdown instructions an agent (Claude Code or Codex) follows. They run small bundled Python helpers: `validate.py` (technique/control-ID validation and the release gate), `export.py` (the optional AI-ready machine formats), `check_doc_style.py` (deliverable style check), `pandoc_convert.py` (docx conversion, needs pandoc), and `pdf_convert.py` (pdf-to-markdown, needs pdfplumber). You can run any of them directly to verify tooling and troubleshoot.

## The workflow

The six phase skills hand off over one engagement artifact, `engagements/<engagement-id>/engagement.md` (schema `red-team-engagement/v3`), each writing only its own section: `#scoping`, `#threat-profile`, `#planning`, `#execution`, `#report`, `#handoff`, and the cross-cutting `#verification`. The `<engagement-id>` is a deterministic slug of your scope reference; `rt-govern` reports the exact path.

### 1. Govern (`/rt-govern`, Phase 1: Intake and Scoping)

Start from the intake template (`templates/INTAKE.md`): run `make new-engagement NAME=<id>` to scaffold `engagements/<id>/intake.md`, fill in the scope, the crown-jewel targets, a data class, a deconfliction contact/window, and the intel sources, then run `/rt-govern engagements/<id>/intake.md`. The skill reads the intake, elicits and validates the business impact, and writes the Scoping Document.

- It elicits the business impact from the stakeholder and validates it against the enterprise business-impact analysis. Business impact is not a red-team product; where the analysis is missing, that is a gap raised to enterprise risk.
- It drafts measurable objectives. Each is an outcome (a business outcome with a measurable success criterion), never a technique, system, or vulnerability class. If every finding would get the same "patch it" response, the request is a penetration test and is redirected.
- `data_class` is `public-reference` (open CTI) or `engagement-sensitive` (anything tied to a target). When unsure, choose `engagement-sensitive`.
- It refuses without a scope reference and a valid data class, and writes no record.
- **Gate 1** is the Scoping Document sign-off: the Stakeholder, Operations Lead, Assessment Lead, and the CISO. The CISO may approve asynchronously, but the gate does not clear without it. The objective intent locks at sign-off; a later change to intent is a material change requiring stakeholder re-approval. Nothing downstream runs without a signed `#scoping` block.

### 2. Intel (`/rt-intel`, Phase 2: Threat Intelligence and Objective Design)

Under a signed Scoping Document, point it at your CTI, advisories, and the Generic Threat Landscape. It selects an intelligence-justified threat actor per objective, maps that actor's ATT&CK/ATLAS/AADAPT techniques with verbatim citations, validates every ID and name with `validate.py`, records the excluded techniques and intelligence gaps, confirms the engagement type, and writes the Threat Profile Brief. It enriches the approach to the signed objectives; it does not change their intent. Markdown, HTML, and text are read directly; a `.docx` source is converted to markdown with pandoc and a `.pdf` with pdfplumber (the original is moved to a sibling `_ingested/` so it is not re-read). On an `engagement-sensitive` run the source content stays local; only the public catalog is fetched.

### 3. Verify (`/rt-verify`, target threat-profile)

Run it in a fresh context so it does not see the producing skill's reasoning. Under Claude Code the skill dispatches the `rt-engagement-verifier` agent (installed with `make install-agents`) for that context; on Codex, start a fresh session. `rt-verify` reviews one section per run; its targets are `scoping`, `threat-profile`, `planning`, and `report`. It re-derives each reviewed item from the artifact, the cited sources, and a fresh catalog fetch, and gates fail-closed. The section is `ready` only when every reviewed item is confirmed. Run it after scoping (step 1), after this threat profile, after planning, and after the report.

### 4. Emulate (`/rt-emulate`, Phase 3: Attack Planning)

From the signed objectives and the Threat Profile it builds the Engagement Planning Pack Part A: a hypothesized attack path per objective, each step a validated, actor-consistent technique with a detection risk, a branch if blocked, and a marked assumption. It references (does not author) the human-owned infrastructure plan, procurement plan, signed Rules of Engagement, and legal/third-party authorizations, and records the **Gate 2** (Rules of Engagement) sign-off that authorizes execution. Gate 2 requires the same four approvers, plus the legal signer and authorizations where physical operations or third-party systems are in scope, and a verified safeguard for every transaction-adjacent path. Run `/rt-verify` with `target: planning` to gate it. The attack path is a planning hypothesis, not an execution script; `rt-emulate` executes nothing.

### 5. Adapt (`/rt-adapt`, Phase 4: Execution and Live Testing)

During live execution it confirms the entry criteria (Gate 2 cleared, safeguards active, SOC blind for a red team operation, C2 separated), then structures and appends the contemporaneous engagement log as the operator acts. When a technique is blocked or detected it proposes ranked, validated variant options (decision support only, human on the trigger). It records detection observations, deconfliction, deviations, disclosures, target cleanup, attacker infrastructure, and recovered secrets (never the value), and writes the Execution Record. The log is a live human record: `rt-adapt` appends what the operator reports and never fabricates or back-fills it. Fast and local; no autonomous execution.

### 6. Report (`/rt-report`, Phase 5: Reporting)

After execution concludes, it measures unaided detection and produces the human report. **Unaided detection is the measure:** the Blue Team Account (the SOC's own account) is captured first, before any disclosure, from the SOC's own experience. The Detection Analysis reconciles it against the Execution Record, with the blue team's account attributed separately. Findings name systems, controls, and processes and **never an individual** (non-attribution); each carries a recommended remediation and a validated NIST CSF / NIST SP 800-53 control-domain mapping. Severity and materiality are human determinations (materiality by the Operations Lead); `rt-report` records them, it does not set them. Material findings escalate to the CISO. It renders the Engagement Report and the Executive Summary under `engagements/<id>/deliverables/`, then runs the style checker and (where pandoc is present) renders editable docx. Machine formats are optional and additive, not required.

### 7. Handoff (`/rt-handoff`, Phase 6: Handoff and Closure)

With findings established in the report, it routes each finding into the enterprise system that will own it (technical vulnerabilities to vulnerability management, control or process failures to control tracking), records the entry reference, and carries the recommended remediation verbatim from the report. It hands the retest team its test cases and PoCs scoped per finding, confirms target cleanup and attacker-infrastructure decommission, sets the evidence disposition, and closes the engagement tracker. The tracker closes only when cleanup and decommission are both confirmed and every finding has been entered. The red team hands findings off; it does not own remediation status or run the retest. This is the closing phase; there is no downstream `rt-*` skill.

## Standalone: vulnerability exposure (`/rt-exposure`)

Separate from a full engagement, `/rt-exposure` (alias `rt-vuln`) provides subject-matter expertise on a newly disclosed vulnerability. It is standalone: no `rt-govern` authorization, no engagement artifact. It reads the advisory/CVE files you give it (md/html/pdf/txt, converted locally like `rt-intel`) and writes its own assessment under `exposures/<vuln-id>/exposure.md`.

Run `/rt-exposure` with the source files, a `vuln_ref` (the CVE/advisory id), a `data_class` (usually `public-reference` for a public CVE), and optionally your critical functions and affected assets. It:

1. Dissects the vulnerability: the weakness (CWE), affected surface, exploitation path mapped to ATT&CK/ATLAS/AADAPT, and severity signals (CVSS/EPSS/KEV), each grounded in a verbatim quote.
2. Assesses exposure (exposed / not-exposed / uncertain) against your scope.
3. Proposes compensating controls, each mapped to a NIST CSF and/or NIST SP 800-53 control domain, with an explicit "limits exposure by ..." claim and a stated residual risk.
4. Gates on two independent verifiers dispatched in fresh contexts (`rt-exposure-verifier`, target `dissection` then `controls`). One re-checks the dissection, one re-checks the controls; where the data class permits, they run on a different model than the producer for uncorrelated errors. The assessment is ready only when both gate fail-closed.

Every technique and control ID is validated by `validate.py` (NIST CSF and NIST SP 800-53 are vendored catalogs, checked fail-closed by exact name). A control that does not counter an identified technique, or claims zero residual risk, is refuted by the control-adequacy verifier. See `skills/rt-exposure/SKILL.md`.

## Running the helpers

All commands run from `skills/_shared/scripts`.

```bash
# Validate technique or control mappings against catalog data (a JSON list of {id, framework, name})
python3 validate.py --entries entries.json

# Force a fresh catalog fetch (rt-verify uses this for independence)
python3 validate.py --entries entries.json --refresh

# The deterministic release gate over a #verification block (with coverage of the expected ids)
python3 validate.py --gate verification.json --expect-ids ids.json

# Catalog freshness: versions of every catalog, and whether AADAPT is behind its source
python3 validate.py --catalog-info

# Re-sync a vendored catalog when its source ships a new version (each prints a review diff)
python3 sync_aadapt.py        # AADAPT
python3 sync_nist80053.py     # NIST SP 800-53 Rev 5
python3 sync_csf.py           # NIST CSF 2.0

# Convert a .docx source to markdown and archive the original (requires pandoc)
python3 pandoc_convert.py to-markdown /path/to/advisory.docx --archive

# Convert a .pdf source to page-numbered markdown and archive the original (requires pdfplumber)
python3 pdf_convert.py to-markdown /path/to/advisory.pdf --archive

# Render markdown documents to editable docx (requires pandoc)
python3 pandoc_convert.py to-docx ../../../engagements/<id>/deliverables/*.md
```

The `--entries` flag reads a JSON list from a file; each item is `{ "id" (or "technique_id"), "framework", "name" (optional) }`. When no name is given it validates the id only. The offensive frameworks are `attack`, `atlas`, and `aadapt`; the control frameworks are `nist-csf` and `nist-800-53`.

Machine formats are optional and additive. `export.py` produces JSON, a STIX 2.1 bundle, and ATT&CK Navigator layers from the validated artifact; it is being updated for the v3 schema in a later tooling pass, so do not rely on its current output shape. See `skills/rt-report/references/machine-formats.md`.

## Reading verdicts

Each item gets one of three verdicts:

- `confirmed`: the ID validates and (if a name was given) the name matches; for a reviewed item, the cited quote resolves and supports the mapping.
- `refuted`: unknown or wrong-type ID, a name mismatch, or a quote that does not support the mapping (reasons like `unknown-id`, `wrong-id-type`, `name-mismatch`).
- `unverifiable`: the catalog was unreachable, or the item has no citation that resolves.

The gate is fail-closed. `validate.py --gate` returns `ready: true` only when there is at least one verdict, every verdict is confirmed, and (with `--expect-ids`) the verdicts cover every expected id, so dropping a failing item cannot pass. An empty set never passes. Each verdict also carries a `catalog_version` for the audit trail.

## Data-class handling

- `public-reference`: source excerpts may leave the machine under scope.
- `engagement-sensitive`: do not send source content anywhere. `validate.py` honors this (it fetches only the public catalog). Honest limit: with a hosted model, the reasoning itself sends the source to the model provider, so "local" means no egress beyond the authorized model host. For a hard guarantee, run a local model and keep the verify context on the same authorized boundary.

## Troubleshooting

- All items `unverifiable` with a catalog error: the framework sources were unreachable. Fail-closed behavior; restore network or retry. The run stays gated until the catalog loads.
- `validate.py` exits non-zero: expected whenever any item is not confirmed. A fail-closed scripting signal, not a crash.
- `--catalog-info` warns AADAPT is stale: run `python3 sync_aadapt.py`, review the diff, commit the regenerated catalog.
- A quote will not resolve: it must be a verbatim substring of the source the agent read.

## Confirm the tooling

```bash
make test
cd skills/_shared/scripts && python3 validate.py --catalog-info
```
