"""Tests for scripts/daily_audit.py"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def _zone(**kwargs) -> dict:
    base = {
        "name": "TestCity",
        "region": "NE Ohio",
        "utility": "Ohio Edison",
        "utilityParent": "FirstEnergy",
        "aggregationStatus": "confirmed_active_aggregation",
        "currentRate": 9.999,
        "previousRate": 8.999,
        "rateChange": 11.1,
        "supplier": "NOPEC",
        "termStart": "2026-06-01",
        "termEnd": "2027-06-01",
        "status": "pricing_updated",
        "confidence": "high",
        "takeaway": "Rate jumped 11%.",
        "hook": "Hi, calling about your energy rate — NOPEC just moved to 9.999¢.",
        "futureUse": "aggregation",
        "lastVerified": "2026-10-01",
        "sourceUrl": "https://nopec.org",
        "_source_file": "nopec_cuyahoga_suburbs",
        "commodity": "electric",
    }
    base.update(kwargs)
    return base


class TestExpiredActive(unittest.TestCase):
    def test_expired_pain_coming_flagged(self):
        from scripts.daily_audit import _check_zone
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        z = _zone(termEnd=yesterday, status="pain_coming")
        findings = _check_zone(z)
        self.assertTrue(any(f["check"] == "EXPIRED_ACTIVE" for f in findings))

    def test_future_term_ok(self):
        from scripts.daily_audit import _check_zone
        z = _zone(termEnd="2028-01-01", status="pain_coming")
        findings = _check_zone(z)
        self.assertFalse(any(f["check"] == "EXPIRED_ACTIVE" for f in findings))

    def test_rollover_not_flagged(self):
        from scripts.daily_audit import _check_zone
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        z = _zone(termEnd=yesterday, status="rollover")
        findings = _check_zone(z)
        self.assertFalse(any(f["check"] == "EXPIRED_ACTIVE" for f in findings))

    def test_severity_high(self):
        from scripts.daily_audit import _check_zone
        past = (date.today() - timedelta(days=30)).isoformat()
        z = _zone(termEnd=past, status="transition")
        findings = _check_zone(z)
        expired = [f for f in findings if f["check"] == "EXPIRED_ACTIVE"]
        self.assertEqual(expired[0]["severity"], "HIGH")


class TestStaleRenewal(unittest.TestCase):
    def test_rollover_91_days_flagged(self):
        from scripts.daily_audit import _check_zone
        old = (date.today() - timedelta(days=91)).isoformat()
        z = _zone(termEnd=old, status="rollover")
        findings = _check_zone(z)
        self.assertTrue(any(f["check"] == "STALE_RENEWAL" for f in findings))

    def test_rollover_30_days_ok(self):
        from scripts.daily_audit import _check_zone
        recent = (date.today() - timedelta(days=30)).isoformat()
        z = _zone(termEnd=recent, status="rollover")
        findings = _check_zone(z)
        self.assertFalse(any(f["check"] == "STALE_RENEWAL" for f in findings))

    def test_stale_1_year_is_high(self):
        from scripts.daily_audit import _check_zone
        old = (date.today() - timedelta(days=370)).isoformat()
        z = _zone(termEnd=old, status="rollover_dissolved")
        findings = _check_zone(z)
        stale = [f for f in findings if f["check"] == "STALE_RENEWAL"]
        self.assertTrue(stale)
        self.assertEqual(stale[0]["severity"], "HIGH")


class TestAggNoRate(unittest.TestCase):
    def test_confirmed_no_rate_flagged(self):
        from scripts.daily_audit import _check_zone
        z = _zone(aggregationStatus="confirmed_active_aggregation", currentRate=None)
        findings = _check_zone(z)
        self.assertTrue(any(f["check"] == "AGG_NO_RATE" for f in findings))

    def test_confirmed_with_rate_ok(self):
        from scripts.daily_audit import _check_zone
        z = _zone(aggregationStatus="confirmed_active_aggregation", currentRate=9.999)
        findings = _check_zone(z)
        self.assertFalse(any(f["check"] == "AGG_NO_RATE" for f in findings))


class TestRateMismatch(unittest.TestCase):
    def test_wrong_rate_change_flagged(self):
        from scripts.daily_audit import _check_zone
        # 10 → 11 = +10%, but rateChange says 5
        z = _zone(currentRate=11.0, previousRate=10.0, rateChange=5.0)
        findings = _check_zone(z)
        self.assertTrue(any(f["check"] == "RATE_MISMATCH" for f in findings))

    def test_correct_rate_change_passes(self):
        from scripts.daily_audit import _check_zone
        z = _zone(currentRate=9.999, previousRate=8.999, rateChange=11.1)
        findings = _check_zone(z)
        self.assertFalse(any(f["check"] == "RATE_MISMATCH" for f in findings))

    def test_rate_change_no_prev_flagged(self):
        from scripts.daily_audit import _check_zone
        z = _zone(currentRate=9.999, previousRate=None, rateChange=11.1)
        findings = _check_zone(z)
        self.assertTrue(any(f["check"] == "RATE_CHANGE_NO_PREV" for f in findings))


class TestStale60(unittest.TestCase):
    def test_old_zone_flagged(self):
        from scripts.daily_audit import _check_zone
        old = (date.today() - timedelta(days=61)).isoformat()
        z = _zone(lastVerified=old, aggregationStatus="confirmed_active_aggregation")
        findings = _check_zone(z)
        self.assertTrue(any(f["check"] == "STALE_60" for f in findings))

    def test_recent_zone_ok(self):
        from scripts.daily_audit import _check_zone
        recent = (date.today() - timedelta(days=30)).isoformat()
        z = _zone(lastVerified=recent)
        findings = _check_zone(z)
        self.assertFalse(any(f["check"] == "STALE_60" for f in findings))

    def test_municipal_utility_exempt(self):
        from scripts.daily_audit import _check_zone
        old = (date.today() - timedelta(days=200)).isoformat()
        z = _zone(lastVerified=old, aggregationStatus="municipal_utility")
        findings = _check_zone(z)
        self.assertFalse(any(f["check"] == "STALE_60" for f in findings))

    def test_180_days_is_high(self):
        from scripts.daily_audit import _check_zone
        old = (date.today() - timedelta(days=181)).isoformat()
        z = _zone(lastVerified=old, aggregationStatus="confirmed_active_aggregation")
        findings = _check_zone(z)
        stale = [f for f in findings if f["check"] == "STALE_60"]
        self.assertEqual(stale[0]["severity"], "HIGH")


class TestMuniIouNotes(unittest.TestCase):
    def test_muni_with_iou_notes_flagged(self):
        from scripts.daily_audit import _check_zone
        z = _zone(aggregationStatus="municipal_utility",
                  notes="Served by AEP Ohio in surrounding territory. Municipal for city core.")
        findings = _check_zone(z)
        self.assertTrue(any(f["check"] == "MUNI_IOU_NOTES" for f in findings))

    def test_muni_clean_notes_ok(self):
        from scripts.daily_audit import _check_zone
        z = _zone(aggregationStatus="municipal_utility",
                  notes="City-owned utility. Not subject to retail choice.")
        findings = _check_zone(z)
        self.assertFalse(any(f["check"] == "MUNI_IOU_NOTES" for f in findings))


class TestCopyRateMismatch(unittest.TestCase):
    def test_wrong_rate_in_takeaway_flagged(self):
        from scripts.daily_audit import _check_zone
        z = _zone(currentRate=9.999, previousRate=8.999,
                  takeaway="Rate is now 12.5¢ per kWh — massive pain story.")
        findings = _check_zone(z)
        self.assertTrue(any(f["check"] == "COPY_RATE_MISMATCH" for f in findings))

    def test_correct_rate_in_hook_ok(self):
        from scripts.daily_audit import _check_zone
        z = _zone(currentRate=9.999, previousRate=8.999,
                  hook="Your rate just moved to 9.999¢ — that's a big jump.")
        findings = _check_zone(z)
        self.assertFalse(any(f["check"] == "COPY_RATE_MISMATCH" for f in findings))

    def test_wrong_pct_in_takeaway_flagged(self):
        from scripts.daily_audit import _check_zone
        z = _zone(currentRate=9.999, previousRate=8.999, rateChange=11.1,
                  takeaway="Rate jumped +25% — that's enormous.")
        findings = _check_zone(z)
        self.assertTrue(any(f["check"] == "COPY_RATE_MISMATCH" for f in findings))


class TestRegionAssignment(unittest.TestCase):
    def test_ashtabula_region_field(self):
        from scripts.daily_audit import _assign_region
        z = _zone(region="NE Ohio / Ashtabula", _source_file="ne_ohio_firstenergy")
        self.assertEqual(_assign_region(z), "Ashtabula County")

    def test_nopec_suburbs_region(self):
        from scripts.daily_audit import _assign_region
        z = _zone(_source_file="nopec_cuyahoga_suburbs")
        self.assertEqual(_assign_region(z), "NE Ohio / Cleveland / NOPEC")

    def test_akron_region(self):
        from scripts.daily_audit import _assign_region
        z = _zone(_source_file="akron_summit_medina")
        self.assertEqual(_assign_region(z), "Akron / Canton")


class TestFindingId(unittest.TestCase):
    def test_same_finding_same_id(self):
        from scripts.daily_audit import _finding_id
        f1 = {"source_file": "nopec", "zone": "Parma", "check": "STALE_60"}
        f2 = {"source_file": "nopec", "zone": "Parma", "check": "STALE_60"}
        self.assertEqual(_finding_id(f1), _finding_id(f2))

    def test_different_check_different_id(self):
        from scripts.daily_audit import _finding_id
        f1 = {"source_file": "nopec", "zone": "Parma", "check": "STALE_60"}
        f2 = {"source_file": "nopec", "zone": "Parma", "check": "EXPIRED_ACTIVE"}
        self.assertNotEqual(_finding_id(f1), _finding_id(f2))


class TestDiffLogic(unittest.TestCase):
    def test_new_finding_detected(self):
        from scripts.daily_audit import _finding_id, _generate_report
        today_f = [{"source_file": "nopec", "zone": "Parma", "check": "STALE_60",
                    "severity": "LOW", "detail": "old", "region": "NE Ohio", "commodity": "electric",
                    "current_value": "", "flagged_at": "2026-10-23"}]
        prev_f = []
        report = _generate_report(today_f, prev_f, 1, 0.1)
        self.assertEqual(len(report["new"]), 1)
        self.assertEqual(len(report["resolved"]), 0)

    def test_resolved_finding_detected(self):
        from scripts.daily_audit import _finding_id, _generate_report
        finding = {"source_file": "nopec", "zone": "Parma", "check": "STALE_60",
                   "severity": "LOW", "detail": "old", "region": "NE Ohio", "commodity": "electric",
                   "current_value": "", "flagged_at": "2026-10-22"}
        report = _generate_report([], [finding], 1, 0.1)
        self.assertEqual(len(report["new"]), 0)
        self.assertEqual(len(report["resolved"]), 1)

    def test_persistent_finding_not_new_or_resolved(self):
        from scripts.daily_audit import _finding_id, _generate_report
        finding = {"source_file": "nopec", "zone": "Parma", "check": "STALE_60",
                   "severity": "LOW", "detail": "old", "region": "NE Ohio", "commodity": "electric",
                   "current_value": "", "flagged_at": "2026-10-22"}
        today_f = [dict(finding, flagged_at="2026-10-23")]
        report = _generate_report(today_f, [finding], 1, 0.1)
        self.assertEqual(len(report["new"]), 0)
        self.assertEqual(len(report["resolved"]), 0)


class TestRunAuditIntegration(unittest.TestCase):
    def test_full_run_produces_files(self):
        from scripts.daily_audit import run_audit
        report = run_audit(verbose=False)
        self.assertIn("zones_checked", report)
        self.assertIn("findings", report)
        self.assertIn("totals", report)
        self.assertIn("by_region", report)
        self.assertGreater(report["zones_checked"], 0)

    def test_md_file_written(self):
        import glob
        from scripts.daily_audit import REPORTS_DIR, run_audit
        run_audit(verbose=False)
        latest = os.path.join(REPORTS_DIR, "audit_latest.md")
        self.assertTrue(os.path.exists(latest))
        content = open(latest).read()
        self.assertIn("FORGE Daily Audit", content)
        self.assertIn("zones checked", content.lower())

    def test_json_file_valid(self):
        import glob
        from scripts.daily_audit import REPORTS_DIR, run_audit
        run_audit(verbose=False)
        latest = os.path.join(REPORTS_DIR, "audit_latest.json")
        self.assertTrue(os.path.exists(latest))
        data = json.load(open(latest))
        self.assertIn("date", data)
        self.assertIn("findings", data)


if __name__ == "__main__":
    unittest.main()
