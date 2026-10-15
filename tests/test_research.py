"""Data loading, comparable rate changes, and the report-only monitor."""

import csv
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
from place_index import classify_lookup, load_places
import territory
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

    def test_archbold_is_toledo_edison_and_not_blacklisted(self):
        zone = _zone("Archbold")
        self.assertEqual(zone["utility"], "Toledo Edison")
        self.assertEqual(zone["utilityParent"], "FirstEnergy")
        self.assertEqual(zone["aggregationStatus"], "unresolved")
        self.assertEqual(zone["futureUse"], "price_to_compare_analysis")
        self.assertEqual(zone["status"], "verify")
        self.assertIsNone(zone["supplier"])
        self.assertIsNone(zone["currentRate"])
        self.assertEqual(
            zone["notes"],
            "Removed from the municipal list 2026-10-15: not a municipal utility; Toledo Edison (FirstEnergy) serves Archbold; not on the AMP list.",
        )
        self.assertNotIn("municipal_blacklist", zone["futureUse"])
        research = zone["research"]
        self.assertEqual(research["utility"], "Toledo Edison")
        self.assertEqual(research["supplier"], "")
        self.assertTrue(research["status"]["unresolved"])
        self.assertFalse(research["notEligible"])
        self.assertFalse(research["hookAllowed"])
        card = zone["card"]
        self.assertTrue(card["ptc"]["applicable"])
        self.assertEqual(card["ptc"]["cents_per_kwh"], 11.26)
        self.assertEqual(card["ptc"]["utility"], "Toledo Edison")
        self.assertIn("2026-10-01", card["ptc"]["effective_start"])
        self.assertIn("2026-12-31", card["ptc"]["effective_end"])
        self.assertFalse(card["currentSourced"])
        self.assertEqual(card["supplier"], "")
        self.assertNotIn("Cannot sell", card["takeaway"])
        weekly = forge_app._compute_weekly(forge_app._load_zones())
        avoid_names = {item["name"] for item in weekly["avoid_list"]}
        unresolved_names = {item["name"] for item in weekly["unresolved_list"]}
        self.assertNotIn("Archbold", avoid_names)
        self.assertIn("Archbold", unresolved_names)
        with open(os.path.join(ROOT, "data", "research", "forge_corrected_dataset.csv"), newline="", encoding="utf-8") as handle:
            original = next(row for row in csv.DictReader(handle) if row["orig_name"] == "Archbold")
        self.assertEqual(original["orig_aggregationStatus"], "municipal_utility")
        self.assertEqual(original["orig_utility"], "Archbold Municipal Electric")
        self.assertIn("Ample, reliable electric power is provided to the Archbold area by Toledo Edison", original["CORR_evidence_quotes"])


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
        self.assertEqual(len(load_queue()), 328)
        westlake_queue = [row for row in load_queue() if row["zone"] == "Westlake"]
        self.assertEqual(len(westlake_queue), 2)
        self.assertTrue(westlake_queue[0]["superseded"])
        self.assertIn("Update FORGE supplier field", westlake_queue[0]["exact_next_action"])
        self.assertEqual(westlake_queue[1]["utility"], "The Illuminating Company")
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

    def test_westlake_correction_keeps_unsourced_forge_history(self):
        region_path = os.path.join(ROOT, "data", "regions", "nopec_cuyahoga_suburbs.json")
        with open(region_path, "rb") as handle:
            region_bytes = handle.read()
        westlake = _zone("Westlake")
        self.assertEqual(westlake["utility"], "Ohio Edison")
        self.assertEqual(westlake["supplier"], "NOPEC")
        self.assertEqual(westlake["currentRate"], 9.999)
        self.assertIn("on NOPEC", westlake["original"]["hook"])
        self.assertEqual(westlake["research"]["utility"], "The Illuminating Company")
        self.assertEqual(westlake["research"]["administrator"], "City of Westlake (consultant Brenda Fargo)")
        self.assertIn("Dynegy", westlake["research"]["supplier"])
        self.assertEqual(westlake["research"]["current"]["rate_raw"], "11.24")
        self.assertIn("TerritoryId=6", westlake["research"]["current"]["source"])
        self.assertEqual(westlake["research"]["prior"]["rate_raw"], "8.38")
        self.assertEqual(westlake["research"]["prior"]["term"], "2025-02 to 2026-06")
        self.assertEqual(westlake["research"]["historical"]["rate_raw"], "4.77")
        self.assertTrue(westlake["research"]["supersededResearch"]["superseded"])
        self.assertEqual(westlake["research"]["supersededResearch"]["utility"], "Ohio Edison")
        self.assertTrue(westlake["research"]["supersededResearch"]["superseded_at"])
        card = westlake["card"]
        self.assertEqual(
            card["hook"],
            "Westlake has no aggregation, residents default to CEI PTC 11.24 c (Oct 1 to Dec 31 2026).",
        )
        self.assertNotIn("NOPEC", card["hook"])
        self.assertTrue(card["noGasAggregation"])
        self.assertEqual(card["rejectedRenewal"]["rate"], "10.11")
        self.assertEqual([item["rate"] for item in card["unsourcedForgeRates"]], ["9.999", "7.0", "8.999"])
        self.assertIsNone(card["ptc"]["comparison"])
        self.assertEqual(card["ptc"]["cents_per_kwh"], 11.24)
        page = self.client.get("/card?file=nopec_cuyahoga_suburbs&name=Westlake").get_data(as_text=True)
        self.assertIn("Westlake has no aggregation, residents default to CEI PTC 11.24 c (Oct 1 to Dec 31 2026).", page)
        self.assertIn("FORGE recorded history, unsourced", page)
        self.assertIn("No gas aggregation.", page)
        self.assertIn("10.11", page)
        self.assertIn("8.38", page)
        self.assertIn("4.77", page)
        self.assertIn("superseded", page)
        weekly = self.client.get("/weekly").get_data(as_text=True)
        self.assertIn("Westlake has no aggregation, residents default to CEI PTC 11.24 c", weekly)
        self.assertNotIn("Westlake is on NOPEC", weekly)
        with open(region_path, "rb") as handle:
            self.assertEqual(handle.read(), region_bytes)
        with open(os.path.join(ROOT, "data", "research", "forge_corrected_dataset.csv"), newline="") as handle:
            stored = [row for row in csv.DictReader(handle) if row["orig_name"] == "Westlake"]
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["norm_utility"], "Ohio Edison")
        self.assertEqual(stored[0]["PRIOR_rate"], "7.0")
        self.assertIn("FORGE repo", stored[0]["PRIOR_source"])

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


class LookupFieldTests(unittest.TestCase):
    def setUp(self):
        self.client = forge_app.app.test_client()

    def test_lookup_field_is_plain_search_and_rejects_secrets(self):
        self.assertEqual(classify_lookup("44241"), ("zip", "44241"))
        self.assertEqual(classify_lookup("Addyston"), ("place", "Addyston"))
        self.assertIsNone(classify_lookup("p@ssw0rd!"))
        self.assertIsNone(classify_lookup("<script>alert(1)</script>"))
        self.assertIsNone(classify_lookup("1234"))

        counties = self.client.get("/counties").get_data(as_text=True)
        self.assertIn('role="search"', counties)
        self.assertIn('method="post"', counties)
        self.assertIn('type="search"', counties)
        self.assertIn('autocomplete="off"', counties)
        self.assertIn('name="q"', counties)
        self.assertNotIn('type="password"', counties)
        self.assertNotIn('name="zip"', counties)
        self.assertNotIn('name="password"', counties)
        self.assertNotIn("ANTHROPIC_API_KEY", counties)
        self.assertNotIn("GOOGLE_MAPS_API_KEY", counties)

        hotspots = self.client.get("/hotspots").get_data(as_text=True)
        self.assertIn('id="zip-input"', hotspots)
        self.assertIn('type="text"', hotspots)
        self.assertIn('inputmode="numeric"', hotspots)
        self.assertIn('autocomplete="off"', hotspots)
        self.assertIn('name="forge-zip-lookup"', hotspots)
        self.assertIn("-webkit-text-security: none", hotspots)
        self.assertIn("'/api/lookup'", hotspots)
        self.assertNotIn("type=\"password\"", hotspots)
        self.assertNotIn("showZipToast", hotspots)
        self.assertNotIn("/api/zip/${", hotspots)

        rejected = self.client.post("/counties", data={"q": "<script>alert(1)</script>"})
        page = rejected.get_data(as_text=True)
        self.assertNotIn("<script>alert", page)
        self.assertNotIn("alert(1)", page)
        self.assertIn("Enter a 5-digit ZIP or a place name.", page)
        self.assertIn('id="place-lookup" type="search" name="q" value=""', page)

        secret = self.client.post("/api/lookup", json={"q": "p@ssw0rd!"})
        self.assertEqual(secret.status_code, 400)
        encoded = json.dumps(secret.get_json())
        self.assertNotIn("p@ssw0rd", encoded)
        self.assertNotIn("API_KEY", encoded)

        zip_lookup = self.client.post("/api/lookup", json={"q": "44241"})
        self.assertEqual(zip_lookup.status_code, 200)
        body = zip_lookup.get_json()
        self.assertEqual(body["zip"], "44241")
        self.assertEqual(body["zone"], {"name": "Streetsboro"})
        self.assertNotIn("hook", body["zone"])
        self.assertTrue(any(item["name"] == "Streetsboro" for item in body["places"]))

        place = self.client.post("/counties", data={"q": "Addyston"})
        html = place.get_data(as_text=True)
        self.assertIn("Addyston", html)
        self.assertIn("village", html)
        self.assertNotIn("type=\"password\"", html)

        poisoned = self.client.get("/api/zip/%3Cscript%3E")
        self.assertEqual(poisoned.status_code, 400)
        self.assertNotIn("script", json.dumps(poisoned.get_json()))


def _coord_keys(value):
    found = []
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in {"lat", "lon", "latitude", "longitude"} or "coord" in str(key).lower():
                found.append(str(key))
            found.extend(_coord_keys(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(_coord_keys(item))
    return found


class NearbyMapTests(unittest.TestCase):
    def setUp(self):
        self.client = forge_app.app.test_client()

    def test_place_index_has_gazetteer_coordinates(self):
        places = load_places()
        missing = [place["name"] for place in places if place.get("lat") is None or place.get("lon") is None]
        self.assertEqual(missing, [])
        solon = next(place for place in places if place["name"] == "Solon" and place["type"] == "city")
        self.assertGreater(solon["lat"], 41)
        self.assertLess(solon["lat"], 42)
        self.assertGreater(solon["lon"], -82)
        self.assertLess(solon["lon"], -81)

    def test_solon_and_reminderville_list_nearby_places_and_zones(self):
        solon = self.client.post("/api/lookup", json={"q": "Solon"})
        self.assertEqual(solon.status_code, 200)
        place = solon.get_json()["places"][0]
        self.assertEqual(place["name"], "Solon")
        self.assertEqual(place["coverage"]["status"], "own")
        nearby = place["nearby"]
        self.assertEqual(nearby["origin"]["category"], "nopec")
        self.assertEqual(nearby["origin"]["rate"], "10.399")
        self.assertIn("11.24", nearby["origin"]["ptc"])
        names = {item["name"] for item in nearby["places"]}
        self.assertIn("Reminderville", names)
        self.assertIn("Twinsburg", names)
        reminderville = next(item for item in nearby["places"] if item["name"] == "Reminderville")
        self.assertEqual(reminderville["category"], "none")
        self.assertEqual(reminderville["status"], "No own program")
        self.assertNotIn("NOPEC", reminderville["status"])
        self.assertNotIn("NOPEC", reminderville["detail"])
        self.assertGreater(reminderville["miles"], 0)
        zones = {item["name"]: item for item in nearby["zones"]}
        self.assertIn("Twinsburg", zones)
        self.assertTrue(zones["Twinsburg"]["card_url"].startswith("/card?"))
        self.assertEqual(zones["Twinsburg"]["rate"], "10.399")
        self.assertIn("NOPEC", zones["Twinsburg"]["supplier"])
        self.assertTrue(zones["Twinsburg"]["ptc"])
        self.assertNotIn("lat", nearby["origin"])

        reminder = self.client.post("/api/lookup", json={"q": "Reminderville"})
        body = reminder.get_json()["places"][0]
        self.assertEqual(body["coverage"]["status"], "not_covered")
        self.assertNotIn("NOPEC", body["coverage"]["label"])
        self.assertEqual(body["nearby"]["origin"]["category"], "none")
        self.assertNotIn("NOPEC", body["nearby"]["origin"]["detail"])
        zone_names = {item["name"] for item in body["nearby"]["zones"]}
        self.assertIn("Solon", zone_names)
        self.assertIn("Twinsburg", zone_names)
        self.assertIn("Aurora", zone_names)

        page = self.client.post("/counties", data={"q": "Solon"}).get_data(as_text=True)
        self.assertIn("Near Solon", page)
        self.assertIn("Reminderville", page)
        self.assertIn("No own program", page)
        self.assertIn("Twinsburg", page)
        self.assertIn("/card?", page)
        self.assertIn('id="locate-me"', page)
        self.assertIn('type="button"', page)
        self.assertNotIn('type="password"', page)

        card = self.client.get("/card?file=cleveland_cuyahoga&name=Solon").get_data(as_text=True)
        self.assertIn("Nearby", card)
        self.assertIn("Reminderville", card)

    def test_locate_uses_boundaries_and_does_not_echo_coordinates(self):
        denied = self.client.get("/api/locate?lat=41.386&lon=-81.441")
        self.assertEqual(denied.status_code, 405)
        self.assertNotIn("41.386", denied.get_data(as_text=True))

        found = self.client.post("/api/locate", json={"lat": 41.386, "lon": -81.441})
        self.assertEqual(found.status_code, 200)
        self.assertEqual(found.headers.get("Cache-Control"), "no-store")
        text = found.get_data(as_text=True)
        self.assertNotIn("41.386", text)
        self.assertNotIn("-81.441", text)
        body = found.get_json()
        self.assertEqual(_coord_keys(body), [])
        self.assertTrue(body["inside_ohio"])
        self.assertEqual(body["county"], "Cuyahoga")
        self.assertEqual(body["township"], "Solon")
        self.assertEqual(body["nearest_place"]["name"], "Solon")
        self.assertIn("not a municipal boundary", body["nearest_place"]["detail"])
        self.assertTrue(body["nearby_zones"])
        self.assertTrue(body["nearby_zones"][0]["card_url"].startswith("/card?"))

        outside = self.client.post("/api/locate", json={"lat": 40.7, "lon": -74.0})
        self.assertTrue(outside.get_json()["ok"])
        self.assertFalse(outside.get_json()["inside_ohio"])
        self.assertNotIn("40.7", outside.get_data(as_text=True))
        self.assertNotIn("-74.0", outside.get_data(as_text=True))

        rejected = self.client.post("/api/locate", json={"lat": "41.386; drop", "lon": -81.44})
        self.assertEqual(rejected.status_code, 400)
        self.assertNotIn("drop", rejected.get_data(as_text=True))
        self.assertNotIn("41.386", rejected.get_data(as_text=True))

    def test_map_colors_do_not_confirm_unresolved_or_uncovered_places(self):
        payload = self.client.get("/api/map").get_json()
        self.assertTrue(payload["ok"])
        self.assertIn("not shown as confirmed coverage", payload["note"])
        solon = next(zone for zone in payload["zones"] if zone["name"] == "Solon")
        self.assertEqual(solon["category"], "nopec")
        self.assertEqual(solon["verification"], "likely")
        self.assertEqual(solon["rate"], "10.399")
        self.assertIn("11.24", solon["ptc"])
        wauseon = next(zone for zone in payload["zones"] if zone["name"] == "Wauseon")
        self.assertEqual(wauseon["category"], "unresolved")
        self.assertTrue(wauseon["unresolved"])
        self.assertNotEqual(wauseon["category"], "nopec")
        reminder = next(place for place in payload["places"] if place["name"] == "Reminderville")
        self.assertEqual(reminder["category"], "none")
        self.assertFalse(reminder["hollow"])
        self.assertNotIn("NOPEC", reminder["detail"])
        self.assertNotIn("NOPEC", reminder["coverage_label"])
        self.assertGreater(payload["counts"]["zones_drawn"], 250)
        self.assertGreater(payload["counts"]["zones_unplaced"], 0)

        page = self.client.get("/map").get_data(as_text=True)
        self.assertIn("Unresolved / needs call", page)
        self.assertIn("Locate me", page)
        self.assertIn("OpenStreetMap", page)
        self.assertIn("County boundaries", page)
        self.assertIn("does not assert aggregation coverage", page)
        self.assertNotIn('type="password"', page)
        self.assertIn('id="filter-county"', page)
        self.assertIn('id="filter-expiring"', page)

        counties = self.client.get("/api/geo/ohio_counties.geojson")
        self.assertEqual(counties.status_code, 200)
        county_body = counties.get_json()
        counties.close()
        self.assertEqual(county_body["type"], "FeatureCollection")
        self.assertGreaterEqual(len(county_body["features"]), 88)
        self.assertIsNone(territory.safe_geo_file("../.env"))
        self.assertIsNone(territory.safe_geo_file("overlays/../../app.py"))
        missing = self.client.get("/api/geo/overlays/not-a-real-file.geojson")
        self.assertEqual(missing.status_code, 404)
        blocked = self.client.get("/api/geo/../app.py")
        self.assertEqual(blocked.status_code, 404)

        nearby = self.client.post("/api/nearby", json={"zone": "Solon", "region": "cleveland_cuyahoga"})
        self.assertEqual(nearby.status_code, 200)
        self.assertIn("Reminderville", {item["name"] for item in nearby.get_json()["nearby"]["places"]})
        self.assertEqual(_coord_keys(nearby.get_json()), [])


class PucoOverlayTests(unittest.TestCase):
    def setUp(self):
        self.client = forge_app.app.test_client()

    def test_crosswalk_flags_do_not_change_zones(self):
        import puco_layer

        region_path = os.path.join(ROOT, "data", "regions", "eastern_ohio_aep.json")
        with open(region_path, "rb") as handle:
            before = handle.read()
        payload = puco_layer.load_queue_flags()
        counts = payload["counts"]
        self.assertEqual(counts["active_missing"], 13)
        self.assertEqual(counts["nopec_admin"], 12)
        self.assertEqual(counts["prospects"], 744)
        self.assertEqual(counts["app_nopec_not_on_map"], 1)
        self.assertEqual(len(load_queue()), 328)
        self.assertEqual(payload["disclaimer"], puco_layer.DISCLAIMER)
        self.assertEqual(payload["attribution"], "Source: PUCO Government Aggregation map")
        active = [item["name"] for item in payload["flags"] if "active_missing" in item["groups"]]
        self.assertIn("Kenwood / Symmes Township", active)
        self.assertIn("Chillicothe", active)
        self.assertEqual(len(active), 13)
        nopec = [item for item in payload["flags"] if "nopec_admin" in item["groups"]]
        self.assertEqual(len(nopec), 12)
        self.assertTrue(all(item["action"].startswith("Flag only. Zone records were not changed.") for item in nopec))
        self.assertIn(puco_layer.DISCLAIMER, nopec[0]["action"])
        prospects = [item for item in payload["flags"] if item["kind"] == "prospect"]
        self.assertEqual(len(prospects), 744)
        self.assertEqual(prospects[0]["flag_label"], "possible prospects to research")
        self.assertIn("14-848E", prospects[0]["listing"])
        self.assertIn("Possible prospect to research.", prospects[0]["action"])
        chillicothe = _zone("Chillicothe")
        self.assertEqual(chillicothe["aggregationStatus"], "no_aggregation_verified")
        self.assertIsNone(chillicothe["supplier"])
        with open(region_path, "rb") as handle:
            self.assertEqual(handle.read(), before)

        page = self.client.get("/queue?puco=active_missing").get_data(as_text=True)
        self.assertIn("13 app-active zones with no PUCO listing", page)
        self.assertIn("12 NOPEC-vs-app administrator conflicts", page)
        self.assertIn("744 possible prospects to research", page)
        self.assertIn("Kenwood / Symmes Township", page)
        self.assertIn("not applied to zones", page)
        self.assertIn(puco_layer.DISCLAIMER, page)
        prospects_page = self.client.get("/queue?puco=prospect").get_data(as_text=True)
        self.assertIn("14-848E", prospects_page)
        self.assertIn("possible prospects to research", prospects_page)

    def test_snapshot_is_append_only_and_map_labels_certification(self):
        import puco_layer

        page = self.client.get("/map").get_data(as_text=True)
        self.assertIn("PUCO certification only: not proof of an active program, supplier or rate", page)
        self.assertIn("Source: PUCO Government Aggregation map", page)
        self.assertIn('id="puco-electric"', page)
        self.assertIn('id="puco-gas"', page)
        self.assertIn("Own certificate", page)
        with open(os.path.join(ROOT, ".gitignore"), encoding="utf-8") as handle:
            self.assertIn("data/cache/", handle.read())

        feature = {
            "type": "Feature",
            "properties": {
                "OBJECTID": 2179,
                "BoundaryType": "Municipality",
                "CommunityName": "Solon",
                "AggType": "Electric",
                "CountyID": 65,
                "AOGCertID": "01-044E",
                "AOGCaseRef": "00-2317-EL-GAG",
                "AOGCompany": "Northeast Ohio Public Energy Council",
                "AOGIssueDate": "1/2/2001",
                "CommCertID": None,
                "CommCaseRef": None,
                "CommCompany": None,
                "CommIssueDate": None,
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-81.5, 41.3], [-81.4, 41.3], [-81.4, 41.4], [-81.5, 41.4], [-81.5, 41.3]]],
            },
        }

        class _Body:
            def __init__(self, payload):
                self.payload = payload

            def read(self):
                return json.dumps(self.payload).encode()

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

        class _Opener:
            def open(self, request, timeout=None):
                if "Ohio_County_Boundaries" in request.full_url:
                    return _Body({"features": [{"attributes": {"CountyID": 65, "CountyName": "Cuyahoga"}}]})
                return _Body({"type": "FeatureCollection", "features": [feature]})

        with tempfile.TemporaryDirectory() as tmp:
            cache = os.path.join(tmp, "cache")
            history = os.path.join(tmp, "history")
            with patch.dict(os.environ, {"FORGE_PUCO_CACHE": cache, "FORGE_HISTORY_DIR": history}):
                first = puco_layer.fetch_snapshot(opener=_Opener())
                raw_path = os.path.join(cache, first["filename"])
                with open(raw_path, "rb") as handle:
                    raw_bytes = handle.read()
                second = puco_layer.fetch_snapshot(opener=_Opener())
                with open(raw_path, "rb") as handle:
                    self.assertEqual(handle.read(), raw_bytes)
                self.assertNotEqual(first["filename"], second["filename"])
                with open(os.path.join(cache, "manifest.jsonl"), encoding="utf-8") as handle:
                    manifest = [line for line in handle.read().splitlines() if line.strip()]
                self.assertEqual(len(manifest), 2)
                journal = history_store.journal_path()
                with open(journal, encoding="utf-8") as handle:
                    journal_text = handle.read()
                self.assertNotIn("-81.5", journal_text)
                self.assertNotIn("coordinates", journal_text)
                events = [event for event in history_store.load_events(journal) if event["kind"] == "puco_snapshot"]
                self.assertEqual(len(events), 2)
                self.assertEqual(events[0]["feature_count"], 1)
                self.assertEqual(events[0]["attribution"], "Source: PUCO Government Aggregation map")
                body = self.client.get("/api/puco/aggregation").get_json()
                self.assertTrue(body["ok"])
                self.assertEqual(body["disclaimer"], puco_layer.DISCLAIMER)
                self.assertEqual(body["attribution"], "Source: PUCO Government Aggregation map")
                drawn = body["geojson"]["features"][0]
                self.assertEqual(drawn["properties"]["council"], "nopec")
                self.assertEqual(drawn["properties"]["county"], "Cuyahoga")
                self.assertEqual(drawn["properties"]["aog_cert"], "01-044E")
                self.assertEqual(drawn["properties"]["aog_case"], "00-2317-EL-GAG")
                self.assertEqual(drawn["properties"]["aog_date"], "1/2/2001")
                self.assertNotIn("rate", drawn["properties"])
        self.assertEqual(puco_layer.council_id(""), "own")
        self.assertEqual(puco_layer.council_id("Southeast Ohio Public Energy Council"), "sopec")
        self.assertEqual(puco_layer.council_id("Miami Valley Communications Council"), "mvcc")
        self.assertEqual(puco_layer.council_id("Some Other Council"), "other")


if __name__ == "__main__":
    unittest.main()
