"""Delete proven-incorrect archives from the dataset, ledger, and journal.

Genuine prior and historical rates stay. The only record of a deletion
remains the one-line removal note.
"""

from __future__ import annotations

import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET = os.path.join(ROOT, "data", "research", "forge_corrected_dataset.csv")
LEDGER = os.path.join(ROOT, "data", "research", "rate_ledger.csv")
NOTES = os.path.join(ROOT, "data", "history", "removal_notes.jsonl")
JOURNAL = os.path.join(ROOT, "data", "history", "journal.jsonl")
OVERLAY = os.path.join(ROOT, "data", "research", "merged_overlay.json")

MUNICIPAL_MARKERS = (
    "municipal_blacklist",
    "Municipal (exempt",
    "Municipal Electric",
    "exempt from retail choice",
)
OWNERSHIP_MARKERS = (
    "owned electric utility",
    "Exempt from Ohio retail electric choice",
)
KNOWN_UTILITIES = (
    "The Illuminating Company",
    "Toledo Edison",
    "Ohio Edison",
    "AEP Ohio",
    "AES Ohio",
    "Duke Energy",
)


def load_notes() -> dict[str, set[str]]:
    fields: dict[str, set[str]] = {}
    with open(NOTES, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            note = json.loads(line)
            fields.setdefault(note["zone"], set()).add(note["field"])
    return fields


def _clear(row: dict, column: str, changes: list[str], zone: str) -> None:
    if (row.get(column) or "").strip():
        changes.append(f"{zone} {column}")
        row[column] = ""


def _notes_name_only_the_wrong_utility(text: str, norm_utility: str) -> bool:
    """True when the note names a utility the correction replaced and not the one kept."""
    mentioned = [name for name in KNOWN_UTILITIES if name in text]
    if not mentioned:
        return False
    if norm_utility and norm_utility in text:
        return False
    return not any(name in norm_utility for name in mentioned)


def purge_dataset(notes: dict[str, set[str]]) -> list[str]:
    with open(DATASET, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    changes: list[str] = []
    for row in rows:
        zone = row.get("orig_name") or ""
        fields = notes.get(zone) or set()
        if not fields:
            continue
        program = row.get("STATUS_program") or ""
        still_municipal = program.startswith("not_eligible")
        norm_utility = (row.get("norm_utility") or "").strip()
        norm_supplier = (row.get("norm_supplier") or "").strip()
        if "utility" in fields:
            original_utility = (row.get("orig_utility") or "").strip()
            if original_utility and original_utility != norm_utility:
                for column in ("orig_utility", "orig_utilityParent", "orig_utilityConfidence"):
                    _clear(row, column, changes, zone)
                notes_text = row.get("orig_notes") or ""
                if original_utility and original_utility in notes_text:
                    _clear(row, "orig_notes", changes, zone)
        if "hook" in fields:
            _clear(row, "orig_hook", changes, zone)
        if "takeaway" in fields:
            _clear(row, "orig_takeaway", changes, zone)
        if "supplier" in fields:
            original_supplier = (row.get("orig_supplier") or "").strip()
            if original_supplier and original_supplier != norm_supplier:
                _clear(row, "orig_supplier", changes, zone)
        if "classification" in fields and not still_municipal:
            if (row.get("orig_futureUse") or "") == "municipal_blacklist":
                _clear(row, "orig_futureUse", changes, zone)
            if (row.get("orig_aggregationStatus") or "") == "municipal_utility":
                _clear(row, "orig_aggregationStatus", changes, zone)
            for column in ("CORR_original_forge_value", "CORR_previous_researched_value"):
                text = row.get(column) or ""
                if any(marker in text for marker in MUNICIPAL_MARKERS):
                    _clear(row, column, changes, zone)
            notes_text = row.get("orig_notes") or ""
            if any(marker in notes_text for marker in OWNERSHIP_MARKERS):
                _clear(row, "orig_notes", changes, zone)
        notes_text = row.get("orig_notes") or ""
        if "utility" in fields and _notes_name_only_the_wrong_utility(notes_text, norm_utility):
            _clear(row, "orig_notes", changes, zone)
        if "recorded rate" in fields or "current rate" in fields:
            original_rate = (row.get("orig_currentRate") or "").strip()
            kept = {(row.get("CURRENT_rate") or "").strip(), (row.get("PRIOR_rate") or "").strip()}
            kept.discard("")
            if original_rate and original_rate not in kept:
                _clear(row, "orig_currentRate", changes, zone)
                _clear(row, "orig_rateChange", changes, zone)
        if "NOPEC" in (row.get("orig_supplier") or "") and "NOPEC" not in norm_supplier:
            if fields & {"supplier", "recorded rate", "hook", "takeaway"}:
                _clear(row, "orig_supplier", changes, zone)
    with open(DATASET, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return changes


def purge_ledger() -> list[str]:
    with open(LEDGER, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    kept = []
    removed = []
    for row in rows:
        rate = (row.get("rate_c_kWh") or "").strip()
        zone = row.get("zone") or ""
        if zone == "Stark County (Unincorporated / Remaining)" and rate == "9.77":
            removed.append(f"ledger {zone} {rate}")
            continue
        if zone in {
            "Mahoning County",
            "Springfield Township (Mahoning)",
            "Jackson Township (Mahoning)",
            "Coitsville Township",
            "Austintown Township",
        } and rate == "10.59":
            removed.append(f"ledger {zone} {rate}")
            continue
        kept.append(row)
    with open(LEDGER, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(kept)
    return removed


def purge_journal() -> list[str]:
    """Drop journal copies that only retell an incorrect municipal classification.

    The corrected zone already lives in the region file. Replaying a journal
    note that says the place was on the municipal list would keep that
    classification in history.
    """
    changes = []
    lines = []
    with open(JOURNAL, encoding="utf-8") as handle:
        raw = handle.readlines()
    for line in raw:
        if not line.strip():
            continue
        event = json.loads(line)
        note = (event.get("note") or "") + " " + ((event.get("zone") or {}).get("notes") or "")
        if event.get("kind") == "zone" and "municipal list" in note.lower():
            changes.append(f"journal {event.get('zone_key')}")
            continue
        lines.append(json.dumps(event, ensure_ascii=False) + "\n")
    with open(JOURNAL, "w", encoding="utf-8") as handle:
        handle.writelines(lines)
    return changes


def purge_overlay() -> list[str]:
    with open(OVERLAY, encoding="utf-8") as handle:
        overlay = json.load(handle)
    changes = []
    meta = overlay.get("meta") or {}
    for key, item in meta.items():
        question = item.get("question") or ""
        if "10.59" in question and "Mahoning" in key:
            item["question"] = (
                "Unresolved question. No county-wide aggregation rate is on file. "
                "Confirm whether the county certificate is active, or whether supply is only through the townships. "
                "Phone number not in sources (community clerk / fiscal officer)."
            )
            changes.append(f"overlay {key} question")
    with open(OVERLAY, "w", encoding="utf-8") as handle:
        json.dump(overlay, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return changes


def main() -> None:
    notes = load_notes()
    changes = []
    changes.extend(purge_dataset(notes))
    changes.extend(purge_ledger())
    changes.extend(purge_journal())
    changes.extend(purge_overlay())
    print(f"purged {len(changes)}")
    for line in changes:
        print(line)


if __name__ == "__main__":
    main()
