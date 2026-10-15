"""Append-only history for the life of the project.

Zone edits, rates, sources, research results, investigation-queue changes,
and refresh/monitor reports are appended. Older lines and report files are
never deleted or overwritten. A later event marks an earlier one superseded
by id; readers set ``superseded_at`` from that later timestamp. Pruning and
cleanup must not touch this directory.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_HISTORY_DIR = os.path.join(ROOT, "data", "history")
JOURNAL_NAME = "journal.jsonl"

# Fields that belong to the loader, not to a stored zone edit.
DERIVED_ZONE_KEYS = {
    "_source_file",
    "_history_key",
    "research",
    "original",
    "card",
    "history",
    "superseded",
    "superseded_at",
}


def history_dir() -> str:
    override = os.environ.get("FORGE_HISTORY_DIR")
    return override if override else DEFAULT_HISTORY_DIR


def journal_path() -> str:
    return os.path.join(history_dir(), JOURNAL_NAME)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def guard_against_prune(path: str) -> None:
    """Refuse to delete or truncate stored history.

    Cleanup may call this before removing a path. History stays for the
    life of the project.
    """
    target = os.path.abspath(path)
    root = os.path.abspath(history_dir())
    if target == root or target.startswith(root + os.sep):
        raise RuntimeError(
            "Refusing to prune history. "
            "History is kept for the life of the project and is append-only."
        )


def append_event(kind: str, body: dict) -> dict:
    """Append one journal line. Never rewrites earlier lines."""
    event = {
        "id": uuid.uuid4().hex,
        "kind": kind,
        "recorded_at": _now(),
    }
    event.update(body)
    path = journal_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    line = json.dumps(event, ensure_ascii=False, default=str) + "\n"
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(line)
    return event


def load_events(path: str | None = None) -> list[dict]:
    """Read the journal. Superseded flags are applied in memory only."""
    path = path or journal_path()
    if not os.path.exists(path):
        return []
    events = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            events.append(json.loads(line))
    by_id = {event["id"]: event for event in events if event.get("id")}
    for event in events:
        prior_id = event.get("supersedes")
        if prior_id and prior_id in by_id:
            prior = by_id[prior_id]
            prior["superseded"] = True
            prior["superseded_at"] = event.get("recorded_at") or ""
    return events


def latest_active(kind: str, match: dict | None = None, path: str | None = None) -> dict | None:
    found = None
    for event in load_events(path):
        if event.get("kind") != kind or event.get("superseded"):
            continue
        if match and any(event.get(key) != value for key, value in match.items()):
            continue
        found = event
    return found


def _append_version(kind: str, match: dict, body: dict) -> dict:
    prior = latest_active(kind, match)
    if prior:
        body = {**body, "supersedes": prior["id"]}
    return append_event(kind, body)


def write_new_file(path: str, content: str) -> str:
    """Create a new file. If the name exists, pick another. Never truncate."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    stem, ext = os.path.splitext(path)
    candidate = path
    number = 1
    while True:
        try:
            fd = os.open(candidate, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            candidate = f"{stem}-{number}{ext}"
            number += 1
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        return candidate


def store_report(kind: str, report: dict, mirror_path: str | None = None) -> dict:
    """Save a refresh or monitor report as a new history file.

    A mirror path, when given, is also created only if that name is free.
    An existing report is left as it was.
    """
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    path = os.path.join(history_dir(), "reports", f"{kind}_{stamp}.json")
    payload = json.dumps(report, indent=2) + "\n"
    written = write_new_file(path, payload)
    mirror = write_new_file(mirror_path, payload) if mirror_path else None
    event = append_event(kind, {
        "path": written,
        "mirror": mirror,
        "run_timestamp": report.get("run_timestamp") or report.get("run_date") or "",
    })
    return {"path": written, "mirror": mirror, "id": event["id"]}


def record_zone_change(region_file: str, zone_key: str, action: str, zone: dict | None) -> dict:
    """Append a zone edit. The region JSON file is not rewritten."""
    return _append_version("zone", {"region_file": region_file, "zone_key": zone_key}, {
        "action": action,
        "region_file": region_file,
        "zone_key": zone_key,
        "zone": zone or {},
    })


def record_observation(observation: dict) -> None:
    """Append a research result and, when present, its rate and source."""
    zone = observation.get("zone") or ""
    region = observation.get("region") or ""
    match = {"zone": zone, "region": region}
    _append_version("research_result", match, {
        **match,
        "rate": observation.get("rate") or "",
        "source_url": observation.get("source_url") or "",
        "supplier": observation.get("supplier") or "",
        "accessed_at": observation.get("accessed_at") or "",
        "observation": observation,
    })
    if str(observation.get("rate") or "").strip():
        _append_version("rate", match, {
            **match,
            "rate": observation.get("rate"),
            "source_url": observation.get("source_url") or "",
            "accessed_at": observation.get("accessed_at") or "",
        })
    if str(observation.get("source_url") or "").strip():
        _append_version("source", match, {
            **match,
            "source_url": observation.get("source_url") or "",
            "accessed_at": observation.get("accessed_at") or "",
        })


def record_queue_item(item: dict) -> None:
    """Append an investigation-queue change. The prior row stays stored."""
    match = {"zone": item.get("zone") or "", "region": item.get("region") or ""}
    _append_version("investigation_queue", match, {
        **match,
        "change": item.get("change") or "",
        "item": item,
    })


def _public_snapshot(zone: dict) -> dict:
    return {key: value for key, value in zone.items() if key not in DERIVED_ZONE_KEYS}


def apply_zone_history(zones: list[dict]) -> list[dict]:
    """Replay zone events onto loaded zones without dropping prior values.

    Region files stay untouched. Superseded edits remain on ``zone['history']``
    and in the journal.
    """
    events = [event for event in load_events() if event.get("kind") == "zone"]
    if not events:
        return zones
    index = {
        (zone.get("_source_file"), zone.get("_history_key") or zone.get("name")): zone
        for zone in zones
    }
    for event in events:
        key = (event.get("region_file"), event.get("zone_key"))
        zone = index.get(key)
        created = False
        if zone is None and event.get("action") == "add":
            zone = {
                "_source_file": event.get("region_file"),
                "_history_key": event.get("zone_key"),
                "name": event.get("zone_key") or "",
            }
            zones.append(zone)
            index[key] = zone
            created = True
        if zone is None:
            continue
        if not created:
            zone.setdefault("history", []).append({
                "superseded": True,
                "superseded_at": event.get("recorded_at") or "",
                "values": _public_snapshot(zone),
            })
        if event.get("action") == "supersede":
            zone["superseded"] = True
            zone["superseded_at"] = event.get("recorded_at") or ""
            continue
        for key_name, value in (event.get("zone") or {}).items():
            if key_name in DERIVED_ZONE_KEYS:
                continue
            zone[key_name] = value
        zone["superseded"] = False
        zone.pop("superseded_at", None)
    return zones
