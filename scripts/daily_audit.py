#!/usr/bin/env python3
"""
FORGE Daily Audit — statewide zone consistency check, zero network, zero AI tokens.

Reads data/regions/ and data/gas/, runs 13 checks per zone grouped by region,
diffs against yesterday's report, and writes:
  data/reports/audit_YYYY-MM-DD.md
  data/reports/audit_YYYY-MM-DD.json
  data/reports/audit_latest.md
  data/reports/audit_latest.json

Never edits zone data files. Never commits anything.
Exit 1 if any HIGH findings exist.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import date, timedelta
from typing import Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

REGIONS_DIR = os.path.join(ROOT, "data", "regions")
GAS_DIR = os.path.join(ROOT, "data", "gas")
REPORTS_DIR = os.path.join(ROOT, "data", "reports")
CLAUDE_MD = os.path.join(ROOT, "CLAUDE.md")

TODAY = date.today()
TODAY_STR = TODAY.isoformat()
STALE_DAYS = 60

# ── Region assignment ──────────────────────────────────────────────────────────

REGION_MAP: dict[str, str] = {
    "cleveland_cuyahoga":          "NE Ohio / Cleveland / NOPEC",
    "nopec_cuyahoga_suburbs":      "NE Ohio / Cleveland / NOPEC",
    "nopec_lorain_summit_portage": "NE Ohio / Cleveland / NOPEC",
    "lake_geauga_nopec":           "NE Ohio / Cleveland / NOPEC",
    "ne_ohio_firstenergy":         "NE Ohio / Cleveland / NOPEC",
    "akron_summit_medina":         "Akron / Canton",
    "youngstown_warren":           "Youngstown / Warren",
    "columbus_aep":                "Columbus / Central Ohio",
    "sopec_columbus_suburbs":      "Columbus / Central Ohio",
    "cincinnati_duke":             "Cincinnati / SW Ohio",
    "cincinnati_duke_suburbs":     "Cincinnati / SW Ohio",
    "dayton_sw_ohio":              "Dayton / Miami Valley",
    "dayton_aes_suburbs":          "Dayton / Miami Valley",
    "toledo_lucas_noac":           "Greater Toledo",
    "nw_central_ohio":             "NW & Central Ohio",
    "eastern_ohio_aep":            "Eastern Ohio",
    "ohio_municipal_utilities":    "Municipal Utilities",
    "ohio_electric_cooperatives":  "Electric Cooperatives",
    "remaining_ohio_markets":      "Other Ohio Markets",
    "ne_ohio_gas":                 "NE Ohio / Cleveland / NOPEC",
    "cincinnati_gas":              "Cincinnati / SW Ohio",
    "toledo_gas":                  "Greater Toledo",
}

REGION_ORDER = [
    "NE Ohio / Cleveland / NOPEC",
    "Ashtabula County",
    "Akron / Canton",
    "Youngstown / Warren",
    "Columbus / Central Ohio",
    "Dayton / Miami Valley",
    "Cincinnati / SW Ohio",
    "Greater Toledo",
    "NW & Central Ohio",
    "Eastern Ohio",
    "Municipal Utilities",
    "Electric Cooperatives",
    "Other Ohio Markets",
    "Gas",
    "Documentation",
]

IOU_NAMES = [
    "Ohio Edison", "Illuminating Company", "CEI", "Toledo Edison",
    "AEP Ohio", "AES Ohio", "Dayton P&L", "Duke Energy Ohio",
]
MUNI_WORDS = ["municipal utility", "village electric", "city electric", "muni util"]
COOP_WORDS = ["cooperative", "co-op", "rural electric"]

ACTIVE_STATUSES = frozenset({"pain_coming", "pain_hit", "transition", "pricing_updated"})
EXEMPT_STATUSES = frozenset({"municipal_utility", "electric_cooperative"})

RATE_RE = re.compile(r"(\d+\.\d+)\s*[¢c](?:/kWh)?", re.IGNORECASE)
PCT_RE = re.compile(r"[+\-](\d+\.?\d*)\s*%")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _assign_region(zone: dict) -> str:
    region_field = (zone.get("region") or "").lower()
    if "ashtabula" in region_field:
        return "Ashtabula County"
    commodity = zone.get("commodity", "electric")
    src = zone.get("_source_file", "")
    if commodity == "gas" and src not in REGION_MAP:
        return "Gas"
    return REGION_MAP.get(src, "Other Ohio Markets")


def _finding(zone: dict, check: str, severity: str, detail: str,
             current_value: str = "") -> dict:
    return {
        "zone": zone.get("name", "?"),
        "region": _assign_region(zone),
        "source_file": zone.get("_source_file", "?"),
        "commodity": zone.get("commodity", "electric"),
        "check": check,
        "severity": severity,
        "detail": detail,
        "current_value": current_value,
        "flagged_at": TODAY_STR,
    }


def _finding_id(f: dict) -> str:
    return f"{f.get('source_file','?')}::{f.get('zone','?')}::{f.get('check','?')}"


# ── Individual checks ──────────────────────────────────────────────────────────

def _check_zone(zone: dict) -> list[dict]:
    findings: list[dict] = []
    agg = zone.get("aggregationStatus", "")
    status = zone.get("status", "")
    cr = zone.get("currentRate")
    pr = zone.get("previousRate")
    rc = zone.get("rateChange")
    te = zone.get("termEnd")
    ts = zone.get("termStart")
    lv = zone.get("lastVerified")
    supplier = zone.get("supplier")
    notes = (zone.get("notes") or "").lower()
    takeaway = zone.get("takeaway") or ""
    hook = zone.get("hook") or ""

    def flag(check_id: str, severity: str, detail: str, value: str = "") -> None:
        findings.append(_finding(zone, check_id, severity, detail, value))

    # ── 1. EXPIRED_ACTIVE ─────────────────────────────────────────────────────
    if te and status in ACTIVE_STATUSES:
        try:
            te_date = date.fromisoformat(te)
            if te_date < TODAY:
                days = (TODAY - te_date).days
                flag("EXPIRED_ACTIVE", "HIGH",
                     f"termEnd={te} passed {days}d ago but status={status!r} — should be rollover", te)
        except ValueError:
            pass

    # ── 2. STALE_RENEWAL ─────────────────────────────────────────────────────
    if status in {"rollover", "rollover_dissolved"} and te:
        try:
            days = (TODAY - date.fromisoformat(te)).days
            if days > 90:
                sev = "HIGH" if days > 365 else "MEDIUM"
                flag("STALE_RENEWAL", sev,
                     f"rollover termEnd={te} expired {days}d ago — any new contract?", te)
        except ValueError:
            pass

    # ── 3. TERM_NO_PROGRAM ───────────────────────────────────────────────────
    if (ts or te) and not supplier and agg not in EXEMPT_STATUSES | {"confirmed_active_aggregation"}:
        flag("TERM_NO_PROGRAM", "MEDIUM",
             f"has term dates but supplier=null and agg={agg!r}",
             f"{ts} → {te}")

    # ── 4. AGG_NO_RATE ───────────────────────────────────────────────────────
    if agg == "confirmed_active_aggregation" and cr is None:
        flag("AGG_NO_RATE", "HIGH",
             "confirmed_active_aggregation but currentRate=null", "null")

    # ── 5. RATE_MISMATCH ─────────────────────────────────────────────────────
    if cr is not None and pr is not None and rc is not None:
        try:
            computed = round((float(cr) - float(pr)) / float(pr) * 100, 1)
            if abs(computed - float(rc)) > 1.0:
                flag("RATE_MISMATCH", "MEDIUM",
                     f"rateChange={rc}% but ({cr}-{pr})/{pr}×100={computed}%",
                     f"stored={rc}% computed={computed}%")
        except (ZeroDivisionError, TypeError, ValueError):
            pass

    # ── 6. RATE_CHANGE_NO_PREV ───────────────────────────────────────────────
    if rc is not None and pr is None:
        flag("RATE_CHANGE_NO_PREV", "MEDIUM",
             f"rateChange={rc}% set but previousRate=null", str(rc))

    # ── 7. RATE_NO_SOURCE ────────────────────────────────────────────────────
    if cr is not None and not zone.get("sourceUrl"):
        if agg == "confirmed_active_aggregation":
            flag("RATE_NO_SOURCE", "LOW",
                 f"confirmed agg with currentRate={cr} but sourceUrl=null", str(cr))

    # ── 8. STALE_60 ──────────────────────────────────────────────────────────
    if lv and agg not in EXEMPT_STATUSES:
        try:
            days_old = (TODAY - date.fromisoformat(lv)).days
            if days_old > STALE_DAYS:
                sev = "HIGH" if days_old > 180 else "MEDIUM" if days_old > 90 else "LOW"
                flag("STALE_60", sev,
                     f"lastVerified={lv} ({days_old}d ago)", lv)
        except ValueError:
            pass

    # ── 9. MUNI_IOU_NOTES ───────────────────────────────────────────────────
    if agg == "municipal_utility":
        iou_hits = [n for n in IOU_NAMES if n.lower() in notes]
        if iou_hits:
            flag("MUNI_IOU_NOTES", "MEDIUM",
                 f"municipal_utility zone but notes reference IOU names: {iou_hits}", str(iou_hits))

    # ── 10. IOU_MUNI_NOTES (reverse) ─────────────────────────────────────────
    if agg not in EXEMPT_STATUSES:
        muni_hits = [w for w in MUNI_WORDS if w in notes]
        if muni_hits and "not" not in notes[:notes.find(muni_hits[0]) + 5]:
            flag("IOU_MUNI_NOTES", "LOW",
                 f"non-muni zone but notes contain muni/coop keywords: {muni_hits}", str(muni_hits))

    # ── 11. COOP_IOU_NOTES ───────────────────────────────────────────────────
    if agg == "electric_cooperative":
        iou_hits = [n for n in IOU_NAMES if n.lower() in notes]
        if iou_hits:
            flag("COOP_IOU_NOTES", "MEDIUM",
                 f"electric_cooperative zone but notes reference IOU names: {iou_hits}", str(iou_hits))

    # ── 12. COPY_RATE_MISMATCH ───────────────────────────────────────────────
    zone_rates = [float(x) for x in [cr, pr] if x is not None]
    for copy_field, copy_text in [("takeaway", takeaway), ("hook", hook)]:
        if not copy_text:
            continue
        for m in RATE_RE.finditer(copy_text):
            v = float(m.group(1))
            if not 5.0 <= v <= 20.0:
                continue
            if zone_rates and not any(abs(v - z) < 0.12 for z in zone_rates):
                flag("COPY_RATE_MISMATCH", "MEDIUM",
                     f"{copy_field} mentions {v}¢ but currentRate={cr}, previousRate={pr}", str(v))
        for m in PCT_RE.finditer(copy_text):
            v = float(m.group(1))
            if not 1.0 <= v <= 50.0:
                continue
            if rc is not None and abs(v - float(rc)) > 1.5:
                flag("COPY_RATE_MISMATCH", "LOW",
                     f"{copy_field} mentions +{v}% but rateChange={rc}%", str(v))

    return findings


def _check_docs(all_zones: list[dict]) -> list[dict]:
    findings: list[dict] = []
    if not os.path.exists(CLAUDE_MD):
        return findings

    with open(CLAUDE_MD) as f:
        content = f.read()

    # Compare zone counts
    electric_count = sum(1 for z in all_zones if z.get("commodity", "electric") == "electric")
    for m in re.finditer(r"(\d+)\s+zones?\s+total", content, re.IGNORECASE):
        claimed = int(m.group(1))
        if claimed != electric_count:
            findings.append({
                "zone": "CLAUDE.md",
                "region": "Documentation",
                "source_file": "CLAUDE.md",
                "commodity": "meta",
                "check": "DOC_COUNT_MISMATCH",
                "severity": "LOW",
                "detail": f"CLAUDE.md claims {claimed} zones but actual={electric_count}",
                "current_value": f"claimed={claimed} actual={electric_count}",
                "flagged_at": TODAY_STR,
            })

    # Compare region file counts
    actual_files = len([f for f in os.listdir(REGIONS_DIR) if f.endswith(".json")])
    for m in re.finditer(r"(\d+)\s+JSON\s+files", content, re.IGNORECASE):
        claimed = int(m.group(1))
        if claimed != actual_files:
            findings.append({
                "zone": "CLAUDE.md",
                "region": "Documentation",
                "source_file": "CLAUDE.md",
                "commodity": "meta",
                "check": "DOC_COUNT_MISMATCH",
                "severity": "LOW",
                "detail": f"CLAUDE.md claims {claimed} JSON files but actual={actual_files}",
                "current_value": f"claimed={claimed} actual={actual_files}",
                "flagged_at": TODAY_STR,
            })

    return findings


# ── Zone loading ───────────────────────────────────────────────────────────────

def _load_zones() -> list[dict]:
    zones: list[dict] = []
    for data_dir, commodity in [(REGIONS_DIR, "electric"), (GAS_DIR, "gas")]:
        if not os.path.exists(data_dir):
            continue
        for fname in sorted(os.listdir(data_dir)):
            if not fname.endswith(".json"):
                continue
            path = os.path.join(data_dir, fname)
            try:
                with open(path) as f:
                    file_zones = json.load(f)
                for z in file_zones:
                    z["_source_file"] = fname[:-5]
                    z.setdefault("commodity", commodity)
                zones.extend(file_zones)
            except json.JSONDecodeError as e:
                print(f"[audit] JSON error in {fname}: {e}", file=sys.stderr)
    return zones


# ── Previous report loading ────────────────────────────────────────────────────

def _load_prev_findings() -> list[dict]:
    yesterday = (TODAY - timedelta(days=1)).isoformat()
    for candidate in [
        os.path.join(REPORTS_DIR, f"audit_{yesterday}.json"),
        os.path.join(REPORTS_DIR, "audit_latest.json"),
    ]:
        if os.path.exists(candidate):
            try:
                with open(candidate) as f:
                    data = json.load(f)
                # Ignore if it's from today (we'd diff against ourselves)
                if data.get("date") == TODAY_STR:
                    continue
                return data.get("findings", [])
            except Exception:
                pass
    return []


# ── Report generation ──────────────────────────────────────────────────────────

def _generate_report(
    all_findings: list[dict],
    prev_findings: list[dict],
    zones_count: int,
    elapsed: float,
) -> dict:
    today_ids = {_finding_id(f) for f in all_findings}
    prev_ids = {_finding_id(f) for f in prev_findings}

    new_findings = [f for f in all_findings if _finding_id(f) not in prev_ids]
    resolved_findings = [f for f in prev_findings if _finding_id(f) not in today_ids]

    by_region: dict[str, list] = {}
    for f in all_findings:
        by_region.setdefault(f.get("region", "Other"), []).append(f)

    high = sum(1 for f in all_findings if f.get("severity") == "HIGH")
    med = sum(1 for f in all_findings if f.get("severity") == "MEDIUM")
    low = sum(1 for f in all_findings if f.get("severity") == "LOW")

    # Build ordered region dict
    ordered_regions: dict[str, list] = {}
    for r in REGION_ORDER:
        if r in by_region:
            ordered_regions[r] = by_region[r]
    for r in by_region:
        if r not in ordered_regions:
            ordered_regions[r] = by_region[r]

    return {
        "date": TODAY_STR,
        "zones_checked": zones_count,
        "elapsed_seconds": round(elapsed, 2),
        "totals": {"high": high, "medium": med, "low": low, "total": len(all_findings)},
        "new": new_findings,
        "resolved": resolved_findings,
        "by_region": ordered_regions,
        "findings": all_findings,
    }


# ── Markdown rendering ─────────────────────────────────────────────────────────

def _render_md(report: dict) -> str:
    lines: list[str] = []
    t = report["totals"]
    prev_date = (TODAY - timedelta(days=1)).isoformat()

    lines += [
        f"# FORGE Daily Audit — {report['date']}",
        "",
        f"**{t['total']} findings** | HIGH: {t['high']}  MEDIUM: {t['medium']}  LOW: {t['low']}",
        f"Zones checked: {report['zones_checked']} | Elapsed: {report['elapsed_seconds']}s",
        "",
    ]

    # ── New / Resolved delta ──
    new_f = report.get("new", [])
    res_f = report.get("resolved", [])

    if new_f:
        lines += [f"## 🆕 New since {prev_date} ({len(new_f)})", ""]
        for f in sorted(new_f, key=lambda x: x.get("severity", "")):
            sev = f.get("severity", "?")
            lines.append(f"- `{sev}` **{f['zone']}** ({f.get('region','?')}) — "
                         f"`{f['check']}`: {f['detail']}")
        lines.append("")
    else:
        lines += [f"## ✅ No new findings since {prev_date}", ""]

    if res_f:
        lines += [f"## ✅ Resolved since {prev_date} ({len(res_f)})", ""]
        for f in res_f:
            lines.append(f"- **{f['zone']}** `{f['check']}` — was: {f['detail']}")
        lines.append("")

    if not new_f and not res_f:
        lines += ["*(No previous report to diff against.)*", ""]

    # ── Per-region sections ──
    for region, findings in report.get("by_region", {}).items():
        if not findings:
            continue
        high_c = sum(1 for f in findings if f.get("severity") == "HIGH")
        med_c = sum(1 for f in findings if f.get("severity") == "MEDIUM")
        low_c = sum(1 for f in findings if f.get("severity") == "LOW")
        badge = f"HIGH:{high_c} MED:{med_c} LOW:{low_c}"
        lines += [f"## {region} ({badge})", ""]

        by_sev = {"HIGH": [], "MEDIUM": [], "LOW": []}
        for f in findings:
            by_sev.setdefault(f.get("severity", "LOW"), []).append(f)

        for sev in ("HIGH", "MEDIUM", "LOW"):
            for f in by_sev[sev]:
                commodity = f" [gas]" if f.get("commodity") == "gas" else ""
                lines.append(
                    f"- `{sev}` **{f['zone']}**{commodity} `{f['check']}`  "
                )
                lines.append(f"  {f['detail']}")
                if f.get("current_value"):
                    lines.append(f"  *current:* `{f['current_value']}`")
        lines.append("")

    lines.append("---")
    lines.append(f"*Generated by scripts/daily_audit.py — {TODAY_STR}*")

    return "\n".join(lines) + "\n"


# ── Output writers ─────────────────────────────────────────────────────────────

def _write_outputs(report: dict) -> tuple[str, str]:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    date_str = report["date"]

    md_path = os.path.join(REPORTS_DIR, f"audit_{date_str}.md")
    json_path = os.path.join(REPORTS_DIR, f"audit_{date_str}.json")
    latest_md = os.path.join(REPORTS_DIR, "audit_latest.md")
    latest_json = os.path.join(REPORTS_DIR, "audit_latest.json")

    md_content = _render_md(report)
    with open(md_path, "w") as f:
        f.write(md_content)
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)

    with open(latest_md, "w") as f:
        f.write(md_content)
    with open(latest_json, "w") as f:
        json.dump(report, f, indent=2)

    return md_path, json_path


# ── Public entry point ─────────────────────────────────────────────────────────

def run_audit(verbose: bool = False) -> dict:
    t0 = time.time()
    zones = _load_zones()

    all_findings: list[dict] = []
    for zone in zones:
        all_findings.extend(_check_zone(zone))
    all_findings.extend(_check_docs(zones))

    prev_findings = _load_prev_findings()
    report = _generate_report(all_findings, prev_findings, len(zones), time.time() - t0)
    md_path, json_path = _write_outputs(report)

    t = report["totals"]
    print(
        f"[audit] {report['zones_checked']} zones | {t['total']} findings "
        f"(HIGH={t['high']} MED={t['medium']} LOW={t['low']}) | {report['elapsed_seconds']}s"
    )
    print(f"[audit] New: {len(report['new'])}  Resolved: {len(report['resolved'])}")
    print(f"[audit] {md_path}")
    if verbose:
        by_check: dict[str, int] = {}
        for f in all_findings:
            by_check[f["check"]] = by_check.get(f["check"], 0) + 1
        for check, cnt in sorted(by_check.items(), key=lambda x: -x[1]):
            print(f"  {check}: {cnt}")

    return report


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="FORGE daily data audit")
    p.add_argument("--verbose", "-v", action="store_true")
    args = p.parse_args()
    report = run_audit(verbose=args.verbose)
    sys.exit(1 if report["totals"]["high"] > 0 else 0)
