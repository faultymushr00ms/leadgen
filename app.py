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

    # Placeholder — replace with real logged RCE once database exists
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


@app.route("/")
def dashboard():
    leads = _load_call_sheet()
    return render_template("dashboard.html",
                           leads=leads,
                           stats=_stats(leads),
                           today=datetime.now().strftime("%A, %B %d %Y"))


@app.route("/leads")
def leads():
    all_leads = _load_qualified()
    return render_template("dashboard.html",
                           leads=all_leads,
                           stats=_stats(all_leads),
                           today=datetime.now().strftime("%A, %B %d %Y"))


@app.route("/lead/<int:idx>")
def lead_detail(idx):
    leads = _load_call_sheet()
    if idx >= len(leads):
        return redirect("/")
    return render_template("lead.html",
                           lead=leads[idx],
                           rank=idx + 1)


@app.route("/goals")
def goals():
    return render_template("goals.html", goals=_load_goals())


@app.route("/log_close", methods=["POST"])
def log_close():
    # Placeholder — writes to console until database exists
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
