"""
FORGE CRM — Web Interface
Run with: python app.py
Then open: http://localhost:5000
"""

import csv
import json
import os
from datetime import datetime, date
from flask import Flask, jsonify, render_template, redirect, request

app = Flask(__name__)
OUTPUT_DIR = "output"
REGIONS_DIR = os.path.join("data", "regions")

STATUS_SORT = {"pain_hit": 0, "pain_coming": 1, "transition": 2, "verify": 3, "stable": 4}


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


@app.route("/hotspots")
def hotspots():
    zones = _load_zones()
    return render_template("hotspots.html",
                           zones=zones,
                           zones_json=json.dumps(zones),
                           active="hotspots")


@app.route("/goals")
def goals():
    return render_template("goals.html",
                           goals=_load_goals(),
                           active="goals")


@app.route("/settings")
def settings():
    ai_enabled = bool(os.getenv("ANTHROPIC_API_KEY"))
    gmaps_enabled = bool(os.getenv("GOOGLE_MAPS_API_KEY"))
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
    os.system("python run_pipeline.py --skip-scrape &")
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
    # Remove internal field before saving
    data.pop("_source_file", None)
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
    data.pop("_source_file", None)
    if os.path.exists(path):
        with open(path) as f:
            zones = json.load(f)
    else:
        zones = []
    zones.append(data)
    with open(path, "w") as f:
        json.dump(zones, f, indent=2)
    return jsonify({"ok": True})

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
