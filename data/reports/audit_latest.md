# FORGE Daily Audit — 2026-10-27

**350 findings** | HIGH: 33  MEDIUM: 249  LOW: 68
Zones checked: 456 | Elapsed: 0.01s

Electric records in `data/regions`: 427 across 20 JSON files. Gas records in `data/gas`: 29 across 3 JSON files. The 13 checks read both directories.

Audit code: `scripts/daily_audit.py` at commit `89fc067` on `claude/review-project-architecture-buf2P` (the script that wrote the 2026-10-23 report). Run read-only against current `main` (`7d84e19`). Zone files were not modified. Open PR #11 (`cursor/daily-data-audit-d8f1`) was also run read-only against `main` and returned 482 issues across 427 electric zones, the same issue counts as that PR's 2026-10-23 baseline. Those totals are not used below. PR #11 assigns no HIGH/MEDIUM/LOW severity, uses different issue ids, and does not read `data/gas`, so it cannot be diffed against the published report.

## Comparison with 2026-10-23

| | 2026-10-23 | 2026-10-27 |
| --- | ---: | ---: |
| Zones checked | 327 | 456 |
| Findings | 456 | 350 |
| HIGH | 15 | 33 |
| MEDIUM | 296 | 249 |
| LOW | 145 | 68 |

- New: **119**
- Resolved: **225**
- Unchanged: **231** (HIGH 12, MEDIUM 161, LOW 58)
- Shared finding ids whose severity set changed: **0**

A finding id is `source_file::zone::check`. Unchanged means that id is in both reports. The day count inside the detail can move without making the finding new. `COPY_RATE_MISMATCH` on takeaway and hook shares one id.

The 2026-10-23 file on this branch (commit `ea64179`) records 327 zones and 456 findings, HIGH 15. That result is the first run described in commit `89fc067`, whose tree has 327 electric records in 19 region files. Current `main` already had 427 electric records in 20 files at `56fc295` (2026-10-23 08:54 EDT). `56fc295` is not an ancestor of `89fc067`. Of 319 record keys present in both trees, 174 differ in at least one of `currentRate`, `previousRate`, `supplier`, `termStart`, `termEnd`, `status`, `aggregationStatus`, `lastVerified`, and `utility`.

New and resolved are id differences between that published finding set and this scan of `main`. They are not a list of edits made on `main` after the audit.

- Of 119 new findings, 85 are on a record key that exists in the 327-zone tree and 34 are on a record key that does not: 28 in `ne_ohio_firstenergy`, 4 in `ne_ohio_gas`, 1 in `merged_confirmed`, and 1 in `remaining_ohio_markets`.
- Of 225 resolved findings, 214 are on a record key still present on `main` and 11 are on a record key absent from `main`: Springboro and Franklin (`dayton_aes_suburbs`), Grove City Area / Southwest Franklin County, Medina County (Rural Unincorporated), Lakeview / Indian Lake Area (`remaining_ohio_markets`), Westerville (`sopec_columbus_suburbs`), Jerusalem Township (`toledo_lucas_noac`).

### Findings by check

| Check | Count |
| --- | ---: |
| STALE_60 | 131 |
| COPY_RATE_MISMATCH | 99 |
| RATE_NO_SOURCE | 36 |
| AGG_NO_RATE | 29 |
| STALE_RENEWAL | 28 |
| IOU_MUNI_NOTES | 11 |
| MUNI_IOU_NOTES | 4 |
| COOP_IOU_NOTES | 4 |
| EXPIRED_ACTIVE | 3 |
| TERM_NO_PROGRAM | 2 |
| DOC_COUNT_MISMATCH | 2 |
| RATE_CHANGE_NO_PREV | 1 |
| RATE_MISMATCH | 0 |

`DOC_COUNT_MISMATCH` is the two header lines in `CLAUDE.md`: "18 JSON files, 251 zones total" against 20 region files and 427 electric records. Other comment lines in that file, counted directly:

| CLAUDE.md comment | Documented | Records in the file |
| --- | ---: | ---: |
| `ohio_municipal_utilities.json` — 47 municipal utilities | 47 | 48 |
| `nopec_cuyahoga_suburbs.json` — 23 additional Cuyahoga NOPEC communities | 23 | 29 |
| `sopec_columbus_suburbs.json` — 14 SOPEC member communities | 14 | 13 |
| `dayton_aes_suburbs.json` — 10 AES Ohio suburbs | 10 | 8 |
| `cincinnati_duke_suburbs.json` — 10 Duke Energy suburbs | 10 | 54 |
| `toledo_lucas_noac.json` — NOAC (13 Toledo-area communities) | 13 | 12 |

`ohio_electric_cooperatives.json` is commented as 24 co-ops and the file has 24 records. The market-facts sentence says "All 25 Ohio co-ops". The NOAC prose line also says 13.

## HIGH findings (33)

Twelve HIGH ids are unchanged from 2026-10-23. Twenty-one are new.

### Unchanged HIGH

- **Golf Manor**, **Wayne Township (Warren Co)**, **Batavia Township**, **Williamsburg**, **Seven Mile**, **Oxford Township (Butler Co)**, **Madison Township (Butler Co)**, **Lemon Township**, **Cheviot**, **Madeira** (`cincinnati_duke_suburbs`) — `AGG_NO_RATE`: `confirmed_active_aggregation` and `currentRate` null.
- **Seven Mile** — `STALE_RENEWAL`: status `rollover`, `termEnd` 2025-09-30, 392 days before 2026-10-27. Supplier Dynegy. `lastVerified` 2026-08-19.
- **East Cleveland** (`cleveland_cuyahoga`) — `AGG_NO_RATE`.

### New HIGH

Expired term still stored as `pain_coming` (`EXPIRED_ACTIVE`). On the 327-zone tree these three were status `rollover`, so this check did not fire there.

- **Springdale** — `termEnd` 2026-08-31 (57 days before this audit), status `pain_coming`, supplier Dynegy, `currentRate` 9.29, `lastVerified` 2026-06-01. Takeaway still says "Renewal window opens in 60 days".
- **Mariemont** — `termEnd` 2026-08-31, status `pain_coming`, supplier Constellation, `currentRate` 9.657, `lastVerified` 2026-06-01.
- **Harrison** — `termEnd` 2026-08-31, status `pain_coming`, supplier Dynegy, `currentRate` 9.24, `lastVerified` 2026-06-03.

`AGG_NO_RATE` on a record key that was in the 327-zone tree:

- **Sharonville** (`cincinnati_duke`) — `currentRate` null, status `verify`, supplier WGL Energy. The 327-zone record had `currentRate` 9.39 and supplier Dynegy Energy Services.
- **Chillicothe** (`eastern_ohio_aep`) — `currentRate` null, `aggregationStatus` `confirmed_active_aggregation`, supplier AEP Energy, status `verify`.
- **Plain Township** (`ne_ohio_firstenergy`) — `currentRate` null, `aggregationStatus` `confirmed_active_aggregation`, supplier NOPEC / NextEra Energy Services, status `stable`.
- **Bay Village** (`nopec_cuyahoga_suburbs`) — `currentRate` null, supplier Dynegy. The 327-zone record had `currentRate` 9.999 and supplier NOPEC.
- **Tiffin** (`nw_central_ohio`) — `currentRate` null, `aggregationStatus` `confirmed_active_aggregation`, supplier NOPEC / NextEra Energy Services.
- **Washington Township (Wood)** (`toledo_lucas_noac`) — `currentRate` null, status `verify`. The 327-zone record had `currentRate` 9.75 and status `rollover`.
- **Wellsville**, **Cortland**, **Coldwater**, **Delphos**, **Ada**, **Liberty Center**, **Hamler**, **West Unity**, **Stryker**, **Wauseon** (`ohio_municipal_utilities`) — `aggregationStatus` `confirmed_active_aggregation`, `currentRate` null, supplier Dynegy. Utilities on the records: Wellsville AEP Ohio, Cortland Ohio Edison, Coldwater AES Ohio, Delphos and Ada AEP Ohio, and Liberty Center, Hamler, West Unity, Stryker, and Wauseon Toledo Edison.

`AGG_NO_RATE` on a record key that was not in the 327-zone tree:

- **Paris Township (Stark)** (`ne_ohio_firstenergy`)
- **Hubbard** (`ne_ohio_gas`) — gas record

### HIGH on the 2026-10-23 report that this scan does not repeat

- **Stark County (Unincorporated / Remaining)** — the 2026-10-23 HIGH was `EXPIRED_ACTIVE` with status `pain_coming`. On `main` the status is `stable`, `aggregationStatus` is `no_aggregation_verified`, `currentRate` is null, supplier is null, and `termEnd` is still 2026-08-31. `EXPIRED_ACTIVE` only fires for `pain_coming`, `pain_hit`, `transition`, and `pricing_updated`, so the passed term is `TERM_NO_PROGRAM` (MEDIUM) and `STALE_60` (MEDIUM, `lastVerified` 2026-05-01). PR #11's status check includes `stable` and still flags this record.
- **Pierce Township / Amelia** — `main` stores `currentRate` 9.199, supplier Archer Energy, `termEnd` 2028-05, status `stable`.
- **Lakewood** — `main` stores `currentRate` 10.599, supplier NOPEC / NextEra Energy Services, `termStart` 2026-09, `termEnd` 2027-06. The 327-zone record had `currentRate` null and supplier Dynegy.


## 🆕 New since 2026-10-23 (119)

- `HIGH` **Sharonville** (Cincinnati / SW Ohio) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Springdale** (Cincinnati / SW Ohio) — `EXPIRED_ACTIVE`: termEnd=2026-08-31 passed 57d ago but status='pain_coming' — should be rollover
- `HIGH` **Mariemont** (Cincinnati / SW Ohio) — `EXPIRED_ACTIVE`: termEnd=2026-08-31 passed 57d ago but status='pain_coming' — should be rollover
- `HIGH` **Harrison** (Cincinnati / SW Ohio) — `EXPIRED_ACTIVE`: termEnd=2026-08-31 passed 57d ago but status='pain_coming' — should be rollover
- `HIGH` **Chillicothe** (Eastern Ohio) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Plain Township** (NE Ohio / Cleveland / NOPEC) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Paris Township (Stark)** (NE Ohio / Cleveland / NOPEC) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Bay Village** (NE Ohio / Cleveland / NOPEC) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Tiffin** (NW & Central Ohio) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Wellsville** (Municipal Utilities) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Cortland** (Municipal Utilities) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Liberty Center** (Municipal Utilities) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Hamler** (Municipal Utilities) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **West Unity** (Municipal Utilities) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Stryker** (Municipal Utilities) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Wauseon** (Municipal Utilities) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Coldwater** (Municipal Utilities) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Delphos** (Municipal Utilities) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Ada** (Municipal Utilities) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Washington Township (Wood)** (Greater Toledo) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `HIGH` **Hubbard** (NE Ohio / Cleveland / NOPEC) — `AGG_NO_RATE`: confirmed_active_aggregation but currentRate=null
- `LOW` **Green** (Akron / Canton) — `IOU_MUNI_NOTES`: non-muni zone but notes contain muni/coop keywords: ['city electric']
- `LOW` **Crosby Township** (Other Ohio Markets) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.88 but sourceUrl=null
- `LOW` **Canfield** (NE Ohio / Cleveland / NOPEC) — `IOU_MUNI_NOTES`: non-muni zone but notes contain muni/coop keywords: ['city electric']
- `LOW` **Wooster** (NE Ohio / Cleveland / NOPEC) — `IOU_MUNI_NOTES`: non-muni zone but notes contain muni/coop keywords: ['municipal utility']
- `LOW` **New Philadelphia / Tuscarawas County** (NE Ohio / Cleveland / NOPEC) — `IOU_MUNI_NOTES`: non-muni zone but notes contain muni/coop keywords: ['municipal utility']
- `LOW` **Bucyrus** (NW & Central Ohio) — `IOU_MUNI_NOTES`: non-muni zone but notes contain muni/coop keywords: ['municipal utility']
- `LOW` **Russells Point** (Other Ohio Markets) — `RATE_NO_SOURCE`: confirmed agg with currentRate=9.26 but sourceUrl=null
- `LOW` **Akron** (NE Ohio / Cleveland / NOPEC) — `IOU_MUNI_NOTES`: non-muni zone but notes contain muni/coop keywords: ['city electric']
- `LOW` **Youngstown** (NE Ohio / Cleveland / NOPEC) — `IOU_MUNI_NOTES`: non-muni zone but notes contain muni/coop keywords: ['city electric']
- `LOW` **Warren** (NE Ohio / Cleveland / NOPEC) — `IOU_MUNI_NOTES`: non-muni zone but notes contain muni/coop keywords: ['city electric']
- `MEDIUM` **Akron** (Akron / Canton) — `COPY_RATE_MISMATCH`: takeaway mentions 9.95¢ but currentRate=9.24, previousRate=None
- `MEDIUM` **Akron** (Akron / Canton) — `COPY_RATE_MISMATCH`: hook mentions 9.95¢ but currentRate=9.24, previousRate=None
- `MEDIUM` **Green** (Akron / Canton) — `COPY_RATE_MISMATCH`: takeaway mentions 9.48¢ but currentRate=9.24, previousRate=None
- `MEDIUM` **Green** (Akron / Canton) — `COPY_RATE_MISMATCH`: takeaway mentions 9.48¢ but currentRate=9.24, previousRate=None
- `MEDIUM` **Green** (Akron / Canton) — `COPY_RATE_MISMATCH`: hook mentions 9.48¢ but currentRate=9.24, previousRate=None
- `MEDIUM` **Green** (Akron / Canton) — `COPY_RATE_MISMATCH`: hook mentions 9.48¢ but currentRate=9.24, previousRate=None
- `MEDIUM` **Sharonville** (Cincinnati / SW Ohio) — `COPY_RATE_MISMATCH`: takeaway mentions 10.276¢ but currentRate=None, previousRate=9.39
- `MEDIUM` **Springdale** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (148d ago)
- `MEDIUM` **Mariemont** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-01 (148d ago)
- `MEDIUM` **Harrison** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (146d ago)
- `MEDIUM` **Wyoming** (Cincinnati / SW Ohio) — `STALE_60`: lastVerified=2026-06-03 (146d ago)
- `MEDIUM` **Lakewood** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: takeaway mentions 10.399¢ but currentRate=10.599, previousRate=None
- `MEDIUM` **Lakewood** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: hook mentions 10.399¢ but currentRate=10.599, previousRate=None
- `MEDIUM` **Strongsville** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Miamisburg** (Dayton / Miami Valley) — `COPY_RATE_MISMATCH`: takeaway mentions 11.53¢ but currentRate=9.049, previousRate=8.71
- `MEDIUM` **Miamisburg** (Dayton / Miami Valley) — `COPY_RATE_MISMATCH`: takeaway mentions 11.73¢ but currentRate=9.049, previousRate=8.71
- `MEDIUM` **Xenia** (Dayton / Miami Valley) — `COPY_RATE_MISMATCH`: takeaway mentions 11.53¢ but currentRate=None, previousRate=8.71
- `MEDIUM` **Xenia** (Dayton / Miami Valley) — `COPY_RATE_MISMATCH`: takeaway mentions 11.73¢ but currentRate=None, previousRate=8.71
- `MEDIUM` **Centerville** (Dayton / Miami Valley) — `COPY_RATE_MISMATCH`: takeaway mentions 11.53¢ but currentRate=9.049, previousRate=8.71
- `MEDIUM` **Centerville** (Dayton / Miami Valley) — `COPY_RATE_MISMATCH`: takeaway mentions 11.73¢ but currentRate=9.049, previousRate=8.71
- `MEDIUM` **Vandalia** (Dayton / Miami Valley) — `COPY_RATE_MISMATCH`: takeaway mentions 11.53¢ but currentRate=9.049, previousRate=8.71
- `MEDIUM` **Vandalia** (Dayton / Miami Valley) — `COPY_RATE_MISMATCH`: takeaway mentions 11.73¢ but currentRate=9.049, previousRate=8.71
- `MEDIUM` **Fairborn** (Dayton / Miami Valley) — `COPY_RATE_MISMATCH`: takeaway mentions 11.53¢ but currentRate=9.049, previousRate=None
- `MEDIUM` **Fairborn** (Dayton / Miami Valley) — `COPY_RATE_MISMATCH`: takeaway mentions 11.73¢ but currentRate=9.049, previousRate=None
- `MEDIUM` **Troy** (Dayton / Miami Valley) — `COPY_RATE_MISMATCH`: takeaway mentions 11.53¢ but currentRate=9.049, previousRate=6.57
- `MEDIUM` **Troy** (Dayton / Miami Valley) — `COPY_RATE_MISMATCH`: takeaway mentions 11.73¢ but currentRate=9.049, previousRate=6.57
- `MEDIUM` **Kettering** (Dayton / Miami Valley) — `COPY_RATE_MISMATCH`: takeaway mentions 11.53¢ but currentRate=9.049, previousRate=None
- `MEDIUM` **Kettering** (Dayton / Miami Valley) — `COPY_RATE_MISMATCH`: takeaway mentions 11.73¢ but currentRate=9.049, previousRate=None
- `MEDIUM` **Mentor** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Chardon / Geauga County** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: takeaway mentions 9.399¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Chardon / Geauga County** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: hook mentions 9.399¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Canfield** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: takeaway mentions 9.98¢ but currentRate=8.66, previousRate=None
- `MEDIUM` **Canfield** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: takeaway mentions 10.39¢ but currentRate=8.66, previousRate=None
- `MEDIUM` **Canfield** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: hook mentions 9.98¢ but currentRate=8.66, previousRate=None
- `MEDIUM` **Canfield** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: hook mentions 10.39¢ but currentRate=8.66, previousRate=None
- `MEDIUM` **Massillon** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: takeaway mentions 8.5¢ but currentRate=10.399, previousRate=8.999
- `MEDIUM` **Ashtabula Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Geneva Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Harpersfield Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Jefferson Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Kingsville Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Plymouth Township (Ashtabula)** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Saybrook Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Andover Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Austinburg Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Cherry Valley Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Colebrook Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Denmark Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Dorset Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Hartsgrove Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Lenox Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Monroe Township (Ashtabula)** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Morgan Township (Ashtabula)** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **New Lyme Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Orwell Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Pierpont Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Richmond Township (Ashtabula)** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Rome Township (Ashtabula)** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Sheffield Township (Ashtabula)** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Trumbull Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Wayne Township (Ashtabula)** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Williamsfield Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Windsor Township** (Ashtabula County) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Westlake** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: takeaway mentions 10.11¢ but currentRate=None, previousRate=8.38
- `MEDIUM` **Shaker Heights** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: hook mentions 10.399¢ but currentRate=9.99, previousRate=None
- `MEDIUM` **Olmsted Falls** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: takeaway mentions 6.5¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Twinsburg** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Parma Heights** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Brecksville** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: takeaway mentions 10.19¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Brecksville** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: takeaway mentions 10.59¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Brecksville** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: takeaway mentions 11.11¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Brecksville** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: takeaway mentions 10.59¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Brecksville** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: hook mentions 10.59¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Brecksville** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: hook mentions 10.59¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Amherst** (NE Ohio / Cleveland / NOPEC) — `MUNI_IOU_NOTES`: municipal_utility zone but notes reference IOU names: ['Ohio Edison']
- `MEDIUM` **Grafton** (NE Ohio / Cleveland / NOPEC) — `MUNI_IOU_NOTES`: municipal_utility zone but notes reference IOU names: ['Ohio Edison']
- `MEDIUM` **Painesville** (NE Ohio / Cleveland / NOPEC) — `MUNI_IOU_NOTES`: municipal_utility zone but notes reference IOU names: ['Ohio Edison']
- `MEDIUM` **Madison Township** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Bainbridge Township** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Newbury Township** (NE Ohio / Cleveland / NOPEC) — `COPY_RATE_MISMATCH`: takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
- `MEDIUM` **Washington Township (Wood)** (Greater Toledo) — `COPY_RATE_MISMATCH`: takeaway mentions 11.09¢ but currentRate=None, previousRate=8.63
- `MEDIUM` **Youngstown** (Youngstown / Warren) — `COPY_RATE_MISMATCH`: takeaway mentions 9.97¢ but currentRate=7.99, previousRate=None
- `MEDIUM` **Youngstown** (Youngstown / Warren) — `COPY_RATE_MISMATCH`: takeaway mentions 9.97¢ but currentRate=7.99, previousRate=None
- `MEDIUM` **Youngstown** (Youngstown / Warren) — `COPY_RATE_MISMATCH`: takeaway mentions 9.97¢ but currentRate=7.99, previousRate=None
- `MEDIUM` **Youngstown** (Youngstown / Warren) — `COPY_RATE_MISMATCH`: hook mentions 9.97¢ but currentRate=7.99, previousRate=None
- `MEDIUM` **Youngstown** (Youngstown / Warren) — `COPY_RATE_MISMATCH`: hook mentions 9.97¢ but currentRate=7.99, previousRate=None
- `MEDIUM` **Mahoning County** (Youngstown / Warren) — `TERM_NO_PROGRAM`: has term dates but supplier=null and agg='unresolved'
- `MEDIUM` **Warren City** (Youngstown / Warren) — `COPY_RATE_MISMATCH`: takeaway mentions 9.999¢ but currentRate=10.399, previousRate=None

## ✅ Resolved since 2026-10-23 (225)

- **Akron** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.24 but sourceUrl=null
- **Akron** `STALE_60` — was: lastVerified=2026-08-19 (65d ago)
- **Green** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.24 but sourceUrl=null
- **Green** `STALE_60` — was: lastVerified=2026-08-19 (65d ago)
- **Stark County (Unincorporated / Remaining)** `EXPIRED_ACTIVE` — was: termEnd=2026-08-31 passed 53d ago but status='pain_coming' — should be rollover
- **Stark County (Unincorporated / Remaining)** `COPY_RATE_MISMATCH` — was: hook mentions 9.999¢ but currentRate=9.77, previousRate=None
- **Kent / Portage County** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Kent / Portage County** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Kent / Portage County** `COPY_RATE_MISMATCH` — was: takeaway mentions 8.999¢ but currentRate=9.999, previousRate=7.0
- **Clinton** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Sharonville** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.39 but sourceUrl=null
- **Loveland** `STALE_RENEWAL` — was: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- **Loveland** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Loveland** `COPY_RATE_MISMATCH` — was: takeaway mentions 10.7¢ but currentRate=9.07, previousRate=None
- **Waynesville** `STALE_RENEWAL` — was: rollover termEnd=2026-06-30 expired 115d ago — any new contract?
- **Waynesville** `STALE_60` — was: lastVerified=2026-06-03 (142d ago)
- **Waynesville** `COPY_RATE_MISMATCH` — was: takeaway mentions 10.7¢ but currentRate=9.14, previousRate=None
- **Waynesville** `COPY_RATE_MISMATCH` — was: hook mentions 10.7¢ but currentRate=9.14, previousRate=None
- **Franklin** `STALE_60` — was: lastVerified=2026-06-03 (142d ago)
- **Springboro** `STALE_60` — was: lastVerified=2026-06-03 (142d ago)
- **Pierce Township / Amelia** `AGG_NO_RATE` — was: confirmed_active_aggregation but currentRate=null
- **Pierce Township / Amelia** `STALE_60` — was: lastVerified=2026-06-03 (142d ago)
- **Cleveland** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.236 but sourceUrl=null
- **Cleveland** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Lakewood** `AGG_NO_RATE` — was: confirmed_active_aggregation but currentRate=null
- **Lakewood** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **East Cleveland** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Parma** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Parma** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Strongsville** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Strongsville** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Euclid** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Euclid** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Solon** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Solon** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **North Royalton** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **North Royalton** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Berea** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Berea** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Ontario** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Miamisburg** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Springboro** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Xenia** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Franklin** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Springfield** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Centerville** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Vandalia** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Fairborn** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.04 but sourceUrl=null
- **Fairborn** `STALE_60` — was: lastVerified=2026-05-01 (175d ago)
- **Troy** `STALE_RENEWAL` — was: rollover termEnd=2025-12-31 expired 296d ago — any new contract?
- **Troy** `TERM_NO_PROGRAM` — was: has term dates but supplier=null and agg='no_aggregation_verified'
- **Troy** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Middletown** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Kettering** `STALE_60` — was: lastVerified=2026-05-01 (175d ago)
- **Mentor** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Mentor** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Willoughby** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Willoughby** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Eastlake** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Eastlake** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Wickliffe** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Wickliffe** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Lake County (NOPEC Group)** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Lake County (NOPEC Group)** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Chardon / Geauga County** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Girard** `COPY_RATE_MISMATCH` — was: hook mentions 9.38¢ but currentRate=6.88, previousRate=None
- **Canfield** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Ashtabula** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Geneva** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Geneva** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Conneaut** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Conneaut** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Wooster** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **New Philadelphia / Tuscarawas County** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Plain Township** `STALE_RENEWAL` — was: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- **Plain Township** `TERM_NO_PROGRAM` — was: has term dates but supplier=null and agg='no_aggregation_verified'
- **Plain Township** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Canton** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **North Canton** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Massillon** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **North Olmsted** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **North Olmsted** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Middleburg Heights** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Middleburg Heights** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Brook Park** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Brook Park** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Broadview Heights** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Broadview Heights** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Seven Hills** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Seven Hills** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Garfield Heights** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Garfield Heights** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Maple Heights** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Maple Heights** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Mayfield Heights** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Mayfield Heights** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Highland Heights** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Highland Heights** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Richmond Heights** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Richmond Heights** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Lyndhurst** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Lyndhurst** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **South Euclid** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **South Euclid** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **University Heights** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **University Heights** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Cleveland Heights** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Cleveland Heights** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Shaker Heights** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Shaker Heights** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Rocky River** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Rocky River** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Bay Village** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Bay Village** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Fairview Park** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Fairview Park** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Olmsted Falls** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Olmsted Falls** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Bedford Heights** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Bedford Heights** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Warrensville Heights** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Warrensville Heights** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Twinsburg** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Twinsburg** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Parma Heights** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Parma Heights** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Beachwood** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Beachwood** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Independence** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Independence** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Bedford** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Bedford** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Brecksville** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Brecksville** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Pepper Pike** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Pepper Pike** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Avon** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Avon** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Avon Lake** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Avon Lake** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **North Ridgeville** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **North Ridgeville** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Amherst** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Amherst** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Sheffield Lake** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Sheffield Lake** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Sheffield Village** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Sheffield Village** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Grafton** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Grafton** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Stow** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Stow** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Tallmadge** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Tallmadge** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Barberton** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Barberton** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Norton** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Norton** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Copley Township** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Copley Township** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Aurora** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Aurora** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Streetsboro** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Streetsboro** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Ravenna** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Ravenna** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Painesville** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Painesville** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Willoughby Hills** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Willoughby Hills** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Mentor-on-the-Lake** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Mentor-on-the-Lake** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Madison Township** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Madison Township** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Bainbridge Township** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Bainbridge Township** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Newbury Township** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Findlay** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Tiffin** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Bucyrus** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Bellefontaine** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Washington Court House** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Marion** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Fostoria** `STALE_60` — was: lastVerified=2026-05-01 (175d ago)
- **Brunswick** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Brunswick** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Elyria** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Lorain (City)** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.999 but sourceUrl=null
- **Lorain (City)** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Grove City Area / Southwest Franklin County** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=10.97 but sourceUrl=null
- **Grove City Area / Southwest Franklin County** `STALE_60` — was: lastVerified=2026-05-01 (175d ago)
- **Medina County (Rural Unincorporated)** `TERM_NO_PROGRAM` — was: has term dates but supplier=null and agg='address_dependent'
- **Medina County (Rural Unincorporated)** `STALE_60` — was: lastVerified=2026-05-01 (175d ago)
- **Lakeview / Indian Lake Area** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Worthington** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=11.162 but sourceUrl=null
- **Worthington** `STALE_60` — was: lastVerified=2026-05-01 (175d ago)
- **Reynoldsburg** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=11.162 but sourceUrl=null
- **Reynoldsburg** `STALE_60` — was: lastVerified=2026-05-01 (175d ago)
- **New Albany** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=11.162 but sourceUrl=null
- **New Albany** `STALE_60` — was: lastVerified=2026-05-01 (175d ago)
- **Westerville** `MUNI_IOU_NOTES` — was: municipal_utility zone but notes reference IOU names: ['AEP Ohio']
- **Lancaster** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=10.01 but sourceUrl=null
- **Lancaster** `STALE_60` — was: lastVerified=2026-05-01 (175d ago)
- **Delaware (City)** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=10.01 but sourceUrl=null
- **Delaware (City)** `STALE_60` — was: lastVerified=2026-05-01 (175d ago)
- **Pickerington** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=10.01 but sourceUrl=null
- **Heath / Newark** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=10.01 but sourceUrl=null
- **Marysville** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=10.01 but sourceUrl=null
- **Jerusalem Township** `STALE_RENEWAL` — was: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- **Jerusalem Township** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.75 but sourceUrl=null
- **Jerusalem Township** `STALE_60` — was: lastVerified=2026-08-19 (65d ago)
- **Washington Township (Wood)** `STALE_RENEWAL` — was: rollover termEnd=2026-05-31 expired 145d ago — any new contract?
- **Washington Township (Wood)** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=9.75 but sourceUrl=null
- **Youngstown** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Warren City** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Sebring** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Austintown Township** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=10.59 but sourceUrl=null
- **Austintown Township** `STALE_60` — was: lastVerified=2026-06-01 (144d ago)
- **Liberty Township (Trumbull)** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Springfield Township (Mahoning)** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=10.59 but sourceUrl=null
- **Springfield Township (Mahoning)** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Jackson Township (Mahoning)** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=10.59 but sourceUrl=null
- **Jackson Township (Mahoning)** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)
- **Coitsville Township** `RATE_NO_SOURCE` — was: confirmed agg with currentRate=10.59 but sourceUrl=null
- **Coitsville Township** `STALE_60` — was: lastVerified=2026-06-04 (141d ago)

## Internal contradictions

No zone name is stored twice inside `data/regions` (0 duplicate names across the 20 files). The suspects below are disagreements inside one record, or between a region file and `data/research/merged_summary.md`.

### Mentor — 10.399 and 9.999

One record, `lake_geauga_nopec.json`. `currentRate` 10.399, `previousRate` 9.999, supplier `NOPEC / NextEra Energy Services`, `termStart` 2026-09, `termEnd` 2027-06, status `pricing_updated`, confidence `high`, `lastVerified` 2026-10-21, utility The Illuminating Company. The takeaway states both prices and also names fixed-term alternatives 12-month 10.299¢ and 24-month 10.599¢. The 10.599¢ figure is why `COPY_RATE_MISMATCH` fires; it is written as an opt-in term, and the stored current and previous rates are 10.399 and 9.999.

`docs/research/ASHTABULA-LAKE-CONTINUATION_2026-10-23.md` labels 10.399¢ Likely – keep flagged (Mentor city notice and the NOPEC pricing page) and labels 9.999¢ Historical only for June–August 2026 meter reads. The continuation's corrections table says the city notices support both numbers and their meter-read windows. Confidence on the record is `high`. The continuation's evidence rule says Confirmed requires three independent sources, and it records zero of the 46 Ashtabula/Lake records as resolved under that rule.

The 327-zone tree stored Mentor at `currentRate` 9.999, `previousRate` 7.0, `termEnd` 2026-12-31, utility Ohio Edison. Those are the values behind the 2026-10-23 `RATE_NO_SOURCE` line. They are not a second Mentor record on `main`.

### Madison Township (Lake) — NOPEC / NextEra through 2027-06, and Dynegy through 2026-12

`nopec_lorain_summit_portage.json` name `Madison Township`: supplier `NOPEC / NextEra Energy Services`, `currentRate` 10.399, `previousRate` 9.999, `termStart` 2026-09, `termEnd` 2027-06, status `pricing_updated`, confidence `medium`, utility The Illuminating Company, `lastVerified` 2026-10-21. The takeaway also names the 10.599¢ 24-month alternative.

`data/research/merged_summary.md` (2026-10-15), hot-lead row 62: Madison Township, Lake, utility CEI, supplier Dynegy, agg rate 10.399, term end 2026-12, confidence single-source. The call list on the same file says: supplier Dynegy vs NOPEC/NextEra, and rate 10.399 vs 9.47. There is no second `Madison Township` row for Lake County in `data/regions`. `merged_confirmed.json` has `Madison County` (Dynegy, 9.47, `termEnd` 2026-12) and `Madison Township (Richland)` (Dynegy, 9.47, `termEnd` 2026-12). Those names are different places.

The continuation file marks this supplier and end-date pair as Conflict and says the township homepage that was checked does not resolve it.

### Painesville — municipal electric record, Ohio Edison note

`nopec_lorain_summit_portage.json`: utility `Painesville Municipal Electric`, `aggregationStatus` `municipal_utility`, `currentRate` null, supplier null, term dates null, status `stable`, confidence `medium`, `lastVerified` 2026-10-15, `futureUse` `municipal_blacklist`. Notes: "Ohio Edison territory. Lake County seat. Commercial and light industrial accounts along Route 20." Takeaway: "Painesville city runs a municipal electric utility. Competitive retail supply is not sold on those accounts. Painesville Township is a separate NOPEC member and is not this zone."

`MUNI_IOU_NOTES` fires on that notes sentence. The same check fires for **Amherst** and **Grafton** in the same file, both `municipal_utility` with notes that name Ohio Edison. The continuation labels the Painesville notes' citywide Ohio Edison characterization Proven incorrect, and says municipal service is Likely – keep flagged, with active competitive aggregation not found.

`main` does not store a Painesville rate of 9.999. The 327-zone record did: `currentRate` 9.999, supplier NOPEC, `aggregationStatus` `confirmed_active_aggregation`, utility Ohio Edison. `merged_summary.md` call list still has Painesville, Lake: supplier City utility vs NOPEC/NextEra, utility CEI vs Ohio Edison.

### Lake County (NOPEC Group) — one stored rate on an umbrella row

`lake_geauga_nopec.json`: `aggregationStatus` `confirmed_active_aggregation`, `currentRate` 10.399, `previousRate` 9.999, supplier `NOPEC / NextEra Energy Services`, `termStart` 2026-09, `termEnd` 2027-06, status `pricing_updated`, confidence `high`, utility The Illuminating Company, `lastVerified` 2026-10-22. Takeaway: "Lake County (NOPEC Group) is not one contract." Notes: "There is no single county ordinance. Use the city or township zone." The continuation says one umbrella supplier, rate, and term was not found, and that individual community evidence cannot establish those fields for the whole county.

### Stark County term after 2026-08-31

`akron_summit_medina.json`: `termStart` 2025-08-01, `termEnd` 2026-08-31, status `stable`, `aggregationStatus` `no_aggregation_verified`, supplier null, `currentRate` null, `lastVerified` 2026-05-01. This is the oldest `lastVerified` on a non-municipal record. See the HIGH section for why it is not `EXPIRED_ACTIVE` on this run.

## Stale records

Age is days before 2026-10-27. One record has no `lastVerified`: **Westerville** in `columbus_aep.json` (`aggregationStatus` `municipal_utility`, status `stable`). `STALE_60` skips `municipal_utility` and `electric_cooperative`, so that blank date is outside the 131 stale findings.

| lastVerified | Records | Age on 2026-10-27 |
| --- | ---: | ---: |
| 2026-05-01 | 43 | 179 |
| 2026-05-29 | 24 | 151 |
| 2026-06-01 | 66 | 148 |
| 2026-06-03 | 25 | 146 |
| 2026-06-04 | 9 | 145 |
| 2026-08-19 | 19 | 69 |
| 2026-10-15 | 124 | 12 |
| 2026-10-20 | 29 | 7 |
| 2026-10-21 | 8 | 6 |
| 2026-10-22 | 108 | 5 |
| missing | 1 |  |

Oldest date on file: **2026-05-01** (179 days), 43 records. 29 of those are `municipal_utility` and are outside `STALE_60`. 14 are not exempt:

- **Stark County (Unincorporated / Remaining)** (`akron_summit_medina`) — `no_aggregation_verified`, status `stable`
- **Cleveland Public Power** (`ohio_municipal_utilities`) — `address_dependent`, status `stable`
- **Columbus Division of Power** (`ohio_municipal_utilities`) — `address_dependent`, status `stable`
- **Hamilton** (`ohio_municipal_utilities`) — `address_dependent`, status `stable`
- **Athens County (Rural AEP)** (`remaining_ohio_markets`) — `address_dependent`, status `verify`
- **Guernsey / Noble / Morgan Counties** (`remaining_ohio_markets`) — `address_dependent`, status `verify`
- **Licking County / Pataskala** (`remaining_ohio_markets`) — `confirmed_active_aggregation`, status `pain_coming`
- **Bexley** (`sopec_columbus_suburbs`) — `confirmed_active_aggregation`, status `pain_coming`
- **Dublin** (`sopec_columbus_suburbs`) — `confirmed_active_aggregation`, status `pain_coming`
- **Grandview Heights** (`sopec_columbus_suburbs`) — `confirmed_active_aggregation`, status `pain_coming`
- **Heath / Newark** (`sopec_columbus_suburbs`) — `unresolved`, status `verify`
- **Hilliard** (`sopec_columbus_suburbs`) — `confirmed_active_aggregation`, status `pain_coming`
- **Marysville** (`sopec_columbus_suburbs`) — `address_dependent`, status `verify`
- **Pickerington** (`sopec_columbus_suburbs`) — `address_dependent`, status `verify`

All 24 records in `ohio_electric_cooperatives.json` are `lastVerified` 2026-05-29 (151 days). `STALE_60` does not flag `electric_cooperative`.

## Research cross-check — Ashtabula and Lake, each zone

Sources: `docs/research/ASHTABULA-LAKE_2026-10-23.md` (30 zones) and `docs/research/ASHTABULA-LAKE-CONTINUATION_2026-10-23.md` (16 zones). The continuation's own tracker says 46 Ashtabula/Lake records were reviewed and 0 were resolved on every requested field under its three-independent-source rule. Labels below are the electric-program labels in those files. Stored columns are the region JSON on `main` today.

44 of these 46 records store `currentRate` 10.399 and `previousRate` 9.999. The two that do not are Painesville (null / null, municipal) and Andover village (9.86 / null, Dynegy).

No `data/gas` record is named for the Ashtabula townships the first research file marks electric-only (Andover, Austinburg, Cherry Valley, Colebrook, Denmark, Dorset, Hartsgrove, Lenox, Monroe, Morgan, Orwell, Sheffield) or for Orwell Village, Roaming Shores, or Rock Creek.

| Zone | File | Utility | Agg status | Supplier | Current | Previous | Term | Status | Conf | Verified | Research label |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- | --- |
| Ashtabula | ne_ohio_firstenergy | The Illuminating Company | address_dependent | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; utility Likely; rate application Likely – keep flagged. City page does not state the current product or cents. |
| Geneva | ne_ohio_firstenergy | The Illuminating Company | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; utility Likely; rate application Likely – keep flagged. Council material does not state the current product or cents. |
| Conneaut | ne_ohio_firstenergy | The Illuminating Company | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; utility Likely; rate application Likely – keep flagged. Ordinances page does not establish the current product or cents. |
| Ashtabula Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; remaining fields not found / keep flagged. |
| Geneva Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; Standard Program application Likely – keep flagged. |
| Harpersfield Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; remaining fields not found / keep flagged. |
| Jefferson Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; Standard Program application Likely – keep flagged. |
| Kingsville Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; Standard Program application Likely – keep flagged. |
| Plymouth Township (Ashtabula) | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; remaining fields not found / keep flagged. Research names this Plymouth Township. |
| Saybrook Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; rate application Likely – keep flagged. |
| Andover Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; electric-only on the NOPEC map; remaining fields not found / keep flagged. |
| Austinburg Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; electric-only; rate Likely – keep flagged. |
| Cherry Valley Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; electric-only; remaining fields not found / keep flagged. |
| Colebrook Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; electric-only; rate Likely – keep flagged. |
| Denmark Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; electric-only; rate Likely – keep flagged. |
| Dorset Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; electric-only; rate Likely – keep flagged. |
| Hartsgrove Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; electric-only; rate Likely – keep flagged. |
| Lenox Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; electric-only; rate Likely – keep flagged. |
| Monroe Township (Ashtabula) | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; electric-only; rate Likely – keep flagged. Research names this Monroe Township. |
| Morgan Township (Ashtabula) | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; electric-only; rate Likely – keep flagged. Research names this Morgan Township. |
| New Lyme Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; remaining fields not found / keep flagged. |
| Orwell Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; electric-only; rate Likely – keep flagged. |
| Pierpont Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; remaining fields not found / keep flagged. |
| Richmond Township (Ashtabula) | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; remaining fields not found / keep flagged. Research names this Richmond Township. |
| Rome Township (Ashtabula) | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; remaining fields not found / keep flagged. Research names this Rome Township. |
| Sheffield Township (Ashtabula) | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; electric-only; rate Likely – keep flagged. Research names this Sheffield Township. |
| Trumbull Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; remaining fields not found / keep flagged. |
| Wayne Township (Ashtabula) | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; remaining fields not found / keep flagged. Research names this Wayne Township. |
| Williamsfield Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; remaining fields not found / keep flagged. |
| Windsor Township | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Confirmed; remaining fields not found / keep flagged. |
| Geneva-on-the-Lake | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | low | 2026-10-22 | Aggregation Likely – keep flagged. Community-specific supplier, rate, type, and dates: not found. |
| Jefferson Village | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | low | 2026-10-22 | Membership Likely – keep flagged. Current local cents, product, and term: not found. |
| North Kingsville | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | low | 2026-10-22 | Village states it joined NOPEC for electricity and gas. Current cents and term: not found locally. |
| Orwell Village | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | low | 2026-10-22 | Electric member, Likely – keep flagged. Current rate not found. Map lists electricity only. |
| Roaming Shores | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | low | 2026-10-22 | Electric membership Likely – keep flagged. Current cents not found. |
| Rock Creek | ne_ohio_firstenergy | FirstEnergy | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | low | 2026-10-22 | Membership Likely – keep flagged. Executed agreement, rate, and term: not found. |
| Mentor | lake_geauga_nopec | The Illuminating Company | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | high | 2026-10-21 | Current Standard 10.399¢ Likely – keep flagged (city notice and NOPEC page). Prior 9.999¢ is Historical only for June–August 2026. |
| Willoughby | lake_geauga_nopec | The Illuminating Company | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | high | 2026-10-22 | City names Standard as the automatic June 2026 option. City-specific cents: not found. Numerical application unresolved. |
| Eastlake | lake_geauga_nopec | The Illuminating Company | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | high | 2026-10-22 | Map membership Likely – keep flagged. Community-specific rate and term: not found. |
| Wickliffe | lake_geauga_nopec | The Illuminating Company | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | high | 2026-10-22 | Directory names Illuminating Company, Likely – keep flagged. Current cents and term: not found locally. |
| Lake County (NOPEC Group) | lake_geauga_nopec | The Illuminating Company | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | high | 2026-10-22 | A single countywide contract, supplier, rate, and term: not found. Likely – keep flagged; unresolved. |
| Painesville | nopec_lorain_summit_portage | Painesville Municipal Electric | municipal_utility | — | — | — | — → — | stable | medium | 2026-10-15 | Municipal electric service, Likely – keep flagged. Active competitive aggregation not found. Notes' citywide Ohio Edison line: Proven incorrect. |
| Willoughby Hills | nopec_lorain_summit_portage | The Illuminating Company | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | City identifies NOPEC electric and gas membership. Local cents and the stored east/west utility split: not found. |
| Mentor-on-the-Lake | nopec_lorain_summit_portage | The Illuminating Company | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-22 | Membership Likely – keep flagged. Current cents not found. Green-plan rejection is an unverified secondary account. |
| Madison Township | nopec_lorain_summit_portage | The Illuminating Company | confirmed_active_aggregation | NOPEC / NextEra Energy Services | 10.399 | 9.999 | 2026-09 → 2027-06 | pricing_updated | medium | 2026-10-21 | NOPEC membership Likely – keep flagged. Local supplier, rate, and term: not found. Open conflict with merged_summary.md (Dynegy, 2026-12). |
| Andover | ne_ohio_firstenergy | Ohio Edison | confirmed_active_aggregation | Dynegy | 9.86 | — | — → 2028-06-30 | stable | high | 2026-06-03 | Dynegy page names the village, Likely – keep flagged, 9.86¢ for May 2026–June 2028. Exact day 2028-06-30 is not on that page. One source does not meet the three-source bar. |

Where the stored record and the research file diverge, zone by zone:

- **Ashtabula** — research says NOPEC membership is Confirmed and the rate application is Likely – keep flagged because the city page does not state the cents. The record stores 10.399 / 9.999 with `aggregationStatus` `address_dependent` and confidence `medium`. The other two cities in that file, Geneva and Conneaut, store the same rates with `confirmed_active_aggregation`.
- **Geneva, Conneaut** — same rate pair and The Illuminating Company, confidence `medium`. Research: membership Confirmed, rate application Likely – keep flagged.
- **Ashtabula County townships in the first research file** (Ashtabula Township, Geneva Township, Harpersfield, Jefferson, Kingsville, Plymouth, Saybrook, Andover, Austinburg, Cherry Valley, Colebrook, Denmark, Dorset, Hartsgrove, Lenox, Monroe, Morgan, New Lyme, Orwell, Pierpont, Richmond, Rome, Sheffield, Trumbull, Wayne, Williamsfield, Windsor) — each stores utility `FirstEnergy`, supplier NOPEC / NextEra, 10.399 / 9.999, term 2026-09 → 2027-06, status `pricing_updated`, confidence `medium`, `lastVerified` 2026-10-22, `confirmed_active_aggregation`. The first research file says `FirstEnergy` is not a billable operating-company name, and that the 10.399¢ Standard product is not established as the default for each township from a township source. Seven of those names on `main` carry an `(Ashtabula)` suffix: Plymouth, Monroe, Morgan, Richmond, Rome, Sheffield, and Wayne.
- **Geneva-on-the-Lake, Jefferson Village, North Kingsville, Orwell Village, Roaming Shores, Rock Creek** — same 10.399 / 9.999 term and supplier, utility `FirstEnergy`, confidence `low`, `lastVerified` 2026-10-22. The continuation says the current local cents were not found for each of them.
- **Mentor** — stored 10.399 current and 9.999 previous match the two prices the continuation cites. Confidence is `high`. The continuation's label for the current price is Likely – keep flagged, not Confirmed.
- **Willoughby, Eastlake, Wickliffe** — each stores 10.399 / 9.999 at confidence `high`. Each record's own hook says the local page opened on 2026-10-22 does not state the current cents (Willoughby: "The city page does not restate the cents."). The continuation says city-specific cents were not found for Willoughby, Eastlake, and Wickliffe.
- **Willoughby Hills** — stores The Illuminating Company, and the notes still say Illuminating Company in the western portion and Ohio Edison in the eastern portion. The continuation says that east/west split was not found on the local NOPEC page checked. Confidence `medium`. Rate pair 10.399 / 9.999.
- **Mentor-on-the-Lake** — stores 10.399 / 9.999, confidence `medium`. The hook says a green option was voted down and "The file price is 10.399¢." The continuation says the green-plan article is an unverified secondary account and does not prove the current Standard price, and that local cents were not found.
- **Lake County (NOPEC Group)** — structured fields are one active program at 10.399 with confidence `high`. Takeaway says it is not one contract. Continuation: single county contract not found.
- **Painesville** — stored municipal fields match the continuation's municipal-service finding. The notes sentence "Ohio Edison territory." is the line the continuation calls Proven incorrect as a citywide characterization. No 9.999 rate is stored.
- **Madison Township** — region JSON is NOPEC / NextEra through 2027-06 at 10.399. `merged_summary.md` row 62 is Dynegy through 2026-12. Continuation status: Conflict. Research also says the local rate was not found on the township pages checked.
- **Andover** (village, separate from Andover Township) — Dynegy, `currentRate` 9.86, `previousRate` null, `termStart` null, `termEnd` 2028-06-30, utility Ohio Edison, confidence `high`, `lastVerified` 2026-06-03, `sourceUrl` null (`RATE_NO_SOURCE` and `STALE_60`). Continuation: the supplier page supports 9.86¢ for May 2026–June 2028 and does not support an exact June 30 end; the label is Likely – keep flagged. Andover Township remains a separate NOPEC 10.399 record.
## NE Ohio / Cleveland / NOPEC (HIGH:5 MED:39 LOW:9)

- `HIGH` **East Cleveland** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Plain Township** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Paris Township (Stark)** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Bay Village** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Hubbard** [gas] `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `MEDIUM` **Lakewood** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.399¢ but currentRate=10.599, previousRate=None
  *current:* `10.399`
- `MEDIUM` **Lakewood** `COPY_RATE_MISMATCH`  
  hook mentions 10.399¢ but currentRate=10.599, previousRate=None
  *current:* `10.399`
- `MEDIUM` **Strongsville** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Mentor** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Chardon / Geauga County** `COPY_RATE_MISMATCH`  
  takeaway mentions 9.399¢ but currentRate=10.399, previousRate=9.999
  *current:* `9.399`
- `MEDIUM` **Chardon / Geauga County** `COPY_RATE_MISMATCH`  
  hook mentions 9.399¢ but currentRate=10.399, previousRate=9.999
  *current:* `9.399`
- `MEDIUM` **Niles** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Girard** `STALE_RENEWAL`  
  rollover termEnd=2025-12-31 expired 300d ago — any new contract?
  *current:* `2025-12-31`
- `MEDIUM` **Girard** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Boardman Township** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Canfield** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 149d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Canfield** `COPY_RATE_MISMATCH`  
  takeaway mentions 9.98¢ but currentRate=8.66, previousRate=None
  *current:* `9.98`
- `MEDIUM` **Canfield** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.39¢ but currentRate=8.66, previousRate=None
  *current:* `10.39`
- `MEDIUM` **Canfield** `COPY_RATE_MISMATCH`  
  hook mentions 9.98¢ but currentRate=8.66, previousRate=None
  *current:* `9.98`
- `MEDIUM` **Canfield** `COPY_RATE_MISMATCH`  
  hook mentions 10.39¢ but currentRate=8.66, previousRate=None
  *current:* `10.39`
- `MEDIUM` **Salem** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Alliance** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Mansfield** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Coshocton** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Massillon** `COPY_RATE_MISMATCH`  
  takeaway mentions 8.5¢ but currentRate=10.399, previousRate=8.999
  *current:* `8.5`
- `MEDIUM` **Perry Township (Stark)** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Andover** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Westlake** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.11¢ but currentRate=None, previousRate=8.38
  *current:* `10.11`
- `MEDIUM` **Shaker Heights** `COPY_RATE_MISMATCH`  
  hook mentions 10.399¢ but currentRate=9.99, previousRate=None
  *current:* `10.399`
- `MEDIUM` **Olmsted Falls** `COPY_RATE_MISMATCH`  
  takeaway mentions 6.5¢ but currentRate=10.399, previousRate=9.999
  *current:* `6.5`
- `MEDIUM` **Twinsburg** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Parma Heights** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Brecksville** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.19¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.19`
- `MEDIUM` **Brecksville** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.59¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.59`
- `MEDIUM` **Brecksville** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.11¢ but currentRate=10.399, previousRate=9.999
  *current:* `11.11`
- `MEDIUM` **Brecksville** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.59¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.59`
- `MEDIUM` **Brecksville** `COPY_RATE_MISMATCH`  
  hook mentions 10.59¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.59`
- `MEDIUM` **Brecksville** `COPY_RATE_MISMATCH`  
  hook mentions 10.59¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.59`
- `MEDIUM` **Amherst** `MUNI_IOU_NOTES`  
  municipal_utility zone but notes reference IOU names: ['Ohio Edison']
  *current:* `['Ohio Edison']`
- `MEDIUM` **Grafton** `MUNI_IOU_NOTES`  
  municipal_utility zone but notes reference IOU names: ['Ohio Edison']
  *current:* `['Ohio Edison']`
- `MEDIUM` **Painesville** `MUNI_IOU_NOTES`  
  municipal_utility zone but notes reference IOU names: ['Ohio Edison']
  *current:* `['Ohio Edison']`
- `MEDIUM` **Madison Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Bainbridge Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Newbury Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `LOW` **Canfield** `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['city electric']
  *current:* `['city electric']`
- `LOW` **Wooster** `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['municipal utility']
  *current:* `['municipal utility']`
- `LOW` **New Philadelphia / Tuscarawas County** `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['municipal utility']
  *current:* `['municipal utility']`
- `LOW` **Jackson Township (Stark)** `STALE_60`  
  lastVerified=2026-08-19 (69d ago)
  *current:* `2026-08-19`
- `LOW` **Perry Township (Stark)** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.99 but sourceUrl=null
  *current:* `9.99`
- `LOW` **Andover** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.86 but sourceUrl=null
  *current:* `9.86`
- `LOW` **Akron** [gas] `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['city electric']
  *current:* `['city electric']`
- `LOW` **Youngstown** [gas] `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['city electric']
  *current:* `['city electric']`
- `LOW` **Warren** [gas] `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['city electric']
  *current:* `['city electric']`

## Ashtabula County (HIGH:0 MED:27 LOW:0)

- `MEDIUM` **Ashtabula Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Geneva Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Harpersfield Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Jefferson Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Kingsville Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Plymouth Township (Ashtabula)** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Saybrook Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Andover Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Austinburg Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Cherry Valley Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Colebrook Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Denmark Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Dorset Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Hartsgrove Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Lenox Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Monroe Township (Ashtabula)** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Morgan Township (Ashtabula)** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **New Lyme Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Orwell Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Pierpont Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Richmond Township (Ashtabula)** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Rome Township (Ashtabula)** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Sheffield Township (Ashtabula)** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Trumbull Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Wayne Township (Ashtabula)** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Williamsfield Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`
- `MEDIUM` **Windsor Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.599¢ but currentRate=10.399, previousRate=9.999
  *current:* `10.599`

## Akron / Canton (HIGH:0 MED:11 LOW:2)

- `MEDIUM` **Akron** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 119d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Akron** `COPY_RATE_MISMATCH`  
  takeaway mentions 9.95¢ but currentRate=9.24, previousRate=None
  *current:* `9.95`
- `MEDIUM` **Akron** `COPY_RATE_MISMATCH`  
  hook mentions 9.95¢ but currentRate=9.24, previousRate=None
  *current:* `9.95`
- `MEDIUM` **Green** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 119d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Green** `COPY_RATE_MISMATCH`  
  takeaway mentions 9.48¢ but currentRate=9.24, previousRate=None
  *current:* `9.48`
- `MEDIUM` **Green** `COPY_RATE_MISMATCH`  
  takeaway mentions 9.48¢ but currentRate=9.24, previousRate=None
  *current:* `9.48`
- `MEDIUM` **Green** `COPY_RATE_MISMATCH`  
  hook mentions 9.48¢ but currentRate=9.24, previousRate=None
  *current:* `9.48`
- `MEDIUM` **Green** `COPY_RATE_MISMATCH`  
  hook mentions 9.48¢ but currentRate=9.24, previousRate=None
  *current:* `9.48`
- `MEDIUM` **Medina County** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Stark County (Unincorporated / Remaining)** `TERM_NO_PROGRAM`  
  has term dates but supplier=null and agg='no_aggregation_verified'
  *current:* `2025-08-01 → 2026-08-31`
- `MEDIUM` **Stark County (Unincorporated / Remaining)** `STALE_60`  
  lastVerified=2026-05-01 (179d ago)
  *current:* `2026-05-01`
- `LOW` **Green** `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['city electric']
  *current:* `['city electric']`
- `LOW` **Medina County** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.5 but sourceUrl=null
  *current:* `9.5`

## Youngstown / Warren (HIGH:0 MED:17 LOW:6)

- `MEDIUM` **Youngstown** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 119d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Youngstown** `COPY_RATE_MISMATCH`  
  takeaway mentions 9.97¢ but currentRate=7.99, previousRate=None
  *current:* `9.97`
- `MEDIUM` **Youngstown** `COPY_RATE_MISMATCH`  
  takeaway mentions 9.97¢ but currentRate=7.99, previousRate=None
  *current:* `9.97`
- `MEDIUM` **Youngstown** `COPY_RATE_MISMATCH`  
  takeaway mentions 9.97¢ but currentRate=7.99, previousRate=None
  *current:* `9.97`
- `MEDIUM` **Youngstown** `COPY_RATE_MISMATCH`  
  hook mentions 9.97¢ but currentRate=7.99, previousRate=None
  *current:* `9.97`
- `MEDIUM` **Youngstown** `COPY_RATE_MISMATCH`  
  hook mentions 9.97¢ but currentRate=7.99, previousRate=None
  *current:* `9.97`
- `MEDIUM` **Trumbull County** `STALE_60`  
  lastVerified=2026-06-04 (145d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Mahoning County** `TERM_NO_PROGRAM`  
  has term dates but supplier=null and agg='unresolved'
  *current:* `2026-06-01 → 2027-12-01`
- `MEDIUM` **Mahoning County** `STALE_60`  
  lastVerified=2026-06-04 (145d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Warren City** `COPY_RATE_MISMATCH`  
  takeaway mentions 9.999¢ but currentRate=10.399, previousRate=None
  *current:* `9.999`
- `MEDIUM` **Howland Township** `STALE_60`  
  lastVerified=2026-06-04 (145d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Brookfield Township (Trumbull)** `STALE_60`  
  lastVerified=2026-06-04 (145d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Weathersfield Township** `STALE_60`  
  lastVerified=2026-06-04 (145d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Vienna Township** `STALE_60`  
  lastVerified=2026-06-04 (145d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Champion Township** `STALE_60`  
  lastVerified=2026-06-04 (145d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Bazetta Township** `STALE_60`  
  lastVerified=2026-06-04 (145d ago)
  *current:* `2026-06-04`
- `MEDIUM` **Campbell** `STALE_60`  
  lastVerified=2026-06-04 (145d ago)
  *current:* `2026-06-04`
- `LOW` **Howland Township** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.14 but sourceUrl=null
  *current:* `10.14`
- `LOW` **Weathersfield Township** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.14 but sourceUrl=null
  *current:* `10.14`
- `LOW` **Vienna Township** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.14 but sourceUrl=null
  *current:* `10.14`
- `LOW` **Champion Township** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.14 but sourceUrl=null
  *current:* `10.14`
- `LOW` **Bazetta Township** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.14 but sourceUrl=null
  *current:* `10.14`
- `LOW` **Bazetta Township** `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['municipal utility']
  *current:* `['municipal utility']`

## Columbus / Central Ohio (HIGH:0 MED:11 LOW:8)

- `MEDIUM` **Columbus** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Gahanna** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Gahanna** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.927¢ but currentRate=11.162, previousRate=9.756
  *current:* `10.927`
- `MEDIUM` **Grove City** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Dublin** `STALE_60`  
  lastVerified=2026-05-01 (179d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Hilliard** `STALE_60`  
  lastVerified=2026-05-01 (179d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Bexley** `STALE_60`  
  lastVerified=2026-05-01 (179d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Grandview Heights** `STALE_60`  
  lastVerified=2026-05-01 (179d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Pickerington** `STALE_60`  
  lastVerified=2026-05-01 (179d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Heath / Newark** `STALE_60`  
  lastVerified=2026-05-01 (179d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Marysville** `STALE_60`  
  lastVerified=2026-05-01 (179d ago)
  *current:* `2026-05-01`
- `LOW` **Columbus** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.01 but sourceUrl=null
  *current:* `10.01`
- `LOW` **Gahanna** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=11.162 but sourceUrl=null
  *current:* `11.162`
- `LOW` **Grove City** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.97 but sourceUrl=null
  *current:* `10.97`
- `LOW` **Ontario** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=8.66 but sourceUrl=null
  *current:* `8.66`
- `LOW` **Dublin** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=11.162 but sourceUrl=null
  *current:* `11.162`
- `LOW` **Hilliard** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=11.162 but sourceUrl=null
  *current:* `11.162`
- `LOW` **Bexley** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=11.162 but sourceUrl=null
  *current:* `11.162`
- `LOW` **Grandview Heights** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=11.162 but sourceUrl=null
  *current:* `11.162`

## Dayton / Miami Valley (HIGH:0 MED:22 LOW:4)

- `MEDIUM` **Beavercreek** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Huber Heights** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Miamisburg** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.53¢ but currentRate=9.049, previousRate=8.71
  *current:* `11.53`
- `MEDIUM` **Miamisburg** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.73¢ but currentRate=9.049, previousRate=8.71
  *current:* `11.73`
- `MEDIUM` **Xenia** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.53¢ but currentRate=None, previousRate=8.71
  *current:* `11.53`
- `MEDIUM` **Xenia** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.73¢ but currentRate=None, previousRate=8.71
  *current:* `11.73`
- `MEDIUM` **Urbana** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Centerville** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.53¢ but currentRate=9.049, previousRate=8.71
  *current:* `11.53`
- `MEDIUM` **Centerville** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.73¢ but currentRate=9.049, previousRate=8.71
  *current:* `11.73`
- `MEDIUM` **Vandalia** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.53¢ but currentRate=9.049, previousRate=8.71
  *current:* `11.53`
- `MEDIUM` **Vandalia** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.73¢ but currentRate=9.049, previousRate=8.71
  *current:* `11.73`
- `MEDIUM` **Dayton** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 119d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Dayton** `RATE_CHANGE_NO_PREV`  
  rateChange=22.7% set but previousRate=null
  *current:* `22.7`
- `MEDIUM` **Dayton** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.691¢ but currentRate=8.71, previousRate=None
  *current:* `10.691`
- `MEDIUM` **Dayton** `COPY_RATE_MISMATCH`  
  hook mentions 10.69¢ but currentRate=8.71, previousRate=None
  *current:* `10.69`
- `MEDIUM` **Riverside** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 119d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Fairborn** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.53¢ but currentRate=9.049, previousRate=None
  *current:* `11.53`
- `MEDIUM` **Fairborn** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.73¢ but currentRate=9.049, previousRate=None
  *current:* `11.73`
- `MEDIUM` **Troy** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.53¢ but currentRate=9.049, previousRate=6.57
  *current:* `11.53`
- `MEDIUM` **Troy** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.73¢ but currentRate=9.049, previousRate=6.57
  *current:* `11.73`
- `MEDIUM` **Kettering** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.53¢ but currentRate=9.049, previousRate=None
  *current:* `11.53`
- `MEDIUM` **Kettering** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.73¢ but currentRate=9.049, previousRate=None
  *current:* `11.73`
- `LOW` **Dayton** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=8.71 but sourceUrl=null
  *current:* `8.71`
- `LOW` **Dayton** `STALE_60`  
  lastVerified=2026-08-19 (69d ago)
  *current:* `2026-08-19`
- `LOW` **Riverside** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.333 but sourceUrl=null
  *current:* `9.333`
- `LOW` **Riverside** `STALE_60`  
  lastVerified=2026-08-19 (69d ago)
  *current:* `2026-08-19`

## Cincinnati / SW Ohio (HIGH:15 MED:74 LOW:9)

- `HIGH` **Sharonville** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Springdale** `EXPIRED_ACTIVE`  
  termEnd=2026-08-31 passed 57d ago but status='pain_coming' — should be rollover
  *current:* `2026-08-31`
- `HIGH` **Mariemont** `EXPIRED_ACTIVE`  
  termEnd=2026-08-31 passed 57d ago but status='pain_coming' — should be rollover
  *current:* `2026-08-31`
- `HIGH` **Golf Manor** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Wayne Township (Warren Co)** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Batavia Township** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Williamsburg** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Seven Mile** `STALE_RENEWAL`  
  rollover termEnd=2025-09-30 expired 392d ago — any new contract?
  *current:* `2025-09-30`
- `HIGH` **Seven Mile** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Harrison** `EXPIRED_ACTIVE`  
  termEnd=2026-08-31 passed 57d ago but status='pain_coming' — should be rollover
  *current:* `2026-08-31`
- `HIGH` **Oxford Township (Butler Co)** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Madison Township (Butler Co)** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Lemon Township** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Cheviot** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Madeira** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `MEDIUM` **Sharonville** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Sharonville** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.276¢ but currentRate=None, previousRate=9.39
  *current:* `10.276`
- `MEDIUM` **Reading** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Norwood** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Norwood** `COPY_RATE_MISMATCH`  
  takeaway mentions 7.03¢ but currentRate=10.39, previousRate=6.67
  *current:* `7.03`
- `MEDIUM` **Cincinnati** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **West Chester Township** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Mason** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Blue Ash** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Montgomery** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Anderson Township** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 149d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Anderson Township** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Anderson Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=9.86, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Anderson Township** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=9.86, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Fairfield** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 149d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Fairfield** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Fairfield** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=9.39, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Milford** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Springdale** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Springdale** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=9.29, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Springdale** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=9.29, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Kenwood / Symmes Township** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Colerain Township** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 119d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Colerain Township** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Colerain Township** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=9.36, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Colerain Township** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=9.36, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Delhi Township** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 119d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Delhi Township** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Delhi Township** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=9.32, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Forest Park** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 149d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Forest Park** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Silverton** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 149d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Silverton** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Clearcreek Township** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 149d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Clearcreek Township** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Hamilton Township (Warren Co)** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=9.2, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Mariemont** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Sycamore Township** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Sycamore Township** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=10.21, previousRate=9.23
  *current:* `10.7`
- `MEDIUM` **Springfield Township (Hamilton Co)** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Springfield Township (Hamilton Co)** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=10.29, previousRate=9.45
  *current:* `10.7`
- `MEDIUM` **Green Township** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Lockland** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Union Township (Clermont Co)** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Miami Township (Clermont Co)** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Golf Manor** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **South Lebanon** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Turtlecreek Township** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Wayne Township (Warren Co)** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Morrow** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Batavia Township** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Williamsburg** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Tate Township** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Goshen Township** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **New Richmond** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Oxford** `STALE_RENEWAL`  
  rollover termEnd=2026-06-30 expired 119d ago — any new contract?
  *current:* `2026-06-30`
- `MEDIUM` **Oxford** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Seven Mile** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=None, previousRate=6.23
  *current:* `10.7`
- `MEDIUM` **Seven Mile** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=None, previousRate=6.23
  *current:* `10.7`
- `MEDIUM` **Harrison** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Harrison** `COPY_RATE_MISMATCH`  
  takeaway mentions 10.7¢ but currentRate=9.24, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Harrison** `COPY_RATE_MISMATCH`  
  hook mentions 10.7¢ but currentRate=9.24, previousRate=None
  *current:* `10.7`
- `MEDIUM` **Monroe** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Oxford Township (Butler Co)** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Madison Township (Butler Co)** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Lemon Township** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Trenton** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Wyoming** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Cheviot** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Madeira** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Mount Healthy** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Miami Township (Hamilton Co)** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **St. Bernard** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `MEDIUM` **Morgan Township (Butler Co)** `STALE_60`  
  lastVerified=2026-06-03 (146d ago)
  *current:* `2026-06-03`
- `LOW` **Reading** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.29 but sourceUrl=null
  *current:* `10.29`
- `LOW` **Norwood** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.39 but sourceUrl=null
  *current:* `10.39`
- `LOW` **Cincinnati** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.44 but sourceUrl=null
  *current:* `10.44`
- `LOW` **Deer Park** `STALE_60`  
  lastVerified=2026-08-19 (69d ago)
  *current:* `2026-08-19`
- `LOW` **Hamilton Township (Warren Co)** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.2 but sourceUrl=null
  *current:* `9.2`
- `LOW` **Hamilton Township (Warren Co)** `STALE_60`  
  lastVerified=2026-08-19 (69d ago)
  *current:* `2026-08-19`
- `LOW` **Liberty Township (Butler Co)** `STALE_60`  
  lastVerified=2026-08-19 (69d ago)
  *current:* `2026-08-19`
- `LOW` **Tate Township** `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['municipal utility']
  *current:* `['municipal utility']`
- `LOW` **Seven Mile** `STALE_60`  
  lastVerified=2026-08-19 (69d ago)
  *current:* `2026-08-19`

## Greater Toledo (HIGH:1 MED:12 LOW:22)

- `HIGH` **Washington Township (Wood)** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `MEDIUM` **Toledo** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 149d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Perrysburg** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 149d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Maumee** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 149d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Sylvania** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 149d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Oregon** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 149d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Lucas County Unincorporated** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 149d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Rossford** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 149d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Northwood** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 149d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Waterville** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 149d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Whitehouse** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 149d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Holland** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 149d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Washington Township (Wood)** `COPY_RATE_MISMATCH`  
  takeaway mentions 11.09¢ but currentRate=None, previousRate=8.63
  *current:* `11.09`
- `LOW` **Toledo** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Toledo** `STALE_60`  
  lastVerified=2026-08-19 (69d ago)
  *current:* `2026-08-19`
- `LOW` **Perrysburg** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Perrysburg** `STALE_60`  
  lastVerified=2026-08-19 (69d ago)
  *current:* `2026-08-19`
- `LOW` **Maumee** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Maumee** `STALE_60`  
  lastVerified=2026-08-19 (69d ago)
  *current:* `2026-08-19`
- `LOW` **Sylvania** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Sylvania** `STALE_60`  
  lastVerified=2026-08-19 (69d ago)
  *current:* `2026-08-19`
- `LOW` **Oregon** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Oregon** `STALE_60`  
  lastVerified=2026-08-19 (69d ago)
  *current:* `2026-08-19`
- `LOW` **Lucas County Unincorporated** `STALE_60`  
  lastVerified=2026-08-19 (69d ago)
  *current:* `2026-08-19`
- `LOW` **Rossford** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Rossford** `STALE_60`  
  lastVerified=2026-08-19 (69d ago)
  *current:* `2026-08-19`
- `LOW` **Northwood** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Northwood** `STALE_60`  
  lastVerified=2026-08-19 (69d ago)
  *current:* `2026-08-19`
- `LOW` **Waterville** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Waterville** `STALE_60`  
  lastVerified=2026-08-19 (69d ago)
  *current:* `2026-08-19`
- `LOW` **Whitehouse** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Whitehouse** `STALE_60`  
  lastVerified=2026-08-19 (69d ago)
  *current:* `2026-08-19`
- `LOW` **Holland** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.75 but sourceUrl=null
  *current:* `9.75`
- `LOW` **Holland** `STALE_60`  
  lastVerified=2026-08-19 (69d ago)
  *current:* `2026-08-19`
- `LOW` **Washington Township (Wood)** `STALE_60`  
  lastVerified=2026-08-19 (69d ago)
  *current:* `2026-08-19`

## NW & Central Ohio (HIGH:1 MED:8 LOW:1)

- `HIGH` **Tiffin** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `MEDIUM` **Lima** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Fremont** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Defiance** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Sandusky** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Port Clinton** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Kenton** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Wilmington** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Ashland** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `LOW` **Bucyrus** `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['municipal utility']
  *current:* `['municipal utility']`

## Eastern Ohio (HIGH:1 MED:10 LOW:0)

- `HIGH` **Chillicothe** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `MEDIUM` **Zanesville** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Cambridge** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Athens / Ohio University Area** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Chillicothe** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Circleville** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Logan** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Gallipolis** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Portsmouth** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Ironton** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Jackson** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`

## Municipal Utilities (HIGH:10 MED:4 LOW:1)

- `HIGH` **Wellsville** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Cortland** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Liberty Center** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Hamler** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **West Unity** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Stryker** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Wauseon** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Coldwater** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Delphos** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `HIGH` **Ada** `AGG_NO_RATE`  
  confirmed_active_aggregation but currentRate=null
  *current:* `null`
- `MEDIUM` **Cleveland Public Power** `STALE_60`  
  lastVerified=2026-05-01 (179d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Columbus Division of Power** `STALE_60`  
  lastVerified=2026-05-01 (179d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Piqua** `MUNI_IOU_NOTES`  
  municipal_utility zone but notes reference IOU names: ['AES Ohio']
  *current:* `['AES Ohio']`
- `MEDIUM` **Hamilton** `STALE_60`  
  lastVerified=2026-05-01 (179d ago)
  *current:* `2026-05-01`
- `LOW` **Cleveland Public Power** `IOU_MUNI_NOTES`  
  non-muni zone but notes contain muni/coop keywords: ['municipal utility']
  *current:* `['municipal utility']`

## Electric Cooperatives (HIGH:0 MED:4 LOW:0)

- `MEDIUM` **Darke Rural Electric** `COOP_IOU_NOTES`  
  electric_cooperative zone but notes reference IOU names: ['AES Ohio']
  *current:* `['AES Ohio']`
- `MEDIUM` **Holmes-Wayne Electric** `COOP_IOU_NOTES`  
  electric_cooperative zone but notes reference IOU names: ['Ohio Edison']
  *current:* `['Ohio Edison']`
- `MEDIUM` **Mid-Ohio Energy** `COOP_IOU_NOTES`  
  electric_cooperative zone but notes reference IOU names: ['Ohio Edison']
  *current:* `['Ohio Edison']`
- `MEDIUM` **South Central Power** `COOP_IOU_NOTES`  
  electric_cooperative zone but notes reference IOU names: ['AEP Ohio']
  *current:* `['AEP Ohio']`

## Other Ohio Markets (HIGH:0 MED:10 LOW:4)

- `MEDIUM` **Medina City** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Struthers** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Poland Township** `STALE_RENEWAL`  
  rollover termEnd=2026-05-31 expired 149d ago — any new contract?
  *current:* `2026-05-31`
- `MEDIUM` **Poland Township** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Licking County / Pataskala** `STALE_60`  
  lastVerified=2026-05-01 (179d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Athens County (Rural AEP)** `STALE_60`  
  lastVerified=2026-05-01 (179d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Guernsey / Noble / Morgan Counties** `STALE_60`  
  lastVerified=2026-05-01 (179d ago)
  *current:* `2026-05-01`
- `MEDIUM` **Steubenville** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **Marietta** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `MEDIUM` **McConnelsville / Morgan County** `STALE_60`  
  lastVerified=2026-06-01 (148d ago)
  *current:* `2026-06-01`
- `LOW` **Crosby Township** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.88 but sourceUrl=null
  *current:* `9.88`
- `LOW` **Medina City** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.5 but sourceUrl=null
  *current:* `9.5`
- `LOW` **Licking County / Pataskala** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=10.01 but sourceUrl=null
  *current:* `10.01`
- `LOW` **Russells Point** `RATE_NO_SOURCE`  
  confirmed agg with currentRate=9.26 but sourceUrl=null
  *current:* `9.26`

## Documentation (HIGH:0 MED:0 LOW:2)

- `LOW` **CLAUDE.md** `DOC_COUNT_MISMATCH`  
  CLAUDE.md claims 251 zones but actual=427
  *current:* `claimed=251 actual=427`
- `LOW` **CLAUDE.md** `DOC_COUNT_MISMATCH`  
  CLAUDE.md claims 18 JSON files but actual=20
  *current:* `claimed=18 actual=20`

---
*Finding lists generated by scripts/daily_audit.py at 89fc067, run read-only on main 7d84e19 — 2026-10-27. Comparison, contradictions, stale dates, and the research table were read from the zone files and docs/research on that same tree.*
