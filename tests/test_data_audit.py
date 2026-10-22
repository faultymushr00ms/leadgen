"""Tests for scripts/data_audit.py — local data consistency checks."""

import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def _zone(**kwargs):
    base = {
        "name": "TestZone",
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
        "hook": "Hi, this is...",
        "futureUse": "aggregation",
        "lastVerified": "2026-10-01",
        "sourceUrl": "https://nopec.org",
        "_source_file": "nopec_cuyahoga_suburbs",
        "commodity": "electric",
    }
    base.update(kwargs)
    return base


class TestExpiredWrongStatus(unittest.TestCase):
    def test_expired_pain_coming_flagged(self):
        from scripts.data_audit import expired_wrong_status
        z = _zone(termEnd="2025-01-01", status="pain_coming")
        results = expired_wrong_status([z])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["check"], "EXPIRED_WRONG_STATUS")

    def test_expired_rollover_not_flagged(self):
        from scripts.data_audit import expired_wrong_status
        z = _zone(termEnd="2025-01-01", status="rollover")
        results = expired_wrong_status([z])
        self.assertEqual(results, [])

    def test_future_term_end_not_flagged(self):
        from scripts.data_audit import expired_wrong_status
        z = _zone(termEnd="2027-12-01", status="pain_coming")
        results = expired_wrong_status([z])
        self.assertEqual(results, [])

    def test_coop_exempt(self):
        from scripts.data_audit import expired_wrong_status
        z = _zone(termEnd="2020-01-01", status="pain_coming",
                  aggregationStatus="electric_cooperative")
        results = expired_wrong_status([z])
        self.assertEqual(results, [])


class TestNopecRateMismatch(unittest.TestCase):
    def test_wrong_rate_flagged(self):
        from scripts.data_audit import nopec_rate_mismatch
        # 7.5¢ is not a known NOPEC rate cycle value
        z = _zone(supplier="NOPEC", currentRate=7.5, status="pricing_updated")
        results = nopec_rate_mismatch([z])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["check"], "NOPEC_RATE_MISMATCH")

    def test_correct_rate_passes(self):
        from scripts.data_audit import nopec_rate_mismatch
        z = _zone(supplier="NOPEC", currentRate=9.999)
        results = nopec_rate_mismatch([z])
        self.assertEqual(results, [])

    def test_non_nopec_supplier_ignored(self):
        from scripts.data_audit import nopec_rate_mismatch
        z = _zone(supplier="Constellation", currentRate=7.5)
        results = nopec_rate_mismatch([z])
        self.assertEqual(results, [])


class TestMissingRateChange(unittest.TestCase):
    def test_missing_rate_change_flagged(self):
        from scripts.data_audit import missing_rate_change
        z = _zone(currentRate=9.999, previousRate=8.999, rateChange=None)
        results = missing_rate_change([z])
        self.assertEqual(len(results), 1)
        self.assertIn("11.1", results[0]["detail"])

    def test_populated_rate_change_passes(self):
        from scripts.data_audit import missing_rate_change
        z = _zone(currentRate=9.999, previousRate=8.999, rateChange=11.1)
        results = missing_rate_change([z])
        self.assertEqual(results, [])


class TestBlankSalesCopy(unittest.TestCase):
    def test_blank_takeaway_flagged(self):
        from scripts.data_audit import blank_takeaway_or_hook
        z = _zone(status="pain_hit", takeaway="", hook="Hello...")
        results = blank_takeaway_or_hook([z])
        self.assertEqual(len(results), 1)

    def test_blank_hook_flagged(self):
        from scripts.data_audit import blank_takeaway_or_hook
        z = _zone(status="pricing_updated", takeaway="Rate up 11%.", hook=None)
        results = blank_takeaway_or_hook([z])
        self.assertEqual(len(results), 1)

    def test_stable_exempt(self):
        from scripts.data_audit import blank_takeaway_or_hook
        z = _zone(status="stable", takeaway="", hook="")
        results = blank_takeaway_or_hook([z])
        self.assertEqual(results, [])

    def test_complete_passes(self):
        from scripts.data_audit import blank_takeaway_or_hook
        z = _zone(status="pain_hit", takeaway="Rate hit hard.", hook="Hi, calling about...")
        results = blank_takeaway_or_hook([z])
        self.assertEqual(results, [])


class TestSupplierAggMismatch(unittest.TestCase):
    def test_supplier_set_no_agg_flagged(self):
        from scripts.data_audit import supplier_agg_status_mismatch
        z = _zone(supplier="NOPEC", aggregationStatus="no_aggregation_verified")
        results = supplier_agg_status_mismatch([z])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["check"], "SUPPLIER_AGG_MISMATCH")

    def test_no_supplier_passes(self):
        from scripts.data_audit import supplier_agg_status_mismatch
        z = _zone(supplier=None, aggregationStatus="no_aggregation_verified")
        results = supplier_agg_status_mismatch([z])
        self.assertEqual(results, [])


class TestRateOutOfRange(unittest.TestCase):
    def test_electric_too_low_flagged(self):
        from scripts.data_audit import rate_out_of_range
        z = _zone(currentRate=1.5, commodity="electric")
        results = rate_out_of_range([z])
        self.assertEqual(len(results), 1)

    def test_electric_too_high_flagged(self):
        from scripts.data_audit import rate_out_of_range
        z = _zone(currentRate=25.0, commodity="electric")
        results = rate_out_of_range([z])
        self.assertEqual(len(results), 1)

    def test_electric_normal_passes(self):
        from scripts.data_audit import rate_out_of_range
        z = _zone(currentRate=9.999, commodity="electric")
        results = rate_out_of_range([z])
        self.assertEqual(results, [])

    def test_gas_out_of_range_flagged(self):
        from scripts.data_audit import rate_out_of_range
        z = _zone(currentRate=9.99, commodity="gas",
                  aggregationStatus="confirmed_active_aggregation")
        results = rate_out_of_range([z])
        self.assertEqual(len(results), 1)


class TestDuplicateZoneNames(unittest.TestCase):
    def test_duplicate_flagged(self):
        from scripts.data_audit import duplicate_zone_names
        z1 = _zone(name="Brunswick", _source_file="remaining_ohio_markets")
        z2 = _zone(name="Brunswick", _source_file="akron_summit_medina")
        results = duplicate_zone_names([z1, z2])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["check"], "DUPLICATE_ZONE")

    def test_unique_names_pass(self):
        from scripts.data_audit import duplicate_zone_names
        z1 = _zone(name="Brunswick", _source_file="remaining_ohio_markets")
        z2 = _zone(name="Strongsville", _source_file="nopec_cuyahoga_suburbs")
        results = duplicate_zone_names([z1, z2])
        self.assertEqual(results, [])

    def test_same_name_different_commodity_ok(self):
        from scripts.data_audit import duplicate_zone_names
        z1 = _zone(name="Cleveland", commodity="electric", _source_file="cleveland_cuyahoga")
        z2 = _zone(name="Cleveland", commodity="gas", _source_file="ne_ohio_gas")
        results = duplicate_zone_names([z1, z2])
        self.assertEqual(results, [])


class TestNoGasZone(unittest.TestCase):
    def test_rollover_electric_no_gas_flagged(self):
        from scripts.data_audit import electric_zone_no_gas_counterpart
        z = _zone(name="Parma", status="rollover", commodity="electric",
                  aggregationStatus="confirmed_active_aggregation")
        results = electric_zone_no_gas_counterpart([z])
        self.assertTrue(any(r["check"] == "NO_GAS_ZONE" for r in results))

    def test_rollover_with_gas_counterpart_passes(self):
        from scripts.data_audit import electric_zone_no_gas_counterpart
        ze = _zone(name="Parma", status="rollover", commodity="electric")
        zg = _zone(name="Parma", commodity="gas", status="verify",
                   aggregationStatus="confirmed_active_aggregation")
        results = electric_zone_no_gas_counterpart([ze, zg])
        names = [r["zone"] for r in results if r["check"] == "NO_GAS_ZONE"]
        self.assertNotIn("parma", names)

    def test_stable_electric_not_flagged(self):
        from scripts.data_audit import electric_zone_no_gas_counterpart
        z = _zone(name="SomeStableZone", status="stable", commodity="electric")
        results = electric_zone_no_gas_counterpart([z])
        names = [r["zone"] for r in results if r["check"] == "NO_GAS_ZONE"]
        self.assertNotIn("somestablezone", names)


class TestRunAuditIntegration(unittest.TestCase):
    def test_run_audit_returns_dict(self):
        from scripts.data_audit import run_audit
        result = run_audit(verbose=False)
        self.assertIn("zones_checked", result)
        self.assertIn("findings", result)
        self.assertIn("high", result)
        self.assertIn("report", result)

    def test_run_audit_report_written(self):
        from scripts.data_audit import run_audit
        result = run_audit(verbose=False)
        self.assertTrue(os.path.exists(result["report"]))


if __name__ == "__main__":
    unittest.main()
