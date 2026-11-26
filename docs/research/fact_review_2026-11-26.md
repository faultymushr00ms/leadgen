# FORGE data fact review — 2026-11-26

Scheduled review of `data/regions/*.json` (427 electric records) and `data/gas/*.json` for non-factual or self-contradicting data.
**No zone data was changed in this run.** Every item below needs a source opened before anything is deleted. This session could not reach ohioec.org, sopec-oh.gov or the city PDFs because they were blocked by the network policy, so the checks used web search snippets only.

## Likely incorrect (fix first)

| Zone (file) | Problem | Evidence |
|---|---|---|
| **Ohio Valley Electric Cooperative** (`ohio_electric_cooperatives.json`) | Probably a fabricated co-op. No Ohio co-op by this name was found. The name matches Ohio Valley Electric Corporation (OVEC), a utility-owned generator in Piketon. The counties listed (Jackson, Gallia, Vinton, Pike, Scioto, Ross) are Buckeye Rural Electric territory, based in Rio Grande. | Search: buckeyerec.coop "Who We Are"; OVEC Wikipedia |
| **Ohio Electric Co-ops — 2 Unconfirmed** (same file) | This is a placeholder, not a real record. The two co-ops missing from the file look like **Hancock-Wood Electric Cooperative** and **North Western Electric Cooperative** (Bryan). Both are on the Ohio co-op member listing. | Search: ohioec.org/ohios-cooperatives snippet |
| **Dayton** (`dayton_sw_ohio.json`) | The takeaway and hook say the aggregation "expired June 30, 2026" and that accounts are on AES default with no contract. An April 2026 Dayton/SOPEC opt-out letter names **AEP Energy** as the selected supplier for a renewal, with opt-out ending May 11, 2026, so the program likely continued. `supplier: "SOPEC"` names the aggregator, not the supplier. `rateChange: 22.7` is stored with `previousRate: null`. There is no `sourceUrl`. | Search: sopec-oh.gov/rates/dayton; Dayton opt-out PDF (April 20, 2026) |
| **Riverside** (`dayton_sw_ohio.json`) | Same "expired, now on AES default" claim with no source. It needs the same check as Dayton. | n/a |

## Internally inconsistent

- **Sharonville** (`cincinnati_duke.json`): `rateChange 42.9` doesn't fit the stored previous rate 9.39 or the WGL 10.276¢ named in the notes, which would be +9.4%. There is no `currentRate`. The 42.9 implies a prior near 7.19¢ that isn't stored anywhere.
- **Washington Township (Wood)** (`toledo_lucas_noac.json`): `rateChange 13.0` matches 9.75/8.63, the NOAC rate. The record is labeled Dynegy and quotes 11.09¢ from December 2026, which would be +28.5%. There is no `currentRate`.
- **Plain City** (`merged_confirmed.json`): the takeaway says accounts were enrolled in NOPEC and the supplier is NOPEC/NextEra, but `aggregationStatus` is `no_aggregation_verified`.
- **Stark County (Unincorporated / Remaining)** (`akron_summit_medina.json`): the record says "No county-wide program" but still carries `termStart 2025-08-01` and `termEnd 2026-08-31`, which are term dates for a program that doesn't exist.
- **Norwood** (`cincinnati_duke.json`): the term started 2026-06-01 but the status is still `pain_coming`. The 6.67→10.39¢ (+55.8%) figures have no source, and no Norwood source turned up in search.

## Stale (true once, now out of date)

- **Cincinnati** (`cincinnati_duke.json`): the 10.44¢ term ended 2026-11-01, but the status is still `stable` and the record was last verified in June. The city page confirms 10.44¢ for May–November 2026 only. The price after November is the missing fact. Keep 10.44¢ as genuine expired history.
- **Oxford** (`cincinnati_duke_suburbs.json`): the record still says "expiring this month, renewal underway" (as of June). The city has an April 2026 update page.
- **Akron** and **Green** (`akron_summit_medina.json`): the stored 9.24¢ term ended 2026-06-30. The record already notes this.

## Sourcing gaps (not wrong, but unsupported)

- 52 records have `confidence: "high"` and no `sourceUrl`. These include Columbus, Dayton, Cincinnati, Toledo, the SOPEC suburbs and most municipal utilities.
- 83 records store a `currentRate` without a `sourceUrl`. This is most of `cincinnati_duke_suburbs.json` (10.7¢ placeholders, which is the Duke default and not an aggregation rate), plus `eastern_ohio_aep.json` and `dayton_aes_suburbs.json`.
- 8 co-ops use `futureUse: address_check`. The CLAUDE.md rule for co-ops is `municipal_blacklist`.

## Checked and consistent

- **Cleveland**: SOPEC/AEP Energy at 10.457¢, August 2026 – July 2027, prior 9.236¢. This matches the city's SOPEC FAQ.

Sources: [SOPEC Dayton rates](https://www.sopec-oh.gov/rates/dayton) · [Buckeye REC — Who We Are](https://buckeyerec.coop/who-we-are) · [Ohio's co-ops list](https://ohioec.org/ohios-cooperatives) · [OVEC](https://www.wikipedia.org/wiki/Ohio_Valley_Electric_Corporation) · [Cincinnati aggregation](https://www.cincinnati-oh.gov/oes/buildings-and-energy/aggregation-program) · [Cleveland SOPEC](https://www.clevelandohio.gov/city-hall/office-mayor/sustainability/programs-resources/sopec) · [Oxford aggregation](https://www.cityofoxford.org/departments/city_manager/sustainability/electrical_aggregation_program.php)
