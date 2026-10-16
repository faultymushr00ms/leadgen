"""Ohio place index: cities, villages, CDPs, and unincorporated communities.

The Census/GNIS files in ``data/research/`` are loaded and never rewritten.
A later correction must be appended elsewhere. A ZIP or ZCTA is not proof
of jurisdiction. HIFLD utility shares are an area indication, not a
PUCO-certified boundary.

Coverage rule: a city or village is covered only by its own program. A
township or county program does not cover it. A CDP or unincorporated
place inherits its containing township's program as possibly covered.
"""

from __future__ import annotations

import csv
import os
import re

import zone_intel

ROOT = os.path.dirname(os.path.abspath(__file__))
RESEARCH_DIR = os.path.join(ROOT, "data", "research")
PLACE_INDEX_PATH = os.path.join(RESEARCH_DIR, "place_index.csv")
CROSSWALK_PATH = os.path.join(RESEARCH_DIR, "place_zone_crosswalk.csv")

UTILITY_NOTE = (
    "Utility shares are HIFLD area overlap, not a PUCO-certified boundary. "
    "A small municipal system may be missing."
)
ZIP_NOTE = (
    "A ZIP or ZCTA is not proof of jurisdiction or program eligibility. "
    "Confirm the city, village, or township and the utility at the street address."
)

_IOU = (
    ("OHIO EDISON", "Ohio Edison"),
    ("TOLEDO EDISON", "Toledo Edison"),
    ("CLEVELAND ELECTRIC", "The Illuminating Company"),
    ("OHIO POWER", "AEP Ohio"),
    ("DUKE ENERGY", "Duke Energy Ohio"),
    ("DAYTON POWER", "AES Ohio"),
)

_places_cache: list | None = None
_crosswalk_cache: list | None = None
_crosswalk_by_geoid: dict | None = None

_TOWNSHIP_RE = re.compile(
    r"^(?P<name>.+?) township \((?P<county>[^)]+)\)(?: \((?P<share>[0-9.]+)% pop\))?$",
    re.I,
)
_COUNTY_RE = re.compile(r"^(?P<name>.+?) \((?P<share>[0-9.]+)% pop\)$")
_UTILITY_RE = re.compile(r"^(?P<name>.*) \((?P<share>[0-9.]+)%\)$")
_ZCTA_RE = re.compile(r"(\d{5})\(([0-9.]+)%\)")


def _norm(value: str | None) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).split())


def _split_semi(text: str | None) -> list[str]:
    return [part.strip() for part in (text or "").split(";") if part.strip()]


def parse_counties(text: str | None) -> list[dict]:
    found = []
    for part in _split_semi(text):
        match = _COUNTY_RE.match(part)
        if match:
            found.append({"name": match.group("name"), "share": match.group("share")})
        else:
            found.append({"name": part, "share": ""})
    return found


def parse_townships(text: str | None, role: str) -> list[dict]:
    found = []
    for part in _split_semi(text):
        match = _TOWNSHIP_RE.match(part)
        if not match:
            continue
        found.append({
            "name": match.group("name"),
            "county": match.group("county"),
            "share": match.group("share") or "",
            "role": role,
            "raw": part,
        })
    return found


def parse_utilities(text: str | None) -> list[dict]:
    found = []
    for part in _split_semi(text):
        match = _UTILITY_RE.match(part)
        if not match:
            continue
        name = match.group("name").strip()
        upper = name.upper()
        if "COOP" in upper or "COOPERATIVE" in upper:
            kind = "cooperative"
        elif "MUNICIPAL" in upper:
            kind = "municipal"
        elif "INVESTOR OWNED" in upper:
            kind = "investor_owned"
        else:
            kind = "other"
        found.append({"name": name, "share": match.group("share"), "kind": kind})
    return found


def parse_zctas(text: str | None) -> list[dict]:
    return [{"zip": zipcode, "share": share} for zipcode, share in _ZCTA_RE.findall(text or "")]


def _canonical_iou(hifld_name: str) -> str:
    upper = hifld_name.upper()
    for needle, label in _IOU:
        if needle in upper:
            return label
    return ""


def _float_or_none(value) -> float | None:
    try:
        number = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    if number != number:
        return None
    return number


def load_places() -> list[dict]:
    """Read the place index. The file is not rewritten."""
    global _places_cache
    if _places_cache is not None:
        return _places_cache
    places = []
    if os.path.exists(PLACE_INDEX_PATH):
        with open(PLACE_INDEX_PATH, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                containing = parse_townships(row.get("townships_containing"), "containing")
                adjacent = parse_townships(row.get("townships_adjacent_if_withdrawn"), "adjacent")
                places.append({
                    "name": (row.get("name") or "").strip(),
                    "census_name": (row.get("census_name") or "").strip(),
                    "type": (row.get("type") or "").strip(),
                    "geoid": (row.get("geoid") or "").strip(),
                    "pop_2020": (row.get("pop_2020") or "").strip(),
                    "counties": parse_counties(row.get("counties")),
                    "county_text": (row.get("counties") or "").strip(),
                    "townships": containing + adjacent,
                    "zctas": parse_zctas(row.get("zcta_2020")),
                    "utilities": parse_utilities(row.get("electric_utility_hifld")),
                    "utility_text": (row.get("electric_utility_hifld") or "").strip(),
                    "amp": (row.get("amp_member_muni_electric") or "").strip(),
                    "lat": _float_or_none(row.get("lat")),
                    "lon": _float_or_none(row.get("lon")),
                    "notes": (row.get("notes") or "").strip(),
                    "source": (row.get("source") or "").strip(),
                })
    _places_cache = places
    return places


def load_crosswalk() -> list[dict]:
    """Read the place-to-zone crosswalk. The file is not rewritten."""
    global _crosswalk_cache, _crosswalk_by_geoid
    if _crosswalk_cache is not None:
        return _crosswalk_cache
    rows = []
    if os.path.exists(CROSSWALK_PATH):
        with open(CROSSWALK_PATH, newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    by_geoid: dict[str, list] = {}
    for row in rows:
        by_geoid.setdefault((row.get("geoid") or "").strip(), []).append(row)
    _crosswalk_by_geoid = by_geoid
    _crosswalk_cache = rows
    return rows


def _crosswalk_for(geoid: str) -> list[dict]:
    if not geoid:
        return []
    load_crosswalk()
    return list((_crosswalk_by_geoid or {}).get(geoid) or [])


def _active_zones(zones: list) -> list:
    return [zone for zone in zones if not zone.get("superseded")]


def _zone_summary(zone: dict) -> dict:
    research = zone.get("research") or {}
    current = research.get("current") or {}
    return {
        "zone": zone.get("name") or "",
        "region": zone.get("_source_file") or "",
        "county": research.get("county") or "",
        "supplier": research.get("supplier") or zone.get("supplier") or "",
        "administrator": research.get("administrator") or "",
        "rate": current.get("rate_raw") or "",
        "card_url": (zone.get("card") or {}).get("url") or "",
    }


def _township_key(township: dict) -> str:
    return _norm(f"{township['name']} township")


def _zone_matches_township(zone: dict, township: dict) -> bool:
    zname = _norm(zone.get("name"))
    key = _township_key(township)
    if key not in zname:
        return False
    county = _norm(township.get("county"))
    if not county:
        return True
    if county in zname:
        return True
    research_county = _norm(((zone.get("research") or {}).get("county") or ""))
    named = re.findall(r"\(([^)]+)\)", zone.get("name") or "")
    if named:
        return any(county in _norm(part) for part in named)
    if research_county:
        return county in research_county
    return True


def _own_zones(place: dict, zones: list, rows: list[dict]) -> list[dict]:
    """City or village programs only. Township and county zones are excluded."""
    if place["type"] not in ("city", "village"):
        return []
    found = []
    seen = set()
    target = _norm(place["name"])
    named = {
        row.get("zone") or ""
        for row in rows
        if row.get("match_kind") == "place" and _norm(row.get("component")) == target
    }
    for zone in zones:
        name = zone.get("name") or ""
        if _norm(name) == target or name in named:
            key = (zone.get("_source_file"), name)
            if key not in seen:
                seen.add(key)
                found.append(zone)
    return found


def _township_programs(place: dict, zones: list) -> list[dict]:
    """Containing-township zones. Adjacent townships are not inheritance."""
    found = []
    seen = set()
    for township in place["townships"]:
        if township["role"] != "containing":
            continue
        for zone in zones:
            if not _zone_matches_township(zone, township):
                continue
            key = (zone.get("_source_file"), zone.get("name"), township["name"], township["county"])
            if key in seen:
                continue
            seen.add(key)
            item = _zone_summary(zone)
            item["township"] = township["name"]
            item["township_county"] = township["county"]
            item["role"] = "possibly_covered"
            found.append(item)
    return found


def _cdp_named_zones(place: dict, zones: list) -> list[dict]:
    if place["type"] not in ("CDP", "unincorporated"):
        return []
    target = _norm(place["name"])
    found = []
    for zone in zones:
        parts = [_norm(part) for part in re.split(r"/", zone.get("name") or "")]
        if target in parts:
            found.append(zone)
    return found


def _not_covering(place: dict, rows: list[dict], own: list[dict], possibly: list[dict]) -> list[dict]:
    own_names = {zone.get("name") for zone in own}
    possible_names = {item["zone"] for item in possibly}
    found = []
    seen = set()
    for row in rows:
        zone_name = row.get("zone") or ""
        if not zone_name or zone_name in own_names or zone_name in possible_names or zone_name in seen:
            continue
        kind = row.get("match_kind") or ""
        if place["type"] in ("city", "village"):
            reason = (
                "A city or village is covered only by its own program. "
                "This township or county record does not cover it."
            )
        elif kind == "place":
            reason = (
                "A CDP or unincorporated place cannot pass its own aggregation. "
                "A zone named for it is not its program."
            )
        else:
            reason = (
                "A CDP or unincorporated place inherits its containing township's "
                "program only, as possibly covered. This other record is not that inheritance."
            )
        seen.add(zone_name)
        found.append({
            "zone": zone_name,
            "match_kind": kind,
            "flag": row.get("flag") or "",
            "reason": reason,
        })
    return found


def coverage_for(place: dict, zones: list | None = None) -> dict:
    zones = _active_zones(zones if zones is not None else [])
    rows = _crosswalk_for(place["geoid"])
    own = _own_zones(place, zones, rows)
    possibly = []
    notes = []
    if place["type"] in ("city", "village"):
        status = "own" if own else "not_covered"
        if own:
            label = "Covered by its own program."
            if len(own) > 1:
                label = "Covered by its own program. Duplicate zone records are listed and were not merged."
                notes.append("Duplicate zone records share this name. They were not merged or deleted.")
        else:
            label = "Not covered. A city or village is not covered by a township or county program."
        programs = []
        for zone in own:
            item = _zone_summary(zone)
            item["role"] = "own"
            programs.append(item)
    else:
        possibly = _township_programs(place, zones)
        named = _cdp_named_zones(place, zones)
        if named:
            notes.append(
                "A zone name includes this place. A CDP or unincorporated community "
                "cannot pass aggregation, so that name is not its own program."
            )
        if possibly:
            status = "possibly_covered"
            label = "Possibly covered by its containing township's program."
        else:
            status = "not_covered"
            label = "No containing-township program found. A county program is not applied as coverage."
        programs = possibly
    return {
        "status": status,
        "label": label,
        "programs": programs,
        "not_covering": _not_covering(place, rows, own, possibly),
        "notes": notes,
    }


def _ptc_rows(place: dict) -> list[dict]:
    rows = []
    for utility in place["utilities"]:
        kind = utility["kind"]
        canonical = _canonical_iou(utility["name"]) if kind == "investor_owned" else ""
        ptc = zone_intel.ptc_for_utility(canonical) if canonical else None
        if kind in ("municipal", "cooperative"):
            rows.append({
                "hifld_name": utility["name"],
                "share": utility["share"],
                "applicable": False,
                "label": "PTC not applicable",
                "reason": "Municipal utility or electric cooperative share.",
                "utility": canonical,
                "cents_per_kwh": None,
            })
            continue
        if not ptc:
            rows.append({
                "hifld_name": utility["name"],
                "share": utility["share"],
                "applicable": False,
                "label": "Price to Compare not assigned",
                "reason": "This HIFLD name does not map to one Ohio investor-owned Price to Compare.",
                "utility": canonical,
                "cents_per_kwh": None,
            })
            continue
        rows.append({
            "hifld_name": utility["name"],
            "share": utility["share"],
            "applicable": True,
            "label": "residential Price to Compare",
            "reason": "",
            "utility": ptc.get("utility") or canonical,
            "code": ptc.get("code") or "",
            "cents_per_kwh": ptc.get("cents_per_kwh"),
            "effective_start": ptc.get("effective_start") or "",
            "effective_end": ptc.get("effective_end") or "",
            "accessed_at": ptc.get("accessed_at") or "",
            "source_url": ptc.get("source_url") or "",
            "customer_class": "residential",
        })
    return rows


def present_place(place: dict, zones: list) -> dict:
    return {
        "name": place["name"],
        "census_name": place["census_name"],
        "type": place["type"],
        "geoid": place["geoid"],
        "pop_2020": place["pop_2020"],
        "counties": place["counties"],
        "townships": [
            {
                "name": township["name"],
                "county": township["county"],
                "share": township["share"],
                "role": township["role"],
            }
            for township in place["townships"]
        ],
        "utilities": place["utilities"],
        "utility_note": UTILITY_NOTE,
        "amp": place["amp"],
        "zctas": place["zctas"],
        "zip_note": ZIP_NOTE,
        "ptc": _ptc_rows(place),
        "coverage": coverage_for(place, zones),
        "notes": place["notes"],
    }


_ZIP_RE = re.compile(r"\d{5}")
_PLACE_RE = re.compile(r"[A-Za-z][A-Za-z0-9 .'\-()]{0,80}")


def classify_lookup(raw) -> tuple[str, str] | None:
    """Accept a 5-digit ZIP or a place name. Reject anything else.

    The raw value is not logged. Callers must not echo a rejected value.
    """
    if not isinstance(raw, str):
        return None
    text = raw.strip()
    if not text or len(text) > 81:
        return None
    if _ZIP_RE.fullmatch(text):
        return ("zip", text)
    if _PLACE_RE.fullmatch(text):
        return ("place", text)
    return None


def lookup_name(query: str, zones: list, limit: int = 25) -> dict:
    """Exact place-name matches win. A 5-digit query is a ZIP lookup."""
    text = (query or "").strip()
    if re.fullmatch(r"\d{5}", text):
        found = lookup_zip(text, zones)
        found["query"] = text
        return found
    target = _norm(text)
    places = load_places()
    exact = [
        place for place in places
        if _norm(place["name"]) == target or _norm(place["census_name"]) == target
    ]
    if exact:
        chosen = exact
        total = len(exact)
        truncated = False
    else:
        starts = [place for place in places if target and _norm(place["name"]).startswith(target)]
        pool = starts or [place for place in places if target and target in _norm(place["name"])]
        total = len(pool)
        truncated = total > limit
        chosen = pool[:limit]
    return {
        "query": text,
        "match": "name",
        "count": total,
        "truncated": truncated,
        "zip_note": ZIP_NOTE,
        "places": [present_place(place, zones) for place in chosen],
    }


def lookup_zip(zipcode: str, zones: list) -> dict:
    classified = classify_lookup(zipcode or "")
    digits = classified[1] if classified and classified[0] == "zip" else ""
    chosen = [
        place for place in load_places()
        if digits and any(item["zip"] == digits for item in place["zctas"])
    ]
    return {
        "query": digits,
        "match": "zip",
        "zip": digits,
        "count": len(chosen),
        "truncated": False,
        "eligibility": "not_proof",
        "zip_note": ZIP_NOTE,
        "places": [present_place(place, zones) for place in chosen],
    }


def county_tree(county: str, zones: list) -> dict:
    """Places in one county, nested under the township that contains or borders them."""
    target = (county or "").strip().lower()
    groups: dict[tuple, list] = {}
    order: list[tuple] = []
    for place in load_places():
        if not any(item["name"].lower() == target for item in place["counties"]):
            continue
        townships = [item for item in place["townships"] if item["county"].lower() == target]
        if not townships:
            townships = [{
                "name": "No township on file",
                "county": county,
                "share": "",
                "role": "unknown",
            }]
        covered = coverage_for(place, zones)
        entry = {
            "name": place["name"],
            "type": place["type"],
            "geoid": place["geoid"],
            "pop_2020": place["pop_2020"],
            "coverage_status": covered["status"],
            "coverage_label": covered["label"],
        }
        for township in townships:
            key = (township["name"], township["role"])
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append(entry)
    townships_out = []
    for key in sorted(order, key=lambda item: (item[0].lower(), item[1])):
        name, role = key
        places = sorted(groups[key], key=lambda item: (item["type"], item["name"].lower()))
        townships_out.append({
            "name": name,
            "role": role,
            "count": len(places),
            "places": places,
        })
    return {"county": county, "townships": townships_out, "place_count": sum(len(groups[key]) for key in groups)}
