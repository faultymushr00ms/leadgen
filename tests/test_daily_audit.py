"""Fixture tests for the read-only daily zone audit."""

import hashlib
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

AS_OF = date(2026, 10, 23)


def load_audit():
    path = os.path.join(ROOT, "scripts", "daily_audit.py")
    spec = importlib.util.spec_from_file_location("daily_audit", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit = load_audit()


def zone(**overrides):
    base = {
        "name": "Example",
        "region": "Test",
        "utility": "Ohio Edison",
        "aggregationStatus": "confirmed_active_aggregation",
        "currentRate": 9.2,
        "previousRate": 8.0,
        "rateChange": None,
        "supplier": "Test Supplier",
        "termStart": "2026-01-01",
        "termEnd": "2027-06-01",
        "status": "stable",
        "takeaway": "Example is on a program at 9.2¢.",
        "hook": "",
        "notes": "",
        "lastVerified": "2026-10-01",
        "sourceUrl": "https://example.com/example",
        "_source_file": "fixture",
    }
    base.update(overrides)
    return base


def issues_of(zones, stale_days=60, docs="", file_counts=None):
    report = audit.build_report(
        zones,
        file_counts or {},
        [],
        docs,
        AS_OF,
        stale_days,
        None,
    )
    return report


def types(report):
    return [item["type"] for item in report["issues"]]


class CleanZoneTests(unittest.TestCase):
    def test_baseline_zone_has_no_issues(self):
        report = issues_of([zone()])
        self.assertEqual(report["totalIssues"], 0)
        self.assertEqual(types(report), [])

    def test_zone_dict_is_not_mutated(self):
        original = zone()
        snapshot = json.dumps(original, sort_keys=True)
        issues_of([original])
        self.assertEqual(json.dumps(original, sort_keys=True), snapshot)


class StatusAndTermTests(unittest.TestCase):
    def test_pain_coming_after_term_end_is_flagged(self):
        report = issues_of([zone(
            name="Springdale",
            status="pain_coming",
            termEnd="2026-08-31",
            takeaway="Springdale is on Dynegy at 9.2¢.",
        )])
        self.assertIn("status_after_term_end", types(report))

    def test_stable_after_term_end_is_flagged(self):
        report = issues_of([zone(status="stable", termEnd="2026-08-31")])
        self.assertIn("status_after_term_end", types(report))

    def test_active_status_after_term_end_is_flagged(self):
        report = issues_of([zone(status="active", termEnd="2026-08-31")])
        self.assertIn("status_after_term_end", types(report))

    def test_status_on_the_term_end_date_is_not_flagged(self):
        report = issues_of([zone(status="pain_coming", termEnd="2026-10-23")])
        self.assertNotIn("status_after_term_end", types(report))

    def test_month_precision_lasts_through_the_month(self):
        still_open = issues_of([zone(status="pain_coming", termEnd="2026-10")])
        self.assertNotIn("status_after_term_end", types(still_open))
        ended = issues_of([zone(status="pain_coming", termEnd="2026-08")])
        self.assertIn("status_after_term_end", types(ended))

    def test_rollover_and_pain_hit_after_term_end_are_not_flagged(self):
        for status in ("rollover", "pain_hit", "pricing_updated", "transition", "verify"):
            report = issues_of([zone(status=status, termEnd="2026-08-31")])
            self.assertNotIn("status_after_term_end", types(report), status)

    def test_pain_coming_before_term_end_is_not_flagged(self):
        report = issues_of([zone(status="pain_coming", termEnd="2027-06-01")])
        self.assertNotIn("status_after_term_end", types(report))

    def test_parse_term_end_month_lengths(self):
        self.assertEqual(audit.parse_term_end("2024-02"), date(2024, 2, 29))
        self.assertEqual(audit.parse_term_end("2026-02"), date(2026, 2, 28))
        self.assertEqual(audit.parse_term_end("2026-08-31"), date(2026, 8, 31))
        self.assertIsNone(audit.parse_term_end(None))
        self.assertIsNone(audit.parse_term_end("August 2026"))


class RenewalWindowTests(unittest.TestCase):
    def test_countdown_after_term_end_is_stale(self):
        report = issues_of([zone(
            name="Springdale",
            status="rollover",
            termEnd="2026-08-31",
            takeaway="Renewal window opens in 60 days into the next term at 9.2¢.",
        )])
        matched = [item for item in report["issues"] if item["type"] == "stale_renewal_window"]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["fields"]["reason"], "term ended")
        self.assertEqual(matched[0]["fields"]["statedDays"], 60)

    def test_accurate_countdown_is_not_flagged(self):
        report = issues_of([zone(
            termEnd="2026-12-22",
            takeaway="Renewal window opens in 60 days. Current rate 9.2¢.",
        )])
        self.assertNotIn("stale_renewal_window", types(report))

    def test_countdown_outside_tolerance_is_flagged(self):
        report = issues_of([zone(
            termEnd="2026-12-22",
            takeaway="Renewal window opens in 80 days. Current rate 9.2¢.",
        )])
        self.assertIn("stale_renewal_window", types(report))

    def test_phrase_in_notes_is_checked(self):
        report = issues_of([zone(
            status="rollover",
            termEnd="2026-08-31",
            notes="Renewal window opens in 60 days.",
        )])
        self.assertIn("stale_renewal_window", types(report))


class AggregationTermTests(unittest.TestCase):
    def test_term_on_zone_with_no_program_is_flagged(self):
        report = issues_of([zone(
            name="Stark County (Unincorporated / Remaining)",
            aggregationStatus="no_aggregation_verified",
            currentRate=None,
            previousRate=None,
            termStart="2025-08-01",
            termEnd="2026-08-31",
            status="verify",
            takeaway="No county-wide program.",
            sourceUrl=None,
        )])
        self.assertIn("term_without_aggregation", types(report))

    def test_term_on_municipal_zone_is_flagged(self):
        report = issues_of([zone(
            aggregationStatus="municipal_utility",
            currentRate=None,
            previousRate=None,
            termEnd="2027-01-01",
            status="verify",
            takeaway="Municipal utility.",
            sourceUrl=None,
        )])
        self.assertIn("term_without_aggregation", types(report))

    def test_confirmed_aggregation_may_have_term_dates(self):
        report = issues_of([zone()])
        self.assertNotIn("term_without_aggregation", types(report))

    def test_blank_terms_are_not_dates(self):
        report = issues_of([zone(
            aggregationStatus="no_aggregation_verified",
            currentRate=None,
            previousRate=None,
            termStart="",
            termEnd=None,
            status="verify",
            takeaway="No program.",
            sourceUrl=None,
        )])
        self.assertNotIn("term_without_aggregation", types(report))


class RateChangeAuditTests(unittest.TestCase):
    def test_disagreement_uses_rate_change_module(self):
        self.assertEqual(audit.rate_change.percent_change(12, 10), 20.0)
        report = issues_of([zone(currentRate=12, previousRate=10, rateChange=5, takeaway="Rate is 12¢, prior 10¢.")])
        matched = [item for item in report["issues"] if item["type"] == "rate_change_disagreement"]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["fields"]["computed"], 20.0)
        self.assertEqual(matched[0]["fields"]["disagreement"], 15.0)
        self.assertNotIn("rate_change_without_previous", types(report))

    def test_stored_percent_within_half_a_point_is_not_flagged(self):
        report = issues_of([zone(
            currentRate=12,
            previousRate=10,
            rateChange=20.5,
            takeaway="Rate is 12¢, prior 10¢, up 20.5%.",
        )])
        self.assertNotIn("rate_change_disagreement", types(report))

    def test_stored_percent_just_over_half_a_point_is_flagged(self):
        report = issues_of([zone(
            currentRate=12,
            previousRate=10,
            rateChange=20.6,
            takeaway="Rate is 12¢, prior 10¢.",
        )])
        self.assertIn("rate_change_disagreement", types(report))

    def test_rate_change_with_null_previous_is_flagged(self):
        report = issues_of([zone(
            name="Dayton",
            currentRate=8.71,
            previousRate=None,
            rateChange=22.7,
            takeaway="Dayton aggregation at 8.71¢.",
        )])
        self.assertIn("rate_change_without_previous", types(report))
        self.assertNotIn("rate_change_disagreement", types(report))

    def test_missing_rate_change_is_not_a_disagreement(self):
        report = issues_of([zone(rateChange=None)])
        self.assertNotIn("rate_change_disagreement", types(report))
        self.assertNotIn("rate_change_without_previous", types(report))


class CoverageTests(unittest.TestCase):
    def test_confirmed_aggregation_without_a_rate(self):
        report = issues_of([zone(
            currentRate=None,
            previousRate=None,
            takeaway="Program is on file.",
            sourceUrl="https://example.com/example",
        )])
        self.assertIn("missing_current_rate", types(report))

    def test_zero_rate_is_still_a_rate(self):
        report = issues_of([zone(currentRate=0, previousRate=None, takeaway="Rate is 0¢.")])
        self.assertNotIn("missing_current_rate", types(report))

    def test_rate_without_source_url(self):
        for empty in (None, "", "  ", "null"):
            report = issues_of([zone(sourceUrl=empty)])
            self.assertIn("missing_source_url", types(report), empty)

    def test_rate_with_source_url_is_fine(self):
        report = issues_of([zone(sourceUrl="https://example.com/rate")])
        self.assertNotIn("missing_source_url", types(report))

    def test_no_rate_and_no_url_is_not_a_source_issue(self):
        report = issues_of([zone(
            aggregationStatus="no_aggregation_verified",
            currentRate=None,
            previousRate=None,
            termStart=None,
            termEnd=None,
            status="verify",
            takeaway="No program on file.",
            sourceUrl=None,
        )])
        self.assertNotIn("missing_source_url", types(report))

    def test_last_verified_threshold(self):
        fresh = issues_of([zone(lastVerified="2026-08-24")])
        self.assertNotIn("last_verified_stale", types(fresh))
        stale = issues_of([zone(lastVerified="2026-08-23")])
        self.assertIn("last_verified_stale", types(stale))
        self.assertEqual(
            [item for item in stale["issues"] if item["type"] == "last_verified_stale"][0]["fields"]["ageDays"],
            61,
        )

    def test_custom_stale_days(self):
        report = issues_of([zone(lastVerified="2026-10-01")], stale_days=5)
        self.assertIn("last_verified_stale", types(report))

    def test_missing_and_unparseable_last_verified(self):
        missing = issues_of([zone(lastVerified=None)])
        self.assertEqual(
            [item for item in missing["issues"] if item["type"] == "last_verified_stale"][0]["fields"]["reason"],
            "missing",
        )
        bad = issues_of([zone(lastVerified="08/01/2026")])
        self.assertEqual(
            [item for item in bad["issues"] if item["type"] == "last_verified_stale"][0]["fields"]["reason"],
            "unparseable",
        )


class UtilityContradictionTests(unittest.TestCase):
    def _muni(self, **overrides):
        base = dict(
            aggregationStatus="municipal_utility",
            utility="Amherst Municipal Power",
            currentRate=None,
            previousRate=None,
            termStart=None,
            termEnd=None,
            status="stable",
            takeaway="Amherst has no aggregation program on file.",
            hook="",
            sourceUrl=None,
        )
        base.update(overrides)
        return zone(**base)

    def test_notes_that_assign_iou_territory_are_flagged(self):
        report = issues_of([self._muni(name="Amherst", notes="Ohio Edison territory. Lorain County.")])
        matched = [item for item in report["issues"] if item["type"] == "utility_contradiction"]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["fields"]["matched"].lower(), "ohio edison territory")

    def test_negated_or_overlap_language_is_not_a_contradiction(self):
        outside = issues_of([self._muni(notes="Accounts outside Ohio Edison territory stay municipal.")])
        self.assertNotIn("utility_contradiction", types(outside))
        overlap = issues_of([self._muni(
            aggregationStatus="electric_cooperative",
            notes="Toledo Edison territory overlaps here — verify from bill.",
        )])
        self.assertNotIn("utility_contradiction", types(overlap))

    def test_takeaway_alone_does_not_flag(self):
        report = issues_of([self._muni(notes="", takeaway="Ohio Edison territory.")])
        self.assertNotIn("utility_contradiction", types(report))

    def test_cooperative_unqualified_territory_is_flagged(self):
        report = issues_of([self._muni(
            aggregationStatus="electric_cooperative",
            notes="Ohio Edison territory.",
        )])
        self.assertIn("utility_contradiction", types(report))

    def test_aggregation_in_iou_territory_is_not_a_contradiction(self):
        report = issues_of([zone(notes="Ohio Edison territory.")])
        self.assertNotIn("utility_contradiction", types(report))


class TextNumberTests(unittest.TestCase):
    def test_cents_that_are_not_the_stored_rate(self):
        report = issues_of([zone(
            name="Hamilton Township (Warren Co)",
            currentRate=9.2,
            previousRate=None,
            status="rollover",
            termEnd="2026-07-31",
            takeaway="Accounts are now on Duke Energy Ohio default supply at 10.70¢+.",
            sourceUrl=None,
        )])
        matched = [item for item in report["issues"] if item["type"] == "text_number_mismatch"]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["fields"]["token"], "10.70")
        self.assertEqual(matched[0]["fields"]["currentRate"], 9.2)

    def test_rounded_text_matches_stored_rates(self):
        rounded = issues_of([zone(currentRate=9.2, takeaway="Current price is 9.20¢.")])
        self.assertNotIn("text_number_mismatch", types(rounded))
        near = issues_of([zone(currentRate=10.691, previousRate=8.71, takeaway="Default is 10.69¢ from 8.71¢.")])
        self.assertNotIn("text_number_mismatch", types(near))

    def test_percent_matches_stored_or_computed(self):
        stored = issues_of([zone(
            currentRate=9.657,
            previousRate=7.289,
            rateChange=32.5,
            takeaway="Went from 7.289¢ to 9.657¢, a 32% hit.",
        )])
        self.assertNotIn("text_number_mismatch", types(stored))

    def test_renewable_wording_is_ignored(self):
        report = issues_of([zone(takeaway="100% renewable option beside the 9.2¢ rate.")])
        self.assertNotIn("text_number_mismatch", types(report))

    def test_unmatched_percent_is_flagged(self):
        report = issues_of([zone(
            previousRate=None,
            rateChange=None,
            takeaway="Example is 9.2¢, a 15% increase at renewal.",
        )])
        matched = [item for item in report["issues"] if item["type"] == "text_number_mismatch"]
        self.assertEqual([item["fields"]["token"] for item in matched], ["15"])

    def test_notes_are_not_scanned_for_numbers(self):
        report = issues_of([zone(notes="Market is 10.70¢.", takeaway="Example is on a program at 9.2¢.")])
        self.assertNotIn("text_number_mismatch", types(report))


class DocumentationTests(unittest.TestCase):
    def test_matching_counts_are_not_flagged(self):
        docs = "\n".join([
            "  regions/                      # 1 JSON files, 1 zones total",
            "    ohio_electric_cooperatives.json   # 1 co-ops",
            "- **Electric co-ops**: All 1 Ohio co-ops are served by Buckeye Power Inc.",
        ])
        zones = [zone(
            aggregationStatus="electric_cooperative",
            currentRate=None,
            previousRate=None,
            termStart=None,
            termEnd=None,
            status="stable",
            takeaway="Co-op.",
            sourceUrl=None,
            _source_file="ohio_electric_cooperatives",
        )]
        report = issues_of(
            zones,
            docs=docs,
            file_counts={"ohio_electric_cooperatives.json": 1},
        )
        self.assertNotIn("doc_count_mismatch", types(report))

    def test_mismatched_counts_are_flagged(self):
        docs = "\n".join([
            "  regions/                      # 2 JSON files, 9 zones total",
            "    ohio_municipal_utilities.json     # 47 municipal utilities",
            "- **Electric co-ops**: All 25 Ohio co-ops are served by Buckeye Power Inc.",
            "- **NOAC**: 13 Toledo-area communities (Toledo Edison).",
        ])
        zones = [zone(
            aggregationStatus="electric_cooperative",
            currentRate=None,
            previousRate=None,
            termStart=None,
            termEnd=None,
            status="stable",
            takeaway="Co-op.",
            sourceUrl=None,
        )]
        report = issues_of(
            zones,
            docs=docs,
            file_counts={"ohio_municipal_utilities.json": 48, "toledo_lucas_noac.json": 12},
        )
        details = {item["detail"]: item for item in report["issues"] if item["type"] == "doc_count_mismatch"}
        self.assertNotIn("files_total", details)
        self.assertEqual(details["zones_total"]["fields"]["documented"], 9)
        self.assertEqual(details["zones_total"]["fields"]["actual"], 1)
        self.assertEqual(details["file:ohio_municipal_utilities.json"]["fields"]["actual"], 48)
        self.assertEqual(details["prose:ohio_coops"]["fields"]["documented"], 25)
        self.assertEqual(details["prose:ohio_coops"]["fields"]["actual"], 1)
        self.assertEqual(details["prose:noac"]["fields"]["actual"], 12)

    def test_approximate_counts_are_skipped(self):
        self.assertIsNone(audit.first_count("~14 central Ohio communities"))
        self.assertIsNone(audit.first_count("Serves 235+ communities"))
        self.assertEqual(audit.first_count("NOAC (13 Toledo-area communities)"), 13)

    def test_real_claude_claims_are_recognized(self):
        with open(os.path.join(ROOT, "CLAUDE.md"), encoding="utf-8") as handle:
            text = handle.read()
        found = audit.check_docs(text, [], {})
        by_detail = {item["detail"]: item for item in found}
        self.assertEqual(by_detail["zones_total"]["fields"]["documented"], 251)
        self.assertEqual(by_detail["files_total"]["fields"]["documented"], 18)
        self.assertEqual(by_detail["file:ohio_municipal_utilities.json"]["fields"]["documented"], 47)
        self.assertEqual(by_detail["file:ohio_electric_cooperatives.json"]["fields"]["documented"], 24)
        self.assertEqual(by_detail["prose:ohio_coops"]["fields"]["documented"], 25)
        self.assertEqual(by_detail["file:nopec_cuyahoga_suburbs.json"]["fields"]["documented"], 23)
        self.assertEqual(by_detail["prose:noac"]["fields"]["documented"], 13)
        self.assertEqual(by_detail["file:toledo_lucas_noac.json"]["fields"]["documented"], 13)


class ReportWritingTests(unittest.TestCase):
    def test_summary_precedes_zone_lists_and_json_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            regions = os.path.join(tmp, "regions")
            os.makedirs(regions)
            with open(os.path.join(regions, "fixture.json"), "w", encoding="utf-8") as handle:
                json.dump([zone(name="Springdale", status="pain_coming", termEnd="2026-08-31")], handle)
            docs = os.path.join(tmp, "CLAUDE.md")
            with open(docs, "w", encoding="utf-8") as handle:
                handle.write("  regions/ # 1 JSON files, 1 zones total\n")
            out = os.path.join(tmp, "reports")
            code = audit.main([
                "--regions", regions,
                "--docs", docs,
                "--out", out,
                "--as-of", "2026-10-23",
                "--stale-days", "60",
            ])
            self.assertEqual(code, 0)
            md_path = os.path.join(out, "audit_2026-10-23.md")
            json_path = os.path.join(out, "audit_2026-10-23.json")
            with open(md_path, encoding="utf-8") as handle:
                md = handle.read()
            self.assertLess(md.index("## Summary"), md.index("## Changes since the previous audit"))
            self.assertLess(md.index("## Changes since the previous audit"), md.index("## Status after term end"))
            self.assertIn("No previous audit", md)
            self.assertIn("Springdale", md)
            with open(json_path, encoding="utf-8") as handle:
                payload = json.load(handle)
            self.assertEqual(payload["zonesScanned"], 1)
            self.assertEqual(payload["totalIssues"], sum(payload["counts"].values()))
            self.assertGreaterEqual(payload["counts"]["status_after_term_end"], 1)

    def test_same_inputs_are_deterministic(self):
        zones = [zone(name="Springdale", status="pain_coming", termEnd="2026-08-31")]
        first = issues_of(zones)
        second = issues_of(zones)
        self.assertEqual(
            json.dumps(first, sort_keys=True),
            json.dumps(second, sort_keys=True),
        )

    def test_second_run_reports_new_and_resolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            regions = os.path.join(tmp, "regions")
            os.makedirs(regions)
            path = os.path.join(regions, "fixture.json")
            docs = os.path.join(tmp, "CLAUDE.md")
            with open(docs, "w", encoding="utf-8") as handle:
                handle.write("  regions/ # 1 JSON files, 1 zones total\n")
            out = os.path.join(tmp, "reports")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump([zone(name="Springdale", status="pain_coming", termEnd="2026-08-31")], handle)
            self.assertEqual(audit.main([
                "--regions", regions, "--docs", docs, "--out", out, "--as-of", "2026-10-23",
            ]), 0)
            with open(path, "w", encoding="utf-8") as handle:
                json.dump([zone(name="Dayton", currentRate=8.71, previousRate=None, rateChange=22.7,
                                 takeaway="Dayton aggregation at 8.71¢.")], handle)
            self.assertEqual(audit.main([
                "--regions", regions, "--docs", docs, "--out", out, "--as-of", "2026-10-23",
            ]), 0)
            with open(os.path.join(out, "audit_2026-10-23.json"), encoding="utf-8") as handle:
                payload = json.load(handle)
            new_zones = [item["zone"] for item in payload["changes"]["new"]]
            resolved_zones = [item["zone"] for item in payload["changes"]["resolved"]]
            self.assertIn("Dayton", new_zones)
            self.assertIn("Springdale", resolved_zones)
            self.assertEqual(payload["changes"]["previousDate"], "2026-10-23")

    def test_region_files_are_not_modified(self):
        with tempfile.TemporaryDirectory() as tmp:
            regions = os.path.join(tmp, "regions")
            os.makedirs(regions)
            path = os.path.join(regions, "fixture.json")
            payload = [zone(status="pain_coming", termEnd="2026-08-31")]
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle)
            with open(path, "rb") as handle:
                before = handle.read()
            code = audit.main([
                "--regions", regions,
                "--docs", os.path.join(tmp, "missing.md"),
                "--out", os.path.join(tmp, "reports"),
                "--as-of", "2026-10-23",
            ])
            self.assertEqual(code, 0)
            with open(path, "rb") as handle:
                self.assertEqual(handle.read(), before)

    def test_invalid_region_file_is_reported_and_scan_continues(self):
        with tempfile.TemporaryDirectory() as tmp:
            regions = os.path.join(tmp, "regions")
            os.makedirs(regions)
            with open(os.path.join(regions, "bad.json"), "w", encoding="utf-8") as handle:
                handle.write("{")
            with open(os.path.join(regions, "ok.json"), "w", encoding="utf-8") as handle:
                json.dump([zone(name="Kept")], handle)
            zones, _counts, issues = audit.load_regions(regions)
            self.assertEqual([item["name"] for item in zones], ["Kept"])
            self.assertEqual(issues[0]["type"], "region_file_invalid")

    def test_bad_cli_args(self):
        self.assertEqual(audit.main(["--as-of", "October", "--regions", ROOT]), 1)
        self.assertEqual(audit.main(["--stale-days", "-1", "--regions", os.path.join(ROOT, "data", "regions")]), 1)
        self.assertEqual(audit.main(["--regions", os.path.join(ROOT, "no-such-regions")]), 1)

    def test_script_does_not_import_network_or_llm_libraries(self):
        with open(os.path.join(ROOT, "scripts", "daily_audit.py"), encoding="utf-8") as handle:
            source = handle.read()
        for banned in ("import requests", "import urllib", "import openai", "import anthropic", "ollama"):
            self.assertNotIn(banned, source)


class RealDataSmokeTests(unittest.TestCase):
    def test_real_regions_are_read_only_and_known_checks_fire(self):
        regions = os.path.join(ROOT, "data", "regions")
        before = _snapshot(regions)
        docs_before = _sha(os.path.join(ROOT, "CLAUDE.md"))
        with tempfile.TemporaryDirectory() as tmp:
            code = audit.main([
                "--regions", regions,
                "--docs", os.path.join(ROOT, "CLAUDE.md"),
                "--out", tmp,
                "--as-of", "2026-10-23",
                "--stale-days", "60",
            ])
            self.assertEqual(code, 0)
            with open(os.path.join(tmp, "audit_2026-10-23.json"), encoding="utf-8") as handle:
                payload = json.load(handle)
        self.assertEqual(_snapshot(regions), before)
        self.assertEqual(_sha(os.path.join(ROOT, "CLAUDE.md")), docs_before)
        self.assertGreater(payload["zonesScanned"], 0)
        for key in (
            "status_after_term_end",
            "stale_renewal_window",
            "term_without_aggregation",
            "rate_change_without_previous",
            "missing_current_rate",
            "missing_source_url",
            "utility_contradiction",
            "text_number_mismatch",
            "doc_count_mismatch",
        ):
            self.assertGreater(payload["counts"][key], 0, key)


def _sha(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _snapshot(directory):
    found = {}
    for dirpath, _dirs, files in os.walk(directory):
        for name in files:
            path = os.path.join(dirpath, name)
            found[os.path.relpath(path, directory)] = _sha(path)
    return found


if __name__ == "__main__":
    unittest.main()
