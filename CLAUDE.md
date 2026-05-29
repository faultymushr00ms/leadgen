# FORGE — Sales Intelligence CRM

## Project Summary

FORGE is a personal B2B energy sales CRM and territory intelligence suite built for a commercial energy broker in Ohio. It combines a multi-agent lead generation pipeline with a real-time market intelligence cockpit ("Hotspots") for tracking Ohio electric aggregation programs, municipal utilities, and electric cooperatives.

**Demo deadline: June 6, 2026 — AGM pitch for AI Integration Specialist role.**

## Stack

- **Backend**: Python 3, Flask, Jinja2
- **Frontend**: Bootstrap 5.3, Bootstrap Icons 1.11, Leaflet.js (CDN)
- **Data**: JSON files per region in `data/regions/`, CSV call sheets in `output/`
- **No database** — all persistence is flat-file JSON/CSV
- **Run**: `python app.py` → http://localhost:5000

## Design System

**Dark theme. No light-mode. Never introduce Bootstrap light-theme classes.**

CSS variables (defined in `templates/base.html`):
```
--forge-orange: #e8611a   (primary accent, CTAs, selected state)
--forge-gold:   #ffb300   (secondary accent, quotes/hooks)
--forge-navy:   #0A1628   (sidebar)
--forge-dark:   #0f1117   (page background)
--forge-panel:  #1a1d27   (card/panel background)
--forge-border: #2a2d3a   (borders, dividers)
--forge-muted:  #6b7280   (secondary text)
```

Badge classes: `.heat-hot`, `.heat-pain`, `.heat-warm`, `.heat-normal`, `.heat-cooling`
Layout classes: `.panel`, `.forge-table`, `.btn-forge`, `.btn-ghost`, `.dark-input`, `.scrollable`

## Key Files

```
app.py                          # Flask app, all routes and API endpoints
templates/
  base.html                     # Dark sidebar layout, CDN includes, CSS vars
  hotspots.html                 # Zone intelligence cockpit (most complex)
  dashboard.html                # Lead call sheet table
  lead.html                     # Lead detail / battlecard
  goals.html                    # Quota tracking
  settings.html                 # Config status
data/
  regions/                      # 18 JSON files, 251 zones total
    ohio_electric_cooperatives.json   # 24 co-ops (aggregationStatus: electric_cooperative)
    ohio_municipal_utilities.json     # 47 municipal utilities (aggregationStatus: municipal_utility)
    cleveland_cuyahoga.json           # NOPEC/Illuminating Co zones
    nopec_cuyahoga_suburbs.json       # 23 additional Cuyahoga NOPEC communities
    nopec_lorain_summit_portage.json  # 21 NOPEC communities (Lorain/Summit/Portage)
    lake_geauga_nopec.json            # Lake/Geauga NOPEC zones
    akron_summit_medina.json          # Akron/Green (Dynegy), Medina County, Stark
    youngstown_warren.json            # Trumbull/Mahoning (pain_hit)
    columbus_aep.json                 # Columbus SOPEC + AEP core zones
    sopec_columbus_suburbs.json       # 14 SOPEC member communities
    dayton_sw_ohio.json               # Dayton/AES Ohio (pain_coming — extreme)
    dayton_aes_suburbs.json           # 10 AES Ohio suburbs
    cincinnati_duke.json              # Cincinnati/Duke aggregation zones
    cincinnati_duke_suburbs.json      # 10 Duke Energy suburbs
    toledo_lucas_noac.json            # NOAC (13 Toledo-area communities)
    ne_ohio_firstenergy.json          # NE Ohio FirstEnergy markets
    nw_central_ohio.json              # Findlay, Lima, Tiffin, etc.
    eastern_ohio_aep.json             # SE Ohio AEP markets
    remaining_ohio_markets.json       # Misc Ohio markets
output/
  call_sheet_*.csv              # Generated lead call sheets (NEVER COMMIT)
  qualified_leads_*.json        # Generated lead files (NEVER COMMIT)
```

## Zone Data Schema

Every zone JSON record:
```json
{
  "name": "Zone Name",
  "region": "Region Label",
  "utility": "Utility Name",
  "aggregationStatus": "confirmed_active_aggregation | municipal_utility | electric_cooperative | no_aggregation_verified | address_dependent",
  "currentRate": 10.01,
  "previousRate": 9.08,
  "rateChange": 10.2,
  "supplier": "Supplier Name or null",
  "termStart": "2026-06-01 or null",
  "termEnd": "2027-06-01 or null",
  "status": "pain_hit | pain_coming | stable | transition | verify",
  "confidence": "high | medium | low",
  "takeaway": "One-sentence sales insight",
  "hook": "Exact opener to say when they pick up",
  "futureUse": "aggregation | municipal_blacklist | price_to_compare_analysis | address_check",
  "notes": "Address exceptions, data caveats",
  "lastVerified": "2026-05-01",
  "sourceUrl": "https://... or null"
}
```

`_source_file` is injected at runtime by `_load_zones()` — never write it to the JSON files.

## API Routes

```
GET  /api/zones                              # All zones (loaded from all region files)
GET  /api/regions                            # List of region file names (without .json)
PUT  /api/zones/<region_file>/<zone_name>    # Update existing zone
POST /api/zones/<region_file>               # Add new zone
DELETE /api/zones/<region_file>/<zone_name>  # Delete zone
```

## Ohio Energy Market Facts

- **Retail electric choice**: Ohio allows competitive supply for commercial/industrial accounts served by IOUs. Municipal utilities and electric cooperatives are **exempt** — cannot sell competitive electric supply to them.
- **IOUs**: Ohio Edison, The Illuminating Company, Toledo Edison (all FirstEnergy), AEP Ohio, AES Ohio (Dayton P&L), Duke Energy Ohio
- **NOPEC**: Serves 235+ NE Ohio communities. Rate: 8.999¢ → 9.999¢ June 1, 2026 (+11%). Critical pain story right now.
- **SOPEC**: ~14 central Ohio/AEP communities. Green rate: 9.756¢ → 11.162¢ June 2026 (+14.4%). Extreme pain story.
- **NOAC**: 13 Toledo-area communities (Toledo Edison). Rate: 9.75¢ through ~June 2027. Stable.
- **Dayton/AES Ohio**: 8.71¢ → 10.691¢ June 2026 (+22.7%). EXTREME pain story, highest urgency.
- **Electric co-ops**: All 25 Ohio co-ops are served by Buckeye Power Inc. All are exempt from retail choice. Use `futureUse: "municipal_blacklist"`.
- **Sales minimum**: 5 RCE (residential customer equivalents) per account. Quota: 100 RCE/month baseline, 600 RCE per 4-month period for bonus.
- **LMRE critical note**: Lorain-Medina Rural Electric (LMRE) co-op territory does NOT participate in NOPEC, even though LMRE overlaps with NOPEC's geographic footprint.

## Security Rules (HARD STOPS)

1. **NEVER commit** `output/*.csv` or `output/*.json` — these contain real lead/call data
2. **NEVER commit** `.env` or any file containing API keys
3. **NEVER include** DNC (do-not-call) records anywhere in the codebase or output
4. **NEVER store or use** third-party service credentials (Salesforce, LinkedIn, etc.)
5. **data/regions/*.json** files ARE safe to commit — they contain publicly sourced market intelligence only

## Branch

All development: `claude/review-project-architecture-buf2P` on `faultymushr00ms/leadgen`

## Pending / Roadmap

- [ ] Leaflet.js map overlay layer (utility territory boundaries)
- [ ] Monthly rate refresh pipeline with `sourceUrl` / `lastVerified` / review queue
- [ ] Address-level utility lookup module (given address → predict IOU vs. co-op vs. municipal)
- [ ] Goals page: wire `log_close` form to persist RCE data (currently logs to console only)
- [ ] `verify` status zones: need field research to confirm aggregation status
- [ ] Hotspots: add "Export filtered zones as PDF battlecard packet" feature
- [ ] Pipeline: reconnect scraper with Google Maps API for lead enrichment
- [ ] Settings page: real API key validation (currently just checks if env var set)
