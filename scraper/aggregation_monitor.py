"""
Ohio Aggregation Monitor — runs once daily via cron or python run_monitor.py
Scrapes public supplier/broker pages for Ohio municipal aggregation programs,
compares against the zones DB, and writes a diff report.

Sources scraped (no API key required):
  - Dynegy Ohio community list
  - Energy Alliances community pages
  - NOPEC member list
  - SOPEC member list
  - NOAC member list
  - Constellation Ohio aggregation index

Output: output/agg_monitor_YYYYMMDD.json
"""

import json
import os
import re
import time
from datetime import date, datetime
from difflib import SequenceMatcher
from typing import Optional

import requests
from bs4 import BeautifulSoup

OUTPUT_DIR = "output"
REGIONS_DIR = os.path.join("data", "regions")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
TIMEOUT = 25

# ── Sources ────────────────────────────────────────────────────────────────────

SOURCES = [
    {
        "name": "Dynegy Ohio",
        "url": "https://www.dynegy.com/municipal-aggregation/communities-we-serve/Ohio",
        "type": "dynegy",
        "fallback_url": "https://www.vistraenergy.com/community-aggregation",
    },
    {
        "name": "Energy Alliances",
        "url": "https://energyalliances.com/",
        "type": "energy_alliances",
    },
    {
        "name": "NOPEC Communities",
        "url": "https://www.nopec.org/communities",
        "type": "nopec",
        "fallback_url": "https://www.nopec.org/about-nopec/nopec-communities/",
    },
    {
        "name": "SOPEC Communities",
        "url": "https://sopec-oa.com/member-communities",
        "type": "sopec",
        "fallback_url": "https://sopec-oa.com/",
    },
    {
        "name": "NOAC Toledo",
        "url": "https://nwohioaggregation.com/",
        "type": "noac",
    },
    {
        "name": "Constellation Ohio",
        "url": "https://home.constellation.com/Government-Aggregation/Ohio",
        "type": "constellation",
        "fallback_url": "https://www.constellation.com/solutions/for-your-home/electricity/government-aggregation/ohio.html",
    },
    {
        "name": "IGS Ohio Aggregation",
        "url": "https://www.igsenergy.com/ohio-aggregation",
        "type": "generic_igs",
    },
]


# ── Scrapers ───────────────────────────────────────────────────────────────────

def _get(url: str) -> Optional[BeautifulSoup]:
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  [monitor] fetch failed {url}: {e}")
        return None


def scrape_dynegy(url: str) -> list[dict]:
    """Dynegy lists Ohio communities in a grid of cards or links."""
    soup = _get(url)
    if not soup:
        return []
    communities = []
    # Dynegy community pages: each community is typically a link with city name
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/municipal-aggregation/communities-we-serve/ohio/" in href.lower():
            name = a.get_text(strip=True)
            if name and len(name) > 2:
                communities.append({"name": name, "supplier": "Dynegy", "source_url": href})
    # Deduplicate
    seen = set()
    result = []
    for c in communities:
        k = c["name"].lower()
        if k not in seen:
            seen.add(k)
            result.append(c)
    return result


def scrape_energy_alliances(url: str) -> list[dict]:
    """Energy Alliances lists Ohio communities they broker for."""
    soup = _get(url)
    if not soup:
        return []
    communities = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "energyalliances.com/" in href and href != url:
            name = a.get_text(strip=True)
            # Filter out nav/footer links
            if name and 3 < len(name) < 60 and not any(
                skip in name.lower()
                for skip in ["home", "about", "contact", "blog", "news", "privacy", "services"]
            ):
                communities.append({"name": name, "supplier": "Energy Alliances (Dynegy)", "source_url": href})
    seen = set()
    result = []
    for c in communities:
        k = c["name"].lower()
        if k not in seen:
            seen.add(k)
            result.append(c)
    return result


def scrape_nopec(url: str) -> list[dict]:
    """NOPEC lists member communities."""
    soup = _get(url)
    if not soup:
        return []
    communities = []
    # NOPEC typically lists communities in a table or list
    for el in soup.find_all(["li", "td", "p"]):
        text = el.get_text(strip=True)
        # Filter: reasonable city name length, no sentence fragments
        if 3 < len(text) < 50 and re.match(r'^[A-Z][a-zA-Z\s\.\-\/]+$', text):
            communities.append({"name": text, "supplier": "NOPEC (NextEra)", "source_url": url})
    seen = set()
    result = []
    for c in communities:
        k = c["name"].lower()
        if k not in seen:
            seen.add(k)
            result.append(c)
    return result


def scrape_generic(url: str, supplier_label: str) -> list[dict]:
    """Generic scraper — extracts plausible Ohio city names from page text."""
    soup = _get(url)
    if not soup:
        return []
    communities = []
    for el in soup.find_all(["li", "td", "h3", "h4", "p", "a"]):
        text = el.get_text(strip=True)
        if 3 < len(text) < 50 and re.match(r'^[A-Z][a-zA-Z\s\.\-\/\(\)]+$', text):
            communities.append({"name": text, "supplier": supplier_label, "source_url": url})
    seen = set()
    result = []
    for c in communities:
        k = c["name"].lower()
        if k not in seen:
            seen.add(k)
            result.append(c)
    return result


SCRAPER_MAP = {
    "dynegy": scrape_dynegy,
    "energy_alliances": scrape_energy_alliances,
    "nopec": scrape_nopec,
    "sopec": lambda url: scrape_generic(url, "SOPEC"),
    "noac": lambda url: scrape_generic(url, "NOAC (Dynegy)"),
    "constellation": lambda url: scrape_generic(url, "Constellation"),
    "generic_igs": lambda url: scrape_generic(url, "IGS Energy"),
}


# ── DB loader ──────────────────────────────────────────────────────────────────

def _load_db_zones() -> dict[str, dict]:
    """Return all zones keyed by lowercase name."""
    zones = {}
    if not os.path.exists(REGIONS_DIR):
        return zones
    for fname in os.listdir(REGIONS_DIR):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(REGIONS_DIR, fname)) as f:
            file_zones = json.load(f)
        for z in file_zones:
            zones[z["name"].lower().strip()] = z
    return zones


# ── Matching ───────────────────────────────────────────────────────────────────

def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _find_db_match(name: str, db_zones: dict) -> Optional[str]:
    """Return the DB key of the best fuzzy match, or None if no good match."""
    name_lower = name.lower().strip()
    # Exact match
    if name_lower in db_zones:
        return name_lower
    # Remove common suffixes for comparison
    stripped = re.sub(r'\s*(township|twp|city|village|county|area)\s*$', '', name_lower).strip()
    if stripped in db_zones:
        return stripped
    # Fuzzy match
    best_score = 0.0
    best_key = None
    for key in db_zones:
        score = _similarity(name_lower, key)
        if score > best_score:
            best_score = score
            best_key = key
    if best_score >= 0.82:
        return best_key
    return None


# ── Main ───────────────────────────────────────────────────────────────────────

def run_monitor() -> dict:
    today_str = date.today().isoformat()
    print(f"\n[AggMonitor] {today_str} — scanning {len(SOURCES)} sources...")

    db_zones = _load_db_zones()
    print(f"[AggMonitor] DB: {len(db_zones)} zones loaded")

    found_communities: list[dict] = []
    source_results: dict[str, int] = {}

    for source in SOURCES:
        print(f"  Scraping: {source['name']}...")
        scraper = SCRAPER_MAP.get(source["type"])
        if not scraper:
            continue
        communities = scraper(source["url"])
        # Try fallback URL if primary returned nothing
        if not communities and source.get("fallback_url"):
            print(f"    primary blocked, trying fallback...")
            communities = scraper(source["fallback_url"])
        source_results[source["name"]] = len(communities)
        print(f"    → {len(communities)} communities found")
        for c in communities:
            c["scraped_from"] = source["name"]
        found_communities.extend(communities)
        time.sleep(1.5)  # polite delay

    # ── Diff against DB ────────────────────────────────────────────────────────
    new_communities = []      # scraped but NOT in DB
    matched_communities = []  # scraped AND in DB

    seen_new = set()
    for c in found_communities:
        db_key = _find_db_match(c["name"], db_zones)
        if db_key:
            matched_communities.append({**c, "db_key": db_key,
                                        "db_status": db_zones[db_key].get("status"),
                                        "db_rate": db_zones[db_key].get("currentRate")})
        else:
            k = c["name"].lower()
            if k not in seen_new:
                seen_new.add(k)
                new_communities.append(c)

    # ── DB zones NOT seen in any scrape (potential stale/dissolved programs) ──
    matched_keys = {_find_db_match(c["name"], db_zones) for c in found_communities}
    matched_keys.discard(None)
    agg_zones_in_db = {
        k: v for k, v in db_zones.items()
        if v.get("aggregationStatus") == "confirmed_active_aggregation"
        and v.get("status") not in ("rollover_dissolved", "stable")
    }
    not_seen_in_scrape = [
        {"name": v["name"], "status": v.get("status"), "supplier": v.get("supplier"),
         "termEnd": v.get("termEnd"), "currentRate": v.get("currentRate")}
        for k, v in agg_zones_in_db.items()
        if k not in matched_keys
    ]

    report = {
        "run_date": today_str,
        "run_timestamp": datetime.now().isoformat(),
        "sources_scraped": source_results,
        "total_scraped": len(found_communities),
        "matched_in_db": len(matched_communities),
        "new_communities_count": len(new_communities),
        "new_communities": sorted(new_communities, key=lambda x: x["name"]),
        "db_agg_zones_not_seen": not_seen_in_scrape,
        "summary": (
            f"{len(new_communities)} new communities found not in DB. "
            f"{len(not_seen_in_scrape)} DB aggregation zones not confirmed by any scrape source."
        ),
    }

    # Write report
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"agg_monitor_{today_str}.json")
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n[AggMonitor] Done.")
    print(f"  New communities not in DB : {len(new_communities)}")
    print(f"  DB agg zones not scraped  : {len(not_seen_in_scrape)}")
    print(f"  Report written            : {out_path}")

    if new_communities:
        print("\n  ── NEW (not in DB) ──")
        for c in new_communities[:20]:
            print(f"    {c['name']:<40} {c['supplier']}")
        if len(new_communities) > 20:
            print(f"    ... and {len(new_communities) - 20} more")

    return report


if __name__ == "__main__":
    run_monitor()
