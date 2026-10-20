"""Place card for a searched name that is not a zone.

Reads the place index and nearby zones. An optional web lookup stores
unverified leads. It does not write zone data. A fact needs three agreeing
sources before it can become a zone, and this module never makes that call.
"""

from __future__ import annotations

import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

import merged_research
import place_index
import territory

WEB_NOTE = (
    "Unverified web lead. Not written into zone data. "
    "A fact needs three agreeing sources."
)
SERVICE_MUNICIPAL = (
    "Municipal electric is flagged for this place. "
    "Competitive supply is not sold on a municipal system. "
    "The index does not say which streets that system serves."
)
SERVICE_COOP = (
    "An electric cooperative is listed in the utility overlap. "
    "Competitive supply is not sold on a cooperative system."
)
NO_ZONE = "Not a zone on file."
EMPTY_TOWNS = "No nearby towns are on file."
EMPTY_TOWNSHIPS = "No containing or adjacent township is on file."
EMPTY_ZONES = "No anchored zone is nearby."
WEB_EMPTY = "The web lookup did not return results."

_TAG = re.compile(r"\s*\[[^\]]+\]")
_PAREN = re.compile(r"\s*\([^)]*\)")
_SMALL = {"of", "and", "the"}
_STATUS = {
    "pain_hit": "Pain Hit",
    "pain_coming": "Pain Coming",
    "stable": "Stable",
    "transition": "Transition",
    "verify": "Pending",
    "rollover": "Rollover",
    "rollover_dissolved": "Dissolved",
    "pricing_updated": "Pricing Updated",
}
_ROLE = {"containing": "Containing", "adjacent": "Adjacent"}
_ENERGY = re.compile(
    r"\b(electric|electricity|aggregation|aggregator|utility|utilities|power|nopec|puco|edison|firstenergy|municipal)\b",
    re.I,
)
_OHIO = re.compile(r"\bohio\b|\.oh\.us\b|\bpuco\b|\bnopec\b|firstenergy|ohio edison", re.I)


def friendly_utility(raw: str) -> str:
    canonical = place_index._canonical_iou(raw or "")
    if canonical:
        return canonical
    text = _TAG.sub(" ", raw or "")
    text = _PAREN.sub(" ", text)
    text = re.sub(r"\s+-\s*$", "", text)
    text = re.sub(r"\s+", " ", text).strip(" -")
    parts = []
    for index, word in enumerate(text.split()):
        low = word.lower()
        parts.append(low if index and low in _SMALL else low.capitalize())
    return " ".join(parts)


def primary_county(place: dict) -> str:
    counties = place.get("counties") or []
    if not counties:
        return ""

    def share(item: dict) -> float:
        try:
            return float(item.get("share") or 0)
        except (TypeError, ValueError):
            return 0.0

    return (max(counties, key=share).get("name") or "").strip()


def _kind_label(utility: dict, place_name: str) -> str:
    kind = utility.get("kind") or ""
    if kind == "investor_owned":
        return "investor-owned"
    if kind == "municipal":
        return "municipal"
    if kind == "cooperative":
        return "cooperative"
    label = friendly_utility(utility.get("name") or "")
    if place_name and place_index._norm(place_name) in place_index._norm(label):
        return ""
    return ""


def service_lines(place: dict) -> dict:
    """Plain-language utility lines. HIFLD shares stay labeled as overlap."""
    place_name = place.get("name") or ""
    lines = []
    municipal_flag = (place.get("amp") or "").strip().lower() == "yes"
    coop_flag = False
    for utility in place.get("utilities") or []:
        label = friendly_utility(utility.get("name") or "")
        if not label:
            continue
        kind = _kind_label(utility, place_name)
        if kind == "municipal":
            municipal_flag = True
        if kind == "cooperative":
            coop_flag = True
        if kind == "investor-owned":
            lead = f"{label}, investor-owned"
        elif kind == "municipal":
            lead = f"{label}, municipal electric"
        elif kind == "cooperative":
            lead = f"{label}, electric cooperative"
        else:
            lead = label
        share = utility.get("share") or ""
        plain = f"{lead}. {share}% area overlap." if share else f"{lead}."
        lines.append({
            "label": label,
            "kind": kind,
            "share": share,
            "plain": plain,
        })
    if municipal_flag:
        callout = SERVICE_MUNICIPAL
    elif coop_flag:
        callout = SERVICE_COOP
    else:
        callout = ""
    return {
        "lines": lines,
        "callout": callout,
        "municipal": municipal_flag,
        "intro": "Place index utility overlap.",
        "note": place_index.UTILITY_NOTE,
    }


def _sales_status(zone: dict) -> str:
    raw = zone.get("status") or ""
    return _STATUS.get(raw, raw)


def _zone_lookup(zones: list) -> dict:
    found = {}
    for zone in zones:
        if zone.get("superseded"):
            continue
        found.setdefault((zone.get("_source_file") or "", zone.get("name") or ""), zone)
    return found


def _township_rows(place: dict, zones: list) -> list[dict]:
    rows = []
    seen = set()
    for township in place.get("townships") or []:
        matches = [
            zone for zone in zones
            if not zone.get("superseded") and place_index._zone_matches_township(zone, township)
        ]
        role = _ROLE.get(township.get("role") or "", township.get("role") or "")
        if not matches:
            rows.append({
                "label": f"{township.get('name') or ''} township".strip(),
                "county": township.get("county") or "",
                "role": role,
                "status": "No zone on file",
                "supplier": "",
                "rate": "",
                "card_url": "",
                "zone_name": "",
            })
            continue
        for zone in matches:
            item = territory._zone_item(zone, None)
            key = (item.get("name"), township.get("name"), township.get("county"))
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "label": f"{township.get('name') or ''} township".strip(),
                "county": township.get("county") or "",
                "role": role,
                "status": _sales_status(zone) or item.get("status") or "",
                "program": item.get("status") or "",
                "supplier": item.get("supplier") or "",
                "rate": item.get("rate") or "",
                "card_url": item.get("card_url") or "",
                "zone_name": item.get("name") or "",
            })
    return rows


def _closest(nearby_items: list, zones: list) -> list[dict]:
    by_key = _zone_lookup(zones)
    rows = []
    for item in nearby_items or []:
        zone = by_key.get((item.get("region") or "", item.get("name") or ""))
        if zone is None:
            zone = next((
                candidate for candidate in zones
                if not candidate.get("superseded") and candidate.get("name") == item.get("name")
            ), None)
        rows.append({
            "name": item.get("name") or "",
            "miles": item.get("miles"),
            "program": item.get("status") or "",
            "status": _sales_status(zone) if zone else (item.get("status") or ""),
            "supplier": item.get("supplier") or "",
            "rate": item.get("rate") or "",
            "card_url": item.get("card_url") or "",
        })
    return rows


def _towns(nearby_items: list) -> list[dict]:
    rows = []
    for item in nearby_items or []:
        rows.append({
            "name": item.get("name") or "",
            "type": item.get("type") or "",
            "miles": item.get("miles"),
            "status": item.get("status") or "",
            "supplier": item.get("supplier") or "",
            "rate": item.get("rate") or "",
            "card_url": item.get("card_url") or "",
        })
    return rows


def stored_web_leads(name: str, county: str) -> list[dict]:
    leads = []
    for row in merged_research.load_unverified_leads():
        if (row.get("field") or "") != "web_lead":
            continue
        if (row.get("community") or "").casefold() != (name or "").casefold():
            continue
        if county and (row.get("county") or "").casefold() != county.casefold():
            continue
        url = (row.get("sources") or "").strip().split()[0]
        if not url.startswith("http"):
            continue
        leads.append({
            "title": row.get("value") or "",
            "url": url,
            "snippet": "",
            "query": "",
            "label": "Unverified lead",
        })
    return leads[:8]


def build(place: dict, zones: list) -> dict:
    """Battlecard fields for one indexed place. Coordinates stay off the payload."""
    county = primary_county(place)
    county_line = f"{county} County" if county else ""
    coverage = place.get("coverage") or {}
    own = coverage.get("status") == "own" and bool(coverage.get("programs"))
    nearby = place.get("nearby") or {}
    service = service_lines(place)
    programs = []
    for program in coverage.get("programs") or []:
        programs.append({
            "zone": program.get("zone") or "",
            "supplier": program.get("supplier") or "",
            "rate": program.get("rate") or "",
            "card_url": program.get("card_url") or "",
        })
    return {
        "name": place.get("name") or "",
        "type": place.get("type") or "",
        "geoid": place.get("geoid") or "",
        "counties": [
            {"name": item.get("name") or "", "share": item.get("share") or ""}
            for item in (place.get("counties") or [])
        ],
        "county": county,
        "county_line": county_line,
        "headline": "A zone record is on file." if own else NO_ZONE,
        "programs": programs,
        "service": service,
        "townships": _township_rows(place, zones),
        "zones": _closest((nearby.get("zones") or []), zones),
        "towns": _towns(nearby.get("places") or []),
        "nearby_note": nearby.get("note") or "",
        "empty_townships": EMPTY_TOWNSHIPS,
        "empty_zones": EMPTY_ZONES,
        "empty_towns": EMPTY_TOWNS,
        "web_leads": stored_web_leads(place.get("name") or "", county),
        "web_note": WEB_NOTE,
    }


def queries_for(name: str, county: str) -> list[str]:
    place = (name or "").strip()
    quoted = f'"{place}, Ohio"'
    queries = [f"{quoted} electric aggregation", f"{quoted} electric utility"]
    if (county or "").strip():
        queries.append(f"{quoted} {(county or '').strip()} County municipal electric")
    else:
        queries.append(f"{quoted} municipal electric")
    return queries


def relevant_lead(name: str, item: dict) -> bool:
    """Keep energy pages about Ohio. A brand that only shares the place name is dropped."""
    blob = " ".join([
        item.get("title") or "",
        item.get("snippet") or "",
        item.get("url") or "",
    ])
    if not _ENERGY.search(blob) or not _OHIO.search(blob):
        return False
    return True


def _clean_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 280:
        text = text[:277].rstrip() + "…"
    return text


def parse_rss(xml_text: str) -> list[dict]:
    """Titles and links from an RSS search result. Non-RSS input yields nothing."""
    try:
        root = ET.fromstring(xml_text or "")
    except ET.ParseError:
        return []
    leads = []
    for item in root.iter("item"):
        title = _clean_text("".join(item.findtext("title") or ""))
        link = (item.findtext("link") or "").strip()
        snippet = _clean_text(item.findtext("description") or "")
        if not title or not link.startswith("http"):
            continue
        leads.append({"title": title, "url": link, "snippet": snippet})
    return leads


def fetch_bing(query: str) -> list[dict]:
    """Bing's public RSS search. A failure returns no leads."""
    url = "https://www.bing.com/search?format=rss&q=" + urllib.parse.quote(query)
    request = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; FORGE-place-lookup/1.0)",
        "Accept": "application/rss+xml, application/xml, text/xml",
    })
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            body = response.read(200_000).decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return []
    return parse_rss(body)


def search_web(name: str, county: str, fetch=None) -> list[dict]:
    fetch = fetch or fetch_bing
    found = []
    seen = set()
    for query in queries_for(name, county):
        try:
            hits = fetch(query) or []
        except Exception:
            hits = []
        for item in hits[:6]:
            url = (item.get("url") or "").strip()
            title = _clean_text(item.get("title") or "")
            if not title or not url.startswith("http") or url in seen:
                continue
            if not relevant_lead(name, {"title": title, "url": url, "snippet": item.get("snippet") or ""}):
                continue
            seen.add(url)
            found.append({
                "title": title,
                "url": url,
                "snippet": _clean_text(item.get("snippet") or ""),
                "query": query,
                "label": "Unverified lead",
            })
            if len(found) >= 8:
                return found
    return found


def store_web_leads(name: str, county: str, leads: list[dict]) -> int:
    rows = []
    for lead in leads:
        rows.append({
            "community": name,
            "county": county,
            "field": "web_lead",
            "value": (lead.get("title") or "")[:240],
            "confidence": "single-source",
            "sources": lead.get("url") or "",
            "notes": f"Query: {lead.get('query') or ''}. {WEB_NOTE}",
            "flag": "unverified web lead",
        })
    return merged_research.append_unverified_rows(rows)


def lookup_web(place: dict, fetch=None) -> dict:
    """Run the optional search and store leads. Zone files are not touched."""
    name = place.get("name") or ""
    county = primary_county(place)
    leads = search_web(name, county, fetch=fetch)
    stored = store_web_leads(name, county, leads) if leads else 0
    return {
        "ok": True,
        "place": name,
        "county": county,
        "geoid": place.get("geoid") or "",
        "queries": queries_for(name, county),
        "leads": leads,
        "stored": stored,
        "note": WEB_NOTE,
        "message": "" if leads else WEB_EMPTY,
    }


def lookup_web_by_geoid(geoid, fetch=None) -> tuple[dict, int]:
    if not isinstance(geoid, str) or not re.fullmatch(r"\d{5,12}", geoid):
        return {"ok": False, "message": "A place is required."}, 400
    place = next((item for item in place_index.load_places() if item.get("geoid") == geoid), None)
    if place is None:
        return {"ok": False, "message": "No place with that id is in the index."}, 404
    return lookup_web(place, fetch=fetch), 200
