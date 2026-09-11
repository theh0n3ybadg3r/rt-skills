# Maintenance: keeping the catalogs current

The skills validate IDs against MITRE offensive frameworks (ATT&CK, ATLAS, AADAPT) and, for the reporting and exposure control-domain mapping, defensive control frameworks (NIST CSF, NIST 800-53). ATT&CK and ATLAS update themselves; the rest are vendored and need a periodic re-sync. This is the whole maintenance surface.

## How each catalog stays current

| Framework | Source | Update model |
| --- | --- | --- |
| ATT&CK | live: `mitre-attack/attack-stix-data` (always-latest STIX) | auto-updates; nothing to do |
| ATLAS | live: `mitre-atlas/atlas-data` latest release (`stix-atlas.json`) | auto-updates; nothing to do |
| AADAPT | vendored: `skills/_shared/scripts/aadapt-catalog.json` | manual re-sync (no live JSON endpoint exists) |
| NIST 800-53 | vendored: `skills/_shared/scripts/nist-800-53-catalog.json` | manual re-sync (OSCAL, public domain) |
| NIST CSF | vendored: `skills/_shared/scripts/nist-csf-catalog.json` | manual re-sync (CSF 2.0, public domain) |

- **ATT&CK and ATLAS** are fetched live and cached for 24h. When MITRE ships a new release with new techniques, the next fetch after the cache expires picks them up automatically. To force it now, pass `--refresh` to `validate.py`.
- **AADAPT, NIST 800-53, and NIST CSF** have no stdlib-simple id+name endpoint, so their catalogs are vendored and version-pinned. These are the files that need a deliberate update.

## Checking freshness

```bash
python3 skills/_shared/scripts/validate.py --catalog-info
```

Reports each catalog's version, count, and source, and warns when the vendored AADAPT is behind the current `AADAPT.yaml` (with the fix to run). It fetches fresh, so it doubles as a way to warm the caches. Example fields: ATT&CK `19.2`, ATLAS `v2026.07`, AADAPT `4.4.0`, NIST 800-53 `5.1.1`.

## Re-syncing the vendored catalogs (when their sources update)

```bash
python3 skills/_shared/scripts/sync_aadapt.py       # AADAPT, from AADAPT.yaml
python3 skills/_shared/scripts/sync_nist80053.py     # NIST 800-53 Rev 5, from the OSCAL catalog
python3 skills/_shared/scripts/sync_csf.py           # NIST CSF 2.0, from the CPRT export
```

Each fetches its source, regenerates the catalog, and prints a review diff (added / removed / renamed). Review the diff, then commit the regenerated catalog. `sync_nist80053.py` normalizes OSCAL enhancement ids (`ac-2.1`) to display form (`AC-2(1)`). Each refuses to overwrite its catalog if it parses zero entries.

The shipped `nist-800-53-catalog.json` and `nist-csf-catalog.json` are representative subsets (marked `"subset": true`) so the skill and tests run offline; run the sync scripts on a networked host to produce the authoritative full catalogs. The NIST OSCAL and CSF sources are U.S. government work in the public domain.

**Recommended cadence:** run `--catalog-info` periodically (a monthly or quarterly check), and run each `sync_*.py` when its source ships a new version.

## Provenance (audit trail)

Every validation verdict carries a `catalog_version` field recording which catalog version it was checked against, and `rt-intel`/`rt-verify` record `catalog_provenance` (the versions used) into the engagement artifact; `rt-exposure` records it into the exposure assessment. This gives auditable evidence that a run used current data.

## If a framework ever changes an ID format

The ID regexes live in `skills/_shared/references/framework-mapping.md` and `skills/_shared/scripts/validate.py` (kept in sync). ID formats are very stable, but if a framework changes its scheme, update the regexes in both places. Cache location: `~/.cache/red-team-skills/catalogs/`.
