"""
Agent 1: Ohio Scraper
Pulls raw business leads from all configured sources, deduplicates them,
and saves a JSON file for Agent 2 (qualifier) to process.

Usage:
    python -m scraper.ohio_scraper
"""

import json
import os
from datetime import datetime
from typing import List
from dotenv import load_dotenv

from .sources.base import RawLead
from .sources.overpass import OverpassSource
from .sources.epa_echo import EPAEchoSource
from .sources.google_maps import GoogleMapsSource

load_dotenv()

OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "raw_leads_{date}.json")


def run_scraper() -> List[RawLead]:
    sources = [
        OverpassSource(),
        EPAEchoSource(),
        GoogleMapsSource(),  # silent no-op if no API key
    ]

    # index maps dedup_key → position in all_leads for fast merge lookups
    all_leads: List[RawLead] = []
    index: dict[str, int] = {}

    print("\n=== Agent 1: Ohio Scraper ===")
    print(f"Running {len(sources)} sources...\n")

    for source in sources:
        try:
            leads = source.fetch()
            new_count = 0
            merged_count = 0

            for lead in leads:
                # Tag which source this record came from
                lead.confirmed_by = [lead.source]
                key = lead.dedup_key()

                if key not in index:
                    # First time seeing this business — add it
                    index[key] = len(all_leads)
                    all_leads.append(lead)
                    new_count += 1
                else:
                    # Already have this business from another source — merge data in
                    all_leads[index[key]].merge(lead)
                    merged_count += 1

            print(f"  [{source.name}] {new_count} new | {merged_count} cross-referenced.\n")
        except Exception as e:
            print(f"  [{source.name}] Unexpected error: {e}\n")

    return all_leads


def save_leads(leads: List[RawLead]) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    path = OUTPUT_FILE.format(date=date_str)

    output = {
        "scraped_at": datetime.now().isoformat(),
        "total_leads": len(leads),
        "leads": [lead.__dict__ for lead in leads],
    }

    with open(path, "w") as f:
        json.dump(output, f, indent=2)

    return path


def print_summary(leads: List[RawLead]):
    from collections import Counter
    sources = Counter(lead.source for lead in leads)
    industries = Counter(lead.industry for lead in leads)
    confidence = Counter(lead.confidence for lead in leads)

    print("=" * 50)
    print(f"SCRAPE COMPLETE — {len(leads)} total unique leads")
    print("=" * 50)

    print("\nConfidence breakdown (cross-reference check):")
    for level in ["HIGH", "MEDIUM", "LOW"]:
        count = confidence.get(level, 0)
        bar = "█" * (count // 5)
        print(f"  {level:<8} {count:>4}  {bar}")

    print("\nBy source:")
    for source, count in sources.most_common():
        print(f"  {source:<20} {count}")

    print("\nTop industries:")
    for industry, count in industries.most_common(10):
        print(f"  {industry:<30} {count}")


if __name__ == "__main__":
    leads = run_scraper()
    path = save_leads(leads)
    print_summary(leads)
    print(f"\nSaved to: {path}")
    print("Ready for Agent 2 (qualifier).")
