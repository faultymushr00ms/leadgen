"""Market Increases page: sourced percents, flags, and battlecard links."""

import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import app as forge_app
import market_increases

PERCENT = re.compile(r"\d+(?:\.\d+)?%")


def _zone(name):
    zones = forge_app._load_zones()
    matches = [zone for zone in zones if zone["name"] == name]
    if len(matches) != 1:
        raise AssertionError(f"{name}: {len(matches)} matches")
    return matches[0]


class MarketIncreaseDataTests(unittest.TestCase):
    def setUp(self):
        market_increases.clear_cache()
        self.report = market_increases.load()

    def test_required_areas_and_quotes_render_from_figures(self):
        ids = [area["id"] for area in self.report["areas"]]
        self.assertEqual(list(market_increases.REQUIRED_AREAS), ids)
        for area in self.report["areas"]:
            self.assertTrue(area["quote"])
            self.assertTrue(area["figures"])
            published = " ".join(figure["percent_as_published"] for figure in area["figures"])
            for token in PERCENT.findall(area["quote"]):
                self.assertIn(token, published, area["id"])

    def test_every_figure_has_a_stated_percent_and_a_real_source(self):
        seen = set()
        for figure in self.report["figures"].values():
            seen.add(figure["id"])
            self.assertTrue(figure["percent_as_published"])
            self.assertTrue(figure["measure"])
            self.assertTrue(figure["utility"])
            self.assertTrue(figure["period_label"])
            self.assertGreaterEqual(len(figure["sources"]), 1)
            stated = [
                source for source in figure["sources"]
                if source.get("states_percent") and source.get("independent", True)
            ]
            self.assertEqual(figure["single_source"], len(stated) < 2)
            for source in figure["sources"]:
                self.assertTrue(source["title"])
                self.assertTrue(source["publisher"])
                self.assertTrue(source["date"])
                self.assertTrue(source["url"].startswith("http"))
        self.assertIn("te-ptc-35", seen)
        self.assertIn("aep-36", seen)
        self.assertIn("pjm-833", seen)

    def test_single_source_flags_follow_independent_publishers(self):
        figures = self.report["figures"]
        self.assertTrue(figures["te-ptc-35"]["single_source"])
        self.assertTrue(figures["cei-ptc-37"]["single_source"])
        self.assertTrue(figures["nopec-40"]["single_source"])
        self.assertTrue(figures["pjm-22"]["single_source"])
        self.assertTrue(figures["ohio-12"]["single_source"])
        self.assertTrue(figures["aes-7-5"]["single_source"])
        self.assertFalse(figures["aep-36"]["single_source"])
        self.assertFalse(figures["duke-30"]["single_source"])
        self.assertFalse(figures["duke-6"]["single_source"])
        self.assertFalse(figures["aes-15"]["single_source"])
        self.assertFalse(figures["pjm-833"]["single_source"])
        self.assertFalse(figures["pjm-bill"]["single_source"])

    def test_unpublished_rates_are_notes_without_a_computed_percent(self):
        by_id = {area["id"]: area for area in self.report["areas"]}
        dayton = " ".join(by_id["dayton"]["notes"])
        self.assertIn("0.0871", dayton)
        self.assertIn("0.10691", dayton)
        self.assertNotIn("%", dayton.split("https://")[0])
        cleveland = " ".join(by_id["greater-cleveland"]["notes"])
        self.assertIn("9.999", cleveland)
        self.assertIn("8.999", cleveland)
        self.assertNotRegex(cleveland, r"11(?:\.\d+)?%")
        columbus = " ".join(by_id["columbus"]["notes"])
        self.assertIn("11.162", columbus)
        self.assertNotIn("%", columbus.split("https://")[0])

    def test_area_matching_uses_utility_then_county(self):
        self.assertEqual(market_increases.match_area("Lucas", "Toledo Edison")["id"], "greater-toledo")
        self.assertEqual(market_increases.match_area("Cuyahoga", "The Illuminating Company")["id"], "greater-cleveland")
        self.assertEqual(market_increases.match_area("Franklin", "AEP Ohio")["id"], "columbus")
        self.assertEqual(market_increases.match_area("Hamilton", "Duke Energy Ohio")["id"], "cincinnati")
        self.assertEqual(market_increases.match_area("Warren", "AES Ohio")["id"], "dayton")
        self.assertEqual(market_increases.match_area("Summit", "Ohio Edison")["id"], "akron")
        self.assertEqual(market_increases.match_area("Mahoning", "Ohio Edison")["id"], "youngstown-warren")
        self.assertEqual(market_increases.match_area("Stark", "AEP Ohio")["id"], "canton-stark")
        self.assertEqual(market_increases.match_area("Stark", "Ohio Edison")["id"], "canton-stark")
        self.assertEqual(market_increases.match_area("Athens", "AEP Ohio")["id"], "ohio")
        self.assertEqual(market_increases.match_area("Clark", "Ohio Edison")["id"], "ohio")
        self.assertEqual(market_increases.match_area("", "")["id"], "ohio")


class MarketIncreasePageTests(unittest.TestCase):
    def setUp(self):
        market_increases.clear_cache()
        self.client = forge_app.app.test_client()

    def test_page_renders_quotes_sources_and_single_source_flag(self):
        response = self.client.get("/market-increases")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("MARKET INCREASES", html)
        self.assertIn("Greater Toledo: Toledo Edison’s default price to compare was up 35%", html)
        self.assertIn("The Illuminating Company’s default price to compare was up 37%", html)
        self.assertIn("833%", html)
        self.assertIn("Single source", html)
        self.assertIn("https://www.firstenergycorp.com/help/oh-understanding-rising-energy-supply-prices.html", html)
        self.assertIn("https://insidelines.pjm.com/pjm-auction-procures-134311-mw-of-generation-resources-supply-responds-to-price-signal/", html)
        self.assertIn('href="/market-increases"', html)
        self.assertIn('id="greater-toledo"', html)
        self.assertIn('id="ohio"', html)

    def test_battlecards_link_to_the_area_card(self):
        archbold = _zone("Archbold")
        self.assertEqual(archbold["card"]["marketArea"]["id"], "greater-toledo")
        self.assertEqual(archbold["card"]["marketArea"]["url"], "/market-increases#greater-toledo")
        card = self.client.get(archbold["card"]["url"])
        self.assertEqual(card.status_code, 200)
        self.assertIn("/market-increases#greater-toledo", card.get_data(as_text=True))

        zones = forge_app._load_zones()
        columbus = next(
            zone for zone in zones
            if (zone.get("research") or {}).get("county") == "Franklin"
            and "AEP" in ((zone.get("research") or {}).get("utility") or "")
            and zone.get("card")
        )
        self.assertEqual(columbus["card"]["marketArea"]["id"], "columbus")
        athens = next(
            zone for zone in zones
            if (zone.get("research") or {}).get("county") == "Athens" and zone.get("card")
        )
        self.assertEqual(athens["card"]["marketArea"]["id"], "ohio")
        athens_page = self.client.get(athens["card"]["url"])
        self.assertIn("/market-increases#ohio", athens_page.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
