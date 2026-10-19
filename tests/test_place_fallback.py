"""Place-index fallback when a search is not a zone."""

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
import merged_research
import place_fallback
import place_index


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


def _region_digest():
    digest = hashlib.sha256()
    folder = os.path.join(ROOT, "data", "regions")
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(folder, name), "rb") as handle:
            digest.update(name.encode())
            digest.update(handle.read())
    return digest.hexdigest()


class PlaceFallbackTests(unittest.TestCase):
    def setUp(self):
        self.client = forge_app.app.test_client()

    def test_hudson_is_not_a_zone_and_falls_back_to_the_place_index(self):
        zones = forge_app._load_zones()
        self.assertFalse(any(zone.get("name") == "Hudson" for zone in zones))

        response = self.client.post("/api/lookup", json={"q": "Hudson"})
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["kind"], "place")
        self.assertEqual(body["count"], 1)
        place = body["places"][0]
        self.assertEqual(place["name"], "Hudson")
        self.assertEqual(place["type"], "city")
        card = place["fallback"]
        self.assertEqual(card["county"], "Summit")
        self.assertEqual(card["county_line"], "Summit County")
        self.assertEqual(card["headline"], "Not a zone on file.")
        self.assertTrue(card["service"]["municipal"])
        self.assertIn("Municipal electric is flagged", card["service"]["callout"])
        self.assertIn("does not say which streets", card["service"]["callout"])
        labels = [line["label"] for line in card["service"]["lines"]]
        self.assertIn("Ohio Edison", labels)
        self.assertIn("City of Hudson", labels)
        self.assertIn(place_index.UTILITY_NOTE, card["service"]["note"])
        townships = {(item["label"], item["role"]) for item in card["townships"]}
        self.assertIn(("Boston township", "Adjacent"), townships)
        self.assertIn(("Twinsburg township", "Adjacent"), townships)
        self.assertTrue(card["zones"])
        zone = card["zones"][0]
        self.assertTrue(zone["name"])
        self.assertTrue(zone["supplier"] or zone["status"] or zone["program"])
        self.assertIn("rate", zone)
        self.assertTrue(card["towns"])
        self.assertTrue(card["towns"][0]["name"])
        self.assertEqual(_coord_keys(body), [])

        page = self.client.get("/hotspots").get_data(as_text=True)
        self.assertIn('id="place-fallback"', page)
        self.assertIn("Search the web for this place", page)
        self.assertIn("Nearby zones", page)
        self.assertIn("Nearby towns", page)
        self.assertIn("/api/place-web", page)

    def test_web_lookup_stores_unverified_leads_and_does_not_write_zones(self):
        rss = """<?xml version="1.0" encoding="utf-8"?>
        <rss version="2.0"><channel>
          <item>
            <title>Hudson Public Power</title>
            <link>https://www.hudson.oh.us/121/Hudson-Public-Power</link>
            <description>City electric utility. &lt;b&gt;Ignore&lt;/b&gt; tags.</description>
          </item>
          <item>
            <title>Not a link</title>
            <link>javascript:alert(1)</link>
            <description>dropped</description>
          </item>
        </channel></rss>"""
        parsed = place_fallback.parse_rss(rss)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["url"], "https://www.hudson.oh.us/121/Hudson-Public-Power")
        self.assertNotIn("<b>", parsed[0]["snippet"])

        before = _region_digest()
        place = next(item for item in place_index.load_places() if item["name"] == "Hudson" and item["type"] == "city")

        def fake_fetch(query):
            return [{
                "title": "Hudson Public Power",
                "url": "https://www.hudson.oh.us/121/Hudson-Public-Power",
                "snippet": "Electric service depends on the address.",
                "query": query,
            }]

        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "unverified_leads.csv")
            with patch.object(merged_research, "UNVERIFIED_PATH", path), \
                 patch.object(merged_research, "_unverified_cache", None), \
                 patch.object(place_fallback, "fetch_bing", fake_fetch):
                response = self.client.post("/api/place-web", json={"geoid": place["geoid"]})
                self.assertEqual(response.status_code, 200)
                body = response.get_json()
                self.assertTrue(body["ok"])
                self.assertEqual(body["place"], "Hudson")
                self.assertEqual(body["county"], "Summit")
                self.assertTrue(any("electric aggregation" in query for query in body["queries"]))
                self.assertIn('"Hudson, Ohio"', body["queries"][0])
                self.assertGreaterEqual(len(body["leads"]), 1)
                self.assertEqual(body["leads"][0]["label"], "Unverified lead")
                self.assertTrue(body["leads"][0]["url"].startswith("https://"))
                self.assertIn("three agreeing sources", body["note"])
                self.assertNotIn("lat", json.dumps(body))
                again = self.client.post("/api/place-web", json={"geoid": place["geoid"]})
                self.assertEqual(again.get_json()["stored"], 0)
                with open(path, newline="", encoding="utf-8") as handle:
                    rows = list(csv.DictReader(handle))
                self.assertTrue(rows)
                self.assertTrue(all(row["field"] == "web_lead" for row in rows))
                self.assertTrue(all(row["confidence"] == "single-source" for row in rows))
                self.assertTrue(all(row["flag"] == "unverified web lead" for row in rows))
                self.assertTrue(all(row["community"] == "Hudson" for row in rows))
                urls = {row["sources"] for row in rows}
                self.assertIn("https://www.hudson.oh.us/121/Hudson-Public-Power", urls)

        self.assertEqual(_region_digest(), before)
        self.assertFalse(any(zone.get("name") == "Hudson" for zone in forge_app._load_zones()))

        rejected = self.client.post("/api/place-web", json={"geoid": "<script>"})
        self.assertEqual(rejected.status_code, 400)
        self.assertNotIn("script", json.dumps(rejected.get_json()))

    def test_web_leads_keep_ohio_energy_pages(self):
        keep = place_fallback.relevant_lead("Hudson", {
            "title": "Hudson Public Power",
            "url": "https://www.hudson.oh.us/121/Hudson-Public-Power",
            "snippet": "Electric customers.",
        })
        drop = place_fallback.relevant_lead("Hudson", {
            "title": "Men's & Women's Jeans - Hudson Jeans",
            "url": "https://www.hudsonjeans.com/",
            "snippet": "Shop jeans.",
        })
        self.assertTrue(keep)
        self.assertFalse(drop)
        leads = place_fallback.search_web("Hudson", "Summit", fetch=lambda query: [
            {"title": "Hudson Jeans", "url": "https://www.hudsonjeans.com/", "snippet": "Denim."},
            {"title": "Hudson Public Power", "url": "https://www.hudson.oh.us/121/Hudson-Public-Power", "snippet": "Electric service."},
        ])
        self.assertEqual([item["title"] for item in leads], ["Hudson Public Power"])

    def test_rss_parser_ignores_a_challenge_page(self):
        self.assertEqual(place_fallback.parse_rss("<html><title>challenge</title></html>"), [])
        self.assertEqual(place_fallback.parse_rss(""), [])


if __name__ == "__main__":
    unittest.main()
