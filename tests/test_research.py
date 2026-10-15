"""Data loading, comparable rate changes, and the report-only monitor."""

import hashlib
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import app as forge_app
import history_store
from forge_config import key_is_configured, pipeline_argv
from zone_intel import (
    append_monitor_items,
    comparable_change,
    compare_observation,
    historical_benchmark,
    load_monitor_additions,
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
        ptc_rows = {row["code"]: row for row in load_ptc()["rates"]}
        self.assertEqual(
            {code: row["cents_per_kwh"] for code, row in ptc_rows.items()},
            {"OE": 11.07, "CEI": 11.24, "TE": 11.26, "AEP": 10.19, "DUKE": 10.49, "AES": 10.86},
        )
        cei = ptc_rows["CEI"]
        self.assertEqual(
            cei["source_url"],
            "https://www.energychoice.ohio.gov/ApplesToApplesComparision.aspx?Category=Electric&RateCode=1&TerritoryId=6",
        )
        self.assertEqual(cei["accessed_at"], "2026-10-15")
        self.assertEqual(cei["effective_start"], "2026-10-01")
        self.assertEqual(cei["effective_end"], "2026-12-31")
        self.assertFalse(cei["value_changed"])
        te = ptc_rows["TE"]
        self.assertEqual(
            te["source_url"],
            "https://www.energychoice.ohio.gov/ApplesToApplesComparision.aspx?Category=Electric&RateCode=1&TerritoryId=3",
        )
        self.assertEqual(te["accessed_at"], "2026-10-15")
        self.assertEqual(te["effective_start"], "2026-10-01")
        self.assertEqual(te["effective_end"], "2026-12-31")
        self.assertFalse(te["value_changed"])


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


class HistoryTests(unittest.TestCase):
    def test_refresh_keeps_prior_records(self):
        zone = _zone("Akron")
        region = zone["_source_file"]
        region_path = os.path.join(ROOT, "data", "regions", f"{region}.json")
        with open(region_path, "rb") as handle:
            region_before = handle.read()
        with tempfile.TemporaryDirectory() as tmp:
            queue_path = os.path.join(tmp, "monitor_additions.csv")
            history_dir = os.path.join(tmp, "history")
            report_path = os.path.join(tmp, "refresh_report.json")
            observations = []
            for rate, accessed_at in (("10.50", "2026-10-15T12:00:00"), ("11.10", "2026-10-16T12:00:00")):
                path = os.path.join(tmp, f"obs-{rate}.json")
                with open(path, "w", encoding="utf-8") as handle:
                    json.dump([{
                        "zone": "Akron",
                        "region": region,
                        "rate": rate,
                        "supplier": "Dynegy",
                        "source_url": "https://example.test/akron",
                        "accessed_at": accessed_at,
                    }], handle)
                observations.append(path)
            env = {"FORGE_HISTORY_DIR": history_dir}
            with patch("zone_intel.MONITOR_QUEUE_PATH", queue_path), patch.dict(os.environ, env):
                import run_refresh
                run_refresh.main(["--observations", observations[0], "--report", report_path])
                with open(queue_path, "rb") as handle:
                    queue_after_first = handle.read()
                with open(report_path, "rb") as handle:
                    report_after_first = handle.read()
                journal_path = history_store.journal_path()
                with open(journal_path, "rb") as handle:
                    journal_after_first = handle.read()
                run_refresh.main(["--observations", observations[1], "--report", report_path])
                with open(queue_path, "rb") as handle:
                    queue_after_second = handle.read()
                with open(report_path, "rb") as handle:
                    report_after_second = handle.read()
                with open(journal_path, "rb") as handle:
                    journal_after_second = handle.read()
                rows = load_monitor_additions(queue_path)
                events = history_store.load_events(journal_path)
            self.assertTrue(queue_after_second.startswith(queue_after_first))
            self.assertIn(b"10.50", queue_after_first)
            self.assertIn(b"11.10", queue_after_second)
            self.assertEqual(report_after_first, report_after_second)
            self.assertIn(b"10.50", report_after_first)
            self.assertTrue(os.path.exists(os.path.join(tmp, "refresh_report-1.json")))
            self.assertTrue(journal_after_second.startswith(journal_after_first))
            self.assertEqual(len(rows), 2)
            self.assertIn("10.50", rows[0]["change"])
            self.assertTrue(rows[0]["superseded"])
            self.assertTrue(rows[0]["superseded_at"])
            self.assertIn("11.10", rows[1]["change"])
            self.assertFalse(rows[1].get("superseded"))
            rates = [event for event in events if event["kind"] == "rate"]
            self.assertEqual([event["rate"] for event in rates], ["10.50", "11.10"])
            self.assertTrue(rates[0]["superseded"])
            self.assertTrue(rates[0]["superseded_at"])
            self.assertFalse(rates[1].get("superseded"))
            reports = [event for event in events if event["kind"] == "refresh_report"]
            self.assertEqual(len(reports), 2)
            with open(reports[0]["path"], encoding="utf-8") as handle:
                self.assertIn("10.50", handle.read())
            with open(reports[1]["path"], encoding="utf-8") as handle:
                self.assertIn("11.10", handle.read())
        with open(region_path, "rb") as handle:
            self.assertEqual(handle.read(), region_before)

    def test_zone_edits_append_and_keep_the_region_file(self):
        zone = _zone("Akron")
        region = zone["_source_file"]
        region_path = os.path.join(ROOT, "data", "regions", f"{region}.json")
        with open(region_path, "rb") as handle:
            before = handle.read()
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {"FORGE_HISTORY_DIR": tmp}):
                client = forge_app.app.test_client()
                first = client.put(
                    f"/api/zones/{region}/Akron",
                    json={"name": "Akron", "notes": "history-test"},
                )
                self.assertEqual(first.status_code, 200)
                journal_path = history_store.journal_path()
                with open(journal_path, "rb") as handle:
                    journal_after_first = handle.read()
                second = client.put(
                    f"/api/zones/{region}/Akron",
                    json={"name": "Akron", "notes": "second-note"},
                )
                self.assertEqual(second.status_code, 200)
                removed = client.delete(f"/api/zones/{region}/Akron")
                self.assertEqual(removed.status_code, 200)
                self.assertTrue(removed.get_json()["superseded"])
                loaded = [
                    item for item in forge_app._load_zones()
                    if item.get("_history_key") == "Akron" and item.get("_source_file") == region
                ]
                self.assertEqual(len(loaded), 1)
                self.assertEqual(len(forge_app._load_zones()), 327)
                self.assertTrue(loaded[0]["superseded"])
                self.assertTrue(loaded[0]["superseded_at"])
                self.assertEqual(loaded[0]["notes"], "second-note")
                kept_notes = [entry["values"].get("notes") for entry in loaded[0]["history"]]
                self.assertIn("history-test", kept_notes)
                self.assertTrue(all(entry.get("superseded_at") for entry in loaded[0]["history"]))
                with open(journal_path, "rb") as handle:
                    journal_after = handle.read()
                self.assertTrue(journal_after.startswith(journal_after_first))
                self.assertIn(b"history-test", journal_after_first)
                events = history_store.load_events(journal_path)
                self.assertEqual(len(events), 3)
                self.assertTrue(events[0]["superseded"])
                self.assertTrue(events[0]["superseded_at"])
                self.assertTrue(events[1]["superseded"])
        with open(region_path, "rb") as handle:
            self.assertEqual(handle.read(), before)

    def test_prune_refuses_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {"FORGE_HISTORY_DIR": tmp}):
                history_store.append_event("note", {"text": "keep"})
                path = history_store.journal_path()
                with self.assertRaises(RuntimeError):
                    history_store.guard_against_prune(path)
                with open(path, encoding="utf-8") as handle:
                    self.assertIn("keep", handle.read())


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
        self.assertIn("TerritoryId=6", ptc)
        self.assertIn("TerritoryId=3", ptc)
        self.assertIn("2026-10-01", ptc)
        self.assertIn("2026-10-15", ptc)
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

    def test_battlecard_shows_residential_ptc_gap(self):
        streetsboro = _zone("Streetsboro")
        ptc = streetsboro["card"]["ptc"]
        self.assertTrue(ptc["applicable"])
        self.assertEqual(ptc["customer_class"], "residential")
        self.assertEqual(ptc["code"], "OE")
        self.assertEqual(ptc["cents_per_kwh"], 11.07)
        self.assertEqual(ptc["effective_start"], "2026-10-01")
        self.assertEqual(ptc["effective_end"], "2026-12-31")
        self.assertIn("TerritoryId=7", ptc["source_url"])
        stored = {row["code"]: row for row in load_ptc()["rates"]}
        self.assertIn("apples-to-apples page cited for 11.07", stored["OE"]["previous_source"])
        self.assertFalse(stored["OE"]["value_changed"])
        self.assertFalse(stored["DUKE"]["value_changed"])
        self.assertFalse(stored["AES"]["value_changed"])
        self.assertEqual(ptc["comparison"]["customer_class"], "residential")
        self.assertEqual(ptc["comparison"]["cents"], -1.071)
        self.assertEqual(ptc["comparison"]["percent"], -9.7)

        sharonville = _zone("Sharonville")
        duke = sharonville["card"]["ptc"]
        self.assertEqual(duke["code"], "DUKE")
        self.assertEqual(duke["effective_end"], "2026-10-31")
        self.assertEqual(duke["comparison"]["cents"], -1.1)
        self.assertEqual(duke["comparison"]["percent"], -10.5)

        centerville = _zone("Centerville")
        aes = centerville["card"]["ptc"]
        self.assertEqual(aes["code"], "AES")
        self.assertEqual(aes["effective_start"], "2026-06-01")
        self.assertEqual(aes["effective_end"], "2027-05-31")
        self.assertEqual(aes["comparison"]["cents"], -1.811)
        self.assertEqual(aes["comparison"]["percent"], -16.7)

        for name in ("Wauseon", "Amherst"):
            blocked = _zone(name)["card"]["ptc"]
            self.assertFalse(blocked["applicable"])
            self.assertEqual(blocked["label"], "PTC not applicable")
            self.assertIsNone(blocked["comparison"])
        coop = next(
            zone for zone in forge_app._load_zones()
            if zone.get("aggregationStatus") == "electric_cooperative" and zone.get("card")
        )
        self.assertEqual(coop["card"]["ptc"]["label"], "PTC not applicable")

        card = self.client.get("/card?file=nopec_lorain_summit_portage&name=Streetsboro").get_data(as_text=True)
        self.assertIn("Residential Price to Compare", card)
        self.assertIn("11.07", card)
        self.assertIn("2026-10-01", card)
        self.assertIn("2026-12-31", card)
        self.assertIn("TerritoryId=7", card)
        self.assertIn("Aggregation current vs this residential PTC: -1.071¢ (-9.7%)", card)
        self.assertNotIn('class="no-print">Residential', card)
        duke_page = self.client.get("/card?file=cincinnati_duke&name=Sharonville").get_data(as_text=True)
        self.assertIn("2026-10-31", duke_page)
        self.assertIn("-1.100¢ (-10.5%)", duke_page)
        municipal = self.client.get("/card?file=ohio_municipal_utilities&name=Wauseon").get_data(as_text=True)
        self.assertIn("PTC not applicable", municipal)
        self.assertNotIn("Aggregation current vs this residential PTC", municipal)
        hotspots = self.client.get("/hotspots").get_data(as_text=True)
        self.assertIn('id="bc-ptc"', hotspots)
        self.assertIn("Aggregation current vs this residential PTC", hotspots)
        reference = self.client.get("/ptc").get_data(as_text=True)
        self.assertIn("Earlier source note kept", reference)
        self.assertIn("2026-10-31", reference)
        self.assertIn("2027-05-31", reference)

    def test_queue_page_marks_superseded_additions(self):
        item = {
            "added_on": "2026-10-15",
            "zone": "Akron",
            "region": "akron_summit_medina",
            "change": "observed rate 10.50 differs from stored 9.999",
            "exact_next_action": "Review this diff.",
            "superseded": True,
            "superseded_at": "2026-10-16T00:00:00+00:00",
        }
        with patch("app.zone_intel.load_monitor_additions", return_value=[item]):
            page = self.client.get("/queue").get_data(as_text=True)
        self.assertIn("Superseded 2026-10-16T00:00:00+00:00", page)
        self.assertIn("observed rate 10.50", page)


if __name__ == "__main__":
    unittest.main()
