"""
Agent 3: Prioritizer
Takes qualified leads from Agent 2 and ranks them by urgency so you
know exactly who to call first each day.

Scoring factors (weights set in config/agent_config.yaml):
  - RCE estimate        — bigger opportunity ranks higher
  - Source confidence   — cross-referenced leads rank higher
  - Follow-up timing    — overdue follow-ups jump the queue
  - Seasonal relevance  — gas in winter, electric in summer
  - Lead freshness      — new leads get a small boost

Usage:
    python -m prioritizer.urgency_agent
    python -m prioritizer.urgency_agent --input output/qualified_leads_2026-05-04.json
"""

import argparse
import csv
import json
import os
import yaml
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional

CONFIG_PATH = "config/agent_config.yaml"
OUTPUT_DIR = "output"


@dataclass
class ScoredLead:
    company_name: str
    phone: str
    location: str
    industry: str
    rce_estimate: float
    confidence: str          # HIGH / MEDIUM / LOW (from cross-referencing)
    source_count: int
    urgency_score: float
    urgency_breakdown: dict
    reasoning: str
    next_action: str
    last_contacted: str = ""
    days_since_contact: Optional[int] = None
    seasonal_flag: str = ""


def _load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def _days_since(date_str: str) -> Optional[int]:
    if not date_str:
        return None
    try:
        last = datetime.fromisoformat(date_str).date()
        return (date.today() - last).days
    except ValueError:
        return None


def _seasonal_flag(config: dict) -> str:
    month = date.today().month
    gas_months = config["seasons"]["gas_peak_months"]
    electric_months = config["seasons"]["electric_peak_months"]
    if month in gas_months:
        return "GAS"
    if month in electric_months:
        return "ELECTRIC"
    return "NEUTRAL"


def _score_lead(lead: dict, config: dict, season: str) -> ScoredLead:
    weights = config["urgency"]
    qual = config["qualification"]

    rce = float(lead.get("rce_estimate", lead.get("estimated_rce", 0)) or 0)
    source_count = int(lead.get("source_count", 1))
    confidence = lead.get("confidence", "LOW")
    last_contacted = lead.get("last_contacted", "")
    days_since = _days_since(last_contacted)
    followup_threshold = weights["followup_days_threshold"]

    # ── RCE score (0–100) ───────────────────────────────────────────────────
    sweet_min = qual["sweet_spot_min"]
    sweet_max = qual["sweet_spot_max"]
    if sweet_min <= rce <= sweet_max:
        rce_score = 100.0
    elif rce > sweet_max:
        # Large accounts are good but not the priority sweet spot
        rce_score = 75.0
    elif rce >= qual["min_rce"]:
        # Scale linearly from min_rce (0) to sweet_spot_min (100)
        rce_score = ((rce - qual["min_rce"]) / (sweet_min - qual["min_rce"])) * 80
    else:
        rce_score = 0.0

    # ── Source confidence score (0–100) ────────────────────────────────────
    confidence_map = {"HIGH": 100, "MEDIUM": 60, "LOW": 25}
    confidence_score = confidence_map.get(confidence, 25)
    # Extra boost per additional confirming source
    confidence_score = min(100, confidence_score + (source_count - 1) * 10)

    # ── Follow-up timing score (0–100) ─────────────────────────────────────
    if days_since is None:
        # Never contacted — treat as fresh cold lead
        followup_score = 50.0
    elif days_since >= followup_threshold:
        # Overdue — max urgency
        followup_score = 100.0
    elif days_since == 0:
        # Just contacted today — don't call again yet
        followup_score = 0.0
    else:
        followup_score = (days_since / followup_threshold) * 100

    # ── Seasonal score (0–100) ─────────────────────────────────────────────
    industry_lower = (lead.get("industry", "")).lower()
    is_gas_industry = any(w in industry_lower for w in ["manufactur", "food", "laundry", "steel", "metal"])
    is_electric_industry = any(w in industry_lower for w in ["warehouse", "storage", "retail", "gym", "fitness"])

    if season == "GAS" and is_gas_industry:
        seasonal_score = 100.0
    elif season == "ELECTRIC" and is_electric_industry:
        seasonal_score = 100.0
    elif season == "NEUTRAL":
        seasonal_score = 50.0
    else:
        seasonal_score = 30.0

    # ── Freshness score (0–100) ────────────────────────────────────────────
    # Leads never contacted get a small bump; stale uncontacted leads fade
    if days_since is None:
        freshness_score = 70.0
    else:
        freshness_score = max(0.0, 100.0 - (days_since * 2))

    # ── Weighted total ─────────────────────────────────────────────────────
    total_weight = (
        weights["rce_weight"]
        + weights["followup_overdue_weight"]
        + weights["seasonal_weight"]
        + weights["lead_freshness_weight"]
    )
    urgency_score = (
        rce_score          * weights["rce_weight"]
        + confidence_score * weights["followup_overdue_weight"]
        + seasonal_score   * weights["seasonal_weight"]
        + freshness_score  * weights["lead_freshness_weight"]
    ) / total_weight

    # ── Human-readable reasoning ───────────────────────────────────────────
    reasons = []
    if sweet_min <= rce <= sweet_max:
        reasons.append(f"Sweet spot RCE (~{rce:.0f})")
    elif rce > sweet_max:
        reasons.append(f"Large account (~{rce:.0f} RCE)")
    if confidence == "HIGH":
        reasons.append(f"Confirmed by {source_count} sources")
    if days_since is not None and days_since >= followup_threshold:
        reasons.append(f"Follow-up overdue ({days_since}d)")
    if season != "NEUTRAL" and seasonal_score == 100:
        reasons.append(f"Peak {season.lower()} season")
    reasoning = " | ".join(reasons) if reasons else "Qualified lead"

    return ScoredLead(
        company_name=lead.get("company_name", "Unknown"),
        phone=lead.get("phone", ""),
        location=lead.get("location", ""),
        industry=lead.get("industry", ""),
        rce_estimate=rce,
        confidence=confidence,
        source_count=source_count,
        urgency_score=round(urgency_score, 1),
        urgency_breakdown={
            "rce": round(rce_score, 1),
            "confidence": round(confidence_score, 1),
            "followup": round(followup_score, 1),
            "seasonal": round(seasonal_score, 1),
            "freshness": round(freshness_score, 1),
        },
        reasoning=reasoning,
        next_action=lead.get("next_action", "call"),
        last_contacted=last_contacted,
        days_since_contact=days_since,
        seasonal_flag=season,
    )


def prioritize(qualified_leads: List[dict]) -> List[ScoredLead]:
    config = _load_config()
    season = _seasonal_flag(config)
    print(f"\n=== Agent 3: Prioritizer ===")
    print(f"Season mode: {season} | Scoring {len(qualified_leads)} qualified leads...\n")

    scored = [_score_lead(lead, config, season) for lead in qualified_leads]
    scored.sort(key=lambda x: x.urgency_score, reverse=True)
    return scored


def save_call_sheet(scored_leads: List[ScoredLead]) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(OUTPUT_DIR, f"call_sheet_{date_str}.csv")

    fieldnames = [
        "rank", "urgency_score", "company_name", "phone", "location",
        "industry", "rce_estimate", "confidence", "source_count",
        "reasoning", "next_action", "last_contacted", "days_since_contact",
        "seasonal_flag",
    ]

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rank, lead in enumerate(scored_leads, start=1):
            writer.writerow({
                "rank": rank,
                "urgency_score": lead.urgency_score,
                "company_name": lead.company_name,
                "phone": lead.phone,
                "location": lead.location,
                "industry": lead.industry,
                "rce_estimate": lead.rce_estimate,
                "confidence": lead.confidence,
                "source_count": lead.source_count,
                "reasoning": lead.reasoning,
                "next_action": lead.next_action,
                "last_contacted": lead.last_contacted,
                "days_since_contact": lead.days_since_contact or "",
                "seasonal_flag": lead.seasonal_flag,
            })

    return path


def print_call_sheet(scored_leads: List[ScoredLead], top_n: int = 20):
    print("=" * 70)
    print(f"YOUR CALL SHEET — Top {min(top_n, len(scored_leads))} leads for today")
    print("=" * 70)
    print(f"{'#':<4} {'Score':<7} {'Company':<28} {'RCE':>6} {'Conf':<8} Why")
    print("-" * 70)
    for rank, lead in enumerate(scored_leads[:top_n], start=1):
        print(
            f"{rank:<4} {lead.urgency_score:<7} {lead.company_name[:27]:<28} "
            f"~{lead.rce_estimate:>4.0f}  {lead.confidence:<8} {lead.reasoning}"
        )
        if lead.phone:
            print(f"     {'':7} {lead.phone}")
    print()


def load_qualified_leads(path: str) -> List[dict]:
    with open(path, "r") as f:
        data = json.load(f)
    # Accept both a bare list and {"leads": [...]} format
    if isinstance(data, list):
        return data
    return data.get("leads", [])


def _find_latest_qualified() -> Optional[str]:
    if not os.path.exists(OUTPUT_DIR):
        return None
    files = sorted(
        f for f in os.listdir(OUTPUT_DIR) if f.startswith("qualified_leads_")
    )
    return os.path.join(OUTPUT_DIR, files[-1]) if files else None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 3: Lead Prioritizer")
    parser.add_argument("--input", help="Path to qualified_leads JSON file")
    parser.add_argument("--top", type=int, default=20, help="How many leads to show")
    args = parser.parse_args()

    input_path = args.input or _find_latest_qualified()

    if not input_path:
        print("No qualified leads file found. Run Agent 2 first.")
        print("Or pass a file: python -m prioritizer.urgency_agent --input output/qualified_leads_2026-05-04.json")
        raise SystemExit(1)

    print(f"Loading leads from: {input_path}")
    leads = load_qualified_leads(input_path)
    scored = prioritize(leads)
    print_call_sheet(scored, top_n=args.top)
    path = save_call_sheet(scored)
    print(f"Full call sheet saved to: {path}")
    print("Open it in Excel or Google Sheets — sorted best lead first.")
