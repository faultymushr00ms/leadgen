"""
EPA ECHO (Enforcement and Compliance History Online) — free, no key required.
Returns regulated industrial facilities in the target counties.
These are almost always high energy users — exactly the sweet spot.
"""

import requests
from typing import List
from .base import BaseSource, RawLead

ECHO_URL = "https://echo.epa.gov/api/echo/facilities"

# Mahoning and Trumbull counties cover the Youngstown metro area
TARGET_COUNTIES = ["MAHONING", "TRUMBULL"]
STATE = "OH"

# NAICS codes that indicate high energy usage
# Full list: https://www.census.gov/naics/
HIGH_ENERGY_NAICS = [
    "311",  # Food manufacturing
    "312",  # Beverage and tobacco
    "313",  # Textile mills
    "321",  # Wood product manufacturing
    "322",  # Paper manufacturing
    "324",  # Petroleum / coal products
    "325",  # Chemical manufacturing
    "326",  # Plastics and rubber
    "327",  # Nonmetallic mineral (glass, concrete)
    "331",  # Primary metal (steel — big in Youngstown)
    "332",  # Fabricated metal
    "333",  # Machinery manufacturing
    "334",  # Computer / electronic
    "335",  # Electrical equipment
    "336",  # Transportation equipment (auto parts)
    "337",  # Furniture manufacturing
    "481",  # Air transportation
    "484",  # Trucking
    "493",  # Warehousing and storage
    "621",  # Ambulatory health care (clinics, surgery centers)
    "622",  # Hospitals
    "713",  # Amusement / recreation
    "721",  # Accommodation (hotels)
    "722",  # Food services
]


def _fetch_county(county: str) -> List[dict]:
    """Fetch all active facilities in one county, handling pagination."""
    results = []
    page = 1

    while True:
        params = {
            "p_st": STATE,
            "p_co": county,
            "p_act": "Y",          # Active facilities only
            "p_rpp": "100",        # 100 results per page (max)
            "p_qpages": str(page),
            "output": "JSON",
        }

        try:
            response = requests.get(ECHO_URL, params=params, timeout=30,
                                    headers={"User-Agent": "OhioLeadGenBot/1.0"})
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"  [EPA ECHO] Request failed for {county} page {page}: {e}")
            break
        except ValueError:
            print(f"  [EPA ECHO] Bad JSON response for {county} page {page}")
            break

        facilities = (
            data.get("Results", {}).get("Facilities", [])
            or data.get("Results", {}).get("FacilitiesResultSet", {}).get("Facility", [])
        )

        if not facilities:
            break

        results.extend(facilities)

        # Stop if we got a partial page — no more pages
        if len(facilities) < 100:
            break
        page += 1

    return results


def _to_lead(facility: dict) -> RawLead | None:
    name = (facility.get("FacilityName") or "").strip()
    if not name:
        return None

    address = (facility.get("LocationAddress") or "").strip()
    city = (facility.get("LocationCity") or "").strip()
    zip_code = (facility.get("LocationZip") or "")[:5]
    naics = (facility.get("NIACSCodes") or facility.get("NAICSCodes") or "").strip()

    # Map NAICS prefix to a readable industry label
    industry = _naics_to_industry(naics)

    lat = float(facility.get("FacilityLatitude") or 0)
    lon = float(facility.get("FacilityLongitude") or 0)

    notes = f"NAICS: {naics}" if naics else ""

    return RawLead(
        company_name=name,
        address=address,
        city=city,
        zip_code=zip_code,
        phone="",  # EPA doesn't provide phone numbers
        industry=industry,
        business_type="EPA Regulated Facility",
        source="EPA ECHO",
        notes=notes,
        latitude=lat,
        longitude=lon,
    )


def _naics_to_industry(naics: str) -> str:
    mapping = {
        "311": "Food Manufacturing",
        "312": "Beverage Manufacturing",
        "322": "Paper Manufacturing",
        "325": "Chemical Manufacturing",
        "326": "Plastics / Rubber",
        "331": "Primary Metal / Steel",
        "332": "Fabricated Metal",
        "333": "Machinery Manufacturing",
        "336": "Auto Parts / Transportation Equipment",
        "493": "Warehouse / Storage",
        "622": "Hospital",
        "721": "Hotel / Accommodation",
        "722": "Food Service / Restaurant",
    }
    for prefix, label in mapping.items():
        if naics.startswith(prefix):
            return label
    return "Industrial / Manufacturing"


class EPAEchoSource(BaseSource):
    name = "EPA ECHO"

    def fetch(self) -> List[RawLead]:
        print(f"  [{self.name}] Querying EPA ECHO for Mahoning + Trumbull counties...")
        all_facilities = []

        for county in TARGET_COUNTIES:
            facilities = _fetch_county(county)
            print(f"  [{self.name}] {county}: {len(facilities)} facilities found.")
            all_facilities.extend(facilities)

        leads: List[RawLead] = []
        seen: set[str] = set()

        for facility in all_facilities:
            lead = _to_lead(facility)
            if lead is None:
                continue
            key = lead.dedup_key()
            if key in seen:
                continue
            seen.add(key)
            leads.append(lead)

        print(f"  [{self.name}] {len(leads)} unique facilities extracted.")
        return leads
