"""Commercial default is the headline price after aggregation ends."""

import json
import os
import unittest

import app as forge_app
import business_default

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WESTLAKE = (
    "Program ended June 2026, businesses now on CEI default 9.45¢, "
    "up 12.8% from Dynegy 8.38¢"
)
KNOWN_COMMERCIAL = {9.3786, 9.4503, 9.431, 9.806}


def _zone(name):
    matches = [zone for zone in forge_app._load_zones() if zone["name"] == name]
    if len(matches) != 1:
        raise AssertionError(f"{name}: {len(matches)} matches")
    return matches[0]


class BusinessDefaultTests(unittest.TestCase):
    def setUp(self):
        self.client = forge_app.app.test_client()

    def test_westlake_headlines_the_commercial_default_and_keeps_stored_rates(self):
        westlake = _zone("Westlake")
        self.assertIsNone(westlake["currentRate"])
        self.assertEqual(westlake["previousRate"], 8.38)
        info = westlake["businessDefault"]
        self.assertTrue(info["applies"])
        self.assertTrue(info["sourced"])
        self.assertEqual(info["cents"], 9.4503)
        self.assertEqual(info["code"], "CEI")
        self.assertEqual(info["priorCents"], 8.38)
        self.assertEqual(info["percent"], 12.8)
        self.assertEqual(info["percentText"], "+12.8%")
        self.assertEqual(info["headline"], WESTLAKE)
        self.assertEqual(info["caption"], "Local business default (generation only)")
        self.assertEqual(info["effectiveLabel"], "June 1, 2026")
        self.assertIn("firstenergycorp.com", info["sourceUrl"])
        self.assertEqual(info["tag"], "default")
        self.assertEqual(westlake["displayRateChange"], 12.8)
        self.assertEqual(westlake["rateDelta"]["source"], "commercial_default")
        self.assertEqual(westlake["rateDelta"]["baseline"], "last aggregation")
        self.assertEqual(westlake["rateDelta"]["cents"], 1.07)
        self.assertEqual(westlake["voice"]["currentText"], "9.4503¢")
        self.assertFalse(westlake["voice"]["currentPending"])
        self.assertEqual(westlake["card"]["hook"], WESTLAKE)
        self.assertEqual(westlake["card"]["takeaway"], WESTLAKE)
        self.assertIn("8.38", westlake["research"]["hook"])
        self.assertNotIn("11.24", westlake["research"]["hook"])
        self.assertEqual(westlake["card"]["ptc"]["cents_per_kwh"], 11.24)
        self.assertEqual(westlake["card"]["ptc"]["customer_class"], "residential")

        with open(os.path.join(ROOT, "data", "regions", "nopec_cuyahoga_suburbs.json"), encoding="utf-8") as handle:
            stored = next(row for row in json.load(handle) if row["name"] == "Westlake")
        self.assertIsNone(stored["currentRate"])
        self.assertEqual(stored["previousRate"], 8.38)
        self.assertIn("8.38", stored["hook"])
        self.assertNotIn("9.4503", stored["hook"])
        self.assertNotIn("11.24", stored["takeaway"])

    def test_card_table_and_weekly_lead_with_the_business_default(self):
        page = self.client.get("/card?file=nopec_cuyahoga_suburbs&name=Westlake").get_data(as_text=True)
        talk_at = page.find('id="what-to-talk-about"')
        default_at = page.find('id="business-default"')
        residential_at = page.find('id="ptc-residential"')
        headline_at = page.find('id="sales-headline"')
        self.assertTrue(0 <= talk_at < default_at < residential_at)
        self.assertGreater(headline_at, residential_at)
        self.assertIn(WESTLAKE, page[talk_at:default_at])
        current = page[default_at:residential_at]
        self.assertIn("9.4503", current)
        self.assertIn("Local business default (generation only)", current)
        self.assertIn("default-tag", current)
        self.assertIn("June 1, 2026", current)
        self.assertIn("firstenergycorp.com", current)
        self.assertIn("+12.8%", current)
        self.assertIn("last aggregation", current)
        self.assertNotIn("11.24", current)
        self.assertIn("11.24", page[residential_at:headline_at])
        self.assertIn(WESTLAKE, page[headline_at:])
        self.assertNotIn("residents default to CEI PTC 11.24", page)

        hotspots = self.client.get("/hotspots").get_data(as_text=True)
        self.assertIn("default-tag", hotspots)
        self.assertIn("bd.applies", hotspots)
        self.assertIn("businessDefault", hotspots)

        payload = self.client.get("/api/zones").get_json()
        row = next(zone for zone in payload if zone["name"] == "Westlake")
        self.assertEqual(row["businessDefault"]["percent"], 12.8)
        self.assertIsNone(row["currentRate"])
        self.assertEqual(row["displayRateChange"], 12.8)

        weekly = self.client.get("/weekly").get_data(as_text=True)
        self.assertIn(WESTLAKE, weekly)
        self.assertIn("default-tag", weekly)
        self.assertIn("+12.8%", weekly)

    def test_missing_commercial_rate_is_an_em_dash_and_active_programs_stay(self):
        blue_ash = _zone("Blue Ash")
        self.assertTrue(blue_ash["businessDefault"]["applies"])
        self.assertFalse(blue_ash["businessDefault"]["sourced"])
        self.assertIsNone(blue_ash["businessDefault"]["cents"])
        self.assertEqual(blue_ash["voice"]["currentText"], "—")
        self.assertNotIn("10.49", blue_ash["voice"]["hook"])
        self.assertIn("No sourced commercial default is on file", blue_ash["voice"]["hook"])
        page = self.client.get("/card?file=cincinnati_duke_suburbs&name=Blue%20Ash").get_data(as_text=True)
        block = page[page.find('id="business-default"'):page.find('id="ptc-residential"')]
        self.assertIn("—", block)
        self.assertNotIn("10.49¢", block)
        self.assertIn("10.49", page[page.find('id="ptc-residential"'):])

        salem = _zone("Salem")
        self.assertFalse(salem["businessDefault"]["applies"])
        self.assertEqual(salem["currentRate"], 9.79)
        self.assertEqual(salem["voice"]["currentText"], "9.79¢")

        kent = _zone("Kent / Portage County")
        self.assertFalse(kent["businessDefault"]["applies"])
        self.assertEqual(kent["displayRateChange"], 4.0)

        brookfield = _zone("Brookfield Township (Trumbull)")
        self.assertEqual(brookfield["businessDefault"]["cents"], 9.3786)
        self.assertEqual(brookfield["voice"]["currentText"], "9.3786¢")
        self.assertIsNone(brookfield["businessDefault"]["percent"])
        self.assertNotIn("11.07", brookfield["voice"]["currentText"])
        self.assertIn("OE default 9.38¢", brookfield["voice"]["hook"])

    def test_affected_zones_use_only_sourced_commercial_rates(self):
        zones = forge_app._load_zones()
        rows = business_default.affected_rows(zones)
        by_name = {row["name"]: row for row in rows}
        self.assertIn("Westlake", by_name)
        self.assertEqual(by_name["Westlake"]["percentText"], "+12.8%")
        self.assertNotIn("Salem", by_name)
        self.assertNotIn("Kent / Portage County", by_name)
        self.assertNotIn("Archbold", by_name)
        for row in rows:
            if row["cents"] is None:
                self.assertEqual(row["percentText"], "—")
                self.assertNotIn("¢", row["headline"].split("No sourced commercial default")[0][-12:])
                continue
            self.assertIn(row["cents"], KNOWN_COMMERCIAL)
            self.assertIn("default", row["headline"])
        priced = [row for row in rows if row["percent"] is not None]
        self.assertGreaterEqual(len(priced), 1)
        self.assertEqual(priced, sorted(priced, key=lambda row: -row["percent"]))


if __name__ == "__main__":
    unittest.main()
