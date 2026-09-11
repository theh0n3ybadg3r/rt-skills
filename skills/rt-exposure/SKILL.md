---
name: rt-exposure
description: >-
  Standalone vulnerability subject-matter-expertise skill (alias rt-vuln). Dissects a newly disclosed vulnerability from provided advisory/CVE files, judges whether the organization is exposed, and proposes compensating controls that limit that exposure, each mapped to a NIST CSF and/or NIST SP 800-53 control domain with verbatim citations. Two independent, fail-closed verifiers (one for the dissection, one for the controls) that can run on a different model than the producer gate the assessment. It does not require an rt-govern authorization and writes its own exposure-assessment artifact.
---

# rt-exposure

Subject-matter expertise on a newly identified vulnerability, on demand and independent of an engagement. It answers three questions from provided sources: what is the vulnerability, are we exposed, and what compensating controls limit that exposure. It is standalone. It does not run under the engagement pipeline or require an rt-govern authorization record; it writes its own `exposure-assessment/v1` artifact and gates it with two independent verifiers.

Shared assets:

- Artifact schema (the five sections it owns): `references/exposure-assessment-v1.md`.
- ID rules and name matching for all frameworks (offensive `attack`/`atlas`/`aadapt` and defensive `nist-csf`/`nist-800-53`): `skills/_shared/references/framework-mapping.md`.
- Bundled helpers this skill may run: `skills/_shared/scripts/validate.py` (technique-ID and control-ID validation for all frameworks), `skills/_shared/scripts/pandoc_convert.py` (convert a `.docx` source to markdown; requires pandoc), and `skills/_shared/scripts/pdf_convert.py` (convert a `.pdf` source to markdown; requires pdfplumber).
- Guidance: `references/dissection-mapping.md`, `references/control-mapping.md`, and the two verifier personas `references/personas/dissection-fidelity.md` and `references/personas/control-adequacy.md`.
- Independent verification: the `rt-exposure-verifier` agent (install it with `make install-agents`), dispatched once per target.
- Writing standard for any prose that reaches a reader: `skills/_shared/references/writing-style.md`.

## Procedure

1. **Set scope.** Read or collect the `#scope` fields: `vuln_ref` (required, non-empty, else stop), `data_class` (exactly `public-reference` or `engagement-sensitive`, else stop), the `sources` to read, and optional `critical_functions` / `affected_assets`. Derive `egress_permitted.source_content = (data_class == public-reference)`. This value sets the verifier model boundary in step 11. Write section 1.
2. **Read the sources yourself.** Read markdown, HTML, and plain-text advisories/CVEs directly. Convert binary sources to markdown first so extraction and verification work against clean, verbatim-quotable text: `.docx` via `python3 skills/_shared/scripts/pandoc_convert.py to-markdown <file> --archive`, `.pdf` via `python3 skills/_shared/scripts/pdf_convert.py to-markdown <file> --archive`. Both converters run locally and make no network calls, so they are safe on an `engagement-sensitive` run. There is no live fetch of the advisory; work from the files provided.
3. **Dissect the vulnerability** (`references/dissection-mapping.md`). Capture the weakness class (CWE id + name), the affected surface (component/version), and any severity/exploitability signals (CVSS, EPSS, KEV listing, vendor severity, exploit availability). Each claim carries a verbatim `quote` copied exactly from a source and a `locator`. A severity number that is not stated in a source is invented; do not record it.
4. **Map the exploitation path** to ATT&CK / ATLAS / AADAPT techniques (`references/dissection-mapping.md` + the shared framework rules). For each: `framework`, `id`, `name`, a verbatim `quote`, and a `locator`. Map behaviors the source describes, not tool names; do not over-map.
5. **Validate the technique IDs.** Write the technique entries as a JSON list of `{"id": ..., "framework": ..., "name": ...}` to a scratch path **outside** `exposures/` (so source-derived content never lands in the artifact tree), run `python3 skills/_shared/scripts/validate.py --entries <tmp.json>`, record each `script_verdict` + `script_reason`, then delete the temp file. Write section 2.
6. **Assess exposure.** Tie the affected surface to the `critical_functions` / `affected_assets` (or judge generically when none are given). State `exposed` / `not-exposed` / `uncertain`, a rationale, and the `conditions` under which it holds. Write section 3.
7. **Propose compensating controls** (`references/control-mapping.md`). For each control: a `control_domain` array of `{framework: nist-csf | nist-800-53, id, name}` entries (prefer a NIST SP 800-53 control paired with a NIST CSF Category), the `counters_technique_ids` it addresses (ids from section 2), an explicit `limits_exposure_by` (the causal reduction against this exposure), and a non-vacuous `residual_risk`. A control that claims to eliminate the risk entirely is an overclaim; state what remains.
8. **Validate the control IDs.** Write every `control_domain` entry as a JSON list of `{"id": ..., "framework": ..., "name": ...}` to a scratch path outside `exposures/`, run `python3 skills/_shared/scripts/validate.py --entries <tmp.json>`, record the combined `script_verdict` per control, then delete the temp file. Both `nist-csf` and `nist-800-53` are name-checked against the vendored catalogs (fail-closed, exact-name).
9. **Record catalog provenance.** Run `python3 skills/_shared/scripts/validate.py --catalog-info` once and put each framework's `version` into `#controls.catalog_provenance` (`attack`/`atlas`/`aadapt` for the dissection techniques, `nist-csf`/`nist-800-53` for the controls). Write section 4.
10. **Independent verification, one dispatch per target.** Dispatch the `rt-exposure-verifier` agent twice, in two fresh contexts, so a generator never grades its own work:
    - `target: dissection` (V1): re-derives the weakness/technique/severity claims, checks each quote resolves and supports its mapping, and validates the technique IDs.
    - `target: controls` (V2): re-derives each control, validates the `control_domain` IDs (NIST CSF and NIST SP 800-53), judges as a semantic call whether the control credibly counters the identified technique/weakness (no map lookup), and checks the limits claim and the residual risk. Each verifier returns a `#verification` block; it does not write the artifact.
11. **Model boundary for the verifiers.** Run the verifiers on a model that differs from the producer where the data class allows, for uncorrelated errors:
    - Default: a different Claude tier than the producer (same vendor never crosses the authorized boundary, so this is safe on any data class).
    - Cross-vendor verification is permitted only when `data_class == public-reference`. On `engagement-sensitive`, the verifier must stay on the session model/host boundary; a cross-vendor pin is refused and reported as a blocker rather than egressing source content (`skills/_shared/references/degradation.md`, KTD4).
    - If the harness cannot pin a per-agent model and producer and verifier collide on the same model, that is a logged reduced-independence note (`boundary: same-model-reduced-independence`), not a failure: two independent fresh contexts still satisfy the fail-closed gate. Record `producer_model`, `verifier_model`, and `boundary` in each block.
12. **Write and gate.** Write both returned blocks into section 5 (one per target, never overwriting the other). For each target, write an ids file of every reviewed item id and run `python3 skills/_shared/scripts/validate.py --gate <the #verification block> --expect-ids <ids.json>`. The assessment is ready only when **both** gates return ready. Never hand-type `ready`.
13. **Report.** Give both gate results and a one-line reason per non-confirmed item. A gated assessment with honest reasons is the correct output when the evidence or the controls are not there.

## Boundaries

- Standalone. It does not read or require an rt-govern Scoping Document (`#scoping`), and it does not write into the `engagements/` tree.
- Extract only what the sources support. Do not invent a CWE, a technique, or a severity number; over-mapping and ungrounded severity are defects V1 refutes.
- Every compensating control needs a control-domain mapping (NIST CSF and/or NIST SP 800-53), an explicit limits claim, and a non-vacuous residual risk. A zero-residual claim is a defect V2 refutes.
- You do not decide readiness. The two independent verifiers plus the fail-closed gate do. Never mark ready to keep moving.
- Respect the data class. On an `engagement-sensitive` run keep source content local (the converters and `validate` are local; the catalog fetch sends no source content), and keep the verifiers on the authorized model boundary.
- Prose you author here (the vulnerability summary, exposure rationale, control descriptions) is written to the deliverable standard in `skills/_shared/references/writing-style.md`: plain analyst English, no em dashes, no AI jargon or stock phrases.
