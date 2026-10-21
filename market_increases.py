"""Market-increase cards for a sales call.

Percents are copied from the research file. This module does not calculate
a percent from two rates. A figure is single-source when fewer than two
sources independently state the percent.
"""

from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(ROOT, "data", "research", "market_increases.json")

REQUIRED_AREAS = (
    "greater-toledo",
    "greater-cleveland",
    "columbus",
    "cincinnati",
    "dayton",
    "akron",
    "youngstown-warren",
    "canton-stark",
    "ohio",
)

_cache: dict | None = None


def _percent_sources(figure: dict) -> list[dict]:
    sources = []
    for source in figure.get("sources") or []:
        if source.get("states_percent") and source.get("independent", True):
            sources.append(source)
    return sources


def _prepare(raw: dict) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("market increases file must be an object")
    figures = {}
    for figure in raw.get("figures") or []:
        figure_id = (figure.get("id") or "").strip()
        if not figure_id or figure_id in figures:
            raise ValueError(f"bad figure id: {figure_id!r}")
        published = (figure.get("percent_as_published") or "").strip()
        if not published:
            raise ValueError(f"{figure_id}: missing percent_as_published")
        for field in ("measure", "utility", "period_label"):
            if not (figure.get(field) or "").strip():
                raise ValueError(f"{figure_id}: missing {field}")
        sources = figure.get("sources") or []
        if not sources:
            raise ValueError(f"{figure_id}: no sources")
        for source in sources:
            for field in ("title", "publisher", "date", "url"):
                if not str(source.get(field) or "").strip():
                    raise ValueError(f"{figure_id}: source missing {field}")
            url = source["url"]
            if not (url.startswith("https://") or url.startswith("http://")):
                raise ValueError(f"{figure_id}: bad url {url}")
            if "states_percent" not in source:
                raise ValueError(f"{figure_id}: source missing states_percent")
        prepared = dict(figure)
        prepared["single_source"] = len(_percent_sources(prepared)) < 2
        figures[figure_id] = prepared

    areas = []
    seen = set()
    for area in raw.get("areas") or []:
        area_id = (area.get("id") or "").strip()
        if area_id not in REQUIRED_AREAS or area_id in seen:
            raise ValueError(f"bad area id: {area_id!r}")
        seen.add(area_id)
        if not (area.get("name") or "").strip() or not (area.get("quote") or "").strip():
            raise ValueError(f"{area_id}: needs a name and a quote")
        resolved = []
        for figure_id in area.get("figure_ids") or []:
            if figure_id not in figures:
                raise ValueError(f"{area_id}: unknown figure {figure_id}")
            resolved.append(figures[figure_id])
        if not resolved:
            raise ValueError(f"{area_id}: needs at least one figure")
        item = dict(area)
        item["figures"] = resolved
        item["url"] = "/market-increases#" + area_id
        areas.append(item)
    missing = [area_id for area_id in REQUIRED_AREAS if area_id not in seen]
    if missing:
        raise ValueError("missing areas: " + ", ".join(missing))
    return {
        "as_of": raw.get("as_of") or "",
        "intro": raw.get("intro") or "",
        "areas": areas,
        "figures": figures,
    }


def load(path: str | None = None) -> dict:
    """Return areas with figures attached. Result is cached for the default file."""
    global _cache
    if path is None and _cache is not None:
        return _cache
    with open(path or PATH, encoding="utf-8") as handle:
        prepared = _prepare(json.load(handle))
    if path is None:
        _cache = prepared
    return prepared


def clear_cache() -> None:
    global _cache
    _cache = None


def match_area(county: str | None, utility: str | None, report: dict | None = None) -> dict:
    """Pick the area card for a zone. Utility locks win over county."""
    report = report or load()
    areas = report["areas"]
    utility_text = (utility or "").lower()
    county_text = (county or "").strip()
    for area in areas:
        if area["id"] == "ohio":
            continue
        for needle in area.get("utility_lock") or []:
            if needle and needle.lower() in utility_text:
                return area
    for area in areas:
        if county_text and county_text in (area.get("counties") or []):
            return area
    for area in areas:
        if area["id"] == "ohio":
            return area
    raise ValueError("statewide area missing")
