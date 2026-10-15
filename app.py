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
from flask import Flask, jsonify, render_template, redirect, request

from forge_config import env_is_configured, pipeline_argv
import zone_intel

load_dotenv()

app = Flask(__name__)
OUTPUT_DIR = "output"
REGIONS_DIR = os.path.join("data", "regions")

STATUS_SORT = {"rollover_dissolved": 0, "rollover": 1, "pain_hit": 2, "pricing_updated": 3, "pain_coming": 4, "transition": 5, "verify": 6, "stable": 7}


def _load_zones() -> list:
    zones = []
    if not os.path.exists(REGIONS_DIR):
        return zones
    for fname in sorted(os.listdir(REGIONS_DIR)):
        if fname.endswith(".json"):
            region_key = fname[:-5]  # strip .json
            with open(os.path.join(REGIONS_DIR, fname)) as f:
                file_zones = json.load(f)
            for z in file_zones:
                z["_source_file"] = region_key
            zones.extend(file_zones)
    zone_intel.attach_research(zones)
    zones.sort(key=lambda z: (
        STATUS_SORT.get(z.get("status", "verify"), 9),
        -(z.get("rateChange") or 0),
        z.get("name", ""),
    ))
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
    }


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

@app.route("/api/zones/<region_file>/<path:zone_name>", methods=["PUT"])
def api_update_zone(region_file, zone_name):
    path = os.path.join(REGIONS_DIR, region_file + ".json")
    if not os.path.exists(path):
        return jsonify({"error": "region not found"}), 404
    with open(path) as f:
        zones = json.load(f)
    data = request.get_json()
    # Research is derived from the reconciliation files. Never persist it
    # back into the original region JSON.
    for key in ("_source_file", "research", "original", "card"):
        data.pop(key, None)
    idx = next((i for i, z in enumerate(zones) if z["name"] == zone_name), None)
    if idx is None:
        return jsonify({"error": "zone not found"}), 404
    zones[idx] = data
    with open(path, "w") as f:
        json.dump(zones, f, indent=2)
    return jsonify({"ok": True})

@app.route("/api/zones/<region_file>", methods=["POST"])
def api_add_zone(region_file):
    path = os.path.join(REGIONS_DIR, region_file + ".json")
    data = request.get_json()
    for key in ("_source_file", "research", "original", "card"):
        data.pop(key, None)
    if os.path.exists(path):
        with open(path) as f:
            zones = json.load(f)
    else:
        zones = []
    zones.append(data)
    with open(path, "w") as f:
        json.dump(zones, f, indent=2)
    return jsonify({"ok": True})

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


def _zip_payload(zipcode: str) -> tuple[dict, int]:
    zipcode = unquote(zipcode).strip()
    disclaimer = zone_intel.zip_disclaimer()
    zip_map = _load_zip_map()
    zone_name = zip_map.get(zipcode)
    if not zone_name:
        return {
            "found": False,
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
    payload = {
        "found": True,
        "zip": zipcode,
        "zone_name": zone_name,
        "eligibility": "not_proof",
        "disclaimer": disclaimer,
        "match_count": len(matches),
        "jurisdictions": jurisdictions,
        "zone": matches[0] if len(matches) == 1 else None,
        "message": (
            f"ZIP {zipcode} is mapped to the zone name “{zone_name}”. "
            "That mapping is not proof the address is eligible."
        ),
    }
    return payload, 200


@app.route("/api/zip/<zipcode>")
def api_zip_lookup(zipcode):
    payload, status = _zip_payload(zipcode)
    return jsonify(payload), status


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


@app.route("/counties")
def counties():
    zones = _load_zones()
    selected = (request.args.get("county") or "").strip()
    zipcode = (request.args.get("zip") or "").strip()
    groups = zone_intel.group_counties(zones)
    current = next((group for group in groups if group["county"].lower() == selected.lower()), None)
    if current is None and groups and not zipcode:
        current = groups[0]
        selected = current["county"]
    zip_result = None
    if zipcode:
        zip_result, _status = _zip_payload(zipcode)
    return render_template(
        "counties.html",
        active="intel",
        groups=groups,
        selected=selected,
        current=current,
        zipcode=zipcode,
        zip_result=zip_result,
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
    return render_template(
        "queue.html",
        active="queue",
        rows=rows,
        total=len(baseline),
        additions=additions,
        verification=verification,
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
        return render_template("battlecard.html", active="intel", zone=None, card=None, queue_item=None), 404
    return render_template(
        "battlecard.html",
        active="intel",
        zone=zone,
        card=zone["card"],
        research=zone.get("research") or {},
        queue_item=zone_intel.queue_for_zone(zone),
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
    path = os.path.join(REGIONS_DIR, region_file + ".json")
    if not os.path.exists(path):
        return jsonify({"error": "region not found"}), 404
    with open(path) as f:
        zones = json.load(f)
    zones = [z for z in zones if z["name"] != zone_name]
    with open(path, "w") as f:
        json.dump(zones, f, indent=2)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
