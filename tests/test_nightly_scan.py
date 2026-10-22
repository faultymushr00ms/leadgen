"""Tests for nightly scan components: region filter, change detection, report writing."""

import hashlib
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


# ── Region filter tests ───────────────────────────────────────────────────────

class TestRegionFilter(unittest.TestCase):

    def _make_zone(self, name, source_file, region=""):
        return {"name": name, "_source_file": source_file, "region": region}

    def test_ne_ohio_preset_includes_correct_files(self):
        from run_refresh import _filter_zones, NE_OHIO_FILES
        zones = [
            self._make_zone("Parma", "nopec_cuyahoga_suburbs"),
            self._make_zone("Akron", "akron_summit_medina"),
            self._make_zone("Cincinnati", "cincinnati_duke"),
            self._make_zone("Dayton", "dayton_sw_ohio"),
        ]
        result = _filter_zones(zones, "ne_ohio")
        names = [z["name"] for z in result]
        self.assertIn("Parma", names)
        self.assertIn("Akron", names)
        self.assertNotIn("Cincinnati", names)
        self.assertNotIn("Dayton", names)

    def test_no_region_returns_all(self):
        from run_refresh import _filter_zones
        zones = [
            self._make_zone("Parma", "nopec_cuyahoga_suburbs"),
            self._make_zone("Cincinnati", "cincinnati_duke"),
        ]
        result = _filter_zones(zones, None)
        self.assertEqual(len(result), 2)

    def test_region_string_filters_by_name_substring(self):
        from run_refresh import _filter_zones
        zones = [
            self._make_zone("Parma", "nopec_cuyahoga_suburbs", "NE Ohio / Cuyahoga"),
            self._make_zone("Cincinnati", "cincinnati_duke", "SW Ohio / Hamilton"),
        ]
        result = _filter_zones(zones, "Cuyahoga")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Parma")

    def test_ne_ohio_excludes_sw_ohio_files(self):
        from run_refresh import _filter_zones
        sw_files = ["cincinnati_duke", "cincinnati_duke_suburbs", "dayton_sw_ohio",
                    "dayton_aes_suburbs", "toledo_lucas_noac"]
        zones = [self._make_zone(f, f) for f in sw_files]
        result = _filter_zones(zones, "ne_ohio")
        self.assertEqual(result, [])


# ── Change detection tests ────────────────────────────────────────────────────

class TestChangeDetector(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.hash_store = os.path.join(self.tmp, "page_hashes.json")

    def _patch_store(self):
        import scraper.change_detector as cd
        cd.HASH_STORE = self.hash_store
        return cd

    def test_same_content_not_changed(self):
        cd = self._patch_store()
        content = "<html>rate is 9.999¢</html>"
        h = hashlib.sha256(content.encode()).hexdigest()[:16]
        with open(self.hash_store, "w") as f:
            json.dump({"http://example.com": h}, f)

        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(status_code=200, text=content)
            mock_get.return_value.raise_for_status = lambda: None
            result = cd.fetch_and_detect("TestZone", "http://example.com", use_ollama=False)

        self.assertFalse(result["changed"])
        self.assertIsNone(result["error"])

    def test_changed_content_flagged(self):
        cd = self._patch_store()
        old_content = "<html>rate is 8.999¢</html>"
        new_content = "<html>rate is 9.999¢</html>"
        old_hash = hashlib.sha256(old_content.encode()).hexdigest()[:16]
        with open(self.hash_store, "w") as f:
            json.dump({"http://example.com": old_hash}, f)

        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(status_code=200, text=new_content)
            mock_get.return_value.raise_for_status = lambda: None
            result = cd.fetch_and_detect("TestZone", "http://example.com", use_ollama=False)

        self.assertTrue(result["changed"])
        self.assertIn(9.999, result["extracted"]["rates_found"])

    def test_no_url_skipped(self):
        cd = self._patch_store()
        result = cd.fetch_and_detect("TestZone", "", use_ollama=False)
        self.assertTrue(result["skipped"])

    def test_extract_rates(self):
        cd = self._patch_store()
        text = "Current rate: 9.999¢/kWh. Previous rate was 8.999c."
        extracted = cd._extract(text)
        self.assertIn(9.999, extracted["rates_found"])
        self.assertIn(8.999, extracted["rates_found"])

    def test_extract_ignores_out_of_range(self):
        cd = self._patch_store()
        text = "1.5¢ and 99.9¢ should be ignored. 10.5¢ is valid."
        extracted = cd._extract(text)
        self.assertNotIn(1.5, extracted["rates_found"])
        self.assertNotIn(99.9, extracted["rates_found"])
        self.assertIn(10.5, extracted["rates_found"])

    def test_extract_supplier_names(self):
        cd = self._patch_store()
        text = "Supplied by Dynegy through the city program. Constellation also bids."
        extracted = cd._extract(text)
        suppliers = [s.lower() for s in extracted["suppliers_found"]]
        self.assertIn("dynegy", suppliers)
        self.assertIn("constellation", suppliers)


# ── Report writing tests ──────────────────────────────────────────────────────

class TestReportWriting(unittest.TestCase):

    def _write_report(self, added_items, tmp_dir):
        """Simulate what nightly_scan.sh's inline Python does."""
        today = "2026-10-22"
        report_file = os.path.join(tmp_dir, f"scan_{today}.md")

        refresh_data = {
            "added": added_items,
            "zones_loaded": 42,
            "observations": 5,
            "diffs_found": len(added_items),
        }
        refresh_json = os.path.join(tmp_dir, f"refresh_report_{today}.json")
        with open(refresh_json, "w") as f:
            json.dump(refresh_data, f)

        lines = [f"# FORGE Scan Report — {today}", ""]
        if added_items:
            lines.append("## Changes Detected")
            lines.append("")
            for item in added_items:
                zone = item.get("zone", "?")
                field = item.get("field", "?")
                old = item.get("stored_value", "?")
                new = item.get("observed_value", "?")
                url = item.get("source_url", "")
                lines.append(f"- **{zone}** — {field}: {old!r} → {new!r}")
                if url:
                    lines.append(f"  Source: {url}")
            lines.append("")
        else:
            lines.append("## No changes detected")
            lines.append("")
        lines.append(f"Zones scanned: 42 | Observations: 5 | Diffs: {len(added_items)}")
        lines.append(f"\nLog: logs/scan_{today}.log")

        with open(report_file, "w") as f:
            f.write("\n".join(lines) + "\n")
        return report_file

    def test_no_changes_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_report([], tmp)
            content = open(path).read()
            self.assertIn("No changes detected", content)
            self.assertNotIn("Changes Detected", content)

    def test_changes_in_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            items = [{
                "zone": "Parma",
                "field": "currentRate",
                "stored_value": "9.999",
                "observed_value": "10.599",
                "source_url": "https://nopec.org/communities",
            }]
            path = self._write_report(items, tmp)
            content = open(path).read()
            self.assertIn("Parma", content)
            self.assertIn("currentRate", content)
            self.assertIn("nopec.org", content)
            self.assertIn("Changes Detected", content)

    def test_report_file_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_report([], tmp)
            self.assertTrue(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()
