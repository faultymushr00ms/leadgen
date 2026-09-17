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
    Returns 1, 2, or 3 based on field-tested industry tiers.
    Tier 1 = bread and butter sweet spot leads — qualify first.
    """
    industry_lower = industry.lower()
    tier1_keywords = [
        "gas station", "convenience", "restaurant", "diner", "asian",
        "hotel", "motel", "car wash", "laundromat", "laundry",
    ]
    tier3_keywords = [
        "retail", "office", "storage", "vacant",
    ]
    if any(k in industry_lower for k in tier1_keywords):
        return 1
    if any(k in industry_lower for k in tier3_keywords):
        return 3
    return 2


def _use_ai_qualifier() -> bool:
    """Returns True if the AI (Claude) qualifier should be used."""
    return bool(os.getenv("ANTHROPIC_API_KEY", "").strip())


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

def _build_prospect(raw: dict) -> dict:
    return {
        "company_name":  raw.get("company_name", "Unknown"),
        "industry":      raw.get("industry", ""),
        "estimated_rce": raw.get("estimated_rce", 0),
        "location":      raw.get("location", f"{raw.get('city', '')}, OH"),
        "phone":         raw.get("phone", ""),
        "source_count":  raw.get("source_count", 1),
        "confidence":    raw.get("confidence", "LOW"),
        "known_info":    raw.get("known_info", ""),
        "last_contacted": raw.get("last_contacted", ""),
    }


def run_agent2_rules(raw_leads: list, limit: int) -> list:
    """Free qualifier — uses field-tested rules, no API required."""
    from training.rule_qualifier import batch_qualify

    sorted_leads = sorted(raw_leads, key=lambda l: _tier_rank(l.get("industry", "")))
    candidates = sorted_leads[:limit] if limit else sorted_leads
    prospects = [_build_prospect(r) for r in candidates]

    print(f"\n[Agent 2 — Rules] Qualifying {len(prospects)} leads...")
    qualified, rejected = batch_qualify(prospects)
    print(f"[Agent 2 — Rules] {len(qualified)} qualified | {rejected} rejected.\n")
    return qualified


def run_agent2_ai(raw_leads: list, limit: int) -> list:
    """
    ★ SUPERSTAR MODE ★
    AI qualifier powered by Claude — sharper reasoning, learns from your
    call history. Activates automatically when ANTHROPIC_API_KEY is in .env.
    """
    from training.training_harness import AgentTrainingHarness

    harness = AgentTrainingHarness()
    sorted_leads = sorted(raw_leads, key=lambda l: _tier_rank(l.get("industry", "")))
    candidates = sorted_leads[:limit] if limit else sorted_leads

    print(f"\n[Agent 2 — ★ AI] Qualifying {len(candidates)} leads with Claude...")
    qualified = []
    rejected_count = 0

    for i, raw in enumerate(candidates, start=1):
        prospect = _build_prospect(raw)
        print(f"  [{i}/{len(candidates)}] {prospect['company_name'][:40]}...",
              end=" ", flush=True)
        try:
            result = harness.qualify_lead(prospect, conversation_history=[])
        except Exception as e:
            print(f"ERROR: {e}")
            continue

        if result.get("is_qualified"):
            qualified.append({**prospect, **result})
            print(f"QUALIFIED (~{result.get('rce_estimate', '?')} RCE)")
        else:
            rejected_count += 1
            print("rejected")

        time.sleep(0.5)

    print(f"\n[Agent 2 — ★ AI] {len(qualified)} qualified | {rejected_count} rejected.\n")
    return qualified


def run_agent2(raw_leads: list, limit: int) -> list:
    """Routes to AI or rule-based qualifier depending on what's available."""
    if _use_ai_qualifier():
        print("[Agent 2] ANTHROPIC_API_KEY detected — using ★ AI qualifier.")
        qualified = run_agent2_ai(raw_leads, limit)
    else:
        print("[Agent 2] No API key — using rule-based qualifier (free).")
        print("          To upgrade: add ANTHROPIC_API_KEY to your .env file.\n")
        qualified = run_agent2_rules(raw_leads, limit)

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
