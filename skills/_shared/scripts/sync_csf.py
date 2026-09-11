#!/usr/bin/env python3
"""Re-sync the vendored NIST Cybersecurity Framework (CSF) 2.0 catalog from its machine-readable source.

The CSF 2.0 Core is U.S. government work in the public domain, so the full catalog can be vendored. Run
this on a networked host to regenerate the Category + Subcategory set:

    python3 sync_csf.py

The shipped catalog carries only the 22 Categories (the control-domain granularity the reporting phase
maps findings to) so the skill runs offline; this regenerates the full Category + Subcategory set.

Source: the NIST Cybersecurity and Privacy Reference Tool (CPRT) publishes CSF 2.0 as JSON. The exact CPRT
download URL/params change over time, so CONFIRM the endpoint before the first run and set CPRT_URL below.
The parser is deliberately schema-agnostic: it walks the JSON and collects every element whose identifier
matches a CSF Category (XX.YY) or Subcategory (XX.YY-NN) shape, paired with its title (falling back to the
element text for Subcategories, which carry an outcome statement rather than a short title).
Stdlib only (the source is JSON).
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

# CONFIRM this against the current CPRT export before running (see module docstring).
CPRT_URL = "https://csrc.nist.gov/extensions/nudp/services/json/csf/download?olirids=all"
CATALOG = Path(__file__).parent / "nist-csf-catalog.json"
CSF_ID_RE = re.compile(r"^[A-Z]{2}\.[A-Z]{2}(?:-\d{2})?$")
ID_KEYS = ("element_identifier", "identifier", "elementIdentifier", "id")
NAME_KEYS = ("title", "name", "text")


def fetch_json() -> object:
    req = urllib.request.Request(CPRT_URL, headers={"User-Agent": "csf-sync"})
    with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310 (trusted NIST host)
        return json.loads(r.read())


def collect(node, out: dict[str, str]) -> None:
    """Walk the JSON, collecting {csf-id: name} for every CSF-shaped element identifier."""
    if isinstance(node, dict):
        cid = next((node[k] for k in ID_KEYS if isinstance(node.get(k), str)), None)
        if cid and CSF_ID_RE.match(cid):
            name = next((node[k] for k in NAME_KEYS if isinstance(node.get(k), str) and node[k].strip()), "")
            if name:
                out[cid] = " ".join(name.split())
        for v in node.values():
            collect(v, out)
    elif isinstance(node, list):
        for child in node:
            collect(child, out)


def main() -> int:
    elements: dict[str, str] = {}
    collect(fetch_json(), elements)

    if not elements:
        print("ERROR: parsed 0 CSF elements; aborting (catalog left unchanged). Confirm CPRT_URL.", file=sys.stderr)
        return 1

    old = json.loads(CATALOG.read_text()).get("catalog", {}) if CATALOG.exists() else {}
    added = sorted(set(elements) - set(old))
    removed = sorted(set(old) - set(elements))
    renamed = sorted(k for k in set(elements) & set(old) if elements[k] != old[k])

    print(f"elements: {len(elements)}")
    print(f"added:   {len(added)}")
    print(f"removed: {removed or 'none'}")
    print("renamed: " + (str([f"{k}: {old[k]!r} -> {elements[k]!r}" for k in renamed]) if renamed else "none"))

    out = {
        "version": "2.0",
        "source": CPRT_URL,
        "note": "NIST Cybersecurity Framework 2.0 Core, U.S. government work in the public domain. Generated "
                "by sync_csf.py. Ids are CSF element identifiers (Category XX.YY, Subcategory XX.YY-NN); names "
                "are the official titles (Subcategories fall back to their outcome-statement text).",
        "catalog": {k: elements[k] for k in sorted(elements)},
    }
    with open(CATALOG, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {CATALOG.name} (review the diff above, then commit).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
