# Factual review, 2026-11-12

Scheduled review of `data/regions/*.json` (427 zones) for statements that are not factual.

## Fixed in this pass

**AES Ohio standard offer was wrong in Beavercreek, Huber Heights, and Urbana** (`dayton_aes_suburbs.json`).
These zones said the AES standard rate "hit 10.691¢ June 2026 (+22.7%)", with 8.71¢ as the prior rate.
The repo's own verified price to compare (`data/research/price_to_compare.json`, from the PUCO Apples to Apples AES page, accessed 2026-10-15) is 10.86¢ for June 1, 2026 to May 31, 2027.
`data/research/market_increases.json` records the step as 9.45¢ → 10.856¢, about 15% (EnergyChoiceMatters, 2026-04-15).
8.71¢ and 10.691¢ are Dayton's SOPEC aggregation rates, not the AES standard offer.
Changes: currentRate 10.86, previousRate 9.45, rateChange 14.9, status `pain_hit` (the increase took effect in June, so `pain_coming` no longer applied), takeaway and hook rewritten, and sourceUrl set.
Nine removal notes were appended to `data/history/removal_notes.jsonl`. The removed values are not in the notes.

## Needs verification (not changed: the source pages were blocked in this session)

1. **Dayton is probably still on SOPEC, not on AES default.** `dayton_sw_ohio.json` says the aggregation "expired June 30" and accounts "jumped … with no contract." In a search snippet, Dayton's city aggregation page lists SOPEC Green at 10.691¢ (Brown 10.576¢) from June 2026 to May 2027, with AEP Energy as supplier. If that is right, the hook is false, status should not be `rollover`, and currentRate should be 10.691 (with 8.71 kept as the genuine prior rate). I couldn't open daytonohio.gov or sopec-oh.gov from this session.
2. **Riverside** (`dayton_sw_ohio.json`) makes the same "expired, now on AES default" claim with no source. It is also a SOPEC community, so it may have renewed the way Dayton did.
3. **Huber Heights** says "No confirmed aggregation," but a 2025 SOPEC opt-out letter for Huber Heights is posted on hhoh.org (DocumentCenter/View/7153).
4. **"Ohio Valley Electric Cooperative"** (`ohio_electric_cooperatives.json`) doesn't appear to exist. Searches only find Ohio Valley Electric Corporation (OVEC), a utility-owned generator in Piketon. Jackson County co-op service is Buckeye Rural Electric. The investigation queue already lists Hancock-Wood Electric and North Western Electric as missing from the co-op file. The "2 Unconfirmed" placeholder record is not a real entity either. Confirm against the ohioec.org roster, then delete the record and add the two missing co-ops.
5. **The Duke standard offer is out of date in about 15 Cincinnati-suburb zones.** They store currentRate 10.7 with status `pain_coming` and no source. 10.70¢ was the June 2026 Duke price to compare. The verified October figure in `price_to_compare.json` is 10.49¢. These zones are Mason, Blue Ash, Montgomery, Kenwood/Symmes, Springboro, Morrow, Tate Township, Goshen Township, New Richmond, Trenton, Mount Healthy, Miami Township, St. Bernard, and Morgan Township. Hamilton Township's takeaway also says "10.70¢+".
6. **Cincinnati** (`cincinnati_duke.json`): 10.44¢ is correct for May to November 2026 (city page and Dynegy page), but that term ended about November 1. The next term is variable, and the city and Dynegy pages give different end dates (May 2029 and June 2028). Status `stable` and the 10.44¢ hook are now out of date.
7. **Hamilton Township (Warren Co)** has confidence `high` with no sourceUrl. Its currentRate (9.2) is the expired Constellation rate, while the takeaway says accounts are on the Duke default.
8. **Stark County (Unincorporated)** has a termStart and termEnd on a record whose status is `no_aggregation_verified`, and the termEnd (2026-08-31) has already passed.
9. **CLAUDE.md** describes "Dayton/AES Ohio: 8.71¢ → 10.691¢ (+22.7%)" as the AES rate. Those figures are Dayton's SOPEC rate. The AES standard offer step was 9.45¢ → 10.86¢ (+15%).

## Systemic

- 51 zones have confidence `high` but no sourceUrl (most are municipal utilities, plus Columbus, Gahanna, Grove City, Ontario, Westerville, Dayton, Riverside, Toledo, Perrysburg, Maumee, Cincinnati, and Sharonville).
- 35 zones still say `confirmed_active_aggregation` after their termEnd has passed. Most are correctly marked `rollover`, but the aggregationStatus label now reads as a current fact.

Network note: ohioec.org, sopec-oh.gov, daytonohio.gov, and hhoh.org could not be reached from this session. Allow them in the environment's network settings to let a future run verify items 1–4.
