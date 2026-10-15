"""PUCO Government Aggregation map overlay.

The MapServer is public and has no stated license. Polygon geometry is
fetched into a gitignored cache and is not committed. Each fetch writes a
new snapshot. Older snapshots stay on disk.

A certificate or map listing is not proof of an active program, a supplier,
or a rate. Crosswalk rows are investigation flags only.
"""

from __future__ import annotations

import csv
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import history_store
import zone_intel

ROOT = os.path.dirname(os.path.abspath(__file__))
RESEARCH_PUCO = os.path.join(zone_intel.RESEARCH_DIR, "puco")
CROSSWALK_PATH = os.path.join(RESEARCH_PUCO, "crosswalk_app_to_puco.csv")
NOT_IN_APP_PATH = os.path.join(RESEARCH_PUCO, "puco_map_not_in_app.csv")

LAYER_PAGE = (
    "https://maps.puco.ohio.gov/arcgis/rest/services/misc/Government_Aggregation/MapServer/0"
)
AGG_QUERY = LAYER_PAGE + "/query"
COUNTY_QUERY = (
    "https://maps.puco.ohio.gov/arcgis/rest/services/boundaries/"
    "Ohio_County_Boundaries/MapServer/0/query"
)
ATTRIBUTION = "Source: PUCO Government Aggregation map"
DISCLAIMER = (
    "PUCO certification only: not proof of an active program, supplier or rate"
)
FLAG_ACTION = "Flag only. Zone records were not changed. " + DISCLAIMER
PROSPECT_ACTION = "Possible prospect to research. " + DISCLAIMER

OUT_FIELDS = ",".join([
    "OBJECTID",
    "BoundaryType",
    "CommunityName",
    "AggType",
    "CountyID",
    "AOGCertID",
    "AOGCaseRef",
    "AOGCompany",
    "AOGIssueDate",
    "CommCertID",
    "CommCaseRef",
    "CommCompany",
    "CommIssueDate",
])
PAGE_SIZE = 2000
SIMPLIFY_DEGREES = 0.0005

COUNCILS = (
    ("nopec", "NOPEC", "#e8611a"),
    ("sopec", "SOPEC", "#ffb300"),
    ("mvcc", "MVCC", "#4dd0e1"),
    ("own", "Own certificate", "#c5cae9"),
    ("other", "Other council", "#80cbc4"),
)
COUNCIL_COLOR = {key: color for key, _label, color in COUNCILS}

_COUNCIL_NAMES = {
    "Northeast Ohio Public Energy Council": "nopec",
    "Southeast Ohio Public Energy Council": "sopec",
    "Miami Valley Communications Council": "mvcc",
}

_GROUP_LABELS = {
    "active_missing": "app-active zone with no PUCO listing",
    "not_on_map": "app zone with no PUCO electric listing",
    "nopec_admin": "NOPEC-vs-app administrator conflict",
    "app_nopec_not_on_map": "app NOPEC administrator with no NOPEC council on the PUCO polygon",
    "status_conflict": "PUCO electric listing where the app status is not an active program",
    "ambiguous": "ambiguous multi-county name",
    "prospect": "possible prospects to research",
}


class PucoUnavailable(RuntimeError):
    """The public map could not be fetched. Zone data is left as stored."""


def cache_dir() -> str:
    override = os.environ.get("FORGE_PUCO_CACHE")
    return override if override else os.path.join(ROOT, "data", "cache", "puco")


def council_id(company: str | None) -> str:
    text = (company or "").strip()
    if not text:
        return "own"
    return _COUNCIL_NAMES.get(text, "other")


def councils_legend() -> list[dict]:
    return [{"id": key, "label": label, "color": color} for key, label, color in COUNCILS]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _read_json(url: str, params: dict, opener) -> dict:
    full = url + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(full, headers={"User-Agent": "FORGE-puco-overlay/1.0"})
    try:
        with opener.open(request, timeout=120) as response:
            payload = response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise PucoUnavailable("The PUCO aggregation map could not be loaded.") from exc
    try:
        body = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PucoUnavailable("The PUCO aggregation map could not be loaded.") from exc
    if isinstance(body, dict) and body.get("error"):
        raise PucoUnavailable("The PUCO aggregation map could not be loaded.")
    return body


def _fetch_features(opener) -> list[dict]:
    features = []
    offset = 0
    while True:
        body = _read_json(AGG_QUERY, {
            "where": "1=1",
            "outFields": OUT_FIELDS,
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "geojson",
            "resultOffset": str(offset),
            "resultRecordCount": str(PAGE_SIZE),
        }, opener)
        batch = body.get("features") or []
        if not isinstance(batch, list):
            raise PucoUnavailable("The PUCO aggregation map could not be loaded.")
        features.extend(batch)
        exceeded = bool((body.get("properties") or {}).get("exceededTransferLimit"))
        if not batch or (len(batch) < PAGE_SIZE and not exceeded):
            break
        offset += len(batch)
        if offset > 10000:
            break
    return features


def _fetch_counties(opener) -> dict[int, str]:
    try:
        body = _read_json(COUNTY_QUERY, {
            "where": "1=1",
            "outFields": "CountyID,CountyName",
            "returnGeometry": "false",
            "f": "json",
        }, opener)
    except PucoUnavailable:
        return {}
    names = {}
    for feature in body.get("features") or []:
        attributes = feature.get("attributes") or {}
        county_id = attributes.get("CountyID")
        name = (attributes.get("CountyName") or "").strip()
        if isinstance(county_id, int) and name:
            names[county_id] = name
    return names


def _manifest_path() -> str:
    return os.path.join(cache_dir(), "manifest.jsonl")


def _append_manifest(entry: dict) -> None:
    path = _manifest_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def latest_snapshot() -> dict | None:
    path = _manifest_path()
    if not os.path.exists(path):
        return None
    found = None
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            raw = os.path.join(cache_dir(), entry.get("filename") or "")
            if entry.get("filename") and os.path.isfile(raw):
                found = entry
    return found


def _perp(start, end, point) -> float:
    x1, y1 = start
    x2, y2 = end
    x0, y0 = point
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return ((x0 - x1) ** 2 + (y0 - y1) ** 2) ** 0.5
    return abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / ((dx * dx + dy * dy) ** 0.5)


def _simplify_ring(ring, epsilon: float) -> list:
    if len(ring) < 4:
        return [[round(point[0], 5), round(point[1], 5)] for point in ring]
    closed = ring[0] == ring[-1]
    core = ring[:-1] if closed else list(ring)
    count = len(core)
    if count <= 2:
        return [[round(point[0], 5), round(point[1], 5)] for point in ring]
    keep = [False] * count
    keep[0] = keep[-1] = True
    stack = [(0, count - 1)]
    while stack:
        start, end = stack.pop()
        best = -1.0
        index = -1
        for cursor in range(start + 1, end):
            distance = _perp(core[start], core[end], core[cursor])
            if distance > best:
                best = distance
                index = cursor
        if best > epsilon and index != -1:
            keep[index] = True
            stack.append((start, index))
            stack.append((index, end))
    simplified = [core[index] for index, flag in enumerate(keep) if flag]
    if len(simplified) < 3:
        simplified = core
    rounded = []
    for point in simplified:
        pair = [round(point[0], 5), round(point[1], 5)]
        if not rounded or pair != rounded[-1]:
            rounded.append(pair)
    if not rounded:
        return []
    if rounded[0] != rounded[-1]:
        rounded.append(rounded[0])
    return rounded


def _simplify_geometry(geometry: dict) -> dict | None:
    if not isinstance(geometry, dict):
        return None
    kind = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if kind == "Polygon" and isinstance(coordinates, list):
        rings = [_simplify_ring(ring, SIMPLIFY_DEGREES) for ring in coordinates if isinstance(ring, list)]
        rings = [ring for ring in rings if len(ring) >= 4]
        if not rings:
            return None
        return {"type": "Polygon", "coordinates": rings}
    if kind == "MultiPolygon" and isinstance(coordinates, list):
        polygons = []
        for polygon in coordinates:
            if not isinstance(polygon, list):
                continue
            rings = [_simplify_ring(ring, SIMPLIFY_DEGREES) for ring in polygon if isinstance(ring, list)]
            rings = [ring for ring in rings if len(ring) >= 4]
            if rings:
                polygons.append(rings)
        if not polygons:
            return None
        return {"type": "MultiPolygon", "coordinates": polygons}
    return None


def _text(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _display_feature(feature: dict, counties: dict[int, str]) -> dict | None:
    props = feature.get("properties") or {}
    geometry = _simplify_geometry(feature.get("geometry") or {})
    if geometry is None:
        return None
    company = _text(props.get("AOGCompany"))
    county_id = props.get("CountyID")
    county = counties.get(county_id, "") if isinstance(county_id, int) else ""
    return {
        "type": "Feature",
        "properties": {
            "object_id": props.get("OBJECTID"),
            "name": _text(props.get("CommunityName")),
            "boundary": _text(props.get("BoundaryType")),
            "agg": _text(props.get("AggType")),
            "county": county,
            "council": council_id(company),
            "council_name": company,
            "aog_cert": _text(props.get("AOGCertID")),
            "aog_case": _text(props.get("AOGCaseRef")),
            "aog_date": _text(props.get("AOGIssueDate")),
            "comm_cert": _text(props.get("CommCertID")),
            "comm_case": _text(props.get("CommCaseRef")),
            "comm_date": _text(props.get("CommIssueDate")),
            "comm_company": _text(props.get("CommCompany")),
        },
        "geometry": geometry,
    }


def _build_display(raw_path: str, county_path: str, display_path: str) -> str:
    with open(raw_path, encoding="utf-8") as handle:
        raw = json.load(handle)
    counties = {}
    if os.path.isfile(county_path):
        with open(county_path, encoding="utf-8") as handle:
            stored = json.load(handle)
        counties = {int(key): value for key, value in stored.items() if str(key).isdigit() and value}
    features = []
    for feature in raw.get("features") or []:
        displayed = _display_feature(feature, counties)
        if displayed:
            features.append(displayed)
    payload = {
        "type": "FeatureCollection",
        "attribution": ATTRIBUTION,
        "disclaimer": DISCLAIMER,
        "features": features,
    }
    return history_store.write_new_file(display_path, json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def fetch_snapshot(opener=None) -> dict:
    """Fetch a new snapshot. Does not overwrite an older snapshot."""
    opener = opener or urllib.request.build_opener()
    features = _fetch_features(opener)
    counties = _fetch_counties(opener)
    fetched_at = _now()
    stamp = _stamp()
    directory = cache_dir()
    os.makedirs(directory, exist_ok=True)
    collection = {"type": "FeatureCollection", "features": features}
    raw_path = history_store.write_new_file(
        os.path.join(directory, f"government_aggregation_{stamp}.geojson"),
        json.dumps(collection, ensure_ascii=False),
    )
    county_path = history_store.write_new_file(
        os.path.join(directory, f"county_names_{stamp}.json"),
        json.dumps({str(key): value for key, value in sorted(counties.items())}, ensure_ascii=False),
    )
    display_path = _build_display(
        raw_path,
        county_path,
        os.path.join(directory, f"government_aggregation_{stamp}.display.geojson"),
    )
    electric = sum(1 for feature in features if (feature.get("properties") or {}).get("AggType") == "Electric")
    gas = sum(1 for feature in features if (feature.get("properties") or {}).get("AggType") == "Gas")
    entry = {
        "fetched_at": fetched_at,
        "filename": os.path.basename(raw_path),
        "county_file": os.path.basename(county_path),
        "display_file": os.path.basename(display_path),
        "feature_count": len(features),
        "electric": electric,
        "gas": gas,
        "attribution": ATTRIBUTION,
        "source": LAYER_PAGE,
    }
    _append_manifest(entry)
    history_store.append_event("puco_snapshot", {
        "source": LAYER_PAGE,
        "attribution": ATTRIBUTION,
        "fetched_at": fetched_at,
        "feature_count": len(features),
        "electric": electric,
        "gas": gas,
        "filename": entry["filename"],
        "county_names": len(counties),
    })
    return entry


def _display_path_for(entry: dict) -> str | None:
    name = entry.get("display_file") or ""
    if not name:
        return None
    path = os.path.join(cache_dir(), name)
    if os.path.isfile(path):
        return path
    return None


def ensure_display() -> tuple[dict, str]:
    """Return the latest snapshot metadata and its display file, fetching once if needed."""
    entry = latest_snapshot()
    if entry is None:
        entry = fetch_snapshot()
    path = _display_path_for(entry)
    if path is None:
        raw = os.path.join(cache_dir(), entry["filename"])
        county = os.path.join(cache_dir(), entry.get("county_file") or "")
        path = _build_display(
            raw,
            county,
            os.path.join(cache_dir(), os.path.splitext(entry["filename"])[0] + ".display.geojson"),
        )
    return entry, path


def display_payload() -> dict:
    entry, path = ensure_display()
    with open(path, encoding="utf-8") as handle:
        geojson = json.load(handle)
    return {
        "ok": True,
        "attribution": ATTRIBUTION,
        "disclaimer": DISCLAIMER,
        "source": LAYER_PAGE,
        "fetched_at": entry.get("fetched_at") or "",
        "feature_count": entry.get("feature_count") or len(geojson.get("features") or []),
        "electric": entry.get("electric"),
        "gas": entry.get("gas"),
        "councils": councils_legend(),
        "geojson": geojson,
    }


def _dataset_regions() -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    if not os.path.exists(zone_intel.DATASET_PATH):
        return index
    with open(zone_intel.DATASET_PATH, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            source = row.get("source_file") or ""
            if source.endswith(".json"):
                source = source[:-5]
            index.setdefault(row.get("orig_name") or "", []).append(source)
    return index


def _card_file(name: str, index: dict[str, list[str]]) -> str:
    matches = [item for item in index.get(name) or [] if item]
    if len(set(matches)) == 1:
        return matches[0]
    return ""


def _groups_for(flags: str, status: str) -> list[str]:
    parts = [part for part in (flags or "").split("|") if part]
    groups = []
    if any(part == "app_zone_not_on_PUCO_electric_map" for part in parts):
        if (status or "").startswith("active"):
            groups.append("active_missing")
        else:
            groups.append("not_on_map")
    if "map_NOPEC_member_vs_app_admin" in parts:
        groups.append("nopec_admin")
    if "app_NOPEC_vs_map_not_NOPEC" in parts:
        groups.append("app_nopec_not_on_map")
    if any(part.startswith("PUCO_electric_listing_vs_app_status") for part in parts):
        groups.append("status_conflict")
    if "ambiguous_multi_county_name" in parts:
        groups.append("ambiguous")
    return groups


def _labels(groups: list[str]) -> str:
    return "; ".join(_GROUP_LABELS[group] for group in groups if group in _GROUP_LABELS)


def load_queue_flags() -> dict:
    """Read the stored crosswalk. Does not change zone records."""
    index = _dataset_regions()
    flags = []
    counts = {
        "active_missing": 0,
        "not_on_map": 0,
        "nopec_admin": 0,
        "app_nopec_not_on_map": 0,
        "status_conflict": 0,
        "ambiguous": 0,
        "flagged_app_rows": 0,
        "prospects": 0,
    }
    if os.path.exists(CROSSWALK_PATH):
        with open(CROSSWALK_PATH, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                groups = _groups_for(row.get("flags") or "", row.get("app_status") or "")
                if not (row.get("flags") or "").strip():
                    continue
                for group in groups:
                    counts[group] += 1
                counts["flagged_app_rows"] += 1
                listing_bits = []
                boundary = (row.get("map_electric_boundary") or "").strip()
                council = (row.get("map_electric_aggregator_council") or "").strip()
                cert = (row.get("map_electric_own_cert") or "").strip()
                if boundary:
                    listing_bits.append(boundary)
                if council:
                    listing_bits.append("Council: " + council)
                if cert:
                    listing_bits.append("Certificate: " + cert)
                if (row.get("map_gas_listed") or "").strip() == "yes":
                    listing_bits.append("Gas polygon also listed")
                if not listing_bits:
                    listing_bits.append("No electric polygon matched")
                name = row.get("app_name") or ""
                flags.append({
                    "kind": "app",
                    "groups": groups,
                    "name": name,
                    "county": row.get("app_county") or "",
                    "flag_label": _labels(groups) or (row.get("flags") or ""),
                    "flags": row.get("flags") or "",
                    "app_status": row.get("app_status") or "",
                    "app_admin": row.get("app_admin") or "",
                    "listing": ". ".join(listing_bits),
                    "action": FLAG_ACTION,
                    "card_file": _card_file(name, index),
                })
    if os.path.exists(NOT_IN_APP_PATH):
        with open(NOT_IN_APP_PATH, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                counts["prospects"] += 1
                cert_bits = [
                    bit for bit in (
                        row.get("CommCertID") or "",
                        row.get("CommCaseRef") or "",
                        row.get("CommIssueDate") or "",
                    ) if bit
                ]
                council = (row.get("AOGCompany") or "").strip()
                listing_bits = [f"{row.get('BoundaryType') or ''} · {row.get('AggType') or ''}".strip(" ·")]
                listing_bits.append("Council: " + council if council else "No council on this polygon")
                if cert_bits:
                    listing_bits.append("Certificate: " + " ".join(cert_bits))
                flags.append({
                    "kind": "prospect",
                    "groups": ["prospect"],
                    "name": row.get("CommunityName") or "",
                    "county": row.get("County") or "",
                    "flag_label": _GROUP_LABELS["prospect"],
                    "flags": "possible_prospect",
                    "app_status": "",
                    "app_admin": "",
                    "listing": ". ".join(listing_bits),
                    "action": PROSPECT_ACTION,
                    "card_file": "",
                })
    return {
        "attribution": ATTRIBUTION,
        "disclaimer": DISCLAIMER,
        "counts": counts,
        "flags": flags,
    }


def filter_flags(flags: list[dict], selected: str) -> list[dict]:
    if selected == "all":
        return flags
    if selected == "prospect":
        return [item for item in flags if item["kind"] == "prospect"]
    if selected in _GROUP_LABELS and selected != "prospect":
        return [item for item in flags if selected in item["groups"]]
    return [item for item in flags if item["kind"] == "app"]
