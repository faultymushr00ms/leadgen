"""
OpenStreetMap via Overpass API — completely free, no key required.
Pulls businesses by type within the Youngstown metro bounding box.
"""

import time
import requests
from typing import List
from .base import BaseSource, RawLead

# Youngstown metro area: Mahoning + Trumbull counties
YOUNGSTOWN_BBOX = {
    "south": 40.85,
    "west": -81.15,
    "north": 41.55,
    "east": -80.35,
}

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# OSM tags that indicate high energy usage — mapped to plain industry names.
# Format: (tag_key, tag_value, industry_label)
HIGH_ENERGY_TAGS = [
    # Industrial / warehouse
    ("building", "industrial",          "Industrial Facility"),
    ("building", "warehouse",           "Warehouse / Distribution"),
    ("building", "factory",             "Manufacturing"),
    ("landuse",  "industrial",          "Industrial"),
    ("man_made", "works",               "Manufacturing / Works"),
    # Car washes and laundry (very high gas/electric)
    ("amenity",  "car_wash",            "Car Wash"),
    ("shop",     "car_wash",            "Car Wash"),
    ("shop",     "laundry",             "Laundromat"),
    ("shop",     "dry_cleaning",        "Dry Cleaning"),
    # Food service
    ("amenity",  "restaurant",          "Restaurant"),
    ("amenity",  "fast_food",           "Fast Food"),
    ("amenity",  "cafe",                "Cafe"),
    # Lodging
    ("tourism",  "hotel",               "Hotel"),
    ("tourism",  "motel",               "Motel"),
    # Fitness
    ("leisure",  "fitness_centre",      "Gym / Fitness Center"),
    ("leisure",  "sports_centre",       "Sports Center"),
    # Retail / grocery
    ("shop",     "supermarket",         "Supermarket"),
    ("shop",     "convenience",         "Convenience Store"),
    ("shop",     "department_store",    "Department Store"),
    # Auto repair
    ("shop",     "car_repair",          "Auto Repair"),
    ("shop",     "car_parts",           "Auto Parts"),
    # Medical
    ("amenity",  "hospital",            "Hospital"),
    ("amenity",  "clinic",              "Medical Clinic"),
    # Cold storage / food processing
    ("cold_storage", "yes",             "Cold Storage"),
]


def _build_query(bbox: dict) -> str:
    b = f"{bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']}"
    tag_blocks = []
    for key, value, _ in HIGH_ENERGY_TAGS:
        tag_blocks.append(f'  node["{key}"="{value}"]({b});')
        tag_blocks.append(f'  way["{key}"="{value}"]({b});')

    inner = "\n".join(tag_blocks)
    return f"[out:json][timeout:120];\n(\n{inner}\n);\nout center;"


def _parse_element(element: dict, industry: str) -> RawLead | None:
    tags = element.get("tags", {})
    name = tags.get("name", "").strip()
    if not name:
        return None

    # Coordinates — ways return center, nodes return direct lat/lon
    lat = element.get("lat") or element.get("center", {}).get("lat", 0)
    lon = element.get("lon") or element.get("center", {}).get("lon", 0)

    address_parts = [
        tags.get("addr:housenumber", ""),
        tags.get("addr:street", ""),
    ]
    address = " ".join(p for p in address_parts if p).strip()

    return RawLead(
        company_name=name,
        address=address,
        city=tags.get("addr:city", ""),
        zip_code=tags.get("addr:postcode", ""),
        phone=tags.get("phone", tags.get("contact:phone", "")),
        industry=industry,
        business_type=industry,
        source="OpenStreetMap",
        latitude=lat,
        longitude=lon,
    )


class OverpassSource(BaseSource):
    name = "OpenStreetMap"

    def fetch(self) -> List[RawLead]:
        print(f"  [{self.name}] Querying Overpass API for Youngstown metro...")
        query = _build_query(YOUNGSTOWN_BBOX)

        try:
            response = requests.post(
                OVERPASS_URL,
                data={"data": query},
                timeout=130,
                headers={"User-Agent": "OhioLeadGenBot/1.0"},
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"  [{self.name}] Request failed: {e}")
            return []

        data = response.json()
        elements = data.get("elements", [])
        print(f"  [{self.name}] Got {len(elements)} raw elements.")

        # Build a tag→industry lookup so each element gets labeled correctly
        tag_lookup = {(k, v): label for k, v, label in HIGH_ENERGY_TAGS}

        leads: List[RawLead] = []
        seen: set[str] = set()

        for element in elements:
            tags = element.get("tags", {})
            industry = "Unknown"
            for key, value, label in HIGH_ENERGY_TAGS:
                if tags.get(key) == value:
                    industry = label
                    break

            lead = _parse_element(element, industry)
            if lead is None:
                continue
            key = lead.dedup_key()
            if key in seen:
                continue
            seen.add(key)
            leads.append(lead)

        print(f"  [{self.name}] {len(leads)} named businesses extracted.")
        return leads
