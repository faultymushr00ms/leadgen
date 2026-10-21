"""Computed Δ% from currentRate and previousRate, and how zones sort."""

import os
import sys
import unittest
from itertools import groupby

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import app as forge_app
import rate_change


def _zone(name):
    matches = [zone for zone in forge_app._load_zones() if zone["name"] == name]
    if len(matches) != 1:
        raise AssertionError(f"{name}: {len(matches)} matches")
    return matches[0]


class PercentHelperTests(unittest.TestCase):
    def test_rounds_to_one_decimal(self):
        self.assertEqual(rate_change.percent_change(10.399, 7.0), 48.6)
        self.assertEqual(rate_change.percent_change(10.599, 7.0), 51.4)
        self.assertEqual(rate_change.percent_change(9.76, 6.96), 40.2)
        self.assertEqual(rate_change.percent_change(9, 10), -10.0)
        self.assertEqual(rate_change.percent_change(10, 10), 0.0)

    def test_missing_or_zero_previous_is_not_a_percent(self):
        self.assertIsNone(rate_change.percent_change(10, None))
        self.assertIsNone(rate_change.percent_change(None, 7))
        self.assertIsNone(rate_change.percent_change(10, 0))
        self.assertIsNone(rate_change.percent_change("", 7))

    def test_both_rates_win_over_a_stored_figure(self):
        zone = {
            "name": "Kent / Portage County",
            "currentRate": 10.399,
            "previousRate": 7.0,
            "rateChange": None,
            "supplier": "NOPEC",
            "region": "Akron / Summit County",
            "_source_file": "akron_summit_medina",
        }
        info = rate_change.describe(zone)
        self.assertEqual(info["percent"], 48.6)
        self.assertEqual(info["text"], "+48.6%")
        self.assertEqual(info["direction"], "up")
        self.assertEqual(info["source"], "computed")
        self.assertEqual(info["cents"], 3.399)
        self.assertTrue(info["previousRateNeedsCheck"])
        self.assertIsNone(zone["rateChange"])

    def test_stored_disagreement_is_ignored_for_display(self):
        zone = {
            "name": "Example",
            "currentRate": 12,
            "previousRate": 10,
            "rateChange": 5,
        }
        info = rate_change.describe(zone)
        self.assertEqual(info["percent"], 20.0)
        self.assertEqual(info["source"], "computed")
        self.assertEqual(info["stored"], 5.0)
        self.assertEqual(info["disagreement"], 15.0)
        self.assertEqual(zone["rateChange"], 5)

    def test_stored_rate_is_fallback_only_when_a_rate_is_missing(self):
        missing_current = {
            "name": "Sharonville",
            "currentRate": None,
            "previousRate": 9.39,
            "rateChange": 42.9,
        }
        info = rate_change.describe(missing_current)
        self.assertEqual(info["percent"], 42.9)
        self.assertEqual(info["text"], "+42.9%")
        self.assertEqual(info["source"], "stored")
        self.assertIsNone(info["computed"])
        self.assertIsNone(info["cents"])
        self.assertFalse(info["previousRateNeedsCheck"])

        missing_previous = {
            "name": "Dayton",
            "currentRate": 8.71,
            "previousRate": None,
            "rateChange": 22.7,
        }
        info = rate_change.describe(missing_previous)
        self.assertEqual(info["percent"], 22.7)
        self.assertEqual(info["source"], "stored")

        neither = {"name": "Empty", "currentRate": None, "previousRate": None, "rateChange": None}
        info = rate_change.describe(neither)
        self.assertIsNone(info["percent"])
        self.assertEqual(info["text"], "—")
        self.assertIsNone(info["direction"])

        zero_previous = {"name": "Zero", "currentRate": 10, "previousRate": 0, "rateChange": 4}
        info = rate_change.describe(zero_previous)
        self.assertIsNone(info["percent"])
        self.assertEqual(info["source"], None)

    def test_decrease_and_flat_signs(self):
        down = rate_change.describe({"currentRate": 8, "previousRate": 10, "rateChange": None})
        self.assertEqual(down["text"], "-20.0%")
        self.assertEqual(down["direction"], "down")
        flat = rate_change.describe({"currentRate": 9.5, "previousRate": 9.5, "rateChange": 12})
        self.assertEqual(flat["text"], "0.0%")
        self.assertEqual(flat["direction"], "flat")
        self.assertEqual(flat["source"], "computed")

    def test_placeholder_priors_are_flagged_and_other_sevens_are_not(self):
        nopec = {"name": "Avon", "previousRate": 7.0, "supplier": "NOPEC", "region": "Lorain County (NOPEC)"}
        self.assertEqual(rate_change.prior_check_reason(nopec), "nopec_prior_7.0")
        other = {"name": "Somewhere", "previousRate": 7.0, "supplier": "Dynegy", "region": "Dayton"}
        self.assertIsNone(rate_change.prior_check_reason(other))
        mahoning = {
            "name": "Springfield Township (Mahoning)",
            "previousRate": 7.9,
            "notes": "NOPEC electric member. There is no Mahoning County Dynegy program.",
        }
        self.assertEqual(rate_change.prior_check_reason(mahoning), "mahoning_township_prior_7.9")
        coitsville = {
            "name": "Coitsville Township",
            "previousRate": 7.9,
            "notes": "NOPEC electric member. There is no Mahoning County Dynegy program.",
        }
        self.assertTrue(rate_change.previous_rate_needs_check(coitsville))
        trumbull = {
            "name": "Howland Township",
            "previousRate": 7.9,
            "region": "Youngstown / Warren",
            "notes": "Part of Trumbull County aggregation. Previous county rate ~7.90¢.",
        }
        self.assertFalse(rate_change.previous_rate_needs_check(trumbull))
        county = {"name": "Mahoning County", "previousRate": 7.9, "region": "Youngstown / Warren"}
        self.assertFalse(rate_change.previous_rate_needs_check(county))
        near = {"name": "Alliance", "previousRate": 7.965, "supplier": "NOPEC"}
        self.assertFalse(rate_change.previous_rate_needs_check(near))

    def test_disagreement_report_uses_a_half_point_cutoff(self):
        wide = {"name": "Wide", "currentRate": 10, "previousRate": 8, "rateChange": 10, "_source_file": "demo"}
        close = {"name": "Close", "currentRate": 10, "previousRate": 8, "rateChange": 25.4, "_source_file": "demo"}
        edge = {"name": "Edge", "currentRate": 10, "previousRate": 8, "rateChange": 25.5, "_source_file": "demo"}
        over = {"name": "Over", "currentRate": 10, "previousRate": 8, "rateChange": 25.6, "_source_file": "demo"}
        rows = rate_change.disagreement_rows([wide, close, edge, over])
        self.assertEqual([row["name"] for row in rows], ["Wide", "Over"])
        report = rate_change.disagreement_report([close])
        self.assertIn("None.", report.split("previousRateNeedsCheck")[0])
        self.assertNotIn("Close", report.split("previousRateNeedsCheck")[0])

    def test_matching_clause_uses_the_computed_percent_only(self):
        zone = {"currentRate": 9.76, "previousRate": 6.96, "rateChange": 1}
        self.assertEqual(
            rate_change.matching_percent_clause(zone, "6.96", "9.76"),
            ", +40.2% versus the current rate",
        )
        self.assertEqual(rate_change.matching_percent_clause(zone, "8.00", "9.76"), "")
        fallback = {"currentRate": None, "previousRate": 6.96, "rateChange": 40.2}
        self.assertEqual(rate_change.matching_percent_clause(fallback, "6.96", None), "")


class SortTests(unittest.TestCase):
    def test_missing_percent_sorts_after_decreases_not_as_zero(self):
        zones = [
            {"name": "Down", "status": "pain_hit", "currentRate": 9, "previousRate": 10, "rateChange": 0},
            {"name": "Flat", "status": "pain_hit", "currentRate": 10, "previousRate": 10, "rateChange": 50},
            {"name": "Missing", "status": "pain_hit", "currentRate": 10, "previousRate": None, "rateChange": None},
            {"name": "Fallback", "status": "pain_hit", "currentRate": None, "previousRate": 5, "rateChange": 3},
            {"name": "Later status", "status": "stable", "currentRate": 20, "previousRate": 10, "rateChange": None},
        ]
        rate_change.annotate_zones(zones)
        zones.sort(key=lambda zone: rate_change.sort_key(zone, {"pain_hit": 2, "stable": 7}))
        self.assertEqual(
            [zone["name"] for zone in zones],
            ["Fallback", "Flat", "Down", "Missing", "Later status"],
        )
        missing_key = rate_change.percent_sort_key(zones[3])
        zero_key = rate_change.percent_sort_key(next(zone for zone in zones if zone["name"] == "Flat"))
        self.assertNotEqual(missing_key, zero_key)
        self.assertGreater(missing_key, zero_key)

    def test_loaded_zones_keep_stored_rate_and_compute_kent(self):
        kent = _zone("Kent / Portage County")
        self.assertEqual(kent["currentRate"], 10.399)
        self.assertEqual(kent["previousRate"], 7.0)
        self.assertIsNone(kent["rateChange"])
        self.assertEqual(kent["displayRateChange"], 48.6)
        self.assertEqual(kent["rateDelta"]["text"], "+48.6%")
        self.assertTrue(kent["previousRateNeedsCheck"])
        self.assertEqual(kent["card"]["rateDelta"]["percent"], 48.6)

        dayton = _zone("Dayton")
        self.assertIsNone(dayton["previousRate"])
        self.assertEqual(dayton["rateChange"], 22.7)
        self.assertEqual(dayton["displayRateChange"], 22.7)
        self.assertEqual(dayton["rateDelta"]["source"], "stored")
        self.assertFalse(dayton["previousRateNeedsCheck"])

        swanton = _zone("Swanton")
        self.assertEqual(swanton["rateChange"], 40.2)
        self.assertEqual(swanton["displayRateChange"], 40.2)

    def test_loaded_order_puts_blank_percents_last_inside_each_status(self):
        zones = forge_app._load_zones()
        for _status, group in groupby(zones, key=lambda zone: zone.get("status")):
            group = list(group)
            percents = [zone.get("displayRateChange") for zone in group]
            numbers = [percent for percent in percents if percent is not None]
            self.assertEqual(numbers, sorted(numbers, reverse=True))
            if None in percents:
                first_blank = percents.index(None)
                self.assertTrue(all(percent is None for percent in percents[first_blank:]))
                if numbers:
                    self.assertLess(first_blank, len(percents))

    def test_placeholder_flags_on_loaded_zones(self):
        zones = forge_app._load_zones()
        flagged = rate_change.flagged_prior_rows(zones)
        names = [row["name"] for row in flagged]
        self.assertEqual(len(flagged), 57)
        self.assertEqual(names.count("Kent / Portage County"), 1)
        self.assertIn("Coitsville Township", names)
        self.assertIn("Springfield Township (Mahoning)", names)
        self.assertIn("Jackson Township (Mahoning)", names)
        self.assertNotIn("Howland Township", names)
        self.assertNotIn("Mahoning County", names)
        self.assertNotIn("Trumbull County", names)
        reasons = {row["reason"] for row in flagged}
        self.assertEqual(reasons, {"nopec_prior_7.0", "mahoning_township_prior_7.9"})
        self.assertEqual(sum(1 for row in flagged if row["reason"] == "nopec_prior_7.0"), 54)
        self.assertEqual(sum(1 for row in flagged if row["reason"] == "mahoning_township_prior_7.9"), 3)
        report = rate_change.disagreement_report(zones)
        self.assertIn("\nNone.\n", report)
        self.assertIn("Kent / Portage County", report)
        path = os.path.join(ROOT, "data", "reports", "rate_change_disagreements.md")
        with open(path, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), report)

    def test_pages_show_signed_percent_and_unverified_prior(self):
        client = forge_app.app.test_client()
        hotspots = client.get("/hotspots").get_data(as_text=True)
        self.assertIn("displayRateChange", hotspots)
        self.assertIn("unverified prior rate", hotspots)
        self.assertIn("+48.6%", hotspots)

        weekly = client.get("/weekly").get_data(as_text=True)
        self.assertIn("+48.6%", weekly)
        self.assertIn("rate-pct-up", weekly)
        self.assertIn("unverified prior rate", weekly)
        self.assertIn("rate-pct-down", weekly)

        card = client.get("/card?file=akron_summit_medina&name=Kent / Portage County").get_data(as_text=True)
        self.assertIn("+48.6%", card)
        self.assertIn("delta-up", card)
        self.assertIn("unverified prior rate", card)

        api = client.get("/api/zones").get_json()
        kent = next(zone for zone in api if zone["name"] == "Kent / Portage County")
        self.assertEqual(kent["displayRateChange"], 48.6)
        self.assertIsNone(kent["rateChange"])


if __name__ == "__main__":
    unittest.main()
