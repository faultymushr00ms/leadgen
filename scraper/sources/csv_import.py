"""
CSV Importer — cleans and ingests messy Map Builder exports.
Handles multi-territory data: Ohio, Texas, New York, Ontario, Alberta.

Deals with:
  - Continuation rows (empty WKT = more notes for the row above)
  - WKT coordinate parsing → territory auto-detection
  - Split/overflowing address columns
  - Inconsistent phone formatting
  - Action code decoding
  - Notes cleanup (keeps business-relevant content)
  - Canadian vs US territory flagging

Usage:
    from scraper.sources.csv_import import CSVImportSource
    source = CSVImportSource("data/raw_import.csv")
    leads = source.fetch()
"""

import csv
import re
import os
from typing import List, Optional, Tuple
from .base import BaseSource, RawLead

# ── Action code decoder ────────────────────────────────────────────────────────
ACTION_CODES = {
    "cb":        "callback",           # Has owner name / some data — worth calling
    "wi":        "walk_in",            # Rep visited without appointment — scouted
    "cho":       "call_head_office",   # Corporate chain — escalate, don't call location
    "ap rb":     "appointment_return", # Had appointment, need to go back — high value
    "ap":        "appointment",        # Live appointment — top priority
    "lv":        "large_volume",       # Large volume marker — corporate lane
    "xlv":       "extra_large_volume", # Extra large — highest value corporate
    "ni":        "not_interested",     # Not interested — skip
    "apoa":      "appt_other_agent",   # Another agent booked — reference only
    "apoa sold": "customer_other_agent", # Closed by another agent — already customer
    "dnq":       "did_not_qualify",    # Does not qualify — skip
    "nis":       "not_in_service",     # Number not in service — skip
    "cx":        "customer",           # Already our customer — exclude from calls
    "mail":      "email_sent",         # Email sent — follow up with call
    "spawn":     "territory_marker",   # Territory/admin marker — not a real lead
    "noor":      "noor_leads",         # Leads from agent Noor — treat as regular
    "dnc":       "do_not_call",        # LEGAL — never appears on call sheet
    "2026":      "call_2026",          # Schedule for 2026
    "2027":      "call_2027",          # Schedule for 2027
    "2028":      "call_2028",          # Schedule for 2028
    "":          "new",                # No status — fresh unworked lead
}

# Leads with these statuses are excluded entirely — never reach the call sheet
HARD_EXCLUDE = {"do_not_call", "customer", "customer_other_agent", "territory_marker"}

# Leads with these statuses are skipped as unqualified
SOFT_SKIP = {"not_interested", "did_not_qualify", "not_in_service", "appt_other_agent"}

# These route into the corporate/large-volume lane in Agent 3
CORPORATE_FLAGS = {"call_head_office", "large_volume", "extra_large_volume"}

# Urgency priority order for Agent 3 (higher = more urgent)
ACTION_PRIORITY = {
    "appointment":        100,
    "appointment_return":  90,
    "email_sent":          80,  # email sent, call to follow up
    "extra_large_volume":  75,
    "large_volume":        70,
    "callback":            65,
    "walk_in":             60,
    "noor_leads":          50,
    "call_2026":           45,
    "new":                 40,
    "call_head_office":    35,  # worth it but longer play
    "call_2027":           20,
    "call_2028":           10,
    "not_interested":       5,  # revisit eventually
    "did_not_qualify":      0,
    "not_in_service":       0,
}

# ── Territory detection from GPS coordinates ───────────────────────────────────
# Bounding boxes: (lat_min, lat_max, lon_min, lon_max)
TERRITORY_BOUNDS = {
    "Alberta":  (49.0,  60.0, -120.0, -110.0),
    "Ontario":  (41.5,  57.0,  -95.0,  -74.0),
    "New York": (40.4,  45.1,  -79.8,  -71.8),
    "Ohio":     (38.4,  42.0,  -84.8,  -80.5),
    "Texas":    (25.8,  36.5, -106.6,  -93.5),
}

# Lines that are clearly personal/non-business — stripped quietly
PERSONAL_PATTERNS = [
    r"biggest whore",
    r"dried out",
    r"needs a hug",
    r"all my electric under an umbrella",  # keep business context, strip personal commentary
]


def _detect_territory(lat: float, lon: float) -> str:
    for territory, (lat_min, lat_max, lon_min, lon_max) in TERRITORY_BOUNDS.items():
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return territory
    return "Unknown"


def _parse_wkt(wkt: str) -> Optional[Tuple[float, float]]:
    """Parse 'POINT (lon lat)' → (lat, lon). Returns None if not a valid point."""
    match = re.search(r"POINT\s*\(([+-]?\d+\.?\d*)\s+([+-]?\d+\.?\d*)\)", wkt or "")
    if not match:
        return None
    lon, lat = float(match.group(1)), float(match.group(2))
    return lat, lon


def _clean_phone(raw: str) -> str:
    """Strip everything except digits, return formatted as XXX-XXX-XXXX."""
    if not raw:
        return ""
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    if len(digits) == 11 and digits[0] == "1":
        return f"{digits[1:4]}-{digits[4:7]}-{digits[7:]}"
    return raw.strip()  # return as-is if we can't parse it


def _clean_notes(raw: str) -> str:
    """Remove personal commentary, keep business-relevant content."""
    if not raw:
        return ""
    lines = raw.split("\n")
    clean_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        is_personal = any(re.search(p, stripped, re.IGNORECASE) for p in PERSONAL_PATTERNS)
        if not is_personal:
            clean_lines.append(stripped)
    return " | ".join(clean_lines)


def _decode_action(code: str) -> str:
    return ACTION_CODES.get((code or "").lower().strip(), code or "new")


def _extract_rce_from_notes(notes: str) -> float:
    """Pull RCE estimates out of free-text notes if present."""
    if not notes:
        return 0.0
    # Matches: "50-100 RCE (96 calculated)", "96 RCE", ".5 RCE", "5 RCE's"
    match = re.search(r"([\d.]+)\s*(?:calculated|RCE)", notes, re.IGNORECASE)
    if match:
        return float(match.group(1))
    # Range: take the midpoint
    range_match = re.search(r"(\d+)\s*[-–]\s*(\d+)\s*RCE", notes, re.IGNORECASE)
    if range_match:
        return (float(range_match.group(1)) + float(range_match.group(2))) / 2
    return 0.0


def _reconstruct_address(row: dict, extra_cols: List[str]) -> Tuple[str, str, str]:
    """
    The Address column often overflows into extra unnamed columns.
    Returns (street, city, zip).
    """
    base_address = (row.get("Address") or "").strip()
    notes_col = (row.get("Notes") or "").strip()

    # Collect overflow columns — anything after the named columns
    overflow = [v.strip() for v in extra_cols if v.strip()]

    # Look for state abbreviation to find city/state boundary
    all_parts = [base_address] + overflow
    street_parts, city_parts, zip_code = [], [], ""

    for part in all_parts:
        if not part:
            continue
        # US/Canada zip/postal code
        zip_match = re.search(r"\b(\d{5}(?:-\d{4})?|[A-Z]\d[A-Z]\s?\d[A-Z]\d)\b", part)
        if zip_match:
            zip_code = zip_match.group(1)
        # State abbreviation (TX, OH, NY, ON, AB...)
        if re.search(r"\b(TX|OH|NY|ON|AB|CA|PA|WV|KY|IN|MI)\b", part):
            city_parts.append(part)
        else:
            street_parts.append(part)

    street = ", ".join(p for p in street_parts if p and p != zip_code)
    city_raw = ", ".join(p for p in city_parts if p)

    # Extract just the city name (before state abbreviation)
    city_match = re.search(r"^([^,]+)", city_raw)
    city = city_match.group(1).strip() if city_match else city_raw

    return street, city, zip_code


# ── Main row merger — handles continuation rows ────────────────────────────────

def _merge_rows(raw_rows: List[dict], fieldnames: List[str]) -> List[dict]:
    """
    Rows without a WKT value are continuation lines — they belong to the
    previous row's notes field. Merge them before processing.
    """
    merged = []
    current = None
    named_fields = set(fieldnames)

    for row in raw_rows:
        wkt = (row.get("WKT") or "").strip()

        if wkt.startswith("POINT"):
            if current:
                merged.append(current)
            current = dict(row)
            current["_extra_notes"] = []
        else:
            # Continuation — grab any non-empty text and append to notes
            extra_text = " ".join(
                v.strip() for v in row.values() if v and v.strip()
            )
            if extra_text and current:
                current["_extra_notes"].append(extra_text)

    if current:
        merged.append(current)

    return merged


# ── Convert one merged row → RawLead ──────────────────────────────────────────

def _row_to_lead(row: dict, fieldnames: List[str]) -> Optional[RawLead]:
    name = (row.get("name") or "").strip()
    if not name:
        return None

    # Coordinates and territory
    coords = _parse_wkt(row.get("WKT", ""))
    lat, lon, territory = 0.0, 0.0, "Unknown"
    if coords:
        lat, lon = coords
        territory = _detect_territory(lat, lon)

    # Phones
    phone1 = _clean_phone(row.get("Phone No.", ""))
    phone2 = _clean_phone(row.get("Phone No. 2", ""))
    phone = phone1 or phone2

    # Address — reconstruct from split columns
    known_cols = {"WKT", "Action", "Date", "App Date", "Future Date",
                  "Sign Date", "name", "Owner", "Phone No.", "Phone No. 2",
                  "Address", "Notes", "Employee Referral", "Noor", "_extra_notes"}
    overflow = [row.get(f, "") for f in fieldnames if f not in known_cols]
    street, city, zip_code = _reconstruct_address(row, overflow)

    # Notes — combine main notes + continuation rows
    main_notes = row.get("Notes", "") or ""
    extra = " | ".join(row.get("_extra_notes", []))
    raw_notes = f"{main_notes} {extra}".strip()
    notes = _clean_notes(raw_notes)

    # RCE extraction from notes
    rce_from_notes = _extract_rce_from_notes(raw_notes)

    # Action code
    raw_action = (row.get("Action") or "").strip().lower()
    action = ACTION_CODES.get(raw_action, raw_action or "new")

    # Hard excludes — these never reach the pipeline
    if action in HARD_EXCLUDE:
        return None

    # Soft skips — unqualified, mark but still pass through for training data
    is_skipped = action in SOFT_SKIP

    # Dates — store for Agent 3 follow-up timing
    last_contact_date = (
        row.get("Date") or row.get("App Date") or row.get("Future Date") or ""
    ).strip()
    # Clean messy date formats like "Dec 13 Dec 16" → take the last date
    if last_contact_date:
        dates = re.findall(r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+(?:\s+\d{4})?",
                           last_contact_date)
        last_contact_date = dates[-1] if dates else last_contact_date

    owner = (row.get("Owner") or "").strip()

    # Build known_info string for the qualifier
    known_info_parts = []
    if action:
        known_info_parts.append(f"Status: {action}")
    if owner:
        known_info_parts.append(f"Contact: {owner}")
    if last_contact_date:
        known_info_parts.append(f"Last contact: {last_contact_date}")
    if rce_from_notes:
        known_info_parts.append(f"RCE noted in field: {rce_from_notes}")
    if action in CORPORATE_FLAGS:
        known_info_parts.append("CORPORATE: email-first approach required")
    if notes:
        known_info_parts.append(notes)

    # Action priority score — passed through to Agent 3
    priority = ACTION_PRIORITY.get(action, 40)

    # Skipped leads get zeroed priority but stay in data for training purposes
    if is_skipped:
        priority = 0

    return RawLead(
        company_name=name,
        address=street,
        city=city,
        zip_code=zip_code,
        phone=phone,
        industry="",          # Map Builder data rarely has industry — qualifier infers it
        business_type="",
        source=f"CSV Import ({territory})",
        notes=" | ".join(known_info_parts),
        latitude=lat,
        longitude=lon,
        state=territory,      # stores territory for multi-territory support
        source_count=1,
        confirmed_by=[f"CSV Import ({territory})"],
    )


# ── Source class ───────────────────────────────────────────────────────────────

class CSVImportSource(BaseSource):
    name = "CSV Import"

    def __init__(self, filepath: str):
        self.filepath = filepath

    def fetch(self) -> List[RawLead]:
        if not os.path.exists(self.filepath):
            print(f"  [CSV Import] File not found: {self.filepath} — skipping.")
            return []

        print(f"  [CSV Import] Reading {self.filepath}...")

        with open(self.filepath, newline="", encoding="utf-8-sig") as f:
            # Sniff the delimiter
            sample = f.read(4096)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = csv.excel
                dialect.delimiter = "\t"

            reader = csv.DictReader(f, dialect=dialect)
            fieldnames = reader.fieldnames or []
            raw_rows = list(reader)

        print(f"  [CSV Import] {len(raw_rows)} raw rows read. Merging continuation rows...")
        merged = _merge_rows(raw_rows, fieldnames)
        print(f"  [CSV Import] {len(merged)} business records after merge.")

        leads: List[RawLead] = []
        seen: set = set()
        territory_counts: dict = {}

        for row in merged:
            lead = _row_to_lead(row, fieldnames)
            if lead is None:
                continue
            key = lead.dedup_key()
            if key in seen:
                continue
            seen.add(key)
            leads.append(lead)
            t = lead.state
            territory_counts[t] = territory_counts.get(t, 0) + 1

        print(f"  [CSV Import] {len(leads)} unique leads extracted.")
        print(f"  [CSV Import] Territory breakdown:")
        for territory, count in sorted(territory_counts.items()):
            print(f"               {territory:<12} {count}")

        return leads
