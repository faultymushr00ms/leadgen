"""Load the reconciliation dataset beside the original FORGE zone records.

Original region JSON is not rewritten. Each loaded zone keeps its FORGE
fields and gains ``original`` (a snapshot of those fields), ``research``
(normalized rates, four status fields, sources, corrections), and ``card``
(display values for battlecards).

Rate changes are computed only when both sides are externally sourced and
share a rate basis. A genuine prior or historical rate stays on file and is
not treated as a current sourced rate. A proven-incorrect value is removed
and is not shown. Escalate-call and conflict rows stay unresolved; they are
not marked inactive.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import uuid
from collections import defaultdict
from datetime import date, datetime, timezone
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
RESEARCH_DIR = os.path.join(ROOT, "data", "research")
DATASET_PATH = os.path.join(RESEARCH_DIR, "forge_corrected_dataset.csv")
LEDGER_PATH = os.path.join(RESEARCH_DIR, "rate_ledger.csv")
QUEUE_PATH = os.path.join(RESEARCH_DIR, "investigation_queue.csv")
PTC_PATH = os.path.join(RESEARCH_DIR, "price_to_compare.json")
MONITOR_QUEUE_PATH = os.path.join(RESEARCH_DIR, "monitor_additions.csv")
CORRECTIONS_PATH = os.path.join(RESEARCH_DIR, "corrections.jsonl")

ORIGINAL_FIELDS = (
    "name",
    "region",
    "utility",
    "utilityParent",
    "utilityConfidence",
    "aggregationStatus",
    "currentRate",
    "previousRate",
    "rateChange",
    "supplier",
    "termStart",
    "termEnd",
    "status",
    "confidence",
    "takeaway",
    "hook",
    "futureUse",
    "notes",
    "lastVerified",
    "sourceUrl",
)

UNRESOLVED_VERIFICATIONS = {"escalate-call", "conflict"}

COMMERCIAL_APPLICABILITY = (
    "Aggregation covers residential and small commercial only. "
    "Large C&I accounts are usually excluded or opt out."
)

MONITOR_FIELDS = [
    "added_on",
    "zone",
    "region",
    "utility",
    "stored_rate",
    "observed_rate",
    "stored_supplier",
    "observed_supplier",
    "source_url",
    "accessed_at",
    "change",
    "exact_next_action",
    "STATUS_verification",
    "STATUS_program",
    "STATUS_term",
    "record_id",
    "recorded_at",
    "supersedes",
    "record_kind",
]

_dataset_cache: dict | None = None
_ledger_cache: list | None = None
_queue_cache: list | None = None
_ptc_cache: dict | None = None
_corrections_cache: list | None = None

_RATE_RE = re.compile(r"-?\d+(?:\.\d+)?")
_HIST_RE = re.compile(r"(-?\d+(?:\.\d+)?)\s*\(([^)]*)\)")


def parse_rate(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    match = _RATE_RE.search(text.replace(",", ""))
    if not match:
        return None
    return float(match.group(0))


def is_externally_sourced(source: str | None) -> bool:
    """A FORGE repo stamp is provenance, not an external source."""
    text = (source or "").strip()
    if not text:
        return False
    low = text.lower()
    if low.startswith("forge") or "unsourced" in low:
        return False
    return "http://" in low or "https://" in low


def basis_family(basis: str | None) -> str:
    text = (basis or "").lower()
    if "price to compare" in text or text == "ptc":
        return "ptc"
    if "aggregation" in text:
        return "aggregation"
    if not text:
        return "unknown"
    return text


def basis_from_source(source: str | None, explicit: str | None = None) -> str:
    if explicit:
        family = basis_family(explicit)
        if family != "unknown":
            return explicit
    url = (source or "").lower()
    if "energychoice.ohio.gov" in url or "price to compare" in url or "apples" in url:
        return "utility Price to Compare (default service, no aggregation found)"
    if any(host in url for host in (
        "dynegy.com", "nopec.org", "sopec", "constellation.com", "mvcc.net",
        "energyalliances", "wglenergy", "directenergy",
    )):
        return "aggregation program"
    return explicit or ""


def comparable_change(
    current_rate,
    current_source,
    current_basis,
    other_rate,
    other_source,
    other_basis,
) -> dict:
    """Cents and percent change, only when the two rates can be compared.

    Comparable means both numbers exist, both are externally sourced, and
    they are not different products (aggregation vs Price to Compare).
    """
    current = parse_rate(current_rate)
    other = parse_rate(other_rate)
    empty = {"comparable": False, "reason": "missing_rate", "cents": None, "percent": None}
    if current is None or other is None:
        return empty
    if not is_externally_sourced(current_source) or not is_externally_sourced(other_source):
        return {"comparable": False, "reason": "unsourced", "cents": None, "percent": None}
    current_family = basis_family(current_basis)
    other_family = basis_family(other_basis)
    if (
        current_family != "unknown"
        and other_family != "unknown"
        and current_family != other_family
    ):
        return {"comparable": False, "reason": "different_basis", "cents": None, "percent": None}
    if other == 0:
        return {"comparable": False, "reason": "zero_baseline", "cents": None, "percent": None}
    cents = round(current - other, 3)
    percent = round((current - other) / other * 100, 1)
    return {
        "comparable": True,
        "reason": "ok",
        "cents": cents,
        "percent": percent,
        "current": current,
        "other": other,
    }


def historical_benchmark(text: str | None, current_rate) -> dict:
    """Earliest archived rate that is not the current term's rate.

    Wayback strings often repeat the current price from a later capture.
    The benchmark is the earlier, different rate, with its capture note.
    """
    raw = (text or "").strip()
    if not raw:
        return {"rate": None, "rate_raw": "", "label": "", "capture": ""}
    parts = [part.strip() for part in raw.split(";") if part.strip()]
    parsed = []
    for part in parts:
        match = _HIST_RE.search(part)
        if match:
            parsed.append((float(match.group(1)), match.group(2).strip(), part))
        else:
            rate = parse_rate(part)
            if rate is not None:
                parsed.append((rate, "", part))
    if not parsed:
        return {"rate": None, "rate_raw": "", "label": "", "capture": ""}
    current = parse_rate(current_rate)
    differing = [
        item for item in parsed
        if current is None or abs(item[0] - current) > 0.0001
    ]
    chosen = differing[0] if differing else parsed[0]
    capture = ""
    cap = re.search(r"Wayback\s+(\d{8})", chosen[1])
    if cap:
        stamp = cap.group(1)
        capture = f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:8]}"
    return {
        "rate": chosen[0],
        "rate_raw": _trim_number(chosen[0]),
        "label": chosen[2],
        "capture": capture,
    }


def _trim_number(value: float) -> str:
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return text


def _split_urls(text: str | None) -> list[str]:
    if not text:
        return []
    parts = re.split(r"\s*\|\|\s*|\s*;\s*", text)
    urls = []
    for part in parts:
        part = part.strip()
        if part.lower().startswith("http"):
            urls.append(part.split()[0])
    return urls


def source_tier(url: str | None) -> str:
    """Tier from the methodology in the reconciliation skill proposal.

    1 community document, 2 administrator/supplier, 3 regulator, 4 secondary.
    Empty when the string is not a URL. This labels a URL; it does not
    confirm the rate.
    """
    raw = (url or "").strip()
    if not raw.lower().startswith("http"):
        return ""
    target = raw.lower()
    if "web.archive.org" in target:
        # The archived URL sits after the timestamp.
        archived = re.search(r"web\.archive\.org/web/\d+/(https?://\S+)", raw, re.I)
        if archived:
            target = archived.group(1).lower()
    if any(host in target for host in (
        "puco.ohio.gov", "energychoice.ohio.gov", "dis.puc.state.oh.us",
    )):
        return "3"
    if any(host in target for host in (
        "dynegy.com", "nopec.org", "sopec", "constellation.com", "mvcc.net",
        "energyalliances.com", "vistra", "wglenergy", "directenergy",
        "igsenergy.com", "aepenergy.com",
    )):
        return "2"
    if ".gov" in target or ".oh.us" in target:
        return "1"
    return "4"


def _blank_to_none(text: str | None):
    text = (text or "").strip()
    return text or None


def _load_dataset_index() -> dict[tuple[str, str], dict]:
    global _dataset_cache
    if _dataset_cache is not None:
        return _dataset_cache
    index = {}
    if not os.path.exists(DATASET_PATH):
        _dataset_cache = index
        return index
    with open(DATASET_PATH, newline="") as handle:
        for row in csv.DictReader(handle):
            index[(row["source_file"], row["orig_name"])] = row
    _dataset_cache = index
    return index


def _correction(row: dict) -> dict:
    evidence = row.get("CORR_evidence") or ""
    quotes = row.get("CORR_evidence_quotes") or ""
    evidence_parts = [part.strip() for part in evidence.split("||")]
    quote_parts = [part.strip() for part in quotes.split("||")]
    sources = []
    for idx, part in enumerate(evidence_parts):
        url = ""
        for token in part.split():
            if token.lower().startswith("http"):
                url = token
                break
        quote = quote_parts[idx] if idx < len(quote_parts) else ""
        if url or quote:
            sources.append({
                "url": url,
                "tier": source_tier(url),
                "accessedAt": (row.get("research_sources_accessed") or "").replace(" ET", ""),
                "quote": quote,
            })
    return {
        "oldValue": row.get("CORR_original_forge_value") or "",
        "previousResearchedValue": row.get("CORR_previous_researched_value") or "",
        "newValue": row.get("CORR_new_value") or "",
        "evidence": evidence,
        "evidenceQuotes": quotes,
        "sourceUrls": _split_urls(evidence),
        "date": row.get("CORR_date") or "",
        "reason": row.get("CORR_reason") or "",
        "type": row.get("CORR_type") or "",
        "uncertainty": row.get("CORR_uncertainty") or "",
        "sources": sources,
    }


def _period(rate_raw, source, basis, start, end, accessed) -> dict:
    raw = (rate_raw or "").strip()
    return {
        "rate": parse_rate(raw),
        "rate_raw": raw,
        "termStart": (start or "").strip(),
        "termEnd": (end or "").strip(),
        "source": (source or "").strip(),
        "sourced": is_externally_sourced(source),
        "basis": basis_from_source(source, basis),
        "accessedAt": (accessed or "").replace(" ET", "").strip(),
    }


def _verification_label(verification: str) -> str:
    if verification == "escalate-call":
        return "needs call"
    if verification == "conflict":
        return "conflict"
    return verification or "unknown"


def _factual_lines(jurisdiction, period, supplier, basis) -> str:
    rate = period.get("rate_raw") or ""
    start = period.get("termStart") or ""
    end = period.get("termEnd") or ""
    term = ""
    if start or end:
        term = f", term {start or '—'}–{end or '—'}"
    who = supplier or "supplier not named on the sourced row"
    product = basis or "rate"
    return f"{jurisdiction} — {who} at {rate}¢/kWh ({product}){term}."


def build_research(row: dict) -> dict:
    accessed = (row.get("research_sources_accessed") or "").strip()
    current = _period(
        row.get("CURRENT_rate"),
        row.get("CURRENT_source"),
        row.get("CURRENT_rate_basis"),
        row.get("CURRENT_term_start"),
        row.get("CURRENT_term_end"),
        accessed,
    )
    prior_explicit = (row.get("PRIOR_basis") or "").strip()
    prior_basis = prior_explicit or basis_from_source(row.get("PRIOR_source"), "")
    prior = _period(
        row.get("PRIOR_rate"),
        row.get("PRIOR_source"),
        prior_basis,
        "",
        "",
        "",
    )
    prior["term"] = (row.get("PRIOR_term") or "").strip()
    future = _period(
        row.get("FUTURE_rate"),
        row.get("FUTURE_source"),
        basis_from_source(row.get("FUTURE_source"), "aggregation program" if row.get("FUTURE_rate") else ""),
        row.get("FUTURE_term_start"),
        row.get("FUTURE_term_end"),
        accessed,
    )
    hist_source = (row.get("HISTORICAL_source") or "").strip()
    benchmark = historical_benchmark(row.get("HISTORICAL_rate_benchmark"), current["rate_raw"])
    historical = {
        "benchmark": (row.get("HISTORICAL_rate_benchmark") or "").strip(),
        "repoRateTrail": (row.get("HISTORICAL_repo_rate_trail") or "").strip(),
        "source": hist_source,
        "sourced": is_externally_sourced(hist_source),
        "basis": basis_from_source(hist_source, "aggregation program" if hist_source else ""),
        "rate": benchmark["rate"],
        "rate_raw": benchmark["rate_raw"],
        "label": benchmark["label"],
        "capture": benchmark["capture"],
    }
    verification = (row.get("STATUS_verification") or "").strip()
    program = (row.get("STATUS_program") or "").strip()
    unresolved = verification in UNRESOLVED_VERIFICATIONS
    not_eligible = program.startswith("not_eligible")
    # A municipal utility named on a conflict row is not silently dropped.
    hook_allowed = (
        verification in {"confirmed", "likely"}
        and current["sourced"]
        and not not_eligible
        and not unresolved
    )
    change_prior = comparable_change(
        current["rate_raw"], current["source"], current["basis"],
        prior["rate_raw"], prior["source"], prior["basis"] or current["basis"],
    )
    change_hist = comparable_change(
        current["rate_raw"], current["source"], current["basis"],
        historical["rate_raw"], historical["source"], historical["basis"],
    )
    change_future = comparable_change(
        future["rate_raw"], future["source"], future["basis"],
        current["rate_raw"], current["source"], current["basis"],
    )
    jurisdiction = (row.get("norm_jurisdiction") or row.get("orig_name") or "").strip()
    supplier = (row.get("norm_supplier") or "").strip()
    if hook_allowed:
        hook = _factual_lines(jurisdiction, current, supplier, current["basis"])
        if future["sourced"] and future["rate_raw"]:
            hook += (
                f" A later term of {future['rate_raw']}¢/kWh is dated "
                f"{future['termStart'] or '—'}–{future['termEnd'] or '—'}."
            )
        takeaway = (
            f"{jurisdiction} is recorded as {program.replace('_', ' ')} "
            f"with {supplier or 'the sourced supplier'} at {current['rate_raw']}¢/kWh"
            f" ({verification})."
        )
    else:
        hook = None
        if unresolved:
            takeaway = (
                f"Verify before using. {_verification_label(verification).capitalize()} "
                "— this record is unresolved and is not marked inactive."
            )
        elif not_eligible:
            takeaway = "Not eligible for competitive retail supply. Municipal utility or electric cooperative."
        elif not current["sourced"]:
            takeaway = "No externally sourced current rate. FORGE-recorded numbers are history only."
        else:
            takeaway = "Verify before using."

    correction = _correction(row)
    return {
        "jurisdiction": jurisdiction,
        "county": (row.get("norm_county") or "").strip(),
        "utility": (row.get("norm_utility") or "").strip(),
        "administrator": (row.get("norm_program_administrator") or "").strip(),
        "supplier": supplier,
        "current": current,
        "prior": prior,
        "historical": historical,
        "future": future,
        "status": {
            "program": program,
            "term": (row.get("STATUS_term") or "").strip(),
            "verification": verification,
            "verificationLabel": _verification_label(verification),
            "salesSignal": (row.get("STATUS_sales_signal_original") or "").strip(),
            "unresolved": unresolved,
        },
        "notEligible": not_eligible,
        "openQuestions": (row.get("open_questions") or "").strip(),
        "accessedAt": accessed.replace(" ET", "").strip(),
        "corrections": [correction],
        "changeVsPrior": change_prior,
        "changeVsHistorical": change_hist,
        "changeVsFuture": change_future,
        "hookAllowed": hook_allowed,
        "hook": hook,
        "takeaway": takeaway,
    }


def build_card(zone: dict) -> dict:
    research = zone.get("research") or {}
    current = research.get("current") or {}
    prior = research.get("prior") or {}
    historical = research.get("historical") or {}
    future = research.get("future") or {}
    status = research.get("status") or {}
    source_file = zone.get("_source_file") or ""
    name = zone.get("name") or ""
    return {
        "name": name,
        "sourceFile": source_file,
        "url": "/card?file=" + quote(source_file) + "&name=" + quote(name),
        "jurisdiction": research.get("jurisdiction") or name,
        "county": research.get("county") or "",
        "utility": research.get("utilityDetail") or research.get("utility") or zone.get("utility") or "",
        "utilityDetail": research.get("utilityDetail") or "",
        "lifecycle": research.get("lifecycle") or None,
        "futureNote": research.get("futureNote") or "",
        "currentCaption": (
            "Last aggregation rate"
            if (research.get("lifecycle") or {}).get("status") == "ended"
            and "aggregation" in (current.get("basis") or "").lower()
            else "Current"
        ),
        "administrator": research.get("administrator") or "",
        "supplier": research.get("supplier") or "",
        "program": status.get("program") or "",
        "termStatus": status.get("term") or "",
        "verification": status.get("verification") or "",
        "verificationLabel": status.get("verificationLabel") or "",
        "unresolved": bool(status.get("unresolved")),
        "notEligible": bool(research.get("notEligible")),
        "hookAllowed": bool(research.get("hookAllowed")),
        "hook": research.get("hook"),
        "takeaway": research.get("takeaway") or "",
        "openQuestions": research.get("openQuestions") or "",
        "accessedAt": research.get("accessedAt") or "",
        "commercialApplicability": COMMERCIAL_APPLICABILITY,
        "currentLabel": current.get("rate_raw") or "",
        "currentSourced": bool(current.get("sourced")),
        "currentBasis": current.get("basis") or "",
        "currentSource": current.get("source") or "",
        "currentStart": current.get("termStart") or "",
        "currentEnd": current.get("termEnd") or "",
        "priorLabel": prior.get("rate_raw") or "",
        "priorSourced": bool(prior.get("sourced")),
        "priorTerm": prior.get("term") or "",
        "priorSource": prior.get("source") or "",
        "historicalLabel": historical.get("rate_raw") or "",
        "historicalText": historical.get("label") or historical.get("benchmark") or "",
        "historicalSourced": bool(historical.get("sourced")),
        "historicalCapture": historical.get("capture") or "",
        "historicalSource": historical.get("source") or "",
        "futureLabel": future.get("rate_raw") or "",
        "futureSourced": bool(future.get("sourced")),
        "futureStart": future.get("termStart") or "",
        "futureEnd": future.get("termEnd") or "",
        "futureSource": future.get("source") or "",
        "changePrior": research.get("changeVsPrior") if (research.get("changeVsPrior") or {}).get("comparable") else None,
        "changeHistorical": research.get("changeVsHistorical") if (research.get("changeVsHistorical") or {}).get("comparable") else None,
        "changeFuture": research.get("changeVsFuture") if (research.get("changeVsFuture") or {}).get("comparable") else None,
        "ptc": residential_ptc_for_card(zone),
        "forgeStatus": zone.get("status"),
        "forgeAggregation": zone.get("aggregationStatus"),
        "forgeSupplier": zone.get("supplier"),
        "forgeCurrentRate": zone.get("currentRate"),
        "forgePreviousRate": zone.get("previousRate"),
        "unsourcedForgeRates": research.get("unsourcedForgeRates") or [],
        "noGasAggregation": bool(research.get("noGasAggregation")),
        "rejectedRenewal": research.get("rejectedRenewal"),
        "municipalFlagUnconfirmed": municipal_flag_unconfirmed(zone, research),
        "supersededUtility": ((research.get("supersededResearch") or {}).get("utility") or ""),
        "supersededAt": ((research.get("supersededResearch") or {}).get("superseded_at") or ""),
        "removalNotes": _removal_notes_for(name),
    }


def load_corrections() -> list[dict]:
    """Append-only research corrections. Later lines can supersede earlier ids."""
    global _corrections_cache
    if _corrections_cache is not None:
        return _corrections_cache
    events = []
    if os.path.exists(CORRECTIONS_PATH):
        with open(CORRECTIONS_PATH, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
    by_id = {event.get("id"): event for event in events if event.get("id")}
    for event in events:
        prior_id = event.get("supersedes")
        if prior_id and prior_id in by_id:
            prior = by_id[prior_id]
            prior["superseded"] = True
            prior["superseded_at"] = event.get("recorded_at") or ""
    _corrections_cache = events
    return events


def _correction_event_for(source_file: str, name: str) -> dict | None:
    found = None
    for event in load_corrections():
        if event.get("superseded"):
            continue
        if event.get("source_file") == source_file and event.get("zone") == name:
            found = event
    return found


def _removal_notes_for(name: str) -> list[dict]:
    import history_store

    path = history_store.removal_notes_path()
    cached = getattr(_removal_notes_for, "_cache", None)
    if cached is None or cached[0] != path:
        cached = (path, history_store.load_removal_notes(path))
        _removal_notes_for._cache = cached
    return [note for note in cached[1] if note.get("zone") == name]


def _research_with_corrections(row: dict, source_file: str, name: str) -> dict:
    """Apply an appended correction. Incorrect values are not kept beside it."""
    event = _correction_event_for(source_file, name)
    if event is None:
        return build_research(row)
    drop_incorrect = bool(event.get("incorrect_history_removed"))
    previous = build_research(row)
    if not drop_incorrect:
        previous["superseded"] = True
        previous["superseded_at"] = event.get("recorded_at") or ""
        for old in previous.get("corrections") or []:
            old["superseded"] = True
            old["superseded_at"] = event.get("recorded_at") or ""
    merged = dict(row)
    merged.update(event.get("fields") or {})
    research = build_research(merged)
    extra = dict(event.get("correction") or {})
    extra.setdefault("date", (event.get("recorded_at") or "")[:10])
    extra.setdefault("type", "verified_correction")
    extra.setdefault("sourceUrls", [])
    extra.setdefault("sources", extra.get("sources") or [])
    if drop_incorrect:
        research["corrections"] = (research.get("corrections") or []) + [extra]
    else:
        research["supersededResearch"] = previous
        research["corrections"] = (previous.get("corrections") or []) + [extra]
    if event.get("hook"):
        research["hook"] = event["hook"]
        research["hookAllowed"] = True
    if event.get("takeaway"):
        research["takeaway"] = event["takeaway"]
    if not drop_incorrect:
        research["unsourcedForgeRates"] = event.get("unsourced_forge_rates") or []
    research["noGasAggregation"] = bool(event.get("no_gas_aggregation"))
    research["rejectedRenewal"] = event.get("rejected_renewal")
    return research


def attach_research(zones: list) -> list:
    """Add research fields. Does not change original FORGE values."""
    import merged_research

    index = _load_dataset_index()
    for zone in zones:
        # _source_file is the region key without .json
        key = (f"{zone.get('_source_file', '')}.json", zone.get("name"))
        name = zone.get("name") or ""
        row = index.get(key)
        if row is None:
            event = _correction_event_for(key[0], name)
            dataset_file = (event or {}).get("dataset_source_file") or ""
            if dataset_file:
                row = index.get((dataset_file, name))
        row = merged_research.prepare_row(key[0], name, row)
        snapshot = {field: zone.get(field) for field in ORIGINAL_FIELDS}
        zone["original"] = snapshot
        if row is None:
            zone["research"] = None
            zone["card"] = None
            continue
        # Guard: never copy research conclusions onto the FORGE status fields.
        before = {field: zone.get(field) for field in ("status", "aggregationStatus", "currentRate", "supplier")}
        zone["research"] = _research_with_corrections(row, key[0], name)
        merged_research.annotate(zone)
        zone["card"] = build_card(zone)
        for field, value in before.items():
            zone[field] = value
    import talking_points
    talking_points.attach(zones)
    return zones


def find_zone(zones: list, source_file: str, name: str) -> dict | None:
    source_file = (source_file or "").strip()
    if source_file.endswith(".json"):
        source_file = source_file[:-5]
    name_l = (name or "").strip().lower()
    for zone in zones:
        if zone.get("name", "").lower() == name_l and zone.get("_source_file") == source_file:
            return zone
    matches = [zone for zone in zones if zone.get("name", "").lower() == name_l]
    if len(matches) == 1 and not source_file:
        return matches[0]
    return None


def zones_named(zones: list, name: str) -> list:
    name_l = (name or "").strip().lower()
    return [zone for zone in zones if zone.get("name", "").lower() == name_l]


# ── Price to Compare ──────────────────────────────────────────────────────────

def load_ptc() -> dict:
    global _ptc_cache
    if _ptc_cache is None:
        with open(PTC_PATH) as handle:
            _ptc_cache = json.load(handle)
    return _ptc_cache


def municipal_flag_unconfirmed(zone: dict, research: dict | None = None) -> bool:
    """A conflict row whose research says the program is active.

    The stored municipal blacklist flag stays in the region file. The card
    treats that flag as unresolved until an owner correction confirms it.
    """
    research = research if research is not None else (zone.get("research") or {})
    status_info = research.get("status") or {}
    program = status_info.get("program") or ""
    return (
        bool(status_info.get("unresolved"))
        and program.startswith("active")
        and (zone.get("aggregationStatus") or "") == "municipal_utility"
    )


def _ptc_not_applicable(zone: dict, research: dict) -> bool:
    """Municipal utilities and cooperatives are outside Price to Compare."""
    if research.get("notEligible"):
        return True
    if municipal_flag_unconfirmed(zone, research):
        return False
    status = zone.get("aggregationStatus") or ""
    if status in {"municipal_utility", "electric_cooperative"}:
        return True
    return False


def residential_rate_gap(aggregation_rate, ptc_cents) -> dict | None:
    """Aggregation current minus the residential Price to Compare.

    This is a labeled residential cross-check. It does not treat the two
    rates as the same product for prior/historical change math.
    """
    current = parse_rate(aggregation_rate)
    other = parse_rate(ptc_cents)
    if current is None or other is None or other == 0:
        return None
    return {
        "cents": round(current - other, 3),
        "percent": round((current - other) / other * 100, 1),
        "customer_class": "residential",
        "aggregation_rate": current,
        "ptc_rate": other,
    }


def residential_ptc_for_card(zone: dict) -> dict:
    """PTC block for a battlecard. Does not rewrite stored rates."""
    research = zone.get("research") or {}
    if _ptc_not_applicable(zone, research):
        return {
            "applicable": False,
            "customer_class": "residential",
            "label": "PTC not applicable",
            "reason": "Municipal utility or electric cooperative.",
            "comparison": None,
        }
    row = ptc_for_utility(research.get("utility") or zone.get("utility") or "")
    if not row:
        return {
            "applicable": False,
            "customer_class": "residential",
            "label": "Price to Compare not assigned",
            "reason": (
                "This zone does not map to one investor-owned utility "
                "(Ohio Edison, The Illuminating Company, Toledo Edison, AEP Ohio, Duke Energy Ohio, or AES Ohio)."
            ),
            "comparison": None,
        }
    current = research.get("current") or {}
    comparison = None
    if current.get("sourced") and basis_family(current.get("basis")) == "aggregation":
        comparison = residential_rate_gap(current.get("rate_raw"), row.get("cents_per_kwh"))
    return {
        "applicable": True,
        "customer_class": "residential",
        "code": row.get("code"),
        "utility": row.get("utility"),
        "cents_per_kwh": row.get("cents_per_kwh"),
        "effective_start": row.get("effective_start") or "",
        "effective_end": row.get("effective_end") or "",
        "accessed_at": row.get("accessed_at") or "",
        "as_of": row.get("as_of") or "",
        "source": row.get("source") or "",
        "source_url": row.get("source_url") or "",
        "comparison": comparison,
    }


def ptc_for_utility(utility: str | None) -> dict | None:
    """Match one PTC row. Mixed-utility strings match nothing (do not guess)."""
    text = (utility or "").lower()
    if not text:
        return None
    hits = []
    if "ohio edison" in text:
        hits.append("OE")
    if "illuminating" in text:
        hits.append("CEI")
    if "toledo edison" in text:
        hits.append("TE")
    if "aep" in text:
        hits.append("AEP")
    if "duke" in text:
        hits.append("DUKE")
    if "aes" in text or "dayton p" in text:
        hits.append("AES")
    # Preserve order, drop dupes.
    ordered = []
    for code in hits:
        if code not in ordered:
            ordered.append(code)
    if len(ordered) != 1:
        return None
    code = ordered[0]
    for row in load_ptc().get("rates", []):
        if row.get("code") == code:
            return row
    return None


# ── NOPEC glance, counties, expiring ──────────────────────────────────────────

def nopec_glance(zones: list) -> dict:
    members = []
    for zone in zones:
        research = zone.get("research") or {}
        admin = research.get("administrator") or ""
        if admin.startswith("NOPEC"):
            members.append(zone)
    by_rate = defaultdict(list)
    for zone in members:
        current = (zone.get("research") or {}).get("current") or {}
        rate = current.get("rate_raw") or "(no current rate)"
        utility = (zone.get("research") or {}).get("utility") or ""
        term = f"{current.get('termStart') or ''}–{current.get('termEnd') or ''}".strip("–")
        by_rate[(rate, utility, term, current.get("basis") or "")].append(zone["name"])
    groups = []
    for (rate, utility, term, basis), names in sorted(by_rate.items(), key=lambda item: item[0][0]):
        groups.append({
            "rate": rate,
            "utility": utility,
            "term": term,
            "basis": basis,
            "count": len(names),
            "names": sorted(names),
        })
    verifications = defaultdict(int)
    for zone in members:
        label = ((zone.get("research") or {}).get("status") or {}).get("verification") or "unknown"
        verifications[label] += 1
    sources = sorted({
        ((zone.get("research") or {}).get("current") or {}).get("source") or ""
        for zone in members
    } - {""})
    return {
        "count": len(members),
        "groups": groups,
        "verifications": dict(verifications),
        "sources": sources,
        "accessedAt": "2026-10-14",
    }


def group_counties(zones: list) -> list[dict]:
    buckets = defaultdict(list)
    for zone in zones:
        county = ((zone.get("research") or {}).get("county") or "Unknown").strip() or "Unknown"
        buckets[county].append(zone)
    result = []
    for county in sorted(buckets):
        rows = sorted(buckets[county], key=lambda zone: zone.get("name") or "")
        result.append({"county": county, "count": len(rows), "zones": rows})
    return result


EXPIRING_TERMS = {
    "expiring_within_6_months",
    "expired",
    "future_term_announced_current_unknown",
}


def expiring_zones(zones: list, queue: list | None = None) -> list:
    scores = {}
    for item in queue or []:
        scores[(item.get("region"), item.get("zone"))] = item
    picked = []
    for zone in zones:
        research = zone.get("research") or {}
        status = research.get("status") or {}
        if status.get("term") not in EXPIRING_TERMS:
            continue
        item = scores.get((zone.get("_source_file"), zone.get("name"))) or {}
        picked.append({
            "zone": zone,
            "triggerScore": item.get("trigger_score") or "",
            "nextAction": item.get("exact_next_action") or "",
        })
    def sort_key(entry):
        end = ((entry["zone"].get("research") or {}).get("current") or {}).get("termEnd") or "9999"
        return (end, entry["zone"].get("name") or "")
    picked.sort(key=sort_key)
    return picked


def hotspot_zones(zones: list, queue: list | None = None, limit: int = 25) -> list:
    """Highest investigation-queue scores. Unresolved rows stay in the list."""
    by_key = {(zone.get("_source_file"), zone.get("name")): zone for zone in zones}
    ranked = []
    for item in queue or []:
        if item.get("superseded"):
            continue
        zone = by_key.get((item.get("region"), item.get("zone")))
        if zone is None:
            continue
        try:
            score = int(item.get("trigger_score") or 0)
        except ValueError:
            score = 0
        if score <= 0:
            continue
        ranked.append({"zone": zone, "item": item, "score": score})
    ranked.sort(key=lambda entry: (-entry["score"], entry["zone"].get("name") or ""))
    return ranked[:limit]


# ── Rate ledger ────────────────────────────────────────────────────────────────

def _role_from_date_type(date_type: str) -> str:
    text = (date_type or "").lower()
    if "future" in text:
        return "future"
    if "prior" in text:
        return "prior"
    if "current" in text:
        return "current"
    if "archived" in text or "wayback" in text:
        return "historical"
    if "forge" in text or "commit" in text:
        return "forge_recorded"
    return "other"


def load_rate_ledger() -> list[dict]:
    """Ledger rows with role, accessed date, and effective dates kept apart.

    The CSV is stored as delivered. Dataset periods add prior/current/future
    rows that carry administrator, utility, and basis. Customer class is
    filled only when the source URL itself states RateCode=1.
    """
    global _ledger_cache
    if _ledger_cache is not None:
        return _ledger_cache
    periods = []
    if os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH, newline="") as handle:
            for row in csv.DictReader(handle):
                rate_raw = (row.get("rate_c_kWh") or "").strip()
                source_url = (row.get("source_url") or "").strip()
                periods.append({
                    "origin": "rate_ledger.csv",
                    "zone": row.get("zone") or "",
                    "region": row.get("region") or "",
                    "role": _role_from_date_type(row.get("date_type") or ""),
                    "rate_raw": rate_raw,
                    "rate": parse_rate(rate_raw),
                    "effective_start": (row.get("term_start") or "").strip(),
                    "effective_end": (row.get("term_end") or "").strip(),
                    "supplier": (row.get("supplier") or "").strip(),
                    "administrator": "",
                    "customer_class": "RateCode=1" if "ratecode=1" in source_url.lower() else "",
                    "utility": "",
                    "basis": (row.get("evidence_tier") or "").strip(),
                    "source": (row.get("source") or "").strip(),
                    "source_url": source_url,
                    "accessed_at": (row.get("date") or "").strip(),
                    "date_type": (row.get("date_type") or "").strip(),
                    "sourced": is_externally_sourced(source_url),
                })
    index = _load_dataset_index()
    for (source_file, name), row in index.items():
        research = build_research(row)
        region = source_file[:-5] if source_file.endswith(".json") else source_file
        common = {
            "origin": "corrected_dataset",
            "zone": name,
            "region": region,
            "supplier": research["supplier"],
            "administrator": research["administrator"],
            "utility": research["utility"],
            "customer_class": "",
        }
        current = research["current"]
        if current["rate_raw"]:
            periods.append({
                **common,
                "role": "current",
                "rate_raw": current["rate_raw"],
                "rate": current["rate"],
                "effective_start": current["termStart"],
                "effective_end": current["termEnd"],
                "basis": current["basis"],
                "source": current["source"],
                "source_url": current["source"] if current["sourced"] else "",
                "accessed_at": current["accessedAt"],
                "date_type": "research accessed (current term)",
                "sourced": current["sourced"],
                "customer_class": "RateCode=1" if "ratecode=1" in (current["source"] or "").lower() else "",
            })
        prior = research["prior"]
        if prior["rate_raw"]:
            periods.append({
                **common,
                "role": "prior",
                "rate_raw": prior["rate_raw"],
                "rate": prior["rate"],
                "effective_start": "",
                "effective_end": prior.get("term") or "",
                "basis": prior["basis"],
                "source": prior["source"],
                "source_url": prior["source"] if prior["sourced"] else "",
                "accessed_at": "",
                "date_type": "prior term on the corrected dataset",
                "sourced": prior["sourced"],
            })
        historical = research["historical"]
        if historical["rate_raw"]:
            periods.append({
                **common,
                "role": "historical",
                "rate_raw": historical["rate_raw"],
                "rate": historical["rate"],
                "effective_start": "",
                "effective_end": "",
                "basis": historical["basis"],
                "source": historical["label"] or historical["benchmark"],
                "source_url": historical["source"],
                "accessed_at": historical["capture"],
                "date_type": "archived page capture (Wayback benchmark)",
                "sourced": historical["sourced"],
            })
        future = research["future"]
        if future["rate_raw"]:
            periods.append({
                **common,
                "role": "future",
                "rate_raw": future["rate_raw"],
                "rate": future["rate"],
                "effective_start": future["termStart"],
                "effective_end": future["termEnd"],
                "basis": future["basis"],
                "source": future["source"],
                "source_url": future["source"] if future["sourced"] else "",
                "accessed_at": future["accessedAt"],
                "date_type": "research accessed (future term)",
                "sourced": future["sourced"],
            })
    _apply_ledger_supersede(periods)
    _ledger_cache = periods
    return periods


def _apply_ledger_supersede(periods: list[dict]) -> None:
    """Mark matched rate_ledger.csv rows superseded. The CSV is not rewritten."""
    import history_store

    events = [
        event for event in history_store.load_events()
        if event.get("kind") == "rate_ledger"
        and event.get("action") == "supersede"
        and not event.get("superseded")
    ]
    for event in events:
        match = event.get("match") or {}
        if not match:
            continue
        for period in periods:
            if period.get("origin") != "rate_ledger.csv":
                continue
            if all(period.get(key) == value for key, value in match.items()):
                period["superseded"] = True
                period["superseded_at"] = event.get("recorded_at") or ""


def _mark_superseded_queue_rows(rows: list[dict]) -> None:
    """A later row for the same zone supersedes the earlier one. The file is not rewritten."""
    grouped: dict[tuple, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        grouped[(row.get("zone"), row.get("region"))].append(index)
    for key, indexes in grouped.items():
        if len(indexes) < 2:
            continue
        zone_name, region = key
        source_file = region if str(region).endswith(".json") else f"{region}.json"
        event = _correction_event_for(source_file, zone_name or "")
        stamp = (event or {}).get("recorded_at") or ""
        for index in indexes[:-1]:
            rows[index]["superseded"] = True
            rows[index]["superseded_at"] = stamp
    for event in load_corrections():
        if event.get("superseded"):
            continue
        dataset_file = event.get("dataset_source_file") or ""
        new_file = event.get("source_file") or ""
        if not dataset_file or dataset_file == new_file:
            continue
        old_region = dataset_file[:-5] if dataset_file.endswith(".json") else dataset_file
        zone_name = event.get("zone") or ""
        stamp = event.get("recorded_at") or ""
        for row in rows:
            if row.get("zone") == zone_name and row.get("region") == old_region:
                row["superseded"] = True
                row["superseded_at"] = stamp


def load_queue() -> list[dict]:
    global _queue_cache
    if _queue_cache is not None:
        return _queue_cache
    rows = []
    if os.path.exists(QUEUE_PATH):
        with open(QUEUE_PATH, newline="") as handle:
            for row in csv.DictReader(handle):
                row["queue_origin"] = "reconciliation"
                rows.append(row)
    _mark_superseded_queue_rows(rows)
    _queue_cache = rows
    return rows


def _monitor_record_id(row: dict, index: int) -> str:
    existing = (row.get("record_id") or "").strip()
    if existing:
        return existing
    raw = "|".join([
        str(index),
        row.get("zone") or "",
        row.get("region") or "",
        row.get("change") or "",
        row.get("source_url") or "",
        row.get("added_on") or "",
    ])
    return "legacy-" + hashlib.sha256(raw.encode()).hexdigest()[:16]


def annotate_monitor_rows(rows: list[dict]) -> list[dict]:
    """Mark superseded queue rows in memory. The file is not rewritten."""
    for index, row in enumerate(rows):
        row["record_id"] = _monitor_record_id(row, index)
    by_id = {row["record_id"]: row for row in rows}
    for row in rows:
        prior_id = (row.get("supersedes") or "").strip()
        if not prior_id or prior_id not in by_id:
            continue
        prior = by_id[prior_id]
        prior["superseded"] = True
        prior["superseded_at"] = row.get("recorded_at") or row.get("added_on") or ""
    return rows


def load_monitor_additions(path: str | None = None) -> list[dict]:
    path = path or MONITOR_QUEUE_PATH
    if not os.path.exists(path):
        return []
    with open(path, newline="") as handle:
        return annotate_monitor_rows(list(csv.DictReader(handle)))


def queue_for_zone(zone: dict, queue: list | None = None) -> dict | None:
    region = zone.get("_source_file") or ""
    name = zone.get("name") or ""
    found = None
    for item in queue if queue is not None else load_queue():
        if item.get("zone") == name and item.get("region") == region and not item.get("superseded"):
            found = item
    return found


# ── Refresh monitor (report only) ──────────────────────────────────────────────

def _norm_supplier(value: str) -> str:
    return re.sub(r"[^a-z]", "", (value or "").lower())[:12]


def _rates_differ(stored: str, observed: str) -> bool:
    left = parse_rate(stored)
    right = parse_rate(observed)
    if left is None or right is None:
        return (stored or "").strip() != (observed or "").strip()
    return abs(left - right) > 0.0005


def compare_observation(zone: dict, observation: dict) -> dict | None:
    """Return a queue item when an observation disagrees with stored research.

    Does not modify ``zone``. A blank observed rate is not a change unless
    ``rate_missing`` is set (the source page was fetched and no longer
    contains the stored rate). No replacement rate is invented.
    """
    research = zone.get("research") or {}
    current = research.get("current") or {}
    stored_rate = current.get("rate_raw") or ""
    stored_supplier = research.get("supplier") or ""
    observed_rate = str(observation.get("rate") or "").strip()
    observed_supplier = str(observation.get("supplier") or "").strip()
    rate_diff = bool(observed_rate) and bool(stored_rate) and _rates_differ(stored_rate, observed_rate)
    supplier_diff = bool(observed_supplier) and bool(stored_supplier) and (
        _norm_supplier(observed_supplier) != _norm_supplier(stored_supplier)
    )
    missing = bool(observation.get("rate_missing")) and bool(stored_rate)
    if not (rate_diff or supplier_diff or missing):
        return None
    bits = []
    if rate_diff:
        bits.append(f"observed rate {observed_rate} differs from stored {stored_rate}")
    if missing and not rate_diff:
        bits.append(f"stored rate {stored_rate} was not found on the source page")
    if supplier_diff:
        bits.append(f"observed supplier {observed_supplier} differs from stored {stored_supplier}")
    status = research.get("status") or {}
    action = (
        "Review this diff. Stored zone data was not changed. "
        + "; ".join(bits) + "."
    )
    return {
        "added_on": observation.get("accessed_at") or date.today().isoformat(),
        "zone": zone.get("name") or "",
        "region": zone.get("_source_file") or "",
        "utility": research.get("utility") or zone.get("utility") or "",
        "stored_rate": stored_rate,
        "observed_rate": observed_rate,
        "stored_supplier": stored_supplier,
        "observed_supplier": observed_supplier,
        "source_url": observation.get("source_url") or current.get("source") or "",
        "accessed_at": observation.get("accessed_at") or "",
        "change": "; ".join(bits),
        "exact_next_action": action,
        "STATUS_verification": status.get("verification") or "",
        "STATUS_program": status.get("program") or "",
        "STATUS_term": status.get("term") or "",
    }


def append_monitor_items(items: list[dict], path: str | None = None) -> list[dict]:
    """Append new diffs to the monitor queue. Skips exact duplicates.

    A newer different observation for the same zone appends a new row whose
    ``supersedes`` points at the prior row. The prior row is left as stored
    and is marked superseded, with a timestamp, when the file is read.
    """
    path = path or MONITOR_QUEUE_PATH
    existing = load_monitor_additions(path)
    seen = {
        (row.get("zone"), row.get("region"), row.get("change"), row.get("source_url"))
        for row in existing
    }
    active = {}
    for row in existing:
        if row.get("superseded"):
            continue
        active[(row.get("zone"), row.get("region"))] = row
    added = []
    recorded_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for item in items:
        key = (item.get("zone"), item.get("region"), item.get("change"), item.get("source_url"))
        if key in seen:
            continue
        seen.add(key)
        row = dict(item)
        row["record_id"] = row.get("record_id") or uuid.uuid4().hex
        row["recorded_at"] = row.get("recorded_at") or recorded_at
        row["record_kind"] = row.get("record_kind") or "observation"
        prior = active.get((row.get("zone"), row.get("region")))
        if prior and not row.get("supersedes"):
            row["supersedes"] = prior["record_id"]
        else:
            row["supersedes"] = row.get("supersedes") or ""
        active[(row.get("zone"), row.get("region"))] = {
            **row,
            "superseded": False,
        }
        added.append(row)
    if not added:
        return []
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    write_header = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MONITOR_FIELDS, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        for item in added:
            writer.writerow(item)
    return added


def zip_disclaimer() -> str:
    return (
        "A ZIP code is not proof of program eligibility. "
        "It only points at the jurisdiction stored for that ZIP. "
        "Confirm the city, village, or township and the utility at the street address."
    )
