"""
Google Maps Places API source.
Does nothing until GOOGLE_MAPS_API_KEY is set in your .env file.
Once the key is present, this activates automatically — no other changes needed.
"""

import os
import time
import requests
from typing import List
from .base import BaseSource, RawLead

PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

# Center of Youngstown metro, radius covers Mahoning + Trumbull counties
YOUNGSTOWN_CENTER = {"lat": 41.0998, "lng": -80.6495}
SEARCH_RADIUS_METERS = 40000  # ~25 miles

# Business types that Google Maps knows about, mapped to industry labels
SEARCH_TARGETS = [
    ("laundry",             "Laundromat"),
    ("car_wash",            "Car Wash"),
    ("car_repair",          "Auto Repair"),
    ("storage",             "Warehouse / Storage"),
    ("restaurant",          "Restaurant"),
    ("lodging",             "Hotel / Motel"),
    ("gym",                 "Gym / Fitness Center"),
    ("supermarket",         "Supermarket"),
    ("hospital",            "Hospital"),
    ("factory",             "Manufacturing"),
    ("moving_company",      "Warehouse / Distribution"),
    ("food_processing",     "Food Processing"),
]


def _fetch_nearby(api_key: str, place_type: str, industry: str) -> List[RawLead]:
    leads = []
    params = {
        "location": f"{YOUNGSTOWN_CENTER['lat']},{YOUNGSTOWN_CENTER['lng']}",
        "radius": SEARCH_RADIUS_METERS,
        "type": place_type,
        "key": api_key,
    }

    while True:
        try:
            response = requests.get(PLACES_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"  [Google Maps] Request failed for {place_type}: {e}")
            break

        for place in data.get("results", []):
            name = place.get("name", "").strip()
            if not name:
                continue

            vicinity = place.get("vicinity", "")
            city = vicinity.split(",")[-1].strip() if "," in vicinity else ""
            address = vicinity.split(",")[0].strip() if "," in vicinity else vicinity

            loc = place.get("geometry", {}).get("location", {})

            leads.append(RawLead(
                company_name=name,
                address=address,
                city=city,
                zip_code="",  # Nearby search doesn't return zip — details call needed
                phone="",     # Same — needs a details call (costs extra credits)
                industry=industry,
                business_type=place_type,
                source="Google Maps",
                latitude=loc.get("lat", 0),
                longitude=loc.get("lng", 0),
            ))

        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break

        # Google requires a short wait before the next page token is valid
        time.sleep(2)
        params = {"pagetoken": next_page_token, "key": api_key}

    return leads


class GoogleMapsSource(BaseSource):
    name = "Google Maps"

    def fetch(self) -> List[RawLead]:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
        if not api_key:
            print(f"  [Google Maps] No API key found — skipping. "
                  "Add GOOGLE_MAPS_API_KEY to .env to enable this source.")
            return []

        print(f"  [Google Maps] API key found. Searching {len(SEARCH_TARGETS)} business types...")
        all_leads: List[RawLead] = []
        seen: set[str] = set()

        for place_type, industry in SEARCH_TARGETS:
            results = _fetch_nearby(api_key, place_type, industry)
            for lead in results:
                key = lead.dedup_key()
                if key not in seen:
                    seen.add(key)
                    all_leads.append(lead)
            print(f"  [Google Maps] {place_type}: {len(results)} results.")
            time.sleep(0.5)  # Be polite to the API

        print(f"  [Google Maps] {len(all_leads)} unique businesses found.")
        return all_leads
