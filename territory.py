"""Nearby places, browser locate, and the Ohio territory map.

Points are Census Gazetteer centroids or Census TIGER county-subdivision
centroids. They are not utility territories or aggregation boundaries.
A color is a program category already on file. Unresolved records stay
marked needs-call and are not drawn as confirmed coverage.

An overlay listed in ``data/geo/overlays.json`` is optional geometry the
owner can add later. Loading it does not assert coverage.
"""

from __future__ import annotations

import json
import math
import os
import re

import place_index
import zone_intel

ROOT = os.path.dirname(os.path.abspath(__file__))
GEO_DIR = os.path.join(ROOT, "data", "geo")
OVERLAYS_PATH = os.path.join(GEO_DIR, "overlays.json")

PLACE_TYPES = ("city", "village", "CDP")
NEARBY_PLACE_LIMIT = 12
NEARBY_ZONE_LIMIT = 8

# Wide enough for the Ohio outline, tight enough to reject other states
# without repeating the caller's numbers in an error.
_OHIO_LAT = (38.05, 42.35)
_OHIO_LON = (-84.95, -80.40)

CATEGORIES = (
    ("nopec", "NOPEC", "#e8611a"),
    ("sopec", "SOPEC", "#ffb300"),
    ("noac", "NOAC", "#4fc3f7"),
    ("dynegy", "Dynegy", "#ce93d8"),
    ("other", "Other aggregation", "#90a4ae"),
    ("none", "No own program", "#6b7280"),
    ("municipal_coop", "Municipal or co-op", "#81c784"),
    ("unresolved", "Unresolved / needs call", "#ff5252"),
)
CATEGORY_LABEL = {key: label for key, label, _color in CATEGORIES}
CATEGORY_COLOR = {key: color for key, _label, color in CATEGORIES}

ANCHOR_PLACE = "Plotted at the Census Gazetteer place centroid. Not a municipal or utility boundary."
ANCHOR_TOWNSHIP = "Plotted at the Census county-subdivision centroid. Not an aggregation boundary."
ANCHOR_COUNTY = "Plotted at the Census county centroid. Not an aggregation boundary."
NEAREST_NOTE = "Nearest city, village, or CDP by Census centroid. This is not a municipal boundary test."
UNRESOLVED_NOTE = "Needs call. Not confirmed. This is not marked inactive."
CITY_NOT_COVERED = "No own program. A city or village is not covered by a neighboring township or county program."
POSSIBLY_NOTE = "Possibly covered by its containing township's program. Not confirmed for this place."
OUTSIDE_OHIO = "That location is outside the Ohio counties on file."
LOCATE_BAD = "A location in Ohio is required."
MAP_NOTE = (
    "Points are Census centroids. They are not utility or aggregation boundaries. "
    "A color is a program category from the research on file. "
    "Unresolved records are marked needs-call and are not shown as confirmed coverage. "
    "County and township lines are boundaries only."
)
OVERLAY_NOTE = (
    "Overlay files are optional GeoJSON under data/geo/overlays. "
    "Adding a file does not assert aggregation coverage. "
    "List it in data/geo/overlays.json as "
    '{"id": "short-name", "title": "Label", "file": "filename.geojson", "default": false}.'
)

_SAFE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,80}")
_TOWNSHIP_NAME = re.compile(r"^(?P<name>.+?) Township(?: \((?P<county>[^)]+)\))?$", re.I)
_COUNTY_NAME = re.compile(r"^(?P<name>.+?) County\b", re.I)

_boundaries = None
_map_cache: dict | None = None
_anchor_cache: dict = {}


def category_legend() -> list[dict]:
    return [{"id": key, "label": label, "color": color} for key, label, color in CATEGORIES]


def _norm(value: str | None) -> str:
    return place_index._norm(value)


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return None
    text = str(value).strip()
    if not re.fullmatch(r"-?\d+(\.\d+)?", text):
        return None
    number = float(text)
    if number != number or math.isinf(number):
        return None
    return number


def miles_between(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 3958.7613
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlng = math.radians(lon2 - lon1)
    hav = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlng / 2) ** 2
    return 2 * radius * math.asin(min(1.0, math.sqrt(hav)))


def _ring_contains(ring, lon: float, lat: float) -> bool:
    inside = False
    if not ring:
        return False
    j = len(ring) - 1
    for i, point in enumerate(ring):
        xi, yi = point[0], point[1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > lat) != (yj > lat):
            denom = (yj - yi) or 1e-15
            if lon < (xj - xi) * (lat - yi) / denom + xi:
                inside = not inside
        j = i
    return inside


def _geom_contains(geometry: dict, lon: float, lat: float) -> bool:
    kind = geometry.get("type")
    coords = geometry.get("coordinates") or []
    if kind == "Polygon":
        if not coords or not _ring_contains(coords[0], lon, lat):
            return False
        return not any(_ring_contains(hole, lon, lat) for hole in coords[1:])
    if kind == "MultiPolygon":
        return any(_geom_contains({"type": "Polygon", "coordinates": poly}, lon, lat) for poly in coords)
    return False


def _ring_centroid(ring):
    points = list(ring or [])
    if len(points) >= 2 and points[0] == points[-1]:
        points = points[:-1]
    if len(points) < 3:
        return None
    twice = 0.0
    cx = 0.0
    cy = 0.0
    for index, (x1, y1) in enumerate(points):
        x2, y2 = points[(index + 1) % len(points)]
        cross = x1 * y2 - x2 * y1
        twice += cross
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    if abs(twice) < 1e-12:
        return (
            sum(point[1] for point in points) / len(points),
            sum(point[0] for point in points) / len(points),
        )
    return (cy / (3.0 * twice), cx / (3.0 * twice))


def _geometry_centroid(geometry: dict):
    kind = geometry.get("type")
    coords = geometry.get("coordinates") or []
    if kind == "Polygon" and coords:
        return _ring_centroid(coords[0])
    if kind == "MultiPolygon":
        best = None
        best_span = -1
        for poly in coords:
            if not poly:
                continue
            ring = poly[0]
            span = len(ring)
            if span > best_span:
                best_span = span
                best = _ring_centroid(ring)
        return best
    return None


def _bbox(geometry: dict):
    xs = []
    ys = []

    def walk(node):
        if isinstance(node, (list, tuple)) and node and isinstance(node[0], (int, float)):
            xs.append(node[0])
            ys.append(node[1])
            return
        if isinstance(node, (list, tuple)):
            for item in node:
                walk(item)

    walk(geometry.get("coordinates"))
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def _load_geojson(filename: str) -> dict:
    path = os.path.join(GEO_DIR, filename)
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _boundaries_index():
    global _boundaries
    if _boundaries is not None:
        return _boundaries
    counties_fc = _load_geojson("ohio_counties.geojson")
    townships_fc = _load_geojson("ohio_townships.geojson")
    counties = []
    county_by_fp = {}
    county_centroid = {}
    for feature in counties_fc.get("features") or []:
        props = feature.get("properties") or {}
        geometry = feature.get("geometry") or {}
        name = (props.get("name") or "").strip()
        geoid = str(props.get("geoid") or "")
        box = _bbox(geometry)
        centroid = _geometry_centroid(geometry)
        item = {"name": name, "geoid": geoid, "geometry": geometry, "bbox": box, "centroid": centroid}
        counties.append(item)
        if len(geoid) >= 3:
            county_by_fp[geoid[-3:]] = name
        if centroid:
            county_centroid[_norm(name)] = centroid
    townships = []
    township_centroid = {}
    township_names: dict[str, list] = {}
    for feature in townships_fc.get("features") or []:
        props = feature.get("properties") or {}
        geometry = feature.get("geometry") or {}
        name = (props.get("name") or "").strip()
        county = county_by_fp.get(str(props.get("countyfp") or ""), "")
        centroid = _geometry_centroid(geometry)
        item = {
            "name": name,
            "namelsad": (props.get("namelsad") or "").strip(),
            "county": county,
            "geometry": geometry,
            "bbox": _bbox(geometry),
            "centroid": centroid,
        }
        townships.append(item)
        if centroid and name and county:
            township_centroid[(_norm(name), county.lower())] = centroid
            township_names.setdefault(_norm(name), []).append(item)
    _boundaries = {
        "counties": counties,
        "townships": townships,
        "county_centroid": county_centroid,
        "township_centroid": township_centroid,
        "township_names": township_names,
        "county_source": counties_fc.get("source") or "",
        "township_source": townships_fc.get("source") or "",
    }
    return _boundaries


def _containing(features, lon: float, lat: float):
    found = []
    for feature in features:
        box = feature.get("bbox")
        if not box:
            continue
        minx, miny, maxx, maxy = box
        if lon < minx or lon > maxx or lat < miny or lat > maxy:
            continue
        if _geom_contains(feature["geometry"], lon, lat):
            found.append(feature)
    return found


def category_for_zone(zone: dict) -> str:
    """Program color. Unresolved wins, so a needs-call row is not painted as confirmed."""
    research = zone.get("research") or {}
    status = research.get("status") or {}
    verification = (status.get("verification") or "").strip()
    if status.get("unresolved") or verification in zone_intel.UNRESOLVED_VERIFICATIONS:
        return "unresolved"
    program = (status.get("program") or "").strip().lower()
    admin = (research.get("administrator") or "").strip()
    admin_l = admin.lower()
    aggregation = zone.get("aggregationStatus") or ""
    municipal = program.startswith("not_eligible") or aggregation in ("municipal_utility", "electric_cooperative")
    if municipal and "not a municipal" not in admin_l:
        return "municipal_coop"
    if program.startswith("ended") or program.startswith("no_program"):
        return "none"
    if program.startswith("unknown"):
        return "unresolved"
    if "nopec" in admin_l:
        return "nopec"
    if "sopec" in admin_l and "mixed" not in admin_l:
        return "sopec"
    if re.search(r"\bnoac\b", admin_l):
        return "noac"
    region = zone.get("region") or ""
    if re.search(r"\bNOAC\b", region) and "sopec" not in admin_l and "nopec" not in admin_l:
        return "noac"
    if "dynegy" in admin_l and not any(word in admin_l for word in ("paused", "expired", "none", "mixed")):
        return "dynegy"
    if program.startswith("active"):
        return "other"
    return "none"


def _zone_bits(zone: dict) -> dict:
    research = zone.get("research") or {}
    card = zone.get("card") or {}
    current = research.get("current") or {}
    status = research.get("status") or {}
    sourced = bool(card.get("currentSourced") if card else current.get("sourced"))
    rate = ""
    if sourced:
        rate = str(card.get("currentLabel") or current.get("rate_raw") or "")
    ptc = card.get("ptc") if card else None
    if not ptc:
        ptc = zone_intel.residential_ptc_for_card(zone)
    if ptc.get("applicable") and ptc.get("cents_per_kwh") is not None:
        ptc_text = f"{ptc.get('cents_per_kwh')}¢ residential ({ptc.get('utility') or 'Price to Compare'})"
    else:
        ptc_text = ptc.get("label") or "Price to Compare not assigned"
    start = card.get("currentStart") or current.get("termStart") or ""
    end = card.get("currentEnd") or current.get("termEnd") or ""
    term = ""
    if start or end:
        term = f"{start or '—'} – {end or '—'}"
    return {
        "supplier": research.get("supplier") or "",
        "administrator": research.get("administrator") or "",
        "utility": card.get("utility") or research.get("utility") or zone.get("utility") or "",
        "rate": rate,
        "ptc": ptc_text,
        "term": term,
        "term_status": status.get("term") or "",
        "verification": status.get("verification") or "",
        "card_url": card.get("url") or "",
        "county": research.get("county") or "",
        "expiring": (status.get("term") or "") in zone_intel.EXPIRING_TERMS,
    }


def _ptc_text_for_place(place: dict) -> str:
    parts = []
    for row in place_index._ptc_rows(place):
        if row.get("applicable") and row.get("cents_per_kwh") is not None:
            parts.append(f"{row.get('utility')} {row.get('cents_per_kwh')}¢ residential (area share)")
        elif row.get("label") == "PTC not applicable":
            parts.append("PTC not applicable (municipal or co-op share)")
    if not parts:
        return "Price to Compare not assigned"
    return "; ".join(dict.fromkeys(parts))


def _linked_zones(coverage: dict, zones: list) -> list[dict]:
    wanted = []
    for item in coverage.get("programs") or []:
        name = item.get("zone") or ""
        region = item.get("region") or ""
        if name:
            wanted.append((region, name))
    found = []
    seen = set()
    for region, name in wanted:
        for zone in zones:
            if zone.get("superseded"):
                continue
            if (zone.get("name") or "") != name:
                continue
            if region and (zone.get("_source_file") or "") != region:
                continue
            key = (zone.get("_source_file"), zone.get("name"))
            if key in seen:
                continue
            seen.add(key)
            found.append(zone)
    return found


def describe_place(place: dict, zones: list) -> dict:
    coverage = place_index.coverage_for(place, zones)
    linked = _linked_zones(coverage, zones)
    hollow = coverage.get("status") == "possibly_covered"
    if not linked:
        detail = CITY_NOT_COVERED if place.get("type") in ("city", "village") else (
            "No containing-township program is on file. A county program is not applied as coverage."
        )
        return {
            "category": "none",
            "hollow": False,
            "unresolved": False,
            "status": CATEGORY_LABEL["none"],
            "detail": detail,
            "supplier": "",
            "administrator": "",
            "utility": "",
            "utilities": _place_utility_hints(place),
            "rate": "",
            "ptc": _ptc_text_for_place(place),
            "term": "",
            "term_status": "",
            "verification": "",
            "expiring": False,
            "card_url": "",
            "card_label": "",
            "counties": [item.get("name") or "" for item in place.get("counties") or []],
            "coverage_label": coverage.get("label") or "",
        }
    keys = [category_for_zone(zone) for zone in linked]
    category = "unresolved" if any(key == "unresolved" for key in keys) or len(set(keys)) > 1 else keys[0]
    unresolved = category == "unresolved"
    bits = _zone_bits(linked[0]) if len(linked) == 1 else {}
    if hollow:
        detail = POSSIBLY_NOTE
        status = "Possibly covered · " + CATEGORY_LABEL[category]
    elif unresolved:
        detail = UNRESOLVED_NOTE
        status = CATEGORY_LABEL["unresolved"]
    elif len(linked) > 1:
        detail = "More than one zone record matches this place. They were not merged."
        status = CATEGORY_LABEL[category]
        bits = {}
    else:
        detail = ""
        status = CATEGORY_LABEL[category]
    utilities = []
    if bits.get("utility"):
        utilities = [bits["utility"]]
    return {
        "category": category,
        "hollow": hollow,
        "unresolved": unresolved,
        "status": status,
        "detail": detail,
        "supplier": bits.get("supplier") or "",
        "administrator": bits.get("administrator") or "",
        "utility": bits.get("utility") or "",
        "utilities": utilities,
        "rate": bits.get("rate") or "",
        "ptc": bits.get("ptc") or _ptc_text_for_place(place),
        "term": bits.get("term") or "",
        "term_status": bits.get("term_status") or "",
        "verification": bits.get("verification") or "",
        "expiring": bool(bits.get("expiring")),
        "card_url": bits.get("card_url") or "",
        "card_label": "Township battlecard" if hollow and bits.get("card_url") else ("Battlecard" if bits.get("card_url") else ""),
        "counties": [item.get("name") or "" for item in place.get("counties") or []],
        "coverage_label": coverage.get("label") or "",
    }


def _place_utility_hints(place: dict) -> list[str]:
    found = []
    for utility in place.get("utilities") or []:
        if utility.get("kind") != "investor_owned":
            continue
        label = place_index._canonical_iou(utility.get("name") or "")
        if label and label not in found:
            found.append(label)
    return found


def _place_item(place: dict, zones: list, miles: float | None, detail_prefix: str = "") -> dict:
    described = describe_place(place, zones)
    detail = described["detail"]
    if detail_prefix:
        detail = detail_prefix if not detail else f"{detail_prefix} {detail}"
    return {
        "name": place.get("name") or "",
        "kind": "place",
        "type": place.get("type") or "",
        "miles": None if miles is None else round(miles, 1),
        "category": described["category"],
        "status": described["status"],
        "detail": detail,
        "supplier": described["supplier"],
        "rate": described["rate"],
        "ptc": described["ptc"],
        "term": described["term"],
        "card_url": described["card_url"],
        "card_label": described["card_label"],
        "unresolved": described["unresolved"],
        "hollow": described["hollow"],
    }


def _zone_item(zone: dict, miles: float | None) -> dict:
    category = category_for_zone(zone)
    bits = _zone_bits(zone)
    detail = UNRESOLVED_NOTE if category == "unresolved" else ""
    if category == "none" and not detail:
        detail = "No aggregation program is recorded for this zone."
    if category == "municipal_coop" and not detail:
        detail = "Municipal utility or electric cooperative. Competitive supply is not sold here."
    return {
        "name": zone.get("name") or "",
        "kind": "zone",
        "type": "zone",
        "region": zone.get("_source_file") or "",
        "miles": None if miles is None else round(miles, 1),
        "category": category,
        "status": CATEGORY_LABEL[category],
        "detail": detail,
        "supplier": bits["supplier"],
        "rate": bits["rate"],
        "ptc": bits["ptc"],
        "term": bits["term"],
        "card_url": bits["card_url"],
        "card_label": "Battlecard" if bits["card_url"] else "",
        "unresolved": category == "unresolved",
        "hollow": False,
    }


def _places_with_coords(types: tuple[str, ...] | None = None) -> list[dict]:
    chosen = []
    for place in place_index.load_places():
        if place.get("lat") is None or place.get("lon") is None:
            continue
        if types and place.get("type") not in types:
            continue
        chosen.append(place)
    return chosen


def _nearest_places(lat: float, lon: float, *, exclude_geoids: set[str], limit: int) -> list[tuple[float, dict]]:
    ranked = []
    for place in _places_with_coords(("city", "village")):
        if place.get("geoid") in exclude_geoids:
            continue
        ranked.append((miles_between(lat, lon, place["lat"], place["lon"]), place))
    ranked.sort(key=lambda item: (item[0], _norm(item[1].get("name"))))
    if len(ranked) >= limit:
        return ranked[:limit]
    cdps = []
    for place in _places_with_coords(("CDP",)):
        if place.get("geoid") in exclude_geoids:
            continue
        cdps.append((miles_between(lat, lon, place["lat"], place["lon"]), place))
    cdps.sort(key=lambda item: (item[0], _norm(item[1].get("name"))))
    return (ranked + cdps)[:limit]


def _zone_anchors(zones: list) -> list[tuple[dict, dict]]:
    cached = _anchor_cache.get(id(zones))
    if cached is not None:
        return cached
    index = _boundaries_index()
    by_name: dict[str, list] = {}
    for place in place_index.load_places():
        if place.get("lat") is None:
            continue
        by_name.setdefault(_norm(place.get("name")), []).append(place)
        census = _norm(place.get("census_name"))
        if census and census != _norm(place.get("name")):
            by_name.setdefault(census, []).append(place)
    anchored = []
    for zone in zones:
        if zone.get("superseded"):
            continue
        anchor = _anchor_zone(zone, by_name, index)
        if anchor:
            anchored.append((zone, anchor))
    _anchor_cache.clear()
    _anchor_cache[id(zones)] = anchored
    return anchored


def _anchor_zone(zone: dict, by_name: dict, index: dict):
    name = zone.get("name") or ""
    research_county = ((zone.get("research") or {}).get("county") or "").split(";")[0].split("/")[0].strip()
    township_match = _TOWNSHIP_NAME.match(name.strip())
    if township_match and "/" not in name:
        found = _township_point(township_match.group("name"), township_match.group("county") or research_county, index)
        if found:
            return found
    if re.search(r"\bCounties\b", name):
        return None
    county_match = _COUNTY_NAME.match(name.strip())
    if county_match and "/" not in name:
        found = _county_point(county_match.group("name"), index)
        if found:
            return found
    candidates = []
    bare = re.sub(r"\s*\([^)]*\)", "", name).strip()
    for candidate in (name, bare):
        if candidate and candidate not in candidates:
            candidates.append(candidate)
    for part in re.split(r"\s*/\s*", name):
        part = re.sub(r"\s*\([^)]*\)", "", part).strip()
        if part and part not in candidates:
            candidates.append(part)
    for candidate in candidates:
        township_match = _TOWNSHIP_NAME.match(candidate)
        if township_match:
            found = _township_point(township_match.group("name"), research_county, index)
            if found:
                return found
        if "/" not in candidate:
            county_match = _COUNTY_NAME.match(candidate)
            if county_match:
                found = _county_point(county_match.group("name"), index)
                if found:
                    return found
        place = _match_place(candidate, research_county, by_name)
        if place:
            return {
                "lat": place["lat"],
                "lon": place["lon"],
                "method": "place",
                "note": ANCHOR_PLACE,
            }
    return None


def _match_place(name: str, county: str, by_name: dict):
    hits = list(by_name.get(_norm(name)) or [])
    if not hits:
        return None
    order = {"city": 0, "village": 1, "CDP": 2, "unincorporated": 3}
    hits.sort(key=lambda place: order.get(place.get("type"), 9))
    if county:
        county_l = county.lower()
        in_county = [
            place for place in hits
            if any(county_l == (item.get("name") or "").lower() for item in place.get("counties") or [])
        ]
        if in_county:
            hits = in_county
    preferred = [place for place in hits if place.get("type") in ("city", "village")]
    return (preferred or hits)[0]


def _township_point(name: str, county: str, index: dict):
    key = (_norm(name), (county or "").lower())
    if key[1]:
        centroid = index["township_centroid"].get(key)
        if centroid:
            return {"lat": centroid[0], "lon": centroid[1], "method": "township", "note": ANCHOR_TOWNSHIP}
        return None
    matches = index["township_names"].get(_norm(name)) or []
    if len(matches) == 1 and matches[0].get("centroid"):
        centroid = matches[0]["centroid"]
        return {"lat": centroid[0], "lon": centroid[1], "method": "township", "note": ANCHOR_TOWNSHIP}
    return None


def _county_point(name: str, index: dict):
    centroid = index["county_centroid"].get(_norm(name))
    if not centroid:
        return None
    return {"lat": centroid[0], "lon": centroid[1], "method": "county", "note": ANCHOR_COUNTY}


def nearby_from_point(lat: float, lon: float, zones: list, *, exclude_geoids: set[str] | None = None,
                      exclude_zone_names: set[str] | None = None) -> dict:
    exclude_geoids = exclude_geoids or set()
    exclude_zone_names = {_norm(name) for name in (exclude_zone_names or set())}
    places = [
        _place_item(place, zones, miles)
        for miles, place in _nearest_places(lat, lon, exclude_geoids=exclude_geoids, limit=NEARBY_PLACE_LIMIT)
    ]
    zone_ranked = []
    for zone, anchor in _zone_anchors(zones):
        if _norm(zone.get("name")) in exclude_zone_names:
            continue
        zone_ranked.append((miles_between(lat, lon, anchor["lat"], anchor["lon"]), zone))
    zone_ranked.sort(key=lambda item: (item[0], _norm(item[1].get("name"))))
    return {
        "places": places,
        "zones": [_zone_item(zone, miles) for miles, zone in zone_ranked[:NEARBY_ZONE_LIMIT]],
        "note": "Distances use Census Gazetteer place centroids and zone centroids. They are not drive times or eligibility.",
    }


def nearby_for_geoid(geoid: str, zones: list, origin_name: str = "") -> dict:
    place = next((item for item in place_index.load_places() if item.get("geoid") == geoid), None)
    if place is None or place.get("lat") is None or place.get("lon") is None:
        return {
            "origin": None,
            "places": [],
            "zones": [],
            "note": "This place has no Census coordinate on file, so nearby places are not listed.",
        }
    described = describe_place(place, zones)
    exclude_names = set()
    if place.get("type") in ("city", "village"):
        exclude_names.add(place.get("name") or origin_name)
    payload = nearby_from_point(
        place["lat"],
        place["lon"],
        zones,
        exclude_geoids={geoid},
        exclude_zone_names=exclude_names,
    )
    payload["origin"] = _place_item(place, zones, 0.0)
    payload["origin"]["status"] = described["status"]
    payload["origin"]["detail"] = described["detail"]
    return payload


def nearby_for_zone(zone: dict, zones: list) -> dict:
    anchors = {id(item): anchor for item, anchor in _zone_anchors(zones)}
    anchor = anchors.get(id(zone))
    origin = _zone_item(zone, 0.0)
    if not anchor:
        return {
            "origin": origin,
            "places": [],
            "zones": [],
            "note": "This zone has no Census place, township, or single-county anchor, so it is not plotted and nearby places are not listed.",
        }
    payload = nearby_from_point(
        anchor["lat"],
        anchor["lon"],
        zones,
        exclude_zone_names={zone.get("name") or ""},
    )
    payload["origin"] = origin
    payload["note"] = anchor["note"] + " " + payload["note"]
    return payload


def locate(lat_value, lon_value, zones: list) -> tuple[dict, int]:
    """Resolve a browser point. The response never includes the coordinates."""
    lat = _number(lat_value)
    lon = _number(lon_value)
    if lat is None or lon is None or not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return {"ok": False, "inside_ohio": False, "message": LOCATE_BAD}, 400
    if not (_OHIO_LAT[0] <= lat <= _OHIO_LAT[1] and _OHIO_LON[0] <= lon <= _OHIO_LON[1]):
        return {"ok": True, "inside_ohio": False, "message": OUTSIDE_OHIO}, 200
    index = _boundaries_index()
    counties = _containing(index["counties"], lon, lat)
    if not counties:
        return {"ok": True, "inside_ohio": False, "message": OUTSIDE_OHIO}, 200
    townships = _containing(index["townships"], lon, lat)
    county_name = counties[0]["name"]
    township = townships[0] if townships else None
    nearest = _nearest_places(lat, lon, exclude_geoids=set(), limit=1)
    nearest_item = None
    exclude = set()
    if nearest:
        miles, place = nearest[0]
        nearest_item = _place_item(place, zones, miles, NEAREST_NOTE)
        exclude.add(place.get("geoid") or "")
    around = nearby_from_point(lat, lon, zones, exclude_geoids=exclude)
    return {
        "ok": True,
        "inside_ohio": True,
        "message": (
            "County and township come from Census TIGER boundaries. "
            "The nearest place is a centroid, not a municipal boundary test."
        ),
        "county": county_name,
        "township": township["name"] if township else "",
        "township_county": township["county"] if township else "",
        "nearest_place": nearest_item,
        "nearby_places": around["places"],
        "nearby_zones": around["zones"],
    }, 200


def _feature_from_zone(zone: dict, anchor: dict) -> dict:
    category = category_for_zone(zone)
    bits = _zone_bits(zone)
    counties = [part.strip() for part in re.split(r"[;/]", bits["county"]) if part.strip()]
    detail = UNRESOLVED_NOTE if category == "unresolved" else anchor["note"]
    if category == "none":
        detail = "No aggregation program is recorded for this zone. " + anchor["note"]
    elif category == "municipal_coop":
        detail = "Municipal utility or electric cooperative. " + anchor["note"]
    elif category != "unresolved":
        detail = anchor["note"]
    return {
        "kind": "zone",
        "name": zone.get("name") or "",
        "lat": round(anchor["lat"], 5),
        "lon": round(anchor["lon"], 5),
        "category": category,
        "category_label": CATEGORY_LABEL[category],
        "color": CATEGORY_COLOR[category],
        "hollow": False,
        "unresolved": category == "unresolved",
        "counties": counties,
        "utilities": [bits["utility"]] if bits["utility"] else [],
        "administrator": bits["administrator"],
        "supplier": bits["supplier"],
        "rate": bits["rate"],
        "ptc": bits["ptc"],
        "term": bits["term"],
        "verification": bits["verification"],
        "expiring": bits["expiring"],
        "card_url": bits["card_url"],
        "card_label": "Battlecard" if bits["card_url"] else "",
        "coverage_label": CATEGORY_LABEL[category],
        "detail": detail,
        "anchor": anchor["note"],
    }


def _feature_from_place(place: dict, zones: list) -> dict:
    described = describe_place(place, zones)
    return {
        "kind": "place",
        "name": place.get("name") or "",
        "type": place.get("type") or "",
        "lat": round(place["lat"], 5),
        "lon": round(place["lon"], 5),
        "category": described["category"],
        "category_label": described["status"],
        "color": CATEGORY_COLOR[described["category"]],
        "hollow": described["hollow"],
        "unresolved": described["unresolved"],
        "counties": described["counties"],
        "utilities": described["utilities"],
        "administrator": described["administrator"],
        "supplier": described["supplier"],
        "rate": described["rate"],
        "ptc": described["ptc"],
        "term": described["term"],
        "verification": described["verification"],
        "expiring": described["expiring"],
        "card_url": described["card_url"],
        "card_label": described["card_label"],
        "coverage_label": described["coverage_label"],
        "detail": described["detail"],
        "anchor": ANCHOR_PLACE,
    }


def map_payload(zones: list, include_unincorporated: bool = False) -> dict:
    global _map_cache
    if _map_cache is not None and not include_unincorporated:
        return _map_cache
    anchored_ids = set()
    unplaced = []
    zone_features = []
    for zone, anchor in _zone_anchors(zones):
        anchored_ids.add(id(zone))
        zone_features.append(_feature_from_zone(zone, anchor))
    for zone in zones:
        if zone.get("superseded"):
            continue
        if id(zone) not in anchored_ids:
            unplaced.append(zone.get("name") or "")
    types = ("city", "village", "CDP", "unincorporated") if include_unincorporated else PLACE_TYPES
    place_features = [_feature_from_place(place, zones) for place in _places_with_coords(types)]
    counties = sorted({county for feature in zone_features + place_features for county in feature["counties"] if county})
    utilities = sorted({utility for feature in zone_features + place_features for utility in feature["utilities"] if utility})
    verifications = sorted({feature["verification"] for feature in zone_features if feature["verification"]})
    payload = {
        "ok": True,
        "note": MAP_NOTE,
        "categories": category_legend(),
        "zones": zone_features,
        "places": place_features,
        "unplaced_zones": unplaced,
        "counts": {
            "zones_drawn": len(zone_features),
            "zones_unplaced": len(unplaced),
            "places": len(place_features),
        },
        "filters": {
            "counties": counties,
            "utilities": utilities,
            "categories": [{"id": key, "label": label} for key, label, _color in CATEGORIES],
            "verifications": verifications,
        },
        "boundaries": {
            "counties": "/api/geo/ohio_counties.geojson",
            "townships": "/api/geo/ohio_townships.geojson",
            "county_source": _boundaries_index()["county_source"],
            "township_source": _boundaries_index()["township_source"],
        },
    }
    if not include_unincorporated:
        _map_cache = payload
    return payload


def load_overlays() -> dict:
    payload = {"note": OVERLAY_NOTE, "layers": []}
    if os.path.exists(OVERLAYS_PATH):
        with open(OVERLAYS_PATH, encoding="utf-8") as handle:
            raw = json.load(handle)
        if isinstance(raw, dict):
            payload["note"] = raw.get("note") or OVERLAY_NOTE
            layers = []
            for layer in raw.get("layers") or []:
                if not isinstance(layer, dict):
                    continue
                filename = os.path.basename(str(layer.get("file") or ""))
                layers.append({
                    "id": str(layer.get("id") or filename or "overlay"),
                    "title": str(layer.get("title") or filename or "Overlay"),
                    "file": filename,
                    "default": bool(layer.get("default")),
                    "available": bool(safe_geo_file("overlays/" + filename)) if filename else False,
                })
            payload["layers"] = layers
    return payload


def safe_geo_file(name: str) -> str | None:
    """Only Census files and listed overlay GeoJSON. No path traversal."""
    if not isinstance(name, str):
        return None
    cleaned = name.strip().replace("\\", "/")
    if not cleaned or cleaned.startswith("/") or ".." in cleaned.split("/"):
        return None
    if cleaned in ("ohio_counties.geojson", "ohio_townships.geojson"):
        path = os.path.realpath(os.path.join(GEO_DIR, cleaned))
        root = os.path.realpath(GEO_DIR)
        if path.startswith(root + os.sep) and os.path.isfile(path):
            return path
        return None
    if cleaned.startswith("overlays/"):
        filename = cleaned.split("/", 1)[1]
        if not filename or "/" in filename or not _SAFE_NAME.fullmatch(filename):
            return None
        if not filename.endswith(".geojson"):
            return None
        root = os.path.realpath(os.path.join(GEO_DIR, "overlays"))
        path = os.path.realpath(os.path.join(root, filename))
        if path.startswith(root + os.sep) and os.path.isfile(path):
            return path
    return None
