# FORGE fact review — 2026-11-11

Scope: all 20 files in `data/regions/` (427 records). Each record was checked against itself (rate math, term dates against today, classification against its fields) and against the research files from 2026-10-14/15 (`data/research/forge_corrected_dataset.csv`, `merged_summary.md`). No live web check was done in this pass. Removal notes went to `data/history/removal_notes.jsonl`, and no removed value was written there.

## Fixed in this pass

| Zone | File | Problem | Fix |
|---|---|---|---|
| Licking County / Pataskala | remaining_ohio_markets | AEP Energy 10.01¢ (9.08→10.01, Jun 2026–Jun 2027) was copied from Columbus. Three sources show Dynegy 10.29¢, Dec 2025–Dec 2026, with no auto-renew. | Set to the sourced Dynegy term. Rewrote the takeaway and hook. |
| Heath / Newark | sopec_columbus_suburbs | The 10.01/9.08/10.2 values were logged as removed on 2026-10-15 but were still stored. | Newark is set to Dynegy 10.29¢ to Dec 2026. The Heath conflict is kept in the notes. |
| Pickerington, Marysville | sopec_columbus_suburbs | "AEP aggregation 9.08→10.01¢" was the copied Columbus figure. No program appears on the SOPEC, Dynegy or Energy Alliances lists. | Removed the supplier, rates and term. The takeaway now says no program was found. |
| Dublin | sopec_columbus_suburbs | Was listed as a SOPEC member at 11.162¢. Dublin is not on the SOPEC member list. | Changed to unresolved / verify. Removed the SOPEC supplier, rates and hook. |
| Beavercreek | dayton_aes_suburbs | Was marked "no aggregation". Three sources show Constellation 8.699¢ through Dec 2026, and Res. 26-36 caps the successor at 10.699¢. | Reclassified as active aggregation and rewrote the takeaway and hook. |
| Niles | ne_ohio_firstenergy | Was treated as an Ohio Edison sales market. Niles is a municipal electric utility and an AMP member. | Changed to municipal_utility / municipal_blacklist. |
| Mansfield | ne_ohio_firstenergy | Was marked "no aggregation". Mansfield joined NOPEC in 2026 at the 10.399¢ Standard price. | Reclassified as active aggregation. |
| Sharonville | cincinnati_duke | rateChange was 42.9% with no current rate. The stored figures support about 9.4%. | Cleared rateChange. |
| Washington Twp (Wood) | toledo_lucas_noac | rateChange was 13.0% with no current rate. | Cleared rateChange. |
| Stark County (Unincorporated) | akron_summit_medina | Term dates were set on a zone with no aggregation. | Cleared the term dates. |
| Delhi Township | cincinnati_duke_suburbs | Said "expiring this month" about a June 2026 estimate. | Reworded to past tense and noted the end date is unverified. |

## Still open — needs a call or a source

1. **AES Ohio default rate.** About 6 records say 10.691¢ (Dayton, Urbana, Huber Heights and others). PUCO Apples-to-Apples shows the AES PTC at **10.86¢** (Jun 2026–May 2027). The CLAUDE.md market fact also says 10.691. Confirm which figure is right before you use it in a pitch.
2. **Duke PTC "10.70¢".** Many Cincinnati-area hooks quote 10.70¢. The 2026-10-15 research shows Duke at 10.49¢ (Oct 2026).
3. **Huber Heights, Logan, Gallipolis, Athens County, McConnelsville.** These are marked "no aggregation", but research lists them as SOPEC members (escalate-call). Confirm before changing.
4. **Urbana.** Marked "no aggregation". A single source (Dynegy page) shows 9.08¢, Dec 2025–May 2028.
5. **Supplier mismatches** in research that are not yet applied (escalate-call or likely): Hamilton Twp (Warren), Mariemont, Harrison, Batavia Twp, Seven Mile, Cheviot, Madeira, Whitehouse, Green. The rollover edits in #14 for Mariemont and Harrison conflict with research showing new Dynegy and Constellation terms.
6. **Cincinnati.** The fixed window ended 2026-11-01, but the status is still "stable". The contract continues as variable pricing, so the hook should change.
7. **Dayton.** The takeaway says accounts "are now on AES standard supply". This is not sourced, and sourceUrl is null.
8. **51 records marked confidence "high" have no sourceUrl** (for example Columbus, Cincinnati, Dayton, Sharonville).

## Wording corrected after a live page check (2026-11-11)

The table above is the first pass. These three rows were corrected against the live pages. Stored rates were not changed.

- **Licking County / Pataskala** and **Heath / Newark** stay on Dynegy at 10.29¢ through December 2026. The no-renewal wording and the Heath conflict note are removed. The county page lists Heath in Group 1, and the Dynegy Heath page lists Heath as eligible. Dynegy lists a successor term at 11.87¢ (Dec 2026–May 2028) on the Pataskala, Newark, and Heath pages; the county page does not. That rate is not stored. Confirm on the county page before quoting.
- **Beavercreek** stays on Constellation at 8.699¢ through December 2026. The city is pausing aggregation after that term because it could not get a rate under 10.699¢. Accounts return to AES Ohio default service at 10.86¢ through May 31, 2027. The takeaway and hook do not imply a successor contract.
