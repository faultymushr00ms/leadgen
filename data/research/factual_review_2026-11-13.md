# Factual review, 2026-11-13

Scheduled review. Earlier runs (11-04 to 11-12) covered `data/regions/` only. This pass covered the 29 gas zones in `data/gas/`, which had never been reviewed, plus stale wording in the electric files that the open branches don't fix.

Note: no route loads `data/gas/` yet. Every `_load_zones()` call uses the default `commodity="electric"`. The gas errors below are not visible in the app today, but they would show up as soon as the gas layer is wired in.

## Fixed in this pass

| Zones | File | Problem | Fix | Source |
|---|---|---|---|---|
| All 8 Toledo-area gas zones | `toledo_gas.json` | Gas utility given as Dominion Energy Ohio. Toledo-area gas is Columbia Gas of Ohio (NiSource). | `gasUtility` set to Columbia Gas of Ohio. Confidence is high for Toledo and medium for the Wood County suburbs. | [Columbia Gas PUCO filing](https://www.columbiagasohio.com/docs/librariesprovider5/rates-and-tariffs/ford-street-application-and-attachment-a.pdf) (about 145,000 Lucas County customers) |
| All 8 Toledo-area gas zones | `toledo_gas.json` | Said NOAC is electric-only with no gas program. NOAC ran an opt-out gas aggregation with Constellation through May 2024 and paused it pending a price under its threshold. | Rewrote the takeaway, hook and notes. Current NOAC gas status is marked unconfirmed. | [NOAC gas restart FAQ, May 2024](https://www.hollandohio.com/wp-content/uploads/2024/05/NOAC-Gas-Agg-Program-Restart-FAQs-5-1-24-final.pdf) |
| All 13 NE Ohio gas zones | `ne_ohio_gas.json` | Named Dominion Energy Ohio, which became Enbridge Gas Ohio on March 7, 2024. Cleveland's note also said the utility was "formerly Columbia Gas of Ohio", which is a separate company. | Renamed to Enbridge Gas Ohio, with the former name kept in the notes. | [Dominion transition page](https://www.dominionenergy.com/ohio/enbridge-update) |
| Cleveland gas | `ne_ohio_gas.json` | Said Cleveland's electric aggregation had expired (Constellation rollover). The sourced electric zone shows SOPEC/AEP Energy at 10.457¢ through July 2027. | Electric claims now match the electric zone. | Electric zone sourceUrl |
| Parma, Strongsville, Solon gas | `ne_ohio_gas.json` | Hooks said electric "just hit 9.999" under NOPEC. The electric zones show 10.399¢. | Hooks updated to 10.399. | Electric zones |
| Euclid gas | `ne_ohio_gas.json` | Called Euclid a NOPEC member at 9.999. The electric zone shows a Dynegy city program at 9.95¢ through June 2028. | Notes and hook corrected. | Dynegy Euclid page (electric zone) |
| Lakewood gas | `ne_ohio_gas.json` | Said Lakewood runs its own electric program independent of NOPEC. That classification was already removed from the electric zone on 2026-10-15, and Lakewood is NOPEC. | Corrected. | NOPEC pricing page (electric zone) |
| Westlake gas | `ne_ohio_gas.json` | "Confirmed" no gas aggregation, with high confidence. The only basis was the electric zone notes. | Status set to verify, confidence low. | — |
| Oxford gas | `cincinnati_gas.json` | Called Oxford's electric "AEP territory". Duke delivers electric there, and AEP Energy is only SOPEC's supplier. | Corrected. | SOPEC Oxford page (electric zone) |
| Colerain Township, Oxford (electric) | `cincinnati_duke_suburbs.json` | Takeaways and hooks still said the contract "expires this month" (June). Oxford also said "renewal underway" and quoted Duke default at 10.7016¢. | Rewritten in past tense with the successor marked unconfirmed. The Duke default is now the October 10.49¢ price to compare. | Term dates in record; `price_to_compare.json` |
| Settings page | `templates/settings.html` | Utility dropdown listed "Dominion Energy Ohio". | Renamed to Enbridge Gas Ohio. | As above |

28 removal notes were appended to `data/history/removal_notes.jsonl`. They don't contain the removed values. Existing history lines are unchanged.

## Still open: needs a source or a call

1. **Hubbard gas**: "Gas aggregation through Major Energy is CONFIRMED", but there's no source. Hubbard was not checked this pass.
2. **Medina County gas**: "confirmed to exist", but there's no source.
3. **Liberty Township (Butler)**: two electric records disagree. `merged_confirmed.json` has Constellation at 10.099¢, stable through 2027-07. `cincinnati_duke_suburbs.json` has a 9.37¢ rollover that ended 2026-07-31. The gas record follows the rollover version.
4. **NOAC electric**: CLAUDE.md says "9.75¢ through ~June 2027, stable". All 8 NOAC electric zones store 9.75¢ with termEnd 2026-05-31 and status rollover. One of the two is wrong.
5. **Delhi Township**: same "this month" wording. It is already fixed on PR #16, so it was left alone here to avoid a merge conflict.
6. Open items from the 11-11 and 11-12 reviews are still open. These cover the AES 10.691 vs 10.86 figure, Duke 10.70 vs 10.49 in about 15 zones, Dayton SOPEC renewal, Huber Heights, "Ohio Valley Electric Cooperative", and 51 high-confidence zones with no sourceUrl.

## Unmerged fact-check work

`main` hasn't changed since 2026-11-02. Corrections from earlier runs are sitting unmerged:

- PR #16 (`claude/friendly-feynman-9m8r0v`): 11-11 fact-check.
- PR #15 (`cursor/dayton-aggregation-renewal-a97f`): Dayton at 10.691¢ through June 2027.
- Branch `claude/friendly-feynman-4yq6dp` (no PR): AES standard offer fix in Beavercreek, Huber Heights and Urbana. It overlaps PR #16 on Beavercreek.
- Branch `claude/friendly-feynman-qxqch9` (no PR): an earlier Dayton correction that overlaps PR #15.
