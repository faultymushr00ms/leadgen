"""Display-only talking points for a town battlecard.

Points are built from dated, linked records already on the card, the news
sweep, and sourced county or nearby program rates. Nothing here writes a
rate, a verification, or a region file. A point without a source URL and a
date is dropped. Wording stays executive: research-log phrases are not used.
"""

from __future__ import annotations

import csv
import os
import re
from datetime import date
from urllib.parse import urlparse

import business_default
import presentation
import rate_change
import territory
import zone_intel

ROOT = os.path.dirname(os.path.abspath(__file__))
NEWS_PATH = os.path.join(ROOT, "data", "research", "news_council_sweep.csv")

# Research vintage for this brief. Upcoming means on or after this day.
AS_OF = date(2026, 10, 16)

_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
_MONTH_NAME = {
    1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
    7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December",
}
_HOST_LABELS = {
    "cleveland.com": "cleveland.com",
    "westlifenews.com": "West Life",
    "energychoice.ohio.gov": "PUCO Apples to Apples",
    "dynegy.com": "Dynegy",
    "nopec.org": "NOPEC",
    "sopec-oh.gov": "SOPEC",
    "dis.puc.state.oh.us": "PUCO DIS",
    "hoodline.com": "Hoodline",
    "firstenergycorp.com": "Utility tariff",
    "aepohio.com": "AEP Ohio tariff",
}
_BANNED = re.compile(
    r"needs call|not confirmed|not in sources|not marked inactive|verify before using|"
    r"\bverify\b|\bunconfirmed\b|\bescalate\b|\bunresolved\b|single-source|forge recorded",
    re.I,
)
_news_cache: list | None = None

_CONFIDENCE_TITLE = {
    "confirmed": "Stated in the cited source.",
    "likely": "Cited source. Supporting detail is in Evidence & notes.",
    "single": "One cited source.",
}
_CHIP = {
    "town": "This town",
    "utility": "Utility default",
    "county": "County contract",
    "nearby": "Nearby rate",
}


def attach(zones: list) -> None:
    """Add card['talkingPoints']. Does not change stored zone fields."""
    news = _load_news()
    for zone in zones:
        card = zone.get("card")
        if not card:
            continue
        card["talkingPoints"] = for_zone(zone, zones, news)


def for_zone(zone: dict, zones: list, news: list | None = None) -> dict:
    news = _load_news() if news is None else news
    card = zone.get("card") or {}
    info = business_default.display_for(zone)
    lead = _is_lead(card) or bool(info.get("applies"))
    points = []
    points.extend(_news_points(zone, card, news))
    points.extend(_record_points(zone, card, points, info))
    if _needs_context(points):
        points.extend(_context_points(zone, card, zones, points))
    points = _dedupe(points)
    points = _trim(points)
    points = [point for point in points if _publishable(point)]
    groups = _groups(points)
    town_news = any(point.get("origin") == "news" for point in points)
    return {
        "lead": lead,
        "intro": _intro(lead, card, town_news, points, info),
        "framing": _framing(town_news, points, lead),
        "points": points,
        "groups": groups,
        "evidence": [
            {
                "sentence": point["sentence"],
                "dateLabel": point["dateLabel"],
                "sourceUrl": point["sourceUrl"],
                "sourceLabel": point["sourceLabel"],
                "quote": point.get("quote") or "",
                "chip": point["chip"],
            }
            for point in points
        ],
    }


def _is_lead(card: dict) -> bool:
    """No running program: local record leads, and the rate grid follows it."""
    if card.get("notEligible"):
        return False
    lifecycle = ((card.get("lifecycle") or {}).get("status") or "")
    if lifecycle in {"ended", "certified_not_launched", "seeking_supplier", "rate_pending"}:
        return True
    program = (card.get("program") or "").lower()
    if program.startswith("ended") or "no_program" in program:
        return True
    return False


def _intro(lead: bool, card: dict, town_news: bool, points: list, info: dict | None = None) -> str:
    if info and info.get("applies") and info.get("headline"):
        return info["headline"]
    if not lead or not points:
        return ""
    lifecycle = ((card.get("lifecycle") or {}).get("status") or "")
    program = (card.get("program") or "").lower()
    ended = lifecycle == "ended" or program.startswith("ended")
    if ended:
        return "The aggregation program has ended. Lead with the local record and the utility default."
    return "No aggregation program is in force. Lead with the utility default and nearby contracts."


def _framing(town_news: bool, points: list, lead: bool) -> str:
    if town_news or not points:
        return ""
    if any(point["scope"] == "town" and point["bucket"] == "fact" for point in points):
        return ""
    if lead:
        return "No dated town news is on file. Utility and nearby lines are comparisons, not a program in this town."
    return "No dated town news is on file. Utility and nearby lines are comparisons beside the rate record."


def _needs_context(points: list) -> bool:
    townish = [point for point in points if point["scope"] == "town"]
    return len(points) < 4 or len(townish) < 2


def _load_news() -> list:
    global _news_cache
    if _news_cache is not None:
        return _news_cache
    rows = []
    if os.path.exists(NEWS_PATH):
        with open(NEWS_PATH, newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    _news_cache = rows
    return rows


def _news_points(zone: dict, card: dict, news: list) -> list:
    county = _county_name(zone)
    key = _place_key(zone.get("name") or card.get("jurisdiction") or "")
    found = []
    for row in news:
        if _place_key(row.get("community") or "") != key:
            continue
        row_county = (row.get("county") or "").strip().lower()
        if county and row_county and row_county != county and county not in row_county and row_county not in county:
            continue
        if _skip_news_row(row):
            continue
        if _contradicts_live_program(row, card):
            continue
        point = _point_from_news(row, card)
        if point:
            found.append(point)
    return found


def _skip_news_row(row: dict) -> bool:
    quote = (row.get("quote") or "").strip().lower()
    flag = (row.get("flag") or "").lower()
    url = (row.get("source_url") or "").strip()
    if not url.startswith("http"):
        return True
    if "unavailable" in quote or "quote unavailable" in flag:
        return True
    if not (row.get("event_date") or row.get("source_pub_date")):
        return True
    return False


def _contradicts_live_program(row: dict, card: dict) -> bool:
    event = (row.get("event_type") or "").lower()
    if "ended" not in event and "paused" not in event:
        return False
    if not card.get("currentSourced"):
        return False
    if zone_intel.basis_family(card.get("currentBasis")) != "aggregation":
        return False
    end = _parse_date(card.get("currentEnd"))
    return end is None or end >= AS_OF


def _point_from_news(row: dict, card: dict) -> dict | None:
    name = (row.get("community") or "").strip()
    event = (row.get("event_type") or "").strip().lower()
    when = _parse_date(row.get("event_date")) or _parse_date(row.get("source_pub_date"))
    if when is None:
        return None
    supplier = _clean_supplier(row.get("supplier") or "")
    rate_text = row.get("rate_cents_kwh") or ""
    rate = _first_number(rate_text)
    term = (row.get("term") or "").strip()
    horizon = _horizon(term, when, event)
    sentence = _news_sentence(name, event, when, supplier, rate, rate_text, term)
    if not sentence:
        return None
    timing = "recent" if ("ended" in event or "paused" in event or horizon < AS_OF) else "upcoming"
    if "ballot" in event and when >= AS_OF:
        timing = "upcoming"
    bucket = "question" if _open_item(event, rate_text, term) else "fact"
    confidence = "confirmed" if "second source" in (row.get("flag") or "").lower() or (row.get("flag") or "").lower().startswith("match") else "single"
    # A second independent URL in the same sweep for this event is handled by
    # dedupe; a single article stays a single cited source.
    return _make_point(
        timing=timing,
        bucket=bucket,
        scope="town",
        sentence=sentence,
        when=when if timing == "recent" else horizon,
        source_url=row.get("source_url") or "",
        confidence=confidence,
        quote=_clean_quote(row.get("quote") or ""),
        origin="news",
        horizon=horizon,
    )


def _open_item(event: str, rate_text: str, term: str) -> bool:
    blob = f"{event} {rate_text} {term}".lower()
    return "not yet set" in blob or "rate_coming" in event or "seeking_supplier" in event or "ballot_issue" in event


def _news_sentence(name, event, when, supplier, rate, rate_text, term) -> str:
    when_label = _format_date(when)
    rate_clause = _rate_clause(rate_text, rate)
    term_clause = _term_clause(term)
    supplier_bit = f"{supplier} " if supplier else ""
    if "ended" in event or "paused" in event:
        if rate and "reject" in rate_text.lower():
            return f"{name} rejected a long-term supplier offer of { _fmt_cents(rate) }¢/kWh."
        if supplier:
            return f"{name} ended its {supplier} aggregation program in {when_label}."
        return f"{name} ended its aggregation program in {when_label}."
    if "ballot_passed" in event:
        return f"{name} voters approved aggregation authority on {when_label}."
    if "ballot" in event:
        return f"{name} has an aggregation ballot dated {when_label}."
    if event.startswith("rfp"):
        if supplier and "selection" in event:
            return f"{name} moved ahead with {supplier} after its {when_label} supply request{term_clause}."
        return f"{name} issued an aggregation supply request on {when_label}."
    if "supplier_change" in event or "new_supplier" in event or "supplier_selection" in event or "new_program" in event:
        bits = f"{name} selected {supplier_bit.strip() or 'a supplier'}"
        if rate_clause:
            bits += f" at {rate_clause}"
        bits += f" ({when_label}){term_clause}."
        return _one_sentence(bits)
    if "rate_increase" in event or "renewal" in event or "opt_out" in event or "rfp_and_new_rate" in event:
        if rate_clause and supplier:
            return _one_sentence(f"{name}'s {supplier} program is {rate_clause}{term_clause}.")
        if rate_clause:
            return _one_sentence(f"{name}'s aggregation rate is {rate_clause}{term_clause}.")
        if supplier:
            return f"{name} sent an aggregation notice for {supplier} on {when_label}."
        return f"{name} issued an aggregation notice on {when_label}."
    if rate_clause and supplier:
        return _one_sentence(f"{name}'s {supplier} aggregation is {rate_clause}{term_clause}.")
    if supplier:
        return f"{name} took an aggregation step with {supplier} on {when_label}."
    return ""


def _record_points(zone: dict, card: dict, existing: list, info: dict | None = None) -> list:
    research = zone.get("research") or {}
    name = card.get("jurisdiction") or zone.get("name") or ""
    supplier = _clean_supplier(card.get("supplier") or "")
    verification = (card.get("verification") or "").strip()
    confidence = _confidence_from_verification(verification)
    points = []
    current_basis = zone_intel.basis_family(card.get("currentBasis"))
    if card.get("currentSourced") and current_basis == "aggregation" and card.get("currentLabel"):
        sentence = _program_sentence(
            name, card.get("administrator") or "", supplier,
            card.get("currentLabel"), card.get("currentStart"), card.get("currentEnd"),
        )
        end = _end_or_start(card.get("currentEnd"), card.get("currentStart"))
        if sentence and end and _first_url(card.get("currentSource")):
            points.append(_make_point(
                timing="upcoming" if end >= AS_OF else "recent",
                bucket="fact",
                scope="town",
                sentence=sentence,
                when=end,
                source_url=card.get("currentSource") or "",
                confidence=confidence,
                origin="record",
                horizon=end,
            ))
    if card.get("futureSourced") and card.get("futureLabel") and _first_url(card.get("futureSource")):
        start = _parse_date(card.get("futureStart"))
        end = _parse_date(card.get("futureEnd"))
        horizon = end or start
        if horizon:
            window = _window_phrase(card.get("futureStart"), card.get("futureEnd"))
            who = supplier or "The supplier"
            sentence = f"{who} lists a {name} aggregation rate of {_fmt_cents(card.get('futureLabel'))}¢/kWh{window}."
            points.append(_make_point(
                timing="upcoming" if horizon >= AS_OF else "recent",
                bucket="fact",
                scope="town",
                sentence=_one_sentence(sentence),
                when=start or horizon,
                source_url=card.get("futureSource") or "",
                confidence="single" if verification in zone_intel.UNRESOLVED_VERIFICATIONS else confidence,
                origin="record",
                horizon=horizon,
            ))
    if card.get("priorSourced") and card.get("priorLabel") and _first_url(card.get("priorSource")):
        if not _rate_already_used(card.get("priorLabel"), existing + points):
            window = _prior_window(card.get("priorTerm") or "")
            who = supplier or "The prior supplier"
            clause = rate_change.matching_percent_clause(
                zone, card.get("priorLabel"), card.get("currentLabel"),
            )
            sentence = (
                f"The last aggregation rate on file is {who} at "
                f"{_fmt_cents(card.get('priorLabel'))}¢/kWh{window}{clause}."
            )
            when = _parse_date(card.get("priorTerm")) or _last_date_in(card.get("priorTerm") or "")
            if when:
                points.append(_make_point(
                    timing="recent",
                    bucket="fact",
                    scope="town",
                    sentence=_one_sentence(sentence),
                    when=when,
                    source_url=card.get("priorSource") or "",
                    confidence=confidence if confidence != "single" else "likely",
                    origin="record",
                    horizon=when,
                ))
    benchmark = _rate_benchmark(card.get("ptc") or {})
    if benchmark:
        aggregation_live = any(
            point["scope"] == "town"
            and point["bucket"] == "fact"
            and point.get("origin") == "record"
            and "last aggregation rate" not in point["sentence"].lower()
            for point in existing + points
        )
        end = benchmark["end"]
        when = benchmark["when"]
        origin = "commercial" if benchmark["kind"] == "commercial" else "ptc"
        timing = "upcoming" if benchmark["in_force"] else "recent"
        if when and (not aggregation_live or _is_lead(card)):
            utility = _utility_subject(benchmark["utility"])
            if benchmark["kind"] == "commercial":
                sentence = f"{utility} GS default is {_fmt_cents(benchmark['cents'])}¢/kWh{benchmark['window']}."
                if info and info.get("applies") and info.get("movement") and info.get("priorText"):
                    whose = info.get("supplier") or "the last aggregation"
                    sentence = (
                        f"{utility} GS default is {_fmt_cents(benchmark['cents'])}¢/kWh"
                        f"{benchmark['window']}, {info['movement']} from {whose} {info['priorText']}¢."
                    )
            else:
                sentence = f"{utility} residential Price to Compare is {_fmt_cents(benchmark['cents'])}¢/kWh{benchmark['window']}."
            points.append(_make_point(
                timing=timing,
                bucket="fact",
                scope="utility",
                sentence=_one_sentence(sentence),
                when=when,
                source_url=benchmark["source_url"],
                confidence="confirmed",
                origin=origin,
                horizon=end or when,
            ))
        elif when and aggregation_live and not _is_lead(card):
            own = _own_rate(existing + points)
            if own is not None:
                delta = own - float(benchmark["cents"])
                direction = "under" if delta < 0 else "over"
                noun = "GS default" if benchmark["kind"] == "commercial" else "residential Price to Compare"
                sentence = (
                    f"That {_fmt_cents(own)}¢ rate is {abs(delta):.3f}¢ {direction} "
                    f"{_utility_object(benchmark['utility'])} {noun} of "
                    f"{_fmt_cents(benchmark['cents'])}¢/kWh."
                )
                points.append(_make_point(
                    timing=timing,
                    bucket="comparison",
                    scope="utility",
                    sentence=sentence,
                    when=when,
                    source_url=benchmark["source_url"],
                    confidence="confirmed",
                    origin=origin,
                    horizon=end or when,
                ))
    return points


def _rate_benchmark(ptc: dict) -> dict | None:
    """Commercial GS default when the tariff states one, otherwise residential PTC."""
    commercial = ptc.get("commercial") or {}
    if commercial.get("sourced") and commercial.get("cents_per_kwh") is not None and commercial.get("source_url"):
        start = commercial.get("effective_start")
        end = commercial.get("effective_end")
        end_d = _parse_date(end)
        start_d = _parse_date(start)
        when = end_d or start_d
        if when is None:
            return None
        return {
            "kind": "commercial",
            "cents": commercial.get("cents_per_kwh"),
            "utility": commercial.get("utility") or ptc.get("utility") or "",
            "source_url": commercial.get("source_url") or "",
            "window": _window_phrase(start, end, full=True),
            "end": end_d,
            "when": when,
            "in_force": end_d is None or end_d >= AS_OF,
            "label": "GS default",
        }
    if ptc.get("applicable") and ptc.get("cents_per_kwh") is not None and ptc.get("source_url"):
        end_d = _parse_date(ptc.get("effective_end"))
        start_d = _parse_date(ptc.get("effective_start"))
        when = end_d or start_d
        if when is None:
            return None
        return {
            "kind": "residential",
            "cents": ptc.get("cents_per_kwh"),
            "utility": ptc.get("utility") or "",
            "source_url": ptc.get("source_url") or "",
            "window": _window_phrase(ptc.get("effective_start"), ptc.get("effective_end"), full=True),
            "end": end_d,
            "when": when,
            "in_force": (end_d or when) >= AS_OF,
            "label": "Price to Compare",
        }
    return None


def _context_points(zone: dict, card: dict, zones: list, existing: list) -> list:
    benchmark = _rate_benchmark(card.get("ptc") or {})
    if not benchmark:
        return []
    local = float(benchmark["cents"])
    utility = benchmark["utility"] or "the utility"
    benchmark_label = benchmark["label"]
    county = _county_name(zone)
    points = []
    used_urls = {_first_url(point.get("sourceUrl")) for point in existing}
    if county:
        for other in zones:
            if other is zone or not other.get("card"):
                continue
            other_name = other.get("name") or ""
            if _county_name(other) != county:
                continue
            if _place_key(other_name) != f"county {county}":
                continue
            point = _comparison_point(
                other, local, utility, scope="county",
                lead=f"{other_name}'s separate contract",
                miles=None,
                benchmark_label=benchmark_label,
            )
            if point and _rate_already_used(_cents_in(point["sentence"]), existing + points):
                point = None
            if point and _first_url(point["sourceUrl"]) not in used_urls:
                points.append(point)
                used_urls.add(_first_url(point["sourceUrl"]))
                break
    try:
        nearby = territory.nearby_for_zone(zone, zones)
    except Exception:
        nearby = {}
    by_name = {}
    for other in zones:
        by_name.setdefault(other.get("name") or "", []).append(other)
    for item in (nearby.get("zones") or [])[:8]:
        matches = by_name.get(item.get("name") or "") or []
        if len(matches) != 1:
            continue
        other = matches[0]
        if other is zone:
            continue
        point = _comparison_point(
            other, local, utility, scope="nearby",
            lead=f"Nearby {other.get('name')} ({item.get('miles')} mi)",
            miles=item.get("miles"),
            benchmark_label=benchmark_label,
        )
        if not point:
            continue
        url = _first_url(point["sourceUrl"])
        if url in used_urls:
            continue
        if _rate_already_used(_cents_in(point["sentence"]), existing + points):
            continue
        points.append(point)
        used_urls.add(url)
        if len(points) >= 2:
            break
    return points


def _comparison_point(other: dict, local: float, utility: str, scope: str, lead: str, miles, benchmark_label: str = "Price to Compare") -> dict | None:
    card = other.get("card") or {}
    if not card.get("currentSourced"):
        return None
    if zone_intel.basis_family(card.get("currentBasis")) != "aggregation":
        return None
    rate = zone_intel.parse_rate(card.get("currentLabel"))
    url = _first_url(card.get("currentSource"))
    if rate is None or not url:
        return None
    end = _parse_date(card.get("currentEnd")) or _parse_date(card.get("currentStart"))
    if end is None:
        return None
    supplier = _clean_supplier(card.get("supplier") or "") or "aggregation"
    delta = rate - local
    direction = "under" if delta < 0 else "over"
    window = _window_phrase(card.get("currentStart"), card.get("currentEnd"))
    if scope == "county":
        sentence = (
            f"{lead} with {supplier} is {_fmt_cents(rate)}¢/kWh{window}, "
            f"{abs(delta):.3f}¢ {direction} this {utility} {benchmark_label} of {_fmt_cents(local)}¢."
        )
    else:
        sentence = (
            f"{lead} is on {supplier} at {_fmt_cents(rate)}¢/kWh{window}, "
            f"{abs(delta):.3f}¢ {direction} this {utility} {benchmark_label} of {_fmt_cents(local)}¢."
        )
    verification = (card.get("verification") or "").strip()
    return _make_point(
        timing="upcoming" if end >= AS_OF else "recent",
        bucket="comparison",
        scope=scope,
        sentence=_one_sentence(sentence),
        when=end,
        source_url=url,
        confidence=_confidence_from_verification(verification),
        origin="comparison",
        horizon=end,
    )


def _program_sentence(name, administrator, supplier, rate, start, end) -> str:
    window = _window_phrase(start, end)
    admin = re.sub(r"\s*\([^)]*\)", "", administrator or "").strip()
    if admin and "county" in admin.lower() and supplier:
        return _one_sentence(f"{name} is on the {admin} {supplier} aggregation at {_fmt_cents(rate)}¢/kWh{window}.")
    if supplier:
        return _one_sentence(f"{name}'s {supplier} aggregation rate is {_fmt_cents(rate)}¢/kWh{window}.")
    return _one_sentence(f"{name}'s aggregation rate is {_fmt_cents(rate)}¢/kWh{window}.")


def _make_point(*, timing, bucket, scope, sentence, when: date, source_url, confidence, origin, horizon: date, quote="") -> dict:
    confidence = confidence if confidence in _CONFIDENCE_TITLE else "single"
    if bucket == "question":
        chip = "Open item"
    elif bucket == "comparison" and scope == "utility":
        chip = "Vs commercial default" if origin == "commercial" else "Vs Price to Compare"
    elif origin == "commercial":
        chip = "Commercial default"
    else:
        chip = _CHIP.get(scope, "This town")
    mark = _display_mark(confidence, bucket)
    return {
        "timing": timing,
        "bucket": bucket,
        "scope": scope,
        "chip": chip,
        "sentence": sentence,
        "dateLabel": _format_date(when),
        "horizon": horizon.isoformat(),
        "sourceUrl": _first_url(source_url),
        "sourceLabel": _source_label(source_url),
        "confidence": confidence,
        "confidenceTitle": mark["tip"],
        "mark": mark,
        "quote": quote if quote and not _BANNED.search(quote) else "",
        "origin": origin,
    }


def _display_mark(confidence: str, bucket: str) -> dict:
    """Map a point onto the card's solid, hollow, or pending mark."""
    if bucket == "question":
        return presentation.confidence_mark("pending")
    if confidence == "confirmed":
        return presentation.confidence_mark("confirmed")
    return presentation.confidence_mark("likely")


def _publishable(point: dict) -> bool:
    if not point.get("sentence") or not point.get("dateLabel"):
        return False
    if not (point.get("sourceUrl") or "").startswith("http"):
        return False
    if _BANNED.search(point["sentence"]) or _BANNED.search(point.get("chip") or ""):
        return False
    if _BANNED.search(point.get("confidenceTitle") or ""):
        return False
    return True


def _dedupe(points: list) -> list:
    kept = []
    seen = set()
    for point in points:
        key = (point["sentence"].lower(), point["sourceUrl"])
        if key in seen:
            continue
        seen.add(key)
        kept.append(point)
    return kept


def _trim(points: list) -> list:
    upcoming = [point for point in points if point["timing"] == "upcoming"]
    recent = [point for point in points if point["timing"] == "recent"]
    upcoming.sort(key=lambda point: (_scope_rank(point), point["horizon"]))
    recent.sort(key=lambda point: point["horizon"], reverse=True)
    recent.sort(key=lambda point: _scope_rank(point))
    ordered = upcoming + recent
    core = [point for point in ordered if point["scope"] != "nearby"]
    extras = [point for point in ordered if point["scope"] == "nearby"]
    chosen = core[:4]
    for point in extras:
        if len(chosen) >= 4:
            break
        if len(chosen) >= 2 and point["scope"] == "nearby" and sum(1 for item in chosen if item["scope"] == "town") >= 2:
            continue
        chosen.append(point)
    upcoming = [point for point in chosen if point["timing"] == "upcoming"]
    recent = [point for point in chosen if point["timing"] == "recent"]
    upcoming.sort(key=lambda point: (_scope_rank(point), point["horizon"]))
    recent.sort(key=lambda point: point["horizon"], reverse=True)
    recent.sort(key=lambda point: _scope_rank(point))
    return (upcoming + recent)[:4]


def _groups(points: list) -> list:
    groups = []
    upcoming = [point for point in points if point["timing"] == "upcoming"]
    recent = [point for point in points if point["timing"] == "recent"]
    if upcoming:
        groups.append({"label": "Upcoming", "points": upcoming})
    if recent:
        groups.append({"label": "Recent", "points": recent})
    return groups


def _scope_rank(point: dict) -> int:
    return {"town": 0, "utility": 1, "county": 2, "nearby": 3}.get(point.get("scope"), 9)


def _confidence_from_verification(verification: str) -> str:
    if verification in {"confirmed"}:
        return "confirmed"
    if verification in {"likely"}:
        return "likely"
    return "single"


def _county_name(zone: dict) -> str:
    research = zone.get("research") or {}
    raw = (research.get("county") or "").split(";")[0].split("/")[0]
    return raw.strip().lower()


def _place_key(name: str) -> str:
    text = re.sub(r"\([^)]*\)", " ", name or "")
    text = text.lower().replace("twp.", " township").replace(" twp", " township")
    if re.search(r"\bcounty\b", text) and not re.search(r"\b(township|village|city)\b", text):
        text = re.sub(r"\bcounty\b", " ", text)
        text = re.sub(r"[^a-z0-9]+", " ", text).strip()
        return f"county {text}"
    text = re.sub(r"\b(city|village)\b", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _clean_supplier(text: str) -> str:
    raw = (text or "").strip()
    if not raw:
        return ""
    low = raw.lower()
    if any(token in low for token in ("tbd", "not named", "none found", "n/a", "utility default")):
        return ""
    if low.startswith("none"):
        return ""
    cleaned = re.sub(r"\s*\([^)]*\)", "", raw).strip(" -")
    return cleaned


def _first_number(value) -> float | None:
    return zone_intel.parse_rate(value)


def _fmt_cents(value) -> str:
    number = zone_intel.parse_rate(value)
    if number is None:
        return str(value)
    text = f"{number:.4f}".rstrip("0").rstrip(".")
    return text


def _rate_clause(rate_text: str, rate: float | None) -> str:
    if rate is None:
        return ""
    low = (rate_text or "").lower()
    if "not to exceed" in low or low.startswith("cap"):
        return f"not to exceed {_fmt_cents(rate)}¢/kWh"
    return f"{_fmt_cents(rate)}¢/kWh"


def _term_clause(term: str) -> str:
    text = (term or "").strip()
    if not text or text.lower() in {"not stated", "n/a"}:
        return ""
    return f", {text}"


def _window_phrase(start, end, full: bool = False) -> str:
    start_d = _parse_date(start)
    end_d = _parse_date(end)
    if start_d and end_d:
        return f" from {_format_date(start_d, full=full or _has_day(start))} through {_format_date(end_d, full=full or _has_day(end))}"
    if end_d:
        return f" through {_format_date(end_d, full=full or _has_day(end))}"
    if start_d:
        return f" from {_format_date(start_d, full=full or _has_day(start))}"
    return ""


def _prior_window(term: str) -> str:
    dates = _all_dates(term)
    if len(dates) >= 2:
        return f" from {_format_date(dates[0])} through {_format_date(dates[-1])}"
    if dates:
        return f" through {_format_date(dates[-1])}"
    return ""


def _has_day(value) -> bool:
    return bool(re.search(r"\d{4}-\d{2}-\d{2}", str(value or "")))


def _format_date(value: date, full: bool = False) -> str:
    if full or value.day not in (1,):
        # Year-month values are stored as day 1 unless the source had a day.
        if value.day == 1 and not full:
            return f"{_MONTH_NAME[value.month]} {value.year}"
        return f"{_MONTH_NAME[value.month]} {value.day}, {value.year}"
    return f"{_MONTH_NAME[value.month]} {value.year}"


def _parse_date(value) -> date | None:
    dates = _all_dates(value)
    return dates[0] if dates else None


def _last_date_in(value) -> date | None:
    dates = _all_dates(value)
    return dates[-1] if dates else None


def _end_or_start(end, start) -> date | None:
    return _parse_date(end) or _parse_date(start)


def _all_dates(value) -> list[date]:
    text = str(value or "")
    found = []
    for match in re.finditer(r"(20\d{2})-(\d{2})(?:-(\d{2}))?", text):
        year, month = int(match.group(1)), int(match.group(2))
        day = int(match.group(3) or 1)
        if 1 <= month <= 12 and 1 <= day <= 31:
            try:
                found.append(date(year, month, day))
            except ValueError:
                continue
    if found:
        return found
    for match in re.finditer(
        r"\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\.?\s+(?:(\d{1,2})(?:st|nd|rd|th)?,?\s+)?(20\d{2})\b",
        text,
        re.I,
    ):
        month = _MONTHS[match.group(1).lower()[:3]]
        day = int(match.group(2) or 1)
        try:
            found.append(date(int(match.group(3)), month, day))
        except ValueError:
            continue
    return found


def _horizon(term: str, event: date, event_type: str) -> date:
    dates = _all_dates(term)
    if dates and "ended" not in event_type and "paused" not in event_type:
        return max(dates)
    return event


def _first_url(text: str) -> str:
    match = re.search(r"https?://[^\s|\"']+", text or "")
    if not match:
        return ""
    return match.group(0).rstrip(".,);")


def _source_label(url: str) -> str:
    host = urlparse(_first_url(url)).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if host in _HOST_LABELS:
        return _HOST_LABELS[host]
    for known, label in _HOST_LABELS.items():
        if host.endswith(known):
            return label
    return host or "Source"


def _clean_quote(quote: str) -> str:
    text = re.sub(r"\s+", " ", (quote or "").strip())
    if _BANNED.search(text):
        return ""
    if len(text) > 280:
        text = text[:277].rstrip() + "…"
    return text


def _one_sentence(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", (text or "").strip())
    cleaned = cleaned.replace("..", ".")
    if cleaned and not cleaned.endswith("."):
        cleaned += "."
    return cleaned


def _cents_in(sentence: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*¢", sentence or "")
    return float(match.group(1)) if match else None


def _rate_already_used(rate, points: list) -> bool:
    number = zone_intel.parse_rate(rate)
    if number is None:
        return False
    token = _fmt_cents(number)
    return any(token in (point.get("sentence") or "") for point in points)


def _utility_subject(utility: str | None) -> str:
    name = (utility or "utility").strip() or "utility"
    if name.lower().startswith("the "):
        return name[0].upper() + name[1:]
    return f"The {name}"


def _utility_object(utility: str | None) -> str:
    name = (utility or "utility").strip() or "utility"
    if name.lower().startswith("the "):
        return name[0].lower() + name[1:]
    return f"the {name}"


def _own_rate(points: list) -> float | None:
    for point in points:
        if point.get("scope") != "town" or point.get("origin") != "record" or point.get("bucket") != "fact":
            continue
        if "last aggregation rate" in (point.get("sentence") or "").lower():
            continue
        match = re.search(r"(\d+(?:\.\d+)?)\s*¢", point.get("sentence") or "")
        if match:
            return float(match.group(1))
    return None
