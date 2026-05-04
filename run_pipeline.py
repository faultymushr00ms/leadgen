"""
Ohio Lead Gen Bot — Full Pipeline
Runs all three agents in sequence and delivers your daily call sheet.

Usage:
    python run_pipeline.py                         # Full run
    python run_pipeline.py --limit 20              # Test with 20 leads (saves API calls)
    python run_pipeline.py --skip-scrape           # Reuse today's existing raw leads
    python run_pipeline.py --skip-scrape --limit 5 # Quick test of Agent 2 + 3 only
"""

import argparse
import json
import os
import time
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

DATE_STR = datetime.now().strftime("%Y-%m-%d")
OUTPUT_DIR = "output"
RAW_LEADS_FILE = os.path.join(OUTPUT_DIR, f"raw_leads_{DATE_STR}.json")
QUALIFIED_LEADS_FILE = os.path.join(OUTPUT_DIR, f"qualified_leads_{DATE_STR}.json")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _check_api_key():
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not key:
        print("\nERROR: ANTHROPIC_API_KEY is not set.")
        print("Steps to fix:")
        print("  1. Copy .env.example to .env")
        print("  2. Open .env and paste your key after ANTHROPIC_API_KEY=")
        print("  3. Run this script again.")
        raise SystemExit(1)


def _load_json(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def _save_json(data: dict, path: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _tier_rank(industry: str) -> int:
    """
    Returns 1, 2, or 3 based on industry energy tier from config.
    Tier 1 = highest energy users = qualify first.
    Unknown industries default to tier 2 so they still get a chance.
    """
    industry_lower = industry.lower()
    tier1_keywords = [
        "warehouse", "distribution", "manufactur", "laundry", "car wash",
        "cold storage", "refriger", "food service", "steel", "metal",
    ]
    tier3_keywords = [
        "small restaurant", "retail (single", "office (small",
    ]
    if any(k in industry_lower for k in tier1_keywords):
        return 1
    if any(k in industry_lower for k in tier3_keywords):
        return 3
    return 2


# ── Agent 1: Scrape ────────────────────────────────────────────────────────────

def run_agent1(skip: bool) -> list:
    if skip and os.path.exists(RAW_LEADS_FILE):
        print(f"[Agent 1] Skipping scrape — loading {RAW_LEADS_FILE}")
        data = _load_json(RAW_LEADS_FILE)
        leads = data.get("leads", [])
        print(f"[Agent 1] {len(leads)} leads loaded from file.\n")
        return leads

    from scraper.ohio_scraper import run_scraper, save_leads, print_summary
    raw_leads = run_scraper()
    path = save_leads(raw_leads)
    print_summary(raw_leads)
    print(f"[Agent 1] Saved to {path}\n")
    return [lead.__dict__ for lead in raw_leads]


# ── Agent 2: Qualify ───────────────────────────────────────────────────────────

def run_agent2(raw_leads: list, limit: int) -> list:
    from training.training_harness import AgentTrainingHarness

    print(f"\n[Agent 2] Qualifying leads with Claude...")
    harness = AgentTrainingHarness()

    # Sort by industry tier so the best candidates go first
    sorted_leads = sorted(raw_leads, key=lambda l: _tier_rank(l.get("industry", "")))

    # Apply limit after sorting so we always test on the best candidates
    candidates = sorted_leads[:limit] if limit else sorted_leads
    print(f"[Agent 2] Processing {len(candidates)} leads "
          f"({'limited' if limit else 'full run'})...\n")

    qualified = []
    rejected_count = 0

    for i, raw in enumerate(candidates, start=1):
        prospect = {
            "company_name": raw.get("company_name", "Unknown"),
            "industry":     raw.get("industry", ""),
            "estimated_rce": raw.get("estimated_rce", 0),
            "location":     raw.get("location", f"{raw.get('city', '')}, OH"),
            "known_info":   raw.get("known_info", f"Source confidence: {raw.get('confidence', 'LOW')}"),
        }

        print(f"  [{i}/{len(candidates)}] {prospect['company_name'][:40]}...", end=" ", flush=True)

        try:
            result = harness.qualify_lead(prospect, conversation_history=[])
        except Exception as e:
            print(f"ERROR: {e}")
            continue

        is_qualified = result.get("is_qualified", False)

        if is_qualified:
            qualified.append({
                **prospect,
                "rce_estimate":   result.get("rce_estimate", 0),
                "confidence":     raw.get("confidence", "LOW"),
                "source_count":   raw.get("source_count", 1),
                "phone":          raw.get("phone", ""),
                "reasoning":      result.get("reasoning", ""),
                "next_action":    result.get("next_action", "call"),
                "estimated_value": result.get("estimated_value", ""),
                "last_contacted": raw.get("last_contacted", ""),
            })
            rce = result.get("rce_estimate", "?")
            print(f"QUALIFIED (~{rce} RCE)")
        else:
            rejected_count += 1
            print("rejected")

        # Polite pause — avoids hammering the API and triggering rate limits
        time.sleep(0.5)

    print(f"\n[Agent 2] Done. {len(qualified)} qualified | {rejected_count} rejected.\n")

    _save_json({
        "qualified_at": datetime.now().isoformat(),
        "total_qualified": len(qualified),
        "leads": qualified,
    }, QUALIFIED_LEADS_FILE)
    print(f"[Agent 2] Saved to {QUALIFIED_LEADS_FILE}\n")

    return qualified


# ── Agent 3: Prioritize ────────────────────────────────────────────────────────

def run_agent3(qualified_leads: list, top_n: int) -> str:
    from prioritizer.urgency_agent import prioritize, save_call_sheet, print_call_sheet

    scored = prioritize(qualified_leads)
    print_call_sheet(scored, top_n=top_n)
    path = save_call_sheet(scored)
    print(f"[Agent 3] Call sheet saved to {path}")
    return path


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Ohio Lead Gen Bot — Full Pipeline")
    parser.add_argument(
        "--skip-scrape", action="store_true",
        help="Skip Agent 1 and reuse today's existing raw leads file.",
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Max leads to qualify (useful for testing — 0 means no limit).",
    )
    parser.add_argument(
        "--top", type=int, default=20,
        help="How many leads to show in the printed call sheet (default: 20).",
    )
    args = parser.parse_args()

    _check_api_key()

    start = datetime.now()
    print("\n" + "=" * 60)
    print("  OHIO LEAD GEN BOT")
    print(f"  {start.strftime('%A, %B %d %Y — %I:%M %p')}")
    print("=" * 60)

    # Agent 1
    raw_leads = run_agent1(skip=args.skip_scrape)
    if not raw_leads:
        print("No leads found from scraper. Check your sources and try again.")
        raise SystemExit(1)

    # Agent 2
    qualified = run_agent2(raw_leads, limit=args.limit)
    if not qualified:
        print("No leads qualified. Try running without --limit or check your config.")
        raise SystemExit(1)

    # Agent 3
    call_sheet_path = run_agent3(qualified, top_n=args.top)

    elapsed = (datetime.now() - start).seconds
    print("\n" + "=" * 60)
    print(f"  DONE in {elapsed}s")
    print(f"  {len(qualified)} qualified leads — call sheet at:")
    print(f"  {call_sheet_path}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
