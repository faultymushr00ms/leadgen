# Fact audit — 2026-11-17

This pass checked all 427 zone records in `data/regions/` against their own fields and against the sourced figures already in `data/research/`. A record was corrected only where a source in the repo contradicts it. Everything else is listed under "Flagged, not changed".

## Corrected

Removal notes for each field are in `data/history/removal_notes.jsonl`. Correction events are in `data/research/corrections.jsonl` (ids start with `fact-audit-`).

| Zone | Was | Now | Basis |
|---|---|---|---|
| Dayton | Aggregation "expired June 30, 2026", accounts "now on AES standard supply", "biggest rate shock in the state"; current 8.71, status rollover | SOPEC/AEP Energy 10.691¢ (100% renewable) June 2026 – June 2027 meter read; prior 8.71; +22.7%; pain_hit | EnergyChoiceMatters 2026-04-09 (already in `news_council_sweep.csv`) |
| Riverside | "Expired June 30, 2026", flipped to AES default; current 9.333 | 10.691¢ through June 2027; prior 9.333; +14.6%; pain_hit | Same source: "also applies to … the City of Riverside" |
| Beavercreek | No aggregation; "AES standard rate hit 10.691¢ (+22.7%)"; prior 8.71 | Constellation aggregation 8.699¢, Aug 2025 – Dec 2026; pain_coming | City aggregation page (research dataset). The AES standard offer is 9.45 → 10.856¢ (≈15%), not 10.691 |
| Huber Heights | Same false AES claim, prior 8.71 | Rates cleared, aggregation `unresolved`, status verify | SOPEC rate page lists 11.19¢ (unconfirmed). Hook now uses the sourced AES ≈15% step |
| Urbana | Same false AES claim, prior 8.71 | Rates cleared, aggregation `unresolved`, status verify | Dynegy page lists 9.08¢ (unconfirmed) |
| Sharonville | rateChange 42.9 with no current rate | rateChange cleared | Its own notes give 9.39 → 10.276 (≈9.4%) |
| Washington Township (Wood) | rateChange 13.0 with no current rate | rateChange cleared | Its own notes give 8.63 → 11.09 (≈28.5%) |

The 10.691¢ figure is the Dayton SOPEC aggregation rate. It had been copied onto non-aggregation AES suburbs as the "AES standard rate". The research dataset's `PRIOR_rate` of 10.691 on those three zones is cleared by the new correction events.

The genuine prior Dayton and Riverside terms (8.71¢ and 9.333¢, ending June 2026) are kept as `previousRate` and in `rate_ledger.csv`. The journal has two `superseded_term` events for these terms. Those events replay as edits, so two later `update` events reapply the corrected values. The journal is append-only, so the earlier events stay in it.

`tests/test_rate_change.py` expected Dayton's old record shape (no prior rate, stored Δ%). It now expects prior 8.71 and a computed Δ% of 22.7.

## Flagged, not changed (need a source or a decision)

1. **"Ohio Valley Electric Cooperative"** (`ohio_electric_cooperatives.json`). A web search found no Ohio co-op by this name. Only Ohio Valley Electric *Corporation* (OVEC, a wholesale generator) came up, and Jackson County is served by Buckeye Rural Electric. Two real Buckeye Power members are missing from the file: **Hancock-Wood Electric** and **North Western Electric**. The "2 Unconfirmed" placeholder is probably those two. ohioec.org is blocked from this session, so the roster could not be confirmed directly.
2. **`previousRate` 8.71 on Miamisburg, Centerville, Vandalia, Xenia** (MVCC/Constellation zones). The record has no source, and 8.71 matches Dayton's SOPEC rate. Kettering and Fairborn are in the same MVCC program and have no prior rate. This is probably the same copy error, but no source contradicts it directly.
3. **Wellsville and Cortland** are in `ohio_municipal_utilities.json` but are tagged as Dynegy aggregations with "high" utility confidence and no source. Wellsville's utility (AEP Ohio) is unverified.
4. **Stale statuses:**
   - **Cincinnati** has `stable` with a term that ended 2026-11-01.
   - **Stark County (Unincorporated)** has `stable` with a term that ended 2026-08-31, on a no-aggregation record.
   - **20 records** say `pain_coming` although their new rate started months ago: Columbus, Gahanna, Grove City, Reading, Norwood, Dublin, Hilliard, Worthington, Bexley, Grandview Heights, Reynoldsburg, Lancaster, Licking County/Pataskala, Massillon, North Canton, plus the MVCC zones.
5. **Westerville** has no `lastVerified` and no source.
6. **Unsourced figures:** 83 records have a rate and 93 have a supplier with no `sourceUrl`. About a dozen Duke-area suburbs carry an identical 10.7¢ with no source. Check whether that is an aggregation rate or an old Duke Price to Compare; the October 2026 Duke Price to Compare is 10.49¢.
7. **Missing rateChange:** 102 records have both rates but a null `rateChange`. This is derived and not wrong, but the Hotspots heat sort ignores them.
