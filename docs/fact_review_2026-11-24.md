# Fact review: zone data, 2026-11-24

Scheduled scan of all 427 records in `data/regions/*.json` for claims that are stale, internally contradictory, or unsupported. No web sources were opened in this pass. Every finding below comes from the record's own fields or from comparing a record against today's date.

## Fixed in this pass

| Zone | File | Problem | Change |
|---|---|---|---|
| Reading, Norwood | cincinnati_duke | `pain_coming`, but the hook said "is moving into"; the term began 2026-06-01 | `pain_hit`, past-tense takeaway and hook |
| Columbus, Gahanna, Grove City | columbus_aep | Same: terms began June/July 2026 | `pain_hit`, past tense |
| Licking County / Pataskala | remaining_ohio_markets | Same; the hook also claimed "lots of build-out hasn't set up supply contracts", which no source supports | `pain_hit`, past tense, unsupported claim dropped |
| Dublin, Hilliard, Bexley, Grandview Heights | sopec_columbus_suburbs | Hooks said the rate is "going over 11¢ in June" and to call "before it hits". That happened 2026-06-01. Dublin's hook also said tech firms "haven't locked in alternatives", which no source supports | `pain_hit`, past tense, unsupported claim dropped |
| Sharonville | cincinnati_duke | `rateChange` 42.9 doesn't match any rate stored on the record (10.276 / 9.39 works out to +9.4%), and `currentRate` is null | `rateChange` → null, removal note logged |
| Washington Township (Wood) | toledo_lucas_noac | `rateChange` 13.0 doesn't match the stored prior rate (8.63) or the stored future rate (11.09), and `currentRate` is null | `rateChange` → null, removal note logged |
| Powell | sopec_columbus_suburbs | Classified `no_aggregation_verified`, but its own sourced text describes council approval of NOPEC and enrollment in September 2026 | `confirmed_active_aggregation`, removal note logged |
| Plain City | merged_confirmed | Classified `no_aggregation_verified`, but its own sourced text describes NOPEC enrollment and a quoted price | `confirmed_active_aggregation`, removal note logged |

Removal notes went to `data/history/removal_notes.jsonl` in the existing format, without the removed values. Nothing in `data/history/` was deleted.

## Needs a decision or a source (not changed)

1. **Dayton** (dayton_sw_ohio): the term expired 2026-06-30, but the record still stores `currentRate: 8.71`, which is the expired rate. `rateChange: 22.7` sits on a record with no `previousRate`. The fix is probably to move 8.71 into `previousRate` as genuine history. That changes how the hotspot card renders, so it was left for review. `supplier: "SOPEC"` also needs a source: Dayton isn't on the SOPEC roster in this file set.
2. **Cincinnati** (cincinnati_duke): `termEnd` 2026-11-01 has passed, but the status is still `stable` and the record still has 10.44¢ as the current rate. The notes say a variable structure follows. The rate after November 1 is unverified.
3. **Worthington** (sopec_columbus_suburbs): marked `pain_coming`, but the stored move is a decrease, 11.162 → 10.69, and the term started June 2026. The stored `previousRate` may be SOPEC's new rate rather than what Worthington actually paid before.
4. **Records that say the stored value is wrong.** On nine records the hook or takeaway says the stored rate is outdated ("The file still has…"), but the stored value was never changed. Those records are Akron, Green, North Canton, Massillon, Brecksville, Norton, Lancaster, Youngstown and Austintown Township. On each one the hook is a research note, not something a rep can say on a call. Example: Youngstown stores 7.99¢, while the city letter and Dynegy both show 9.97¢.
5. **Supplier set where the record says there is no aggregation:** Wyoming (Dynegy, but the program ended July 2026), Westlake (Dynegy, ended June 2026), and Unity Township, Marble Cliff, New Concord, Norwich and Piketon (AEP Energy, no program or rate stored).
6. **Stark County (Unincorporated)**: the record has term dates (2025-08-01 → 2026-08-31) and status `stable`, but no program exists.
7. **Co-ops**: eight co-op records use `futureUse: address_check`. CLAUDE.md says co-ops use `municipal_blacklist`: Butler, Darke, Frontier, Holmes-Wayne, LMRE, North Central, Pioneer and Midwest Energy & Communications.
8. **Past increases written in the future tense** (notes and takeaways, statuses already past-dated): Miami Township (Clermont), Willoughby, Eastlake, North Olmsted, Brook Park, Seven Hills, Highland Heights, Richmond Heights, Lyndhurst, University Heights, Cleveland Heights, Rocky River, Olmsted Falls, Norton and Mentor-on-the-Lake. All of them say "rising/starting June 2026", which is now past.
9. **83 records store a `currentRate` with no `sourceUrl`.** Most are Duke suburbs at the generic 10.7¢ and eastern Ohio AEP zones at 10.19¢ or 11.262¢. Under the history rules these are unsourced values, so they're candidates for removal if a verified source contradicts them.
10. **Westerville** (columbus_aep) has no `lastVerified`.

## Correct as stored

The Dayton-area MVCC zones (Kettering, Fairborn, Centerville, Miamisburg, Vandalia) are still `pain_coming`. That's correct: the stored Dynegy 11.53¢ term starts December 2026. Reynoldsburg, Lancaster, North Canton and Massillon have started terms but are tracked in item 4.
