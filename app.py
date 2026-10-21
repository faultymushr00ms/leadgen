"""
FORGE CRM — Web Interface
Run with: python app.py
Then open: http://localhost:5000
"""

import csv
import json
import os
import subprocess
from datetime import datetime, date
from urllib.parse import unquote

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, redirect, request, send_file

from forge_config import env_is_configured, pipeline_argv
import history_store
import merged_research
import place_fallback
import place_index
import presentation
import puco_layer
import rate_change
import territory
import zone_intel

load_dotenv()

app = Flask(__name__)
OUTPUT_DIR = "output"
REGIONS_DIR = os.path.join("data", "regions")
GAS_DIR = os.path.join("data", "gas")

STATUS_SORT = {"rollover_dissolved": 0, "rollover": 1, "pain_hit": 2, "pricing_updated": 3, "pain_coming": 4, "transition": 5, "verify": 6, "stable": 7}


def _load_zones(commodity: str = "electric") -> list:
    zones = []
    dirs = [(REGIONS_DIR, "electric"), (GAS_DIR, "gas")]
    for data_dir, dir_commodity in dirs:
        if commodity != "all" and dir_commodity != commodity:
            continue
        if not os.path.exists(data_dir):
            continue
        for fname in sorted(os.listdir(data_dir)):
            if fname.endswith(".json"):
                region_key = fname[:-5]
                with open(os.path.join(data_dir, fname)) as f:
                    file_zones = json.load(f)
                for z in file_zones:
                    z["_source_file"] = region_key
                    z["_history_key"] = z.get("name")
                    z.setdefault("commodity", dir_commodity)
                zones.extend(file_zones)
    zone_intel.attach_research(zones)
    zones = history_store.apply_zone_history(zones)
    presentation.attach(zones)
    rate_change.annotate_zones(zones)
    zones.sort(key=lambda z: rate_change.sort_key(z, STATUS_SORT))
    return zones


# ── Helpers ────────────────────────────────────────────────────────────────────

def _latest_file(prefix: str, ext: str) -> str | None:
    if not os.path.exists(OUTPUT_DIR):
        return None
    files = sorted(f for f in os.listdir(OUTPUT_DIR)
                   if f.startswith(prefix) and f.endswith(ext))
    return os.path.join(OUTPUT_DIR, files[-1]) if files else None


def _load_call_sheet() -> list:
    path = _latest_file("call_sheet_", ".csv")
    if not path:
        return []
    leads = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            row["urgency_score"] = float(row.get("urgency_score", 0))
            row["rce_estimate"] = float(row.get("rce_estimate", 0))
            leads.append(row)
    return leads


def _load_qualified() -> list:
    path = _latest_file("qualified_leads_", ".json")
    if not path:
        return []
    with open(path) as f:
        return json.load(f).get("leads", [])


def _load_goals() -> dict:
    today = date.today()
    days_in_month = 20  # working days
    day_of_month = min(today.day, days_in_month)
    days_left = max(1, days_in_month - day_of_month)

    rce_this_month = 0
    rce_period = 0

    baseline_pct = min(100, round((rce_this_month / 100) * 100))
    bonus_pct = min(100, round((rce_period / 600) * 100))
    rce_needed = max(0, 100 - rce_this_month)
    rce_per_day_needed = round(rce_needed / days_left, 1)
    rce_per_day_bonus = round(max(0, 150 - rce_this_month) / days_left, 1)

    return {
        "rce_this_month": rce_this_month,
        "rce_period": rce_period,
        "baseline_pct": baseline_pct,
        "bonus_pct": bonus_pct,
        "days_left": days_left,
        "rce_per_day_needed": rce_per_day_needed,
        "rce_per_day_bonus": rce_per_day_bonus,
    }


def _stats(leads: list) -> dict:
    qualified = len(leads)
    high_conf = sum(1 for l in leads if l.get("confidence") == "HIGH")
    sweet = sum(1 for l in leads
                if 5 <= float(l.get("rce_estimate", 0)) <= 30)
    return {
        "qualified": qualified,
        "high_confidence": high_conf,
        "sweet_spot": sweet,
        "rce_logged": 0,
        "quota_pct": 0,
    }


@app.context_processor
def inject_globals():
    return {
        "now": datetime.now().strftime("%a %b %d  %H:%M"),
        "active": "",
        "confidence_mark": presentation.confidence_mark,
        "lifecycle_label": presentation.lifecycle_label,
        "program_label": presentation.program_label,
        "term_label": presentation.term_label,
        "source_links": presentation.source_links,
    }


app.jinja_env.filters["voice"] = presentation.polish


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    leads = _load_call_sheet()
    return render_template("dashboard.html",
                           leads=leads,
                           stats=_stats(leads),
                           active="leads",
                           today=datetime.now().strftime("%A, %B %d %Y"))


@app.route("/leads")
def leads():
    all_leads = _load_qualified()
    return render_template("dashboard.html",
                           leads=all_leads,
                           stats=_stats(all_leads),
                           active="leads",
                           today=datetime.now().strftime("%A, %B %d %Y"))


@app.route("/lead/<int:idx>")
def lead_detail(idx):
    leads = _load_call_sheet()
    if idx >= len(leads):
        return redirect("/")
    return render_template("lead.html",
                           lead=leads[idx],
                           rank=idx + 1,
                           active="leads")


def _compute_weekly(zones: list) -> dict:
    from datetime import date, timedelta
    today = date.today()
    cutoff_90 = today + timedelta(days=90)
    cutoff_30 = today + timedelta(days=30)

    rollover_alerts, contract_review, pain_hit, pain_coming = [], [], [], []
    timing_windows, avoid_list, verify_list, unresolved_list = [], [], [], []
    blacklisted = {"municipal_utility", "electric_cooperative"}
    hot_statuses = {"rollover_dissolved", "rollover", "pain_hit", "pricing_updated", "pain_coming"}

    for z in zones:
        agg = z.get("aggregationStatus", "")
        status = z.get("status", "")
        research = z.get("research") or {}
        research_status = research.get("status") or {}
        program = research_status.get("program") or ""
        unresolved = bool(research_status.get("unresolved"))
        # Needs-call and conflict rows stay unresolved. A research note that
        # the app called a zone municipal does not move it to the avoid list.
        if unresolved and program.startswith("active"):
            unresolved_list.append(z)
            continue
        if agg in blacklisted or program.startswith("not_eligible"):
            avoid_list.append(z)
            if unresolved:
                unresolved_list.append(z)
            continue
        if unresolved:
            unresolved_list.append(z)
            continue

        term_end_str = z.get("termEnd")
        term_end_date = None
        if term_end_str:
            try:
                term_end_date = date.fromisoformat(term_end_str)
            except ValueError:
                pass

        expired = term_end_date is not None and term_end_date <= today
        near_expiry_90 = term_end_date is not None and term_end_date <= cutoff_90
        near_expiry_30 = term_end_date is not None and term_end_date <= cutoff_30

        if status == "rollover_dissolved":
            rollover_alerts.append(z)
        elif status == "rollover":
            rollover_alerts.append(z)
        elif expired and status not in hot_statuses:
            # termEnd passed but zone not yet manually flagged — surface for review
            contract_review.append(z)
        elif status == "pain_hit":
            pain_hit.append(z)
        elif status == "pricing_updated":
            pain_hit.append(z)
        elif status == "pain_coming":
            pain_coming.append(z)
            if near_expiry_90:
                timing_windows.append(z)
        elif status == "transition":
            if near_expiry_90:
                timing_windows.append(z)
        elif status == "verify":
            verify_list.append(z)

    return {
        "rollover_alerts": rollover_alerts,
        "contract_review": contract_review,
        "pain_hit": pain_hit,
        "pain_coming": pain_coming,
        "timing_windows": timing_windows,
        "avoid_list": avoid_list,
        "verify_list": verify_list,
        "targetable_count": len(rollover_alerts) + len(pain_hit) + len(pain_coming),
        "blacklisted_count": len(avoid_list),
        "timing_count": len(timing_windows),
        "rollover_count": len(rollover_alerts),
        "review_count": len(contract_review),
        "unresolved_list": unresolved_list,
        "unresolved_count": len(unresolved_list),
    }


@app.route("/weekly")
def weekly():
    zones = _load_zones()
    w = _compute_weekly(zones)
    return render_template("weekly.html", active="weekly", **w)


@app.route("/hotspots")
def hotspots():
    zones = _load_zones()
    return render_template("hotspots.html",
                           zones=zones,
                           active="hotspots")


@app.route("/goals")
def goals():
    return render_template("goals.html",
                           goals=_load_goals(),
                           active="goals")


@app.route("/settings")
def settings():
    ai_enabled = env_is_configured("ANTHROPIC_API_KEY")
    gmaps_enabled = env_is_configured("GOOGLE_MAPS_API_KEY")
    return render_template("settings.html",
                           ai_enabled=ai_enabled,
                           gmaps_enabled=gmaps_enabled,
                           active="settings")


@app.route("/log_close", methods=["POST"])
def log_close():
    company = request.form.get("company", "Unknown")
    rce = request.form.get("rce", "0")
    years = request.form.get("contract_years", "5")
    print(f"[FORGE] Close logged: {company} | {rce} RCE | {years}-year contract")
    return redirect("/goals")


@app.route("/export")
def export():
    from flask import send_file
    path = _latest_file("call_sheet_", ".csv")
    if path:
        return send_file(path, as_attachment=True)
    return redirect("/")


@app.route("/run")
def run_pipeline():
    # sys.executable is the venv interpreter when the app itself is.
    subprocess.Popen(
        pipeline_argv(),
        cwd=os.path.dirname(os.path.abspath(__file__)),
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return redirect("/")


@app.route("/api/zones", methods=["GET"])
def api_zones_list():
    zones = _load_zones()
    return jsonify(zones)

@app.route("/api/regions", methods=["GET"])
def api_regions_list():
    if not os.path.exists(REGIONS_DIR):
        return jsonify([])
    files = sorted(f.replace(".json","") for f in os.listdir(REGIONS_DIR) if f.endswith(".json"))
    return jsonify(files)

def _find_loaded_zone(region_file, zone_name):
    matches = [
        zone for zone in _load_zones()
        if zone.get("_source_file") == region_file
        and (zone.get("name") == zone_name or zone.get("_history_key") == zone_name)
    ]
    current = [zone for zone in matches if zone.get("name") == zone_name]
    if current:
        return current[0]
    return matches[0] if matches else None


def _zone_payload():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None
    for key in (
        "_source_file", "_history_key", "research", "original", "card", "history",
        "displayRateChange", "previousRateNeedsCheck", "rateDelta",
    ):
        data.pop(key, None)
    return data


@app.route("/api/zones/<region_file>/<path:zone_name>", methods=["PUT"])
def api_update_zone(region_file, zone_name):
    # Region JSON stays as first recorded. The edit is appended to history.
    data = _zone_payload()
    if data is None:
        return jsonify({"error": "expected object"}), 400
    zone = _find_loaded_zone(region_file, zone_name)
    if zone is None:
        return jsonify({"error": "zone not found"}), 404
    event = history_store.record_zone_change(
        region_file,
        zone.get("_history_key") or zone.get("name"),
        "update",
        data,
    )
    return jsonify({"ok": True, "id": event["id"], "appended": True})

@app.route("/api/zones/<region_file>", methods=["POST"])
def api_add_zone(region_file):
    data = _zone_payload()
    if data is None or not data.get("name"):
        return jsonify({"error": "name required"}), 400
    event = history_store.record_zone_change(region_file, data["name"], "add", data)
    return jsonify({"ok": True, "id": event["id"], "appended": True})

_ZIP_MAP_PATH = os.path.join("data", "zip_zone_map.json")
_zip_map_cache: dict | None = None

def _load_zip_map() -> dict:
    global _zip_map_cache
    if _zip_map_cache is None:
        if os.path.exists(_ZIP_MAP_PATH):
            with open(_ZIP_MAP_PATH) as f:
                raw = json.load(f)
            _zip_map_cache = {k: v for k, v in raw.items() if not k.startswith("_")}
        else:
            _zip_map_cache = {}
    return _zip_map_cache


_LOOKUP_REJECTED = "Enter a 5-digit ZIP or a place name."


def _zip_payload(zipcode: str) -> tuple[dict, int]:
    """ZIP map lookup. Invalid input is not echoed or logged."""
    disclaimer = zone_intel.zip_disclaimer()
    classified = place_index.classify_lookup(unquote(zipcode or "").strip())
    if classified is None or classified[0] != "zip":
        return {
            "ok": False,
            "found": False,
            "kind": "rejected",
            "eligibility": "not_proof",
            "disclaimer": disclaimer,
            "message": _LOOKUP_REJECTED,
        }, 400
    zipcode = classified[1]
    zip_map = _load_zip_map()
    zone_name = zip_map.get(zipcode)
    if not zone_name:
        return {
            "ok": True,
            "found": False,
            "kind": "zip",
            "zip": zipcode,
            "eligibility": "not_proof",
            "disclaimer": disclaimer,
            "message": "ZIP not mapped. That is not a finding about eligibility.",
        }, 404

    all_zones = _load_zones()
    matches = zone_intel.zones_named(all_zones, zone_name)
    jurisdictions = []
    for zone in matches:
        research = zone.get("research") or {}
        card = zone.get("card") or {}
        jurisdictions.append({
            "name": zone.get("name"),
            "source_file": zone.get("_source_file"),
            "jurisdiction": research.get("jurisdiction") or zone.get("name"),
            "county": research.get("county") or "",
            "utility": research.get("utility") or zone.get("utility") or "",
            "verification": (research.get("status") or {}).get("verificationLabel") or "",
            "card_url": card.get("url") or "",
        })
    single = {"name": matches[0].get("name")} if len(matches) == 1 else None
    payload = {
        "ok": True,
        "found": True,
        "kind": "zip",
        "zip": zipcode,
        "zone_name": zone_name,
        "eligibility": "not_proof",
        "disclaimer": disclaimer,
        "match_count": len(matches),
        "jurisdictions": jurisdictions,
        "zone": single,
        "message": (
            f"ZIP {zipcode} is mapped to the zone name “{zone_name}”. "
            "That mapping is not proof the address is eligible."
        ),
    }
    return payload, 200


def _lookup_payload(raw) -> tuple[dict, int]:
    """Classify a lookup. Rejected text is not copied into the response."""
    classified = place_index.classify_lookup(raw if isinstance(raw, str) else "")
    if classified is None:
        return {
            "ok": False,
            "found": False,
            "kind": "rejected",
            "message": _LOOKUP_REJECTED,
        }, 400
    kind, value = classified
    zones = _load_zones()
    if kind == "zip":
        payload, status = _zip_payload(value)
        payload["places"] = _with_nearby(place_index.lookup_zip(value, zones).get("places") or [], zones)
        return payload, status
    found = place_index.lookup_name(value, zones)
    places = _with_nearby(found.get("places") or [], zones)
    return {
        "ok": True,
        "found": bool(places),
        "kind": "place",
        "query": value,
        "count": found.get("count") or 0,
        "truncated": bool(found.get("truncated")),
        "zip_note": found.get("zip_note") or "",
        "places": places,
        "message": "Place name matched." if places else "No place with that name is in the index.",
    }, 200


@app.route("/api/zip/<path:zipcode>")
def api_zip_lookup(zipcode):
    payload, status = _zip_payload(zipcode)
    return jsonify(payload), status


@app.route("/api/lookup", methods=["POST"])
def api_lookup():
    """POST body only. The lookup value is not placed in the URL or the log."""
    data = request.get_json(silent=True) or {}
    raw = data.get("q") if isinstance(data, dict) else ""
    payload, status = _lookup_payload(raw)
    return jsonify(payload), status


@app.route("/api/place-web", methods=["POST"])
def api_place_web():
    """Optional web lookup for one indexed place. Results are unverified leads."""
    data = request.get_json(silent=True) or {}
    geoid = data.get("geoid") if isinstance(data, dict) else ""
    payload, status = place_fallback.lookup_web_by_geoid(geoid)
    return jsonify(payload), status


def _with_nearby(places: list, zones: list) -> list:
    """Attach nearest places, zones, and a place card. Coordinates stay off this payload."""
    active = [zone for zone in zones if not zone.get("superseded")]
    for place in places:
        place["nearby"] = territory.nearby_for_geoid(place.get("geoid") or "", zones, place.get("name") or "")
        place["fallback"] = place_fallback.build(place, active)
    return places


def _json_no_store(payload, status: int = 200):
    response = jsonify(payload)
    response.headers["Cache-Control"] = "no-store"
    return response, status


@app.route("/map")
def territory_map():
    return render_template("map.html", active="map", overlay_note=territory.OVERLAY_NOTE)


@app.route("/api/map")
def api_map():
    places = (request.args.get("places") or "incorporated").strip()
    payload = territory.map_payload(_load_zones(), include_unincorporated=(places == "all"))
    return jsonify(payload)


@app.route("/api/locate", methods=["POST"])
def api_locate():
    """Browser geolocation. The body is not logged, stored, or copied into the response."""
    data = request.get_json(silent=True) or {}
    lat = data.get("lat") if isinstance(data, dict) else None
    lon = data.get("lon") if isinstance(data, dict) else None
    payload, status = territory.locate(lat, lon, _load_zones())
    return _json_no_store(payload, status)


@app.route("/api/nearby", methods=["POST"])
def api_nearby():
    data = request.get_json(silent=True) or {}
    name = data.get("zone") if isinstance(data, dict) else ""
    region = data.get("region") if isinstance(data, dict) else ""
    if not isinstance(name, str) or not isinstance(region, str):
        return jsonify({"ok": False, "message": "A zone name is required."}), 400
    zones = _load_zones()
    zone = zone_intel.find_zone(zones, region.strip(), name.strip())
    if zone is None:
        return jsonify({"ok": False, "message": "No zone with that name is on file."}), 404
    return jsonify({"ok": True, "zone": zone.get("name") or "", "nearby": territory.nearby_for_zone(zone, zones)})


@app.route("/api/overlays")
def api_overlays():
    return jsonify(territory.load_overlays())


@app.route("/api/puco/aggregation")
def api_puco_aggregation():
    try:
        return jsonify(puco_layer.display_payload())
    except puco_layer.PucoUnavailable:
        return jsonify({
            "ok": False,
            "message": "The PUCO aggregation map could not be loaded.",
            "attribution": puco_layer.ATTRIBUTION,
            "disclaimer": puco_layer.DISCLAIMER,
        }), 503


@app.route("/api/geo/<path:name>")
def api_geo(name):
    path = territory.safe_geo_file(name)
    if not path:
        return jsonify({"ok": False, "message": "That map file is not available."}), 404
    return send_file(path, mimetype="application/geo+json", max_age=0)


def _queue_view():
    baseline = zone_intel.load_queue()
    additions = zone_intel.load_monitor_additions()
    return baseline, additions


@app.route("/intel")
def intel():
    zones = _load_zones()
    return render_template(
        "intel.html",
        active="intel",
        glance=zone_intel.nopec_glance(zones),
        ptc=zone_intel.load_ptc(),
    )


@app.route("/counties", methods=["GET", "POST"])
def counties():
    zones = _load_zones()
    if request.method == "POST":
        selected = (request.form.get("county") or "").strip()
        raw_lookup = request.form.get("q") or ""
    else:
        selected = (request.args.get("county") or "").strip()
        raw_lookup = request.args.get("zip") or request.args.get("q") or ""
    groups = zone_intel.group_counties(zones)
    known = {group["county"].lower(): group["county"] for group in groups}
    selected = known.get(selected.lower(), "")
    lookup_error = None
    lookup_value = ""
    zip_result = None
    place_hits = []
    if str(raw_lookup).strip():
        payload, _status = _lookup_payload(raw_lookup)
        if not payload.get("ok"):
            lookup_error = payload.get("message")
        elif payload.get("kind") == "zip":
            lookup_value = payload.get("zip") or ""
            zip_result = payload
            place_hits = payload.get("places") or []
        else:
            lookup_value = payload.get("query") or ""
            place_hits = payload.get("places") or []
            if not place_hits:
                lookup_error = payload.get("message")
    current = next((group for group in groups if group["county"].lower() == selected.lower()), None)
    if current is None and groups and not str(raw_lookup).strip():
        current = groups[0]
        selected = current["county"]
    return render_template(
        "counties.html",
        active="intel",
        groups=groups,
        selected=selected,
        current=current,
        lookup_value=lookup_value,
        lookup_error=lookup_error,
        zip_result=zip_result,
        place_hits=place_hits,
        disclaimer=zone_intel.zip_disclaimer(),
    )


@app.route("/ptc")
def price_to_compare():
    zones = _load_zones()
    defaults = []
    for zone in zones:
        research = zone.get("research") or {}
        current = research.get("current") or {}
        if "price to compare" in (current.get("basis") or "").lower() and current.get("rate_raw"):
            defaults.append(zone)
    defaults.sort(key=lambda zone: ((zone.get("research") or {}).get("utility") or "", zone.get("name") or ""))
    return render_template(
        "ptc.html",
        active="intel",
        ptc=zone_intel.load_ptc(),
        defaults=defaults,
    )


@app.route("/queue")
def investigation_queue():
    baseline, additions = _queue_view()
    verification = (request.args.get("verification") or "").strip()
    rows = baseline
    if verification:
        rows = [row for row in baseline if row.get("STATUS_verification") == verification]
    puco = puco_layer.load_queue_flags()
    selected = (request.args.get("puco") or "app").strip()
    return render_template(
        "queue.html",
        active="queue",
        rows=rows,
        total=len(baseline),
        additions=additions,
        verification=verification,
        puco_flags=puco_layer.filter_flags(puco["flags"], selected),
        puco_counts=puco["counts"],
        puco_filter=selected,
        puco_disclaimer=puco["disclaimer"],
        puco_attribution=puco["attribution"],
    )


@app.route("/hot-leads")
def hot_leads():
    zones = _load_zones()
    by_name = {}
    for zone in zones:
        by_name.setdefault((zone.get("name") or "").casefold(), zone)
    rows = []
    for row in merged_research.load_hot_leads():
        item = dict(row)
        zone = by_name.get((row.get("community") or "").casefold())
        if zone is None:
            cleaned = (row.get("community") or "").replace(" Twp", "").casefold()
            zone = by_name.get(cleaned)
        item["card_url"] = zone["card"]["url"] if zone and zone.get("card") else ""
        rows.append(item)
    return render_template("hot_leads.html", active="hotleads", rows=rows)


@app.route("/unverified")
def unverified_leads():
    query = (request.args.get("q") or "").strip().lower()
    groups = merged_research.unverified_groups()
    if query:
        groups = [
            group for group in groups
            if query in group["community"].lower() or query in group["county"].lower()
        ]
    return render_template(
        "unverified.html",
        active="unverified",
        groups=groups,
        questions=merged_research.unmatched_questions(),
        q=request.args.get("q") or "",
    )


@app.route("/expiring")
def expiring():
    zones = _load_zones()
    queue = zone_intel.load_queue()
    return render_template(
        "expiring.html",
        active="expiring",
        expiring=zone_intel.expiring_zones(zones, queue),
        hotspots=zone_intel.hotspot_zones(zones, queue),
    )


@app.route("/card")
def battlecard():
    zones = _load_zones()
    source_file = (request.args.get("file") or "").strip()
    name = (request.args.get("name") or "").strip()
    zone = zone_intel.find_zone(zones, source_file, name)
    if zone is None or not zone.get("card"):
        return render_template("battlecard.html", active="intel", zone=None, card=None, queue_item=None, nearby=None), 404
    return render_template(
        "battlecard.html",
        active="intel",
        zone=zone,
        card=zone["card"],
        research=zone.get("research") or {},
        queue_item=zone_intel.queue_for_zone(zone),
        nearby=territory.nearby_for_zone(zone, zones),
    )


@app.route("/api/rate-ledger")
def api_rate_ledger():
    return jsonify(zone_intel.load_rate_ledger())


@app.route("/api/queue")
def api_queue():
    baseline, additions = _queue_view()
    return jsonify({"baseline": baseline, "additions": additions})


@app.route("/api/ptc")
def api_ptc():
    return jsonify(zone_intel.load_ptc())


@app.route("/api/zones/<region_file>/<path:zone_name>", methods=["DELETE"])
def api_delete_zone(region_file, zone_name):
    """Mark a zone superseded. The record stays stored."""
    zone = _find_loaded_zone(region_file, zone_name)
    if zone is None:
        return jsonify({"error": "zone not found"}), 404
    event = history_store.record_zone_change(
        region_file,
        zone.get("_history_key") or zone.get("name"),
        "supersede",
        {"name": zone.get("name")},
    )
    return jsonify({"ok": True, "superseded": True, "id": event["id"], "superseded_at": event["recorded_at"]})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
