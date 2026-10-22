"""
FORGE Data Audit — local consistency checks, zero network, zero AI tokens.
Runs against data/regions/ and data/gas/ and writes findings to:
  - data/reports/audit_YYYY-MM-DD.md
  - data/research/investigation_queue.csv (appends)

Never writes to data/regions/*.json.
"""

from __future__ import annotations

import csv
import json
import os
import sys
from datetime import date, datetime
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

REGIONS_DIR = os.path.join(ROOT, "data", "regions")
GAS_DIR = os.path.join(ROOT, "data", "gas")
REPORTS_DIR = os.path.join(ROOT, "data", "reports")
QUEUE_PATH = os.path.join(ROOT, "data", "research", "investigation_queue.csv")

TODAY = date.today()
TODAY_STR = TODAY.isoformat()

# Known program rates — update these when rates change
KNOWN_RATES = {
    "NOPEC": 9.999,
    "Medina County": 9.5,
}

ACTIVE_STATUSES = {"confirmed_active_aggregation"}
BLACKLIST_STATUSES = {"municipal_utility", "electric_cooperative"}

CHECKS = []


def check(fn):
    CHECKS.append(fn)
    return fn


# ── Individual checks ─────────────────────────────────────────────────────────

@check
def expired_wrong_status(zones):
    findings = []
    skip = {"rollover", "rollover_dissolved", "pain_hit", "pricing_updated",
             "stable", "verify", "no_aggregation_verified"}
    for z in zones:
        agg = z.get("aggregationStatus", "")
        if agg in BLACKLIST_STATUSES:
            continue
        te = z.get("termEnd")
        status = z.get("status", "")
        if te and status not in skip:
            try:
                if date.fromisoformat(te) < TODAY:
                    findings.append(_finding(z, "EXPIRED_WRONG_STATUS",
                        f"termEnd={te} passed but status={status} — should be rollover",
                        priority="HIGH"))
            except ValueError:
                pass
    return findings


@check
def nopec_rate_mismatch(zones):
    """Flag NOPEC zones with a rate that doesn't match any known NOPEC cycle rate."""
    findings = []
    # Known NOPEC rate cycles — add new rows when NOPEC announces a rate change
    NOPEC_VALID_RATES = {8.999, 9.999, 10.399}
    skip_statuses = {"rollover", "rollover_dissolved", "verify", "stable"}
    for z in zones:
        if (z.get("supplier") or "").upper() != "NOPEC":
            continue
        if z.get("status") in skip_statuses:
            continue
        rate = z.get("currentRate")
        if rate is None:
            continue
        rate = float(rate)
        if not any(abs(rate - v) < 0.05 for v in NOPEC_VALID_RATES):
            findings.append(_finding(z, "NOPEC_RATE_MISMATCH",
                f"supplier=NOPEC but currentRate={rate} doesn't match any known NOPEC rate cycle",
                priority="MEDIUM"))
    return findings


@check
def medina_county_program_confusion(zones):
    findings = []
    for z in zones:
        supplier = (z.get("supplier") or "").upper()
        notes = (z.get("notes") or "").lower()
        if supplier == "NOPEC" and "medina county" in notes and "aggregation program" in notes:
            if "do not confuse" not in notes and "not medina county" not in notes:
                findings.append(_finding(z, "PROGRAM_CONFUSION",
                    "supplier=NOPEC but notes reference Medina County aggregation program — verify which program applies",
                    priority="HIGH"))
    return findings


@check
def missing_rate_change(zones):
    findings = []
    for z in zones:
        if z.get("aggregationStatus") in BLACKLIST_STATUSES:
            continue
        cr = z.get("currentRate")
        pr = z.get("previousRate")
        rc = z.get("rateChange")
        if cr is not None and pr is not None and rc is None:
            expected = round((float(cr) - float(pr)) / float(pr) * 100, 1)
            findings.append(_finding(z, "MISSING_RATE_CHANGE",
                f"currentRate={cr} previousRate={pr} but rateChange=null — should be {expected}%",
                priority="LOW"))
    return findings


@check
def blank_takeaway_or_hook(zones):
    findings = []
    for z in zones:
        if z.get("aggregationStatus") in BLACKLIST_STATUSES:
            continue
        status = z.get("status", "")
        if status in ("stable", "verify"):
            continue
        if not z.get("takeaway") or not z.get("hook"):
            findings.append(_finding(z, "MISSING_SALES_COPY",
                f"status={status} active zone has blank takeaway or hook",
                priority="MEDIUM"))
    return findings


@check
def supplier_agg_status_mismatch(zones):
    findings = []
    for z in zones:
        supplier = z.get("supplier")
        agg = z.get("aggregationStatus", "")
        if supplier and agg == "no_aggregation_verified":
            findings.append(_finding(z, "SUPPLIER_AGG_MISMATCH",
                f"supplier={supplier} set but aggregationStatus=no_aggregation_verified",
                priority="HIGH"))
    return findings


@check
def rate_out_of_range(zones):
    findings = []
    for z in zones:
        if z.get("aggregationStatus") in BLACKLIST_STATUSES:
            continue
        commodity = z.get("commodity", "electric")
        rate = z.get("currentRate")
        if rate is None:
            continue
        rate = float(rate)
        if commodity == "electric" and not (5.0 <= rate <= 20.0):
            findings.append(_finding(z, "RATE_OUT_OF_RANGE",
                f"currentRate={rate}¢/kWh is outside expected electric range 5-20¢",
                priority="MEDIUM"))
        if commodity == "gas" and not (0.3 <= rate <= 3.0):
            findings.append(_finding(z, "RATE_OUT_OF_RANGE",
                f"currentRate={rate}$/ccf is outside expected gas range 0.30-3.00",
                priority="MEDIUM"))
    return findings


@check
def rollover_stale_over_6_months(zones):
    findings = []
    from datetime import timedelta
    cutoff = TODAY - timedelta(days=180)
    for z in zones:
        if z.get("status") not in ("rollover", "rollover_dissolved"):
            continue
        te = z.get("termEnd")
        if te:
            try:
                if date.fromisoformat(te) < cutoff:
                    lv = z.get("lastVerified", "")
                    findings.append(_finding(z, "ROLLOVER_STALE",
                        f"rollover zone expired {te} (>180 days ago) — has anything happened? lastVerified={lv}",
                        priority="MEDIUM"))
            except ValueError:
                pass
    return findings


@check
def duplicate_zone_names(zones):
    findings = []
    seen: dict[str, list] = {}
    for z in zones:
        key = (z.get("name", "").lower(), z.get("commodity", "electric"))
        seen.setdefault(key, []).append(z.get("_source_file", "?"))
    for (name, commodity), files in seen.items():
        if len(files) > 1:
            findings.append({
                "zone": name,
                "source_file": ", ".join(files),
                "commodity": commodity,
                "check": "DUPLICATE_ZONE",
                "detail": f"Zone appears in {len(files)} files: {', '.join(files)}",
                "priority": "HIGH",
                "flagged_at": TODAY_STR,
            })
    return findings


@check
def high_confidence_no_source(zones):
    findings = []
    for z in zones:
        if z.get("aggregationStatus") in BLACKLIST_STATUSES:
            continue
        if z.get("confidence") == "high" and not z.get("sourceUrl"):
            status = z.get("status", "")
            if status in ("pain_hit", "rollover", "pricing_updated"):
                findings.append(_finding(z, "HIGH_CONF_NO_SOURCE",
                    f"confidence=high status={status} but sourceUrl=null — where is this from?",
                    priority="LOW"))
    return findings


@check
def electric_zone_no_gas_counterpart(zones):
    """Flag rollover electric zones that have no gas zone entry — missed opportunity."""
    findings = []
    electric = {z["name"].lower() for z in zones
                if z.get("commodity", "electric") == "electric"
                and z.get("status") in ("rollover", "pain_hit")
                and z.get("aggregationStatus") not in BLACKLIST_STATUSES}
    gas_names = {z["name"].lower() for z in zones if z.get("commodity") == "gas"}
    for name in sorted(electric - gas_names):
        findings.append({
            "zone": name,
            "source_file": "—",
            "commodity": "electric",
            "check": "NO_GAS_ZONE",
            "detail": f"Rollover/pain_hit electric zone '{name}' has no gas counterpart — gas opportunity untracked",
            "priority": "LOW",
            "flagged_at": TODAY_STR,
        })
    return findings


# ── Helpers ───────────────────────────────────────────────────────────────────

def _finding(zone: dict, check: str, detail: str, priority: str = "MEDIUM") -> dict:
    return {
        "zone": zone.get("name", "?"),
        "source_file": zone.get("_source_file", "?"),
        "commodity": zone.get("commodity", "electric"),
        "check": check,
        "detail": detail,
        "priority": priority,
        "flagged_at": TODAY_STR,
    }


def _load_all_zones() -> list:
    zones = []
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


def _write_queue(findings: list) -> int:
    if not findings:
        return 0
    os.makedirs(os.path.dirname(QUEUE_PATH), exist_ok=True)
    write_header = not os.path.exists(QUEUE_PATH)
    added = 0
    with open(QUEUE_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "flagged_at", "priority", "check", "zone", "source_file", "commodity", "detail"
        ])
        if write_header:
            writer.writeheader()
        for item in findings:
            writer.writerow({k: item.get(k, "") for k in writer.fieldnames})
            added += 1
    return added


def _write_report(findings: list, elapsed: float) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, f"audit_{TODAY_STR}.md")

    by_priority = {"HIGH": [], "MEDIUM": [], "LOW": []}
    for f in findings:
        by_priority.setdefault(f.get("priority", "LOW"), []).append(f)

    lines = [
        f"# FORGE Data Audit — {TODAY_STR}",
        f"",
        f"**{len(findings)} findings** across {len(CHECKS)} checks | {elapsed:.1f}s",
        f"",
    ]

    for priority in ("HIGH", "MEDIUM", "LOW"):
        items = by_priority[priority]
        if not items:
            continue
        lines.append(f"## {priority} ({len(items)})")
        lines.append("")
        for item in items:
            commodity = f" [{item['commodity']}]" if item.get("commodity") != "electric" else ""
            lines.append(f"- **{item['zone']}**{commodity} `{item['check']}`  ")
            lines.append(f"  {item['detail']}")
            lines.append("")

    if not findings:
        lines.append("## All checks passed — no findings.")
        lines.append("")

    lines.append(f"*Queued to investigation_queue.csv*")

    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


def run_audit(verbose: bool = False) -> dict:
    import time
    t0 = time.time()

    zones = _load_all_zones()
    all_findings = []

    for check_fn in CHECKS:
        try:
            results = check_fn(zones)
            all_findings.extend(results)
            if verbose and results:
                print(f"  [{check_fn.__name__}] {len(results)} findings")
        except Exception as e:
            print(f"[audit] check {check_fn.__name__} failed: {e}", file=sys.stderr)

    elapsed = time.time() - t0
    queued = _write_queue(all_findings)
    report_path = _write_report(all_findings, elapsed)

    high = sum(1 for f in all_findings if f.get("priority") == "HIGH")
    med = sum(1 for f in all_findings if f.get("priority") == "MEDIUM")
    low = sum(1 for f in all_findings if f.get("priority") == "LOW")

    print(f"[audit] {len(zones)} zones | {len(all_findings)} findings "
          f"(HIGH={high} MED={med} LOW={low}) | {elapsed:.1f}s")
    print(f"[audit] report: {report_path}")
    print(f"[audit] queued: {queued} items → investigation_queue.csv")

    return {
        "zones_checked": len(zones),
        "findings": len(all_findings),
        "high": high,
        "medium": med,
        "low": low,
        "report": report_path,
        "queued": queued,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="FORGE data consistency audit")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    result = run_audit(verbose=args.verbose)
    sys.exit(1 if result["high"] > 0 else 0)
