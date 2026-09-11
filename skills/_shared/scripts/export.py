#!/usr/bin/env python3
"""Render an engagement artifact into machine-ingestible (AI-ready) formats.

Reads `engagements/<id>/engagement.md` (schema `red-team-engagement/v3`), parses its JSON sections, and
emits, into `deliverables/machine/`:

- engagement.json          consolidated structured view of every section
- engagement.stix.json     a STIX 2.1 bundle (attack-pattern per technique, intrusion-set per threat
                           actor, `uses` relationships) for SIEM / TIP / ML ingestion
- coverage.navigator.json  an ATT&CK Navigator layer of the planned techniques
- outcomes.navigator.json  an ATT&CK Navigator layer of the executed techniques, colored by outcome

These machine formats are optional and additive: the methodology mandates no machine deliverable, so this is
a convenience for a downstream SIEM / TIP / ML pipeline. It is the deterministic counterpart to rt-report's
human documents (markdown, HTML, docx). Everything here is a mechanical transform of the artifact's own JSON,
so it is code, not model judgment. The technique IDs were already validated by validate.py before they
reached the artifact; export.py does not re-validate, it re-serializes.

STIX object ids are deterministic uuid5 values, so re-running on an unchanged artifact yields byte identical
output (no random, no wall-clock). Navigator layers are ATT&CK-enterprise only; ATLAS and AADAPT techniques
cannot render in the enterprise Navigator, so they are carried by the STIX bundle (which is framework-neutral)
and noted, not forced into the layer.

Stdlib only (json, re, uuid, argparse), no third-party dependencies, for Claude Code + Codex portability.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from pathlib import Path

# A fixed namespace so uuid5-derived STIX ids are stable across runs and machines.
NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "https://red-team-skills/engagement")
# Deterministic created/modified timestamp (the v3 artifact carries no timestamp; keep output stable).
DEFAULT_STIX_TS = "2026-01-01T00:00:00.000Z"

# framework -> STIX external_references source_name
FRAMEWORK_SOURCE = {
    "attack": "mitre-attack",
    "atlas": "mitre-atlas",
    "aadapt": "mitre-aadapt",
}

# Outcome -> Navigator color + score + legend label, from the defender's point of view.
OUTCOME_STYLE = {
    "blocked": {"color": "#2ca25f", "score": 1, "label": "blocked (defense worked)"},
    "detected": {"color": "#f4a742", "score": 2, "label": "detected (caught, still succeeded)"},
    "success": {"color": "#d62728", "score": 3, "label": "success (undetected)"},
}
OUTCOME_DEFAULT = {"color": "#8c8c8c", "score": 0, "label": "other"}

JSON_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)


# --------------------------------------------------------------------------- parsing

def parse_engagement(md_path: Path) -> dict:
    """Parse the engagement markdown into sections keyed by the `schema` suffix after `#`.

    v3 keys: scoping, threat-profile, planning, execution, report, handoff, verification. There can be
    several `#verification` blocks (one per verified target), so verification is always a list; the
    single-instance sections are stored as their object.
    """
    text = md_path.read_text()
    sections: dict = {"verification": []}
    for raw in JSON_BLOCK.findall(text):
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue  # skip a non-conforming block rather than abort the whole export
        schema = obj.get("schema", "") if isinstance(obj, dict) else ""
        key = schema.split("#", 1)[1] if "#" in schema else ""
        if key == "verification":
            sections["verification"].append(obj)
        elif key:
            sections[key] = obj
    return sections


def engagement_id(md_path: Path, sections: dict) -> str:
    scoping = sections.get("scoping") or {}
    return scoping.get("engagement_ref") or md_path.parent.name


# --------------------------------------------------------------------------- technique gathering

def infer_framework(tid: str) -> str:
    """Framework from an id's shape, for entries that omit the field (e.g. execution log)."""
    if re.match(r"^T\d{4}(\.\d{3})?$", tid or ""):
        return "attack"
    if (tid or "").startswith("AML.T"):
        return "atlas"
    if (tid or "").startswith("ADT"):
        return "aadapt"
    return ""


def gather_techniques(sections: dict) -> dict:
    """Union of every technique seen in the artifact -> {framework, name}.

    Threat-profile techniques carry names; planning steps and execution log entries carry only an id,
    so their name may stay empty and their framework is inferred from the id shape. First named wins.
    """
    techs: dict = {}

    def add(tid, framework, name):
        if not tid:
            return
        framework = framework or infer_framework(tid)
        cur = techs.get(tid)
        if cur is None:
            techs[tid] = {"framework": framework or "", "name": name or ""}
        else:
            if not cur["framework"] and framework:
                cur["framework"] = framework
            if not cur["name"] and name:
                cur["name"] = name

    for t in (sections.get("threat-profile") or {}).get("techniques", []):
        add(t.get("id"), t.get("framework"), t.get("name"))
    for path in (sections.get("planning") or {}).get("attack_paths", []):
        for step in path.get("steps", []):
            add(step.get("technique_id"), step.get("framework"), None)
    for e in (sections.get("execution") or {}).get("log", []):
        add(e.get("technique_id"), e.get("framework"), None)
    return techs


def technique_url(framework: str, tid: str) -> str | None:
    if framework == "attack" and re.match(r"^T\d{4}(\.\d{3})?$", tid):
        return "https://attack.mitre.org/techniques/" + tid.replace(".", "/")
    if framework == "atlas" and tid.startswith("AML.T"):
        return "https://atlas.mitre.org/techniques/" + tid
    return None  # AADAPT has no stable per-technique URL; external_id + source_name is enough


# --------------------------------------------------------------------------- STIX 2.1 bundle

def _oid(prefix: str, key: str) -> str:
    return f"{prefix}--{uuid.uuid5(NAMESPACE, key)}"


def build_stix(sections: dict) -> dict:
    """A STIX 2.1 bundle: attack-pattern per technique, intrusion-set per actor, `uses` relationships.

    A v3 actor and a technique are linked by their shared `objective_id`, so an actor `uses` every
    technique mapped for the same objective.
    """
    ts = DEFAULT_STIX_TS
    techs = gather_techniques(sections)
    objects: list = []

    ap_id: dict = {}  # technique id -> STIX attack-pattern id (for relationships)
    for tid in sorted(techs):
        info = techs[tid]
        framework = info["framework"]
        source_name = FRAMEWORK_SOURCE.get(framework, framework or "unknown")
        ref = {"source_name": source_name, "external_id": tid}
        url = technique_url(framework, tid)
        if url:
            ref["url"] = url
        oid = _oid("attack-pattern", f"{framework}:{tid}")
        ap_id[tid] = oid
        objects.append({
            "type": "attack-pattern",
            "spec_version": "2.1",
            "id": oid,
            "created": ts,
            "modified": ts,
            "name": info["name"] or tid,
            "external_references": [ref],
        })

    # technique ids per objective, so an actor selected for an objective `uses` them.
    tids_by_objective: dict = {}
    for t in (sections.get("threat-profile") or {}).get("techniques", []):
        tids_by_objective.setdefault(t.get("objective_id"), []).append(t.get("id"))

    seen_actor: set = set()
    seen_rel: set = set()
    for actor in (sections.get("threat-profile") or {}).get("actors", []):
        name = actor.get("name")
        if not name:
            continue
        set_id = _oid("intrusion-set", f"intrusion-set:{name}")
        if name not in seen_actor:
            seen_actor.add(name)
            obj = {
                "type": "intrusion-set",
                "spec_version": "2.1",
                "id": set_id,
                "created": ts,
                "modified": ts,
                "name": name,
            }
            if actor.get("motivation"):
                obj["description"] = actor["motivation"]
            objects.append(obj)
        for tid in tids_by_objective.get(actor.get("objective_id"), []):
            target = ap_id.get(tid)
            if not target or (name, tid) in seen_rel:
                continue
            seen_rel.add((name, tid))
            objects.append({
                "type": "relationship",
                "spec_version": "2.1",
                "id": _oid("relationship", f"uses:{name}:{tid}"),
                "created": ts,
                "modified": ts,
                "relationship_type": "uses",
                "source_ref": set_id,
                "target_ref": target,
            })

    return {
        "type": "bundle",
        "id": _oid("bundle", engagement_id(Path("."), sections)),
        "objects": objects,
    }


# --------------------------------------------------------------------------- Navigator layers

def _attack_only(pairs):
    """Keep only enterprise ATT&CK technique ids (T#### / T####.###)."""
    return [(tid, extra) for tid, extra in pairs
            if re.match(r"^T\d{4}(\.\d{3})?$", tid or "")]


def build_coverage_layer(sections: dict, eng_id: str) -> dict:
    """Planned coverage: every ATT&CK technique in the threat profile and the attack paths, score 1."""
    seen: dict = {}
    for t in (sections.get("threat-profile") or {}).get("techniques", []):
        if t.get("framework") == "attack":
            seen[t.get("id")] = t.get("name", "")
    for path in (sections.get("planning") or {}).get("attack_paths", []):
        for step in path.get("steps", []):
            if step.get("framework") == "attack":
                seen.setdefault(step.get("technique_id"), "")
    techniques = [
        {"techniqueID": tid, "score": 1, "comment": name, "enabled": True}
        for tid, name in _attack_only(seen.items())
    ]
    return {
        "name": f"{eng_id} planned coverage",
        "versions": {"navigator": "4.9.1", "layer": "4.5"},
        "domain": "enterprise-attack",
        "description": ("Planned ATT&CK coverage for this engagement (threat profile + attack paths). "
                        "ATLAS and AADAPT techniques are in the STIX bundle, not this layer."),
        "techniques": sorted(techniques, key=lambda t: t["techniqueID"]),
        "gradient": {"colors": ["#ffffff", "#66b1ff"], "minValue": 0, "maxValue": 1},
    }


def build_outcomes_layer(sections: dict, eng_id: str) -> dict:
    """Executed ATT&CK techniques colored by outcome (blocked / detected / success)."""
    entries = (sections.get("execution") or {}).get("log", [])
    pairs = [(e.get("technique_id"), e) for e in entries]
    techniques = []
    for tid, e in _attack_only(pairs):
        style = OUTCOME_STYLE.get(e.get("outcome"), OUTCOME_DEFAULT)
        techniques.append({
            "techniqueID": tid,
            "score": style["score"],
            "color": style["color"],
            "comment": f"{e.get('outcome', '')}: {e.get('action', '')}".strip(": "),
            "enabled": True,
        })
    legend = [{"label": s["label"], "color": s["color"]} for s in OUTCOME_STYLE.values()]
    return {
        "name": f"{eng_id} execution outcomes",
        "versions": {"navigator": "4.9.1", "layer": "4.5"},
        "domain": "enterprise-attack",
        "description": ("Executed ATT&CK techniques colored by outcome from the defender's view: "
                        "green blocked, orange detected, red undetected success. ATLAS/AADAPT "
                        "outcomes are in the STIX bundle, not this ATT&CK-only layer."),
        "techniques": sorted(techniques, key=lambda t: t["techniqueID"]),
        "legendItems": legend,
    }


# --------------------------------------------------------------------------- orchestration

def build_all(sections: dict, eng_id: str) -> dict:
    """Every machine artifact, keyed by output filename."""
    consolidated = {
        "schema": "red-team-engagement/v3#consolidated",
        "engagement_id": eng_id,
        "scoping": sections.get("scoping"),
        "threat-profile": sections.get("threat-profile"),
        "planning": sections.get("planning"),
        "execution": sections.get("execution"),
        "report": sections.get("report"),
        "handoff": sections.get("handoff"),
        "verification": sections.get("verification", []),
    }
    return {
        "engagement.json": consolidated,
        "engagement.stix.json": build_stix(sections),
        "coverage.navigator.json": build_coverage_layer(sections, eng_id),
        "outcomes.navigator.json": build_outcomes_layer(sections, eng_id),
    }


FORMAT_FILES = {
    "json": ["engagement.json"],
    "stix": ["engagement.stix.json"],
    "navigator": ["coverage.navigator.json", "outcomes.navigator.json"],
}


def write_outputs(artifacts: dict, out_dir: Path, which: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    names = sorted(set(sum(FORMAT_FILES.values(), []))) if which == "all" else FORMAT_FILES[which]
    written = []
    for name in names:
        if name not in artifacts:
            continue
        path = out_dir / name
        path.write_text(json.dumps(artifacts[name], indent=2) + "\n")
        written.append(path)
    return written


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Render an engagement artifact into AI-ready machine formats.")
    ap.add_argument("--engagement", required=True, help="path to engagements/<id>/engagement.md")
    ap.add_argument("--out", help="output dir (default: <engagement dir>/deliverables/machine)")
    ap.add_argument("--format", choices=["all", "json", "stix", "navigator"], default="all")
    args = ap.parse_args(argv)

    md_path = Path(args.engagement)
    if not md_path.is_file():
        ap.error(f"engagement file not found: {md_path}")
    sections = parse_engagement(md_path)
    eng_id = engagement_id(md_path, sections)
    out_dir = Path(args.out) if args.out else md_path.parent / "deliverables" / "machine"

    artifacts = build_all(sections, eng_id)
    written = write_outputs(artifacts, out_dir, args.format)
    print(json.dumps({
        "engagement_id": eng_id,
        "out_dir": str(out_dir),
        "written": [p.name for p in written],
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
