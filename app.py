"""
FORGE CRM — Web Interface
Run with: python app.py
Then open: http://localhost:5000
"""

import csv
import json
import os
from datetime import datetime, date
from flask import Flask, render_template, redirect, request

app = Flask(__name__)
OUTPUT_DIR = "output"


# ── Ohio zone data ─────────────────────────────────────────────────────────────
OHIO_ZONES = [
    {
        "id": 1,
        "county": "Mahoning",
        "city": "Youngstown",
        "heat": "hot",
        "utility": "Ohio Edison",
        "energy_type": "Gas + Electric",
        "rate_change_pct": 8.4,
        "rate_change_date": "May 2025",
        "opportunity_count": 142,
        "lat": 41.0998,
        "lng": -80.6495,
        "trigger": "Rate hike effective May 2025 — customers actively shopping",
    },
    {
        "id": 2,
        "county": "Trumbull",
        "city": "Warren",
        "heat": "pain",
        "utility": "Ohio Edison",
        "energy_type": "Gas + Electric",
        "rate_change_pct": 6.1,
        "rate_change_date": "Mar 2025",
        "opportunity_count": 118,
        "lat": 41.2373,
        "lng": -80.8184,
        "trigger": "High industrial density — multiple contracts expiring Q3",
    },
    {
        "id": 3,
        "county": "Columbiana",
        "city": "Salem",
        "heat": "pain",
        "utility": "Ohio Edison",
        "energy_type": "Gas + Electric",
        "rate_change_pct": 5.8,
        "rate_change_date": "Apr 2025",
        "opportunity_count": 76,
        "lat": 40.9017,
        "lng": -80.8562,
        "trigger": "Border territory — competitors underserving this area",
    },
    {
        "id": 4,
        "county": "Stark",
        "city": "Canton",
        "heat": "warm",
        "utility": "Ohio Edison",
        "energy_type": "Gas + Electric",
        "rate_change_pct": 3.2,
        "rate_change_date": "Feb 2025",
        "opportunity_count": 203,
        "lat": 40.7989,
        "lng": -81.3784,
        "trigger": None,
    },
    {
        "id": 5,
        "county": "Summit",
        "city": "Akron",
        "heat": "warm",
        "utility": "FirstEnergy",
        "energy_type": "Gas + Electric",
        "rate_change_pct": 2.5,
        "rate_change_date": "Jan 2025",
        "opportunity_count": 287,
        "lat": 41.0814,
        "lng": -81.5190,
        "trigger": None,
    },
    {
        "id": 6,
        "county": "Cuyahoga",
        "city": "Cleveland",
        "heat": "warm",
        "utility": "Ohio Edison",
        "energy_type": "Gas + Electric",
        "rate_change_pct": 1.8,
        "rate_change_date": "Dec 2024",
        "opportunity_count": 412,
        "lat": 41.4993,
        "lng": -81.6944,
        "trigger": None,
    },
    {
        "id": 7,
        "county": "Portage",
        "city": "Ravenna",
        "heat": "normal",
        "utility": "FirstEnergy",
        "energy_type": "Electric",
        "rate_change_pct": 0,
        "rate_change_date": "",
        "opportunity_count": 54,
        "lat": 41.1581,
        "lng": -81.2423,
        "trigger": None,
    },
    {
        "id": 8,
        "county": "Lake",
        "city": "Mentor",
        "heat": "normal",
        "utility": "Ohio Edison",
        "energy_type": "Electric",
        "rate_change_pct": 0,
        "rate_change_date": "",
        "opportunity_count": 89,
        "lat": 41.6661,
        "lng": -81.3395,
        "trigger": None,
    },
    {
        "id": 9,
        "county": "Geauga",
        "city": "Chardon",
        "heat": "cooling",
        "utility": "Ohio Edison",
        "energy_type": "Electric",
        "rate_change_pct": -1.2,
        "rate_change_date": "Mar 2025",
        "opportunity_count": 31,
        "lat": 41.5789,
        "lng": -81.1631,
        "trigger": None,
    },
    {
        "id": 10,
        "county": "Ashtabula",
        "city": "Ashtabula",
        "heat": "cooling",
        "utility": "Ohio Edison",
        "energy_type": "Electric",
        "rate_change_pct": -0.8,
        "rate_change_date": "Feb 2025",
        "opportunity_count": 28,
        "lat": 41.8650,
        "lng": -80.7898,
        "trigger": None,
    },
    {
        "id": 11,
        "county": "Lawrence",
        "city": "Ironton",
        "heat": "normal",
        "utility": "AEP Ohio",
        "energy_type": "Gas + Electric",
        "rate_change_pct": 2.1,
        "rate_change_date": "Apr 2025",
        "opportunity_count": 41,
        "lat": 38.5367,
        "lng": -82.6824,
        "trigger": None,
    },
    {
        "id": 12,
        "county": "Medina",
        "city": "Medina",
        "heat": "normal",
        "utility": "FirstEnergy",
        "energy_type": "Gas + Electric",
        "rate_change_pct": 0,
        "rate_change_date": "",
        "opportunity_count": 67,
        "lat": 41.1381,
        "lng": -81.8638,
        "trigger": None,
    },
]

HEAT_ORDER = {"hot": 0, "pain": 1, "warm": 2, "normal": 3, "cooling": 4}
OHIO_ZONES_SORTED = sorted(OHIO_ZONES, key=lambda z: (HEAT_ORDER.get(z["heat"], 9), -z["rate_change_pct"]))


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
    return render_template("hotspots.html",
                           zones=OHIO_ZONES_SORTED,
                           zones_json=json.dumps(OHIO_ZONES_SORTED),
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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
