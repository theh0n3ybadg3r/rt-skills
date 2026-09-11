# Machine (AI-ready) formats (optional, additive)

The Phase 5 deliverables are the human Engagement Report and the Executive Summary. The methodology mandates **no** machine-format deliverable. This file describes an **optional, additive** export for downstream tooling; skip it unless a consumer asks for it.

Where a downstream SIEM, threat-intel platform, or ML pipeline wants a structured export, `skills/_shared/scripts/export.py` produces one deterministically from the engagement artifact. It re-serializes content the phase skills already produced and `rt-verify` already validated; it does not re-validate, re-map, or add anything. Because the transform is mechanical and schema-precise, it is code, not model output.

## export.py is being updated for v3

`export.py` currently keys to the earlier deliverable set and schema and is being updated for the v3 schema and the real deliverable names in a later tooling/docs pass. **Do not rely on its current output shape**, and **do not modify it** here. The human Engagement Report and Executive Summary remain the Phase 5 deliverables regardless of the export.

When the export is wanted, run it once per engagement:

```bash
python3 skills/_shared/scripts/export.py --engagement engagements/<id>/engagement.md
# optional: --format all|json|stix|navigator   --out <dir>
```

## What it produces (subject to the v3 update)

- **JSON**: a consolidated structured view of the artifact's sections, for generic ingestion and archival.
- **STIX 2.1 bundle**: an `attack-pattern` per technique across the artifact (each with an `external_references` entry naming the framework and id) and an `intrusion-set` per threat actor, with `uses` relationships. The bundle is framework-neutral, so it is the format that carries ATLAS and AADAPT techniques. Object ids are deterministic `uuid5` values, so re-running on an unchanged artifact yields byte-identical output.
- **ATT&CK Navigator layers**: layer documents (`domain: enterprise-attack`) of the planned and the executed ATT&CK techniques, the latter colored by outcome. Caveat: the Navigator can only render enterprise `T####` ids; ATLAS (`AML.T####`) and AADAPT (`ADT####`) techniques are carried by the STIX bundle and the JSON instead. This is a Navigator limitation, not a gap in coverage.

The control-domain mappings in `#report.findings` (`nist-csf` / `nist-800-53`) are validated by `validate.py` at report time, not by `export.py`.
