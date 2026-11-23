Non-factual data audit — 2026-11-22

Scope: all 427 zone records in data/regions/*.json (19 files incl.
merged_confirmed.json). Automated consistency checks plus manual read of
flagged records. Read only: no zone data was changed by this pass. Every
item below needs a verified source before an edit. Removals follow the
CLAUDE.md history rule: one-line note, no removed value.

## 1. Stored rateChange contradicts the record (shown in UI)

rate_change.py uses a stored rateChange whenever one rate is missing, and
the disagreement report only checks zones that have both rates. Each of
these percentages is wrong but is displayed.

| Zone | File | Stored | What the record supports |
|---|---|---|---|
| Sharonville | cincinnati_duke | +42.9% | currentRate null. Takeaway gives 10.276¢ vs prior 9.39¢ = +9.4% |
| Washington Township (Wood) | toledo_lucas_noac | +13.0% | currentRate null. Notes give 11.09¢ vs prior 8.63¢ = +28.5% |
| Dayton | dayton_sw_ohio | +22.7% | previousRate null. 8.71 is stored as *current*, but the takeaway says it expired |

## 2. Unsourced placeholder priors that are not flagged

Trumbull County priors of exactly 7.9¢. The text says "~7.90¢". No
sourceUrl. Status is pain_hit, confidence high. The rule in rate_change.py
only flags 7.9 on *Mahoning* townships. These six get an unlabeled +28.4%:
Trumbull County, Howland Township, Weathersfield Township, Vienna Township,
Champion Township, Bazetta Township (youngstown_warren.json).

Parma (cleveland_cuyahoga) notes: "Prior cycle approx 7.0¢. Cumulative
increase ~43%." This has no source and is not a stored field.

## 3. Records that contradict themselves

- Dayton: supplier is "SOPEC". SOPEC is an aggregation council, not a
  supplier. currentRate 8.71 belongs to a term that ended 2026-06-30. The
  takeaway says accounts are now on ~10.691¢. "Biggest rate shock in the
  state" has no source, and the record has no sourceUrl.
- Pepper Pike: aggregationStatus is confirmed_active_aggregation, but the
  notes say "Likely NOPEC member but unconfirmed".
- Wayne Township (Warren Co): supplier is "Dynegy", but the notes say
  "Supplier likely Dynegy … unconfirmed".
- Delhi Township: termEnd 2026-06-30 is "approximate … based on Energy
  Alliances pattern". It is inferred, not sourced.
- Stark County (Unincorporated): no_aggregation_verified, but the record
  carries termStart 2025-08-01 and termEnd 2026-08-31 with no program.
- Turtlecreek Township: "52% … over two renewals" and "two consecutive
  large increases". The record shows only one prior (6.56¢ to May 2025)
  and does not account for June 2025–May 2026.

## 4. Stale claims (dates now in the past)

- Cincinnati: term ended 2026-11-01. Status is still stable and the
  10.44¢ is presented as current. lastVerified is 2026-06-01.
- Sharonville: "WGL Energy 10.276¢ beginning November 2026". This is
  future tense, verified 2026-06-01.
- Miami Township (Clermont): "is moving … starting June 2026".
- Fairfield: "Renewal into Duke's 10.70¢ environment is imminent — a 14%
  increase". This is a projection stated as fact, from June 2026. Anderson
  Township and Clearcreek Township use the same "imminent" language.
- Girard: "accounts likely defaulted". This is speculation and still
  unconfirmed since June 2026.
- 33 rollover records still show an expired term's rate in currentRate.
  That is genuine history, but the UI labels it current.

## 5. Non-zone and unsourced filler

- ohio_electric_cooperatives.json has a "Ohio Electric Co-ops — 2
  Unconfirmed" record. Its own notes call it a placeholder. It is not a
  real zone and it counts toward zone totals. The file has 24 records
  (23 real co-ops plus this one), but CLAUDE.md says 25 co-ops.
- Population figures ("~8,600", "~20,000", etc.) and superlatives ("Largest
  unincorporated township…", "Highest pain in Clermont County", "One of the
  largest rate shocks in Warren County") appear in about 25 notes with no
  source.
- 30 high-confidence active-aggregation records have no sourceUrl,
  including Columbus, Toledo, Dayton, Dublin, Hilliard, Perrysburg, Sylvania
  and the Trumbull townships. 134 records overall carry a rate or supplier
  with no sourceUrl.

## Suggested code fix

In rate_change.py, check stored rateChange values when a rate is missing
against any rate stated in the record's own text, or stop displaying them.
Extend the 7.9 placeholder flag to Trumbull County zones.
