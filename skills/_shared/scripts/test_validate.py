"""Offline tests for validate.py (no network). Run: python -m unittest -q."""
import json
import unittest
from pathlib import Path

import validate

FIXTURE = json.loads((Path(__file__).parent.parent / "fixtures" / "catalog-fixture.json").read_text())


def v(id_, framework, name, catalogs=FIXTURE):
    return validate.validate_entry({"id": id_, "framework": framework, "name": name}, catalogs)


class NameNormalization(unittest.TestCase):
    def test_case_and_whitespace_insensitive(self):
        self.assertEqual(validate.normalize_name("Process   Injection"), validate.normalize_name("process injection"))


class AttackValidation(unittest.TestCase):
    def test_confirmed(self):
        self.assertEqual(v("T1055", "attack", "Process Injection")["verdict"], "confirmed")

    def test_confirmed_with_messy_whitespace_and_case(self):
        self.assertEqual(v("T1055", "attack", "  process   injection ")["verdict"], "confirmed")

    def test_subtechnique_child_name_confirmed(self):
        # STIX stores the child-only name; the plain child name must confirm.
        self.assertEqual(v("T1566.001", "attack", "Spearphishing Attachment")["verdict"], "confirmed")

    def test_subtechnique_parent_child_display_form_confirmed(self):
        # Advisories often cite the Navigator "Parent: Child" display form; accept it too.
        self.assertEqual(v("T1566.001", "attack", "Phishing: Spearphishing Attachment")["verdict"], "confirmed")

    def test_subtechnique_wrong_name_refuted(self):  # A3-style: genuinely wrong name
        r = v("T1566.001", "attack", "OS Credential Dumping")
        self.assertEqual(r["verdict"], "refuted")
        self.assertTrue(r["reason"].startswith("name-mismatch"))

    def test_name_mismatch_refuted(self):  # Covers A3
        r = v("T1055", "attack", "Phishing")
        self.assertEqual(r["verdict"], "refuted")
        self.assertTrue(r["reason"].startswith("name-mismatch"))

    def test_unknown_id_refuted(self):
        self.assertEqual(v("T9999", "attack", "Whatever")["reason"], "unknown-id")

    def test_tactic_id_rejected_as_wrong_type(self):  # TA-before-T disambiguation
        r = v("TA0001", "attack", "Initial Access")
        self.assertEqual(r["verdict"], "refuted")
        self.assertEqual(r["reason"], "wrong-id-type")

    def test_mitigation_id_rejected_as_wrong_type(self):
        self.assertEqual(v("M1049", "attack", "Antivirus")["reason"], "wrong-id-type")


class AtlasValidation(unittest.TestCase):
    def test_confirmed(self):  # Covers A4
        self.assertEqual(v("AML.T0051", "atlas", "LLM Prompt Injection")["verdict"], "confirmed")

    def test_unknown_id_refuted(self):
        self.assertEqual(v("AML.T9999", "atlas", "Nope")["reason"], "unknown-id")

    def test_atlas_tactic_rejected_as_wrong_type(self):
        self.assertEqual(v("AML.TA0000", "atlas", "Recon")["reason"], "wrong-id-type")


class FailClosed(unittest.TestCase):
    def test_catalog_unavailable_is_unverifiable(self):  # Covers A6
        r = v("T1055", "attack", "Process Injection", catalogs={"attack": None})
        self.assertEqual(r["verdict"], "unverifiable")
        self.assertEqual(r["reason"], "catalog-unavailable")

    def test_never_confirmed_when_catalog_missing(self):
        # Even a correct id/name cannot be confirmed without a catalog.
        self.assertNotEqual(v("AML.T0051", "atlas", "LLM Prompt Injection", catalogs={"atlas": None})["verdict"], "confirmed")


class CacheFailClosed(unittest.TestCase):
    def test_expired_cache_plus_unreachable_returns_none(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            def boom():
                raise RuntimeError("network down")
            # No cache present + fetch fails -> None (fail-closed), not a stale catalog.
            self.assertIsNone(validate._cached_or_fetch("attack", boom, Path(tmp), ttl=0))

    def test_within_ttl_cache_used_without_fetch(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "attack-catalog.json").write_text('{"T1055": "Process Injection"}')
            def boom():
                raise AssertionError("should not fetch when a fresh cache exists")
            got = validate._cached_or_fetch("attack", boom, Path(tmp), ttl=9999)
            self.assertEqual(got, {"T1055": "Process Injection"})


class UnknownFramework(unittest.TestCase):
    def test_unknown_framework_refuted(self):
        self.assertEqual(v("T1055", "madeup-framework", "x")["verdict"], "refuted")


class ReadyGate(unittest.TestCase):
    def test_empty_inventory_is_not_ready(self):  # P0: empty must not vacuously pass
        self.assertFalse(validate.ready_from_verdicts([]))

    def test_all_confirmed_is_ready(self):
        self.assertTrue(validate.ready_from_verdicts([{"verdict": "confirmed"}, {"verdict": "confirmed"}]))

    def test_any_non_confirmed_gates(self):
        self.assertFalse(validate.ready_from_verdicts([{"verdict": "confirmed"}, {"verdict": "refuted"}]))
        self.assertFalse(validate.ready_from_verdicts([{"verdict": "unverifiable"}]))


class StixParsing(unittest.TestCase):
    def _bundle(self):
        import json as _json
        return _json.dumps({"objects": [
            {"type": "attack-pattern", "name": "Phishing",
             "external_references": [{"source_name": "mitre-attack", "external_id": "T1566"}]},
            {"type": "attack-pattern", "name": "Revoked", "revoked": True,
             "external_references": [{"source_name": "mitre-attack", "external_id": "T9001"}]},
            {"type": "attack-pattern", "name": "Deprecated", "x_mitre_deprecated": True,
             "external_references": [{"source_name": "mitre-attack", "external_id": "T9002"}]},
            {"type": "course-of-action", "name": "NotATechnique",
             "external_references": [{"source_name": "mitre-attack", "external_id": "T9003"}]},
            {"type": "attack-pattern", "name": "ForeignSourced",
             "external_references": [{"source_name": "nist", "external_id": "T7777"}]},
        ]}).encode()

    def test_parses_and_filters(self):
        cat = validate.catalog_from_stix(self._bundle(), "attack")
        self.assertEqual(cat, {"T1566": "Phishing"})  # revoked/deprecated/non-AP/foreign all excluded


class CacheFailClosedFetch(unittest.TestCase):
    def test_empty_fetched_catalog_returns_none(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            # e.g. the ATLAS *-latest.yaml symlink returning a filename string -> empty parse -> None.
            self.assertIsNone(validate._cached_or_fetch("atlas", lambda: {}, Path(tmp), ttl=9999))


class Cli(unittest.TestCase):
    def _entries_file(self, tmp, entries):
        import json as _json
        p = Path(tmp) / "entries.json"
        p.write_text(_json.dumps(entries))
        return str(p)

    def test_exit_zero_all_confirmed(self):
        import tempfile
        fixture = str(Path(__file__).parent.parent / "fixtures" / "catalog-fixture.json")
        with tempfile.TemporaryDirectory() as tmp:
            ef = self._entries_file(tmp, [{"id": "T1055", "framework": "attack", "name": "Process Injection"}])
            self.assertEqual(validate.main(["--entries", ef, "--offline-catalog", fixture]), 0)

    def test_exit_one_when_any_not_confirmed(self):
        import tempfile
        fixture = str(Path(__file__).parent.parent / "fixtures" / "catalog-fixture.json")
        with tempfile.TemporaryDirectory() as tmp:
            ef = self._entries_file(tmp, [{"id": "T1055", "framework": "attack", "name": "Phishing"}])
            self.assertEqual(validate.main(["--entries", ef, "--offline-catalog", fixture]), 1)

    def test_exit_one_on_empty_inventory(self):  # P0 at the CLI boundary
        import tempfile
        fixture = str(Path(__file__).parent.parent / "fixtures" / "catalog-fixture.json")
        with tempfile.TemporaryDirectory() as tmp:
            ef = self._entries_file(tmp, [])
            self.assertEqual(validate.main(["--entries", ef, "--offline-catalog", fixture]), 1)


class Aadapt(unittest.TestCase):
    CAT = validate.load_aadapt_catalog()  # vendored, offline

    def _v(self, id_, name):
        return validate.validate_entry({"id": id_, "framework": "aadapt", "name": name}, {"aadapt": self.CAT})

    def test_catalog_loads(self):
        self.assertIsNotNone(self.CAT)
        self.assertEqual(self.CAT.get("ADT3012.005"), "Reentrancy")

    def test_confirmed_technique_and_subtechnique(self):
        self.assertEqual(self._v("ADT3015", "Flash Loan")["verdict"], "confirmed")
        self.assertEqual(self._v("ADT3012.005", "Reentrancy")["verdict"], "confirmed")

    def test_name_mismatch_refuted(self):
        self.assertEqual(self._v("ADT3012.005", "Flash Loan")["verdict"], "refuted")

    def test_native_tactic_is_wrong_type(self):  # ADTA0001 Fraud is a tactic, not a technique
        self.assertEqual(self._v("ADTA0001", "Fraud")["reason"], "wrong-id-type")

    def test_reused_attack_tactic_is_wrong_type(self):  # AADAPT reuses ATT&CK TA#### tactics
        self.assertEqual(self._v("TA0001", "Initial Access")["reason"], "wrong-id-type")

    def test_unknown_id_refuted(self):
        self.assertEqual(self._v("ADT9999", "Nope")["reason"], "unknown-id")


class NistControls(unittest.TestCase):
    CAT = validate.load_nist_catalog()  # vendored, offline

    def _v(self, id_, name=None):
        e = {"id": id_, "framework": "nist-800-53"}
        if name is not None:
            e["name"] = name
        return validate.validate_entry(e, {"nist-800-53": self.CAT})

    def test_catalog_loads(self):
        self.assertIsNotNone(self.CAT)
        self.assertEqual(self.CAT.get("SC-7"), "Boundary Protection")

    def test_confirmed_control(self):
        self.assertEqual(self._v("SC-7", "Boundary Protection")["verdict"], "confirmed")

    def test_enhancement_id_confirmed(self):  # display form AC-2(1), not OSCAL ac-2.1
        self.assertEqual(self._v("AC-2(1)", "Automated System Account Management")["verdict"], "confirmed")

    def test_name_mismatch_refuted(self):
        r = self._v("SC-7", "Least Privilege")
        self.assertEqual(r["verdict"], "refuted")
        self.assertTrue(r["reason"].startswith("name-mismatch"))

    def test_no_parent_child_tolerance_for_controls(self):
        # The "Parent: Child" name tolerance is technique-only; a colon form must not confirm a control.
        self.assertEqual(self._v("AC-2(1)", "Account Management: Automated System Account Management")["verdict"],
                         "refuted")

    def test_unknown_id_refuted(self):
        self.assertEqual(self._v("ZZ-99", "Nope")["reason"], "unknown-id")

    def test_catalog_unavailable_is_unverifiable(self):
        r = validate.validate_entry({"id": "SC-7", "framework": "nist-800-53", "name": "Boundary Protection"},
                                    {"nist-800-53": None})
        self.assertEqual(r["verdict"], "unverifiable")

    def test_csf_shaped_id_rejected_under_800_53(self):  # CSF/800-53 no-collision, reverse direction
        self.assertEqual(self._v("PR.AA", "x")["reason"], "malformed-or-unknown-id-shape")


class NistCsf(unittest.TestCase):
    CAT = validate.load_nist_csf_catalog()  # vendored, offline

    def _v(self, id_, name=None):
        e = {"id": id_, "framework": "nist-csf"}
        if name is not None:
            e["name"] = name
        return validate.validate_entry(e, {"nist-csf": self.CAT})

    def test_catalog_loads(self):
        self.assertIsNotNone(self.CAT)
        self.assertEqual(self.CAT.get("PR.AA"), "Identity Management, Authentication, and Access Control")

    def test_confirmed_category(self):
        self.assertEqual(self._v("DE.CM", "Continuous Monitoring")["verdict"], "confirmed")

    def test_id_only_confirms(self):  # no name carried -> id-only validation
        r = self._v("PR.AA")
        self.assertEqual(r["verdict"], "confirmed")
        self.assertEqual(r["reason"], "id-valid-name-not-checked")

    def test_name_mismatch_refuted(self):
        r = self._v("PR.AA", "Continuous Monitoring")
        self.assertEqual(r["verdict"], "refuted")
        self.assertTrue(r["reason"].startswith("name-mismatch"))

    def test_no_parent_child_tolerance_for_controls(self):
        # "Parent: Child" tolerance is technique-only; a colon form must not confirm a CSF category.
        self.assertEqual(self._v("PR.AA", "Protect: Identity Management, Authentication, and Access Control")["verdict"],
                         "refuted")

    def test_subcategory_shape_valid_but_unknown_in_category_seed(self):
        # PR.AA-01 is a valid Subcategory shape; the shipped seed carries Categories only -> unknown-id.
        self.assertEqual(self._v("PR.AA-01", "some outcome")["reason"], "unknown-id")

    def test_unknown_id_refuted(self):
        self.assertEqual(self._v("ZZ.ZZ", "Nope")["reason"], "unknown-id")

    def test_bad_shape_refuted(self):  # a NIST 800-53 style id is not a CSF shape
        self.assertEqual(self._v("AC-2")["reason"], "malformed-or-unknown-id-shape")

    def test_catalog_unavailable_is_unverifiable(self):
        r = validate.validate_entry({"id": "PR.AA", "framework": "nist-csf", "name": "Identity Management, Authentication, and Access Control"},
                                    {"nist-csf": None})
        self.assertEqual(r["verdict"], "unverifiable")


class GateCli(unittest.TestCase):
    def _vf(self, tmp, doc):
        import json as _json
        p = Path(tmp) / "verification.json"
        p.write_text(_json.dumps(doc))
        return str(p)

    def test_all_confirmed_exit_zero(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(validate.main(["--gate", self._vf(tmp, {"verdicts": [{"verdict": "confirmed"}]})]), 0)

    def test_empty_verdict_set_exit_one(self):  # empty must not vacuously pass
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(validate.main(["--gate", self._vf(tmp, {"verdicts": []})]), 1)

    def test_any_refuted_exit_one(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            doc = {"verdicts": [{"verdict": "confirmed"}, {"verdict": "refuted"}]}
            self.assertEqual(validate.main(["--gate", self._vf(tmp, doc)]), 1)


class InputShape(unittest.TestCase):
    def test_technique_id_alias(self):
        r = validate.validate_entry({"technique_id": "T1055", "framework": "attack", "name": "Process Injection"}, FIXTURE)
        self.assertEqual(r["verdict"], "confirmed")

    def test_id_only_when_no_name_confirms(self):
        r = validate.validate_entry({"id": "T1055", "framework": "attack"}, FIXTURE)
        self.assertEqual(r["verdict"], "confirmed")
        self.assertEqual(r["reason"], "id-valid-name-not-checked")

    def test_id_only_still_refutes_bad_id(self):
        self.assertEqual(validate.validate_entry({"id": "T9999", "framework": "attack"}, FIXTURE)["verdict"], "refuted")


class ParentTolerance(unittest.TestCase):
    def test_wrong_parent_segment_refuted(self):  # tightened: parent segment must match too
        self.assertEqual(v("T1566.001", "attack", "Wrong Parent: Spearphishing Attachment")["verdict"], "refuted")

    def test_correct_parent_child_confirmed(self):
        self.assertEqual(v("T1566.001", "attack", "Phishing: Spearphishing Attachment")["verdict"], "confirmed")


class GateCoverage(unittest.TestCase):
    def _f(self, tmp, name, doc):
        import json as _json
        p = Path(tmp) / name
        p.write_text(_json.dumps(doc))
        return str(p)

    def test_missing_expected_id_gates(self):  # dropping a failing entry must not pass
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            vf = self._f(tmp, "v.json", {"verdicts": [{"id": "T1", "verdict": "confirmed"}]})
            idf = self._f(tmp, "ids.json", ["T1", "T2"])
            self.assertEqual(validate.main(["--gate", vf, "--expect-ids", idf]), 1)

    def test_full_coverage_ready(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            vf = self._f(tmp, "v.json", {"verdicts": [{"id": "T1", "verdict": "confirmed"}, {"id": "T2", "verdict": "confirmed"}]})
            idf = self._f(tmp, "ids.json", ["T1", "T2"])
            self.assertEqual(validate.main(["--gate", vf, "--expect-ids", idf]), 0)

    def test_non_dict_verdicts_gate_without_crash(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            vf = self._f(tmp, "v.json", {"verdicts": ["confirmed", "confirmed"]})
            self.assertEqual(validate.main(["--gate", vf]), 1)


class MaintenanceHelpers(unittest.TestCase):
    def test_read_aadapt_version_from_vendored_file(self):
        self.assertEqual(validate.read_catalog_version(Path("/nonexistent"), "aadapt"), "4.4.0")

    def test_read_nist_version_from_vendored_file(self):
        self.assertEqual(validate.read_catalog_version(Path("/nonexistent"), "nist-800-53"), "5.1.1")

    def test_stix_collection_version_extracted(self):
        import json as _json
        bundle = _json.dumps({"objects": [
            {"type": "x-mitre-collection", "version": "15.1"},
            {"type": "attack-pattern", "name": "x"},
        ]}).encode()
        self.assertEqual(validate.stix_collection_version(bundle), "15.1")

    def test_stix_collection_version_absent_is_blank(self):
        self.assertEqual(validate.stix_collection_version(b'{"objects":[]}'), "")


if __name__ == "__main__":
    unittest.main()
