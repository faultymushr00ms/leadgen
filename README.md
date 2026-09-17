# Ohio Lead Gen Bot

A three-agent pipeline that finds, qualifies, and prioritizes commercial energy leads so you can spend your time on the phone with the right people — not hunting for them.

---

## What This Does

Every day the system runs through three stages automatically:

1. **Scrape** — Pull Ohio business listings from public sources
2. **Qualify** — Score each business by estimated energy usage (RCE)
3. **Prioritize** — Rank qualified leads by urgency so you know exactly who to call first

You end up with a sorted call sheet. Top of the list = highest value, most time-sensitive. Work it top to bottom.

---

## The Sweet Spot

This bot is calibrated for natural gas and electricity sales.

| RCE Range | What It Means | Action |
|---|---|---|
| Under 5 | Too small | Auto-rejected |
| 5 – 49 | Warm, not ideal | Kept, lower priority |
| **50 – 100** | **Sweet spot** | **Top of your call sheet** |
| 100+ | Large account | Qualified, flagged for special handling |

RCE = Residential Commercial Equivalent. One RCE ≈ the energy usage of one average home.

---

## The Three Agents

### Agent 1: Scraper
**File:** `scraper/ohio_scraper.py` *(to be built)*

Pulls business listings from:
- Ohio Secretary of State business registry
- Google Maps / Places API (by industry + location)
- Optionally: county auditor records, Yelp, LinkedIn

Outputs raw business data: name, address, phone, industry type, business size signals.

### Agent 2: Qualifier
**File:** `training/training_harness.py` *(exists)*

Takes the raw list and asks: *Is this worth calling?*

- Estimates RCE based on business type, size, and industry
- Rejects anything under 5 RCE immediately
- Flags sweet spot leads (50-100 RCE) for priority handling
- Can be trained on past calls — the more examples you feed it, the smarter it gets

### Agent 3: Prioritizer
**File:** `prioritizer/urgency_agent.py` *(to be built)*

Takes the qualified list and asks: *Who do I call first, today?*

Scores each lead on:
- **Opportunity size** — higher RCE estimate = higher score
- **Follow-up timing** — how long since last contact
- **Season** — winter raises gas urgency, summer raises electric urgency
- **Lead freshness** — new business vs. cold lead vs. warm follow-up
- **Business signals** — recent growth, new location, industry type

Outputs your daily call sheet ranked 1 to N.

---

## Output: Your Daily Call Sheet

A simple file (CSV or printable list) with:

```
Rank | Company          | Phone        | Est. RCE | Why Now
-----|------------------|--------------|----------|---------------------------
1    | Acme Warehouse   | 614-555-0101 | ~75 RCE  | Follow-up due, sweet spot
2    | River Logistics  | 513-555-0188 | ~60 RCE  | Cold, high industry match
3    | Glenbrook Diner  | 740-555-0234 | ~12 RCE  | Warm, check in
```

---

## Project Structure

```
leadgen/
├── README.md                    <- You are here
├── config/
│   └── agent_config.yaml        <- RCE thresholds, season weights, rules
├── scraper/
│   └── ohio_scraper.py          <- Agent 1 (to build)
├── training/
│   └── training_harness.py      <- Agent 2 (exists)
├── prioritizer/
│   └── urgency_agent.py         <- Agent 3 (to build)
├── output/
│   └── call_sheet.csv           <- Generated daily (gitignored)
├── models/
│   └── trained_agent.json       <- Saved agent state (gitignored)
├── .env.example                 <- Shows what keys you need
└── requirements.txt             <- Python dependencies
```

---

## Setup

### 1. Clone and install dependencies
```bash
git clone https://github.com/faultymushr00ms/leadgen.git
cd leadgen
pip install -r requirements.txt
```

### 2. Set your API key
Copy `.env.example` to `.env` and fill in your Anthropic API key:
```bash
cp .env.example .env
```

Then open `.env` and add:
```
ANTHROPIC_API_KEY=your-key-here
```

### 3. Configure the agent
Open `config/agent_config.yaml` and review the RCE thresholds and rules.
Defaults are set for Ohio commercial gas/electric — adjust if needed.

### 4. Run the pipeline
```bash
python run_pipeline.py
```

Your call sheet will appear in `output/call_sheet.csv`.

---

## Training the Qualifier

The more real call outcomes you feed Agent 2, the smarter it gets.

After a call, log what happened:
```python
from training.training_harness import AgentTrainingHarness, TrainingExample

harness = AgentTrainingHarness()

harness.add_training_example(TrainingExample(
    prospect_data={"company_name": "Acme Warehouse", "industry": "Warehouse", "estimated_rce": 72},
    conversation=[],           # transcript if you have it
    is_qualified=True,         # did this turn into a real lead?
    feedback="Owner confirmed 3 locations, all electric",
    rce_score=72.0
))
```

After 5+ examples, the qualifier starts making noticeably better predictions.

---

## What's Built vs. What's Next

| Component | Status |
|---|---|
| Agent 2: Qualifier | Done |
| `agent_config.yaml` | Needs to be created |
| `requirements.txt` | Needs to be created |
| `.env.example` | Needs to be created |
| Agent 1: Scraper | To build |
| Agent 3: Prioritizer | To build |
| `run_pipeline.py` | To build |
| Daily output / call sheet | To build |

---

## Compliance Note

Ohio Secretary of State data is public record. Google Maps API usage requires a Google Cloud account and follows their terms of service. Do not call numbers on the national Do Not Call registry for unsolicited sales. Always identify yourself and your company at the start of a call.

---

## Stack

- **Language:** Python 3.10+
- **AI:** Anthropic Claude (via `anthropic` SDK)
- **Scraping:** `requests`, `beautifulsoup4`, optionally Google Maps API
- **Config:** YAML
- **Output:** CSV (upgradeable to a simple web dashboard later)
