"""Display price for zones whose aggregation ended or never started.

Businesses in those zones buy generation from the utility. The headline
current figure is that utility's small-commercial default in
``data/research/commercial_ptc.json`` (energy plus capacity, generation
only). The percent compares that default with the last aggregation rate.

Stored zone rates, research rows, and residential Price to Compare values
are left as recorded. A utility with no commercial row shows an em dash.
"""

from __future__ import annotations

import re

import rate_change
import zone_intel

_MONTHS = (
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)
_DATE = re.compile(r"(20\d{2})-(\d{2})(?:-(\d{2}))?")
_CAPTION = "Local business default (generation only)"


def display_for(zone: dict) -> dict:
    """Derived headline price for one zone. Does not write zone fields."""
    if not _applies(zone):
        return _empty()
    research = zone.get("research") or {}
    utility = (research.get("utility") or zone.get("utility") or "").strip()
    residential = zone_intel.ptc_for_utility(utility) or {}
    commercial = zone_intel.commercial_for_code(residential.get("code")) if residential else None
    prior, supplier = _last_aggregation(zone, rate_change.as_float(residential.get("cents_per_kwh")))
    ended, ended_label = _ended(zone)
    code = (commercial or {}).get("code") or residential.get("code") or ""
    if not commercial:
        headline = _missing_headline(ended, ended_label, utility)
        return _pack(
            sourced=False,
            utility=utility,
            code=code,
            prior=prior,
            supplier=supplier,
            ended=ended,
            ended_label=ended_label,
            headline=headline,
        )
    cents = float(commercial["cents_per_kwh"])
    percent = rate_change.percent_change(cents, prior) if prior is not None else None
    exact = _trim(cents)
    prior_text = _trim(prior) if prior is not None else ""
    movement = _movement(percent)
    spoken = f"{cents:.2f}"
    headline = _headline(
        ended, ended_label, code or _utility_name(utility), spoken,
        movement, supplier, prior_text,
    )
    effective = commercial.get("effective_start") or ""
    delta = _delta(zone, cents, prior, percent)
    return _pack(
        sourced=True,
        utility=commercial.get("utility") or utility,
        code=code,
        cents=cents,
        exact=exact,
        text=f"{exact}¢",
        effective=effective,
        effective_label=_month_label(effective, with_day=True),
        source=commercial.get("source") or "",
        source_url=commercial.get("source_url") or "",
        schedule=commercial.get("schedule") or "",
        prior=prior,
        prior_text=prior_text,
        supplier=supplier,
        percent=percent,
        movement=movement,
        ended=ended,
        ended_label=ended_label,
        headline=headline,
        tag="default",
        rate_delta=delta,
    )


def apply(zones: list) -> list:
    """Attach the display price and use it for Δ%, voice, and the card headline.

    Call this after research, voice, and the stored-rate percent are attached.
    """
    for zone in zones:
        info = display_for(zone)
        zone["businessDefault"] = info
        card = zone.get("card")
        if isinstance(card, dict):
            card["businessDefault"] = info
        if not info["applies"]:
            continue
        delta = info["rateDelta"]
        zone["rateDelta"] = delta
        zone["displayRateChange"] = None if delta is None else delta["percent"]
        if isinstance(card, dict):
            card["rateDelta"] = delta
        _rewrite_copy(zone, card if isinstance(card, dict) else None, info)
    return zones


def affected_rows(zones: list) -> list[dict]:
    """Ended and no-aggregation zones this rule reprices, for review."""
    rows = []
    for zone in zones:
        info = zone.get("businessDefault") or display_for(zone)
        if not info.get("applies"):
            continue
        rows.append({
            "name": zone.get("name") or "",
            "sourceFile": zone.get("_source_file") or "",
            "code": info.get("code") or "",
            "utility": info.get("utility") or "",
            "cents": info.get("cents"),
            "priorCents": info.get("priorCents"),
            "percent": info.get("percent"),
            "percentText": info.get("percentText") or "—",
            "headline": info.get("headline") or "",
        })
    rows.sort(key=lambda row: (row["percent"] is None, -(row["percent"] or 0), row["name"]))
    return rows


def _applies(zone: dict) -> bool:
    if (zone.get("commodity") or "electric") == "gas":
        return False
    aggregation = zone.get("aggregationStatus") or ""
    if aggregation in {"municipal_utility", "electric_cooperative"}:
        return False
    research = zone.get("research") or {}
    if research.get("notEligible"):
        return False
    status = research.get("status") or {}
    program = (status.get("program") or "").lower()
    if program.startswith("not_eligible") or program.startswith("active"):
        return False
    life = ((research.get("lifecycle") or {}).get("status") or "").lower()
    if life == "active":
        return False
    term = (status.get("term") or "").lower()
    current = research.get("current") or {}
    ended = life == "ended" or program.startswith("ended") or term.startswith("ended") or term == "expired"
    no_program = "no_program" in program or life in {"no_program", "none"}
    ptc_as_current = (
        zone_intel.basis_family(current.get("basis")) == "ptc" and bool(current.get("sourced"))
    )
    return ended or no_program or ptc_as_current


def _ended(zone: dict) -> tuple[bool, str]:
    research = zone.get("research") or {}
    life = research.get("lifecycle") or {}
    status = research.get("status") or {}
    program = (status.get("program") or "").lower()
    term = (status.get("term") or "").lower()
    life_status = (life.get("status") or "").lower()
    ended = life_status == "ended" or program.startswith("ended") or term.startswith("ended") or term == "expired"
    label = _month_label(life.get("endedDate") or "")
    return ended, label


def _last_aggregation(zone: dict, residential) -> tuple[float | None, str]:
    """Last sourced aggregation rate, or a stored previous rate that is not a PTC."""
    research = zone.get("research") or {}
    supplier = _clean_supplier(research.get("supplier") or zone.get("supplier") or "")

    def usable(period: dict) -> float | None:
        if not period.get("sourced"):
            return None
        if zone_intel.basis_family(period.get("basis")) != "aggregation":
            return None
        rate = period.get("rate")
        if rate is None:
            rate = rate_change.as_float(period.get("rate_raw"))
        if rate is None:
            return None
        if residential is not None and abs(float(rate) - float(residential)) <= 0.0001:
            return None
        return float(rate)

    current = usable(research.get("current") or {})
    if current is not None:
        return current, supplier
    prior = usable(research.get("prior") or {})
    if prior is not None:
        return prior, supplier
    # A stored previousRate with no sourced aggregation row is not used.
    # Westlake's 8.38 is the sourced prior, so the comparison still runs.
    return None, supplier


def _delta(zone: dict, cents: float, prior, percent) -> dict:
    stored = rate_change.as_float(zone.get("rateChange"))
    if percent is None:
        text, direction, gap = "—", None, None
    else:
        gap = round(cents - float(prior), 3)
        if percent > 0:
            direction, text = "up", f"+{percent:.1f}%"
        elif percent < 0:
            direction, text = "down", f"{percent:.1f}%"
        else:
            direction, text = "flat", f"{percent:.1f}%"
    disagreement = None
    if percent is not None and stored is not None:
        disagreement = round(abs(percent - stored), 1)
    return {
        "percent": percent,
        "text": text,
        "direction": direction,
        "source": "commercial_default",
        "computed": percent,
        "stored": stored,
        "cents": gap,
        "disagreement": disagreement,
        "previousRateNeedsCheck": False,
        "baseline": "last aggregation",
    }


def _rewrite_copy(zone: dict, card: dict | None, info: dict) -> None:
    headline = info.get("headline") or ""
    voice = zone.get("voice")
    if not isinstance(voice, dict):
        voice = {}
        zone["voice"] = voice
    if info["sourced"]:
        voice["currentText"] = info["text"]
        voice["currentPending"] = False
    else:
        voice["currentText"] = "—"
        voice["currentPending"] = True
    voice["currentCaption"] = info["caption"]
    if headline:
        voice["hook"] = headline
        voice["takeaway"] = headline
    if info.get("priorText") and voice.get("priorText") in (None, "", "—"):
        voice["priorText"] = f"{info['priorText']}¢"
        voice["priorNote"] = "Last aggregation"
    if card is None:
        return
    card["voice"] = voice
    if headline:
        # Generated card copy. The research row and the region file stay as stored.
        card["hook"] = headline
        card["hookAllowed"] = True
        card["takeaway"] = headline
    talk = card.get("talkingPoints")
    if isinstance(talk, dict) and headline:
        talk["intro"] = headline
        talk["lead"] = True


def _headline(ended, ended_label, code, spoken, movement, supplier, prior_text) -> str:
    who = code or "the utility"
    if ended:
        when = f" {ended_label}" if ended_label else ""
        sentence = f"Program ended{when}, businesses now on {who} default {spoken}¢"
    else:
        sentence = f"No aggregation program, businesses are on the {who} default {spoken}¢"
    if movement and prior_text:
        whose = supplier or "the last aggregation"
        sentence += f", {movement} from {whose} {prior_text}¢"
    return sentence


def _missing_headline(ended, ended_label, utility) -> str:
    who = _utility_name(utility)
    if ended:
        when = f" {ended_label}" if ended_label else ""
        return f"Program ended{when}. No sourced commercial default is on file for {who}."
    return f"No aggregation program. No sourced commercial default is on file for {who}."


def _movement(percent) -> str:
    if percent is None:
        return ""
    if percent > 0:
        return f"up {percent:.1f}%"
    if percent < 0:
        return f"down {abs(percent):.1f}%"
    return "flat"


def _pack(
    *,
    sourced,
    utility="",
    code="",
    cents=None,
    exact="",
    text="",
    effective="",
    effective_label="",
    source="",
    source_url="",
    schedule="",
    prior=None,
    prior_text="",
    supplier="",
    percent=None,
    movement="",
    ended=False,
    ended_label="",
    headline="",
    tag="",
    rate_delta=None,
) -> dict:
    if percent is None:
        percent_text = ""
    elif percent > 0:
        percent_text = f"+{percent:.1f}%"
    else:
        percent_text = f"{percent:.1f}%"
    return {
        "applies": True,
        "sourced": sourced,
        "cents": cents,
        "exact": exact,
        "text": text,
        "caption": _CAPTION,
        "detail": "Generation only",
        "effective": effective,
        "effectiveLabel": effective_label,
        "source": source,
        "sourceUrl": source_url,
        "code": code,
        "utility": utility,
        "schedule": schedule,
        "priorCents": prior,
        "priorText": prior_text,
        "supplier": supplier,
        "percent": percent,
        "percentText": percent_text,
        "movement": movement,
        "ended": ended,
        "endedLabel": ended_label,
        "headline": headline,
        "tag": tag,
        "rateDelta": rate_delta,
    }


def _empty() -> dict:
    return {
        "applies": False,
        "sourced": False,
        "cents": None,
        "exact": "",
        "text": "",
        "caption": "",
        "detail": "",
        "effective": "",
        "effectiveLabel": "",
        "source": "",
        "sourceUrl": "",
        "code": "",
        "utility": "",
        "schedule": "",
        "priorCents": None,
        "priorText": "",
        "supplier": "",
        "percent": None,
        "percentText": "",
        "movement": "",
        "ended": False,
        "endedLabel": "",
        "headline": "",
        "tag": "",
        "rateDelta": None,
    }


def _clean_supplier(text: str) -> str:
    raw = re.sub(r"\s*\([^)]*\)", "", text or "").strip(" -")
    low = raw.lower()
    if not raw or low.startswith("none") or "not named" in low or "utility default" in low:
        return ""
    return raw


def _utility_name(utility: str) -> str:
    text = (utility or "").strip()
    if not text or "address" in text.lower():
        return "this utility"
    return text


def _month_label(value, with_day: bool = False) -> str:
    match = _DATE.search(str(value or ""))
    if not match:
        return ""
    year, month = int(match.group(1)), int(match.group(2))
    if not 1 <= month <= 12:
        return ""
    name = _MONTHS[month]
    day = int(match.group(3) or 0)
    if with_day and day:
        return f"{name} {day}, {year}"
    return f"{name} {year}"


def _trim(value) -> str:
    return f"{float(value):.4f}".rstrip("0").rstrip(".")
