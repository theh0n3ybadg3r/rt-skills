#!/usr/bin/env python3
"""Re-sync the vendored AADAPT catalog from MITRE's AADAPT.yaml.

AADAPT (unlike ATT&CK and ATLAS) has no live JSON/STIX endpoint, so `aadapt-catalog.json` is vendored.
Run this when MITRE ships a new AADAPT version:

    python3 sync_aadapt.py

It fetches AADAPT.yaml, extracts every technique/sub-technique id + official name and the release
version, regenerates the catalog, and prints a review diff (added / removed / renamed) so a human can
approve the change before committing. Prefers PyYAML; falls back to a stdlib regex parse so it runs with
no dependency.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

YAML_URL = "https://raw.githubusercontent.com/mitre/AADAPT/main/adapt-data/dist/AADAPT.yaml"
CATALOG = Path(__file__).parent / "aadapt-catalog.json"
ID_RE = re.compile(r"^ADT\d{4}(\.\d{3})?$")


def fetch_yaml() -> str:
    req = urllib.request.Request(YAML_URL, headers={"User-Agent": "aadapt-sync"})
    with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310 (trusted MITRE host)
        return r.read().decode("utf-8", "replace")


def _version(text: str) -> str:
    m = re.search(r"^version:\s*['\"]?([\w.]+)", text, re.M)
    return m.group(1) if m else ""


def parse_with_pyyaml(text: str):
    import yaml
    cat: dict[str, str] = {}

    def walk(o):
        if isinstance(o, dict):
            i, n = o.get("id"), o.get("name")
            if isinstance(i, str) and ID_RE.match(i) and isinstance(n, str):
                cat[i] = n
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(yaml.safe_load(text))
    return cat, _version(text)


def parse_with_regex(text: str):
    """Fallback: scan `id: ADT...` then the adjacent `name:` line in the flat dist file."""
    cat: dict[str, str] = {}
    cur = None
    for line in text.splitlines():
        mid = re.search(r"\bid:\s*(ADT\d{4}(?:\.\d{3})?)\b", line)
        if mid:
            cur = mid.group(1)
            continue
        if cur:
            mn = re.search(r"\bname:\s*(.+?)\s*$", line)
            if mn:
                cat[cur] = mn.group(1).strip().strip("\"'")
                cur = None
    return cat, _version(text)


def main() -> int:
    text = fetch_yaml()
    try:
        cat, version = parse_with_pyyaml(text)
        parser = "pyyaml"
    except ImportError:
        cat, version = parse_with_regex(text)
        parser = "regex-fallback"

    if not cat:
        print("ERROR: parsed 0 techniques; aborting (catalog left unchanged).", file=sys.stderr)
        return 1

    old = json.loads(CATALOG.read_text()).get("catalog", {}) if CATALOG.exists() else {}
    added = sorted(set(cat) - set(old))
    removed = sorted(set(old) - set(cat))
    renamed = sorted(k for k in set(cat) & set(old) if cat[k] != old[k])

    print(f"parser: {parser}   version: {version}   techniques: {len(cat)}")
    print(f"added:   {added or 'none'}")
    print(f"removed: {removed or 'none'}")
    print("renamed: " + (str([f"{k}: {old[k]!r} -> {cat[k]!r}" for k in renamed]) if renamed else "none"))

    out = {
        "version": version,
        "source": YAML_URL,
        "note": "AADAPT has no live JSON/STIX endpoint (source is YAML). Generated from AADAPT.yaml and "
                "version-pinned; re-sync on a new AADAPT release with sync_aadapt.py.",
        "catalog": {k: cat[k] for k in sorted(cat)},
    }
    with open(CATALOG, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {CATALOG.name} (review the diff above, then commit).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
