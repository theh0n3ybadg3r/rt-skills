# framework-mapping: ID conventions and name matching

Canonical rules for the frameworks the `validate` helper checks: the three offensive technique frameworks (`attack`, `atlas`, `aadapt`), shared by `rt-intel`, `rt-emulate`, and `rt-verify`, and the defensive control frameworks (`nist-800-53`, `nist-csf`), used for the reporting-phase control-domain mapping. Keep this in sync with the regexes in `skills/_shared/scripts/validate.py` (the helper is authoritative for execution; this file is the human reference).

## ID regexes

Anchor every pattern. Match the two-letter tactic prefix (`TA`) **before** the one-letter technique prefix (`T`), or a tactic ID is misread as a technique.

### ATT&CK (Enterprise), `framework: attack`

| kind          | regex             | accept as technique? |
| ------------- | ----------------- | -------------------- |
| technique     | `^T\d{4}$`        | yes                  |
| sub-technique | `^T\d{4}\.\d{3}$` | yes                  |
| tactic        | `^TA\d{4}$`       | no                   |
| mitigation    | `^M\d{4}$`        | no                   |
| group         | `^G\d{4}$`        | no                   |
| software      | `^S\d{4}$`        | no                   |
| data source   | `^DS\d{4}$`       | no                   |

### ATLAS, `framework: atlas`

| kind          | regex                  | accept as technique? |
| ------------- | ---------------------- | -------------------- |
| technique     | `^AML\.T\d{4}$`        | yes                  |
| sub-technique | `^AML\.T\d{4}\.\d{3}$` | yes                  |
| tactic        | `^AML\.TA\d{4}$`       | no                   |
| mitigation    | `^AML\.M\d{4}$`        | no                   |
| case study    | `^AML\.CS\d{4}$`       | no                   |

### AADAPT (digital-asset / payment tech), `framework: aadapt`

| kind          | regex               | accept as technique? |
| ------------- | ------------------- | -------------------- |
| technique     | `^ADT\d{4}$`        | yes                  |
| sub-technique | `^ADT\d{4}\.\d{3}$` | yes                  |
| native tactic | `^ADTA\d{4}$`       | no                   |
| reused tactic | `^TA\d{4}$`         | no                   |

AADAPT uses its own `ADT####` namespace (two techniques adapt ATT&CK, e.g. `ADT1195` from `T1195`, but keep the `ADT` prefix). It reuses ATT&CK tactic IDs (`TA####`) verbatim and adds one native tactic, `ADTA0001` Fraud. A `TA####` or `ADTA####` id under `framework: aadapt` is a tactic, not a technique.

Only `technique` and `sub-technique` are valid inventory IDs. Any other kind is `refuted` with reason `wrong-id-type`.

### OWASP (referenced, not validated here)

The program also recognizes OWASP as a vocabulary for naming a web/application vulnerability class in a finding. It is not a technique framework the `validate` helper checks, and an OWASP-driven scope is a penetration test (redirected to that function), not this program's work. No OWASP catalog is loaded.

## Defensive control frameworks (used by rt-report and rt-exposure)

The compensating-control side validates control IDs the same way: id shape, catalog existence, and (where a name catalog is shipped) official-name match, fail-closed. These frameworks are `control` kind, so the ATT&CK "Parent: Child" name tolerance does not apply; a name matches only by exact normalized form.

### NIST SP 800-53 Rev 5, `framework: nist-800-53`

| kind        | regex                      | accept? |
| ----------- | -------------------------- | ------- |
| control     | `^[A-Z]{2}-\d+$`           | yes     |
| enhancement | `^[A-Z]{2}-\d+(\(\d+\))?$` | yes     |

Controls are `AC-2`, `SC-7`; enhancements are the display form `AC-2(1)` (the OSCAL source form `ac-2.1` is normalized to display form when the catalog is synced). The name must be the official control title.

### NIST CSF 2.0, `framework: nist-csf`

| kind        | regex                        | accept? |
| ----------- | ---------------------------- | ------- |
| category    | `^[A-Z]{2}\.[A-Z]{2}$`       | yes     |
| subcategory | `^[A-Z]{2}\.[A-Z]{2}-\d{2}$` | yes     |

CSF 2.0 ids are a `Function.Category` (e.g. `PR.AA` Identity Management, Authentication, and Access Control; `DE.CM` Continuous Monitoring) or a Subcategory that adds `-NN` (e.g. `PR.AA-01`). Categories carry a dot before any dash, so a CSF id never collides with a NIST 800-53 control id (`AC-2`). The vendored catalog ships the 22 Categories (the control-domain granularity the reporting phase maps findings and detection gaps to); run `sync_csf.py` to regenerate the full Category + Subcategory set. The name must match the official Category title (exact normalized form; no `Parent: Child` tolerance, it is a control framework). CSF is the reporting-phase control-domain framework, paired with NIST 800-53.

## Name matching

A name matches when its normalized form equals the catalog's normalized official name. Normalization:

1. Unicode NFKC.
2. Casefold.
3. Collapse all runs of whitespace to a single space; strip ends.

Sub-technique naming: the STIX object's `name` is the **child only** (e.g. `T1566.001` -> `Spearphishing Attachment`), while ATT&CK Navigator and many advisories cite the display form `Parent: Child` (e.g. `Phishing: Spearphishing Attachment`). `validate.name_matches` accepts **either** form, the plain child name, or a `Parent: Child` string whose segment after the last `:` matches the catalog's child name. A name that is neither (e.g. `T1566.001` labeled `OS Credential Dumping`) is a `refuted` mismatch. This catches hallucinated/wrong names without false-refuting legitimate citation styles.

## Catalog sources (loaded by validate.py)

- ATT&CK Enterprise: STIX 2.1 bundle, always-latest raw file `https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json` (~54 MB). IDs live on `attack-pattern` objects' `external_references` where `source_name == "mitre-attack"`; skip objects with `revoked` or `x_mitre_deprecated` true.
- ATLAS: `stix-atlas.json` (~1 MB), a GitHub **release asset** on the latest `mitre-atlas/atlas-data` release (resolve the release, then the asset's `browser_download_url`). Do **not** raw-fetch `*-latest.yaml` (git symlinks return a filename string) or the deprecated `dist/ATLAS.yaml`.
- AADAPT: no live JSON/STIX endpoint exists (the source is `AADAPT.yaml`), so a small version-pinned catalog is vendored at `skills/_shared/scripts/aadapt-catalog.json` (v4.4.0). Re-sync from `https://raw.githubusercontent.com/mitre/AADAPT/main/adapt-data/dist/AADAPT.yaml` on a new release.

ATT&CK and ATLAS are fetched then cached on disk; AADAPT is read from the vendored file. Any fetch or parse failure (or a missing vendored file) makes that framework's entries `unverifiable`, never `confirmed` (fail-closed).

The defensive frameworks are vendored like AADAPT (no live id+name endpoint): NIST 800-53 Rev 5 at `skills/_shared/scripts/nist-800-53-catalog.json` (public-domain OSCAL, re-sync with `sync_nist80053.py`) and NIST CSF 2.0 at `skills/_shared/scripts/nist-csf-catalog.json` (public-domain, re-sync with `sync_csf.py`). A missing or corrupt vendored control catalog makes that framework's entries `unverifiable` (fail-closed).
