"""
Rule-Based Qualifier — Free, no API key required.
Uses field-tested industry knowledge to estimate RCE and qualify leads.

This is the default qualifier. It runs instantly and costs nothing.
As you learn more from the field, update config/agent_config.yaml —
no code changes needed.

The AI qualifier (training_harness.py) is the upgrade path. It activates
automatically when ANTHROPIC_API_KEY is set in your .env file.
"""

import yaml
from typing import Dict, Any, Tuple

CONFIG_PATH = "config/agent_config.yaml"

# Base RCE estimates by industry type, drawn from field experience.
# Format: (rce_low, rce_high, energy_type)
# energy_type: "gas" | "electric" | "both"
INDUSTRY_RCE_TABLE = {
    # Tier 1 — bread and butter
    "gas station":                  (10, 25, "both"),
    "gas station with car wash":    (20, 45, "both"),
    "convenience store":            (8,  20, "both"),
    "small restaurant":             (8,  20, "gas"),
    "restaurant":                   (8,  25, "gas"),
    "diner":                        (10, 22, "gas"),
    "asian restaurant":             (15, 35, "gas"),   # hot pot / pho skew high
    "chinese restaurant":           (12, 30, "gas"),
    "vietnamese restaurant":        (15, 35, "gas"),   # pho
    "hotel":                        (20, 60, "both"),
    "motel":                        (15, 40, "both"),
    "car wash":                     (20, 50, "both"),
    "laundromat":                   (30, 60, "gas"),
    "coin laundry":                 (30, 60, "gas"),
    "dry cleaning":                 (15, 35, "gas"),

    # Tier 2 — often qualify
    "fast food":                    (10, 25, "both"),
    "bakery":                       (10, 28, "gas"),
    "cafe":                         (8,  20, "both"),
    "coffee shop":                  (8,  18, "both"),
    "bar":                          (8,  20, "both"),
    "tavern":                       (8,  20, "both"),
    "auto repair":                  (8,  20, "both"),
    "body shop":                    (10, 22, "both"),
    "gym":                          (15, 35, "electric"),
    "fitness center":               (15, 35, "electric"),
    "grocery":                      (15, 35, "both"),
    "supermarket":                  (20, 50, "both"),
    "dental":                       (8,  18, "both"),
    "medical":                      (8,  20, "both"),
    "clinic":                       (8,  20, "both"),

    # Tier 2 — warehouses: look bigger than they are, but ~5 RCE is the target
    # Others willing to skip these — that's our edge
    "warehouse":                    (4,  8,  "both"),   # active ops: ~5 RCE, sweet spot
    "distribution":                 (5,  10, "both"),
    "industrial":                   (5,  15, "both"),

    # Tier 3 — variable
    "retail":                       (4,  15, "electric"),
    "office":                       (4,  12, "both"),
    "light manufacturing":          (10, 40, "both"),
    "manufacturing":                (10, 60, "both"),   # wide range — flag large ones

    # Low — storage only or inactive (not the same as active warehouse)
    "storage":                      (2,   5, "electric"),  # storage-only = minimal use
    "steel":                        (80, 400, "both"),     # usually big corp — flag
}


def _load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def _match_industry(industry: str) -> Tuple[float, float, str]:
    """
    Match a raw industry string to the RCE table.
    Returns (rce_low, rce_high, energy_type).
    Falls back to a conservative estimate if no match found.
    """
    industry_lower = industry.lower().strip()

    # Try exact match first
    if industry_lower in INDUSTRY_RCE_TABLE:
        return INDUSTRY_RCE_TABLE[industry_lower]

    # Try partial match — longest matching key wins (most specific)
    best_key = ""
    for key in INDUSTRY_RCE_TABLE:
        if key in industry_lower and len(key) > len(best_key):
            best_key = key

    if best_key:
        return INDUSTRY_RCE_TABLE[best_key]

    # Unknown industry — conservative middle estimate
    return (5, 20, "both")


def _apply_nuance(rce_mid: float, known_info: str, config: dict) -> float:
    """
    Apply keyword-based boosts and reductions from config.
    These encode field observations that a simple lookup table misses.
    """
    info_lower = (known_info or "").lower()
    adjusted = rce_mid

    for rule in config.get("nuance_rules", {}).get("rce_boosters", []):
        if rule["keyword"].lower() in info_lower:
            adjusted += rule["boost"]

    for rule in config.get("nuance_rules", {}).get("rce_reducers", []):
        if rule["keyword"].lower() in info_lower:
            adjusted -= rule["reduce"]

    return max(0, adjusted)


def _check_red_flags(known_info: str, config: dict) -> str | None:
    """
    Returns a rejection reason if a hard red flag is found, else None.
    """
    info_lower = (known_info or "").lower()

    # Contract length check — electricity contracts > 2 years = move on
    contract_triggers = ["2 year contract", "24 month contract", "3 year contract",
                         "36 month", "locked in", "long-term contract"]
    for trigger in contract_triggers:
        if trigger in info_lower:
            return f"Contract flag: '{trigger}' detected"

    # Config rejection triggers
    for trigger in config.get("rejection_triggers", []):
        trigger_words = trigger.lower().split()
        if any(word in info_lower for word in trigger_words if len(word) > 4):
            return f"Rejection trigger: {trigger}"

    return None


def _is_skip_industry(industry: str, config: dict) -> bool:
    """
    Returns True only for truly dead leads — vacant/empty/storage-only.
    Active warehouses are NOT skipped even though they look big.
    Large corporate accounts are flagged, not skipped.
    """
    industry_lower = industry.lower()
    hard_skip_keywords = ["vacant", "empty", "storage only", "inactive"]
    return any(k in industry_lower for k in hard_skip_keywords)


def qualify_lead(prospect_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score and qualify a single lead using rules only — no API call.

    Returns the same JSON shape as the AI qualifier so the pipeline
    can swap between them without any other changes.
    """
    config = _load_config()
    qual = config["qualification"]

    industry = prospect_data.get("industry", "")
    known_info = prospect_data.get("known_info", "")
    company = prospect_data.get("company_name", "Unknown")

    # ── Hard skip: industry is explicitly not our market ──────────────────
    if _is_skip_industry(industry, config):
        return {
            "is_qualified": False,
            "rce_estimate": 0,
            "confidence": 0,
            "reasoning": f"Industry '{industry}' is in skip list — not our market",
            "next_action": "reject",
            "estimated_value": "",
        }

    # ── Hard red flags ────────────────────────────────────────────────────
    flag = _check_red_flags(known_info, config)
    if flag:
        return {
            "is_qualified": False,
            "rce_estimate": 0,
            "confidence": 0,
            "reasoning": flag,
            "next_action": "reject",
            "estimated_value": "",
        }

    # ── RCE estimation ────────────────────────────────────────────────────
    rce_low, rce_high, energy_type = _match_industry(industry)
    rce_mid = (rce_low + rce_high) / 2
    rce_adjusted = _apply_nuance(rce_mid, known_info, config)

    # ── Qualification decision ────────────────────────────────────────────
    min_rce = qual["min_rce"]
    sweet_min = qual["sweet_spot_min"]
    sweet_max = qual["sweet_spot_max"]
    max_rce = qual["max_rce"]

    if rce_adjusted < min_rce:
        return {
            "is_qualified": False,
            "rce_estimate": round(rce_adjusted, 1),
            "confidence": 30,
            "reasoning": f"Estimated {rce_adjusted:.0f} RCE — below minimum {min_rce}",
            "next_action": "reject",
            "estimated_value": "",
        }

    if rce_adjusted > max_rce:
        # Don't hard reject — flag for corporate approach
        # Willing to play the corporate game others won't
        return {
            "is_qualified": True,
            "rce_estimate": round(rce_adjusted, 1),
            "confidence": 40,
            "reasoning": f"Large account (~{rce_adjusted:.0f} RCE) — requires corporate approach",
            "next_action": "corporate_approach",
            "estimated_value": f"~${round(rce_adjusted * 4)}/month if won",
        }

    # It qualifies — determine how good it is
    in_sweet_spot = sweet_min <= rce_adjusted <= sweet_max

    if in_sweet_spot:
        confidence = 75
        label = "Sweet spot"
        next_action = "call"
    elif rce_adjusted < sweet_min:
        confidence = 50
        label = "Below sweet spot — warm lead"
        next_action = "call"
    else:
        confidence = 65
        label = "Above sweet spot — larger account"
        next_action = "call"

    # Source confidence boosts certainty
    source_count = prospect_data.get("source_count", 1)
    confidence = min(95, confidence + (source_count - 1) * 8)

    # Rough value estimate (monthly)
    monthly_savings_per_rce = 4  # conservative $4/RCE/month savings estimate
    estimated_monthly = round(rce_adjusted * monthly_savings_per_rce)

    return {
        "is_qualified": True,
        "rce_estimate": round(rce_adjusted, 1),
        "confidence": confidence,
        "reasoning": f"{label} | ~{rce_adjusted:.0f} RCE | {energy_type} customer | {industry}",
        "next_action": next_action,
        "estimated_value": f"~${estimated_monthly}/month savings potential",
    }


def batch_qualify(leads: list) -> Tuple[list, int]:
    """
    Qualify a list of prospect dicts. Returns (qualified_list, rejected_count).
    Used by run_pipeline.py.
    """
    qualified = []
    rejected = 0
    for lead in leads:
        result = qualify_lead(lead)
        if result["is_qualified"]:
            qualified.append({**lead, **result})
        else:
            rejected += 1
    return qualified, rejected
