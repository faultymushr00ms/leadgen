"""Percent change between a zone's current and previous rates.

The sales Δ% is computed from currentRate and previousRate whenever both
are present, rounded to one decimal. A stored rateChange is used only when
one of those rates is missing. Zones with no percent sort after every real
value. A stored figure that disagrees with the computed percent by more
than half a point is reported, not shown in the UI.

previousRateNeedsCheck marks round priors that look like placeholders:
exactly 7.0 on a NOPEC-area zone, and exactly 7.9 on a Mahoning township.
Those rates stay stored. The flag only tells the battlecard to label the
percent as an unverified prior.
"""

from __future__ import annotations

import re

DISAGREEMENT_POINTS = 0.5
NOPEC_PLACEHOLDER_PRIOR = 7.0
MAHONING_TOWNSHIP_PLACEHOLDER_PRIOR = 7.9

_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")


def as_float(value):
    """A rate or percent, or None when the cell is empty."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        if number != number:
            return None
        return number
    text = str(value).strip().replace(",", "")
    if not text or text.lower() in {"none", "null", "nan", "—", "-"}:
        return None
    match = _NUMBER.search(text)
    if not match:
        return None
    return float(match.group(0))


def percent_change(current, previous):
    """(current - previous) / previous * 100, rounded to 1 decimal.

    None when either rate is missing or the previous rate is zero.
    """
    current_n = as_float(current)
    previous_n = as_float(previous)
    if current_n is None or previous_n is None or previous_n == 0:
        return None
    return round((current_n - previous_n) / previous_n * 100.0, 1)


def prior_check_reason(zone: dict) -> str | None:
    """Why a stored previousRate should be treated as unverified, if it should."""
    previous = as_float(zone.get("previousRate"))
    if previous is None:
        return None
    rounded = round(previous, 3)
    if rounded == NOPEC_PLACEHOLDER_PRIOR and _nopec_area(zone):
        return "nopec_prior_7.0"
    if rounded == MAHONING_TOWNSHIP_PLACEHOLDER_PRIOR and _mahoning_township(zone):
        return "mahoning_township_prior_7.9"
    return None


def previous_rate_needs_check(zone: dict) -> bool:
    return prior_check_reason(zone) is not None


def describe(zone: dict) -> dict:
    """Display percent for one zone. Does not rewrite stored fields."""
    current = as_float(zone.get("currentRate"))
    previous = as_float(zone.get("previousRate"))
    stored = as_float(zone.get("rateChange"))
    computed = percent_change(current, previous)
    rate_missing = current is None or previous is None
    if computed is not None:
        percent = computed
        source = "computed"
        cents = round(current - previous, 3)
    elif stored is not None and rate_missing:
        percent = round(stored, 1)
        source = "stored"
        cents = None
    else:
        percent = None
        source = None
        cents = None
    disagreement = None
    if computed is not None and stored is not None:
        disagreement = round(abs(computed - stored), 1)
    if percent is None:
        direction = None
        text = "—"
    elif percent > 0:
        direction = "up"
        text = f"+{percent:.1f}%"
    elif percent < 0:
        direction = "down"
        text = f"{percent:.1f}%"
    else:
        direction = "flat"
        text = f"{percent:.1f}%"
    return {
        "percent": percent,
        "text": text,
        "direction": direction,
        "source": source,
        "computed": computed,
        "stored": stored,
        "cents": cents,
        "disagreement": disagreement,
        "previousRateNeedsCheck": previous_rate_needs_check(zone),
    }


def matching_percent_clause(zone: dict, prior_rate, current_rate) -> str:
    """A percent phrase when the cited rates are the ones the percent used.

    Empty when the percent is a stored fallback, or when the cited prior or
    current is a different number than the zone rates.
    """
    info = describe(zone)
    if info["source"] != "computed" or info["percent"] is None:
        return ""
    if not _close(zone.get("previousRate"), prior_rate):
        return ""
    if not _close(zone.get("currentRate"), current_rate):
        return ""
    return f", {info['text']} versus the current rate"


def annotate(zone: dict) -> dict:
    """Attach the display percent. Stored rateChange is left as entered."""
    info = describe(zone)
    zone["displayRateChange"] = info["percent"]
    zone["previousRateNeedsCheck"] = info["previousRateNeedsCheck"]
    zone["rateDelta"] = info
    card = zone.get("card")
    if isinstance(card, dict):
        card["rateDelta"] = info
        card["previousRateNeedsCheck"] = info["previousRateNeedsCheck"]
    return info


def annotate_zones(zones: list) -> list:
    for zone in zones:
        annotate(zone)
    return zones


def percent_sort_key(zone: dict) -> tuple:
    """Higher percents first. Missing percents sort after every real value."""
    percent = zone.get("displayRateChange")
    if percent is None:
        return (1, 0.0)
    return (0, -float(percent))


def sort_key(zone: dict, status_order: dict) -> tuple:
    status = zone.get("status") or "verify"
    band, magnitude = percent_sort_key(zone)
    return (status_order.get(status, 9), band, magnitude, zone.get("name") or "")


def disagreement_rows(zones: list) -> list[dict]:
    """Stored rateChange more than 0.5 points from the computed percent."""
    rows = []
    for zone in zones:
        info = describe(zone)
        gap = info["disagreement"]
        if gap is None or gap <= DISAGREEMENT_POINTS:
            continue
        rows.append({
            "name": zone.get("name") or "",
            "sourceFile": zone.get("_source_file") or "",
            "currentRate": zone.get("currentRate"),
            "previousRate": zone.get("previousRate"),
            "stored": info["stored"],
            "computed": info["computed"],
            "disagreement": gap,
        })
    rows.sort(key=lambda row: (-row["disagreement"], row["name"]))
    return rows


def flagged_prior_rows(zones: list) -> list[dict]:
    rows = []
    for zone in zones:
        reason = prior_check_reason(zone)
        if not reason:
            continue
        info = describe(zone)
        rows.append({
            "name": zone.get("name") or "",
            "sourceFile": zone.get("_source_file") or "",
            "region": zone.get("region") or "",
            "currentRate": zone.get("currentRate"),
            "previousRate": zone.get("previousRate"),
            "percentText": info["text"],
            "reason": reason,
        })
    rows.sort(key=lambda row: (row["reason"], row["name"]))
    return rows


def disagreement_report(zones: list) -> str:
    """Text report. Disagreements are not rendered in the product UI."""
    gaps = disagreement_rows(zones)
    flagged = flagged_prior_rows(zones)
    lines = [
        "Rate change check",
        "",
        "Displayed Δ% is computed from currentRate and previousRate (1 decimal)",
        "when both exist. Stored rateChange is used only when a rate is missing.",
        "A gap is listed when both rates exist and |stored - computed| > 0.5 points.",
        "",
        "Disagreements",
    ]
    if not gaps:
        lines.append("None.")
    else:
        for row in gaps:
            lines.append(
                f"- {row['name']} ({row['sourceFile']}): "
                f"current {row['currentRate']}, previous {row['previousRate']}, "
                f"stored {row['stored']}, computed {row['computed']}, "
                f"gap {row['disagreement']}"
            )
    lines.extend([
        "",
        "previousRateNeedsCheck",
        "Round priors left in place: previousRate 7.0 on a NOPEC-area zone,",
        "and previousRate 7.9 on a Mahoning township. No replacement rate was",
        "written. The June 2026 NOPEC standard-program step cited elsewhere",
        "(8.999¢ to 9.999¢) is a different pair than these stored currents.",
        "",
    ])
    if not flagged:
        lines.append("None.")
    else:
        for row in flagged:
            lines.append(
                f"- {row['name']} | {row['sourceFile']} | {row['region']} | "
                f"previous {row['previousRate']} | current {row['currentRate']} | "
                f"{row['percentText']} | {row['reason']}"
            )
    return "\n".join(lines) + "\n"


def _close(left, right) -> bool:
    a = as_float(left)
    b = as_float(right)
    if a is None or b is None:
        return False
    return abs(a - b) <= 0.0001


def _blob(*parts) -> str:
    return " ".join(str(part or "") for part in parts).lower()


def _nopec_area(zone: dict) -> bool:
    return "nopec" in _blob(
        zone.get("supplier"),
        zone.get("region"),
        zone.get("notes"),
        zone.get("_source_file"),
    )


def _mahoning_township(zone: dict) -> bool:
    name = (zone.get("name") or "").lower()
    if "township" not in name and "twp" not in name:
        return False
    return "mahoning" in _blob(
        zone.get("name"),
        zone.get("notes"),
        zone.get("takeaway"),
        zone.get("region"),
    )
