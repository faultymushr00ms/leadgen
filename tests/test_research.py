"""Data loading, comparable rate changes, and the report-only monitor."""

import csv
import hashlib
import json
import os
import re
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
    def setUp(self):
        self.client = forge_app.app.test_client()

    def test_all_zones_keep_forge_fields_and_gain_research(self):
        zones = forge_app._load_zones()
        self.assertEqual(len(zones), 393)
        self.assertTrue(all(zone.get("research") and zone.get("original") for zone in zones))
        streetsboro = _zone("Streetsboro")
        self.assertEqual(streetsboro["supplier"], "Dynegy")
        self.assertEqual(streetsboro["currentRate"], 9.999)
        self.assertIsNone(streetsboro["previousRate"])
        self.assertEqual(streetsboro["status"], "pricing_updated")
        self.assertEqual(streetsboro["original"]["supplier"], "Dynegy")
        research = streetsboro["research"]
        self.assertEqual(research["supplier"], "Dynegy")
        self.assertEqual(research["current"]["rate_raw"], "9.999")
        self.assertTrue(research["current"]["sourced"])
        correction = research["corrections"][0]
        self.assertEqual(correction["type"], "program_or_supplier_correction")
        self.assertEqual(correction["date"], "2026-10-14")
        self.assertEqual(correction["oldValue"], "")
        self.assertIn("Dynegy", correction["newValue"])
        self.assertIn("9.999", correction["newValue"])
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
        self.assertEqual(wauseon["utility"], "Toledo Edison")
        self.assertEqual(wauseon["aggregationStatus"], "confirmed_active_aggregation")
        self.assertEqual(wauseon["status"], "verify")
        self.assertTrue(wauseon["research"]["status"]["unresolved"])
        self.assertEqual(wauseon["research"]["status"]["verificationLabel"], "needs call")
        self.assertFalse(wauseon["research"]["notEligible"])
        self.assertFalse(wauseon["card"]["hookAllowed"])
        self.assertEqual(wauseon["research"]["future"]["rate_raw"], "11.09")
        self.assertEqual(wauseon["research"]["current"]["rate_raw"], "")
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
        self.assertEqual(zone["aggregationStatus"], "confirmed_active_aggregation")
        self.assertEqual(zone["futureUse"], "aggregation")
        self.assertEqual(zone["status"], "stable")
        self.assertEqual(zone["supplier"], "Dynegy")
        self.assertEqual(zone["currentRate"], 9.03)
        self.assertEqual(zone["termStart"], "2025-12")
        self.assertEqual(zone["termEnd"], "2027-12")
        self.assertIn("9.03", zone["notes"])
        self.assertNotIn("municipal_blacklist", zone["futureUse"])
        research = zone["research"]
        self.assertEqual(research["utility"], "Toledo Edison")
        self.assertEqual(research["supplier"], "Dynegy")
        self.assertEqual(research["current"]["rate_raw"], "9.03")
        self.assertFalse(research["status"]["unresolved"])
        self.assertFalse(research["notEligible"])
        self.assertTrue(research["hookAllowed"])
        card = zone["card"]
        self.assertTrue(card["ptc"]["applicable"])
        self.assertEqual(card["ptc"]["cents_per_kwh"], 11.26)
        self.assertEqual(card["ptc"]["utility"], "Toledo Edison")
        self.assertIn("2026-10-01", card["ptc"]["effective_start"])
        self.assertIn("2026-12-31", card["ptc"]["effective_end"])
        self.assertTrue(card["currentSourced"])
        self.assertEqual(card["supplier"], "Dynegy")
        self.assertEqual(card["currentLabel"], "9.03")
        self.assertNotIn("Cannot sell", card["takeaway"])
        weekly = forge_app._compute_weekly(forge_app._load_zones())
        avoid_names = {item["name"] for item in weekly["avoid_list"]}
        unresolved_names = {item["name"] for item in weekly["unresolved_list"]}
        self.assertNotIn("Archbold", avoid_names)
        self.assertNotIn("Archbold", unresolved_names)
        with open(os.path.join(ROOT, "data", "research", "forge_corrected_dataset.csv"), newline="", encoding="utf-8") as handle:
            original = next(row for row in csv.DictReader(handle) if row["orig_name"] == "Archbold")
        self.assertEqual(original["orig_aggregationStatus"], "")
        self.assertEqual(original["orig_utility"], "")
        self.assertNotIn("Archbold Municipal Electric", json.dumps(original))
        self.assertIn("Ample, reliable electric power is provided to the Archbold area by Toledo Edison", original["CORR_evidence_quotes"])
        notes = [note for note in history_store.load_removal_notes() if note["zone"] == "Archbold"]
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["note"], "removed incorrect value")
        self.assertEqual(notes[0]["field"], "classification")
        self.assertNotIn("Municipal", notes[0]["reason"])

    def test_swanton_moved_to_toledo_edison_aggregation(self):
        zone = _zone("Swanton")
        self.assertEqual(zone["_source_file"], "nw_central_ohio")
        self.assertEqual(zone["region"], "Toledo / NW Ohio")
        self.assertEqual(zone["utility"], "Toledo Edison")
        self.assertEqual(zone["utilityParent"], "FirstEnergy")
        self.assertEqual(zone["utilityConfidence"], "high")
        self.assertEqual(zone["aggregationStatus"], "confirmed_active_aggregation")
        self.assertEqual(zone["futureUse"], "aggregation")
        self.assertEqual(zone["supplier"], "Dynegy")
        self.assertEqual(zone["currentRate"], 9.76)
        self.assertEqual(zone["previousRate"], 6.96)
        self.assertEqual(zone["rateChange"], 40.2)
        self.assertEqual(zone["termStart"], "2026-05")
        self.assertEqual(zone["termEnd"], "2028-06")
        self.assertEqual(
            zone["takeaway"],
            "IOU-served (Toledo Edison) village with Dynegy opt-out aggregation at 9.76c through Jun 2028; customers can opt out and shop. Closable.",
        )
        self.assertNotIn("municipal_blacklist", zone["futureUse"])
        history_blob = json.dumps(zone.get("history") or [])
        self.assertNotIn("Swanton Municipal Electric", history_blob)
        self.assertNotIn("municipal_blacklist", history_blob)
        notes = [note for note in history_store.load_removal_notes() if note["zone"] == "Swanton"]
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["field"], "classification")
        self.assertEqual(notes[0]["note"], "removed incorrect value")
        self.assertEqual(notes[0]["date"], "2026-10-15")
        self.assertNotIn("Municipal", json.dumps(notes))
        research = zone["research"]
        self.assertEqual(research["utility"], "Toledo Edison")
        self.assertEqual(research["supplier"], "Dynegy")
        self.assertEqual(research["administrator"], "Village of Swanton")
        self.assertEqual(research["status"]["verification"], "likely")
        self.assertEqual(research["status"]["program"], "active_aggregation")
        self.assertFalse(research["status"]["unresolved"])
        self.assertFalse(research["notEligible"])
        self.assertTrue(research["hookAllowed"])
        self.assertEqual(research["takeaway"], zone["takeaway"])
        self.assertEqual(research["current"]["rate"], 9.76)
        self.assertTrue(research["current"]["sourced"])
        self.assertEqual(research["prior"]["rate"], 6.96)
        self.assertTrue(research["prior"]["sourced"])
        self.assertEqual(research["changeVsPrior"]["cents"], 2.8)
        self.assertEqual(research["changeVsPrior"]["percent"], 40.2)
        card = zone["card"]
        self.assertTrue(card["ptc"]["applicable"])
        self.assertEqual(card["ptc"]["code"], "TE")
        self.assertEqual(card["ptc"]["cents_per_kwh"], 11.26)
        self.assertEqual(card["ptc"]["comparison"]["cents"], -1.5)
        self.assertEqual(card["ptc"]["comparison"]["percent"], -13.3)
        self.assertNotIn("Cannot sell", card["takeaway"])
        self.assertIn("419-826-9515", card["openQuestions"])
        weekly = forge_app._compute_weekly(forge_app._load_zones())
        avoid_names = {item["name"] for item in weekly["avoid_list"]}
        self.assertNotIn("Swanton", avoid_names)
        with open(os.path.join(ROOT, "data", "research", "forge_corrected_dataset.csv"), newline="", encoding="utf-8") as handle:
            original = next(row for row in csv.DictReader(handle) if row["orig_name"] == "Swanton" and row["record_index"] == "22")
        self.assertEqual(original["source_file"], "ohio_municipal_utilities.json")
        self.assertEqual(original["orig_aggregationStatus"], "")
        self.assertEqual(original["orig_utility"], "")
        self.assertEqual(original["orig_futureUse"], "")
        self.assertEqual(original["CURRENT_rate"], "9.76")
        self.assertNotIn("Swanton Municipal Electric", json.dumps(original))
        self.assertNotIn("municipal_blacklist", json.dumps(original))
        periods = [
            row for row in load_rate_ledger()
            if row["origin"] == "rate_ledger.csv" and row["zone"] == "Swanton"
        ]
        municipal = [
            row for row in periods
            if "Municipal" in (row["supplier"] or "")
        ]
        self.assertEqual(municipal, [])
        verified = [
            row for row in periods
            if row["source"] == "verified correction (likely)" and row["rate_raw"] == "9.76"
        ]
        self.assertEqual(len(verified), 1)
        self.assertFalse(verified[0].get("superseded"))
        self.assertEqual(verified[0]["region"], "nw_central_ohio")
        prior = [row for row in periods if row["rate_raw"] == "6.96" and row["role"] == "prior"]
        self.assertEqual(len(prior), 1)
        self.assertEqual(prior[0]["effective_start"], "2023-05")
        self.assertEqual(prior[0]["effective_end"], "2026-05")
        queue = [row for row in load_queue() if row["zone"] == "Swanton"]
        self.assertEqual(len(queue), 2)
        old = next(row for row in queue if row["region"] == "ohio_municipal_utilities")
        new = next(row for row in queue if row["region"] == "nw_central_ohio")
        self.assertTrue(old["superseded"])
        self.assertEqual(old["utility"], "Toledo Edison")
        self.assertNotIn("Swanton Municipal Electric", old["exact_next_action"])
        self.assertFalse(new.get("superseded"))
        self.assertEqual(new["rank"], "329")
        self.assertEqual(new["utility"], "Toledo Edison")
        self.assertIn("419-826-9515", new["exact_next_action"])
        self.assertIn("2026 renewal ordinance", new["exact_next_action"])
        page = self.client.get("/card?file=nw_central_ohio&name=Swanton")
        self.assertEqual(page.status_code, 200)
        body = page.get_data(as_text=True)
        self.assertIn("Closable.", body)
        self.assertIn("9.76", body)
        self.assertIn("6.96", body)
        self.assertIn("11.26", body)
        self.assertIn("419-826-9515", body)
        self.assertNotIn("Cannot sell", body)
        self.assertNotIn("Swanton Municipal Electric", body)
        self.assertNotIn("municipal_blacklist", body)
        self.assertNotIn("Municipal (exempt", body)
        self.assertIn("Swanton | classification | removed incorrect value | 2026-10-15 |", body)
        self.assertIn("Toledo Edison <strong>11.26¢/kWh</strong>", body)
        missing = self.client.get("/card?file=ohio_municipal_utilities&name=Swanton")
        self.assertEqual(missing.status_code, 404)

    def test_conflict_municipal_flags_stay_unresolved(self):
        """The six former conflict towns are IOU aggregation. Wauseon's current rate is still a call."""
        weekly = forge_app._compute_weekly(forge_app._load_zones())
        avoid_names = {zone["name"] for zone in weekly["avoid_list"]}
        unresolved_names = {zone["name"] for zone in weekly["unresolved_list"]}
        expected = {
            "Wellsville": ("AEP Ohio", "9.56"),
            "Cortland": ("Ohio Edison", "9.81"),
            "Coldwater": ("AES Ohio", "9.08"),
            "Delphos": ("AEP Ohio", "10.87"),
            "Ada": ("AEP Ohio", "9.45"),
        }
        for name, (utility, rate) in expected.items():
            zone = _zone(name)
            self.assertEqual(zone["utility"], utility)
            self.assertEqual(zone["aggregationStatus"], "confirmed_active_aggregation")
            self.assertEqual(zone["supplier"], "Dynegy")
            self.assertEqual(zone["research"]["current"]["rate_raw"], rate)
            self.assertFalse(zone["research"]["notEligible"])
            self.assertFalse(zone["card"]["municipalFlagUnconfirmed"])
            self.assertNotIn(name, avoid_names)
            self.assertNotIn(name, unresolved_names)
            self.assertTrue(zone["card"]["ptc"]["applicable"])
        wauseon = _zone("Wauseon")
        self.assertIn("Wauseon", unresolved_names)
        self.assertNotIn("Wauseon", avoid_names)
        self.assertEqual(wauseon["card"]["ptc"]["code"], "TE")
        ripley = _zone("Ripley")
        self.assertEqual(ripley["aggregationStatus"], "municipal_utility")
        self.assertIn("Ripley", avoid_names)
        self.assertNotIn("Franklin", [zone["name"] for zone in forge_app._load_zones() if zone["_source_file"] == "dayton_aes_suburbs"])
        self.assertEqual(len([zone for zone in forge_app._load_zones() if zone["name"] == "Franklin"]), 1)
        self.assertEqual(len([zone for zone in forge_app._load_zones() if zone["name"] == "Springboro"]), 1)

    def test_misinfo_sweep_sells_the_corrected_towns(self):
        plain = _zone("Plain Township")
        self.assertEqual(plain["utility"], "AEP Ohio")
        self.assertEqual(plain["aggregationStatus"], "confirmed_active_aggregation")
        self.assertIn("NOPEC", plain["supplier"])
        self.assertIsNone(plain["currentRate"])
        self.assertEqual(plain["previousRate"], 8.26)
        self.assertNotIn("shut down", (plain["hook"] or "").lower())
        self.assertNotIn("shut down", plain["card"]["takeaway"].lower())

        paulding = _zone("Paulding")
        self.assertEqual(paulding["utility"], "AEP Ohio")
        self.assertEqual(paulding["currentRate"], 9.7)
        self.assertIn("Jason Vance", paulding["card"]["openQuestions"])
        self.assertNotIn(paulding["name"], {zone["name"] for zone in forge_app._compute_weekly(forge_app._load_zones())["avoid_list"]})

        mentor = _zone("Mentor")
        self.assertEqual(mentor["card"]["utility"], "The Illuminating Company")
        self.assertEqual(mentor["card"]["ptc"]["code"], "CEI")
        self.assertEqual(mentor["card"]["ptc"]["cents_per_kwh"], 11.24)

        canton = _zone("Canton")
        self.assertEqual(canton["utility"], "AEP Ohio")
        self.assertEqual(canton["card"]["ptc"]["code"], "AEP")
        marion = _zone("Marion")
        self.assertEqual(marion["utility"], "Ohio Edison")
        self.assertEqual(marion["card"]["ptc"]["code"], "OE")

        stow = _zone("Stow")
        self.assertEqual(stow["card"]["supplier"], "Dynegy")
        self.assertNotIn("NOPEC", stow["card"]["supplier"])
        bay = _zone("Bay Village")
        self.assertEqual(bay["card"]["futureLabel"], "10.16")
        self.assertEqual(bay["research"]["current"]["rate_raw"], "")
        self.assertEqual(bay["card"]["utility"], "The Illuminating Company")

        stark = _zone("Stark County (Unincorporated / Remaining)")
        self.assertIsNone(stark["currentRate"])
        self.assertEqual(stark["research"]["current"]["rate_raw"], "")
        self.assertEqual(_zone("Paris Township (Stark)")["supplier"], "NOPEC / NextEra Energy Services")

        point = _zone("Russells Point")
        self.assertEqual(point["currentRate"], 9.26)
        self.assertEqual(point["supplier"], "Dynegy")
        lakeview = _zone("Lakeview")
        self.assertEqual(lakeview["aggregationStatus"], "municipal_utility")
        self.assertTrue(lakeview["research"]["notEligible"])

        mahoning = _zone("Springfield Township (Mahoning)")
        self.assertNotEqual(mahoning["currentRate"], 10.59)
        self.assertIn("NOPEC", mahoning["supplier"])
        self.assertEqual(_zone("Mahoning County")["currentRate"], None)

        notes = json.dumps(history_store.load_removal_notes())
        for token in ("9.999", "9.94", "9.38", "10.59", "9.77", "Municipal Electric"):
            self.assertNotIn(token, notes)

    def test_incorrect_history_is_removed_and_genuine_rates_stay(self):
        euclid = _zone("Euclid")
        self.assertEqual(euclid["supplier"], "Dynegy")
        self.assertEqual(euclid["currentRate"], 9.95)
        self.assertIsNone(euclid["previousRate"])
        self.assertEqual(euclid["research"]["historical"]["rate_raw"], "7.69")
        self.assertEqual(euclid["research"]["prior"]["rate_raw"], "")
        stow = _zone("Stow")
        self.assertEqual(stow["research"]["historical"]["rate_raw"], "8.38")
        self.assertEqual(stow["currentRate"], 8.99)
        green = _zone("Green")
        self.assertEqual(green["research"]["prior"]["rate_raw"], "9.24")
        self.assertEqual(green["research"]["current"]["rate_raw"], "9.48")
        self.assertNotIn("10.399", green["research"]["corrections"][0]["reason"])
        self.assertNotIn("10.399", green["research"]["corrections"][0]["newValue"])
        shaker = _zone("Shaker Heights")
        self.assertEqual(shaker["research"]["historical"]["rate_raw"], "9.49")
        self.assertEqual(shaker["currentRate"], 9.99)
        notes = history_store.load_removal_notes()
        blob = json.dumps(notes)
        for token in ("9.999", "8.999", "7.0", "Swanton Municipal Electric", "municipal_blacklist"):
            self.assertNotIn(token, blob)
        self.assertTrue(any(note["zone"] == "Euclid" and note["note"] == "removed incorrect value" for note in notes))
        ledger = [
            row for row in load_rate_ledger()
            if row["origin"] == "rate_ledger.csv" and row["zone"] == "Euclid" and row["supplier"] == "NOPEC"
        ]
        self.assertEqual(ledger, [])
        stark = [
            row for row in load_rate_ledger()
            if row["origin"] == "rate_ledger.csv"
            and row["zone"] == "Stark County (Unincorporated / Remaining)"
            and row["rate_raw"] == "9.77"
        ]
        self.assertEqual(stark, [])
        self.assertEqual(_zone("Fostoria")["currentRate"], 10.59)
        self.assertEqual(_zone("Madison Township (Butler Co)")["research"]["current"]["rate_raw"], "9.77")
        westlake = _zone("Westlake")
        self.assertEqual(westlake["research"]["prior"]["rate_raw"], "8.38")
        self.assertEqual(westlake["research"]["historical"]["rate_raw"], "4.77")
        self.assertNotIn("10.59", _zone("Mahoning County")["card"]["openQuestions"])
        with open(os.path.join(ROOT, "data", "history", "journal.jsonl"), encoding="utf-8") as handle:
            journal = handle.read()
        self.assertNotIn("municipal list", journal.lower())
        self.assertNotIn("Archbold", journal)
        with open(os.path.join(ROOT, "data", "research", "forge_corrected_dataset.csv"), newline="", encoding="utf-8") as handle:
            stored = {row["orig_name"]: row for row in csv.DictReader(handle)}
        for name in ("Ada", "Wellsville", "Cortland", "Wauseon", "Coldwater", "Delphos", "Fremont"):
            self.assertNotIn("Exempt from Ohio retail", stored[name]["orig_notes"])
            self.assertNotIn("owned electric utility", stored[name]["orig_notes"])
        self.assertEqual(stored["Green"]["PRIOR_rate"], "9.24")
        self.assertEqual(stored["Fostoria"]["CURRENT_rate"], "10.59")
        self.assertEqual(stored["Madison Township (Butler Co)"]["CURRENT_rate"], "9.77")


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
        self.assertEqual(len(load_queue()), 323)
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
                self.assertEqual(len(forge_app._load_zones()), 393)
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
        self.assertIn("Pending", wauseon)
        self.assertIn("11.09", wauseon)
        self.assertNotIn("not marked inactive", wauseon.lower())
        self.assertNotIn("Verify before using", wauseon)
        queue = self.client.get("/queue?verification=escalate-call").get_data(as_text=True)
        self.assertIn("Wauseon", queue)
        self.assertIn("888-682-2170", queue)
        self.assertIn("Pending", queue)
        self.assertNotIn(">unresolved<", queue)
        expiring = self.client.get("/expiring").get_data(as_text=True)
        self.assertIn("Heath / Newark", expiring)
        zip_page = self.client.get("/counties?zip=44241&county=Portage").get_data(as_text=True)
        self.assertIn("not proof", zip_page)
        self.assertIn("Streetsboro", zip_page)
        self.assertIn("Portage", zip_page)
        resolved = self.client.get("/api/zip/45066")
        body = resolved.get_json()
        self.assertEqual(body["match_count"], 1)
        self.assertEqual(body["zone"]["name"], "Springboro")
        self.assertEqual(body["jurisdictions"][0]["utility"], "Duke Energy Ohio")
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
        self.assertIsNone(duke["comparison"])
        self.assertEqual(sharonville["card"]["futureLabel"], "10.276")
        self.assertEqual(sharonville["research"]["current"]["rate_raw"], "")
        self.assertIn("City of Sharonville", sharonville["card"]["openQuestions"])

        centerville = _zone("Centerville")
        aes = centerville["card"]["ptc"]
        self.assertEqual(aes["code"], "AES")
        self.assertEqual(aes["effective_start"], "2026-06-01")
        self.assertEqual(aes["effective_end"], "2027-05-31")
        self.assertEqual(aes["comparison"]["cents"], -1.811)
        self.assertEqual(aes["comparison"]["percent"], -16.7)

        amherst = _zone("Amherst")["card"]["ptc"]
        self.assertFalse(amherst["applicable"])
        self.assertEqual(amherst["label"], "PTC not applicable")
        self.assertIsNone(amherst["comparison"])
        wauseon_ptc = _zone("Wauseon")["card"]["ptc"]
        self.assertTrue(wauseon_ptc["applicable"])
        self.assertEqual(wauseon_ptc["code"], "TE")
        self.assertEqual(wauseon_ptc["cents_per_kwh"], 11.26)
        self.assertIsNone(wauseon_ptc["comparison"])
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
        self.assertIn("10.276", duke_page)
        self.assertNotIn("-1.100¢ (-10.5%)", duke_page)
        municipal = self.client.get("/card?file=ohio_municipal_utilities&name=Wauseon").get_data(as_text=True)
        self.assertIn("Toledo Edison", municipal)
        self.assertIn("11.26", municipal)
        self.assertIn("11.09", municipal)
        self.assertNotIn("Municipal blacklist flag is not confirmed.", municipal)
        self.assertNotIn("Aggregation current vs this residential PTC", municipal)
        hotspots = self.client.get("/hotspots").get_data(as_text=True)
        self.assertIn('id="bc-ptc"', hotspots)
        self.assertIn("Aggregation current vs this residential PTC", hotspots)
        reference = self.client.get("/ptc").get_data(as_text=True)
        self.assertIn("Earlier source note kept", reference)
        self.assertIn("2026-10-31", reference)
        self.assertIn("2027-05-31", reference)

    def test_westlake_drops_unsourced_rates_and_keeps_real_history(self):
        westlake = _zone("Westlake")
        self.assertEqual(westlake["utility"], "The Illuminating Company")
        self.assertEqual(westlake["supplier"], "Dynegy")
        self.assertIsNone(westlake["currentRate"])
        self.assertEqual(westlake["previousRate"], 8.38)
        self.assertNotIn("NOPEC", westlake["hook"])
        self.assertNotIn("9.999", json.dumps(westlake["original"]))
        self.assertEqual(westlake["research"]["utility"], "The Illuminating Company")
        self.assertEqual(westlake["research"]["administrator"], "City of Westlake (consultant Brenda Fargo)")
        self.assertIn("Dynegy", westlake["research"]["supplier"])
        self.assertEqual(westlake["research"]["current"]["rate_raw"], "11.24")
        self.assertIn("TerritoryId=6", westlake["research"]["current"]["source"])
        self.assertEqual(westlake["research"]["prior"]["rate_raw"], "8.38")
        self.assertEqual(westlake["research"]["prior"]["term"], "2025-02 to 2026-06")
        self.assertEqual(westlake["research"]["historical"]["rate_raw"], "4.77")
        self.assertNotIn("supersededResearch", westlake["research"])
        card = westlake["card"]
        self.assertEqual(
            card["hook"],
            "Westlake has no aggregation, residents default to CEI PTC 11.24 c (Oct 1 to Dec 31 2026).",
        )
        self.assertNotIn("NOPEC", card["hook"])
        self.assertTrue(card["noGasAggregation"])
        self.assertEqual(card["rejectedRenewal"]["rate"], "10.11")
        self.assertEqual(card["unsourcedForgeRates"], [])
        self.assertEqual(card["removalNotes"][0]["note"], "removed incorrect value")
        self.assertNotIn("9.999", json.dumps(card["removalNotes"]))
        self.assertIsNone(card["ptc"]["comparison"])
        self.assertEqual(card["ptc"]["cents_per_kwh"], 11.24)
        page = self.client.get("/card?file=nopec_cuyahoga_suburbs&name=Westlake").get_data(as_text=True)
        self.assertIn("Westlake has no aggregation, residents default to CEI PTC 11.24 c (Oct 1 to Dec 31 2026).", page)
        self.assertNotIn("FORGE recorded history, unsourced", page)
        self.assertIn("No gas aggregation.", page)
        self.assertIn("10.11", page)
        self.assertIn("8.38", page)
        self.assertIn("4.77", page)
        self.assertIn("Westlake | recorded rate | removed incorrect value | 2026-10-15 |", page)
        self.assertNotIn("9.999", page)
        self.assertNotIn("8.999", page)
        weekly = self.client.get("/weekly").get_data(as_text=True)
        self.assertIn("Westlake has no aggregation, residents default to CEI PTC 11.24 c", weekly)
        self.assertNotIn("Westlake is on NOPEC", weekly)
        with open(os.path.join(ROOT, "data", "research", "forge_corrected_dataset.csv"), newline="") as handle:
            stored = [row for row in csv.DictReader(handle) if row["orig_name"] == "Westlake"]
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["norm_utility"], "The Illuminating Company")
        self.assertEqual(stored[0]["PRIOR_rate"], "8.38")
        self.assertIn("hoodline.com", stored[0]["PRIOR_source"])
        self.assertIn("4.77", stored[0]["HISTORICAL_rate_benchmark"])
        self.assertEqual(stored[0]["HISTORICAL_repo_rate_trail"], "")
        self.assertNotIn("9.999", json.dumps(stored[0]))
        self.assertNotIn("7.0", stored[0]["PRIOR_rate"])

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
        self.assertIn("Pending", page)
        self.assertNotIn("Unresolved / needs call", page)
        self.assertNotIn("Needs call. Not confirmed.", page)
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
        self.assertEqual(counts["active_missing"], 16)
        self.assertEqual(counts["nopec_admin"], 12)
        self.assertEqual(counts["prospects"], 744)
        self.assertEqual(counts["app_nopec_not_on_map"], 1)
        self.assertEqual(len(load_queue()), 323)
        self.assertEqual(payload["disclaimer"], puco_layer.DISCLAIMER)
        self.assertEqual(payload["attribution"], "Source: PUCO Government Aggregation map")
        active = [item["name"] for item in payload["flags"] if "active_missing" in item["groups"]]
        self.assertIn("Kenwood / Symmes Township", active)
        self.assertIn("Chillicothe", active)
        self.assertEqual(len(active), 16)
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
        self.assertEqual(chillicothe["aggregationStatus"], "confirmed_active_aggregation")
        self.assertEqual(chillicothe["supplier"], "AEP Energy")
        self.assertIsNone(chillicothe["currentRate"])
        self.assertIn("SOPEC", chillicothe["research"]["openQuestions"])
        with open(region_path, "rb") as handle:
            self.assertEqual(handle.read(), before)

        page = self.client.get("/queue?puco=active_missing").get_data(as_text=True)
        self.assertIn("16 app-active zones with no PUCO listing", page)
        self.assertIn("12 NOPEC-vs-app administrator conflicts", page)
        self.assertIn("744 possible prospects to research", page)
        self.assertIn("Kenwood / Symmes Township", page)
        self.assertIn("not applied to zones", page)
        self.assertIn(puco_layer.DISCLAIMER, page)
        prospects_page = self.client.get("/queue?puco=prospect").get_data(as_text=True)
        self.assertIn("14-848E", prospects_page)
        self.assertIn("possible prospects to research", prospects_page)

    def test_merged_research_lifecycle_hot_leads_and_unverified(self):
        self.assertEqual(len(forge_app._load_zones()), 393)
        kettering = _zone("Kettering")
        self.assertEqual(kettering["supplier"], "Constellation")
        self.assertEqual(kettering["currentRate"], 9.049)
        self.assertEqual(kettering["card"]["futureLabel"], "11.53")
        self.assertEqual(kettering["card"]["futureStart"], "2026-12")
        self.assertEqual(kettering["card"]["futureEnd"], "2029-12")
        self.assertEqual(kettering["card"]["lifecycle"]["status"], "active")
        self.assertIn("11.73", kettering["card"]["futureNote"])
        card = self.client.get("/card?file=dayton_sw_ohio&name=Kettering").get_data(as_text=True)
        self.assertIn("Announced / Future", card)
        self.assertIn("Ending soon", card)
        self.assertNotIn("lifecycle:", card)
        self.assertIn("11.53", card)

        worthington = _zone("Worthington")
        self.assertEqual(worthington["supplier"], "Direct Energy")
        self.assertEqual(worthington["currentRate"], 10.69)
        self.assertEqual(worthington["card"]["supplier"], "Direct Energy")
        self.assertEqual(worthington["card"]["verification"], "likely")
        self.assertFalse(worthington["card"]["unresolved"])

        powell = _zone("Powell")
        self.assertIsNone(powell["currentRate"])
        self.assertEqual(powell["card"]["lifecycle"]["status"], "rate_pending")
        self.assertNotIn("9.99", powell["takeaway"])
        self.assertIn("855-667-3201", powell["card"]["openQuestions"])
        self.assertIn("number not in sources", powell["card"]["openQuestions"])

        albany = _zone("Albany")
        self.assertEqual(albany["currentRate"], 11.262)
        self.assertEqual(albany["card"]["ptc"]["cents_per_kwh"], 10.19)
        self.assertEqual(albany["card"]["ptc"]["comparison"]["customer_class"], "residential")
        morrow_county = _zone("Morrow County")
        self.assertEqual(morrow_county["currentRate"], 8.87)
        self.assertIn("Village of Morrow", morrow_county["notes"])
        morrow_page = self.client.get("/card?file=merged_confirmed&name=Morrow%20County").get_data(as_text=True)
        self.assertIn("Village of Morrow", morrow_page)
        self.assertIn("Canaan", morrow_page)
        village = _zone("Morrow")
        self.assertNotEqual(village["currentRate"], 8.87)
        plain_city = _zone("Plain City")
        self.assertIsNone(plain_city["currentRate"])
        self.assertEqual(plain_city["card"]["lifecycle"]["status"], "rate_pending")
        self.assertNotIn("10.499", plain_city["notes"] or "")

        wyoming = _zone("Wyoming")
        self.assertEqual(wyoming["card"]["lifecycle"]["status"], "ended")
        self.assertEqual(wyoming["card"]["lifecycle"]["endedDate"], "2026-07")
        self.assertIn("513-821-7600", wyoming["card"]["openQuestions"])
        self.assertEqual(wyoming["card"]["currentCaption"], "Last aggregation rate")
        self.assertEqual(wyoming["aggregationStatus"], "no_aggregation_verified")
        page = self.client.get("/card?file=cincinnati_duke_suburbs&name=Wyoming").get_data(as_text=True)
        self.assertIn("Ended 2026-07", page)
        self.assertIn("no offer guaranteed savings", page)

        fremont = _zone("Fremont")
        self.assertIn("10.67", fremont["card"]["openQuestions"])
        self.assertIn("9.96", fremont["card"]["openQuestions"])
        self.assertEqual(fremont["currentRate"], 9.96)
        plain = _zone("Plain Township")
        self.assertEqual(plain["utility"], "AEP Ohio")
        self.assertIsNone(plain["currentRate"])
        self.assertIn("855-667-3201", plain["card"]["openQuestions"])
        self.assertIn("Ohio Edison", plain["notes"])

        hot = self.client.get("/hot-leads").get_data(as_text=True)
        self.assertIn("Residential Price to Compare", hot)
        self.assertIn("agg−PTC", hot)
        self.assertIn("Silverton", hot)
        self.assertIn("10.49", hot)
        unverified = self.client.get("/unverified?q=Ashley").get_data(as_text=True)
        self.assertIn("Ashley", unverified)
        self.assertIn("Seeking supplier", unverified)
        self.assertNotIn("single-source", unverified.lower())
        self.assertNotIn("not confirmed", unverified.lower())
        reminderville = self.client.get("/unverified?q=Reminderville").get_data(as_text=True)
        self.assertIn("Reminderville", reminderville)
        self.assertIn("NOPEC/NextEra", reminderville)
        self.assertNotIn("Not a battlecard rate", reminderville)
        self.assertNotIn("single-source", reminderville.lower())

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


class PresentationCopyTests(unittest.TestCase):
    """Research-log phrasing stays in the data and stays off the screen."""

    BANNED = (
        "needs call",
        "not confirmed",
        "not marked inactive",
        "verify before using",
        "number not in sources",
        "unresolved",
        "escalate-call",
        "forge recorded",
        "single-source",
    )
    PAGES = (
        "/hotspots",
        "/hot-leads",
        "/unverified",
        "/unverified?q=Ashley",
        "/queue",
        "/queue?verification=escalate-call",
        "/weekly",
        "/expiring",
        "/intel",
        "/map",
        "/counties?county=Cuyahoga",
        "/card?file=ohio_municipal_utilities&name=Archbold",
        "/card?file=cleveland_cuyahoga&name=Cleveland",
        "/card?file=nopec_cuyahoga_suburbs&name=Westlake",
        "/card?file=ne_ohio_firstenergy&name=Girard",
        "/card?file=ohio_municipal_utilities&name=Wauseon",
        "/card?file=sopec_columbus_suburbs&name=Powell",
    )

    def setUp(self):
        self.client = forge_app.app.test_client()

    def test_research_log_phrases_do_not_render(self):
        for path in self.PAGES:
            page = self.client.get(path)
            self.assertEqual(page.status_code, 200, path)
            visible = _visible_text(page.get_data(as_text=True)).lower()
            for phrase in self.BANNED:
                self.assertNotIn(phrase, visible, f"{phrase} on {path}")

    def test_unverified_rate_is_not_shown_as_current(self):
        wauseon = _zone("Wauseon")
        self.assertIn("not marked inactive", wauseon["research"]["takeaway"])
        self.assertFalse(wauseon["card"]["currentSourced"])
        self.assertEqual(wauseon["card"]["voice"]["currentText"], "—")
        self.assertEqual(wauseon["card"]["voice"]["confidence"]["label"], "Pending")
        self.assertNotIn("not marked inactive", wauseon["card"]["voice"]["takeaway"])
        girard = _zone("Girard")
        self.assertFalse(girard["card"]["currentSourced"])
        self.assertEqual(girard["card"]["voice"]["currentText"], "—")
        self.assertEqual(girard["card"]["voice"]["status"], "Rate pending")
        page = self.client.get("/card?file=ne_ohio_firstenergy&name=Girard").get_data(as_text=True)
        self.assertIn('class="v pending"', page)
        self.assertIn("Rate pending", page)
        streetsboro = _zone("Streetsboro")
        self.assertTrue(streetsboro["card"]["currentSourced"])
        self.assertEqual(streetsboro["card"]["voice"]["currentText"], "9.999¢")
        self.assertEqual(streetsboro["card"]["voice"]["confidence"]["kind"], "hollow")


class TalkingPointTests(unittest.TestCase):
    """Sourced talking points on the battlecard, with research-log wording kept off them."""

    BANNED = re.compile(
        r"needs call|not confirmed|not in sources|not marked inactive|verify before using|"
        r"\bverify\b|\bunconfirmed\b|\bescalate\b|\bunresolved\b|single-source|forge recorded",
        re.I,
    )

    def setUp(self):
        self.client = forge_app.app.test_client()

    def test_ended_active_and_no_program_towns(self):
        westlake = _zone("Westlake")
        self.assertIsNone(westlake["currentRate"])
        self.assertEqual(westlake["previousRate"], 8.38)
        talk = westlake["card"]["talkingPoints"]
        self.assertTrue(talk["lead"])
        self.assertIn("ended", talk["intro"].lower())
        self.assertGreaterEqual(len(talk["points"]), 2)
        self.assertLessEqual(len(talk["points"]), 4)
        self.assertEqual(talk["groups"][0]["label"], "Upcoming")
        self.assertEqual(talk["groups"][1]["label"], "Recent")
        sentences = " ".join(point["sentence"] for point in talk["points"])
        self.assertIn("9.4503", sentences)
        self.assertIn("GS default", sentences)
        self.assertIn("10.11", sentences)
        self.assertIn("June 2026", sentences)
        self.assertIn("8.38", sentences)
        self.assertNotIn("11.24", sentences)
        self.assertTrue(all(point["sourceUrl"].startswith("http") and point["dateLabel"] for point in talk["points"]))

        page = self.client.get("/card?file=nopec_cuyahoga_suburbs&name=Westlake").get_data(as_text=True)
        section = _talk_section(page)
        self.assertIn("cleveland.com", section)
        self.assertIn("What to talk about", section)
        self.assertLess(page.find('id="what-to-talk-about"'), page.find('class="rate-grid'))
        self.assertLess(page.find('id="what-to-talk-about"'), page.find('id="battlecard-nearby"'))
        self.assertLess(page.find('id="battlecard-nearby"'), page.find('class="rate-grid'))
        self.assertLess(section.find("Upcoming"), section.find("Recent"))
        self.assertIn("vs commercial default", page)
        self.assertLess(page.find('id="ptc-commercial"'), page.find('id="ptc-residential"'))
        self.assertIn("11.24", page[page.find('id="ptc-residential"'):])
        self.assertIsNone(self.BANNED.search(_visible_text(section)))

        brookfield = _zone("Brookfield Township (Trumbull)")
        brook = brookfield["card"]["talkingPoints"]
        self.assertTrue(brook["lead"])
        self.assertIn("not a program in this town", brook["framing"])
        brook_text = " ".join(point["sentence"] for point in brook["points"])
        self.assertIn("9.3786", brook_text)
        self.assertIn("GS default", brook_text)
        self.assertIn("10.14", brook_text)
        self.assertNotIn("11.07", brook_text)
        self.assertGreaterEqual(len(brook["points"]), 2)
        brook_page = self.client.get(
            "/card?file=youngstown_warren&name=Brookfield%20Township%20(Trumbull)"
        ).get_data(as_text=True)
        brook_section = _talk_section(brook_page)
        self.assertNotIn("cleveland.com", brook_section)
        self.assertIn("9.3786", brook_section)
        self.assertIn("11.07", brook_page[brook_page.find('id="ptc-residential"'):])
        self.assertLess(brook_page.find('id="what-to-talk-about"'), brook_page.find('class="rate-grid'))
        self.assertIsNone(self.BANNED.search(_visible_text(brook_section)))

        archbold = _zone("Archbold")
        self.assertEqual(archbold["currentRate"], 9.03)
        active = archbold["card"]["talkingPoints"]
        self.assertFalse(active["lead"])
        active_text = " ".join(point["sentence"] for point in active["points"])
        self.assertIn("9.03", active_text)
        self.assertIn("9.431", active_text)
        self.assertIn("0.401", active_text)
        arch_page = self.client.get("/card?file=ohio_municipal_utilities&name=Archbold").get_data(as_text=True)
        self.assertIn("11.26", arch_page[arch_page.find('id="ptc-residential"'):])
        arch_section = _talk_section(arch_page)
        self.assertIn("talk-compact", arch_section)
        self.assertNotIn("talk-lead", arch_section)
        self.assertLess(arch_page.find('class="rate-grid'), arch_page.find('id="what-to-talk-about"'))
        self.assertLess(arch_page.find('id="what-to-talk-about"'), arch_page.find('id="battlecard-nearby"'))
        self.assertIsNone(self.BANNED.search(_visible_text(arch_section)))

        girard = self.client.get("/card?file=ne_ohio_firstenergy&name=Girard").get_data(as_text=True)
        girard_section = _talk_section(girard)
        self.assertIn("11.46", girard_section)
        self.assertNotIn("6.88", girard_section)
        self.assertIn("2.081", girard_section)
        self.assertIn("9.3786", girard_section)
        self.assertFalse(_zone("Girard")["card"]["talkingPoints"]["lead"])
        self.assertIsNone(self.BANNED.search(_visible_text(girard_section)))

    def test_banned_phrases_stay_off_every_town_and_files_stay_put(self):
        paths = [
            "data/regions/nopec_cuyahoga_suburbs.json",
            "data/regions/ne_ohio_firstenergy.json",
            "data/regions/ohio_municipal_utilities.json",
            "data/regions/youngstown_warren.json",
        ]
        before = {}
        for path in paths:
            with open(os.path.join(ROOT, path), "rb") as handle:
                before[path] = hashlib.sha256(handle.read()).hexdigest()
        zones = forge_app._load_zones()
        for path in paths:
            with open(os.path.join(ROOT, path), "rb") as handle:
                self.assertEqual(before[path], hashlib.sha256(handle.read()).hexdigest())
        for zone in zones:
            talk = (zone.get("card") or {}).get("talkingPoints") or {}
            blob = " ".join(
                [talk.get("intro") or "", talk.get("framing") or ""]
                + [
                    " ".join([
                        point.get("sentence") or "",
                        point.get("chip") or "",
                        point.get("quote") or "",
                        point.get("confidenceTitle") or "",
                    ])
                    for point in talk.get("points") or []
                ]
            )
            self.assertIsNone(self.BANNED.search(blob), zone.get("name"))
            points = talk.get("points") or []
            self.assertLessEqual(len(points), 4, zone.get("name"))
            for point in points:
                self.assertTrue(point["sourceUrl"].startswith("http"), zone.get("name"))
                self.assertTrue(point["dateLabel"], zone.get("name"))

    def test_hotspots_pane_has_the_section(self):
        page = self.client.get("/hotspots").get_data(as_text=True)
        self.assertIn('id="bc-talk"', page)
        self.assertIn("vs commercial default", page)
        self.assertIn("max-width: 840px", page)
        self.assertIn("min-width: 440px", page)
        self.assertIn("max-width: 1100px", page)
        self.assertNotIn("width: 360px", page)


class CommercialDefaultTests(unittest.TestCase):
    """Small-commercial tariff rate leads. Residential PTC stays a smaller line."""

    def setUp(self):
        self.client = forge_app.app.test_client()

    def test_salem_leads_with_sourced_gs_and_keeps_residential(self):
        salem = _zone("Salem")
        ptc = salem["card"]["ptc"]
        self.assertEqual(ptc["customer_class"], "residential")
        self.assertEqual(ptc["cents_per_kwh"], 11.07)
        commercial = ptc["commercial"]
        self.assertTrue(commercial["sourced"])
        self.assertEqual(commercial["cents_per_kwh"], 9.3786)
        self.assertEqual(commercial["schedule"], "GS")
        self.assertEqual(commercial["energy_cents"], 7.2774)
        self.assertEqual(commercial["capacity_cents"], 2.1012)
        self.assertIn("firstenergycorp.com", commercial["source_url"])
        self.assertIn("Rider GEN", commercial["source"])
        page = self.client.get("/card?file=ne_ohio_firstenergy&name=Salem").get_data(as_text=True)
        commercial_at = page.find('id="ptc-commercial"')
        residential_at = page.find('id="ptc-residential"')
        self.assertTrue(0 <= commercial_at < residential_at)
        commercial_html = page[commercial_at:residential_at]
        residential_html = page[residential_at:]
        self.assertIn("9.3786", commercial_html)
        self.assertIn("Commercial default", commercial_html)
        self.assertNotIn("11.07", commercial_html)
        self.assertIn("11.07", residential_html)
        self.assertIn("Residential Price to Compare", residential_html)
        self.assertIn("ptc-residential", page)
        self.assertEqual(salem["currentRate"], 9.79)

    def test_each_iou_is_sourced_or_pending_without_a_made_up_rate(self):
        expected = {
            "OE": ("Salem", 9.3786, "GS"),
            "CEI": ("Westlake", 9.4503, "GS"),
            "TE": ("Archbold", 9.431, "GS"),
            "AEP": ("Canton", 9.806, "GS-NDM"),
            "DUKE": ("Sharonville", None, ""),
            "AES": ("Centerville", None, ""),
        }
        for code, (name, cents, schedule) in expected.items():
            commercial = _zone(name)["card"]["ptc"]["commercial"]
            self.assertEqual(commercial.get("code", code) if commercial["sourced"] else code, code)
            if cents is None:
                self.assertFalse(commercial["sourced"])
                self.assertIsNone(commercial.get("cents_per_kwh"))
            else:
                self.assertTrue(commercial["sourced"], name)
                self.assertEqual(commercial["cents_per_kwh"], cents)
                self.assertEqual(commercial["schedule"], schedule)
                self.assertTrue(commercial["source_url"].startswith("http"))
        page = self.client.get("/card?file=cincinnati_duke&name=Sharonville").get_data(as_text=True)
        commercial_html = page[page.find('id="ptc-commercial"'):page.find('id="ptc-residential"')]
        self.assertIn("Pending", commercial_html)
        self.assertIn("No sourced small-commercial default is on file", commercial_html)
        self.assertNotIn("¢/kWh", commercial_html)
        self.assertIn("10.49", page[page.find('id="ptc-residential"'):])


def _talk_section(html: str) -> str:
    start = html.find('id="what-to-talk-about"')
    end = html.find("<!-- /what-to-talk-about -->")
    if start < 0 or end < start:
        raise AssertionError("talking-points section missing")
    return html[start:end]


def _visible_text(html: str) -> str:
    html = re.sub(r"(?is)<script\b[^>]*>.*?</script>", " ", html)
    html = re.sub(r"(?is)<style\b[^>]*>.*?</style>", " ", html)
    html = re.sub(r"(?is)<!--.*?-->", " ", html)
    html = re.sub(r"(?is)<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html)


if __name__ == "__main__":
    unittest.main()
