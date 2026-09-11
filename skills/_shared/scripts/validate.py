#!/usr/bin/env python3
"""Deterministic technique-ID and control-ID validation (KTD2).

Validates {framework, id, name} entries against authoritative catalogs. Offensive technique frameworks
(`attack`, `atlas`, `aadapt`) and defensive control frameworks (`nist-800-53`, `nist-csf`) share the same
machinery: ID existence, ID-type, and official-name match are checked
locally against a catalog fetched from its canonical source and cached on disk (KTD1), or against a
vendored catalog when no live endpoint exists. Whether a quote *supports* a mapping, or a control
*limits* an exposure, is NOT decided here; that is the reviewing persona's semantic judgment.

Fail-closed: if a framework's catalog cannot be loaded, its entries are `unverifiable`, never
`confirmed`.

Stdlib only (json, urllib, re), no third-party dependencies, for Claude Code + Codex portability.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path

ATTACK_URL = (
    "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/"
    "master/enterprise-attack/enterprise-attack.json"
)
ATLAS_RELEASE_API = "https://api.github.com/repos/mitre-atlas/atlas-data/releases/latest"
ATLAS_STIX_ASSET = "stix-atlas.json"
AADAPT_CATALOG_PATH = Path(__file__).parent / "aadapt-catalog.json"
NIST_CATALOG_PATH = Path(__file__).parent / "nist-800-53-catalog.json"
NIST_CSF_CATALOG_PATH = Path(__file__).parent / "nist-csf-catalog.json"

DEFAULT_CACHE_DIR = Path.home() / ".cache" / "red-team-skills" / "catalogs"
DEFAULT_TTL_SECONDS = 24 * 3600

# Valid inventory-ID patterns per framework: technique/sub-technique shapes for the offensive
# frameworks, and control/countermeasure shapes for the defensive ones. `is_valid_id` matches any.
TECHNIQUE_PATTERNS = {
    "attack": (re.compile(r"^T\d{4}$"), re.compile(r"^T\d{4}\.\d{3}$")),
    "atlas": (re.compile(r"^AML\.T\d{4}$"), re.compile(r"^AML\.T\d{4}\.\d{3}$")),
    "aadapt": (re.compile(r"^ADT\d{4}$"), re.compile(r"^ADT\d{4}\.\d{3}$")),
    # NIST 800-53 controls: two-letter family, number, optional numbered enhancement (AC-2, AC-2(1)).
    "nist-800-53": (re.compile(r"^[A-Z]{2}-\d+(?:\(\d+\))?$"),),
    # NIST CSF 2.0: Category (function.category, e.g. PR.AA) or Subcategory (PR.AA-01). These carry a
    # dot before any dash, so they never collide with a NIST 800-53 control id (AC-2).
    "nist-csf": (re.compile(r"^[A-Z]{2}\.[A-Z]{2}$"), re.compile(r"^[A-Z]{2}\.[A-Z]{2}-\d{2}$")),
}
# Recognized non-technique ID shapes, so we can say "wrong-id-type" instead of "unknown".
NON_TECHNIQUE_PATTERNS = {
    "attack": [re.compile(p) for p in (r"^TA\d{4}$", r"^M\d{4}$", r"^G\d{4}$", r"^S\d{4}$", r"^DS\d{4}$")],
    "atlas": [re.compile(p) for p in (r"^AML\.TA\d{4}$", r"^AML\.M\d{4}$", r"^AML\.CS\d{4}$")],
    "aadapt": [re.compile(p) for p in (r"^ADTA\d{4}$", r"^TA\d{4}$")],
}
FRAMEWORK_SOURCE_NAMES = {"attack": {"mitre-attack"}, "atlas": {"mitre-atlas", "mitre-atlas-collection"}}

# Each framework is a `technique` (offensive TTP) or a `control` (defensive measure). The "Parent: Child"
# name tolerance is an ATT&CK/Navigator convention, so it applies to technique frameworks only.
FRAMEWORK_KIND = {
    "attack": "technique", "atlas": "technique", "aadapt": "technique",
    "nist-800-53": "control", "nist-csf": "control",
}
# Vendored catalogs (no live JSON/STIX endpoint); their version is read from the file, not a sidecar.
VENDORED_CATALOGS = {
    "aadapt": AADAPT_CATALOG_PATH,
    "nist-800-53": NIST_CATALOG_PATH,
    "nist-csf": NIST_CSF_CATALOG_PATH,
}


def normalize_name(name: str) -> str:
    """NFKC + casefold + whitespace-collapse (see framework-mapping.md)."""
    s = unicodedata.normalize("NFKC", name or "")
    s = s.casefold()
    return " ".join(s.split())


def name_matches(extracted: str, official: str) -> bool:
    """True when the extracted name matches the catalog's official name.

    STIX stores a sub-technique's `name` as the child only (e.g. "Spearphishing Attachment"),
    while advisories commonly cite the Navigator display form "Parent: Child"
    (e.g. "Phishing: Spearphishing Attachment"). Accept either.
    """
    e = normalize_name(extracted)
    o = normalize_name(official)
    if e == o:
        return True
    if ":" in e and normalize_name(e.rsplit(":", 1)[-1]) == o:
        return True
    return False


def name_ok(tid: str, name: str, catalog: dict, kind: str = "technique") -> bool:
    """Name check with catalog-aware parent tolerance.

    Accepts the exact official name, or (technique frameworks only) the Navigator "Parent: Child"
    display form for a sub-technique when BOTH segments match the catalog (the parent segment against
    the parent technique's official name, not just the child). This stops a mislabeled parent from
    passing. Control frameworks do an exact-normalized match only (no parent/child convention).
    """
    official = catalog.get(tid, "")
    if normalize_name(name) == normalize_name(official):
        return True
    if kind == "technique" and "." in tid and ":" in name:
        parent_official = catalog.get(tid.split(".")[0])
        parent_seg, child_seg = name.split(":", 1)
        if (parent_official
                and normalize_name(parent_seg) == normalize_name(parent_official)
                and normalize_name(child_seg) == normalize_name(official)):
            return True
    return False


def is_valid_id(framework: str, tid: str) -> bool:
    """True when the id matches a valid inventory shape (technique or control) for the framework."""
    pats = TECHNIQUE_PATTERNS.get(framework)
    return bool(pats) and any(p.match(tid or "") for p in pats)


def is_known_non_technique(framework: str, tid: str) -> bool:
    return any(p.match(tid or "") for p in NON_TECHNIQUE_PATTERNS.get(framework, []))


# --------------------------------------------------------------------------- catalog building

def _fetch(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "red-team-skills-validator"})
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (trusted MITRE hosts)
        return r.read()


def catalog_from_stix(raw: bytes, framework: str) -> dict[str, str]:
    """Build {technique_id: official_name} from a STIX bundle's attack-pattern objects."""
    bundle = json.loads(raw)
    sources = FRAMEWORK_SOURCE_NAMES[framework]
    out: dict[str, str] = {}
    for obj in bundle.get("objects", []):
        if obj.get("type") != "attack-pattern":
            continue
        if obj.get("revoked") or obj.get("x_mitre_deprecated"):
            continue
        name = obj.get("name")
        if not name:
            continue
        for ref in obj.get("external_references", []):
            ext_id = ref.get("external_id")
            if not ext_id:
                continue
            # Require BOTH the authoritative source_name AND a technique-shaped id, so a
            # technique-shaped external_id from a foreign source (or a cross-reference) cannot
            # pollute the catalog or bind an id to the wrong object's name.
            if ref.get("source_name") in sources and is_valid_id(framework, ext_id):
                out[ext_id] = name
    return out


def stix_collection_version(raw: bytes) -> str:
    """The release version from a STIX bundle's x-mitre-collection object, or '' if absent."""
    try:
        for obj in json.loads(raw).get("objects", []):
            if obj.get("type") == "x-mitre-collection":
                # ATLAS uses `version`; ATT&CK uses `x_mitre_version` (e.g. "19.2").
                v = obj.get("version") or obj.get("x_mitre_version")
                if v:
                    return str(v)
    except (json.JSONDecodeError, TypeError, AttributeError):
        pass
    return ""


def _write_version(cache_dir: Path, framework: str, version: str) -> None:
    try:
        (cache_dir / f"{framework}-version.txt").write_text(version or "")
    except OSError:
        pass


def read_catalog_version(cache_dir: Path, framework: str) -> str:
    """Version of the catalog last loaded for a framework. Vendored catalogs read the version from the
    file; the live frameworks read the sidecar written when the catalog was last fetched."""
    path = VENDORED_CATALOGS.get(framework)
    if path is not None:
        try:
            return str(json.loads(path.read_text()).get("version", ""))
        except (OSError, json.JSONDecodeError, AttributeError):
            return ""
    try:
        return (cache_dir / f"{framework}-version.txt").read_text().strip()
    except OSError:
        return ""


def _cached_or_fetch(framework: str, raw_getter, cache_dir: Path, ttl: int) -> dict[str, str] | None:
    """Return the parsed {id:name} catalog, using an on-disk cache. None on any failure (fail-closed)."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache = cache_dir / f"{framework}-catalog.json"
    if cache.exists() and (time.time() - cache.stat().st_mtime) < ttl:
        try:
            return json.loads(cache.read_text())
        except (OSError, json.JSONDecodeError):
            pass  # fall through to refetch
    try:
        catalog = raw_getter()
        if not catalog:
            return None
        cache.write_text(json.dumps(catalog))
        return catalog
    except Exception:  # network, parse, symlink-string, anything -> fail-closed
        # No fresh catalog (a within-TTL cache would have returned above) and refetch failed.
        # Do NOT fall back to an expired cache: validating against stale data would silently
        # defeat the fail-closed gate (A6). Return None -> entries become `unverifiable`.
        return None


def load_attack_catalog(cache_dir: Path = DEFAULT_CACHE_DIR, ttl: int = DEFAULT_TTL_SECONDS):
    def getter():
        raw = _fetch(ATTACK_URL)
        _write_version(cache_dir, "attack", stix_collection_version(raw))
        return catalog_from_stix(raw, "attack")
    return _cached_or_fetch("attack", getter, cache_dir, ttl)


def load_atlas_catalog(cache_dir: Path = DEFAULT_CACHE_DIR, ttl: int = DEFAULT_TTL_SECONDS):
    def getter():
        release = json.loads(_fetch(ATLAS_RELEASE_API, timeout=30))
        _write_version(cache_dir, "atlas", str(release.get("tag_name", "")))
        url = next((a["browser_download_url"] for a in release.get("assets", [])
                    if a.get("name") == ATLAS_STIX_ASSET), None)
        if not url:
            raise RuntimeError(f"{ATLAS_STIX_ASSET} not found in latest atlas-data release")
        return catalog_from_stix(_fetch(url), "atlas")
    return _cached_or_fetch("atlas", getter, cache_dir, ttl)


def _load_vendored(path: Path) -> dict[str, str] | None:
    """Load a vendored {id:name} catalog file's `catalog` map. None on any failure (fail-closed)."""
    try:
        doc = json.loads(path.read_text())
        cat = doc.get("catalog") if isinstance(doc, dict) else None
        return cat if isinstance(cat, dict) and cat else None
    except (OSError, json.JSONDecodeError):
        return None  # missing/corrupt bundled catalog -> fail-closed (entries become unverifiable)


def load_aadapt_catalog(cache_dir: Path = DEFAULT_CACHE_DIR, ttl: int = DEFAULT_TTL_SECONDS):
    """AADAPT has no live JSON/STIX endpoint; load the vendored, version-pinned catalog (offline).

    cache_dir/ttl are accepted for a uniform loader signature and ignored.
    """
    return _load_vendored(AADAPT_CATALOG_PATH)


def load_nist_catalog(cache_dir: Path = DEFAULT_CACHE_DIR, ttl: int = DEFAULT_TTL_SECONDS):
    """NIST 800-53 Rev 5 controls: vendored, version-pinned (OSCAL catalog). cache_dir/ttl ignored."""
    return _load_vendored(NIST_CATALOG_PATH)


def load_nist_csf_catalog(cache_dir: Path = DEFAULT_CACHE_DIR, ttl: int = DEFAULT_TTL_SECONDS):
    """NIST CSF 2.0 Categories/Subcategories: vendored, version-pinned (CPRT export). cache_dir/ttl ignored."""
    return _load_vendored(NIST_CSF_CATALOG_PATH)


def build_catalogs(frameworks, cache_dir: Path = DEFAULT_CACHE_DIR, ttl: int = DEFAULT_TTL_SECONDS):
    loaders = {
        "attack": load_attack_catalog, "atlas": load_atlas_catalog, "aadapt": load_aadapt_catalog,
        "nist-800-53": load_nist_catalog, "nist-csf": load_nist_csf_catalog,
    }
    return {fw: loaders[fw](cache_dir, ttl) for fw in frameworks if fw in loaders}


AADAPT_YAML_URL = "https://raw.githubusercontent.com/mitre/AADAPT/main/adapt-data/dist/AADAPT.yaml"


def aadapt_source_version() -> str:
    """The `version:` in the live AADAPT.yaml (for staleness), or '' when unreachable."""
    try:
        text = _fetch(AADAPT_YAML_URL, timeout=30).decode("utf-8", "replace")
        m = re.search(r"^version:\s*['\"]?([\w.]+)", text, re.M)
        return m.group(1) if m else ""
    except Exception:
        return ""


# Static source/maintenance descriptions for the freshness report, in display order.
CATALOG_SOURCES = {
    "attack": ("live: mitre-attack/attack-stix-data (enterprise-attack.json, always-latest)", "auto-updates (live)"),
    "atlas": ("live: mitre-atlas/atlas-data latest release (stix-atlas.json)", "auto-updates (live)"),
    "aadapt": (f"vendored: {AADAPT_CATALOG_PATH.name} (no live JSON endpoint)", "manual re-sync (run sync_aadapt.py)"),
    "nist-800-53": (f"vendored: {NIST_CATALOG_PATH.name} (OSCAL Rev 5 catalog)", "manual re-sync (run sync_nist80053.py)"),
    "nist-csf": (f"vendored: {NIST_CSF_CATALOG_PATH.name} (CSF 2.0 Categories)", "manual re-sync (run sync_csf.py)"),
}


def catalog_info(cache_dir: Path = DEFAULT_CACHE_DIR, ttl: int = DEFAULT_TTL_SECONDS) -> dict:
    """Freshness report per catalog: version, count, source, and AADAPT staleness."""
    # Force a fresh fetch so the report is accurate and the version sidecars get populated for
    # subsequent --entries stamping (ttl arg kept for signature uniformity).
    catalog_frameworks = list(CATALOG_SOURCES)
    meta = build_catalogs(catalog_frameworks, cache_dir=cache_dir, ttl=0)
    report = {}
    for fw in catalog_frameworks:
        cat = meta.get(fw)
        source, maintenance = CATALOG_SOURCES[fw]
        entry = {
            "reachable": cat is not None,
            "version": read_catalog_version(cache_dir, fw) if cat is not None else "",
            "count": len(cat) if cat else 0,
            "source": source,
            "maintenance": maintenance,
        }
        if fw == "aadapt" and cat is not None:  # AADAPT is the one vendored catalog with a live version probe
            latest = aadapt_source_version()
            entry["source_version"] = latest
            entry["stale"] = bool(latest) and latest != entry["version"]
            if entry["stale"]:
                entry["action"] = f"vendored {entry['version']} is behind source {latest}: run sync_aadapt.py"
        report[fw] = entry
    return report


# --------------------------------------------------------------------------- validation

def validate_entry(entry: dict, catalogs: dict[str, dict | None]) -> dict:
    """Return {id, verdict, reason} for one entry. Deterministic ID (and optional name) check.

    Accepts either `id` or `technique_id` for the identifier. `name` is optional: when it is
    absent or empty the check validates the ID only (used by emulation procedures and adapt
    variants, which carry no name); when a name is given it must match the catalog.
    """
    tid = entry.get("id") or entry.get("technique_id") or ""
    framework = entry.get("framework", "")
    name = entry.get("name")

    def result(verdict, reason):
        return {"id": tid, "framework": framework, "verdict": verdict, "reason": reason}

    if framework not in TECHNIQUE_PATTERNS:
        return result("refuted", f"unknown-framework:{framework!r}")

    catalog = catalogs.get(framework)
    if not isinstance(catalog, dict):  # fail-closed: unreachable/unparseable/malformed catalog
        return result("unverifiable", "catalog-unavailable")

    if not is_valid_id(framework, tid):
        if is_known_non_technique(framework, tid):
            return result("refuted", "wrong-id-type")
        return result("refuted", "malformed-or-unknown-id-shape")

    if tid not in catalog:
        return result("refuted", "unknown-id")

    if not name:  # id-only validation (no name carried)
        return result("confirmed", "id-valid-name-not-checked")

    if not name_ok(tid, name, catalog, FRAMEWORK_KIND.get(framework, "technique")):
        return result("refuted", f"name-mismatch:expected {catalog[tid]!r}")

    return result("confirmed", "id-and-name-match")


def validate(entries, catalogs) -> list[dict]:
    return [validate_entry(e, catalogs) for e in entries]


def ready_from_verdicts(verdicts) -> bool:
    """Deterministic release gate. Ready only when there is at least one verdict AND every
    verdict is `confirmed`. An empty list is NOT ready: an empty inventory must never vacuously
    pass the gate (`all([]) is True`)."""
    verdicts = list(verdicts)
    return len(verdicts) >= 1 and all(
        isinstance(v, dict) and v.get("verdict") == "confirmed" for v in verdicts
    )


# --------------------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Validate technique-ID or control-ID entries against their catalogs, or gate verification verdicts."
    )
    ap.add_argument("--entries", help="JSON file: list of {id, framework, name} entries to validate")
    ap.add_argument("--gate", help="JSON file: a #verification block or verdict list; compute the ready gate")
    ap.add_argument("--expect-ids", help="with --gate: JSON list of ids the gate must cover (all confirmed)")
    ap.add_argument("--offline-catalog",
                    help="DEV/TEST ONLY: JSON {framework:{id:name}} used instead of a live fetch; bypasses real validation")
    ap.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    ap.add_argument("--refresh", action="store_true",
                    help="ignore any cached catalog and refetch (use for independent verification)")
    ap.add_argument("--catalog-info", action="store_true",
                    help="report catalog versions/freshness (and AADAPT staleness) and exit")
    args = ap.parse_args(argv)

    if args.catalog_info:
        print(json.dumps(catalog_info(cache_dir=Path(args.cache_dir)), indent=2))
        return 0

    if args.gate and args.entries:
        ap.error("pass either --entries or --gate, not both")

    if args.gate:  # deterministic release gate over verification verdicts (fail-closed)
        doc = json.loads(Path(args.gate).read_text())
        verdicts = list(doc.get("verdicts", []) if isinstance(doc, dict) else doc)
        ready = ready_from_verdicts(verdicts)
        reason = "ok" if ready else ("empty-verdict-set" if not verdicts else "not-all-confirmed")
        if ready and args.expect_ids:  # coverage: every expected id must be present (no dropped failures)
            expected = set(json.loads(Path(args.expect_ids).read_text()))
            got = {v.get("id") for v in verdicts if isinstance(v, dict)}
            missing = sorted(expected - got)
            if missing:
                ready, reason = False, f"incomplete-coverage:missing {missing}"
        print(json.dumps({"ready": ready, "entries": len(verdicts), "reason": reason}, indent=2))
        return 0 if ready else 1

    if not args.entries:
        ap.error("one of --entries or --gate is required")
    entries = json.loads(Path(args.entries).read_text())
    frameworks = sorted({e.get("framework") for e in entries if e.get("framework")})

    if args.offline_catalog:
        catalogs = json.loads(Path(args.offline_catalog).read_text())
    else:
        ttl = 0 if args.refresh else DEFAULT_TTL_SECONDS
        catalogs = build_catalogs(frameworks, cache_dir=Path(args.cache_dir), ttl=ttl)

    verdicts = validate(entries, catalogs)
    versions = ({} if args.offline_catalog
                else {fw: read_catalog_version(Path(args.cache_dir), fw) for fw in frameworks})
    for v in verdicts:  # provenance: stamp which catalog version each verdict was checked against
        v["catalog_version"] = "offline" if args.offline_catalog else versions.get(v.get("framework"), "")
    print(json.dumps(verdicts, indent=2))
    # Fail-closed: non-zero unless there is >=1 entry and all are confirmed (empty never passes).
    return 0 if ready_from_verdicts(verdicts) else 1


if __name__ == "__main__":
    sys.exit(main())
