"""Report-only refresh monitor.

Compare stored research rates against a snapshot file or a live fetch of each
zone's stored source URL. Disagreements are appended to the investigation
monitor queue. Region JSON is never written. Reports and observations are
appended to history; a later run does not replace an earlier report.

Usage:
    python run_refresh.py
    python run_refresh.py --observations observations.json
    python run_refresh.py --fetch --limit 20
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

import history_store  # noqa: E402
from zone_intel import (  # noqa: E402
    append_monitor_items,
    compare_observation,
    load_queue,
)


def _load_zones():
    # Import late so tests can call compare/append without starting Flask.
    from app import _load_zones as load
    return load()


def _report(zones, observations, fetch_notes) -> dict:
    items = []
    for obs in observations:
        if obs.get("fetch_error") or obs.get("skipped"):
            continue
        name = (obs.get("zone") or "").strip().lower()
        region = (obs.get("region") or "").strip()
        if region.endswith(".json"):
            region = region[:-5]
        matches = [
            zone for zone in zones
            if zone.get("name", "").lower() == name
            and (not region or zone.get("_source_file") == region)
        ]
        if len(matches) != 1:
            fetch_notes.append({
                "zone": obs.get("zone"),
                "region": region,
                "note": f"{len(matches)} stored zones matched; no queue item written",
            })
            continue
        item = compare_observation(matches[0], obs)
        if item:
            items.append(item)
    added = append_monitor_items(items) if items else []
    for observation in observations:
        history_store.record_observation(observation)
    for item in added:
        history_store.record_queue_item(item)
    queue = load_queue()
    return {
        "run_date": date.today().isoformat(),
        "run_timestamp": datetime.now().isoformat(timespec="seconds"),
        "mode": "report-only",
        "zones_loaded": len(zones),
        "baseline_queue": len(queue),
        "observations": len(observations),
        "diffs_found": len(items),
        "queue_items_added": len(added),
        "added": added,
        "notes": fetch_notes,
        "zone_files_written": 0,
    }


def _fetch(zones, limit: int | None) -> tuple[list, list]:
    import requests

    observations = []
    notes = []
    checked = 0
    for zone in zones:
        research = zone.get("research") or {}
        current = research.get("current") or {}
        url = current.get("source") or ""
        rate = current.get("rate_raw") or ""
        if not current.get("sourced") or not rate:
            continue
        if limit is not None and checked >= limit:
            break
        checked += 1
        try:
            response = requests.get(
                url,
                timeout=20,
                headers={"User-Agent": "FORGE-refresh-monitor/1.0 (report-only)"},
            )
            response.raise_for_status()
        except Exception as exc:
            notes.append({"zone": zone.get("name"), "source_url": url, "fetch_error": str(exc)})
            continue
        present = rate in response.text
        observations.append({
            "zone": zone.get("name"),
            "region": zone.get("_source_file"),
            "source_url": url,
            "accessed_at": date.today().isoformat(),
            "rate_missing": not present,
            "http_status": response.status_code,
        })
    return observations, notes


def main(argv: list[str] | None = None) -> dict:
    parser = argparse.ArgumentParser(description="Report-only source refresh. Appends history and does not overwrite zone data.")
    parser.add_argument("--observations", help="JSON list of {zone, region, rate, supplier, source_url, accessed_at}")
    parser.add_argument("--fetch", action="store_true", help="Fetch stored source URLs and flag missing rates")
    parser.add_argument("--limit", type=int, default=None, help="Max sourced pages to fetch")
    parser.add_argument("--report", default=None, help="Also copy the JSON report here. An existing file is kept.")
    parser.add_argument("--puco", action="store_true", help="Fetch a new PUCO aggregation snapshot into the local cache")
    args = parser.parse_args(argv)

    zones = _load_zones()
    observations = []
    notes = []
    if args.observations:
        with open(args.observations) as handle:
            observations.extend(json.load(handle))
    if args.fetch:
        fetched, fetch_notes = _fetch(zones, args.limit)
        observations.extend(fetched)
        notes.extend(fetch_notes)
    report = _report(zones, observations, notes)
    if args.puco:
        import puco_layer
        snapshot = puco_layer.fetch_snapshot()
        report["puco_snapshot"] = {
            "filename": snapshot.get("filename") or "",
            "feature_count": snapshot.get("feature_count"),
            "fetched_at": snapshot.get("fetched_at") or "",
        }
        report["zone_files_written"] = 0

    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    mirror = args.report or os.path.join("output", f"refresh_report_{stamp}.json")
    stored = history_store.store_report("refresh_report", report, mirror)
    print(
        f"[refresh] report-only. zones={report['zones_loaded']} "
        f"observations={report['observations']} diffs={report['diffs_found']} "
        f"queued={report['queue_items_added']} zone_files_written=0"
    )
    print(f"[refresh] report: {stored['path']}")
    if stored["mirror"]:
        print(f"[refresh] copy: {stored['mirror']}")
    return report


if __name__ == "__main__":
    main()
