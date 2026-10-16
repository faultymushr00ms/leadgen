# FORGE merged reconciliation, 2026-10-15

Inputs: supplier_sweep.csv (295 rows), gov_records_sweep.csv (579), news_council_sweep.csv (34) and misinfo_sweep_2026-10-15.csv (93). The baseline is forge_corrected_dataset.csv (327 rows). team/summary.md was ignored. No repo was edited. Scripts are in team/merge_work/.

Rule used: confidence counts **independent source domains** that agree on a value. Three or more agreeing domains = `confirmed`, two = `likely`, one = `single-source`. Pages from the same publisher (for example several Dynegy pages) count as one source. When sources disagreed, every claim was kept: the losing claims are listed in the `notes` column of merged_changes.csv.

## Counts
- merged_changes.csv: **3470 rows** covering 821 community records (327 baseline rows plus communities that appear only in the sweeps).
- By classification: add 1883, keep 1327, call 92, update 91, delete 77
- By confidence: single-source 1936, unverified (baseline only) 675, likely 551, confirmed 191, conflict 78, other (misinfo-specific wording) 39
- Lifecycle per community: active 618, certified but not launched 76, not eligible 67, no program 22, ended 9, other/blank 9, unknown 8, rate pending 4, seeking supplier 2
- Hot leads: 1 ended program 9, 2 seeking supplier / rate pending 13, 3 contract expires <=6 mo 92, 4 new community not in app 24 (the full ranked list is in merged_hot_leads.csv).
- Many `add` rows have only one source. Most of these are PUCO-map or supplier-page-only communities, and they need a second check before they go in the app.

## Price to Compare used (residential, from energychoice.ohio.gov Apples to Apples, fetched 2026-10-15)
AEP Ohio 10.19¢ (Oct–Dec 2026), Ohio Edison 11.07¢ (Oct–Dec 2026), CEI 11.24¢ (Oct–Dec 2026), Toledo Edison 11.26¢ (Oct–Dec 2026), Duke 10.49¢ (Oct 2026 only), AES Ohio 10.86¢ (Jun 2026–May 2027). In the tables below, "agg−PTC" is negative when the aggregation rate is below the utility default.

## Contradictions resolved (sources re-fetched 2026-10-15)
| Community | Conflict | Resolution | Confidence |
|---|---|---|---|
| **Westlake** (Cuyahoga) | News says it ended. The gov sweep says "active" based on a Dynegy opt-out and a certificate. | **Ended in June 2026.** The PUCO opt-out (02/07/2025) and certificate 03-099E (01/15/2025) cover the 14-month Dynegy 8.38¢ term that ran "until June 2026" (city page). cleveland.com and West Life report the city rejected a 10.11¢ long-term offer. DIS also shows a 07/20/2026 Dynegy "Notice of Material change of CRES provider", which fits the exit (the filing text was not opened). The certificate is still open, so a restart is possible. The utility is **CEI**, not Ohio Edison. | confirmed |
| **Wyoming** (Hamilton) | Gov sweep: active. Baseline: ended. | **Ended in July 2026.** Energy Alliances: "Electric Aggregation Program – Ended July 2026 … unable to secure pricing that would guarantee savings". The gov sweep's "active" rests on a 05/2025 opt-out and a 02/2026 certificate. The new natural-gas aggregation (AEP Energy) is a separate program. | likely (one live source; call the city) |
| **Loveland** (Hamilton) | News: ended May 2026. Baseline: Direct Energy 10.36¢. | **Both are true, in sequence.** The Dynegy program ended with May 2026 meter reads (CivicAlert, 04/06/2026). The city then launched a **Direct Energy 10.36¢** program from Aug 2026 to Nov 2027 meter reads (city page; opt-out letters from 07/10/2026). Status: **active**. | likely (both city sources are lovelandoh.gov) |
| **Plain Twp** (Stark) | Baseline: ended. The other sweeps say NOPEC. | **Active through NOPEC since 2026.** The Dynegy program ended in May 2026. The township page says "supplied through our membership with … NOPEC". The NOPEC map shows "Member Since: 2026", and NOPEC has posted an enrollment-letter news item. The township page lists **both AEP Ohio and Ohio Edison**, so the territory is mixed. The rate for AEP-area accounts is unverified; NOPEC's OE Standard is 10.399¢. | confirmed (status) |
| **Fremont** (Sandusky) | Baseline: Ohio Edison 9.96¢. News: AEP 10.67¢. | **Two Dynegy tiers, one per utility.** Toledo Edison accounts pay **9.96¢** (Aug 2026–Dec 2027). AEP/Ohio Power accounts pay **10.67¢** (Jul 2026–Dec 2027), per the Dynegy "Fremont-OP" page and the city opt-out letter. The utility is AEP and TE, **not Ohio Edison**. | likely (rates); confirmed (supplier/term) |
| **Worthington** (Franklin) | Baseline supplier: AEP Energy. | **Direct Energy Services, 10.69¢, Jun 2026–Jun 2028** (worthington.org: "renewed … with Direct Energy Services"; Energy Alliances agrees). Supplier updated; rate and term kept. | likely |
| **MVCC towns** (19 communities) | Who supplies after Dec 2026? | Through Dec 2026: **Constellation 9.049¢**, confirmed by constellation.com, Centerville, Clayton and Trotwood. **From Dec 2026: Dynegy 11.53¢ default (11.73¢ renewable), Dec 2026–Dec 2029.** This is on Dynegy's MVCC pages for Kettering, Lewisburg and Xenia. That rate is **above the AES PTC of 10.86¢** (+0.67¢). No MVCC or city notice has been seen yet, so the other 16 members are inferred from the program level. | likely |
| **Morrow** city vs **Morrow County** | Case 23-0969-EL-GAG was matched to the Village of Morrow (Warren Co.). | **Wrong match.** That case belongs to the Morrow County Commissioners. Morrow County's program is **Dynegy 8.87¢, Jul 2025–Dec 2026**, and only Canaan, Gilead, Perry and Washington townships are eligible ("All cities and villages are ineligible"). Sources: Dynegy county page, Dynegy Washington Twp T&C, canaantwp.org. The Village of Morrow (Warren Co., Duke) has no program; that row is kept. Cardington Twp (Morrow Co.) has its own Dynegy program at 8.85¢ to Dec 2026. | confirmed (county); likely (village) |
| **Heath** (Licking) | Is Heath in the Licking County program? | **Not resolved; call.** The live Dynegy page says "The City of Newark is eligible … All other cities, villages, and townships are ineligible" (10.29¢, Dec 2025–Dec 2026). An older county page lists "Group 1 – Newark, Heath, Johnstown". The app's AEP Energy 10.01¢ is wrong. Newark is active and **expires Dec 2026**. | conflict |
| Tuscarawas Twp (Stark) | Gov sweep: active Dynegy 9.56¢. News: ended. | The gov-sweep row was a **name collision** with Franklin Twp (Tuscarawas County). The township page says the trustees "decided to end the electric aggregation program at the end of May" 2026. | single-source |
| Crosby Twp (Hamilton) | Did the 9.99¢-capped deal get signed? | Dynegy's site shows **9.88¢, Jun 2026–Dec 2027**, so the bid came in under the cap. Status: active. | likely |
| Plain City / Powell | NOPEC map member vs "no program yet" | Both set to **rate pending**. Plain City voters approved aggregation in Nov 2025. Powell picked NOPEC in Jun 2026, but the "plan of operation" is not final. NOPEC membership does not prove a program is active, and Powell's baseline 9.99¢ has no source. | likely / call |

Other cross-file conflicts that are still open are marked `call` in merged_changes.csv. Most are about 30 townships that the NOPEC map lists while Dynegy also has a township page, plus a few utility mismatches.

## Hot leads for sales (ranked)
Ranking: (1) ended programs, (2) seeking a supplier, rate pending, or certified but not launched, (3) contracts expiring by Apr 2027, sorted by end date, (4) new communities not in the app. "agg rate" is the current or last aggregation rate in ¢/kWh.

### 1 ended program (9)
| # | Community | County | Utility | Supplier | Agg rate | Term end | PTC | agg−PTC | Conf. | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Silverton | Hamilton | Duke Energy Ohio | Dynegy (expired) | 9.15 | 2026-05 | Duke Energy Ohio 10.49 | -1.34 | unverified (baseline only) | residents back on utility default; last aggregation rate shown |
| 2 | Tuscarawas Twp | Stark | Ohio Edison | None (program ended May 2026) | none | 2026-05 | Ohio Edison 11.07 |  | single-source | residents back on utility default; last aggregation rate shown |
| 3 | Delaware (City) | Delaware | Ohio Edison / AEP Ohio | Dynegy (expired) | 9.28 | 2026-06 | AEP Ohio 10.19 / Ohio Edison 11.07 | -0.91 / -1.79 | likely | residents back on utility default; last aggregation rate shown |
| 4 | Williamsburg | Clermont | Duke Energy Ohio | Dynegy (expired) | 9.38 | 2026-07 | Duke Energy Ohio 10.49 | -1.11 | unverified (baseline only) | residents back on utility default; last aggregation rate shown |
| 5 | Wyoming | Hamilton | Duke Energy Ohio | None (Dynegy ended Jul 2026) | 9.97 | 2026-07 | Duke Energy Ohio 10.49 | -0.52 | likely | residents back on utility default; last aggregation rate shown |
| 6 | Hilliard | Franklin | AEP Ohio | Dynegy (expired) | 9.59 | 2026-09 | AEP Ohio 10.19 | -0.60 | single-source | residents back on utility default; last aggregation rate shown |
| 7 | Bexley | Franklin | AEP Ohio | None (Dynegy program paused) |  |  | AEP Ohio 10.19 |  | unverified (baseline only) | residents back on utility default; last aggregation rate shown |
| 8 | Westlake | Cuyahoga | CEI | None (Dynegy term ended Jun 2026) | none (last 8.38; rejected 10.11) |  | CEI 11.24 |  | confirmed | residents back on utility default; last aggregation rate shown |
| 9 | Zanesville | Muskingum | AEP Ohio |  | 10.19 |  | AEP Ohio 10.19 | +0.00 | unverified (baseline only) | residents back on utility default; last aggregation rate shown |

### 2 seeking supplier / rate pending (13)
| # | Community | County | Utility | Supplier | Agg rate | Term end | PTC | agg−PTC | Conf. | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| 10 | Plain City | Madison | AEP Ohio | NOPEC/NextEra | unconfirmed (NOPEC AEP Standard 10.499 if enrolled) | 2027-06 | AEP Ohio 10.19 |  | likely | rate pending (voters approved Nov 2025; NOPEC member on map; enrollment/launch not confirmed) |
| 11 | Powell | Delaware | AEP Ohio | NOPEC/NextEra | unconfirmed (baseline 9.99 unsourced) | 2029-06 | AEP Ohio 10.19 |  | likely | rate pending (NOPEC selected Jun 2026; plan of operation not finalized) |
| 12 | Ashley | Delaware | AEP Ohio |  |  |  | AEP Ohio 10.19 |  | single-source | seeking supplier |
| 13 | Augusta Twp | Carroll | ? |  |  |  | n/a (utility not established) |  | escalate-call | PUCO case 23-1153-EL-GAG recently certified; no supplier found |
| 14 | Centerburg | Knox | AEP Ohio |  |  |  | AEP Ohio 10.19 |  | single-source | rate pending |
| 15 | Darke County | Darke | ? |  |  |  | n/a (utility not established) |  | single-source | seeking supplier |
| 16 | Frazeysburg | Muskingum | ? |  |  |  | n/a (utility not established) |  | escalate-call | PUCO case 25-1198-EL-GAG recently certified; no supplier found |
| 17 | Lincoln Heights | Hamilton | ? |  |  |  | n/a (utility not established) |  | escalate-call | PUCO case 24-0224-EL-GAG recently certified; no supplier found |
| 18 | Reily Twp | Butler | ? |  |  |  | n/a (utility not established) |  | escalate-call | PUCO case 23-1089-EL-GAG recently certified; no supplier found |
| 19 | Rutland (Village) | Meigs | AEP Ohio |  |  |  | AEP Ohio 10.19 |  | single-source | rate pending |
| 20 | Twin Twp | Preble | ? |  |  |  | n/a (utility not established) |  | escalate-call | PUCO case 24-0036-EL-GAG recently certified; no supplier found |
| 21 | West Alexandria | Preble | ? |  |  |  | n/a (utility not established) |  | escalate-call | PUCO case 23-1155-EL-GAG recently certified; no supplier found |
| 22 | West Mansfield | Logan | ? |  |  |  | n/a (utility not established) |  | escalate-call | PUCO case 24-1047-EL-GAG recently certified; no supplier found |

### 3 contract expires <=6 mo (92)
| # | Community | County | Utility | Supplier | Agg rate | Term end | PTC | agg−PTC | Conf. | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| 23 | Cincinnati | Hamilton | Duke Energy Ohio | Dynegy | 10.44 | 2026-11 | Duke Energy Ohio 10.49 | -0.05 | unverified (baseline only) | term ends 2026-11 |
| 24 | Sharonville | Hamilton | Duke Energy Ohio | Dynegy (current) -> WGL Energy (from Nov 2026) | 9.39 | 2026-11 | Duke Energy Ohio 10.49 | -1.10 | unverified (baseline only) | term ends 2026-11 |
| 25 | Ada | Hardin | Ada Municipal Electric | Dynegy | 9.45 | 2026-12 | n/a (utility not established) |  | unverified (baseline only) | term ends 2026-12 |
| 26 | Allen County | Allen | AEP Ohio | Dynegy | 9.78 | 2026-12 | AEP Ohio 10.19 | -0.41 | likely | term ends 2026-12 |
| 27 | Auglaize County | Auglaize | AES Ohio / AEP Ohio | Dynegy | 9.09 | 2026-12 | AEP Ohio 10.19 / AES Ohio 10.86 | -1.10 / -1.77 | likely | term ends 2026-12 |
| 28 | Beaver Township Twp | Mahoning | Ohio Edison | Dynegy | 10.399 | 2026-12 | Ohio Edison 11.07 | -0.67 | single-source | term ends 2026-12 |
| 29 | Beavercreek | Greene | AES Ohio | Constellation | 8.699 | 2026-12 | AES Ohio 10.86 | -2.16 | single-source | term ends 2026-12 |
| 30 | Brookville | Montgomery | AES Ohio | Constellation | 9.049 | 2026-12 | AES Ohio 10.86 | -1.81 | confirmed | term ends 2026-12; next: Dynegy 11.53 (Dec 2026-Dec 2029; 11.73 renewable) |
| 31 | Cardington | Morrow | ? | Dynegy | 8.85 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 32 | Cardington Twp | Morrow | ? | Dynegy | 8.85 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 33 | Centerville | Montgomery | AES Ohio | Constellation | 9.049 | 2026-12 | AES Ohio 10.86 | -1.81 | confirmed | term ends 2026-12; next: Dynegy 11.53 (Dec 2026-Dec 2029; 11.73 renewable) |
| 34 | Chester Township Twp | Geauga | CEI | Dynegy | 10.399 | 2026-12 | CEI 11.24 | -0.84 | single-source | term ends 2026-12 |
| 35 | Clark County | Clark | Ohio Edison | Dynegy | 8.89 | 2026-12 | Ohio Edison 11.07 | -2.18 | likely | term ends 2026-12 |
| 36 | Clay Twp | Montgomery | ? | Dynegy | 9.09 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 37 | Clayton | Montgomery | AES Ohio | Constellation | 9.049 | 2026-12 | AES Ohio 10.86 | -1.81 | confirmed | term ends 2026-12; next: Dynegy 11.53 (Dec 2026-Dec 2029; 11.73 renewable) |
| 38 | Clinton County | Clinton | AES Ohio / Duke Energy Ohio | Dynegy | 8.98 | 2026-12 | Duke Energy Ohio 10.49 / AES Ohio 10.86 | -1.51 / -1.88 | likely | term ends 2026-12 |
| 39 | Eaton | Preble | AES Ohio / Duke Energy Ohio | Constellation | 9.049 | 2026-12 | Duke Energy Ohio 10.49 / AES Ohio 10.86 | -1.44 / -1.81 | confirmed | term ends 2026-12; next: Dynegy 11.53 (Dec 2026-Dec 2029; 11.73 renewable) |
| 40 | Englewood | Montgomery | AES Ohio | Constellation | 9.049 | 2026-12 | AES Ohio 10.86 | -1.81 | confirmed | term ends 2026-12; next: Dynegy 11.53 (Dec 2026-Dec 2029; 11.73 renewable) |
| 41 | Erie County | Erie | Ohio Edison | Dynegy | 8.88 | 2026-12 | Ohio Edison 11.07 | -2.19 | confirmed | term ends 2026-12 |
| 42 | Fairborn | Greene | Ohio Edison / AES Ohio | Constellation | 9.049 | 2026-12 | Ohio Edison 11.07 / AES Ohio 10.86 | -2.02 / -1.81 | confirmed | term ends 2026-12; next: Dynegy 11.53 (Dec 2026-Dec 2029; 11.73 renewable) |
| 43 | Fairfield County | Fairfield | AEP Ohio | Constellation | 9.468 | 2026-12 | AEP Ohio 10.19 | -0.72 | likely | term ends 2026-12 |
| 44 | Fayette | Fulton | ? | Dynegy | 9.78 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 45 | Fredericktown | Knox | ? | Dynegy | 9.63 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 46 | Germantown | Montgomery | AES Ohio | Constellation | 9.049 | 2026-12 | AES Ohio 10.86 | -1.81 | confirmed | term ends 2026-12; next: Dynegy 11.53 (Dec 2026-Dec 2029; 11.73 renewable) |
| 47 | Golf Manor | Hamilton | Duke Energy Ohio | Dynegy | 9.79 | 2026-12 | Duke Energy Ohio 10.49 | -0.70 | unverified (baseline only) | term ends 2026-12 |
| 48 | Greene County | Greene | Toledo Edison / AES Ohio | Dynegy | 9.36 | 2026-12 | Toledo Edison 11.26 / AES Ohio 10.86 | -1.90 / -1.50 | confirmed | term ends 2026-12 |
| 49 | Hanover Township Twp | Butler | Duke Energy Ohio | Direct Energy | 10.29 | 2026-12 | Duke Energy Ohio 10.49 | -0.20 | likely | term ends 2026-12 |
| 50 | Hanover Township Twp | Columbiana | Ohio Edison | Dynegy | 10.29 | 2026-12 | Ohio Edison 11.07 | -0.78 | single-source | term ends 2026-12 |
| 51 | Heath / Newark | Licking | AEP Ohio | Dynegy (Newark only) | 10.29 | 2026-12 | AEP Ohio 10.19 | +0.10 | conflict | term ends 2026-12 |
| 52 | Henry County | Henry | Toledo Edison | Dynegy | 8.96 | 2026-12 | Toledo Edison 11.26 | -2.30 | likely | term ends 2026-12 |
| 53 | Kettering | Montgomery | AES Ohio | Constellation | 9.049 | 2026-12 | AES Ohio 10.86 | -1.81 | confirmed | term ends 2026-12; next: Dynegy 11.53 (Dec 2026-Dec 2029; 11.73 renewable) |
| 54 | Lakeview / Indian Lake Area | Logan | AEP Ohio | Dynegy | 9.26 | 2026-12 | AEP Ohio 10.19 | -0.93 | unverified (baseline only) | term ends 2026-12 |
| 55 | Lemon Township | Butler | Duke Energy Ohio | Constellation | 8.846 | 2026-12 | Duke Energy Ohio 10.49 | -1.64 | single-source | term ends 2026-12 |
| 56 | Lewisburg | Preble | AES Ohio | Constellation | 9.049 | 2026-12 | AES Ohio 10.86 | -1.81 | confirmed | term ends 2026-12; next: Dynegy 11.53 (Dec 2026-Dec 2029; 11.73 renewable) |
| 57 | Liberty Twp | Hancock | ? | Dynegy | 9.26 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 58 | Licking County / Pataskala | Licking | AEP Ohio | Dynegy | 10.29 | 2026-12 | AEP Ohio 10.19 | +0.10 | unverified (baseline only) | term ends 2026-12 |
| 59 | Logan County | Logan | AES Ohio | Dynegy | 9.26 | 2026-12 | AES Ohio 10.86 | -1.60 | likely | term ends 2026-12 |
| 60 | Louisville | Stark | AEP Ohio | Dynegy | 10.29 | 2026-12 | AEP Ohio 10.19 | +0.10 | likely | term ends 2026-12 |
| 61 | Madison County | Madison | Ohio Edison / AES Ohio / AEP Ohio | Dynegy | 9.47 | 2026-12 | AEP Ohio 10.19 / Ohio Edison 11.07 / AES Ohio 10.86 | -0.72 / -1.60 / -1.39 | confirmed | term ends 2026-12 |
| 62 | Madison Township | Lake | CEI | Dynegy | 10.399 | 2026-12 | CEI 11.24 | -0.84 | single-source | term ends 2026-12 |
| 63 | Madison Twp | Clark | ? | Dynegy | 9.47 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 64 | Madison Twp | Columbiana | ? | Dynegy | 9.47 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 65 | Madison Twp | Franklin | ? | Dynegy | 9.47 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 66 | Marlboro Twp | Stark | ? | Dynegy | 8.99 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 67 | Mercer County | Mercer | AES Ohio | Dynegy | 9.45 | 2026-12 | AES Ohio 10.86 | -1.41 | likely | term ends 2026-12 |
| 68 | Miami County | Miami | AES Ohio | Dynegy | 9.59 | 2026-12 | AES Ohio 10.86 | -1.27 | likely | term ends 2026-12 |
| 69 | Miamisburg | Montgomery | AES Ohio | Constellation | 9.049 | 2026-12 | AES Ohio 10.86 | -1.81 | confirmed | term ends 2026-12; next: Dynegy 11.53 (Dec 2026-Dec 2029; 11.73 renewable) |
| 70 | Middletown | Butler | AES Ohio | Dynegy | 9.29 | 2026-12 | AES Ohio 10.86 | -1.57 | unverified (baseline only) | term ends 2026-12 |
| 71 | Milford | Clermont | Duke Energy Ohio | Constellation | 8.499 | 2026-12 | Duke Energy Ohio 10.49 | -1.99 | single-source | term ends 2026-12 |
| 72 | Monroe | Butler | AES Ohio / Duke Energy Ohio | Constellation | 9.049 | 2026-12 | Duke Energy Ohio 10.49 / AES Ohio 10.86 | -1.44 / -1.81 | confirmed | term ends 2026-12; next: Dynegy 11.53 (Dec 2026-Dec 2029; 11.73 renewable) |
| 73 | Monroe Township Twp | Ashtabula | Ohio Edison | Dynegy | 10.399 | 2026-12 | Ohio Edison 11.07 | -0.67 | single-source | term ends 2026-12 |
| 74 | Monroe Twp | Clermont | ? | Dynegy | 9.59 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 75 | Moraine | Montgomery | AES Ohio | Constellation | 9.049 | 2026-12 | AES Ohio 10.86 | -1.81 | confirmed | term ends 2026-12; next: Dynegy 11.53 (Dec 2026-Dec 2029; 11.73 renewable) |
| 76 | Morrow County | Morrow | AEP Ohio / Ohio Edison (mixed) | Dynegy | 8.87 | 2026-12 | AEP Ohio 10.19 / Ohio Edison 11.07 | -1.32 / -2.20 | confirmed | term ends 2026-12 |
| 77 | Mount Vernon | Knox | ? | Dynegy | 9.63 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 78 | Muskingum County | Muskingum | AEP Ohio | Constellation | 9.266 | 2026-12 | AEP Ohio 10.19 | -0.92 | likely | term ends 2026-12 |
| 79 | New Lebanon | Montgomery | AES Ohio | Constellation | 9.049 | 2026-12 | AES Ohio 10.86 | -1.81 | confirmed | term ends 2026-12; next: Dynegy 11.53 (Dec 2026-Dec 2029; 11.73 renewable) |
| 80 | Oakwood | Montgomery | AES Ohio | Constellation | 9.049 | 2026-12 | AES Ohio 10.86 | -1.81 | likely | term ends 2026-12 |
| 81 | Osnaburg Twp | Stark | ? | Dynegy | 7.95 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 82 | Oxford Township (Butler Co) | Butler | Duke Energy Ohio | Constellation | 8.731 | 2026-12 | Duke Energy Ohio 10.49 | -1.76 | unverified (baseline only) | term ends 2026-12 |
| 83 | Pleasant Twp | Franklin | ? | Dynegy | 9.47 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 84 | Pleasant Twp | Marion | ? | Dynegy | 9.47 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 85 | Preble County | Preble | AES Ohio | Dynegy | 9.39 | 2026-12 | AES Ohio 10.86 | -1.47 | likely | term ends 2026-12 |
| 86 | Putnam County | Putnam | AEP Ohio | Direct Energy | 9.2 | 2026-12 | AEP Ohio 10.19 | -0.99 | likely | term ends 2026-12 |
| 87 | Richland County | Richland | Ohio Edison / AEP Ohio | Dynegy | 8.89 | 2026-12 | AEP Ohio 10.19 / Ohio Edison 11.07 | -1.30 / -2.18 | likely | term ends 2026-12 |
| 88 | Rushcreek Twp | Logan | ? | Dynegy | 8.99 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 89 | Rushsylvania | Logan | ? | Dynegy | 8.99 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 90 | Russell Township Twp | Geauga | CEI | Dynegy | 10.399 | 2026-12 | CEI 11.24 | -0.84 | single-source | term ends 2026-12 |
| 91 | Sandusky County | Sandusky | Toledo Edison / Ohio Edison / AEP Ohio | Dynegy | 8.76 | 2026-12 | AEP Ohio 10.19 / Toledo Edison 11.26 / Ohio Edison 11.07 | -1.43 / -2.50 / -2.31 | likely | term ends 2026-12 |
| 92 | Seneca County | Seneca | AEP Ohio | Dynegy | 9.31 | 2026-12 | AEP Ohio 10.19 | -0.88 | likely | term ends 2026-12 |
| 93 | Seven Mile | Butler | Duke Energy Ohio | Constellation | 9.096 | 2026-12 | Duke Energy Ohio 10.49 | -1.39 | single-source | term ends 2026-12 |
| 94 | South Lebanon | Warren | Duke Energy Ohio | Dynegy | 9.09 | 2026-12 | Duke Energy Ohio 10.49 | -1.40 | unverified (baseline only) | term ends 2026-12 |
| 95 | Trotwood | Montgomery | AES Ohio | Constellation | 9.049 | 2026-12 | AES Ohio 10.86 | -1.81 | confirmed | term ends 2026-12; next: Dynegy 11.53 (Dec 2026-Dec 2029; 11.73 renewable) |
| 96 | Troy | Miami | AES Ohio | Constellation | 9.049 | 2026-12 | AES Ohio 10.86 | -1.81 | confirmed | term ends 2026-12; next: Dynegy 11.53 (Dec 2026-Dec 2029; 11.73 renewable) |
| 97 | Tuscarawas County | Tuscarawas | AEP Ohio | Dynegy | 9.71 | 2026-12 | AEP Ohio 10.19 | -0.48 | likely | term ends 2026-12 |
| 98 | Union | Montgomery | AES Ohio | Constellation | 9.049 | 2026-12 | AES Ohio 10.86 | -1.81 | confirmed | term ends 2026-12; next: Dynegy 11.53 (Dec 2026-Dec 2029; 11.73 renewable) |
| 99 | Union Twp | Licking | ? | Dynegy | 9.59 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 100 | Van Wert County | Van Wert | AES Ohio / AEP Ohio | Dynegy | 9.34 | 2026-12 | AEP Ohio 10.19 / AES Ohio 10.86 | -0.85 / -1.52 | likely | term ends 2026-12 |
| 101 | Vandalia | Montgomery | AES Ohio | Constellation | 9.049 | 2026-12 | AES Ohio 10.86 | -1.81 | confirmed | term ends 2026-12; next: Dynegy 11.53 (Dec 2026-Dec 2029; 11.73 renewable) |
| 102 | Waldo | Marion | ? | Dynegy | 9.06 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 103 | Warsaw | Coshocton | ? | Dynegy | 9.36 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 104 | Washington County | Washington | AEP Ohio | Constellation | 9.84 | 2026-12 | AEP Ohio 10.19 | -0.35 | likely | term ends 2026-12 |
| 105 | Wayne County | Wayne | AEP Ohio | Dynegy | 9.56 | 2026-12 | AEP Ohio 10.19 | -0.63 | likely | term ends 2026-12 |
| 106 | West Carrollton | Montgomery | AES Ohio | Constellation | 9.049 | 2026-12 | AES Ohio 10.86 | -1.81 | confirmed | term ends 2026-12; next: Dynegy 11.53 (Dec 2026-Dec 2029; 11.73 renewable) |
| 107 | West Chester Township | Butler | Duke Energy Ohio | Dynegy | 9.299 | 2026-12 | Duke Energy Ohio 10.49 | -1.19 | unverified (baseline only) | term ends 2026-12 |
| 108 | West Twp | Columbiana | ? | Dynegy | 9.26 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 109 | Weston | Wood | ? | Dynegy | 9.35 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 110 | Williams County | Williams | Toledo Edison | Dynegy | 8.78 | 2026-12 | Toledo Edison 11.26 | -2.48 | likely | term ends 2026-12 |
| 111 | Winchester | Adams | ? | Dynegy | 9.19 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 112 | Wood County | Wood | Toledo Edison | Dynegy | 8.78 | 2026-12 | Toledo Edison 11.26 | -2.48 | likely | term ends 2026-12 |
| 113 | York Twp | Sandusky | ? | Dynegy | 9.34 | 2026-12 | n/a (utility not established) |  | single-source | term ends 2026-12 |
| 114 | Aurora | Portage | Ohio Edison | Dynegy | 9.59 | 2027-04 | Ohio Edison 11.07 | -1.48 | unverified (baseline only) | term ends 2027-04 |

### 4 new community not in app (24)
| # | Community | County | Utility | Supplier | Agg rate | Term end | PTC | agg−PTC | Conf. | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| 115 | Hardin County | Hardin | AEP Ohio | Dynegy | 8.99 | 2027-05 | AEP Ohio 10.19 | -1.20 | likely | rate confidence likely |
| 116 | Hocking County | Hocking | AEP Ohio | Dynegy | 9.97 | 2027-05 | AEP Ohio 10.19 | -0.22 | likely | rate confidence likely |
| 117 | Ottawa County | Ottawa | Toledo Edison / Ohio Edison | Dynegy | 8.89 | 2027-05 | Toledo Edison 11.26 / Ohio Edison 11.07 | -2.37 / -2.18 | likely | rate confidence likely |
| 118 | Upper Arlington | Franklin | AEP Ohio | AEP Energy | 11.162 | 2027-05 | AEP Ohio 10.19 | +0.97 | likely | rate confidence likely |
| 119 | Albany | Athens | AEP Ohio | AEP Energy | 11.262 | 2027-06 | AEP Ohio 10.19 | +1.07 | likely | rate confidence likely |
| 120 | Amesville | Athens | AEP Ohio | AEP Energy | 11.262 | 2027-06 | AEP Ohio 10.19 | +1.07 | likely | rate confidence likely |
| 121 | Athens County (Unincorporated) | Athens | AEP Ohio | AEP Energy | 11.262 | 2027-06 | AEP Ohio 10.19 | +1.07 | likely | rate confidence likely |
| 122 | Belpre | Washington | AEP Ohio | AEP Energy | 11.262 | 2027-06 | AEP Ohio 10.19 | +1.07 | likely | rate confidence likely |
| 123 | Buchtel | Athens | AEP Ohio | AEP Energy | 11.262 | 2027-06 | AEP Ohio 10.19 | +1.07 | likely | rate confidence likely |
| 124 | Chauncey | Athens | AEP Ohio | AEP Energy | 11.262 | 2027-06 | AEP Ohio 10.19 | +1.07 | likely | rate confidence likely |
| 125 | Chesterhill | Morgan | AEP Ohio | AEP Energy | 11.262 | 2027-06 | AEP Ohio 10.19 | +1.07 | likely | rate confidence likely |
| 126 | Glenford | Perry | AEP Ohio | AEP Energy | 11.262 | 2027-06 | AEP Ohio 10.19 | +1.07 | likely | rate confidence likely |
| 127 | Jacksonville | Athens | AEP Ohio | AEP Energy | 11.262 | 2027-06 | AEP Ohio 10.19 | +1.07 | likely | rate confidence likely |
| 128 | Lowell | Washington | AEP Ohio | AEP Energy | 11.262 | 2027-06 | AEP Ohio 10.19 | +1.07 | likely | rate confidence likely |
| 129 | New Straitsville | Perry | AEP Ohio | AEP Energy | 11.262 | 2027-06 | AEP Ohio 10.19 | +1.07 | likely | rate confidence likely |
| 130 | Racine | Meigs | AEP Ohio | AEP Energy | 11.262 | 2027-06 | AEP Ohio 10.19 | +1.07 | likely | rate confidence likely |
| 131 | Rio Grande | Gallia | AEP Ohio | AEP Energy | 11.262 | 2027-06 | AEP Ohio 10.19 | +1.07 | likely | rate confidence likely |
| 132 | Shawnee | Perry | AEP Ohio | AEP Energy | 11.262 | 2027-06 | AEP Ohio 10.19 | +1.07 | likely | rate confidence likely |
| 133 | Somerset | Perry | AEP Ohio | AEP Energy | 11.262 | 2027-06 | AEP Ohio 10.19 | +1.07 | likely | rate confidence likely |
| 134 | Trimble | Athens | AEP Ohio | AEP Energy | 11.262 | 2027-06 | AEP Ohio 10.19 | +1.07 | likely | rate confidence likely |
| 135 | Liberty Township Twp | Butler | Duke Energy Ohio | Constellation | 10.099 | 2027-07 | Duke Energy Ohio 10.49 | -0.39 | likely | rate confidence likely |
| 136 | Fulton County | Fulton | Toledo Edison | Dynegy | 9.03 | 2027-12 | Toledo Edison 11.26 | -2.23 | likely | rate confidence likely |
| 137 | Huron County | Huron | Ohio Edison | Dynegy | 8.92 | 2027-12 | Ohio Edison 11.07 | -2.15 | likely | rate confidence likely |
| 138 | Fayette County | Fayette | AES Ohio | Dynegy | 10.29 | 2028-06 | AES Ohio 10.86 | -0.57 | likely | rate confidence likely |

## Call list
Generic G-sweep entries such as "Community clerk" mean no specific number was found, so none is given. Supplier lines: Dynegy aggregation 888-682-2170 / 1-833-241-4599; NOPEC 855-667-3201; Constellation (MVCC) 833-866-3986; Direct Energy 866-968-8065; Energy Alliances 513-794-5555; Palmer Energy 419-491-1040.

| Community | County | Fields in question | What to ask | Phone(s) |
|---|---|---|---|---|
| Amherst | Lorain | supplier | Resolve: supplier: City utility / AMP vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map / | number not in sources: community clerk / fiscal officer |
| Andover | Ashtabula | supplier | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map / | number not in sources: community clerk / fiscal officer |
| Beaver Township Twp | Mahoning | rate, supplier, term_end | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.399 vs 9.78 [gov_records_sweep; PUCO ArcGIS] | number not in sources: community clerk / fiscal officer |
| Canfield | Mahoning | supplier | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map / | number not in sources: community clerk / fiscal officer |
| Carlisle Township Twp | Lorain | rate, supplier | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.399 vs 9.88 [gov_records_sweep; PUCO ArcGIS] | number not in sources: community clerk / fiscal officer |
| Chester Township Twp | Geauga | rate, supplier, term_end | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.399 vs 9.299 [gov_records_sweep; PUCO ArcGIS] | number not in sources: community clerk / fiscal officer |
| Chillicothe | Ross | orig_currentRate / CURRENT | Resolve: misinfo: orig_currentRate / CURRENT: SOPEC member (AEP Energy) - current SOPEC rate not vs from misinfo_sweep_2026-10-15.csv | number not in sources: community clerk / fiscal officer |
| Cleveland | Cuyahoga | term_end | Resolve: term_end: 2027-08 vs 2026-08 [news_council_sweep; https://citizenportal.ai/articles/10593443/ohio/cuy | number not in sources: community clerk / fiscal officer |
| Columbia Township Twp | Lorain | rate, supplier | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.399 vs 9.47 [gov_records_sweep; PUCO ArcGIS] | number not in sources: community clerk / fiscal officer |
| Columbus | Franklin | term_end | Resolve: term_end: 2027-05 vs 2027-06 [news_council_sweep; https://www.energychoicematters.com/stories/2026041 | number not in sources: community clerk / fiscal officer |
| Concord Township Twp | Lake | rate, supplier | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.399 vs 9.47 [gov_records_sweep; PUCO ArcGIS] | number not in sources: community clerk / fiscal officer |
| Eaton Township Twp | Lorain | rate, supplier, term_end | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.399 vs 11.53 [gov_records_sweep; PUCO ArcGIS] | number not in sources: community clerk / fiscal officer |
| Fairfield Township Twp | Columbiana | rate, supplier, term_end | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.07 vs 10.399 [supplier_sweep; https://www.nopec.org/communities/community-map / https: | number not in sources: community clerk / fiscal officer |
| Franklin Township Twp | Portage | rate, supplier | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.399 vs 9.56 [gov_records_sweep; PUCO ArcGIS] | number not in sources: community clerk / fiscal officer |
| Fremont | Sandusky | norm_utility | Resolve: misinfo: norm_utility: NOT Ohio Edison: Dynegy T&C says TE, PUCO/HIFLD sa vs from misinfo_sweep_2026-10-15.csv | Dynegy 888-682-2170 |
| Grafton | Lorain | supplier | Resolve: supplier: NOPEC/NextEra vs Village utility / AMP [gov_records_sweep; PUCO ArcGIS] | number not in sources: community clerk / fiscal officer |
| Green Township Twp | Mahoning | rate, supplier | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.399 vs 9.47 [gov_records_sweep; PUCO ArcGIS] | number not in sources: community clerk / fiscal officer |
| Hanover Township Twp | Butler | rate, supplier, term_end | Resolve: supplier: Direct Energy vs Dynegy [gov_records_sweep; https://dis.puc.state.oh.us/CaseRecord.aspx?CaseNo=16; rate: 10.29 vs 9.76 [supplier_sweep; https://energyalliances.com/hanover] | number not in sources: community clerk / fiscal officer |
| Hanover Township Twp | Columbiana | rate, supplier, term_end | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.29 vs 10.399 [supplier_sweep; https://www.nopec.org/communities/community-map / https: | number not in sources: community clerk / fiscal officer |
| Heath / Newark | Licking | lifecycle, zone scope / orig supplier | Is Heath in the Licking County Dynegy group? What is the successor after Dec 2026? | City of Heath 740-522-1420; Licking County Commissioners 740-670-5110; Dynegy 888-682-2170 |
| Jefferson Township Twp | Ashtabula | rate, supplier | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.399 vs 9.56 [gov_records_sweep; PUCO ArcGIS] | number not in sources: community clerk / fiscal officer |
| LaGrange Township Twp | Lorain | rate, supplier, term_end | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.399 vs 8.75 [gov_records_sweep; PUCO ArcGIS] | number not in sources: community clerk / fiscal officer |
| Louisville | Stark | rate, term_end | Resolve: rate: 10.29 vs 10.53 [news_council_sweep; https://www.louisvilleohio.gov/DocumentCenter/View/80; term_end: 2026-12 vs 2027-12 [news_council_sweep; https://www.louisvilleohio.gov/DocumentCenter/View/ | Community clerk; Dynegy 1-833-241-4599 |
| Madison Township | Lake | rate, supplier, term_end | Resolve: supplier: Dynegy vs NOPEC/NextEra [baseline,supplier_sweep; https://www.nopec.org/communities/commun; rate: 10.399 vs 9.47 [gov_records_sweep; PUCO ArcGIS] | number not in sources: community clerk / fiscal officer |
| Mahoning County | Mahoning | orig_currentRate / orig_hook | Resolve: misinfo: orig_currentRate / orig_hook: No county-wide program found; 10.59 unsourced (mat vs from misinfo_sweep_2026-10-15.csv | number not in sources: community clerk / fiscal officer |
| Mantua Township Twp | Portage | rate, supplier, term_end | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.399 vs 9.19 [gov_records_sweep; PUCO ArcGIS] | number not in sources: community clerk / fiscal officer |
| Marysville | Union | norm_utility | Resolve: misinfo: norm_utility: Mixed AES Ohio / Union REC - address check vs from misinfo_sweep_2026-10-15.csv | number not in sources: community clerk / fiscal officer |
| Milton Township Twp | Mahoning | rate, supplier, term_end | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.299 vs 10.399 [supplier_sweep; https://www.nopec.org/communities/community-map / https: | number not in sources: community clerk / fiscal officer |
| Monroe Township Twp | Ashtabula | rate, supplier, term_end | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.399 vs 9.59 [gov_records_sweep; PUCO ArcGIS] | number not in sources: community clerk / fiscal officer |
| North Canton | Stark | rate, term_end | Resolve: rate: 10.399 vs 9.999 [news_council_sweep; http://northcantonohio.gov/m/newsflash/Home/Detail/51; term_end: 2026-08 vs 2027-06 [baseline,supplier_sweep; https://www.nopec.org/communities/community-ma | number not in sources: community clerk / fiscal officer |
| Oxford | Butler | supplier | Resolve: supplier: AEP Energy vs Constellation [supplier_sweep; forge_corrected_dataset.csv] | number not in sources: community clerk / fiscal officer |
| Painesville | Lake | supplier, utility | Resolve: supplier: City utility vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; utility: CEI vs Ohio Edison [gov_records_sweep; PUCO ArcGIS] | number not in sources: community clerk / fiscal officer |
| Paris Township (Stark) Twp | Stark | rate, supplier, term_end | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.131 vs 10.399 [supplier_sweep; https://www.nopec.org/communities/community-map / https: | number not in sources: community clerk / fiscal officer |
| Paris Township Twp | Portage | rate, supplier, term_end | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.131 vs 10.399 [supplier_sweep; https://www.nopec.org/communities/community-map / https: | number not in sources: community clerk / fiscal officer |
| Pickerington | Fairfield | norm_utility | Resolve: misinfo: norm_utility: Mixed: South Central Power co-op (95% per HIFLD) / vs from misinfo_sweep_2026-10-15.csv | number not in sources: community clerk / fiscal officer |
| Plain City | Madison | lifecycle, rate | Has NOPEC enrollment started? What is the price? | NOPEC 855-667-3201; Plain City village office (number not in sources) |
| Plain Township | Stark | rate | What NOPEC price applies to AEP-territory accounts? | NOPEC 855-667-3201 (the township asks people not to call Township Hall about accounts) |
| Powell | Delaware | rate | Is the plan of operation adopted? What is the launch date and rate? | NOPEC 855-667-3201; City of Powell (number not in sources) |
| Ravenna | Portage | supplier | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map / | number not in sources: community clerk / fiscal officer |
| Richmond Township Twp | Ashtabula | rate, supplier | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.399 vs 9.84 [gov_records_sweep; PUCO ArcGIS] | number not in sources: community clerk / fiscal officer |
| Russell Township Twp | Geauga | rate, supplier, term_end | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.399 vs 9.26 [gov_records_sweep; PUCO ArcGIS] | number not in sources: community clerk / fiscal officer |
| Summit County | Summit | lifecycle, rate, supplier, term_end, utility | Resolve: supplier: Dynegy vs ; rate: 9.94 vs  | Summit County Clerk / Dynegy 1-833-241-4599 |
| Trumbull Township Twp | Ashtabula | rate, supplier, term_end | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.14 vs 10.399 [supplier_sweep; https://www.nopec.org/communities/community-map / https: | number not in sources: community clerk / fiscal officer |
| Wauseon | Fulton | CURRENT | Resolve: misinfo: CURRENT: Keep 11.09 as FUTURE only; current rate needs call vs from misinfo_sweep_2026-10-15.csv | number not in sources: community clerk / fiscal officer |
| Wayne Township Twp | Ashtabula | rate, supplier | Resolve: supplier: Dynegy vs NOPEC/NextEra [supplier_sweep; https://www.nopec.org/communities/community-map /; rate: 10.399 vs 9.47 [gov_records_sweep; PUCO ArcGIS] | number not in sources: community clerk / fiscal officer |
| MVCC (19 towns) | Montgomery/Greene/Preble/Miami/Butler | future supplier | Confirm Dynegy 11.53¢ from Dec 2026 for all 19 members | Constellation MVCC 833-866-3986; Dynegy 888-682-2170; Palmer Energy (Valerie) 419-491-1040 |
| Wyoming | Hamilton | lifecycle | Confirm the electric program ended in July 2026 and whether a restart is planned | City of Wyoming 513-821-7600; Energy Alliances 513-794-5555 / 800-735-0359 |
| Henry/Williams/Wood villages, Wauseon | — | current vs future rate | Which rate applies before the Dec 2026 11.09¢ term? | Dynegy 888-682-2170; Palmer Energy 419-491-1040 |
