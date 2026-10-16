"""User-facing copy for battlecards, hotspots, and the map.

This module only formats text that templates and page scripts display.
It does not change verification, sourced-rate rules, or stored research.
"""

from __future__ import annotations

import re

DASH = "—"

# Phrases that belong in a research log, not on a card a buyer will see.
_REPLACEMENTS = (
    (re.compile(r"this (?:record|row) is not marked inactive\.?", re.I), ""),
    (re.compile(r"these rows are not marked inactive\.?", re.I), ""),
    (re.compile(r"not marked inactive\.?", re.I), ""),
    (re.compile(r"verify before using\.?", re.I), ""),
    (re.compile(r"do not pitch from the old forge hook\.?", re.I), ""),
    (re.compile(r"needs a call", re.I), ""),
    (re.compile(r"needs call", re.I), ""),
    (re.compile(r"escalate-call", re.I), ""),
    (re.compile(r"phone number not in sources(?:\s*\([^)]*\))?", re.I), "phone pending"),
    (re.compile(r"number not in sources(?:\s*\([^)]*\))?", re.I), "pending"),
    (re.compile(r"single-source\s*[—–-]\s*not confirmed\.?", re.I), ""),
    (re.compile(r"not confirmed\.?", re.I), ""),
    (re.compile(r"\bno confirmed\b", re.I), ""),
    (re.compile(r"\bunconfirmed\b", re.I), ""),
    (re.compile(r"single-source", re.I), ""),
    (re.compile(r"forge[-\s]?recorded(?:\s*\([^)]*\))?", re.I), ""),
    (re.compile(r"\b(?:unresolved|open)\s+question\.?", re.I), ""),
    (re.compile(r"\bunresolved\b", re.I), ""),
    (re.compile(r"not used for a change figure\.?", re.I), ""),
    (re.compile(r"municipal blacklist flag is\.?", re.I), ""),
    (re.compile(r"not a battlecard rate\.?", re.I), ""),
    (re.compile(r"not battlecard rates\.?", re.I), ""),
    (re.compile(r"\bunsourced\b", re.I), ""),
    (re.compile(r"only one source found", re.I), ""),
    (re.compile(r"unresolved question\.?", re.I), ""),
    (re.compile(r"re-researched\s*\d{4}-\d{2}-\d{2}\.?", re.I), ""),
    (re.compile(r"other claims kept:.*", re.I), ""),
    (re.compile(r"misinfo:.*", re.I), ""),
)

_URL = re.compile(r"https?://\S+")
_PHONE = re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b")
_RECORDED = re.compile(r"\bis recorded as\b.+\bwith (.+) at ([\d.]+)¢/kWh", re.I)
_HOLLOW = re.compile(
    r"^(?:this record is(?: and is)?|question|and is|not used for a change figure)\.?$",
    re.I,
)
_LOG_LINE = re.compile(r"^(?:rate|term_end|misinfo|question)\b", re.I)

_LIFE_LOCK = {
    "ended": "Ended",
    "rate_pending": "Rate pending",
    "seeking_supplier": "Seeking supplier",
    "certified_not_launched": "Certified",
    "certified": "Certified",
}


def polish(text) -> str:
    """Return sales copy with research-log phrasing removed."""
    raw = (text or "").strip()
    if not raw:
        return ""
    chunks = re.split(r"(?<=[.!?])\s+|\s+\|\s+", raw)
    kept = []
    for chunk in chunks:
        cleaned = _polish_chunk(chunk)
        if cleaned and cleaned not in kept:
            kept.append(cleaned)
    return " ".join(kept)


def _polish_chunk(chunk: str) -> str:
    cleaned, _urls = _without_urls(chunk)
    for pattern, repl in _REPLACEMENTS:
        cleaned = pattern.sub(repl, cleaned)
    cleaned = re.sub(r"\s*\((?:likely|confirmed|conflict)\)", "", cleaned, flags=re.I)
    match = _RECORDED.search(cleaned)
    if match:
        cleaned = f"{match.group(1).strip(' .')} at {match.group(2)}¢/kWh."
    cleaned = _tidy(cleaned)
    if re.search(r"phone pending", cleaned, re.I):
        return "Phone pending."
    if not _keep(cleaned):
        return ""
    if cleaned[-1] not in ".!?" and len(cleaned) > 48:
        cleaned += "."
    return cleaned


def _keep(text: str) -> bool:
    text = text.strip(" .")
    if not text or _HOLLOW.match(text) or _LOG_LINE.match(text):
        return False
    if re.search(r"this record is", text, re.I):
        return False
    if re.search(r"\d", text) or _PHONE.search(text):
        return True
    if re.fullmatch(r"[A-Z][a-z]{5,}", text):
        return True
    words = re.findall(r"[A-Za-z]{2,}", text)
    if len(words) >= 2:
        return True
    return len(words) == 1 and len(words[0]) >= 4


def confidence_mark(verification=None, confidence=None) -> dict:
    """Solid dot, hollow dot, or a muted Pending mark.

    A research verification wins over the original zone confidence so a
    conflict is never drawn as confirmed.
    """
    ver = (verification or "").strip().lower()
    conf = (confidence or "").strip().lower()
    if ver == "confirmed":
        kind, label = "solid", "Confirmed"
    elif ver == "likely":
        kind, label = "hollow", "Likely"
    elif ver:
        kind, label = "pending", "Pending"
    elif conf in {"high", "confirmed"} or conf.startswith("confirmed"):
        kind, label = "solid", "Confirmed"
    elif conf in {"medium", "likely"} or conf.startswith("likely"):
        kind, label = "hollow", "Likely"
    else:
        kind, label = "pending", "Pending"
    return {"kind": kind, "label": label, "tip": label}


def sales_status(card: dict | None, zone: dict | None = None) -> tuple[str, str]:
    """Return (label, optional date) using the sales status vocabulary."""
    card = card or {}
    life = card.get("lifecycle") or {}
    life_status = (life.get("status") or "").strip().lower()
    term = (card.get("termStatus") or "").strip().lower()
    program = (card.get("program") or "").strip().lower()
    if life_status in _LIFE_LOCK:
        label = _LIFE_LOCK[life_status]
    elif term == "expiring_within_6_months":
        label = "Ending soon"
    elif term == "future_term_announced_current_unknown":
        label = "Rate pending"
    elif term == "expired":
        label = "Ended"
    elif life_status == "active" or term == "current" or program.startswith("active"):
        label = "Active"
    elif zone and (zone.get("aggregationStatus") or "") in {"municipal_utility", "electric_cooperative"}:
        label = ""
    else:
        label = ""
    date = ""
    if label == "Ended":
        date = (life.get("endedDate") or "").strip()
    return label, date


def lifecycle_label(text) -> str:
    low = (text or "").strip().lower()
    if not low:
        return DASH
    if low.startswith("ended") or "program ended" in low:
        return "Ended"
    if "seeking" in low:
        return "Seeking supplier"
    if "rate pending" in low or low.startswith("rate_pending"):
        return "Rate pending"
    if "certified" in low:
        return "Certified"
    if "ending" in low or "expir" in low:
        return "Ending soon"
    if low.startswith("active"):
        return "Active"
    polished = polish(text)
    return polished or DASH


def program_label(program) -> str:
    text = (program or "").strip().lower().replace("_", " ")
    if not text:
        return DASH
    if text.startswith("active"):
        return "Active"
    if text.startswith("not eligible") or "municipal" in text or "coop" in text:
        return "Not eligible"
    if "ended" in text or "paused" in text:
        return "Ended"
    if "rate pending" in text:
        return "Rate pending"
    if "seeking" in text:
        return "Seeking supplier"
    if "certified" in text:
        return "Certified"
    return polish(text) or DASH


def term_label(term) -> str:
    text = (term or "").strip().lower()
    if text in {"", "unknown"}:
        return DASH
    if text == "current":
        return "Active"
    if text == "expired" or text.startswith("ended"):
        return "Ended"
    if text == "expiring_within_6_months":
        return "Ending soon"
    if text == "future_term_announced_current_unknown":
        return "Rate pending"
    if text == "variable_rate":
        return "Active"
    polished = polish(term.replace("_", " ") if term else "")
    return polished or DASH


def _rate_text(label, sourced) -> str:
    if sourced and (label or "").strip():
        return f"{str(label).strip()}¢"
    return DASH


def voice_for_card(zone: dict) -> dict:
    card = zone.get("card") or {}
    research = zone.get("research") or {}
    status, status_date = sales_status(card, zone)
    mark = confidence_mark(
        card.get("verification"),
        zone.get("confidence"),
    )
    takeaway = _headline(card, status)
    hook = card.get("hook") if card.get("hookAllowed") and card.get("hook") else ""
    return {
        "status": status,
        "statusDate": status_date,
        "confidence": mark,
        "takeaway": takeaway,
        "hook": hook or "",
        "currentText": _rate_text(card.get("currentLabel"), card.get("currentSourced")),
        "currentPending": not bool(card.get("currentSourced")),
        "currentCaption": card.get("currentCaption") or "Current",
        "priorText": _rate_text(card.get("priorLabel"), card.get("priorSourced")),
        "historicalText": _rate_text(card.get("historicalLabel"), card.get("historicalSourced")),
        "futureText": _rate_text(card.get("futureLabel"), card.get("futureSourced")),
        "evidence": _evidence(zone, card, research),
        "notEligible": bool(card.get("notEligible")),
    }


def voice_for_zone(zone: dict) -> dict:
    if zone.get("card"):
        return voice_for_card(zone)
    mark = confidence_mark(None, zone.get("confidence"))
    return {
        "status": "",
        "statusDate": "",
        "confidence": mark,
        "takeaway": polish(zone.get("takeaway") or ""),
        "hook": polish(zone.get("hook") or ""),
        "currentText": DASH,
        "currentPending": True,
        "currentCaption": "Current",
        "priorText": DASH,
        "historicalText": DASH,
        "futureText": DASH,
        "evidence": [line for line in [polish(zone.get("notes") or "")] if line],
        "notEligible": (zone.get("aggregationStatus") or "") in {
            "municipal_utility",
            "electric_cooperative",
        },
    }


def attach(zones: list) -> list:
    """Add a voice dict for templates. Does not rewrite research fields."""
    for zone in zones:
        spoken = voice_for_zone(zone)
        zone["voice"] = spoken
        card = zone.get("card")
        if card is not None:
            card["voice"] = spoken
    return zones


def _headline(card: dict, status: str) -> str:
    life = card.get("lifecycle") or {}
    if status == "Ended":
        reason = polish(life.get("reason") or "")
        if reason:
            return reason[:1].upper() + reason[1:]
    if status == "Rate pending":
        detail = polish(life.get("detail") or "")
        if detail:
            return detail[:1].upper() + detail[1:]
        return "Aggregation rate is not on file."
    if status == "Seeking supplier":
        return "The community is seeking a supplier."
    if status == "Certified":
        return "Certificate on file."
    text = polish(card.get("takeaway") or "")
    if text.lower().startswith("ended "):
        # The date is already on the status pill.
        parts = text.split(".", 1)
        text = polish(parts[1] if len(parts) > 1 else "")
    if text:
        return text
    if card.get("currentSourced") and card.get("supplier") and card.get("currentLabel"):
        return f"{card['supplier']} at {card['currentLabel']}¢/kWh."
    return ""


def _evidence(zone: dict, card: dict, research: dict) -> list[str]:
    lines: list[str] = []

    def add(text, *, raw=False):
        cleaned = (text or "").strip() if raw else polish(text)
        if cleaned and cleaned not in lines:
            lines.append(cleaned)

    for phone in phones_in(card.get("openQuestions"), zone.get("notes"), card.get("takeaway")):
        add(f"Phone {phone}", raw=True)
    add(card.get("openQuestions"))
    add(card.get("futureNote"))
    life = card.get("lifecycle") or {}
    detail = polish(life.get("detail") or "")
    if detail and detail not in lines:
        add(detail, raw=True)
    if card.get("noGasAggregation"):
        add("No gas aggregation.", raw=True)
    renewal = card.get("rejectedRenewal") or None
    if renewal:
        add(f"Rejected renewal {renewal.get('rate')}¢/kWh. {renewal.get('note') or ''}")
    for note in card.get("removalNotes") or []:
        add(
            " | ".join([
                note.get("zone") or "",
                note.get("field") or "",
                note.get("note") or "",
                note.get("date") or "",
                note.get("reason") or "",
            ]),
            raw=True,
        )
    if card.get("commercialApplicability"):
        add(card.get("commercialApplicability"))
    if card.get("supersededUtility"):
        add(f"Earlier utility {card.get('supersededUtility')} superseded {card.get('supersededAt') or ''}.")
    for correction in research.get("corrections") or []:
        if not correction:
            continue
        bits = [correction.get("type") or "", correction.get("date") or ""]
        if correction.get("reason"):
            bits.append(correction["reason"])
        add(" · ".join(bit for bit in bits if bit))
    return lines


def source_links(card: dict) -> list[dict]:
    links = []
    if card.get("currentSourced") and card.get("currentSource"):
        links.append({"label": "Current", "url": card["currentSource"]})
    if card.get("priorSourced") and card.get("priorSource"):
        links.append({"label": "Prior", "url": card["priorSource"]})
    if card.get("historicalSourced"):
        links.append({"label": "Historical", "url": card.get("historicalSource") or ""})
    if card.get("futureSourced") and card.get("futureSource"):
        links.append({"label": "Future", "url": card["futureSource"]})
    ptc = card.get("ptc") or {}
    if ptc.get("applicable") and ptc.get("source_url"):
        links.append({"label": "Residential Price to Compare", "url": ptc["source_url"]})
    life = card.get("lifecycle") or {}
    for url in _URL.findall(life.get("sources") or ""):
        links.append({"label": "Program", "url": url.rstrip(".,;")})
    seen = set()
    unique = []
    for item in links:
        key = (item["label"], item["url"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def phones_in(*parts) -> list[str]:
    found = []
    for part in parts:
        for match in _PHONE.findall(part or ""):
            if match not in found:
                found.append(match)
    return found


def _without_urls(text: str) -> tuple[str, list[str]]:
    urls = [url.rstrip(".,;") for url in _URL.findall(text)]
    return _URL.sub("", text), urls


def _tidy(text: str) -> str:
    text = text.replace(" — ", ". ").replace(" – ", ". ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\(\s*\)", "", text)
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    text = re.sub(r"([,.;:])\s*([,.;:])", r"\1", text)
    text = re.sub(r"(?:^|\s)(?:with|and|or)\s*(?=[,.;:]|$)", " ", text, flags=re.I)
    text = re.sub(r"\s{2,}", " ", text).strip(" \t-–—;:,")
    text = re.sub(r"\s+\.", ".", text)
    return text.strip()
