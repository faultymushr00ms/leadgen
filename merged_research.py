"""Merged-research overlay for battlecards, hot leads, and unverified adds.

The overlay is generated from the October 15 merged reconciliation. Loading
zones does not rewrite region files. Confirmed and likely field changes are
applied in memory. Single-source adds stay in the unverified-leads layer.
"""

from __future__ import annotations

import csv
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
RESEARCH_DIR = os.path.join(ROOT, "data", "research")
OVERLAY_PATH = os.path.join(RESEARCH_DIR, "merged_overlay.json")
HOT_LEADS_PATH = os.path.join(RESEARCH_DIR, "merged_hot_leads.csv")
UNVERIFIED_PATH = os.path.join(RESEARCH_DIR, "unverified_leads.csv")

_overlay_cache: dict | None = None
_hot_cache: list | None = None
_unverified_cache: list | None = None

_ENDED_LIKE = {"ended", "rate_pending", "seeking_supplier", "certified_not_launched"}


def load_overlay() -> dict:
    global _overlay_cache
    if _overlay_cache is not None:
        return _overlay_cache
    if not os.path.exists(OVERLAY_PATH):
        _overlay_cache = {"patches": {}, "synthetic": {}, "meta": {}, "unmatched_questions": []}
        return _overlay_cache
    import json
    with open(OVERLAY_PATH, encoding="utf-8") as handle:
        _overlay_cache = json.load(handle)
    return _overlay_cache


def prepare_row(source_file: str, name: str, row: dict | None) -> dict | None:
    """Return the dataset row plus a confirmed/likely patch, or a synthetic add."""
    overlay = load_overlay()
    key = f"{source_file}|{name}"
    if row is None:
        base = (overlay.get("synthetic") or {}).get(key)
        if not base:
            return None
        row = dict(base)
    else:
        row = dict(row)
    patch = (overlay.get("patches") or {}).get(key) or {}
    row.update(patch)
    return row


def annotate(zone: dict) -> None:
    """Attach lifecycle, future notes, and call questions. Does not edit the zone file."""
    research = zone.get("research")
    if not research:
        return
    source_file = f"{zone.get('_source_file', '')}.json"
    key = f"{source_file}|{zone.get('name') or ''}"
    meta = (load_overlay().get("meta") or {}).get(key) or {}
    if meta.get("lifecycle"):
        research["lifecycle"] = meta["lifecycle"]
    if meta.get("futureNote"):
        research["futureNote"] = meta["futureNote"]
    if meta.get("utilityDetail"):
        research["utilityDetail"] = meta["utilityDetail"]
    question = (meta.get("question") or "").strip()
    if question and question not in (research.get("openQuestions") or ""):
        research["openQuestions"] = ((research.get("openQuestions") or "") + " " + question).strip()
    lifecycle = research.get("lifecycle") or {}
    status = lifecycle.get("status") or ""
    if status in _ENDED_LIKE:
        hook = research.get("hook") or ""
        generated = "¢/kWh" in hook and " — " in hook
        if status != "ended" or generated:
            research["hookAllowed"] = False
            research["hook"] = None
        research["takeaway"] = _lifecycle_takeaway(lifecycle)
    caveat = (zone.get("notes") or "").strip()
    if "not in this program" in caveat and caveat not in (research.get("takeaway") or ""):
        research["takeaway"] = ((research.get("takeaway") or "").rstrip() + " " + caveat).strip()
    if meta.get("unresolved"):
        info = research.setdefault("status", {})
        verification = meta.get("verification") or "escalate-call"
        info["unresolved"] = True
        info["verification"] = verification
        info["verificationLabel"] = "needs call" if verification == "escalate-call" else "conflict"
        research["hookAllowed"] = False
        research["hook"] = None
        if status not in _ENDED_LIKE:
            research["takeaway"] = (
                "Verify before using. Needs call — this record is unresolved and is not marked inactive."
            )


def _lifecycle_takeaway(lifecycle: dict) -> str:
    status = lifecycle.get("status") or ""
    detail = (lifecycle.get("detail") or "").strip()
    if status == "ended":
        when = lifecycle.get("endedDate") or "date not stated"
        reason = lifecycle.get("reason") or detail or "reason not stated"
        sources = lifecycle.get("sources") or "source not stated"
        return f"Ended {when}. {reason} Sources: {sources}"
    if status == "rate_pending":
        return "Rate pending. " + (detail or "No launched aggregation rate.")
    if status == "seeking_supplier":
        return "Seeking a supplier. No aggregation rate to quote."
    if status == "certified_not_launched":
        return "Certified but not launched. A PUCO certificate is certification only."
    return detail or "Verify before using."


def load_hot_leads() -> list[dict]:
    global _hot_cache
    if _hot_cache is not None:
        return _hot_cache
    rows = []
    if os.path.exists(HOT_LEADS_PATH):
        with open(HOT_LEADS_PATH, newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    _hot_cache = rows
    return rows


def load_unverified_leads() -> list[dict]:
    global _unverified_cache
    if _unverified_cache is not None:
        return _unverified_cache
    rows = []
    if os.path.exists(UNVERIFIED_PATH):
        with open(UNVERIFIED_PATH, newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    _unverified_cache = rows
    return rows


def unverified_groups() -> list[dict]:
    grouped: dict[tuple, dict] = {}
    for row in load_unverified_leads():
        key = (row.get("community") or "", row.get("county") or "")
        bucket = grouped.setdefault(key, {
            "community": key[0],
            "county": key[1],
            "fields": [],
            "confidence": row.get("confidence") or "single-source",
            "flags": [],
        })
        flag = (row.get("flag") or "single-source — not confirmed").strip()
        if flag and flag not in bucket["flags"]:
            bucket["flags"].append(flag)
        if (row.get("confidence") or "").startswith("likely"):
            bucket["confidence"] = row["confidence"]
        bucket["fields"].append({
            "field": row.get("field") or "",
            "value": row.get("value") or "",
            "sources": row.get("sources") or "",
        })
    groups = []
    for bucket in grouped.values():
        flags = bucket.pop("flags")
        flags.sort(key=lambda item: (0 if item.startswith("likely") else 1, item))
        bucket["flag"] = " ".join(flags) if flags else "single-source — not confirmed"
        groups.append(bucket)
    groups.sort(key=lambda item: (item["county"].lower(), item["community"].lower()))
    return groups


def unmatched_questions() -> list[dict]:
    return list(load_overlay().get("unmatched_questions") or [])
