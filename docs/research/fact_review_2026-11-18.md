# FORGE data fact review — 2026-11-18

This was an automated consistency audit of all 427 zone records in `data/regions/*.json`. It compared each record's fields with each other, with today's date, and with CLAUDE.md. The data files were not edited. Each finding still needs a source check before anything is removed. CLAUDE.md requires that incorrect values are deleted with a one-line removal note, and that genuine superseded values are kept as history.

## A. Numbers that are wrong by arithmetic
| Zone (file) | Problem |
|---|---|
| Sharonville (cincinnati_duke) | `rateChange` 42.9 with `currentRate` null. The text gives WGL at 10.276¢ against a prior of 9.39¢, which is +9.4%, not +42.9%. |
| Washington Township, Wood (toledo_lucas_noac) | `rateChange` 13.0 with `currentRate` null. The text gives 11.09¢ against a prior of 8.63¢, which is +28.5%. The record is also in the NOAC file, but its text says "Wood County Dynegy program". |
| Dayton (dayton_sw_ohio) | `currentRate` 8.71 is the expired rate. `previousRate` is null and `rateChange` is 22.7. The takeaway says the accounts are now about 10.691¢. `supplier` is "SOPEC", which is an aggregator, not a supplier. No `sourceUrl`. "Biggest rate shock in the state" is unsourced. |
| Hamilton Township, Warren (cincinnati_duke_suburbs) | `currentRate` 9.2 (Constellation, expired 2026-07-31), but the takeaway says the accounts are on Duke default at 10.70¢. No `sourceUrl`. |

## B. Status contradicted by the record's own text
| Zone (file) | Problem |
|---|---|
| Clinton (akron_summit_medina) | `no_aggregation_verified`, and the notes say "No municipal or township aggregation program found". The takeaway and hook say Clinton is on NOPEC's map and in the 2026 annual report at 10.399¢. The notes also hold a street address ("2534 W Comet Rd"). |
| Plain City (merged_confirmed) | `no_aggregation_verified`, but the text says accounts enrolled in NOPEC's standard program. |
| Powell (sopec_columbus_suburbs) | `no_aggregation_verified`, but the text says council approved NOPEC and accounts enrolled in September 2026. The record is in the SOPEC file, but the program is NOPEC. |
| Salem, Alliance (ne_ohio_firstenergy) | `currentRate` (9.79 / 10.399) is set on non-aggregation zones with no source. Salem's own takeaway says the figure is unlabeled. |

## C. Stale as of today (claims that time has overtaken)
- 20 zones are `pain_coming`, but `termStart` has already passed. The increase has already happened. Zones: Reading, Norwood, Columbus, Gahanna, Grove City, Miamisburg, Centerville, Vandalia, Fairborn, Kettering, North Canton, Massillon, Licking County/Pataskala, Dublin, Hilliard, Worthington, Reynoldsburg, Bexley, Grandview Heights, Lancaster.
- Cincinnati: `termEnd` 2026-11-01 has passed, but the status is still `stable`. `lastVerified` is 2026-06-01.
- Stark County (Unincorporated): `termEnd` 2026-08-31 has passed, but the status is still `stable`.
- Seven Mile: the hook says the accounts have been on Duke default "for 9 months". It is now about 13 months. Relative-time wording goes stale.
- Westerville (columbus_aep): no `lastVerified`.
- 83 zones carry a `currentRate` with no `sourceUrl`. The full list comes from re-running the audit.

## D. Electric co-op file — needs source verification (ohioec.org was blocked from this session)
- "Ohio Valley Electric Cooperative" (HQ "Jackson, OH area"): I could not confirm that it exists as a Buckeye Power member. Its stated counties overlap Buckeye Rural Electric. This looks like a possible fabricated entity.
- "Ohio Electric Co-ops — 2 Unconfirmed" is a placeholder record, not a real zone.
- Possibly missing real members: Hancock-Wood Electric and North Western Electric (Bryan). A search result confirms North Western is on the ohioec.org roster. Midwest Electric (St. Marys) also appears in search results.
- The Frontier Power Company is listed as Wood/Sandusky/Hancock with HQ near Weston. My understanding is that it is Coshocton-based, which points to a mix-up with Hancock-Wood.
- HQ cities to check: Firelands (file says Norwalk; I believe New London), LMRE (file says Oberlin area; I believe Wellington), Tricounty REC (file says Defiance; I believe Malinta). Mid-Ohio Energy has no HQ listed (I believe Kenton).
- The count of member co-ops (24 vs 25) is inconsistent across sources and in CLAUDE.md.
