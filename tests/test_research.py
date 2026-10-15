"""Data loading, comparable rate changes, and the report-only monitor."""

import hashlib
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import app as forge_app
from forge_config import key_is_configured, pipeline_argv
from zone_intel import (
    append_monitor_items,
    comparable_change,
    compare_observation,
    historical_benchmark,
    load_ptc,
    load_queue,
    load_rate_ledger,
)


def _zone(name):
    zones = forge_app._load_zones()
    matches = [zone for zone in zones if zone["name"] == name]
    if len(matches) != 1:
        raise AssertionError(f"{name}: {len(matches)} matches")
    return matches[0]


class DataLoadTests(unittest.TestCase):
    def test_all_zones_keep_forge_fields_and_gain_research(self):
        zones = forge_app._load_zones()
        self.assertEqual(len(zones), 327)
        self.assertTrue(all(zone.get("research") and zone.get("original") for zone in zones))
        streetsboro = _zone("Streetsboro")
        self.assertEqual(streetsboro["supplier"], "NOPEC")
        self.assertEqual(streetsboro["currentRate"], 9.999)
        self.assertEqual(streetsboro["status"], "pricing_updated")
        self.assertEqual(streetsboro["original"]["supplier"], "NOPEC")
        research = streetsboro["research"]
        self.assertEqual(research["supplier"], "Dynegy")
        self.assertEqual(research["current"]["rate_raw"], "9.999")
        self.assertTrue(research["current"]["sourced"])
        correction = research["corrections"][0]
        self.assertEqual(correction["type"], "program_or_supplier_correction")
        self.assertEqual(correction["date"], "2026-10-14")
        self.assertIn("NOPEC", correction["oldValue"])
        self.assertIn("Dynegy", correction["newValue"])
        self.assertTrue(correction["sourceUrls"])
        self.assertTrue(correction["reason"])

    def test_region_files_are_not_rewritten_by_loading(self):
        path = os.path.join(ROOT, "data", "regions", "nopec_lorain_summit_portage.json")
        with open(path, "rb") as handle:
            before = hashlib.sha256(handle.read()).hexdigest()
        forge_app._load_zones()
        with open(path, "rb") as handle:
            after = hashlib.sha256(handle.read()).hexdigest()
        self.assertEqual(before, after)

    def test_needs_call_and_conflict_stay_unresolved(self):
        wauseon = _zone("Wauseon")
        self.assertEqual(wauseon["aggregationStatus"], "municipal_utility")
        self.assertEqual(wauseon["status"], "stable")
        self.assertTrue(wauseon["research"]["status"]["unresolved"])
        self.assertEqual(wauseon["research"]["status"]["verificationLabel"], "conflict")
        self.assertFalse(wauseon["research"]["notEligible"])
        self.assertFalse(wauseon["card"]["hookAllowed"])
        medina = _zone("Medina County")
        self.assertEqual(medina["research"]["status"]["verification"], "escalate-call")
        self.assertEqual(medina["research"]["status"]["verificationLabel"], "needs call")
        self.assertEqual(medina["aggregationStatus"], "confirmed_active_aggregation")
        weekly = forge_app._compute_weekly(forge_app._load_zones())
        avoid_names = {zone["name"] for zone in weekly["avoid_list"]}
        unresolved_names = {zone["name"] for zone in weekly["unresolved_list"]}
        self.assertIn("Wauseon", unresolved_names)
        self.assertNotIn("Wauseon", avoid_names)
        self.assertIn("Medina County", unresolved_names)


class RateChangeTests(unittest.TestCase):
    def test_comparable_only_when_sourced_and_same_basis(self):
        sourced = comparable_change(
            "9.049", "https://www.centervilleohio.gov/312/Electric-Aggregation", "aggregation program",
            "6.57", "https://www.mvcc.net/services/electric-supply-aggregation-program/", "aggregation program",
        )
        self.assertTrue(sourced["comparable"])
        self.assertEqual(sourced["cents"], 2.479)
        self.assertEqual(sourced["percent"], 37.7)

        unsourced = comparable_change(
            "9.999", "https://www.dynegy.com/municipal-aggregation/communities-we-serve/ohio/Streetsboro",
            "aggregation program",
            "7.0", "FORGE repo (app value)", "aggregation program",
        )
        self.assertFalse(unsourced["comparable"])
        self.assertEqual(unsourced["reason"], "unsourced")
        self.assertIsNone(unsourced["cents"])

        mixed = comparable_change(
            "10.49", "https://www.energychoice.ohio.gov/ApplesToApplesComparision.aspx?Category=Electric&RateCode=1&TerritoryId=4",
            "utility Price to Compare (default service, no aggregation found)",
            "9.39", "https://www.dynegy.com/municipal-aggregation/communities-we-serve/ohio/Sharonville",
            "aggregation program",
        )
        self.assertFalse(mixed["comparable"])
        self.assertEqual(mixed["reason"], "different_basis")

        missing = comparable_change("", "https://example.com/a", "aggregation program", "6.57", "https://example.com/b", "aggregation program")
        self.assertEqual(missing["reason"], "missing_rate")

    def test_historical_benchmark_skips_the_current_capture(self):
        text = (
            "7.69 (APR 2025 - MAY 2026, Wayback 20250514) ; "
            "9.95 (MAY 2026 - JUN 2028, Wayback 20260413)"
        )
        bench = historical_benchmark(text, "9.95")
        self.assertEqual(bench["rate"], 7.69)
        self.assertEqual(bench["capture"], "2025-05-14")
        euclid = _zone("Euclid")
        change = euclid["research"]["changeVsHistorical"]
        self.assertTrue(change["comparable"])
        self.assertEqual(change["cents"], 2.26)
        self.assertEqual(change["percent"], 29.4)
        newark = _zone("Heath / Newark")
        hist = newark["research"]["changeVsHistorical"]
        self.assertTrue(hist["comparable"])
        self.assertEqual(hist["cents"], 4.05)
        streetsboro = _zone("Streetsboro")
        self.assertFalse(streetsboro["research"]["changeVsPrior"]["comparable"])

    def test_ledger_keeps_roles_and_separate_dates(self):
        periods = load_rate_ledger()
        roles = {row["role"] for row in periods}
        self.assertTrue({"current", "prior", "historical", "future", "forge_recorded"} <= roles)
        current = [
            row for row in periods
            if row["origin"] == "corrected_dataset" and row["zone"] == "Streetsboro" and row["role"] == "current"
        ]
        self.assertEqual(len(current), 1)
        row = current[0]
        self.assertEqual(row["rate_raw"], "9.999")
        self.assertEqual(row["supplier"], "Dynegy")
        self.assertEqual(row["administrator"], "Dynegy")
        self.assertEqual(row["utility"], "Ohio Edison")
        self.assertEqual(row["accessed_at"], "2026-10-14")
        self.assertEqual(row["effective_start"], "2026-06")
        self.assertEqual(row["effective_end"], "2027-12")
        self.assertTrue(row["source_url"].startswith("https://"))
        prior = [
            row for row in periods
            if row["origin"] == "corrected_dataset" and row["zone"] == "Centerville" and row["role"] == "prior"
        ]
        self.assertEqual(prior[0]["rate_raw"], "6.57")
        self.assertTrue(prior[0]["sourced"])
        self.assertEqual(len(load_queue()), 327)
        ptc = {row["code"]: row["cents_per_kwh"] for row in load_ptc()["rates"]}
        self.assertEqual(ptc, {"OE": 11.07, "CEI": 11.24, "TE": 11.26, "AEP": 10.19, "DUKE": 10.49, "AES": 10.86})


class MonitorTests(unittest.TestCase):
    def test_diff_is_queued_and_zone_is_not_overwritten(self):
        zone = _zone("Akron")
        stored = zone["research"]["current"]["rate_raw"]
        item = compare_observation(zone, {
            "rate": "10.50",
            "supplier": "Dynegy",
            "source_url": "https://www.dynegy.com/municipal-aggregation/communities-we-serve/ohio/Akron",
            "accessed_at": "2026-10-15",
        })
        self.assertIsNotNone(item)
        self.assertIn("10.50", item["change"])
        self.assertEqual(zone["research"]["current"]["rate_raw"], stored)
        same = compare_observation(zone, {"rate": stored, "supplier": "Dynegy", "accessed_at": "2026-10-15"})
        self.assertIsNone(same)
        missing = compare_observation(zone, {"rate_missing": True, "accessed_at": "2026-10-15", "source_url": "https://example.test/akron"})
        self.assertIn("not found", missing["change"])
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "monitor_additions.csv")
            added = append_monitor_items([item], path)
            again = append_monitor_items([item], path)
            self.assertEqual(len(added), 1)
            self.assertEqual(again, [])
            self.assertTrue(os.path.exists(path))
        self.assertEqual(_zone("Akron")["research"]["current"]["rate_raw"], stored)


class AppBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.client = forge_app.app.test_client()

    def test_placeholder_keys_are_unset(self):
        self.assertFalse(key_is_configured("your-anthropic-api-key-here"))
        self.assertFalse(key_is_configured("your-google-maps-api-key-here"))
        self.assertFalse(key_is_configured("  "))
        self.assertFalse(key_is_configured(None))
        self.assertTrue(key_is_configured("sk-ant-real-key-value"))
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "your-anthropic-api-key-here", "GOOGLE_MAPS_API_KEY": "your-google-maps-api-key-here"}):
            page = self.client.get("/settings").get_data(as_text=True)
        self.assertEqual(page.count("Dormant"), 2)
        self.assertNotIn(">Active<", page.split("Rule-Based Qualifier")[0])

    def test_run_uses_this_interpreter(self):
        self.assertEqual(pipeline_argv()[0], sys.executable)
        self.assertTrue(pipeline_argv()[1].endswith("run_pipeline.py"))
        with patch("app.subprocess.Popen") as popen:
            response = self.client.get("/run", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        argv = popen.call_args.args[0]
        self.assertEqual(argv[0], sys.executable)
        self.assertNotEqual(argv[0], "python")

    def test_views_render_research(self):
        intel = self.client.get("/intel").get_data(as_text=True)
        self.assertIn("NOPEC", intel)
        self.assertIn("10.399", intel)
        ptc = self.client.get("/ptc").get_data(as_text=True)
        for rate in ("11.07", "11.24", "11.26", "10.19", "10.49", "10.86"):
            self.assertIn(rate, ptc)
        card = self.client.get("/card?file=nopec_lorain_summit_portage&name=Streetsboro").get_data(as_text=True)
        self.assertIn("Current", card)
        self.assertIn("Prior", card)
        self.assertIn("Historical", card)
        self.assertIn("9.999", card)
        self.assertIn("Dynegy", card)
        self.assertNotIn("Route 303", card)
        wauseon = self.client.get("/card?file=ohio_municipal_utilities&name=Wauseon").get_data(as_text=True)
        self.assertIn("Unresolved", wauseon)
        self.assertIn("not marked inactive", wauseon)
        self.assertIn("Verify before using", wauseon)
        queue = self.client.get("/queue?verification=conflict").get_data(as_text=True)
        self.assertIn("Wauseon", queue)
        self.assertIn("unresolved", queue)
        expiring = self.client.get("/expiring").get_data(as_text=True)
        self.assertIn("Heath / Newark", expiring)
        zip_page = self.client.get("/counties?zip=44241&county=Portage").get_data(as_text=True)
        self.assertIn("not proof", zip_page)
        self.assertIn("Streetsboro", zip_page)
        self.assertIn("Portage", zip_page)
        ambiguous = self.client.get("/api/zip/45066")
        body = ambiguous.get_json()
        self.assertEqual(body["match_count"], 2)
        self.assertIsNone(body["zone"])
        self.assertIn("not proof", body["disclaimer"])
        self.assertEqual(self.client.get("/hotspots").status_code, 200)
        weekly = self.client.get("/weekly").get_data(as_text=True)
        self.assertIn("Streetsboro — Dynegy at 9.999", weekly)
        self.assertNotIn("still on the NOPEC program", weekly)


if __name__ == "__main__":
    unittest.main()
