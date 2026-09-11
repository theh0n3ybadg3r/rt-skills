"""Offline tests for export.py (no network). Run: python -m unittest -q test_export."""
import json
import tempfile
import unittest
from pathlib import Path

import export

# A minimal but representative v3 engagement artifact: a scoping objective, a threat profile
# (ATT&CK + AADAPT techniques and an actor, all on OBJ-1), an attack path, an execution log with an
# adapted sibling (T5555.002, framework omitted), a report finding, and two verification blocks.
SAMPLE = """# Engagement TEST-ENG-001

## 1. Scoping Document (rt-govern)

```json
{
  "schema": "red-team-engagement/v3#scoping",
  "engagement_ref": "TEST-ENG-001",
  "engagement_type": "red-team-operation",
  "data_class": "engagement-sensitive",
  "scoping_summary": {"crown_jewels": ["key store"]},
  "objectives": [
    {"id": "OBJ-1", "outcome": "steal signing keys", "success_criterion": "a key is extracted",
     "target_crown_jewel": "key store"},
    {"id": "OBJ-2", "outcome": "read the audit log", "success_criterion": "a log entry is read",
     "target_crown_jewel": "audit store"}
  ],
  "gate1_sign_off": {"stakeholder": "s", "operations_lead": "o",
                     "assessment_lead": "a", "ciso": "c"}
}
```

## 2. Threat Profile (rt-intel)

```json
{
  "schema": "red-team-engagement/v3#threat-profile",
  "sources": ["CTI-TEST"],
  "catalog_provenance": {"attack": "19.2", "aadapt": "4.4.0"},
  "engagement_type_confirmed": "red-team-operation",
  "actors": [
    {"objective_id": "OBJ-1", "name": "Testers", "motivation": "demo actor"}
  ],
  "techniques": [
    {"id": "T5555", "framework": "attack", "name": "Test Attack Technique",
     "objective_id": "OBJ-1", "sourced": "intelligence"},
    {"id": "ADT7777", "framework": "aadapt", "name": "Test Aadapt Technique",
     "objective_id": "OBJ-1", "sourced": "intelligence"},
    {"id": "T6666", "framework": "attack", "name": "Second Objective Technique",
     "objective_id": "OBJ-2", "sourced": "intelligence"}
  ]
}
```

## 3. Planning Pack (rt-emulate)

```json
{
  "schema": "red-team-engagement/v3#planning",
  "attack_paths": [
    {"objective_id": "OBJ-1",
     "steps": [
       {"step": 1, "technique_id": "T5555", "framework": "attack", "actor_consistent": true,
        "action": "do it", "detection_risk": "medium", "branch_if_blocked": "try the sibling"},
       {"step": 2, "technique_id": "T7777", "framework": "attack", "actor_consistent": true,
        "action": "planning-only move", "detection_risk": "low", "branch_if_blocked": "stop"}
     ],
     "terminal_action": "extract a key"}
  ]
}
```

## 4. Execution Record (rt-adapt)

```json
{
  "schema": "red-team-engagement/v3#execution",
  "log": [
    {"timestamp": "2026-03-05T09:00:00Z", "objective_id": "OBJ-1", "action": "attempt",
     "technique_id": "T5555", "framework": "attack", "outcome": "blocked"},
    {"timestamp": "2026-03-05T10:00:00Z", "objective_id": "OBJ-1", "action": "attempt sibling",
     "technique_id": "T5555.002", "outcome": "success"}
  ]
}
```

## 5. Report (rt-report)

```json
{
  "schema": "red-team-engagement/v3#report",
  "findings": [
    {"id": "F-1", "source": "attack-path", "objective_id": "OBJ-1",
     "description": "the key store allowed unauthenticated read",
     "control_domain": [{"framework": "nist-800-53", "id": "SC-7", "name": "Boundary Protection"}]}
  ]
}
```

## 7. Verification (rt-verify)

```json
{
  "schema": "red-team-engagement/v3#verification",
  "target": "threat-profile",
  "ready": true,
  "verdicts": [{"id": "T5555", "verdict": "confirmed"}]
}
```

```json
{
  "schema": "red-team-engagement/v3#verification",
  "target": "planning",
  "ready": true,
  "verdicts": [{"id": "T5555", "verdict": "confirmed"}]
}
```
"""


class ExportTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.md = Path(self.tmp.name) / "engagement.md"
        self.md.write_text(SAMPLE)
        self.sections = export.parse_engagement(self.md)
        self.eng_id = export.engagement_id(self.md, self.sections)

    def tearDown(self):
        self.tmp.cleanup()


class Parsing(ExportTestBase):
    def test_sections_bucketed_by_schema(self):
        for key in ("scoping", "threat-profile", "planning", "execution", "report"):
            self.assertIn(key, self.sections)

    def test_verification_is_a_list_of_all_blocks(self):
        self.assertEqual(len(self.sections["verification"]), 2)
        self.assertEqual({v["target"] for v in self.sections["verification"]},
                         {"threat-profile", "planning"})

    def test_engagement_id_from_engagement_ref(self):
        self.assertEqual(self.eng_id, "TEST-ENG-001")


class Stix(ExportTestBase):
    def setUp(self):
        super().setUp()
        self.bundle = export.build_stix(self.sections)
        self.aps = [o for o in self.bundle["objects"] if o["type"] == "attack-pattern"]

    def test_bundle_shape(self):
        self.assertEqual(self.bundle["type"], "bundle")
        self.assertTrue(self.bundle["id"].startswith("bundle--"))

    def test_attack_pattern_has_spec_version_and_external_id(self):
        by_id = {o["external_references"][0]["external_id"]: o for o in self.aps}
        self.assertIn("T5555", by_id)
        self.assertIn("ADT7777", by_id)
        self.assertEqual(by_id["T5555"]["spec_version"], "2.1")
        self.assertEqual(by_id["T5555"]["external_references"][0]["source_name"], "mitre-attack")
        self.assertEqual(by_id["ADT7777"]["external_references"][0]["source_name"], "mitre-aadapt")

    def test_adapted_sibling_included_with_inferred_framework(self):
        # T5555.002 appears only in the execution log with no framework field.
        by_id = {o["external_references"][0]["external_id"]: o for o in self.aps}
        self.assertIn("T5555.002", by_id)
        self.assertEqual(by_id["T5555.002"]["external_references"][0]["source_name"], "mitre-attack")

    def test_intrusion_set_and_uses_relationships(self):
        sets = [o for o in self.bundle["objects"] if o["type"] == "intrusion-set"]
        rels = [o for o in self.bundle["objects"] if o["type"] == "relationship"]
        self.assertEqual(len(sets), 1)
        self.assertEqual(sets[0]["name"], "Testers")
        self.assertTrue(all(r["relationship_type"] == "uses" for r in rels))
        # Actor is on OBJ-1; the two OBJ-1 techniques (T5555, ADT7777) are `uses` targets.
        self.assertEqual(len(rels), 2)
        # The OBJ-2 technique (T6666) is an attack-pattern but must NOT link to the OBJ-1 actor:
        # this discriminates objective_id-scoped linkage from "link the actor to every technique".
        ap_ext = {o["external_references"][0]["external_id"] for o in self.aps}
        self.assertIn("T6666", ap_ext)
        t6666_oid = next(o["id"] for o in self.aps if o["external_references"][0]["external_id"] == "T6666")
        self.assertNotIn(t6666_oid, {r["target_ref"] for r in rels})

    def test_deterministic_ids_across_runs(self):
        again = export.build_stix(self.sections)
        self.assertEqual([o["id"] for o in self.bundle["objects"]],
                         [o["id"] for o in again["objects"]])


class Navigator(ExportTestBase):
    def test_coverage_layer_attack_only(self):
        layer = export.build_coverage_layer(self.sections, self.eng_id)
        self.assertEqual(layer["domain"], "enterprise-attack")
        ids = {t["techniqueID"] for t in layer["techniques"]}
        self.assertIn("T5555", ids)
        self.assertIn("T7777", ids)  # planning-only technique: proves the planning reader path ran
        self.assertIn("T6666", ids)
        self.assertNotIn("ADT7777", ids)  # AADAPT never enters the enterprise layer

    def test_outcomes_layer_colored_by_outcome(self):
        layer = export.build_outcomes_layer(self.sections, self.eng_id)
        by_id = {t["techniqueID"]: t for t in layer["techniques"]}
        self.assertEqual(by_id["T5555"]["color"], export.OUTCOME_STYLE["blocked"]["color"])
        self.assertEqual(by_id["T5555.002"]["color"], export.OUTCOME_STYLE["success"]["color"])


class AllArtifacts(ExportTestBase):
    def test_every_artifact_json_serializes(self):
        artifacts = export.build_all(self.sections, self.eng_id)
        for name, obj in artifacts.items():
            round_tripped = json.loads(json.dumps(obj))
            self.assertEqual(round_tripped, obj, name)

    def test_write_outputs_writes_expected_files(self):
        artifacts = export.build_all(self.sections, self.eng_id)
        out = Path(self.tmp.name) / "machine"
        written = export.write_outputs(artifacts, out, "all")
        names = {p.name for p in written}
        self.assertIn("engagement.json", names)
        self.assertIn("engagement.stix.json", names)
        self.assertIn("coverage.navigator.json", names)
        for p in written:  # each written file is valid JSON on disk
            json.loads(p.read_text())

    def test_format_filter_navigator_only(self):
        artifacts = export.build_all(self.sections, self.eng_id)
        out = Path(self.tmp.name) / "nav"
        written = {p.name for p in export.write_outputs(artifacts, out, "navigator")}
        self.assertEqual(written, {"coverage.navigator.json", "outcomes.navigator.json"})

    def test_format_filter_json_only(self):  # the per-deliverable JSONs were removed; json = engagement.json only
        artifacts = export.build_all(self.sections, self.eng_id)
        out = Path(self.tmp.name) / "j"
        written = {p.name for p in export.write_outputs(artifacts, out, "json")}
        self.assertEqual(written, {"engagement.json"})

    def test_consolidated_is_v3_shape(self):
        eng = export.build_all(self.sections, self.eng_id)["engagement.json"]
        self.assertEqual(eng["schema"], "red-team-engagement/v3#consolidated")
        for key in ("scoping", "threat-profile", "planning", "execution", "report"):
            self.assertIn(key, eng)
        self.assertNotIn("intel", eng)  # retired v2 key must be gone


if __name__ == "__main__":
    unittest.main()
