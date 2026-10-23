#!/usr/bin/env python3
"""Read-only audit of every zone in data/regions.

Offline and deterministic: no LLM, no network, no writes under data/regions.
Writes data/reports/audit_YYYY-MM-DD.md and audit_YYYY-MM-DD.json.
"""

from __future__ import annotations

import argparse
import calendar
import json
import os
import re
import sys
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import rate_change

DEFAULT_REGIONS = os.path.join(ROOT, "data", "regions")
DEFAULT_DOCS = os.path.join(ROOT, "CLAUDE.md")
DEFAULT_OUT = os.path.join(ROOT, "data", "reports")

ACTIVE_STATUSES = {"pain_coming", "stable", "active"}
NO_PROGRAM = {"no_aggregation_verified", "municipal_utility", "electric_cooperative"}
RENEWAL_TOLERANCE_DAYS = 7
COPY_FIELDS = ("takeaway", "hook")
RENEWAL_FIELDS = ("takeaway", "hook", "notes")

ISSUE_TYPES = [
    ("status_after_term_end", "Status after term end"),
    ("stale_renewal_window", "Stale renewal window"),
    ("term_without_aggregation", "Term dates without an aggregation program"),
    ("rate_change_disagreement", "Stored rate change disagrees with computed percent"),
    ("rate_change_without_previous", "Rate change with no previous rate"),
    ("missing_current_rate", "Confirmed aggregation with no current rate"),
    ("missing_source_url", "Rate on file with no source URL"),
    ("last_verified_stale", "Last verified older than the threshold"),
    ("utility_contradiction", "Municipal or co-op noted as IOU territory"),
    ("text_number_mismatch", "Copy cites a number the fields do not hold"),
    ("doc_count_mismatch", "Documentation count does not match the data"),
    ("region_file_invalid", "Region file could not be read"),
]
TYPE_ORDER = {key: index for index, (key, _label) in enumerate(ISSUE_TYPES)}
TYPE_LABELS = dict(ISSUE_TYPES)

RATE_RE = re.compile(
    r"(?<![\d.])(\d+(?:\.\d+)?)(?:\s*¢|\s*cents?\b|\s*c\b)",
    re.IGNORECASE,
)
PERCENT_RE = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*%")
RENEWAL_RE = re.compile(r"renewal window opens in (\d+) days", re.IGNORECASE)
IOU_TERRITORY_RE = re.compile(
    r"\b(?:ohio edison|(?:the\s+)?illuminating company|toledo edison|"
    r"aep ohio|aes ohio|duke energy(?:\s+ohio)?|"
    r"dayton power(?:\s+(?:&|and)\s+light)?|dp&l)\s+territory\b",
    re.IGNORECASE,
)
QUALIFIER_RE = re.compile(
    r"\b(?:not|outside|except|excluding|beyond|adjacent|borders?|bordering|"
    r"near|nearby|surround(?:s|ing)?|overlap(?:s|ping)?|embedded|"
    r"formerly|previously|historically|was|were|may\s+be)\b",
    re.IGNORECASE,
)
HEADER_RE = re.compile(
    r"regions/\s+#\s*(\d+)\s+JSON files,\s*(\d+)\s+zones total"
)
FILE_LINE_RE = re.compile(r"^\s+([\w.-]+\.json)\s+#\s*(.+)$", re.MULTILINE)
COUNT_RE = re.compile(r"(?<![~\d])(\d+)(?!\d|\+)")
COOP_PROSE_RE = re.compile(r"All\s+(\d+)\s+Ohio co-ops")
NOAC_PROSE_RE = re.compile(r"\*\*NOAC\*\*:\s*(\d+)\b")
AUDIT_NAME_RE = re.compile(r"audit_(\d{4}-\d{2}-\d{2})\.json$")


def parse_term_end(value):
    """Last day a term is still in force, or None when the cell is empty.

    YYYY-MM counts through the last calendar day of that month.
    """
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"none", "null"}:
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        pass
    try:
        parsed = datetime.strptime(text, "%Y-%m")
    except ValueError:
        return None
    last_day = calendar.monthrange(parsed.year, parsed.month)[1]
    return date(parsed.year, parsed.month, last_day)


def _decimals(token: str) -> int:
    if "." not in token:
        return 0
    return len(token.split(".", 1)[1])


def number_matches(token: str, stored) -> bool:
    """True when token is stored, rounded to the decimals written in the copy."""
    number = rate_change.as_float(stored)
    if number is None:
        return False
    value = float(token.replace(",", ""))
    tolerance = 0.5 * (10 ** (-_decimals(token)))
    return abs(value - number) <= tolerance + 1e-9


def make_issue(issue_type: str, zone: dict, detail: str, fields: dict) -> dict:
    name = str(zone.get("name") or "")
    source = str(zone.get("_source_file") or "")
    return {
        "id": f"{issue_type}|{source}|{name}|{detail}",
        "type": issue_type,
        "zone": name,
        "sourceFile": source,
        "detail": detail,
        "fields": fields,
    }


def _has_term(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    return True


def _has_source(zone: dict) -> bool:
    url = zone.get("sourceUrl")
    if not isinstance(url, str):
        return False
    return url.strip().lower() not in {"", "none", "null"}


def _sentences(text: str) -> list[str]:
    sentences = []
    for chunk in re.split(r"[\n\r]+", text):
        sentences.extend(re.split(r"(?<=[.!?])\s+", chunk.strip()))
    return [sentence for sentence in sentences if sentence.strip()]


def _excerpt(text: str, start: int, end: int) -> str:
    snippet = text[max(0, start - 40): end + 40].replace("\n", " ").replace("`", "'")
    return " ".join(snippet.split())


def _ignorable_percent(text: str, match: re.Match) -> bool:
    token = match.group(1)
    if abs(float(token) - 100) > 0.001:
        return False
    window = text[max(0, match.start() - 40): match.end() + 40].lower()
    return re.search(r"renewable|carbon|usage|green|recs?\b", window) is not None


def check_zone(zone: dict, as_of: date, stale_days: int, issues: list) -> None:
    status = (zone.get("status") or "").strip().lower()
    term_end = parse_term_end(zone.get("termEnd"))
    if status in ACTIVE_STATUSES and term_end is not None and term_end < as_of:
        issues.append(make_issue(
            "status_after_term_end",
            zone,
            str(zone.get("termEnd")),
            {
                "status": zone.get("status"),
                "termStart": zone.get("termStart"),
                "termEnd": zone.get("termEnd"),
                "aggregationStatus": zone.get("aggregationStatus"),
            },
        ))

    for field in RENEWAL_FIELDS:
        text = zone.get(field) or ""
        if not isinstance(text, str):
            continue
        for match in RENEWAL_RE.finditer(text):
            stated = int(match.group(1))
            actual_days = None if term_end is None else (term_end - as_of).days
            if term_end is None:
                reason = "no termEnd"
            elif term_end < as_of:
                reason = "term ended"
            elif abs(actual_days - stated) > RENEWAL_TOLERANCE_DAYS:
                reason = "countdown differs"
            else:
                continue
            issues.append(make_issue(
                "stale_renewal_window",
                zone,
                f"{field}|{stated}",
                {
                    "field": field,
                    "statedDays": stated,
                    "actualDaysUntilTermEnd": actual_days,
                    "reason": reason,
                    "termEnd": zone.get("termEnd"),
                    "excerpt": _excerpt(text, match.start(), match.end()),
                },
            ))

    aggregation = zone.get("aggregationStatus")
    if aggregation in NO_PROGRAM and (
        _has_term(zone.get("termStart")) or _has_term(zone.get("termEnd"))
    ):
        issues.append(make_issue(
            "term_without_aggregation",
            zone,
            f"{zone.get('termStart')}|{zone.get('termEnd')}",
            {
                "aggregationStatus": aggregation,
                "termStart": zone.get("termStart"),
                "termEnd": zone.get("termEnd"),
                "status": zone.get("status"),
            },
        ))

    described = rate_change.describe(zone)
    gap = described["disagreement"]
    if gap is not None and gap > rate_change.DISAGREEMENT_POINTS:
        issues.append(make_issue(
            "rate_change_disagreement",
            zone,
            "rateChange",
            {
                "currentRate": zone.get("currentRate"),
                "previousRate": zone.get("previousRate"),
                "rateChange": zone.get("rateChange"),
                "computed": described["computed"],
                "disagreement": gap,
            },
        ))

    stored_change = rate_change.as_float(zone.get("rateChange"))
    previous = rate_change.as_float(zone.get("previousRate"))
    if stored_change is not None and previous is None:
        issues.append(make_issue(
            "rate_change_without_previous",
            zone,
            "previousRate",
            {
                "currentRate": zone.get("currentRate"),
                "previousRate": zone.get("previousRate"),
                "rateChange": zone.get("rateChange"),
            },
        ))

    if aggregation == "confirmed_active_aggregation" and rate_change.as_float(zone.get("currentRate")) is None:
        issues.append(make_issue(
            "missing_current_rate",
            zone,
            "currentRate",
            {
                "aggregationStatus": aggregation,
                "currentRate": zone.get("currentRate"),
                "supplier": zone.get("supplier"),
                "status": zone.get("status"),
            },
        ))

    if rate_change.as_float(zone.get("currentRate")) is not None and not _has_source(zone):
        issues.append(make_issue(
            "missing_source_url",
            zone,
            "sourceUrl",
            {
                "currentRate": zone.get("currentRate"),
                "sourceUrl": zone.get("sourceUrl"),
                "lastVerified": zone.get("lastVerified"),
                "aggregationStatus": aggregation,
            },
        ))

    verified_raw = zone.get("lastVerified")
    verified_text = "" if verified_raw is None else str(verified_raw).strip()
    if not verified_text or verified_text.lower() in {"none", "null"}:
        issues.append(make_issue(
            "last_verified_stale",
            zone,
            "missing",
            {
                "lastVerified": zone.get("lastVerified"),
                "ageDays": None,
                "thresholdDays": stale_days,
                "reason": "missing",
            },
        ))
    else:
        try:
            verified_on = datetime.strptime(verified_text, "%Y-%m-%d").date()
        except ValueError:
            issues.append(make_issue(
                "last_verified_stale",
                zone,
                "unparseable",
                {
                    "lastVerified": zone.get("lastVerified"),
                    "ageDays": None,
                    "thresholdDays": stale_days,
                    "reason": "unparseable",
                },
            ))
        else:
            age = (as_of - verified_on).days
            if age > stale_days:
                issues.append(make_issue(
                    "last_verified_stale",
                    zone,
                    verified_text,
                    {
                        "lastVerified": verified_text,
                        "ageDays": age,
                        "thresholdDays": stale_days,
                        "reason": "older than threshold",
                    },
                ))

    if aggregation in {"municipal_utility", "electric_cooperative"}:
        notes = zone.get("notes") or ""
        if isinstance(notes, str):
            for sentence in _sentences(notes):
                match = IOU_TERRITORY_RE.search(sentence)
                if not match or QUALIFIER_RE.search(sentence):
                    continue
                issues.append(make_issue(
                    "utility_contradiction",
                    zone,
                    match.group(0).lower(),
                    {
                        "aggregationStatus": aggregation,
                        "utility": zone.get("utility"),
                        "matched": match.group(0),
                        "sentence": sentence.strip(),
                    },
                ))
                break

    computed = rate_change.percent_change(zone.get("currentRate"), zone.get("previousRate"))
    seen = set()
    for field in COPY_FIELDS:
        text = zone.get(field) or ""
        if not isinstance(text, str) or not text:
            continue
        for match in RATE_RE.finditer(text):
            token = match.group(1)
            key = (field, "rate", token)
            if key in seen:
                continue
            seen.add(key)
            if number_matches(token, zone.get("currentRate")) or number_matches(token, zone.get("previousRate")):
                continue
            issues.append(make_issue(
                "text_number_mismatch",
                zone,
                f"{field}|rate|{token}",
                {
                    "field": field,
                    "kind": "rate",
                    "token": token,
                    "currentRate": zone.get("currentRate"),
                    "previousRate": zone.get("previousRate"),
                    "excerpt": _excerpt(text, match.start(), match.end()),
                },
            ))
        for match in PERCENT_RE.finditer(text):
            if _ignorable_percent(text, match):
                continue
            token = match.group(1)
            key = (field, "percent", token)
            if key in seen:
                continue
            seen.add(key)
            if number_matches(token, zone.get("rateChange")) or number_matches(token, computed):
                continue
            issues.append(make_issue(
                "text_number_mismatch",
                zone,
                f"{field}|percent|{token}",
                {
                    "field": field,
                    "kind": "percent",
                    "token": token,
                    "rateChange": zone.get("rateChange"),
                    "computed": computed,
                    "excerpt": _excerpt(text, match.start(), match.end()),
                },
            ))


def _doc_issue(label: str, detail: str, documented: int, actual, claim: str, extra: dict | None = None) -> dict:
    fields = {
        "label": label,
        "documented": documented,
        "actual": actual,
        "claim": claim,
    }
    if extra:
        fields.update(extra)
    return make_issue(
        "doc_count_mismatch",
        {"name": label, "_source_file": "CLAUDE.md"},
        detail,
        fields,
    )


def first_count(comment: str) -> int | None:
    match = COUNT_RE.search(comment)
    if not match:
        return None
    return int(match.group(1))


def check_docs(doc_text: str, zones: list, file_counts: dict) -> list:
    """Exact counts written in CLAUDE.md. Approximate figures (~14, 235+) are skipped."""
    if not doc_text:
        return []
    issues = []
    header = HEADER_RE.search(doc_text)
    if header:
        documented_files = int(header.group(1))
        documented_zones = int(header.group(2))
        claim = header.group(0).strip()
        if documented_files != len(file_counts):
            issues.append(_doc_issue(
                "JSON file count",
                "files_total",
                documented_files,
                len(file_counts),
                claim,
                {"actualFiles": sorted(file_counts)},
            ))
        if documented_zones != len(zones):
            issues.append(_doc_issue(
                "Zone count",
                "zones_total",
                documented_zones,
                len(zones),
                claim,
            ))
    for match in FILE_LINE_RE.finditer(doc_text):
        filename = match.group(1)
        comment = match.group(2).strip()
        documented = first_count(comment)
        if documented is None:
            continue
        actual = file_counts.get(filename)
        if actual != documented:
            extra = {"note": "file not in data/regions"} if actual is None else None
            issues.append(_doc_issue(
                filename,
                f"file:{filename}",
                documented,
                actual,
                comment,
                extra,
            ))
    coop = COOP_PROSE_RE.search(doc_text)
    if coop:
        documented = int(coop.group(1))
        actual = sum(1 for zone in zones if zone.get("aggregationStatus") == "electric_cooperative")
        if documented != actual:
            issues.append(_doc_issue(
                "Ohio co-op count",
                "prose:ohio_coops",
                documented,
                actual,
                coop.group(0),
            ))
    noac = NOAC_PROSE_RE.search(doc_text)
    if noac:
        documented = int(noac.group(1))
        actual = file_counts.get("toledo_lucas_noac.json")
        if documented != actual:
            issues.append(_doc_issue(
                "NOAC community count",
                "prose:noac",
                documented,
                actual,
                noac.group(0),
            ))
    return issues


def sort_key(item: dict) -> tuple:
    return (
        TYPE_ORDER.get(item.get("type"), 99),
        item.get("sourceFile") or "",
        item.get("zone") or "",
        item.get("detail") or "",
        item.get("id") or "",
    )


def _slim(item: dict) -> dict:
    return {
        "id": item.get("id") or "",
        "type": item.get("type") or "",
        "zone": item.get("zone") or "",
        "sourceFile": item.get("sourceFile") or "",
        "detail": item.get("detail") or "",
    }


def diff_issues(current: list, previous: dict | None) -> dict:
    if previous is None:
        return {
            "previousDate": None,
            "new": [],
            "resolved": [],
            "note": "No previous audit. Counts above are the baseline.",
        }
    if previous.get("error"):
        return {
            "previousDate": previous.get("previousDate"),
            "new": [],
            "resolved": [],
            "note": "Previous audit file could not be read.",
        }
    prev_by_id = {
        item["id"]: item
        for item in (previous.get("issues") or [])
        if isinstance(item, dict) and item.get("id")
    }
    cur_by_id = {item["id"]: item for item in current}
    new_ids = sorted(cur_by_id.keys() - prev_by_id.keys(), key=lambda item_id: sort_key(cur_by_id[item_id]))
    resolved_ids = sorted(prev_by_id.keys() - cur_by_id.keys(), key=lambda item_id: sort_key(prev_by_id[item_id]))
    previous_date = previous.get("previousDate")
    if not new_ids and not resolved_ids:
        note = f"No new or resolved issues since {previous_date}."
    else:
        note = f"Compared with {previous_date}."
    return {
        "previousDate": previous_date,
        "new": [_slim(cur_by_id[item_id]) for item_id in new_ids],
        "resolved": [_slim(prev_by_id[item_id]) for item_id in resolved_ids],
        "note": note,
    }


def build_report(zones, file_counts, extra_issues, doc_text, as_of: date, stale_days: int, previous) -> dict:
    issues = list(extra_issues)
    for zone in zones:
        check_zone(zone, as_of, stale_days, issues)
    issues.extend(check_docs(doc_text, zones, file_counts))
    issues.sort(key=sort_key)
    counts = {key: 0 for key, _label in ISSUE_TYPES}
    for item in issues:
        counts[item["type"]] = counts.get(item["type"], 0) + 1
    return {
        "asOf": as_of.isoformat(),
        "staleDays": stale_days,
        "zonesScanned": len(zones),
        "regionFiles": len(file_counts),
        "totalIssues": len(issues),
        "counts": counts,
        "changes": diff_issues(issues, previous),
        "issues": issues,
    }


def load_regions(regions_dir: str) -> tuple[list, dict, list]:
    zones = []
    file_counts = {}
    issues = []
    for fname in sorted(os.listdir(regions_dir)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(regions_dir, fname)
        try:
            with open(path, encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            issues.append(make_issue(
                "region_file_invalid",
                {"name": fname, "_source_file": fname[:-5]},
                "unreadable",
                {"path": fname, "reason": "unreadable"},
            ))
            continue
        if not isinstance(data, list):
            issues.append(make_issue(
                "region_file_invalid",
                {"name": fname, "_source_file": fname[:-5]},
                "not-a-list",
                {"path": fname, "reason": "not a list"},
            ))
            continue
        file_counts[fname] = len(data)
        source = fname[:-5]
        for record in data:
            if not isinstance(record, dict):
                continue
            zone = dict(record)
            zone["_source_file"] = source
            zones.append(zone)
    return zones, file_counts, issues


def load_previous(out_dir: str, as_of: date) -> dict | None:
    """Newest audit on or before as_of. Read this before overwriting today's file."""
    if not os.path.isdir(out_dir):
        return None
    candidates = []
    for name in os.listdir(out_dir):
        match = AUDIT_NAME_RE.fullmatch(name)
        if not match:
            continue
        try:
            day = date.fromisoformat(match.group(1))
        except ValueError:
            continue
        if day <= as_of:
            candidates.append((day, os.path.join(out_dir, name)))
    if not candidates:
        return None
    day, path = max(candidates)
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {"previousDate": day.isoformat(), "error": True, "issues": []}
    if not isinstance(data, dict):
        return {"previousDate": day.isoformat(), "error": True, "issues": []}
    data["previousDate"] = day.isoformat()
    return data


def fmt(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, float):
        text = f"{value:.6f}".rstrip("0").rstrip(".")
        return text or "0"
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def format_fields(fields: dict) -> str:
    parts = []
    for key, value in fields.items():
        if key == "label":
            continue
        if key == "excerpt":
            parts.append(f'excerpt "{value}"')
        elif key == "sentence":
            parts.append(f'sentence "{value}"')
        else:
            parts.append(f"{key} `{fmt(value)}`")
    return ", ".join(parts)


def _section_blurb(key: str, report: dict) -> str:
    if key == "status_after_term_end":
        return (
            "Status is pain_coming, stable, or active, and termEnd is before the audit date. "
            "A term written as YYYY-MM stays in force through the last day of that month."
        )
    if key == "stale_renewal_window":
        return (
            'Copy says "renewal window opens in N days" and that countdown is off by more than '
            f"{RENEWAL_TOLERANCE_DAYS} days, the term has ended, or termEnd is missing."
        )
    if key == "term_without_aggregation":
        return (
            "termStart or termEnd is set while aggregationStatus is no_aggregation_verified, "
            "municipal_utility, or electric_cooperative."
        )
    if key == "rate_change_disagreement":
        return (
            "Stored rateChange and the percent from currentRate vs previousRate "
            f"(rate_change, 1 decimal) differ by more than {rate_change.DISAGREEMENT_POINTS} points."
        )
    if key == "rate_change_without_previous":
        return "rateChange is stored and previousRate is null, so the percent cannot be recomputed."
    if key == "missing_current_rate":
        return "aggregationStatus is confirmed_active_aggregation and currentRate is null."
    if key == "missing_source_url":
        return "currentRate is set and sourceUrl is empty."
    if key == "last_verified_stale":
        return (
            f"lastVerified is missing, not YYYY-MM-DD, or more than {report['staleDays']} days "
            f"before {report['asOf']}."
        )
    if key == "utility_contradiction":
        return (
            "Classified municipal_utility or electric_cooperative, and a notes sentence assigns an "
            "IOU territory (Ohio Edison, Illuminating Company, Toledo Edison, AEP Ohio, AES Ohio, "
            "Duke Energy, Dayton Power & Light) without overlap, border, or negation language. "
            "The conflict can be a bad note or a bad classification."
        )
    if key == "text_number_mismatch":
        return (
            "A cents figure in takeaway or hook matches neither currentRate nor previousRate, "
            "or a percent matches neither stored rateChange nor the computed percent. "
            "100% renewable, carbon, usage, or green wording is ignored. "
            "Tolerance is half a unit of the last decimal written in the copy."
        )
    if key == "doc_count_mismatch":
        return (
            "An exact count in CLAUDE.md does not match the region files or status counts. "
            "Approximate figures (a leading ~ or a trailing +) are not checked."
        )
    if key == "region_file_invalid":
        return "A file in data/regions is not a JSON list and was skipped."
    return ""


def render_markdown(report: dict) -> str:
    lines = [
        f"# FORGE Data Audit — {report['asOf']}",
        "",
        "Read-only scan of `data/regions`. Those files were not modified.",
        "",
        "## Summary",
        "",
        f"- As of: {report['asOf']}",
        f"- Zones scanned: {report['zonesScanned']}",
        f"- Region files: {report['regionFiles']}",
        f"- Last-verified threshold: {report['staleDays']} days",
        f"- Issues: {report['totalIssues']}",
        "",
        "| Issue | Count |",
        "| --- | ---: |",
    ]
    for key, label in ISSUE_TYPES:
        lines.append(f"| {label} | {report['counts'].get(key, 0)} |")
    lines.extend(["", "## Changes since the previous audit", ""])
    changes = report["changes"]
    lines.append(changes.get("note") or "")
    lines.append("")
    if changes.get("previousDate"):
        lines.append(f"- New: {len(changes.get('new') or [])}")
        lines.append(f"- Resolved: {len(changes.get('resolved') or [])}")
        lines.append("")
    for bucket, title in (("new", "### New"), ("resolved", "### Resolved")):
        items = changes.get(bucket) or []
        if not items:
            continue
        lines.extend([title, ""])
        for item in items:
            label = TYPE_LABELS.get(item["type"], item["type"])
            lines.append(f"- **{item['zone']}** (`{item['sourceFile']}`) — {label}")
        lines.append("")
    grouped: dict[str, list] = {}
    for item in report["issues"]:
        grouped.setdefault(item["type"], []).append(item)
    for key, label in ISSUE_TYPES:
        items = grouped.get(key) or []
        if not items:
            continue
        lines.extend([f"## {label}", ""])
        blurb = _section_blurb(key, report)
        if blurb:
            lines.extend([blurb, ""])
        for item in items:
            lines.append(
                f"- **{item['zone']}** (`{item['sourceFile']}`) — {format_fields(item['fields'])}"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_report(out_dir: str, as_of: date, report: dict) -> tuple[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    stem = f"audit_{as_of.isoformat()}"
    json_path = os.path.join(out_dir, stem + ".json")
    md_path = os.path.join(out_dir, stem + ".md")
    payload = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    with open(json_path, "w", encoding="utf-8") as handle:
        handle.write(payload)
    with open(md_path, "w", encoding="utf-8") as handle:
        handle.write(render_markdown(report))
    return md_path, json_path


def read_text(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Read-only audit of data/regions zones.")
    parser.add_argument("--regions", default=DEFAULT_REGIONS)
    parser.add_argument("--docs", default=DEFAULT_DOCS)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--as-of", default=None, help="Audit date YYYY-MM-DD. Default: today.")
    parser.add_argument("--stale-days", type=int, default=60)
    args = parser.parse_args(argv)

    if args.as_of:
        try:
            as_of = date.fromisoformat(args.as_of)
        except ValueError:
            print("invalid --as-of, expected YYYY-MM-DD", file=sys.stderr)
            return 1
    else:
        as_of = date.today()
    if args.stale_days < 0:
        print("invalid --stale-days", file=sys.stderr)
        return 1
    if not os.path.isdir(args.regions):
        print(f"regions directory not found: {args.regions}", file=sys.stderr)
        return 1

    zones, file_counts, file_issues = load_regions(args.regions)
    doc_text = ""
    if args.docs and os.path.isfile(args.docs):
        doc_text = read_text(args.docs)
    elif args.docs:
        file_issues.append(make_issue(
            "doc_count_mismatch",
            {"name": "CLAUDE.md", "_source_file": "CLAUDE.md"},
            "docs-missing",
            {
                "label": "CLAUDE.md",
                "documented": None,
                "actual": None,
                "claim": args.docs,
                "note": "documentation file not found",
            },
        ))
    previous = load_previous(args.out, as_of)
    report = build_report(zones, file_counts, file_issues, doc_text, as_of, args.stale_days, previous)
    md_path, _json_path = write_report(args.out, as_of, report)
    print(
        f"[audit] {report['zonesScanned']} zones, {report['totalIssues']} issues → {md_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
