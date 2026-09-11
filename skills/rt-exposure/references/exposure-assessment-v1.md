# exposure-assessment/v1: standalone artifact schema

The exposure assessment is one markdown file that `rt-exposure` writes and the `rt-exposure-verifier` agent reads. It is **standalone**: it does not require or read an rt-govern Scoping Document (`#scoping`), and it does not live in the engagement tree. Each section is a fenced `json` block with the machine-readable content so the `validate` helper and the verifier can parse it; a rendered human summary can accompany it.

Filename convention: `exposures/<vuln-id>/exposure.md`. The `<vuln-id>` is a deterministic slug of `vuln_ref`: if `vuln_ref` is a URL or file path take its last segment, then lowercase, keep `[a-z0-9-]`, and collapse every other run of characters to a single `-` (`CVE-2026-12345` -> `cve-2026-12345`).

Sections, in order: 1. Scope (`#scope`), 2. Vulnerability (`#vulnerability`), 3. Exposure (`#exposure`), 4. Controls (`#controls`), 5. Verification (`#verification`). Sections 2-4 are the producer's draft; section 5 holds the two independent verifier verdicts and the gate.

Frameworks: `attack` / `atlas` / `aadapt` for the offensive mapping (the exploitation path), and `nist-csf` / `nist-800-53` for the defensive control-domain mapping (the compensating controls). See `skills/_shared/references/framework-mapping.md` for the ID rules.

---

## 1. Scope (`#scope`)

The lightweight authorization for a standalone run. No `authorized_by`, `flags`, or `deconfliction`; this is SME analysis, not an authorized offensive engagement.

```json
{
  "schema": "exposure-assessment/v1#scope",
  "vuln_ref": "string, the CVE id / advisory id / source doc path (required, non-empty)",
  "data_class": "public-reference | engagement-sensitive",
  "egress_permitted": { "source_content": true, "public_catalog_fetch": true },
  "sources": ["string, the advisory/CVE source files this assessment reads"],
  "critical_functions": [
    "string, optional: in-scope business functions to judge exposure against"
  ],
  "affected_assets": ["string, optional: the org's assets/products in scope"]
}
```

Rules:

- `vuln_ref` required and non-empty, and `data_class` one of the two literals, else refuse and write nothing.
- `egress_permitted.source_content` is `true` only when `data_class == public-reference` (public CVEs and vendor advisories are the common case for this skill). It drives the verifier model boundary (see the SKILL Procedure).
- `critical_functions` / `affected_assets` are optional; when absent, the exposure judgment is generic ("who is exposed") rather than org-specific.

## 2. Vulnerability (`#vulnerability`)

The dissection: what the weakness is and how it is exploited, every claim grounded in a verbatim quote from a source.

```json
{
  "schema": "exposure-assessment/v1#vulnerability",
  "summary": "string, one-paragraph plain-English description of the vulnerability",
  "weaknesses": [
    {
      "cwe": "string, e.g. CWE-89",
      "name": "string, the CWE name as extracted",
      "quote": "verbatim string from a source",
      "locator": "string, source id + section/page/line"
    }
  ],
  "affected_surface": [
    {
      "component": "string, affected product/component/version",
      "quote": "verbatim",
      "locator": "string"
    }
  ],
  "techniques": [
    {
      "id": "string, e.g. T1190 / AML.T0051 / ADT3012.005",
      "framework": "attack | atlas | aadapt",
      "name": "string, technique name as extracted",
      "citations": [
        { "quote": "verbatim string from the source", "locator": "string" }
      ],
      "script_verdict": "confirmed | refuted | unverifiable, from the validate helper",
      "script_reason": "string"
    }
  ],
  "severity_signals": [
    {
      "kind": "cvss | epss | kev | vendor-severity | exploit-availability",
      "value": "string, e.g. 9.8 / CRITICAL / listed",
      "quote": "verbatim string from a source",
      "locator": "string"
    }
  ]
}
```

Rules:

- Every `weaknesses[]`, `affected_surface[]`, `techniques[]`, and `severity_signals[]` entry carries at least one verbatim `quote` and a `locator`. No quote, no claim; a severity number that is not stated in a source is invented and V1 refutes it.
- `techniques[].script_verdict` is the deterministic ID/name check; it is not the final verdict (V1 sets that).
- CWE ids are recorded but not deterministically catalog-checked (there is no CWE catalog in the helper); they are prose the fidelity verifier judges against the quote.

## 3. Exposure (`#exposure`)

Whether the organization is exposed, tied to the scope.

```json
{
  "schema": "exposure-assessment/v1#exposure",
  "verdict": "exposed | not-exposed | uncertain",
  "rationale": "string, why, tied to affected_surface and critical_functions/affected_assets",
  "conditions": [
    "string, the preconditions under which the exposure holds or does not"
  ]
}
```

## 4. Controls (`#controls`)

The compensating controls, each anchored to a control-domain mapping (NIST CSF and/or NIST SP 800-53), with an explicit limits claim and a stated residual risk.

```json
{
  "schema": "exposure-assessment/v1#controls",
  "catalog_provenance": {
    "attack": "string, version",
    "atlas": "string, version",
    "aadapt": "string, version",
    "nist-csf": "string, version",
    "nist-800-53": "string, version"
  },
  "controls": [
    {
      "title": "string, short name of the compensating control",
      "control_domain": [
        {
          "framework": "nist-csf | nist-800-53",
          "id": "string, e.g. SC-7 / PR.IR",
          "name": "string"
        }
      ],
      "counters_technique_ids": [
        "string, ids from #vulnerability.techniques this control addresses"
      ],
      "limits_exposure_by": "string, the causal reduction: how this control reduces THIS exposure",
      "residual_risk": "string, what exposure remains after the control (non-vacuous)",
      "script_verdict": "confirmed | refuted | unverifiable, the combined id/name check over the control_domain entries"
    }
  ]
}
```

Rules:

- Every control needs at least one `control_domain` entry (NIST CSF and/or NIST SP 800-53), a non-empty `limits_exposure_by`, and a non-vacuous `residual_risk`. A zero-residual claim ("fully eliminates the risk") is an overclaim V2 refutes.
- `counters_technique_ids` must reference ids present in `#vulnerability.techniques`.
- `script_verdict` is the deterministic ID/name check from the helper over the `control_domain` entries; it is not the final verdict (V2 sets that).

## 5. Verification (`#verification`)

Section 5 holds **two blocks**: `target: dissection` (V1, the dissection-fidelity verifier) and `target: controls` (V2, the control-adequacy verifier), each appended, never overwriting the other. Each sets the release gate for its target; the assessment is ready only when **both** blocks are ready.

```json
{
  "schema": "exposure-assessment/v1#verification",
  "target": "dissection | controls",
  "producer_model": "string, the model that produced sections 2-4",
  "verifier_model": "string, the model this verifier ran on",
  "boundary": "same-vendor-different-tier | cross-vendor-permitted-public-reference | same-model-reduced-independence",
  "catalog_provenance": {
    "attack": "string",
    "atlas": "string",
    "aadapt": "string",
    "nist-csf": "string",
    "nist-800-53": "string"
  },
  "ready": false,
  "verdicts": [
    {
      "id": "string, matches a reviewed item id (a technique id, or a control title)",
      "verdict": "confirmed | refuted | unverifiable",
      "reason": "string",
      "checks": {
        "id_name": "confirmed | refuted | unverifiable (validate helper)",
        "quote_resolves": true,
        "quote_supports_mapping": "yes | no | unclear (V1 dissection persona)",
        "severity_grounded": "yes | no | n/a (V1)",
        "control_domain_id_name": "confirmed | refuted | unverifiable (V2, over the control_domain entries)",
        "counters_technique": "yes | no | unclear (V2 control persona, semantic judgment)",
        "limits_claim_supported": "yes | no | unclear (V2)",
        "residual_risk_stated": "yes | no (V2)"
      }
    }
  ]
}
```

Gate rule (fail-closed), computed by the `validate` helper's gate mode per target, never hand-typed:

- **V1 (dissection)** item is `confirmed` only when `id_name == confirmed` (for a mapped technique) AND at least one citation resolves AND `quote_supports_mapping == yes` AND, for a severity signal, `severity_grounded == yes`.
- **V2 (controls)** item is `confirmed` only when `control_domain_id_name == confirmed` (every control_domain entry's id and name validate) AND `counters_technique == yes` AND `limits_claim_supported == yes` AND `residual_risk_stated == yes`.
- Any `refuted` or `unverifiable` item, or an empty verdict set, means `ready: false` for that target. An empty set must never vacuously pass.
- Catalog unreachable means `id_name == unverifiable`, so the item is `unverifiable` and the target is gated. Never passed silently.
- The assessment is ready only when both target blocks are `ready: true`.
