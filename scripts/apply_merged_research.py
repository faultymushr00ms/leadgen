"""Build the merged-research overlay and apply confirmed/likely zone edits.

Reads data/research/merged_changes.csv and merged_summary.md. Writes:
- data/research/merged_overlay.json
- data/research/unverified_leads.csv
- data/regions/merged_confirmed.json
and updates existing region records only where a confirmed or likely
update (or a named keep that the live file still contradicts) applies.

Single-source adds are not written as zones.
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

CHANGES_PATH = os.path.join(ROOT, "data", "research", "merged_changes.csv")
SUMMARY_PATH = os.path.join(ROOT, "data", "research", "merged_summary.md")
DATASET_PATH = os.path.join(ROOT, "data", "research", "forge_corrected_dataset.csv")
OVERLAY_PATH = os.path.join(ROOT, "data", "research", "merged_overlay.json")
UNVERIFIED_PATH = os.path.join(ROOT, "data", "research", "unverified_leads.csv")
REGIONS_DIR = os.path.join(ROOT, "data", "regions")
NEW_REGION = "merged_confirmed.json"

MONTHS = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
    "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12",
}
PHRASES = (
    "certified but not launched",
    "seeking supplier",
    "rate pending",
    "not eligible",
    "no program found",
    "no program",
    "active",
    "ended",
    "unknown",
)
MVCC_TOWNS = {
    "brookville", "centerville", "clayton", "eaton", "englewood", "fairborn",
    "germantown", "kettering", "lewisburg", "miamisburg", "monroe", "moraine",
    "new lebanon", "trotwood", "troy", "vandalia", "west carrollton", "xenia",
}
MVCC_QUESTION = (
    "Open question. Confirm the announced Dynegy 11.53¢ default "
    "(11.73¢ renewable) from December 2026 for this MVCC member. "
    "Phone: Constellation MVCC 833-866-3986; Dynegy 888-682-2170; "
    "Palmer Energy 419-491-1040."
)
SUPPLIER_NAMES = {
    "nopec/nextera": "NOPEC / NextEra Energy Services",
    "nopec / nextera": "NOPEC / NextEra Energy Services",
    "constellation": "Constellation",
    "dynegy": "Dynegy",
    "direct energy": "Direct Energy",
    "aep energy": "AEP Energy",
    "archer energy": "Archer Energy",
}


def conf_kind(value: str) -> str:
    text = (value or "").strip().lower()
    if "->" in text and "call" in text.split("->", 1)[-1]:
        return "callish"
    if text.startswith("confirmed"):
        return "confirmed"
    if text.startswith("likely"):
        return "likely"
    if text.startswith("single-source"):
        return "single"
    if text.startswith("conflict"):
        return "conflict"
    if "unverified" in text:
        return "unverified"
    return "other"


def applicable(classification: str, confidence: str) -> bool:
    return classification in {"update", "delete", "add"} and conf_kind(confidence) in {"confirmed", "likely"}


def cleanup_name(name: str) -> str:
    text = re.sub(r"\s+", " ", (name or "").strip())
    if re.search(r"township", text, re.I) and re.search(r"\s+Twp$", text, re.I):
        text = re.sub(r"\s+Twp$", "", text, flags=re.I)
    elif re.search(r"\s+Twp$", text, re.I):
        text = re.sub(r"\s+Twp$", " Township", text, flags=re.I)
    return text


def first_url(text: str) -> str:
    match = re.search(r"https?://[^\s\]\|]+", text or "")
    if not match:
        return ""
    return match.group(0).rstrip(".,)")


def urls_in(text: str) -> list[str]:
    found = []
    for match in re.finditer(r"https?://[^\s\]\|]+", text or ""):
        url = match.group(0).rstrip(".,)")
        if url not in found:
            found.append(url)
    return found


def clean_rate(value: str) -> str:
    text = (value or "").strip()
    low = text.lower()
    if not text or low.startswith("unconfirmed") or low.startswith("none") or "if enrolled" in low:
        return ""
    if ";" in text or "/" in text:
        return ""
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*¢?(?:/kwh)?", text, re.I)
    return match.group(1) if match else ""


def clean_term(value: str) -> str:
    text = (value or "").strip()
    match = re.fullmatch(r"(\d{4}-\d{2})(?:-\d{2})?", text)
    return match.group(1) if match else ""


def month_token(token: str) -> str:
    match = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})", token or "", re.I)
    if not match:
        return ""
    return f"{match.group(2)}-{MONTHS[match.group(1)[:3].lower()]}"


def parse_future(value: str) -> tuple[str, str, str, str]:
    text = (value or "").strip()
    match = re.search(r"(\d+(?:\.\d+)?)\s*\(([^)]*)\)", text)
    if not match:
        return clean_rate(text), "", "", ""
    inner = match.group(2)
    dated = [
        match.group(0)
        for match in re.finditer(
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}",
            inner,
            re.I,
        )
    ]
    start = month_token(dated[0]) if dated else ""
    end = month_token(dated[1]) if len(dated) > 1 else ""
    renewable = re.search(r"(\d+(?:\.\d+)?)\s*renewable", inner, re.I)
    note = f"{match.group(1)}¢ default"
    if renewable:
        note += f"; {renewable.group(1)}¢ renewable"
    who = text.split()[0] if text else "Supplier"
    return match.group(1), start, end, f"{who} {note}, {start or '—'}–{end or '—'}"


def clean_supplier(value: str) -> str:
    text = (value or "").strip()
    low = text.lower()
    if not text or low.startswith("none") or "unconfirmed" in low or "expired" in low or " vs " in low:
        return ""
    return SUPPLIER_NAMES.get(low, text)


def split_lifecycle(value: str) -> tuple[str | None, str]:
    text = (value or "").strip()
    low = text.lower()
    for phrase in PHRASES:
        if low == phrase or low.startswith(phrase + " (") or low.startswith(phrase + "("):
            rest = text[len(phrase):].strip()
            if rest.startswith("(") and rest.endswith(")"):
                rest = rest[1:-1].strip()
            return phrase, rest
    return None, text


def parse_lifecycle(value: str, sources: str, confidence: str) -> dict:
    phrase, detail = split_lifecycle(value)
    ended_date = ""
    reason = ""
    if phrase == "ended":
        if ";" in detail:
            ended_date, reason = [part.strip() for part in detail.split(";", 1)]
        elif re.fullmatch(r"\d{4}-\d{2}", detail):
            ended_date = detail
        else:
            reason = detail
        if not reason:
            quote = re.search(r":\s*\"([^\"]+)", sources or "")
            reason = (quote.group(1).strip() if quote else "")[:240]
    labels = {
        "active": ("active", "Active"),
        "seeking supplier": ("seeking_supplier", "Seeking supplier"),
        "rate pending": ("rate_pending", "Rate pending"),
        "ended": ("ended", "Ended"),
        "certified but not launched": ("certified_not_launched", "Certified but not launched"),
        "not eligible": ("not_eligible", "Not eligible"),
        "no program found": ("no_program", "No program"),
        "no program": ("no_program", "No program"),
        "unknown": ("unknown", "Unknown"),
    }
    if phrase in labels:
        status, label = labels[phrase]
    else:
        status, label = "other", (value or "Unknown").strip()[:80]
    kind = conf_kind(confidence)
    if kind not in {"confirmed", "likely"}:
        label = f"{label} · {kind or 'unverified'}"
    return {
        "status": status,
        "label": label,
        "detail": detail,
        "endedDate": ended_date,
        "reason": reason,
        "sources": " ".join(urls_in(sources)[:4]),
        "confidence": kind,
        "raw": value or "",
    }


def classify_utility(value: str, kind: str) -> tuple[str, str | None, str, str]:
    text = (value or "").strip()
    low = text.lower()
    if not text or text in {"?", "n/a"}:
        return "address-dependent", None, "low", ""
    hits = []
    for needle, parent, canonical in (
        ("the illuminating company", "FirstEnergy", "The Illuminating Company"),
        ("illuminating", "FirstEnergy", "The Illuminating Company"),
        ("cei", "FirstEnergy", "The Illuminating Company"),
        ("ohio edison", "FirstEnergy", "Ohio Edison"),
        ("toledo edison", "FirstEnergy", "Toledo Edison"),
        ("aep ohio", "AEP", "AEP Ohio"),
        ("ohio power", "AEP", "AEP Ohio"),
        ("aes ohio", "AES", "AES Ohio"),
        ("dayton p&l", "AES", "AES Ohio"),
        ("duke", "Duke Energy", "Duke Energy Ohio"),
    ):
        if needle == "cei":
            if re.search(r"\bcei\b", low):
                hits.append((parent, canonical))
        elif needle in low:
            hits.append((parent, canonical))
    canonicals = []
    for parent, canonical in hits:
        if canonical not in canonicals:
            canonicals.append(canonical)
    parents = {parent for parent, _canonical in hits}
    if len(canonicals) == 1 and len(parents) == 1:
        confidence = "high" if kind == "confirmed" else "medium"
        return canonicals[0], next(iter(parents)), confidence, ""
    if len(canonicals) > 1:
        return "address-dependent", None, "low", text
    return "address-dependent", None, "low", text


def blank_row(columns: list[str], name: str, county: str) -> dict:
    row = {column: "" for column in columns}
    row["source_file"] = NEW_REGION
    row["orig_name"] = name
    row["norm_jurisdiction"] = name
    row["norm_county"] = county
    row["research_sources_accessed"] = "2026-10-15"
    row["CURRENT_rate_basis"] = "aggregation program"
    return row


def program_for(lifecycle: dict | None, has_rate: bool) -> str:
    status = (lifecycle or {}).get("status") or ""
    if status == "ended":
        return "ended_or_paused"
    if status == "rate_pending":
        return "rate_pending"
    if status == "seeking_supplier":
        return "seeking_supplier"
    if status == "certified_not_launched":
        return "certified_not_launched"
    if status == "not_eligible":
        return "not_eligible"
    if status == "no_program":
        return "no_program_found_utility_default"
    if has_rate and status in {"", "active"}:
        return "active_aggregation"
    if status == "active":
        return ""
    if has_rate:
        return "active_aggregation"
    return ""


def load_zones() -> list[dict]:
    zones = []
    for fname in sorted(os.listdir(REGIONS_DIR)):
        if not fname.endswith(".json") or fname == NEW_REGION:
            continue
        with open(os.path.join(REGIONS_DIR, fname), encoding="utf-8") as handle:
            for zone in json.load(handle):
                zone["_file"] = fname
                zones.append(zone)
    return zones


def dataset_index() -> dict[tuple[str, str], dict]:
    index = {}
    with open(DATASET_PATH, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            index[(row["source_file"], row["orig_name"])] = row
    return index


def dataset_county(zone: dict, index: dict) -> str:
    row = index.get((zone["_file"], zone["name"]))
    return (row or {}).get("norm_county") or ""


def find_zone(community: str, county: str, zones: list[dict], index: dict) -> dict | None:
    cleaned = cleanup_name(community)
    hits = [
        zone for zone in zones
        if zone["name"].casefold() in {cleaned.casefold(), community.casefold()}
    ]
    if not hits:
        return None
    if len(hits) == 1:
        known = dataset_county(hits[0], index)
        if known and county and known.casefold() != county.casefold():
            return None
        return hits[0]
    for zone in hits:
        if dataset_county(zone, index).casefold() == (county or "").casefold():
            return zone
    return None


def collides(base: str, used: set[str]) -> bool:
    text = base.casefold()
    for name in used:
        if name == text:
            return True
        if name.startswith(text + " township") or text.startswith(name + " township"):
            return True
        if name.startswith(text + " (") or text.startswith(name + " ("):
            return True
    return False


def parse_phones(summary: str) -> dict[tuple[str, str], str]:
    phones = {}
    started = False
    for line in summary.splitlines():
        if line.startswith("## Call list"):
            started = True
            continue
        if started and line.startswith("## "):
            break
        if not started or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 5 or "---" in cells[0] or cells[0] == "Community":
            continue
        phones[(cells[0].casefold(), cells[1].casefold())] = cells[-1]
    return phones


def phone_for(community: str, county: str, phones: dict) -> str:
    key = (community.casefold(), county.casefold())
    if key in phones:
        return phones[key]
    cleaned = cleanup_name(community).casefold()
    for (name, phone_county), phone in phones.items():
        if phone_county == county.casefold() and cleanup_name(name).casefold() == cleaned:
            return phone
    return ""


def question_text(rows: list[dict], phone: str) -> str:
    parts = []
    for row in rows:
        note = (row.get("notes") or "").replace("\n", " ").strip()
        parts.append(f"{row['field']}: {row['new_value']}. {note[:220]}".strip())
    phone_text = (phone or "").strip()
    if not phone_text or phone_text.lower().startswith("number not in sources"):
        phone_line = "Phone number not in sources (community clerk / fiscal officer)."
    else:
        phone_line = "Phone: " + phone_text
    return "Unresolved question. " + " ".join(parts) + " " + phone_line


def best_row(rows: list[dict], field: str) -> dict | None:
    ranked = {"confirmed": 3, "likely": 2, "unverified": 1, "single": 0, "conflict": 0, "callish": 0, "other": 0}
    chosen = None
    score = -1
    for row in rows:
        if row["field"] != field:
            continue
        kind = conf_kind(row["confidence"])
        if kind > score if False else ranked.get(kind, 0) > score:
            chosen = row
            score = ranked.get(kind, 0)
    return chosen


def group_rows(rows: list[dict]) -> dict[tuple[str, str], list[dict]]:
    grouped: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        if " vs " in (row["community"] or ""):
            continue
        grouped.setdefault((row["community"], row["county"]), []).append(row)
    return grouped


def lifecycle_from(rows: list[dict], allow_weak: bool) -> dict | None:
    chosen = None
    score = -1
    ranked = {"confirmed": 4, "likely": 3, "unverified": 2, "single": 1}
    for row in rows:
        if row["field"] != "lifecycle":
            continue
        kind = conf_kind(row["confidence"])
        if not allow_weak and kind not in {"confirmed", "likely"}:
            continue
        if ranked.get(kind, 0) > score:
            chosen = row
            score = ranked.get(kind, 0)
    if not chosen:
        return None
    return parse_lifecycle(chosen["new_value"], chosen.get("sources") or "", chosen["confidence"])


def extract_from_lifecycle_detail(detail: str) -> dict:
    """Pull a rate stated inside a likely lifecycle sentence, such as Crosby."""
    found = {}
    match = re.search(
        r"\b(Dynegy|Constellation|Direct Energy|AEP Energy|Archer Energy|NOPEC)\b\s+(\d+\.\d+)",
        detail or "",
        re.I,
    )
    if match:
        found["supplier"] = clean_supplier(match.group(1))
        found["rate"] = match.group(2)
    terms = [
        match.group(0)
        for match in re.finditer(
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}",
            detail or "",
            re.I,
        )
    ]
    if len(terms) >= 2:
        found["term_start"] = month_token(terms[0])
        found["term_end"] = month_token(terms[1])
    return found


def field_bag(rows: list[dict]) -> dict[str, dict]:
    bag = {}
    for field in ("supplier", "rate", "term_end", "term_start", "utility", "future_supplier_rate", "lifecycle"):
        chosen = None
        for row in rows:
            if row["field"] != field or row["classification"] not in {"add", "update"}:
                continue
            if conf_kind(row["confidence"]) not in {"confirmed", "likely"}:
                continue
            if field.startswith("misinfo") or row["field"].startswith("misinfo"):
                continue
            chosen = row
        if chosen:
            bag[field] = chosen
    return bag


def add_is_zone(bag: dict, lifecycle: dict | None, extra: dict) -> bool:
    """A priced add, a future rate, or an explicit non-active lifecycle becomes a zone.

    A supplier name alone, including a NOPEC map listing, is not a program.
    """
    if clean_rate((bag.get("rate") or {}).get("new_value") or "") or extra.get("rate"):
        return True
    if bag.get("future_supplier_rate"):
        return True
    status = (lifecycle or {}).get("status") or ""
    return status in {"rate_pending", "seeking_supplier", "certified_not_launched", "ended", "no_program"}


def verification_for(bag: dict, lifecycle: dict | None) -> str:
    status = (lifecycle or {}).get("status") or ""
    if status in {"rate_pending", "seeking_supplier", "certified_not_launched"}:
        return "escalate-call"
    kinds = [conf_kind(row["confidence"]) for row in bag.values()]
    if "likely" in kinds:
        return "likely"
    if kinds:
        return "confirmed"
    return "likely"


def build_patch_from_bag(bag: dict, existing: dict | None, lifecycle: dict | None) -> tuple[dict, dict]:
    patch = {}
    meta = {}
    if lifecycle:
        meta["lifecycle"] = lifecycle
        program = program_for(lifecycle, bool(clean_rate((bag.get("rate") or {}).get("new_value") or "")))
        if program:
            patch["STATUS_program"] = program
    future = bag.get("future_supplier_rate")
    if future:
        rate, start, end, note = parse_future(future["new_value"])
        if rate:
            patch["FUTURE_rate"] = rate
            if start:
                patch["FUTURE_term_start"] = start
            if end:
                patch["FUTURE_term_end"] = end
            source = first_url(future.get("sources") or "")
            if source:
                patch["FUTURE_source"] = source
            meta["futureNote"] = note
    utility = bag.get("utility")
    if utility:
        canonical, _parent, _conf, detail = classify_utility(utility["new_value"], conf_kind(utility["confidence"]))
        patch["norm_utility"] = canonical
        if detail:
            meta["utilityDetail"] = detail
    supplier = bag.get("supplier")
    if supplier:
        cleaned = clean_supplier(supplier["new_value"])
        if cleaned:
            patch["norm_supplier"] = cleaned
            kind = conf_kind(supplier["confidence"])
            if kind in {"confirmed", "likely"}:
                patch["STATUS_verification"] = kind
                patch["open_questions"] = ""
            if "nopec" in cleaned.lower():
                patch["norm_program_administrator"] = "NOPEC"
            elif "sopec" in (supplier.get("sources") or "").lower() or "aep energy" in cleaned.lower():
                if "sopec" in (supplier.get("sources") or "").lower():
                    patch["norm_program_administrator"] = "SOPEC"
    rate = bag.get("rate")
    if rate:
        cleaned = clean_rate(rate["new_value"])
        if cleaned:
            if existing and (existing.get("CURRENT_rate") or "").strip() and existing.get("CURRENT_rate") != cleaned:
                if not (existing.get("HISTORICAL_rate_benchmark") or "").strip() and (existing.get("PRIOR_rate") or "").strip():
                    patch["HISTORICAL_rate_benchmark"] = existing["PRIOR_rate"]
                    patch["HISTORICAL_source"] = existing.get("PRIOR_source") or ""
                patch["PRIOR_rate"] = existing["CURRENT_rate"]
                patch["PRIOR_source"] = existing.get("CURRENT_source") or ""
                patch["PRIOR_term"] = " ".join(
                    part for part in (existing.get("CURRENT_term_start") or "", existing.get("CURRENT_term_end") or "") if part
                )
                patch["PRIOR_basis"] = existing.get("CURRENT_rate_basis") or "aggregation program"
            patch["CURRENT_rate"] = cleaned
            patch["CURRENT_rate_basis"] = "aggregation program"
            patch["CURRENT_source"] = first_url(rate.get("sources") or "") or (
                first_url((supplier or {}).get("sources") or "")
            )
    term = bag.get("term_end")
    if term and clean_term(term["new_value"]):
        patch["CURRENT_term_end"] = clean_term(term["new_value"])
    if patch.get("CURRENT_rate"):
        patch["STATUS_verification"] = verification_for(bag, lifecycle)
        if lifecycle and lifecycle["status"] == "active":
            patch["STATUS_term"] = "current"
        elif lifecycle and lifecycle["status"] == "ended":
            patch["STATUS_term"] = "expired"
    elif lifecycle and lifecycle["status"] in {"rate_pending", "seeking_supplier", "certified_not_launched"}:
        patch["STATUS_verification"] = "escalate-call"
    return patch, meta


def zone_record(name: str, county: str, bag: dict, lifecycle: dict | None, extra: dict) -> dict:
    utility_row = bag.get("utility") or {}
    canonical, parent, utility_confidence, detail = classify_utility(
        (utility_row.get("new_value") or extra.get("utility") or ""),
        conf_kind(utility_row.get("confidence") or ""),
    )
    supplier = clean_supplier((bag.get("supplier") or {}).get("new_value") or extra.get("supplier") or "")
    rate = clean_rate((bag.get("rate") or {}).get("new_value") or extra.get("rate") or "")
    term_end = clean_term((bag.get("term_end") or {}).get("new_value") or extra.get("term_end") or "")
    term_start = extra.get("term_start") or ""
    status_name = (lifecycle or {}).get("status") or ""
    if status_name in {"ended", "rate_pending", "seeking_supplier", "certified_not_launched"} or not rate:
        aggregation = "no_aggregation_verified"
        status = "verify"
    elif term_end and term_end <= "2027-04":
        aggregation = "confirmed_active_aggregation"
        status = "pain_coming"
    else:
        aggregation = "confirmed_active_aggregation"
        status = "stable"
    if canonical == "address-dependent":
        utility_confidence = "low"
        parent = None
    notes = []
    if detail:
        notes.append(f"Utility on the account: {detail}.")
    if status_name == "certified_not_launched":
        notes.append("A PUCO certificate is certification only. This program is not launched.")
    if status_name == "rate_pending":
        notes.append((lifecycle or {}).get("detail") or "Rate pending. No launched aggregation rate.")
    if name.startswith("Fulton County") and rate == "9.03":
        notes.append("Archbold is served by this county Dynegy program. This is the same contract, not a second price.")
    if "Morrow County" in name:
        notes.append("Eligible townships only: Canaan, Gilead, Perry, and Washington. Cities and villages, including the Village of Morrow in Warren County, are not in this program.")
    if not rate and supplier:
        notes.append("Supplier is confirmed or likely. No aggregation rate was in the confirmed add.")
    source = ""
    for key in ("rate", "supplier", "future_supplier_rate", "lifecycle", "utility"):
        if bag.get(key):
            source = first_url(bag[key].get("sources") or "") or source
    kind = verification_for(bag, lifecycle)
    return {
        "name": name,
        "region": f"{county} County",
        "utility": canonical,
        "utilityParent": parent,
        "utilityConfidence": utility_confidence,
        "aggregationStatus": aggregation,
        "currentRate": float(rate) if rate else None,
        "previousRate": None,
        "rateChange": None,
        "supplier": supplier or None,
        "termStart": term_start or None,
        "termEnd": term_end or None,
        "status": status,
        "confidence": "high" if kind == "confirmed" else "medium",
        "takeaway": "",
        "hook": "",
        "futureUse": "aggregation",
        "notes": " ".join(notes),
        "lastVerified": "2026-10-15",
        "sourceUrl": source or None,
        "_utility_detail": detail,
    }


def synthetic_from_zone(columns: list[str], zone: dict, county: str, bag: dict, lifecycle: dict | None, extra: dict) -> dict:
    row = blank_row(columns, zone["name"], county)
    row["norm_utility"] = zone["utility"] if zone["utility"] != "address-dependent" else "address-dependent"
    row["norm_supplier"] = zone.get("supplier") or ""
    if zone.get("currentRate") is not None and zone.get("supplier") and "NOPEC" in zone["supplier"]:
        row["norm_program_administrator"] = "NOPEC"
    elif any("sopec" in (item.get("sources") or "").lower() for item in bag.values()):
        row["norm_program_administrator"] = "SOPEC"
    if zone.get("currentRate") is not None:
        row["CURRENT_rate"] = str(zone["currentRate"])
        row["CURRENT_term_start"] = zone.get("termStart") or extra.get("term_start") or ""
        row["CURRENT_term_end"] = zone.get("termEnd") or ""
        row["CURRENT_source"] = zone.get("sourceUrl") or ""
        row["CURRENT_rate_basis"] = "aggregation program"
    future = bag.get("future_supplier_rate")
    if future:
        rate, start, end, _note = parse_future(future["new_value"])
        row["FUTURE_rate"] = rate
        row["FUTURE_term_start"] = start
        row["FUTURE_term_end"] = end
        row["FUTURE_source"] = first_url(future.get("sources") or "")
    row["STATUS_program"] = program_for(lifecycle, zone.get("currentRate") is not None)
    row["STATUS_verification"] = verification_for(bag, lifecycle)
    if lifecycle and lifecycle["status"] == "ended":
        row["STATUS_term"] = "expired"
    elif zone.get("currentRate") is not None:
        row["STATUS_term"] = "current"
    return row


def append_note(zone: dict, text: str) -> None:
    notes = zone.get("notes") or ""
    if text not in notes:
        zone["notes"] = (notes + " " + text).strip()


def set_parent(zone: dict, utility: str, confidence: str) -> None:
    canonical, parent, utility_confidence, _detail = classify_utility(utility, "confirmed" if confidence == "high" else "likely")
    zone["utility"] = canonical
    zone["utilityParent"] = parent
    zone["utilityConfidence"] = confidence or utility_confidence


def align_named_zones(zones: list[dict]) -> list[str]:
    """Bring a few live records in line with confirmed facts the file still contradicts."""
    by_name = {zone["name"]: zone for zone in zones}
    changed = []

    def mark(zone: dict) -> None:
        changed.append(zone["_file"])

    for name in ("Centerville", "Kettering", "Miamisburg", "Vandalia", "Fairborn"):
        zone = by_name.get(name)
        if not zone:
            continue
        zone["supplier"] = "Constellation"
        zone["currentRate"] = 9.049
        zone["termStart"] = "2026-01"
        zone["termEnd"] = "2026-12"
        zone["rateChange"] = None
        zone["aggregationStatus"] = "confirmed_active_aggregation"
        zone["status"] = "pain_coming"
        zone["futureUse"] = "aggregation"
        zone["hook"] = ""
        zone["lastVerified"] = "2026-10-15"
        zone["sourceUrl"] = "https://www.constellation.com/oh-mvcc"
        zone["confidence"] = "high"
        if name == "Fairborn":
            zone["utility"] = "address-dependent"
            zone["utilityParent"] = None
            zone["utilityConfidence"] = "low"
            utility_sentence = "Utility on the account: Ohio Edison / AES Ohio."
        else:
            set_parent(zone, "AES Ohio", "high")
            utility_sentence = "Utility: AES Ohio."
        zone["takeaway"] = (
            f"{name} is on Constellation at 9.049¢/kWh through December 2026. "
            "Announced/future: Dynegy 11.53¢ from December 2026 through December 2029 (11.73¢ renewable)."
        )
        zone["notes"] = (
            f"{utility_sentence} MVCC aggregation. Current Constellation term through December 2026. "
            "Announced/future: Dynegy 11.53¢ default, December 2026–December 2029, with 11.73¢ renewable."
        )
        mark(zone)

    troy = by_name.get("Troy")
    if troy:
        troy["supplier"] = "Constellation"
        troy["currentRate"] = 9.049
        troy["termStart"] = None
        troy["termEnd"] = "2026-12"
        troy["rateChange"] = None
        troy["aggregationStatus"] = "confirmed_active_aggregation"
        troy["status"] = "pain_coming"
        troy["futureUse"] = "aggregation"
        troy["hook"] = ""
        troy["confidence"] = "high"
        troy["lastVerified"] = "2026-10-15"
        troy["sourceUrl"] = "https://www.constellation.com/oh-mvcc"
        set_parent(troy, "AES Ohio", "high")
        troy["takeaway"] = (
            "Troy is on Constellation at 9.049¢/kWh through December 2026. "
            "Announced/future: Dynegy 11.53¢ from December 2026 through December 2029 (11.73¢ renewable)."
        )
        troy["notes"] = (
            "AES Ohio. Prior 6.57¢ remains the earlier recorded figure. "
            "Announced/future: Dynegy 11.53¢ default, December 2026–December 2029, with 11.73¢ renewable."
        )
        mark(troy)

    monroe = by_name.get("Monroe")
    if monroe:
        monroe["utility"] = "address-dependent"
        monroe["utilityParent"] = None
        monroe["utilityConfidence"] = "low"
        monroe["supplier"] = "Constellation"
        monroe["currentRate"] = 9.049
        monroe["termEnd"] = "2026-12"
        monroe["rateChange"] = None
        append_note(
            monroe,
            "Utility on the account: AES Ohio / Duke Energy Ohio. Announced/future: Dynegy 11.53¢ default, December 2026–December 2029, with 11.73¢ renewable.",
        )
        mark(monroe)

    loveland = by_name.get("Loveland")
    if loveland:
        if loveland.get("currentRate") not in (None, 10.36):
            loveland["previousRate"] = loveland.get("currentRate")
        loveland["supplier"] = "Direct Energy"
        loveland["currentRate"] = 10.36
        loveland["termStart"] = "2026-08"
        loveland["termEnd"] = "2027-11"
        loveland["rateChange"] = None
        loveland["aggregationStatus"] = "confirmed_active_aggregation"
        loveland["status"] = "stable"
        loveland["hook"] = ""
        loveland["confidence"] = "medium"
        loveland["lastVerified"] = "2026-10-15"
        loveland["sourceUrl"] = "https://www.lovelandoh.gov/182/Electric-Aggregation"
        loveland["takeaway"] = (
            "Loveland's Dynegy term ended with May 2026 meter reads. "
            "Direct Energy is 10.36¢/kWh from August 2026 through November 2027."
        )
        loveland["notes"] = loveland["takeaway"] + " Duke Energy Ohio."
        mark(loveland)

    worthington = by_name.get("Worthington")
    if worthington:
        earlier = worthington.get("previousRate")
        if worthington.get("currentRate") not in (None, 10.69):
            worthington["previousRate"] = worthington.get("currentRate")
        worthington["supplier"] = "Direct Energy"
        worthington["currentRate"] = 10.69
        worthington["termStart"] = "2026-06"
        worthington["termEnd"] = "2028-06"
        worthington["rateChange"] = None
        worthington["hook"] = ""
        worthington["confidence"] = "medium"
        worthington["lastVerified"] = "2026-10-15"
        worthington["sourceUrl"] = "https://www.worthington.org/882/Electric-Aggregation"
        worthington["takeaway"] = "Worthington aggregation is Direct Energy at 10.69¢/kWh, June 2026 through June 2028."
        worthington["notes"] = (
            worthington["takeaway"]
            + " AEP Ohio. Earlier recorded rate 9.756¢ remains a prior figure."
        )
        mark(worthington)

    pierce = by_name.get("Pierce Township / Amelia")
    if pierce:
        pierce["supplier"] = "Archer Energy"
        pierce["currentRate"] = 9.199
        pierce["termStart"] = None
        pierce["termEnd"] = "2028-05"
        pierce["rateChange"] = None
        pierce["hook"] = ""
        pierce["status"] = "stable"
        pierce["aggregationStatus"] = "confirmed_active_aggregation"
        pierce["confidence"] = "medium"
        pierce["lastVerified"] = "2026-10-15"
        pierce["sourceUrl"] = "https://piercetownship.org/township-news/new-energy-aggregation-agreement-with-archer-energy/"
        pierce["takeaway"] = "Pierce Township / Amelia is on Archer Energy at 9.199¢/kWh through May 2028."
        pierce["notes"] = "Duke Energy Ohio. Archer Energy at 9.199¢/kWh through May 2028. Earlier 6.99¢ remains the prior recorded figure."
        mark(pierce)

    powell = by_name.get("Powell")
    if powell:
        powell["currentRate"] = None
        powell["rateChange"] = None
        powell["termEnd"] = None
        powell["status"] = "verify"
        powell["aggregationStatus"] = "no_aggregation_verified"
        powell["hook"] = ""
        powell["confidence"] = "medium"
        powell["lastVerified"] = "2026-10-15"
        powell["takeaway"] = "Powell selected NOPEC. The plan of operation is not final, so there is no aggregation rate to quote."
        powell["notes"] = powell["takeaway"] + " AEP Ohio. Phone: NOPEC 855-667-3201. City of Powell phone number not in sources."
        mark(powell)

    delaware = by_name.get("Delaware (City)")
    if delaware:
        delaware["utility"] = "address-dependent"
        delaware["utilityParent"] = None
        delaware["utilityConfidence"] = "low"
        delaware["currentRate"] = None
        delaware["supplier"] = None
        delaware["rateChange"] = None
        delaware["termStart"] = None
        delaware["termEnd"] = None
        delaware["status"] = "verify"
        delaware["aggregationStatus"] = "no_aggregation_verified"
        delaware["hook"] = ""
        delaware["confidence"] = "medium"
        delaware["lastVerified"] = "2026-10-15"
        delaware["takeaway"] = "Delaware City's electric aggregation ended. The utility is address-dependent (Ohio Edison and AEP Ohio)."
        delaware["notes"] = delaware["takeaway"]
        mark(delaware)

    fremont = by_name.get("Fremont")
    if fremont:
        append_note(
            fremont,
            "Two Dynegy tiers: Toledo Edison accounts 9.96¢ August 2026–December 2027; AEP Ohio accounts 10.67¢ July 2026–December 2027.",
        )
        mark(fremont)

    plain = by_name.get("Plain Township")
    if plain and plain["_file"] == "ne_ohio_firstenergy.json":
        append_note(
            plain,
            "The township page lists both AEP Ohio and Ohio Edison. The AEP-area NOPEC price is unverified.",
        )
        mark(plain)

    wyoming = by_name.get("Wyoming")
    if wyoming:
        append_note(
            wyoming,
            "Electric aggregation ended July 2026. Energy Alliances: unable to secure pricing that guaranteed savings. Phone: City of Wyoming 513-821-7600; Energy Alliances 513-794-5555 / 800-735-0359.",
        )
        wyoming["hook"] = ""
        wyoming["status"] = "verify"
        mark(wyoming)

    xenia = by_name.get("Xenia")
    if xenia:
        xenia["currentRate"] = None
        xenia["rateChange"] = None
        xenia["supplier"] = None
        xenia["hook"] = ""
        xenia["status"] = "verify"
        xenia["aggregationStatus"] = "no_aggregation_verified"
        xenia["takeaway"] = (
            "Xenia is in the MVCC group. The current supplier is not confirmed. "
            "Announced/future: Dynegy 11.53¢ from December 2026 through December 2029 (11.73¢ renewable)."
        )
        xenia["notes"] = xenia["takeaway"]
        xenia["lastVerified"] = "2026-10-15"
        mark(xenia)

    return changed


def write_region(fname: str, zones: list[dict]) -> None:
    clean = []
    for zone in zones:
        item = {key: value for key, value in zone.items() if not key.startswith("_")}
        clean.append(item)
    text = json.dumps(clean, indent=2, ensure_ascii=False) + "\n"
    path = os.path.join(REGIONS_DIR, fname)
    with open(path, encoding="utf-8") as handle:
        current = handle.read()
    if current != text:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)


def main() -> None:
    with open(CHANGES_PATH, newline="", encoding="utf-8") as handle:
        changes = list(csv.DictReader(handle))
    summary = open(SUMMARY_PATH, encoding="utf-8").read() if os.path.exists(SUMMARY_PATH) else ""
    phones = parse_phones(summary)
    with open(DATASET_PATH, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = list(reader.fieldnames or [])
        dataset_rows = list(reader)
    index = {(row["source_file"], row["orig_name"]): row for row in dataset_rows}
    zones = load_zones()
    grouped = group_rows(changes)

    patches: dict[str, dict] = {}
    synthetic: dict[str, dict] = {}
    meta: dict[str, dict] = {}
    new_zones = []
    unmatched_questions = []
    partial_adds = []
    used = {zone["name"].casefold() for zone in zones}

    stats = {"updates": 0, "deletes_skipped": 0, "added": 0, "merged_into_existing": 0, "calls": 0, "unverified_rows": 0}

    for (community, county), rows in grouped.items():
        updates = [
            row for row in rows
            if row["classification"] == "update"
            and applicable("update", row["confidence"])
            and not row["field"].startswith("misinfo")
        ]
        adds = [row for row in rows if row["classification"] == "add" and applicable("add", row["confidence"])]
        deletes = [row for row in rows if row["classification"] == "delete" and applicable("delete", row["confidence"])]
        stats["deletes_skipped"] += len(deletes)
        calls = [row for row in rows if row["classification"] == "call"]
        zone = find_zone(community, county, zones, index)
        bag = field_bag(updates + adds)
        lifecycle = lifecycle_from(rows, allow_weak=zone is not None)
        if zone is None and lifecycle and lifecycle.get("confidence") not in {"confirmed", "likely"}:
            if not adds and not updates:
                lifecycle = None

        extra = {}
        if lifecycle and lifecycle["status"] == "active" and "rate" not in bag:
            extra = extract_from_lifecycle_detail(lifecycle.get("detail") or "")

        if adds and zone is None and not add_is_zone(bag, lifecycle, extra):
            for row in adds:
                partial_adds.append({
                    "community": community,
                    "county": county,
                    "field": row["field"],
                    "value": row["new_value"],
                    "confidence": conf_kind(row["confidence"]),
                    "sources": row.get("sources") or "",
                    "notes": row.get("notes") or "",
                    "flag": "likely — no aggregation rate. Not a battlecard rate.",
                })
            target_key = ""
        elif adds and zone is None:
            base = cleanup_name(community)
            name = f"{base} ({county})" if collides(base, used) else base
            if name.casefold() in used:
                name = f"{base} ({county})"
            record = zone_record(name, county, bag, lifecycle, extra)
            new_zones.append(record)
            used.add(name.casefold())
            key = f"{NEW_REGION}|{name}"
            synthetic[key] = synthetic_from_zone(columns, record, county, bag, lifecycle, extra)
            meta[key] = {}
            if lifecycle:
                meta[key]["lifecycle"] = lifecycle
            if record.get("_utility_detail"):
                meta[key]["utilityDetail"] = record["_utility_detail"]
            future = bag.get("future_supplier_rate")
            if future:
                _rate, _start, _end, note = parse_future(future["new_value"])
                meta[key]["futureNote"] = note
            stats["added"] += 1
            target_key = key
        elif zone is not None and (updates or (adds and bag)):
            existing = index.get((zone["_file"], zone["name"]))
            patch, patch_meta = build_patch_from_bag(bag, existing, lifecycle if (updates or adds) else None)
            key = f"{zone['_file']}|{zone['name']}"
            if patch:
                patches[key] = {**patches.get(key, {}), **patch}
            meta[key] = {**meta.get(key, {}), **patch_meta}
            if adds and zone.get("_file") != NEW_REGION:
                stats["merged_into_existing"] += 1
            if updates:
                stats["updates"] += 1
            target_key = key
        elif zone is not None and lifecycle:
            key = f"{zone['_file']}|{zone['name']}"
            meta.setdefault(key, {})["lifecycle"] = lifecycle
            target_key = key
        else:
            target_key = ""

        if calls:
            stats["calls"] += 1
            phone = phone_for(community, county, phones)
            question = question_text(calls, phone)
            if community.casefold() == "wauseon":
                question += " Also listed for the current-versus-future rate question: Dynegy 888-682-2170; Palmer Energy 419-491-1040."
            if target_key:
                bucket = meta.setdefault(target_key, {})
                bucket["question"] = question
                bucket["unresolved"] = True
                kind = "conflict" if any(conf_kind(row["confidence"]) == "conflict" for row in calls) else "escalate-call"
                bucket["verification"] = kind
                if any(
                    "unsourced" in (row.get("new_value") or "").lower()
                    or (row.get("new_value") or "").lower().startswith("unconfirmed")
                    for row in calls
                ):
                    patches.setdefault(target_key, {})
                    patches[target_key]["CURRENT_rate"] = ""
                    patches[target_key]["CURRENT_source"] = ""
                file_name, zone_name = target_key.split("|", 1)
                if zone_name and file_name != NEW_REGION:
                    existing = index.get((file_name, zone_name))
                    if existing is not None:
                        patches.setdefault(target_key, {})
                        patches[target_key]["STATUS_verification"] = kind
            else:
                unmatched_questions.append({
                    "community": community,
                    "county": county,
                    "question": question,
                })

        cleaned = cleanup_name(community).casefold()
        if target_key and (cleaned in MVCC_TOWNS or (cleaned == "union" and county.casefold() == "montgomery")):
            bucket = meta.setdefault(target_key, {})
            if MVCC_QUESTION not in (bucket.get("question") or ""):
                bucket["question"] = ((bucket.get("question") or "") + " " + MVCC_QUESTION).strip()

    by_file: dict[str, list] = {}
    for fname in sorted(os.listdir(REGIONS_DIR)):
        if fname.endswith(".json") and fname != NEW_REGION:
            with open(os.path.join(REGIONS_DIR, fname), encoding="utf-8") as handle:
                by_file[fname] = json.load(handle)
    # Apply align on freshly loaded dicts, then write changed files.
    flat = []
    for fname, items in by_file.items():
        for item in items:
            item["_file"] = fname
            flat.append(item)
    changed = set(align_named_zones(flat))

    def keep_lifecycle(life: dict | None) -> bool:
        if not life:
            return False
        if life.get("confidence") not in {"confirmed", "likely"}:
            return False
        return life.get("status") not in {"unknown", "other"}

    for bucket in meta.values():
        if not keep_lifecycle(bucket.get("lifecycle")):
            bucket.pop("lifecycle", None)

    def add_question(key: str, text: str) -> None:
        bucket = meta.setdefault(key, {})
        if text not in (bucket.get("question") or ""):
            bucket["question"] = ((bucket.get("question") or "") + " " + text).strip()

    add_question(
        "cincinnati_duke_suburbs.json|Wyoming",
        "Unresolved question. Confirm the electric program ended in July 2026 and whether a restart is planned. Phone: City of Wyoming 513-821-7600; Energy Alliances 513-794-5555 / 800-735-0359.",
    )
    meta["cincinnati_duke_suburbs.json|Wyoming"]["unresolved"] = True
    meta["cincinnati_duke_suburbs.json|Wyoming"]["verification"] = "escalate-call"
    add_question(
        "nw_central_ohio.json|Fremont",
        "Two Dynegy tiers. Toledo Edison accounts 9.96¢ August 2026–December 2027. AEP Ohio accounts 10.67¢ July 2026–December 2027.",
    )
    add_question(
        "ne_ohio_firstenergy.json|Plain Township",
        "The township page lists both AEP Ohio and Ohio Edison. The AEP-area NOPEC price is unverified. Phone: NOPEC 855-667-3201.",
    )
    for fname in changed:
        write_region(fname, by_file[fname])

    new_clean = []
    for zone in new_zones:
        new_clean.append({key: value for key, value in zone.items() if not key.startswith("_")})
    new_clean.sort(key=lambda item: (item["region"], item["name"]))
    with open(os.path.join(REGIONS_DIR, NEW_REGION), "w", encoding="utf-8") as handle:
        handle.write(json.dumps(new_clean, indent=2, ensure_ascii=False) + "\n")

    unverified = []
    for row in changes:
        if row["classification"] == "add" and conf_kind(row["confidence"]) == "single" and " vs " not in row["community"]:
            unverified.append({
                "community": row["community"],
                "county": row["county"],
                "field": row["field"],
                "value": row["new_value"],
                "confidence": "single-source",
                "sources": row.get("sources") or "",
                "notes": row.get("notes") or "",
                "flag": "single-source — not confirmed. Not a battlecard rate.",
            })
    unverified.extend(partial_adds)
    stats["unverified_rows"] = len(unverified)
    stats["partial_adds"] = len(partial_adds)
    with open(UNVERIFIED_PATH, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["community", "county", "field", "value", "confidence", "sources", "notes", "flag"],
            lineterminator="\r\n",
        )
        writer.writeheader()
        writer.writerows(unverified)

    overlay = {
        "patches": patches,
        "synthetic": synthetic,
        "meta": meta,
        "unmatched_questions": unmatched_questions,
        "stats": stats,
    }
    with open(OVERLAY_PATH, "w", encoding="utf-8") as handle:
        json.dump(overlay, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(json.dumps({
        "new_zones": len(new_clean),
        "patches": len(patches),
        "meta": len(meta),
        "unmatched_questions": len(unmatched_questions),
        "changed_region_files": sorted(changed),
        **stats,
    }, indent=2))


if __name__ == "__main__":
    main()
