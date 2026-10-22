"""Map overlap chooser: one click lists every community polygon under the point."""

import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import app as forge_app


class ZoneChooserTests(unittest.TestCase):
    def setUp(self):
        self.client = forge_app.app.test_client()

    def test_map_keeps_single_clicks_and_offers_a_chooser(self):
        page = self.client.get("/map").get_data(as_text=True)
        self.assertIn("/static/zone_chooser.js", page)
        self.assertIn("zone-chooser", page)
        self.assertIn("zones here", page)
        self.assertIn("chooseAction(hits) === 'open'", page)
        self.assertIn("openPopup(event.latlng)", page)
        self.assertIn("Escape", page)
        script = self.client.get("/static/zone_chooser.js")
        self.assertEqual(script.status_code, 200)
        body = script.get_data(as_text=True)
        script.close()
        self.assertIn("featuresAtPoint", body)
        self.assertIn("describeHit", body)

    def test_chooser_rules(self):
        result = subprocess.run(
            ["node", "--test", os.path.join(ROOT, "tests", "zone_chooser.test.js")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)


if __name__ == "__main__":
    unittest.main()
